`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Module Name: aging_sensor_top
// Description: Top-level module with Auto-Start (Power-On Reset)
//////////////////////////////////////////////////////////////////////////////////

module aging_sensor_top(
    // Differential clock input (100MHz)
    input wire sys_clk_p,
    input wire sys_clk_n,
    
    // REMOVED: input wire fpga_button
    
    // UART interface
    input wire rx,
    output wire tx
);
    //========================================================================
    // Internal Signals
    //========================================================================
    
    // Clock signals
    wire sys_clk_in;
    wire sys_clk;
    wire phase_clk;
    wire clk_en;
    wire clk_locked;
    
    // Reset Logic
    wire sys_reset_n;           // System reset (Active Low)
    wire vio_soft_reset;        // Software reset from VIO (Active High)
    
    // -----------------------------------------------------------------------
    // NEW RESET ARCHITECTURE:
    // 1. The Clock Wizard runs immediately (reset tied to 0).
    // 2. The rest of the system is held in reset until the clock is LOCKED.
    // 3. VIO can force a reset if needed.
    // -----------------------------------------------------------------------
    assign sys_reset_n = clk_locked && ~vio_soft_reset;

    // Phase shift control
    wire psen;
    wire psincdec;
    wire psdone;

    // System Monitor signals
    wire [7:0] sysmon_daddr;
    wire sysmon_den;
    wire [15:0] sysmon_do;
    wire sysmon_drdy;

    // Temperature and voltage data
    wire [20:0] temp_data;
    wire [20:0] vccint_data;

    // Aging sensor signals
    wire sensor_alarm;
    wire sensor_test_bit;
    wire sensor_start;
    wire sensor_critpath;
    wire sensor_ff1_out;

    // Controller signals
    wire [15:0] display_value;
    wire measuring;
    wire meas_complete;

    // UART transmission signals
    wire uart_send_trigger;
    wire uart_send;
    wire [7:0] uart_data;
    wire uart_busy;

    // Failure detection
    wire failure_held;
    
    // VIO control signals
    wire vio_trigger_meas;
    wire vio_continuous_mode;
    wire vio_force_send;
    
    wire temp_trigger;        // Triggers temperature reading
    wire temp_meas_done;      // Indicates temperature reading is finished
    
    // Trigger Temp Catcher when Controller finishes OR VIO forces it
    assign temp_trigger = uart_send_trigger | vio_force_send;

    //========================================================================
    // Clock Input Buffer
    //========================================================================
    IBUFDS i_bufds_sys_clk (
        .I  (sys_clk_p),
        .IB (sys_clk_n),
        .O  (sys_clk_in)
    );

    //========================================================================
    // Clock Wizard
    //========================================================================
    clk_wiz_0 clock_gen (
        .clk_in1(sys_clk_in),
        .reset(1'b0),            // FIXED: Tie to 0 so it starts immediately
        .locked(clk_locked),
        .sys_clk(sys_clk),
        .phase_clk(phase_clk),
        .clk_en(clk_en),
        .psclk(sys_clk_in),      // Corrected: Uses input clock
        .psen(psen),
        .psincdec(psincdec),
        .psdone(psdone)
    );

    //========================================================================
    // System Management Wizard
    //========================================================================
    system_management_wiz_0 sysmon (
        .daddr_in(sysmon_daddr),
        .den_in(sysmon_den),
        .di_in(16'h0000),
        .dwe_in(1'b0),
        .do_out(sysmon_do),
        .drdy_out(sysmon_drdy),
        .dclk_in(sys_clk),
        .reset_in(~sys_reset_n),    // Reset if system is in reset
        .vp(1'b0),
        .vn(1'b0),
        .channel_out(),
        .eoc_out(),
        .alarm_out(),
        .eos_out(),
        .busy_out()
    );

    //========================================================================
    // Temperature Catcher
    //========================================================================
    temp_catcher temp_reader (
        .clk(sys_clk),
        .reset(sys_reset_n),
        .drdy(sysmon_drdy),
        .do_data(sysmon_do),
        .daddr(sysmon_daddr),
        .den(sysmon_den),
        .temp(temp_data),
        .vccint(vccint_data)
    );

    //========================================================================
    // Inverter Chain (Critical Path)
    //========================================================================
    not_series #(
        .size(100)
    ) critical_path (
        .clk(sys_clk),
        .test_bit(sensor_test_bit),
        .start(sensor_start),
        .critpath(sensor_critpath)
    );

    //========================================================================
    // Modern Sensible - Aging Sensor
    //========================================================================
    modern_sensible aging_sensor (
        .sclk(sys_clk),
        .psclk(phase_clk),
        .in_sensor(sensor_critpath),
        .reset(sys_reset_n),
        .clk_en(clk_en),
        .alarm(sensor_alarm),
        .ff1_out(sensor_ff1_out)
    );

    //========================================================================
    // Controller
    //========================================================================
    controller_controller main_controller (
        .clk(sys_clk),
        .reset(sys_reset_n),
        .alarm(sensor_alarm),
        .psdone(psdone),
        .trigger_meas(vio_trigger_meas),
        .continuous_mode(vio_continuous_mode),
        .display_value(display_value),
        .change(sensor_test_bit),
        .psincdec(psincdec),
        .send(uart_send_trigger),
        .psen(psen),
        .measuring(measuring),
        .meas_complete(meas_complete)
    );

    //========================================================================
    // Failure Holder
    //========================================================================
    failure_holder failure_latch (
        .ff1(sensor_start),
        .ff2(sensor_ff1_out),
        .reset(sys_reset_n),
        .held(failure_held)
    );

    //========================================================================
    // Sensor Stream
    //========================================================================
    sensor_stream #(
        .BAUDRATE(9600),
        .CLK_FREQ(100000000)
    ) data_streamer (
        .temp({3'b000, temp_data}),
        .vccint({3'b000, vccint_data}),
        .sensor(display_value),
        .failure(failure_held),
        .reset(sys_reset_n),
        .clk(sys_clk),
        .sendin(uart_send_trigger | vio_force_send),
        .send(uart_send),
        .data(uart_data)
    );

    //========================================================================
    // UART Transmitter
    //========================================================================
    uart_tx #(
        .BAUDRATE(9600),
        .CLK_FREQ(100000000)
    ) uart_transmitter (
        .clk(sys_clk),
        .reset(sys_reset_n),
        .send(uart_send),
        .data(uart_data),
        .tx(tx),
        .tx_busy(uart_busy)
    );

    //========================================================================
    // ILA
    //========================================================================
    (* dont_touch = "true" *)
    ila_0 ila_debug (
        .clk(sys_clk),
        .probe0({
            clk_locked,         
            sys_reset_n,        
            sensor_alarm,       
            measuring,          
            psen,               
            psincdec,           
            psdone,             
            uart_busy           
        }),
        .probe1(display_value),
        .probe2(temp_data),
        .probe3(vccint_data),
        .probe4(uart_data),
        .probe5({
            vio_trigger_meas,   
            vio_continuous_mode,
            vio_force_send,     
            meas_complete,      
            sensor_test_bit,    
            sensor_start,       
            sensor_critpath,    
            sensor_ff1_out      
        }),
        .probe6(sysmon_daddr),
        .probe7(sysmon_do)
    );
    
    reg [15:0] debug_live_shifts;
    
    // Increment whenever the Clock Wizard confirms a phase shift (psdone)
    // Reset when a measurement completes so we start fresh next time
    always @(posedge sys_clk) begin
        if (meas_complete || ~sys_reset_n) begin
            debug_live_shifts <= 0;
        end else if (psdone) begin
            debug_live_shifts <= debug_live_shifts + 1;
        end
    end

    // MUX: If measuring, show the LIVE count. If done, show the FINAL result.
    wire [15:0] vio_display_mux;
    assign vio_display_mux = measuring ? debug_live_shifts : display_value;

    //========================================================================
    // VIO
    //========================================================================
    (* dont_touch = "true" *)
    vio_0 vio_control (
        .clk(sys_clk),
        .probe_in0(clk_locked),
        .probe_in1(sys_reset_n),
        .probe_in2(sensor_alarm),
        .probe_in3(failure_held),
        .probe_in4(vio_display_mux),
        .probe_in5(temp_data),
        .probe_in6(vccint_data),
        .probe_in7(uart_busy),
        .probe_in8(measuring),
        .probe_out0(vio_trigger_meas),
        .probe_out1(vio_continuous_mode),
        .probe_out2(vio_force_send),
        .probe_out3(vio_soft_reset)
    );
endmodule