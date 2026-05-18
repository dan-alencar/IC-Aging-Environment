`timescale 1ns / 1ps

// Phase-sweep FSM for the metastability/aging sensor.
//
// On each alarm the measured phase count is captured and a one-cycle
// retrigger pulse is raised.  The top module latches this on CLK100MHZ
// and holds the MMCM in reset until it relocks, giving a clean restart
// from 0° phase for every new measurement.
//
// Two reset domains:
//   reset      — active-low, ~(button | ~locked): resets FSM + counters
//   hard_reset — active-low, ~button only:        resets display_value
//                (display_value survives the MMCM relock period so the
//                 7-segment display and VIO show the last measurement)
//
// States:
//   IDLE  — step phase each cycle; jump to ALARM if alarm detected
//   SHIFT — assert psen for one clock (psincdec=0, decrement)
//   WAIT  — wait for MMCM psdone; increment inc_count on each ack
//   ALARM — capture display_value; generate send + retrigger pulses; → IDLE
module controller_controller (
    input  logic             clk,
    input  logic             reset,       // active-low: ~(button | ~locked)
    input  logic             hard_reset,  // active-low: ~button only
    input  logic             alarm,
    input  logic             psdone,
    output logic [15:0]      display_value,
    output logic             change,
    output logic             psincdec,
    output logic             send,
    output logic             psen,
    output logic             retrigger    // one-cycle pulse → triggers MMCM reset
);

    typedef enum logic [1:0] {
        IDLE  = 2'b00,
        SHIFT = 2'b01,
        WAIT  = 2'b10,
        ALARM = 2'b11
    } state_t;

    state_t      state;
    logic [15:0] inc_count;
    logic        signal, sig_ant;
    logic        psdone_prev;

    // FSM, counters, and change toggle — reset by the full reset (includes ~locked)
    always_ff @(posedge clk or negedge reset) begin
        if (!reset) begin
            state       <= IDLE;
            inc_count   <= '0;
            psdone_prev <= 1'b0;
            sig_ant     <= 1'b0;
            change      <= 1'b0;
        end else begin
            sig_ant     <= signal;
            psdone_prev <= psdone;

            case (state)
                IDLE: begin
                    if (alarm) state <= ALARM;
                    else begin
                        change <= ~change;
                        state  <= SHIFT;
                    end
                end
                SHIFT: state <= WAIT;
                WAIT: begin
                    if (psdone && !psdone_prev) begin
                        inc_count <= inc_count + 1'b1;
                        state     <= IDLE;
                    end
                end
                ALARM: state <= IDLE;  // one cycle; MMCM reset via retrigger
                default: state <= IDLE;
            endcase
        end
    end

    // display_value — only reset on button press so it survives MMCM relock
    always_ff @(posedge clk or negedge hard_reset) begin
        if (!hard_reset)             display_value <= '0;
        else if (state == IDLE && alarm) display_value <= inc_count;
    end

    // Combinational outputs
    always_comb begin
        signal   = 1'b0;
        psen     = 1'b0;
        psincdec = 1'b0;
        if (state == SHIFT) begin psen = 1'b1; psincdec = 1'b0; end
        if (state == ALARM) signal = 1'b1;
    end

    assign retrigger = (state == ALARM);  // high for one clk cycle on alarm
    assign send = signal && !sig_ant;

endmodule
