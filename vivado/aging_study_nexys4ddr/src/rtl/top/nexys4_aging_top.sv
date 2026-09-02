`timescale 1ns / 1ps

// Top-level module for the Nexys4 DDR aging study (pure RTL, no block design).
//
// Signal conventions:
//   reset_n  — active-low derived from BTNU (N17); fed to RTL modules that use
//              negedge-reset (controller, adder, failure, stream, uart, temp).
//   reset_p  — active-high (raw button); fed to modules that use posedge-reset
//              (DisplayController) or FDCE CLR (modern_sensible).
//
// Clock domains:
//   clk_sys : 0°  100 MHz — main system clock
//   psclk   : 0°, dynamically phase-shiftable — FF1 in modern_sensible
//   clk_en  : 100° fixed offset 100 MHz — FF3 (alarm latch) in modern_sensible
//
// alarm_sig originates in the clk_en domain (FF3 Q-output).
// alarm_sync is a 2-FF synchronised version for all clk_sys-domain consumers.
//
// Display layout (8 digits):
//   AN[7:4] / in4..in7 — phase step count  (left  4 digits)
//   AN[3:0] / in0..in3 — error count       (right 4 digits)

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
    output logic        held_led,     // J13 — tied low on this branch (no functional canary)
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
    // Metastability sensor — 3-FF XOR comparator across phase-shifted domains
    //   FF1: psclk (phase-shifted)   → samples crit_bit
    //   FF2: clk_sys (reference)     → samples crit_bit
    //   FF3: clk_en  (100° offset)   → latches XOR(FF1, FF2) = alarm_sig
    // -----------------------------------------------------------------------
    logic        alarm_sig;           // clk_en domain: FF3 Q-output
    logic        sensor_ff1_out;      // FF2 output of modern_sensible (clk_sys domain)

    modern_sensible u_sensor (
        .sclk      (clk_sys),
        .psclk     (psclk),
        .in_sensor (crit_bit),
        .reset     (reset_p),   // FDCE CLR is active-high
        .clk_en    (clk_en),
        .alarm     (alarm_sig),
        .ff1_out   (sensor_ff1_out)
    );

    // -----------------------------------------------------------------------
    // 2-FF synchronizer: alarm_sig (clk_en domain) → alarm_sync (clk_sys).
    // Prevents CDC violations in controller_controller.
    // alarm_sig is kept directly for the alarm_led (no timing path needed).
    // -----------------------------------------------------------------------
    logic alarm_meta, alarm_sync;
    always_ff @(posedge clk_sys or posedge reset_p) begin
        if (reset_p) begin
            alarm_meta <= 1'b0;
            alarm_sync <= 1'b0;
        end else begin
            alarm_meta <= alarm_sig;
            alarm_sync <= alarm_meta;
        end
    end

    // -----------------------------------------------------------------------
    // Critical path — 50-stage inverter chain (timing-only, no functional
    // canary: an inverter chain has no "expected value" to compare against,
    // unlike adder_canary's dual-adder mismatch check).
    // -----------------------------------------------------------------------
    logic crit_bit;
    logic crit_start;
    logic ctrl_change;

    not_series #(
        .size(50)
    ) u_delay_line (
        .clk      (clk_sys),
        .test_bit (ctrl_change),   // toggle stimulus from the controller
        .start    (crit_start),    // debug: registered launch edge
        .critpath (crit_bit)
    );

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
    // Receiving 'T' latches the current measurement into sensor_stream and
    // transmits one 15-byte packet.  The controller is NOT reset here; it
    // runs autonomously and keeps display_value up-to-date at all times.
    // -----------------------------------------------------------------------
    logic uart_trigger_pulse;
    assign uart_trigger_pulse = uart_rx_valid && (uart_rx_data == 8'h54);

    // -----------------------------------------------------------------------
    // Phase controller — sweeps MMCM phase autonomously.
    // ctrl_rst_n is only the power-on / button reset; the controller
    // auto-restarts in IDLE (see controller_controller.sv) without needing
    // any external periodic trigger.
    // -----------------------------------------------------------------------
    logic        ctrl_rst_n;
    logic [15:0] display_value;
    logic        send_unused;

    assign ctrl_rst_n = reset_n;

    controller_controller u_ctrl (
        .clk          (clk_sys),
        .reset        (ctrl_rst_n),
        .alarm        (alarm_sync),
        .psdone       (psdone),
        .display_value(display_value),
        .change       (ctrl_change),   // drives the inverter chain's toggle input
        .psincdec     (psincdec_ctrl),
        .send         (send_unused),
        .psen         (psen_ctrl)
    );

    // -----------------------------------------------------------------------
    // No functional failure latch on this branch — failure_holder compared
    // adder_canary's ref_bit against modern_sensible's captured bit, and
    // there is no reference/expected value for a pure timing sensor.
    // held stays tied low; kept as a signal name so downstream consumers
    // (sensor_stream, held_led) don't need further changes.
    // -----------------------------------------------------------------------
    logic held;
    assign held = 1'b0;

    // -----------------------------------------------------------------------
    // UART — packet serialiser → transmitter
    // Triggered by: 'T' from Python (snapshot request), or manual buttons.
    // sensor_stream latches all inputs at trigger time → consistent packet.
    // -----------------------------------------------------------------------
    logic uart_send_trigger;
    assign uart_send_trigger = uart_trigger_pulse | button | UARTsend;

    logic stream_send;
    logic [7:0] stream_data;

    sensor_stream u_stream (
        .temp        ({3'b000, temp_raw}),
        .vccint      ({3'b000, vccint_raw}),
        .sensor      (display_value),
        .failure     (held),
        .wrong       (16'b0),
        .correct     (16'b0),
        .error_count (16'b0),
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
        .bin   ({5'b0, display_value}),
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
        .bin   (21'b0),   // no functional canary on this branch -- always 0
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
    //   probe_in0 : display_value  [15:0]  phase count at alarm
    //   probe_in1 : (tied 0)       [15:0]  no functional canary on this branch
    //   probe_in2 : alarm_sync     [0]     alarm (clk_sys domain)
    //   probe_in3 : locked         [0]     MMCM lock
    //   probe_in4 : (tied 0)       [0]     no functional canary on this branch
    //   probe_in5 : temp_raw       [20:0]  XADC temperature
    //   probe_in6 : vccint_raw     [20:0]  XADC VCCINT
    //   probe_in7 : (tied 0)       [15:0]  no functional canary on this branch
    //   probe_in8 : (tied 0)       [15:0]  no functional canary on this branch
    //   probe_in9 : psen_ctrl      [0]     phase shift enable (sweep activity)
    // -----------------------------------------------------------------------
    vio_0 u_vio (
        .clk       (clk_sys),
        .probe_in0 (display_value),
        .probe_in1 (16'b0),
        .probe_in2 (alarm_sync),
        .probe_in3 (locked),
        .probe_in4 (1'b0),
        .probe_in5 (temp_raw),
        .probe_in6 (vccint_raw),
        .probe_in7 (16'b0),
        .probe_in8 (16'b0),
        .probe_in9 (psen_ctrl)
    );

    // -----------------------------------------------------------------------
    // LEDs and debug pins
    // -----------------------------------------------------------------------
    assign alarm_led       = alarm_sig;    // raw clk_en signal — LED only, no timing path
    assign error_any_led   = 1'b0;         // no functional canary on this branch
    assign held_led        = held;
    assign direction       = psincdec_ctrl;
    assign shift           = psen_ctrl;

endmodule
