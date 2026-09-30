`timescale 1ns / 1ps

module fpga_unified_top (
    input  logic sys_clk_p,
    input  logic sys_clk_n,
    
    // UARTs
    input  logic fpga_uart_rx,    // PC -> FPGA (J9)
    output logic fpga_uart_tx,    // FPGA -> PC (J9)
    
    output logic mcu_usart1_rx,   // FPGA -> STM32
    input  logic mcu_usart1_tx,   // STM32 -> FPGA
    
    // Control
    input  logic fpga_button,     // Reset
    output logic status_o         // LED
);

    // =========================================================================
    // 1. CLOCK GENERATION & RESET
    // =========================================================================
    wire clk_fixed_sys;    // 100MHz System
    wire clk_phase_dynamic;// 100MHz Shiftable (Capture)
    wire clk_phase_100;    // 100MHz Phase 100 (Enable)
    wire locked;
    
    // Basic Reset Sync (Replaces external rstgen)
    logic rst_n_meta, rst_n;
    always_ff @(posedge clk_fixed_sys) begin
        rst_n_meta <= !fpga_button; // Active High button -> Active Low logic
        rst_n      <= rst_n_meta;
    end

    // Dynamic Phase Shift Signals
    wire psen, psincdec, psdone;

    clk_wiz_0 clock_gen (
        .clk_in1_p(sys_clk_p), 
        .clk_in1_n(sys_clk_n),
        .clk_out1(clk_phase_100),     // Phase 100
        .clk_out2(clk_phase_dynamic), // Dynamic Phase
        .clk_out3(clk_fixed_sys),     // System Fixed
        .reset(fpga_button),          // Active High for Wiz
        .locked(locked),
        .psclk(clk_fixed_sys),
        .psen(psen),
        .psincdec(psincdec),
        .psdone(psdone)
    );

    // =========================================================================
    // 2. AGING EXPERIMENT CORE
    // =========================================================================
    wire latched_alarm;
    wire controller_change;
    wire [15:0] phase_count;
    wire controller_send_trigger; // Used internally or ignored since Sysmon polls

    // Controller (Manager)
    controller_controller aging_manager (
        .clk(clk_fixed_sys),
        .reset(locked),
        .alarm(latched_alarm),
        .psdone(psdone),
        .display_value(phase_count),
        .change(controller_change),
        .psincdec(psincdec),
        .send(controller_send_trigger),
        .psen(psen)
    );

    // Delay Line (Launch)
    wire ref_start, delayed_signal;
    not_series #(.size(50)) delay_line (
        .clk(clk_fixed_sys),
        .test_bit(controller_change),
        .start(ref_start), 
        .critpath(delayed_signal)
    );

    // Sensor (Capture)
    wire sensor_ff_out, raw_alarm;
    modern_sensible sampler (
        .sclk(clk_fixed_sys),
        .psclk(clk_phase_dynamic),
        .clk_en(clk_phase_100),
        .in_sensor(delayed_signal), 
        .reset(fpga_button),
        .alarm(raw_alarm),        
        .ff1_out(sensor_ff_out)
    );

    // Failure Hold
    wire failure_detected;
    failure_holder comparator (
        .ff1(ref_start), .ff2(sensor_ff_out), 
        .reset(rst_n), .held(failure_detected)
    );
    
    holder_button alarm_guarantee (
        .clk(clk_fixed_sys), .button(fpga_button), 
        .alarm(failure_detected), .held(latched_alarm)
    );

    assign status_o = latched_alarm;

    // =========================================================================
    // 3. UNIFIED COMMUNICATION (ROUTER + ARBITER + MONITOR)
    // =========================================================================
    
    // A. Router (PC RX -> FPGA/STM)
    // -------------------------------------------------------------
    logic w_router_to_croc; // Not connected to softcore yet
    logic w_router_to_stm;
    logic w_wd_reset_n;     // Safe reset from watchdog
    
    // Logic 1 indicates Idle in UART
    assign mcu_usart1_rx = w_router_to_stm; 

    uart_router #(
        .CLK_FREQ(100000000), // Updated to 100MHz
        .BAUD_RATE(115200),
        .WATCHDOG_MS(1000)
    ) u_router (
        .clk(clk_fixed_sys),
        .rst_n(rst_n),
        
        // PC Interface
        .uart_rx_phys(fpga_uart_rx),
        .uart_tx_phys( ), // Logic handled by Arbiter below
        
        // CROC (Softcore) - Loopback or Open for now
        .uart_tx_to_croc(w_router_to_croc),
        .uart_tx_from_croc(1'b1), // Idle
        
        // STM32
        .uart_tx_to_stm(w_router_to_stm),
        .uart_tx_from_stm(mcu_usart1_tx),
        
        // Safety
        .heartbeat_pin(1'b0), // Tie to 0 if no heartbeat source yet
        .safe_rst_n(w_wd_reset_n)
    );

    // B. SysMon Monitor (Replaces old sensor_stream)
    // -------------------------------------------------------------
    logic monitor_tx_line;
    logic monitor_tx_active;

    sysmon_monitor #(
        .CLK_FREQ(100000000), // 100MHz
        .BAUD_RATE(115200)
    ) i_sysmon_monitor (
        .clk(clk_fixed_sys),
        .rst_n(rst_n),
        
        // Inject Aging Data
        .aging_alarm(latched_alarm),
        .aging_count(phase_count),
        
        // UART Output
        .tx_out(monitor_tx_line),
        .tx_active(monitor_tx_active)
    );

    // C. Arbiter (Monitor vs Softcore -> PC TX)
    // -------------------------------------------------------------
    uart_arbiter i_arbiter (
        .clk(clk_fixed_sys),
        .rst_n(rst_n),
        
        // Channel 1: Softcore (Disabled/Idle for now)
        .tx_croc(1'b1), 
        
        // Channel 2: Monitor
        .tx_monitor(monitor_tx_line),
        .monitor_active(monitor_tx_active),
        
        // Result
        .tx_combined(fpga_uart_tx)
    );

endmodule