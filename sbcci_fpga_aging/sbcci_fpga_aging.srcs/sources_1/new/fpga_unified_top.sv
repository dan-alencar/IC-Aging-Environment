`timescale 1ns / 1ps

module fpga_unified_top (
    input  logic sys_clk_p,
    input  logic sys_clk_n,
    input  logic fpga_uart_rx,
    output logic fpga_uart_tx,
    output logic mcu_usart1_rx, 
    input  logic mcu_usart1_tx, 
    input  logic fpga_button,
    output logic status_o 
);

    // =========================================================================
    // 1. CLOCK & RESET GENERATION
    // =========================================================================
    wire clk_sys, clk_phase, clk_enable, locked;
    wire psen, psincdec, psdone;

    // Synchronized reset
    logic [2:0] reset_sync;
    logic global_rst_n;
    
    always_ff @(posedge clk_sys or negedge fpga_button) begin
        if (!fpga_button) begin
            reset_sync <= 3'b000;
        end else begin
            reset_sync <= {reset_sync[1:0], 1'b1};
        end
    end
    
    assign global_rst_n = reset_sync[2] & locked;

    // CLOCK WIZARD
    clk_wiz_0 clock_gen (
        .clk_in1_p(sys_clk_p), 
        .clk_in1_n(sys_clk_n),
        .clk_out1(clk_enable), 
        .clk_out2(clk_phase), 
        .clk_out3(clk_sys),    
        .reset(!fpga_button),
        .locked(locked),
        .psclk(clk_sys), 
        .psen(psen), 
        .psincdec(psincdec), 
        .psdone(psdone)
    );

    // =========================================================================
    // 2. AUTO-RESTART TIMER FOR PHASE SWEEPS
    // =========================================================================
    logic [27:0] sweep_timer;
    logic sweep_rst_n;
    
    // Sweep every 1 second (100M cycles at 100MHz)
    // Adjust this to change sweep frequency
    localparam SWEEP_PERIOD = 100_000_000;

    always_ff @(posedge clk_sys or negedge global_rst_n) begin
        if (!global_rst_n) begin
            sweep_timer <= 0;
            sweep_rst_n <= 1'b0;
        end else begin
            if (sweep_timer >= SWEEP_PERIOD) begin
                sweep_timer <= 0;
                sweep_rst_n <= 1'b0;  // Pulse reset low
            end else begin
                sweep_timer <= sweep_timer + 1;
                sweep_rst_n <= 1'b1;  // Run normally
            end
        end
    end

    // =========================================================================
    // 3. AGING SENSOR EXPERIMENT
    // =========================================================================
    wire change_sig, ref_sig, delayed_sig, raw_alarm, alarm_latched;
    wire [15:0] phase_val;
    wire send_trigger;
    
    // Phase Shift Controller
    controller_controller mgr (
        .clk(clk_sys), 
        .reset(sweep_rst_n),
        .alarm(alarm_latched),    
        .psdone(psdone), 
        .display_value(phase_val),
        .change(change_sig), 
        .psincdec(psincdec), 
        .send(send_trigger),
        .psen(psen)
    );

    // Delay chain for critical path monitoring
    not_series #(.size(50)) dly (
        .clk(clk_sys), 
        .test_bit(change_sig),
        .start(ref_sig), 
        .critpath(delayed_sig)
    );

    // Aging sensor
    modern_sensible sns (
        .sclk(clk_sys), 
        .psclk(clk_phase), 
        .clk_en(clk_enable),
        .in_sensor(delayed_sig), 
        .reset(!sweep_rst_n),
        .alarm(raw_alarm), 
        .ff1_out()       
    );

    // Latch alarm until next sweep
    holder_button hld (
        .clk(clk_sys), 
        .reset(!sweep_rst_n),
        .button(1'b0),
        .alarm(raw_alarm), 
        .held(alarm_latched)
    );

    // =========================================================================
    // 4. COMMUNICATION INFRASTRUCTURE
    // =========================================================================
    logic route_to_stm, router_tx_out, mon_tx, mon_active;

    assign mcu_usart1_rx = route_to_stm;
    
    // UART Router - handles PC <-> STM32/CROC communication
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

    // System Monitor - NOW USING IP WRAPPER
    // This reads temp/voltage and transmits when triggered
    sysmon_monitor #(
        .CLK_FREQ(100000000), 
        .BAUD_RATE(125000)
    ) u_mon (
        .clk(clk_sys), 
        .rst_n(global_rst_n),
        .aging_alarm(alarm_latched), 
        .aging_count(phase_val), 
        .i_trigger(send_trigger),
        .tx_out(mon_tx), 
        .tx_active(mon_active)
    );

    // UART Arbiter - multiplexes router and monitor TX
    uart_arbiter u_arb (
        .clk(clk_sys), 
        .rst_n(global_rst_n),
        .tx_croc(router_tx_out), 
        .tx_monitor(mon_tx), 
        .monitor_active(mon_active),
        .tx_combined(fpga_uart_tx)
    );

    // =========================================================================
    // 5. STATUS LED
    // =========================================================================
    logic [25:0] heartbeat;
    always_ff @(posedge clk_sys or negedge global_rst_n) begin
        if (!global_rst_n) 
            heartbeat <= 0;
        else 
            heartbeat <= heartbeat + 1;
    end
    
    // LED behavior:
    // - OFF: PLL not locked
    // - FAST BLINK (bit 23): Alarm detected (timing violation found)
    // - SLOW BLINK (bit 25): No alarm (system running but no violation yet)
    assign status_o = locked ? (alarm_latched ? heartbeat[23] : heartbeat[25]) : 1'b0;

endmodule