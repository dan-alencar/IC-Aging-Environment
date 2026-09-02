`timescale 1ns / 1ps

// Top-level module for the Nexys4 DDR aging study (pure RTL, no block design).
// experimental-multi-sensor branch: NUM_SENSORS independent rca_sensor_channel
// instances feed one shared controller_controller_multi phase-sweep engine.
//
// Signal conventions:
//   reset_n  — active-low derived from BTNU (N17); fed to RTL modules that use
//              negedge-reset (controller, channels, stream, uart, temp).
//   reset_p  — active-high (raw button); fed to modules that use posedge-reset
//              (DisplayController) or the per-channel alarm synchronizer.
//
// Clock domains (shared across all channels -- one MMCM per device):
//   clk_sys : 0°  100 MHz — main system clock
//   psclk   : 0°, dynamically phase-shiftable — FF1 in each channel
//   clk_en  : 100° fixed offset 100 MHz — FF3 (alarm latch) in each channel
//
// chan_alarm originates in the clk_en domain (each channel's FF3 Q-output).
// alarm_sync is a 2-FF synchronised version (per channel) for all
// clk_sys-domain consumers, notably controller_controller_multi.
//
// Display layout (8 digits) -- representative only, shows channels 0-1:
//   AN[7:4] / in4..in7 — channel 0 slack   (left  4 digits)
//   AN[3:0] / in0..in3 — always 0 (no functional canary display on this branch)

module nexys4_aging_top (
    input  logic        CLK100MHZ,
    input  logic        reset,        // BTNU N17  — active-high, resets all
    input  logic        button,       // BTNC M18  — manual UART send
    input  logic        UARTsend,     // BTNL M17  — additional manual UART send
    input  logic        rx,           // UART RX from PC C4 (unused)
    output logic        tx,           // UART TX to PC D4
    output logic        CA,
    output logic        CB,
    output logic        CC,
    output logic        CD,
    output logic        CE,
    output logic        CF,
    output logic        CG,
    output logic        DP,
    output logic [7:0]  AN,
    output logic        alarm_led,    // H17 — metastability alarm
    output logic        error_any_led,// K15 — adder canary: any mismatch
    output logic        held_led,     // J13 — tied low on this branch (no cross-channel functional canary)
    output logic        direction,    // J15 — psincdec debug output
    output logic        shift         // P18 — psen debug output
);

    // -----------------------------------------------------------------------
    // Clocking and reset
    //   MMCM is only reset by the button (reset).  Lock-loss asserts reset_p,
    //   which holds all RTL in reset until the MMCM relocks.
    // -----------------------------------------------------------------------
    logic clk_en, psclk, clk_sys, locked;
    logic psen_ctrl, psincdec_ctrl, psdone;

    logic reset_n, reset_p;
    assign reset_p = reset | ~locked;
    assign reset_n = ~reset_p;

    clk_wiz_0 u_clk_wiz (
        .clk_in1  (CLK100MHZ),
        .reset    (reset),
        .locked   (locked),
        .clk_en   (clk_en),
        .sensor0  (psclk),
        .clk_sys  (clk_sys),
        .psclk    (clk_sys),       // DPS reference clock = system clock
        .psen     (psen_ctrl),
        .psincdec (psincdec_ctrl),
        .psdone   (psdone)
    );

    // -----------------------------------------------------------------------
    // XADC — on-chip temperature and VCCINT via DRP polling (temp_catcher)
    // -----------------------------------------------------------------------
    logic [6:0]  xadc_daddr;
    logic        xadc_den;
    logic [15:0] xadc_do;
    logic        xadc_drdy;

    (* DONT_TOUCH = "true" *)
    XADC #(
        .INIT_40 (16'h9000),   // 16x averaging, calibration enabled
        .INIT_41 (16'h2EF0),   // continuous sequencer mode
        .INIT_42 (16'h0400),   // DCLK divider = 4 → 25 MHz ADC clock
        .INIT_48 (16'h0300),   // sequencer: temperature (bit 8) + VCCINT (bit 9) — matches XADC Wizard reference
        .INIT_49 (16'h0000),
        .INIT_4A (16'h0000),
        .INIT_4B (16'h0000),
        .INIT_4C (16'h0000),
        .INIT_4D (16'h0000),
        .INIT_4E (16'h0000),
        .INIT_4F (16'h0000),
        .INIT_50 (16'hB5ED),
        .INIT_51 (16'h57E4),
        .INIT_52 (16'hA147),
        .INIT_53 (16'hCA33),
        .INIT_54 (16'hA93A),
        .INIT_55 (16'hD4FE),
        .INIT_56 (16'h9555),
        .INIT_57 (16'hAE4E),
        .SIM_DEVICE ("7SERIES")
    ) u_xadc (
        .CONVSTCLK (1'b0),
        .CONVST    (1'b0),
        .RESET     (reset),
        .DCLK      (clk_sys),
        .DEN       (xadc_den),
        .DWE       (1'b0),
        .DADDR     (xadc_daddr),
        .DI        (16'h0000),
        .DO        (xadc_do),
        .DRDY      (xadc_drdy),
        .EOC       (),
        .EOS       (),
        .BUSY      (),
        .CHANNEL   (),
        .ALM       (),
        .OT        (),
        .VAUXN     (16'b0),
        .VAUXP     (16'b0),
        .VN        (1'b0),
        .VP        (1'b0)
    );

    logic [20:0] temp_raw, vccint_raw;

    temp_catcher u_temp (
        .clk     (clk_sys),
        .reset   (reset_n),
        .drdy    (xadc_drdy),
        .do_data (xadc_do),
        .daddr   (xadc_daddr),
        .den     (xadc_den),
        .temp    (temp_raw),
        .vccint  (vccint_raw)
    );

    // -----------------------------------------------------------------------
    // N-channel RCA sensor array + shared phase-sweep controller.
    // All channels are independent rca_sensor_channel instances (self-
    // contained: their own adder + metastability sampler). They share the
    // one MMCM phase sweep via controller_controller_multi, which latches
    // each channel's own phase-step count independently -- see that
    // module's header comment for why a mux isn't used.
    // -----------------------------------------------------------------------
    localparam int NUM_SENSORS = 4;

    logic [NUM_SENSORS-1:0] chan_alarm;
    logic [NUM_SENSORS-1:0] chan_ff1;
    logic [NUM_SENSORS-1:0] chan_ff2;
    logic [NUM_SENSORS-1:0] chan_raw_alarm;
    logic [NUM_SENSORS-1:0] chan_error_flag;

    genvar gi;
    generate
        for (gi = 0; gi < NUM_SENSORS; gi = gi + 1) begin : g_sensors
            rca_sensor_channel #(
                .WIDTH(64)
            ) u_channel (
                .clk_sys(clk_sys),
                .clk_phase(psclk),
                .clk_en(clk_en),
                .rst_n(reset_n),
                .sensor_alarm(chan_alarm[gi]),
                .sensor_ff1(chan_ff1[gi]),
                .sensor_ff2(chan_ff2[gi]),
                .sensor_raw_alarm(chan_raw_alarm[gi]),
                .adder_error_flag(chan_error_flag[gi])
            );
        end
    endgenerate

    // Per-channel 2-FF synchronizer: chan_alarm (clk_en domain) -> alarm_sync
    // (clk_sys). Prevents CDC violations feeding controller_controller_multi.
    // chan_alarm is kept directly for alarm_led (no timing path needed there).
    logic [NUM_SENSORS-1:0] alarm_meta, alarm_sync;
    always_ff @(posedge clk_sys or posedge reset_p) begin
        if (reset_p) begin
            alarm_meta <= '0;
            alarm_sync <= '0;
        end else begin
            alarm_meta <= chan_alarm;
            alarm_sync <= alarm_meta;
        end
    end

    // -----------------------------------------------------------------------
    // UART RX — receive trigger byte 'T' (0x54) from the PC.
    // Provides an explicit Python-controlled sweep trigger so each measurement
    // is requested after the previous packet has been parsed, instead of
    // waiting for the 1 Hz fallback timer.
    // -----------------------------------------------------------------------
    logic       uart_rx_valid;
    logic [7:0] uart_rx_data;

    uart_rx u_uart_rx (
        .clk   (clk_sys),
        .reset (reset_n),
        .rx    (rx),
        .valid (uart_rx_valid),
        .data  (uart_rx_data)
    );

    // -----------------------------------------------------------------------
    // UART 'T' (0x54) receive — snapshot trigger for the Python app.
    // Receiving 'T' latches the current measurement into multi_sensor_stream
    // and transmits one packet. The controller is NOT reset here; it runs
    // autonomously and keeps display_value up-to-date at all times.
    // -----------------------------------------------------------------------
    logic uart_trigger_pulse;
    assign uart_trigger_pulse = uart_rx_valid && (uart_rx_data == 8'h54);

    // -----------------------------------------------------------------------
    // Phase controller — sweeps MMCM phase autonomously across all channels.
    // ctrl_rst_n is only the power-on / button reset; the controller
    // auto-restarts in IDLE (see controller_controller_multi.sv) without
    // needing any external periodic trigger.
    // -----------------------------------------------------------------------
    logic        ctrl_rst_n;
    logic [15:0] display_value [NUM_SENSORS-1:0];
    logic        send_unused;

    assign ctrl_rst_n = reset_n;

    controller_controller_multi #(
        .NUM_CHANNELS(NUM_SENSORS)
    ) u_ctrl (
        .clk          (clk_sys),
        .reset        (ctrl_rst_n),
        .alarm        (alarm_sync),
        .psdone       (psdone),
        .display_value(display_value),
        .change       (),           // unused: each channel's adder self-stimulates internally
        .psincdec     (psincdec_ctrl),
        .send         (send_unused),
        .psen         (psen_ctrl)
    );

    // -----------------------------------------------------------------------
    // No functional failure latch on this branch -- each rca_sensor_channel
    // exposes its own adder_error_flag (wired to the VIO for debug), but
    // there is no single cross-channel "held" concept without a further
    // protocol/display redesign. held stays tied low; kept as a signal name
    // so downstream consumers (multi_sensor_stream, held_led) don't need
    // further changes.
    // -----------------------------------------------------------------------
    logic held;
    assign held = 1'b0;

    // -----------------------------------------------------------------------
    // UART — packet serialiser → transmitter
    // Triggered by: 'T' from Python (snapshot request), or manual buttons.
    // multi_sensor_stream latches all channels at trigger time → consistent packet.
    // -----------------------------------------------------------------------
    logic uart_send_trigger;
    assign uart_send_trigger = uart_trigger_pulse | button | UARTsend;

    logic stream_send;
    logic [7:0] stream_data;

    multi_sensor_stream #(
        .NUM_CHANNELS(NUM_SENSORS)
    ) u_stream (
        .temp        ({3'b000, temp_raw}),
        .vccint      ({3'b000, vccint_raw}),
        .slack       (display_value),
        .alarm       (alarm_sync),
        .reset       (reset_n),
        .clk         (clk_sys),
        .sendin      (uart_send_trigger),
        .send        (stream_send),
        .data        (stream_data)
    );

    uart_tx u_uart (
        .clk     (clk_sys),
        .reset   (reset_n),
        .send    (stream_send),
        .data    (stream_data),
        .tx      (tx),
        .tx_busy ()
    );

    // -----------------------------------------------------------------------
    // BCD conversion for 7-segment display
    // -----------------------------------------------------------------------
    logic [3:0] phase_un, phase_dec, phase_cent, phase_mil;
    logic [3:0] phase_bil, phase_tril, phase_quadr, phase_quint;

    BinToBCD u_bcd_phase (
        .clk   (clk_sys),
        .bin   ({5'b0, display_value[0]}),   // channel 0 slack -- representative only
        .un    (phase_un),
        .dec   (phase_dec),
        .cent  (phase_cent),
        .mil   (phase_mil),
        .bil   (phase_bil),
        .tril  (phase_tril),
        .quadr (phase_quadr),
        .quint (phase_quint)
    );

    logic [3:0] err_un, err_dec, err_cent, err_mil;
    logic [3:0] err_bil, err_tril, err_quadr, err_quint;

    BinToBCD u_bcd_err (
        .clk   (clk_sys),
        .bin   (21'b0),   // no functional canary display on this branch -- always 0
        .un    (err_un),
        .dec   (err_dec),
        .cent  (err_cent),
        .mil   (err_mil),
        .bil   (err_bil),
        .tril  (err_tril),
        .quadr (err_quadr),
        .quint (err_quint)
    );

    // -----------------------------------------------------------------------
    // 7-segment multiplexed display
    // -----------------------------------------------------------------------
    logic seg0, seg1, seg2, seg3, seg4, seg5, seg6;

    DisplayController u_display (
        .clk   (clk_sys),
        .reset (reset_p),
        .in0   (err_un),
        .in1   (err_dec),
        .in2   (err_cent),
        .in3   (err_mil),
        .in4   (phase_un),
        .in5   (phase_dec),
        .in6   (phase_cent),
        .in7   (phase_mil),
        .seg0  (seg0),
        .seg1  (seg1),
        .seg2  (seg2),
        .seg3  (seg3),
        .seg4  (seg4),
        .seg5  (seg5),
        .seg6  (seg6),
        .dp    (DP),
        .an    (AN)
    );

    assign CA = seg0;
    assign CB = seg1;
    assign CC = seg2;
    assign CD = seg3;
    assign CE = seg4;
    assign CF = seg5;
    assign CG = seg6;

    // -----------------------------------------------------------------------
    // VIO debug core — observe UART packet fields and sensor state via
    // Vivado Hardware Manager without needing the UART/App connection.
    //   probe_in0 : display_value[0]    [15:0]  channel 0 slack (representative)
    //   probe_in1 : display_value[1]    [15:0]  channel 1 slack (representative)
    //   probe_in2 : alarm_sync[0]       [0]     channel 0 alarm (clk_sys domain)
    //   probe_in3 : locked              [0]     MMCM lock
    //   probe_in4 : chan_error_flag[0]  [0]     channel 0 functional-error flag
    //   probe_in5 : temp_raw            [20:0]  XADC temperature
    //   probe_in6 : vccint_raw          [20:0]  XADC VCCINT
    //   probe_in7 : display_value[2]    [15:0]  channel 2 slack (representative)
    //   probe_in8 : display_value[3]    [15:0]  channel 3 slack (representative)
    //   probe_in9 : psen_ctrl           [0]     phase shift enable (sweep activity)
    // NOTE: widths unchanged from the single-sensor VIO config so
    // create_project.tcl's vio_0 customization doesn't need to change --
    // every probe below is repointed to a representative channel (assumes
    // NUM_SENSORS >= 4). Real per-channel data goes out over
    // multi_sensor_stream; this VIO is debug-only.
    // -----------------------------------------------------------------------
    vio_0 u_vio (
        .clk       (clk_sys),
        .probe_in0 (display_value[0]),
        .probe_in1 (display_value[1]),
        .probe_in2 (alarm_sync[0]),
        .probe_in3 (locked),
        .probe_in4 (chan_error_flag[0]),
        .probe_in5 (temp_raw),
        .probe_in6 (vccint_raw),
        .probe_in7 (display_value[2]),
        .probe_in8 (display_value[3]),
        .probe_in9 (psen_ctrl)
    );

    // -----------------------------------------------------------------------
    // LEDs and debug pins
    // -----------------------------------------------------------------------
    assign alarm_led       = chan_alarm[0]; // raw clk_en signal — LED only, no timing path
    assign error_any_led   = chan_error_flag[0];
    assign held_led        = held;
    assign direction       = psincdec_ctrl;
    assign shift           = psen_ctrl;

endmodule
