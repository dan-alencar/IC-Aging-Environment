`timescale 1ns / 1ps

// Phase-sweep FSM for the metastability/aging sensor.
//
// States:
//   IDLE  — request a phase shift each cycle; jump to ALARM if alarm detected
//   SHIFT — assert psen for one clock cycle
//   WAIT  — wait for MMCM psdone handshake
//   ALARM — alarm detected; hold display_value, generate one-cycle send pulse
module controller_controller (
    input  logic             clk,
    input  logic             reset,     // active-low
    input  logic             alarm,
    input  logic             psdone,
    output logic [15:0]      display_value,
    output logic             change,
    output logic             psincdec,
    output logic             send,
    output logic             psen
);

    typedef enum logic [1:0] {
        IDLE  = 2'b00,
        SHIFT = 2'b01,
        WAIT  = 2'b10,
        ALARM = 2'b11
    } state_t;

    state_t       state, next_state;
    logic [15:0]  inc_count;
    logic         signal, sig_ant;
    logic         change_enable;
    logic         psdone_prev;

    // --- Sequential: state register ---
    always_ff @(posedge clk or negedge reset) begin
        if (!reset) state <= IDLE;
        else        state <= next_state;
    end

    // --- Combinational: next-state and output logic ---
    always_comb begin
        next_state    = state;
        change_enable = 1'b1;
        signal        = 1'b0;
        psen          = 1'b0;
        psincdec      = 1'b0;

        case (state)
            IDLE:  begin
                if (alarm) next_state = ALARM;
                else       next_state = SHIFT;
            end
            SHIFT: begin
                psen       = 1'b1;
                next_state = WAIT;
            end
            WAIT:  begin
                if (psdone) next_state = IDLE;
                else        next_state = WAIT;
            end
            ALARM: begin
                change_enable = 1'b0;
                signal        = 1'b1;
                next_state    = ALARM;
            end
        endcase
    end

    // --- change toggle (output unused in pure-RTL flow) ---
    always_ff @(posedge clk or negedge reset) begin
        if (!reset)             change <= 1'b0;
        else if (change_enable) change <= ~change;
    end

    // --- Phase-shift counter: synchronous psdone edge detection ---
    always_ff @(posedge clk or negedge reset) begin
        if (!reset) begin
            inc_count   <= '0;
            psdone_prev <= 1'b0;
        end else begin
            psdone_prev <= psdone;
            if (psdone && !psdone_prev)
                inc_count <= inc_count + 1'b1;
        end
    end

    // --- Capture display value on entry to ALARM state ---
    always_ff @(posedge clk or negedge reset) begin
        if (!reset)                    display_value <= '0;
        else if (state == IDLE && alarm) display_value <= inc_count;
    end

    // --- One-cycle send pulse ---
    always_ff @(posedge clk or negedge reset) begin
        if (!reset) sig_ant <= 1'b0;
        else        sig_ant <= signal;
    end

    assign send = ~sig_ant && signal;

endmodule
