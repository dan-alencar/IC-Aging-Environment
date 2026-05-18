`timescale 1ns / 1ps

// Phase-sweep FSM for the metastability/aging sensor.
//
// State machine:
//   IDLE   (2'b00) — request a phase shift; jump to ALARM if alarm detected
//   SHIFT  (2'b01) — assert psen for one cycle
//   WAIT   (2'b10) — wait for MMCM psdone handshake
//   ALARM  (2'b11) — alarm detected; hold display_value and assert send pulse
//
// Fixes vs. original:
//   - Combinational next-state block uses always@(*) + blocking assignments;
//     original used non-blocking in a combinational block (sim/synth mismatch).
//   - alarm is now in the sensitivity list (was missing → stale next_state).
//   - State ALARM now self-loops (next_state = ALARM); original left next_state
//     unassigned, inferring a latch that kept the FSM stuck by accident.
//   - psdone is no longer used as a clock edge for inc_count; rising-edge
//     detection on clk_sys replaces always@(posedge psdone) to avoid routing
//     a data signal through a clock net (Vivado DRC warning).
//   - sig_ant always block now has a proper else branch (was executing the
//     assignment unconditionally, even during reset).
//   - initial blocks removed (ignored by synthesis; reset handles init).
module controller_controller (
    input             clk,
    input             reset,     // active-low
    input             alarm,
    input             psdone,
    output reg [15:0] display_value,
    output reg        change,
    output reg        psincdec,
    output            send,
    output reg        psen
);

    // -----------------------------------------------------------------------
    // State encoding
    // -----------------------------------------------------------------------
    localparam IDLE  = 2'b00;
    localparam SHIFT = 2'b01;
    localparam WAIT  = 2'b10;
    localparam ALARM = 2'b11;

    reg [1:0]  state, next_state;
    reg [15:0] inc_count;
    reg        signal, sig_ant;
    reg        change_enable;
    reg        psdone_prev;

    // -----------------------------------------------------------------------
    // Sequential: state register
    // -----------------------------------------------------------------------
    always @(posedge clk or negedge reset) begin
        if (!reset)
            state <= IDLE;
        else
            state <= next_state;
    end

    // -----------------------------------------------------------------------
    // Combinational: next-state and output logic
    // Blocking assignments + always@(*) — no latches, correct simulation.
    // -----------------------------------------------------------------------
    always @(*) begin
        // Safe defaults for every output driven here — prevents latches
        next_state    = state;
        change_enable = 1'b1;
        signal        = 1'b0;
        psen          = 1'b0;
        psincdec      = 1'b0;

        case (state)
            IDLE: begin
                if (alarm) next_state = ALARM;
                else       next_state = SHIFT;
            end
            SHIFT: begin
                psen       = 1'b1;
                next_state = WAIT;
            end
            WAIT: begin
                if (psdone) next_state = IDLE;
                else        next_state = WAIT;
            end
            ALARM: begin
                change_enable = 1'b0;
                signal        = 1'b1;
                next_state    = ALARM; // hold until reset
            end
        endcase
    end

    // -----------------------------------------------------------------------
    // change toggle (output unused in pure-RTL flow; kept for wiring compat.)
    // -----------------------------------------------------------------------
    always @(posedge clk) begin
        if (change_enable)
            change <= ~change;
    end

    // -----------------------------------------------------------------------
    // Phase-shift counter: counts completed MMCM phase shifts.
    // Uses synchronous edge detection on psdone — avoids routing a data
    // signal through a clock net.
    // -----------------------------------------------------------------------
    always @(posedge clk or negedge reset) begin
        if (!reset) begin
            inc_count   <= 16'h0;
            psdone_prev <= 1'b0;
        end else begin
            psdone_prev <= psdone;
            if (psdone && !psdone_prev)
                inc_count <= inc_count + 1'b1;
        end
    end

    // -----------------------------------------------------------------------
    // Capture display value on entry to ALARM state
    // -----------------------------------------------------------------------
    always @(posedge clk or negedge reset) begin
        if (!reset)
            display_value <= 16'h0;
        else if (state == IDLE && alarm)
            display_value <= inc_count;
    end

    // -----------------------------------------------------------------------
    // One-cycle send pulse when signal goes 0→1
    // -----------------------------------------------------------------------
    always @(posedge clk or negedge reset) begin
        if (!reset)
            sig_ant <= 1'b0;
        else
            sig_ant <= signal;
    end

    assign send = ~sig_ant && signal;

endmodule
