// N-channel phase-sweep controller.
//
// The single-sensor controller_controller.v/.sv drives one shared MMCM
// dynamic-phase-shift interface (psen/psincdec/psdone/psclk) -- there is
// only one of those per clock wizard, so N sensor channels cannot each run
// an independent phase sweep at the same time. This module keeps exactly
// one shared sweep engine, but lets every channel observe it in parallel
// and independently latch its own result: each channel gets a sticky
// "already latched" bit, and snapshots the current phase-step count
// (inc_count) the first time its own alarm bit fires during a sweep pass.
// The sweep keeps decrementing phase (bounded by MAX_SHIFT, so a pass
// always terminates even if some channel never trips) until every channel
// has latched, then reports all N results together, restores phase, and
// autonomously starts the next pass -- giving genuinely simultaneous,
// directly-comparable per-channel data with no mux and no per-channel
// phase-shift hardware.
//
// FSM states/semantics otherwise match controller_controller.v/.sv
// (CHECK_ALARM -> INIT_SHIFT -> WAIT_SHIFT -> DONE -> RESET_PHASE ->
// WAIT_RESET -> IDLE), generalized to arrays where needed.
module controller_controller_multi #(
    parameter int NUM_CHANNELS = 4,
    parameter logic [15:0] MAX_SHIFT = 16'hFFFF   // sweep safety bound
) (
    input  logic                    clk,
    input  logic                    reset,        // active-low, async
    input  logic [NUM_CHANNELS-1:0] alarm,
    input  logic                    psdone,
    output logic [15:0]             display_value [NUM_CHANNELS-1:0],
    output logic                    change,
    output logic                    psincdec,
    output logic                    send,
    output logic                    psen,
    output logic [2:0]              debug_state
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

    state_t state, next_state;
    assign debug_state = state;

    // psdone edge-detect (clk_sys domain) -- avoids double-counting if
    // psdone stays high across more than one clk cycle.
    logic psdone_prev, psdone_edge;
    always_ff @(posedge clk or negedge reset) begin
        if (!reset) psdone_prev <= 1'b0;
        else        psdone_prev <= psdone;
    end
    assign psdone_edge = psdone && !psdone_prev;

    logic change_enable;
    logic [15:0] inc_count, reset_count;
    logic [NUM_CHANNELS-1:0] latched;
    logic all_latched;
    assign all_latched = &latched;

    logic signal, sig_ant;
    assign send = ~sig_ant && signal;

    always_ff @(posedge clk or negedge reset) begin
        if (!reset) sig_ant <= 1'b0;
        else        sig_ant <= signal;
    end

    // Toggle generator for the critical-path stimulus -- shared across
    // every channel (each channel's own adder free-runs internally; this
    // `change` output is only used by branches whose critical path needs
    // an external toggle, e.g. an inverter chain. Kept here for interface
    // parity with controller_controller.v/.sv).
    always_ff @(posedge clk or negedge reset) begin
        if (!reset)          change <= 1'b0;
        else if (change_enable) change <= ~change;
    end

    always_ff @(posedge clk or negedge reset) begin
        if (!reset) state <= CHECK_ALARM;
        else        state <= next_state;
    end

    always_comb begin
        next_state    = state;
        change_enable = 1'b0;
        psincdec      = 1'b0;
        psen          = 1'b0;
        signal        = 1'b0;

        case (state)
            CHECK_ALARM: begin
                change_enable = 1'b1;
                if (all_latched || (inc_count >= MAX_SHIFT))
                    next_state = DONE;
                else
                    next_state = INIT_SHIFT;
            end
            INIT_SHIFT: begin
                change_enable = 1'b1;
                psen          = 1'b1;
                next_state    = WAIT_SHIFT;
            end
            WAIT_SHIFT: begin
                change_enable = 1'b1;
                next_state    = psdone_edge ? CHECK_ALARM : WAIT_SHIFT;
            end
            DONE: begin
                signal     = 1'b1;
                next_state = RESET_PHASE;
            end
            RESET_PHASE: begin
                psincdec = 1'b1;
                if (reset_count >= inc_count) begin
                    next_state = IDLE;
                end else begin
                    psen       = 1'b1;
                    next_state = WAIT_RESET;
                end
            end
            WAIT_RESET: begin
                psincdec   = 1'b1;
                next_state = psdone_edge ? RESET_PHASE : WAIT_RESET;
            end
            IDLE: begin
                next_state = CHECK_ALARM;   // autonomous: start the next sweep pass
            end
            default: next_state = CHECK_ALARM;
        endcase
    end

    // Per-channel latch + shared phase counters. Cleared at the start of
    // every sweep pass (IDLE -> CHECK_ALARM) so each pass is an
    // independent, directly-comparable measurement across all channels.
    // A channel that never trips within MAX_SHIFT keeps display_value at
    // MAX_SHIFT (maximum-margin sentinel), not 0 -- 0 would be
    // indistinguishable from "tripped immediately".
    always_ff @(posedge clk or negedge reset) begin
        if (!reset) begin
            inc_count   <= 16'd0;
            reset_count <= 16'd0;
            latched     <= '0;
            for (int i = 0; i < NUM_CHANNELS; i++) display_value[i] <= MAX_SHIFT;
        end else if (state == IDLE) begin
            inc_count   <= 16'd0;
            reset_count <= 16'd0;
            latched     <= '0;
            for (int i = 0; i < NUM_CHANNELS; i++) display_value[i] <= MAX_SHIFT;
        end else begin
            if (state == CHECK_ALARM) begin
                for (int i = 0; i < NUM_CHANNELS; i++) begin
                    if (alarm[i] && !latched[i]) begin
                        latched[i]       <= 1'b1;
                        display_value[i] <= inc_count;
                    end
                end
            end
            if (psdone_edge) begin
                if (!psincdec) inc_count   <= inc_count + 16'd1;
                else           reset_count <= reset_count + 16'd1;
            end
        end
    end

endmodule
