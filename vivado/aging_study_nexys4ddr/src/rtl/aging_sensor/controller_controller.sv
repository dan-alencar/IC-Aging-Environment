`timescale 1ns / 1ps

// Phase-sweep FSM for the metastability/aging sensor.
// Ported from sbcci_fpga_aging/controller_controller.v — same states,
// same back-off logic, clean synchronous SystemVerilog.
//
// Continuous autonomous measurement — no external trigger required:
//   CHECK_ALARM  — sweep if clear, capture immediately if alarm already high
//   INIT_SHIFT   — assert psen=1 / psincdec=0 for one cycle (decrement phase)
//   WAIT_SHIFT   — wait for psdone; inc_count++; back to CHECK_ALARM
//   DONE         — latch display_value=inc_count; start back-off
//   RESET_PHASE  — if reset_count >= inc_count → IDLE; else psen=1/psincdec=1
//   WAIT_RESET   — wait for psdone; reset_count++; back to RESET_PHASE
//   IDLE         — reset inc_count/reset_count; immediately → CHECK_ALARM
//
// display_value is updated exactly once per sweep (in DONE) and held in IDLE.
// As the device ages and the critical path degrades, the alarm fires after
// fewer phase steps → display_value decreases over time.
module controller_controller (
    input  logic         clk,
    input  logic         reset,     // active-low; pulsed periodically by top
    input  logic         alarm,
    input  logic         psdone,
    output logic [15:0]  display_value,
    output logic         change,    // sweep-activity toggle (indicator only)
    output logic         psincdec,
    output logic         send,
    output logic         psen
);

    typedef enum logic [2:0] {
        CHECK_ALARM = 3'b000,
        INIT_SHIFT  = 3'b001,
        WAIT_SHIFT  = 3'b010,
        DONE        = 3'b011,
        RESET_PHASE = 3'b100,
        WAIT_RESET  = 3'b101,
        IDLE        = 3'b110
    } state_t;

    state_t      state;
    logic [15:0] inc_count;
    logic [15:0] reset_count;
    logic        signal, sig_ant;
    logic        psdone_prev;

    always_ff @(posedge clk or negedge reset) begin
        if (!reset) begin
            state       <= CHECK_ALARM;
            inc_count   <= '0;
            reset_count <= '0;
            psdone_prev <= 1'b0;
            sig_ant     <= 1'b0;
            change      <= 1'b0;
        end else begin
            sig_ant     <= signal;
            psdone_prev <= psdone;

            case (state)
                CHECK_ALARM: begin
                    change <= ~change;
                    state  <= alarm ? DONE : INIT_SHIFT;
                end

                INIT_SHIFT: state <= WAIT_SHIFT;

                WAIT_SHIFT: begin
                    if (psdone && !psdone_prev) begin
                        inc_count <= inc_count + 1'b1;
                        state     <= CHECK_ALARM;
                    end
                end

                DONE: state <= RESET_PHASE;

                RESET_PHASE: begin
                    if (reset_count >= inc_count)
                        state <= IDLE;
                    else
                        state <= WAIT_RESET;
                end

                WAIT_RESET: begin
                    if (psdone && !psdone_prev) begin
                        reset_count <= reset_count + 1'b1;
                        state       <= RESET_PHASE;
                    end
                end

                IDLE: begin
                    // Auto-restart: reset sweep counters and begin next measurement
                    // immediately without waiting for an external trigger.
                    inc_count   <= '0;
                    reset_count <= '0;
                    state       <= CHECK_ALARM;
                end

                default: state <= CHECK_ALARM;
            endcase
        end
    end

    // display_value latched in DONE, held through back-off and IDLE
    always_ff @(posedge clk or negedge reset) begin
        if (!reset)
            display_value <= '0;
        else if (state == DONE)
            display_value <= inc_count;
    end

    always_comb begin
        signal   = 1'b0;
        psen     = 1'b0;
        psincdec = 1'b0;
        case (state)
            DONE:       signal = 1'b1;
            INIT_SHIFT: psen   = 1'b1;                // psincdec=0: decrement (forward)
            RESET_PHASE: begin
                psincdec = 1'b1;
                if (reset_count < inc_count) psen = 1'b1; // increment (back-off)
            end
            WAIT_RESET: psincdec = 1'b1;
            default: ;
        endcase
    end

    assign send = signal && !sig_ant;

endmodule
