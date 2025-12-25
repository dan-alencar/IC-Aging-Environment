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

    // 1. CLOCK & RESET
    wire clk_sys, clk_phase, clk_enable, locked;
    wire psen, psincdec, psdone;
    
    // Hardware Reset (Active Low logic from Active High Button)
    wire btn_rst_n = fpga_button; 

    // -------------------------------------------------------------------------
    // 0x0F SNIFFER (The "Kick" Trigger)
    // -------------------------------------------------------------------------
    logic cmd_rst_n = 1'b1;
    logic [2:0] rx_state = 0;
    logic [15:0] rx_cnt = 0;
    logic [2:0] rx_bit_idx = 0;
    logic [7:0] rx_shift = 0;
    logic rx_sync, rx_reg;
    logic [7:0] prev_byte = 0; // History buffer
    localparam RX_CPB = 100000000 / 125000; 

    always_ff @(posedge clk_sys) begin
        rx_sync <= fpga_uart_rx; rx_reg <= rx_sync;
        if (cmd_rst_n == 0) cmd_rst_n <= 1'b1; // Auto-clear reset

        case (rx_state)
            0: if (rx_reg == 0) begin rx_cnt <= 0; rx_bit_idx <= 0; rx_state <= 1; end
            1: if (rx_cnt == RX_CPB/2) begin 
                   if (rx_reg == 0) begin rx_cnt <= 0; rx_state <= 2; end
                   else rx_state <= 0;
               end else rx_cnt <= rx_cnt + 1;
            2: if (rx_cnt == RX_CPB-1) begin 
                   rx_cnt <= 0; rx_shift[rx_bit_idx] <= rx_reg;
                   if (rx_bit_idx == 7) rx_state <= 3;
                   else rx_bit_idx <= rx_bit_idx + 1;
               end else rx_cnt <= rx_cnt + 1;
            3: if (rx_cnt == RX_CPB-1) begin 
                   // CHECK FOR SEQUENCE: 0x0F, 0x0F
                   if (rx_shift == 8'h0F && prev_byte == 8'h0F) begin
                        cmd_rst_n <= 1'b0; // FIRE RESET
                        prev_byte <= 0;    // Clear history to prevent double firing
                   end else begin
                        prev_byte <= rx_shift; // Store for next check
                   end
                   rx_state <= 0;
               end else rx_cnt <= rx_cnt + 1;
        endcase
    end

    // MASTER RESET: Active if Locked AND Button Released AND No UART Command
    wire experiment_rst_n;
    assign experiment_rst_n = locked && btn_rst_n && cmd_rst_n;
    
    logic rst_n;
    always_ff @(posedge clk_sys) rst_n <= experiment_rst_n;

    clk_wiz_0 clock_gen (
        .clk_in1_p(sys_clk_p), .clk_in1_n(sys_clk_n),
        .clk_out1(clk_enable), .clk_out2(clk_phase), .clk_out3(clk_sys),    
        .reset(!fpga_button),  .locked(locked),
        .psclk(clk_sys), .psen(psen), .psincdec(psincdec), .psdone(psdone)
    );

    // 2. DIAGNOSTIC LED & LATCH
    logic [25:0] heartbeat;
    always_ff @(posedge clk_sys) heartbeat <= heartbeat + 1;
    wire alarm_latched;
    assign status_o = locked ? (alarm_latched ? heartbeat[25] : 1'b1) : 1'b0;

    // 3. COMMS (Router + Monitor)
    logic route_to_stm, router_tx_out, mon_tx, mon_active;
    wire [15:0] phase_val;
    assign mcu_usart1_rx = route_to_stm;
    
    uart_router #(.CLK_FREQ(100000000), .BAUD_RATE(125000)) u_router (
        .clk(clk_sys), .rst_n(rst_n),
        .uart_rx_phys(fpga_uart_rx), .uart_tx_phys(router_tx_out), 
        .uart_tx_to_stm(route_to_stm), .uart_tx_from_stm(mcu_usart1_tx),
        .uart_tx_to_croc(), .uart_tx_from_croc(1'b1),
        .heartbeat_pin(1'b0), .safe_rst_n()
    );

    sysmon_monitor #(.CLK_FREQ(100000000), .BAUD_RATE(125000)) u_mon (
        .clk(clk_sys), .rst_n(rst_n),
        .aging_alarm(alarm_latched), .aging_count(phase_val), 
        .tx_out(mon_tx), .tx_active(mon_active)
    );

    uart_arbiter u_arb (
        .clk(clk_sys), .rst_n(rst_n),
        .tx_croc(router_tx_out), .tx_monitor(mon_tx), .monitor_active(mon_active),
        .tx_combined(fpga_uart_tx)
    );
    
    // 4. AGING EXPERIMENT
    wire change_sig, send_trig, ref_sig, delayed_sig, raw_fail;
    
    controller_controller mgr (
        .clk(clk_sys), 
        .reset(experiment_rst_n), // Cleared by 0x0F
        .alarm(alarm_latched),    // Stops when Latch is set
        .psdone(psdone), 
        .display_value(phase_val),
        .change(change_sig), 
        .psincdec(psincdec), 
        .send(send_trig), 
        .psen(psen)
    );

    not_series #(.size(50)) dly (
        .clk(clk_sys), .test_bit(change_sig),
        .start(ref_sig), .critpath(delayed_sig)
    );

    // FIXED: Using internal ALARM from the module
    modern_sensible sns (
        .sclk(clk_sys), .psclk(clk_phase), .clk_en(clk_enable),
        .in_sensor(delayed_sig), .reset(!experiment_rst_n),
        .alarm(raw_fail), // <--- CONNECTED INTERNAL DETECTOR
        .ff1_out()        // Not needed for failure logic anymore
    );

    // Latch the error until 0x0F reset
    holder_button hld (
        .clk(clk_sys), 
        .reset(!experiment_rst_n), // Input to clear latch on 0x0F
        .button(1'b0), 
        .alarm(raw_fail), 
        .held(alarm_latched)
    );

endmodule