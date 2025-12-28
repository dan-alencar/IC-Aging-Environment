`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Module Name: fpga_unified_top
// Description: Top-level for aging sensor system
//              
// Clock Configuration (from clk_wiz_0):
//   clk_out1: 100MHz, 100° phase  -> clk_en (catcher clock for FF3)
//   clk_out2: 100MHz, 0° phase, FINE_PS enabled -> psclk (phase-shiftable)
//   clk_out3: 100MHz, 0° phase  -> clk_sys (system clock)
//
// Trigger Options:
//   1. Periodic timer - automatic every SWEEP_PERIOD
//   2. VIO manual trigger - for debugging
//////////////////////////////////////////////////////////////////////////////////

module fpga_unified_top (
    input  wire sys_clk_p,
    input  wire sys_clk_n,
    input  wire fpga_uart_rx,
    output wire fpga_uart_tx,
    output wire mcu_usart1_rx, 
    input  wire mcu_usart1_tx, 
    input wire fpga_button,
    output wire status_o 
);

    // =========================================================================
    // 1. CLOCK INPUT - Differential to Single-ended
    // =========================================================================
    // The clock wizard expects single-ended input (clk_in1)
    // We need IBUFDS to convert differential to single-ended
    wire sys_clk_se;
    
    IBUFDS #(
        .DIFF_TERM("FALSE"),
        .IBUF_LOW_PWR("FALSE")
    ) ibuf_clk (
        .I(sys_clk_p),
        .IB(sys_clk_n),
        .O(sys_clk_se)
    );

    // =========================================================================
    // 2. CLOCK WIZARD (MMCM) WITH DYNAMIC PHASE SHIFT
    // =========================================================================
    // Clock outputs:
    //   clk_out1 = clk_en (100° phase, catcher clock for sensor FF3)
    //   clk_out2 = clk_phase (0° initial, dynamic phase shift enabled)
    //   clk_out3 = clk_sys (0° phase, main system clock)
    
    wire clk_en;        // clk_out1 - catcher clock (100° offset)
    wire clk_phase;     // clk_out2 - phase-shiftable clock
    wire clk_sys;       // clk_out3 - system clock
    wire locked;
    wire psen, psincdec, psdone;

    clk_wiz_0 clock_gen (
        .clk_in1(sys_clk_se),       // Single-ended input from IBUFDS
        .reset(1'b0),               // No reset - starts immediately
        .locked(locked),
        .clk_out1(clk_en),          // 100° phase - catcher clock
        .clk_out2(clk_phase),       // Phase-shiftable clock
        .clk_out3(clk_sys),         // System clock
        .psclk(clk_sys),            // Phase shift control clock (use output clock)
        .psen(psen),
        .psincdec(psincdec),
        .psdone(psdone)
    );

    // =========================================================================
    // 3. RESET GENERATION
    // =========================================================================
    reg [3:0] locked_sync = 4'b0000;
    wire global_rst_n;
    
    always @(posedge clk_sys or negedge locked) begin
        if (!locked)
            locked_sync <= 4'b0000;
        else
            locked_sync <= {locked_sync[2:0], 1'b1};
    end
    
    assign global_rst_n = locked_sync[3];

    // =========================================================================
    // 4. CALIBRATION TRIGGER SYSTEM
    // =========================================================================
    // VIO controls
    wire vio_manual_trigger;
    wire vio_enable_periodic;
    wire vio_force_reset;
    
    // Periodic timer trigger
    reg [27:0] sweep_timer = 28'd0;
    reg periodic_trigger = 1'b0;
    localparam SWEEP_PERIOD = 28'd100_000_000;  // 1 second at 100MHz
    
    always @(posedge clk_sys) begin
        if (!global_rst_n) begin
            sweep_timer <= 28'd0;
            periodic_trigger <= 1'b0;
        end else begin
            if (sweep_timer >= SWEEP_PERIOD) begin
                sweep_timer <= 28'd0;
                periodic_trigger <= 1'b1;
            end else begin
                sweep_timer <= sweep_timer + 1;
                periodic_trigger <= 1'b0;
            end
        end
    end
    
    // Combined trigger
    wire combined_trigger;
    assign combined_trigger = (periodic_trigger & vio_enable_periodic) | vio_manual_trigger | vio_force_reset;
    
    // Generate reset pulse for controller (active-low)
    reg [7:0] reset_pulse_cnt = 8'd0;
    reg ctrl_rst_n = 1'b1;
    reg trigger_prev = 1'b0;
    wire trigger_edge;
    
    assign trigger_edge = combined_trigger & ~trigger_prev;
    
    always @(posedge clk_sys) begin
        if (!global_rst_n) begin
            reset_pulse_cnt <= 8'd0;
            ctrl_rst_n <= 1'b0;
            trigger_prev <= 1'b0;
        end else begin
            trigger_prev <= combined_trigger;
            
            if (trigger_edge) begin
                reset_pulse_cnt <= 8'd100;
                ctrl_rst_n <= 1'b0;
            end else if (reset_pulse_cnt > 0) begin
                reset_pulse_cnt <= reset_pulse_cnt - 1;
                ctrl_rst_n <= 1'b0;
            end else begin
                ctrl_rst_n <= 1'b1;
            end
        end
    end

    // =========================================================================
    // 5. CRITICAL PATH (Inverter Chain)
    // =========================================================================
    wire test_bit;
    wire crit_start;
    wire crit_end;

    not_series #(
        .size(50)
    ) critical_path (
        .clk(clk_sys),
        .test_bit(test_bit),
        .start(crit_start),
        .critpath(crit_end)
    );

    // =========================================================================
    // 6. AGING SENSOR
    // =========================================================================
    wire sensor_alarm;
    wire sensor_ff1, sensor_ff2, sensor_raw_alarm;

    modern_sensible sensor (
        .sclk(clk_sys),             // System clock for FF2
        .psclk(clk_phase),          // Phase-shifted clock for FF1
        .clk_en(clk_en),            // Catcher clock for FF3 (100° offset)
        .in_sensor(crit_end),       // Critical path output
        .reset(1'b0),               // Not used
        .alarm(sensor_alarm),       // Filtered alarm
        .ff1_out(sensor_ff1),       // Debug: FF1 value
        .ff2_out(sensor_ff2),       // Debug: FF2 value
        .raw_alarm(sensor_raw_alarm) // Debug: Unfiltered XOR
    );

    // =========================================================================
    // 7. PHASE SHIFT CONTROLLER
    // =========================================================================
    wire [15:0] phase_count;
    wire send_trigger;
    wire [2:0] ctrl_state;

    controller_controller ctrl (
        .clk(clk_sys),
        .reset(~fpga_button),
        .alarm(sensor_alarm),
        .psdone(psdone),
        .display_value(phase_count),
        .change(test_bit),
        .psincdec(psincdec),
        .send(send_trigger),
        .psen(psen),
        .debug_state(ctrl_state)
    );

    // =========================================================================
    // 8. SYSTEM MONITOR (XADC)
    // =========================================================================
    wire [15:0] sysmon_temp;
    wire [15:0] sysmon_vccint;
    wire sysmon_done;
    wire sysmon_busy;

    sysmon_reader u_sysmon (
        .clk(clk_sys),
        .rst_n(global_rst_n),
        .trigger(send_trigger),
        .temp_data(sysmon_temp),
        .vccint_data(sysmon_vccint),
        .read_done(sysmon_done),
        .busy(sysmon_busy)
    );

    // =========================================================================
    // 9. DATA STREAMING (sensor_stream + uart_tx)
    // =========================================================================
    wire stream_send;
    wire [7:0] stream_data;
    wire mon_tx_line;
    wire mon_tx_busy;

    sensor_stream #(
        .BAUDRATE(125000),
        .CLK_FREQ(100000000)
    ) u_stream (
        .clk(clk_sys),
        .reset(global_rst_n),
        .temp({8'b0, sysmon_temp}),
        .vccint({8'b0, sysmon_vccint}),
        .sensor(phase_count),
        .failure(1'b0),
        .sendin(sysmon_done),
        .send(stream_send),
        .data(stream_data)
    );

    uart_tx #(
        .BAUDRATE(125000),
        .CLK_FREQ(100000000)
    ) u_uart_tx (
        .clk(clk_sys),
        .reset(global_rst_n),
        .send(stream_send),
        .data(stream_data),
        .tx(mon_tx_line),
        .tx_busy(mon_tx_busy)
    );

    wire mon_active;
    assign mon_active = sysmon_busy | mon_tx_busy;

    // =========================================================================
    // 10. UART INFRASTRUCTURE
    // =========================================================================
    wire route_to_stm;
    wire router_tx_out;

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

    uart_arbiter u_arb (
        .clk(clk_sys), 
        .rst_n(global_rst_n),
        .tx_croc(router_tx_out),
        .tx_monitor(mon_tx_line),
        .monitor_active(mon_active),
        .tx_combined(fpga_uart_tx)
    );

    // =========================================================================
    // 11. VIO FOR DEBUGGING AND CONTROL
    // =========================================================================
    vio_0 u_vio (
        .clk(clk_sys),
        // Monitoring
        .probe_in0(sysmon_temp),        // 16-bit
        .probe_in1(sysmon_vccint),      // 16-bit
        .probe_in2(phase_count),        // 16-bit
        .probe_in3(ctrl_state),         // 3-bit
        .probe_in4(sensor_alarm),       // 1-bit - filtered alarm
        .probe_in5(locked),             // 1-bit
        .probe_in6(global_rst_n),       // 1-bit
        .probe_in7(fpga_button),        // 1-bit - button state
        .probe_in8(psen),               // 1-bit
        .probe_in9(psdone),             // 1-bit
        .probe_in10(sensor_ff1),        // 1-bit - FF1 output (psclk domain)
        .probe_in11(sensor_ff2),        // 1-bit - FF2 output (sclk domain)
        .probe_in12(sensor_raw_alarm),  // 1-bit - unfiltered XOR
        .probe_in13(crit_end),          // 1-bit - critical path output
        .probe_in14(test_bit),          // 1-bit - toggle input to critical path
        .probe_in15(send_trigger),      // 1-bit
        // Control outputs
        .probe_out0(vio_manual_trigger),
        .probe_out1(vio_enable_periodic),
        .probe_out2(vio_force_reset)
    );

    // =========================================================================
    // 12. STATUS LED
    // =========================================================================
    reg [25:0] heartbeat = 26'd0;
    
    always @(posedge clk_sys) begin
        if (!global_rst_n) 
            heartbeat <= 26'd0;
        else 
            heartbeat <= heartbeat + 1;
    end
    
    wire calibrating;
    assign calibrating = (ctrl_state != 3'b011) && ctrl_rst_n;
    
    assign status_o = locked ? (calibrating ? heartbeat[22] : heartbeat[25]) : 1'b0;

endmodule