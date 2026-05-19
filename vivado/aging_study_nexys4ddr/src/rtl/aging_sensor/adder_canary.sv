`timescale 1ns / 1ps

// Dual-adder aging sensor: sensor adder for timing measurement, canary adder
// for functional error detection.  Both are structurally identical 16-bit LUT
// ripple-carry adder instances so they age at the same rate.
//
// Sensor adder (u_sensor): driven by a toggle FF so its MSB transitions every
//   clock cycle (worst-case carry through all 16 stages each time).
//   crit_bit = sum_sensor[15]: always-toggling input to modern_sensible →
//   deterministic phase measurement (restores ±2-step jitter vs. old ~9000).
//
// Canary adder (u_canary): free-running counter A, constant B = 0xAAAA.
//   ref_bit  = sum_ref[15]: expected MSB, fed to failure_holder.
//   wrong/correct/error_count: functional error metrics.
//
// On the first rising edge of alarm_sync, wrong/correct are latched.
// error_count increments every cycle where sum_canary != sum_ref (wraps at 0xFFFF).
// error_any:  sticky flag set on first mismatch, cleared only by reset.
module adder_canary (
    input  logic        clk,
    input  logic        reset,    // active-low
    input  logic        alarm,    // alarm_sync from top (clk_sys domain)
    output logic        crit_bit,
    output logic        ref_bit,
    output logic [15:0] wrong,
    output logic [15:0] correct,
    output logic [15:0] error_count,
    output logic        error_any
);
    localparam logic [15:0] B = 16'hAAAA;

    // --- Canary adder: free-running counter ---
    logic [15:0] a;
    logic [16:0] sum_canary;  // aging-sensitive: LUT ripple carry
    logic [16:0] sum_ref;     // reference: freely synthesised (may use CARRY4)

    (* DONT_TOUCH = "yes" *)
    ripple_adder #(.N(16)) u_canary (
        .a  (a),
        .b  (B),
        .sum(sum_canary)
    );

    assign sum_ref = {1'b0, a} + {1'b0, B};

    // --- Sensor adder: worst-case toggle pattern ---
    // toggle alternates every cycle; a_sensor selects the two boundary values
    // that force a full 16-stage carry on every transition of sum_sensor[15].
    logic        toggle;
    logic [15:0] a_sensor;
    logic [16:0] sum_sensor;

    assign a_sensor = toggle ? 16'h5556 : 16'h5555;

    (* DONT_TOUCH = "yes" *)
    ripple_adder #(.N(16)) u_sensor (
        .a  (a_sensor),
        .b  (B),
        .sum(sum_sensor)
    );

    // crit_bit toggles every cycle — deterministic input to modern_sensible
    assign crit_bit = sum_sensor[15];

    logic mismatch;
    assign mismatch = (sum_canary[15:0] != sum_ref[15:0]);

    logic alarm_prev;

    always_ff @(posedge clk or negedge reset) begin
        if (!reset) begin
            a           <= '0;
            toggle      <= 1'b0;
            ref_bit     <= 1'b0;
            wrong       <= '0;
            correct     <= '0;
            error_count <= '0;
            error_any   <= 1'b0;
            alarm_prev  <= 1'b0;
        end else begin
            a          <= a + 1'b1;
            toggle     <= ~toggle;
            ref_bit    <= sum_ref[15];
            alarm_prev <= alarm;

            if (alarm && !alarm_prev) begin
                wrong   <= sum_canary[15:0];
                correct <= sum_ref[15:0];
            end

            if (mismatch)
                error_count <= error_count + 1'b1;

            if (mismatch)
                error_any <= 1'b1;
        end
    end
endmodule
