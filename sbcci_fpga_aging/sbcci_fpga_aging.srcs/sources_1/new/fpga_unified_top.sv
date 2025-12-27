`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Module Name: fpga_unified_top
// Description: Fixed top-level module with proper reset sequencing
//////////////////////////////////////////////////////////////////////////////////

module fpga_unified_top (
    input  logic sys_clk_p,
    input  logic sys_clk_n,
    input  logic fpga_uart_rx,
    output logic fpga_uart_tx,
    output logic mcu_usart1_rx, 
    input  logic mcu_usart1_tx, 
    output logic status_o 
);

    // =========================================================================
    // 1. CLOCK GENERATION
    // =========================================================================
    wire clk_sys, clk_phase, clk_enable, locked;
    wire psen, psincdec, psdone;

    clk_wiz_0 clock_gen (
        .clk_in1_p(sys_clk_p), 
        .clk_in1_n(sys_clk_n),
        .clk_out1(clk_enable), 
        .clk_out2(clk_phase), 
        .clk_out3(clk_sys),    
        .reset(1'b0),
        .locked(locked),
        .psclk(clk_sys), 
        .psen(psen), 
        .psincdec(psincdec), 
        .psdone(psdone)
    );

    // =========================================================================
    // 2. POWER-ON RESET GENERATION - ACTIVE LOW DIRECTLY FROM LOCKED
    // =========================================================================
    // Use locked directly with a small synchronizer
    // The synchronizer uses async reset from ~locked to ensure it starts correctly
    
    reg [3:0] locked_sync = 4'b0000;  // Initialize to 0
    wire global_rst_n;
    
    always @(posedge clk_sys or negedge locked) begin
        if (!locked) begin
            locked_sync <= 4'b0000;
        end else begin
            locked_sync <= {locked_sync[2:0], 1'b1};
        end
    end
    
    assign global_rst_n = locked_sync[3];

    // =========================================================================
    // 3. AUTO-RESTART TIMER FOR PHASE SWEEPS
    // =========================================================================
    reg [27:0] sweep_timer = 28'd0;
    reg sweep_rst_n = 1'b0;
    
    localparam SWEEP_PERIOD = 100_000_000;  // 1 second at 100MHz

    always @(posedge clk_sys or negedge global_rst_n) begin
        if (!global_rst_n) begin
            sweep_timer <= 28'd0;
            sweep_rst_n <= 1'b0;
        end else begin
            if (sweep_timer >= SWEEP_PERIOD) begin
                sweep_timer <= 28'd0;
                sweep_rst_n <= 1'b0;
            end else begin
                sweep_timer <= sweep_timer + 1;
                sweep_rst_n <= 1'b1;
            end
        end
    end

    // =========================================================================
    // 4. AGING SENSOR EXPERIMENT
    // =========================================================================
    wire change_sig, ref_sig, delayed_sig, raw_alarm, alarm_latched;
    wire [15:0] phase_val;
    wire send_trigger;
    wire [2:0] ctrl_debug_state;
    
    controller_controller mgr (
        .clk(clk_sys), 
        .reset(sweep_rst_n),
        .alarm(alarm_latched),    
        .psdone(psdone), 
        .display_value(phase_val),
        .change(change_sig), 
        .psincdec(psincdec), 
        .send(send_trigger),
        .psen(psen),
        .debug_state(ctrl_debug_state)
    );

    not_series #(.size(50)) dly (
        .clk(clk_sys), 
        .test_bit(change_sig),
        .start(ref_sig), 
        .critpath(delayed_sig)
    );

    modern_sensible sns (
        .sclk(clk_sys), 
        .psclk(clk_phase), 
        .clk_en(clk_enable),
        .in_sensor(delayed_sig), 
        .reset(~sweep_rst_n),
        .alarm(raw_alarm), 
        .ff1_out()       
    );

    holder_button hld (
        .clk(clk_sys), 
        .reset(~sweep_rst_n),
        .button(1'b0),
        .alarm(raw_alarm), 
        .held(alarm_latched)
    );

    // =========================================================================
    // 5. COMMUNICATION INFRASTRUCTURE
    // =========================================================================
    logic route_to_stm, router_tx_out, mon_tx, mon_active;

    assign mcu_usart1_rx = route_to_stm;
    
    uart_router #(
        .CLK_FREQ(100000000), 
        .BAUD_RATE(125000)
    ) u_router (
        .clk(clk_sys), 
        .rst_n(global_rst_n),
        .uart_rx_phys(fpga_uart_rx), 
        .uart_tx_phys(router_tx_out), 
        .uart_tx_to_stm(route_to_stm), 
        .uart_tx_from_stm(mcu_usart1_tx),
        .uart_tx_to_croc(), 
        .uart_tx_from_croc(1'b1),
        .heartbeat_pin(1'b0), 
        .safe_rst_n()
    );
    
    wire [15:0] mon_debug_temp;
    wire [15:0] mon_debug_vcc;
    wire [2:0]  mon_debug_state;

    sysmon_monitor_fixed #(
        .CLK_FREQ(100000000), 
        .BAUD_RATE(125000)
    ) u_mon (
        .clk(clk_sys), 
        .rst_n(global_rst_n),
        .aging_alarm(alarm_latched), 
        .aging_count(phase_val), 
        .i_trigger(send_trigger),
        .tx_out(mon_tx), 
        .tx_active(mon_active),
        .debug_temp(mon_debug_temp),
        .debug_vcc(mon_debug_vcc),
        .debug_state(mon_debug_state)
    );
    
    // =========================================================================
    // 6. VIO FOR DEBUGGING
    // =========================================================================
    vio_0 u_vio (
        .clk(clk_sys),
        .probe_in0(mon_debug_temp),
        .probe_in1(mon_debug_vcc),  
        .probe_in2(mon_debug_state),
        .probe_in3(send_trigger),
        .probe_in4(phase_val),
        .probe_in5(locked),
        .probe_in6(global_rst_n),
        .probe_in7(sweep_rst_n),
        .probe_in8(psen),
        .probe_in9(psdone),
        .probe_in10(alarm_latched),
        .probe_in11(ctrl_debug_state)  // 0=IDLE,1=STAB,2=CHECK,3=INIT,4=WAIT,5=LOCKED,6=SEND
    );

    // UART Arbiter
    uart_arbiter u_arb (
        .clk(clk_sys), 
        .rst_n(global_rst_n),
        .tx_croc(router_tx_out), 
        .tx_monitor(mon_tx), 
        .monitor_active(mon_active),
        .tx_combined(fpga_uart_tx)
    );

    // =========================================================================
    // 7. STATUS LED
    // =========================================================================
    reg [25:0] heartbeat = 26'd0;
    
    always @(posedge clk_sys or negedge global_rst_n) begin
        if (!global_rst_n) 
            heartbeat <= 26'd0;
        else 
            heartbeat <= heartbeat + 1;
    end
    
    assign status_o = locked ? (alarm_latched ? heartbeat[23] : heartbeat[25]) : 1'b0;

endmodule