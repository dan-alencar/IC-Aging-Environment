`timescale 1ns / 1ps

// Functional aging canary based on a 16-bit LUT ripple-carry adder.
//
// A free-running counter drives operand A; B is the fixed constant 0xAAAA.
// The ripple adder is the aging-sensitive path; a freely-synthesised
// reference adder gives the expected result.
//
// crit_bit = sum_canary[15] (MSB): critical path = 15 carry LUTs + 1 XOR LUT.
// ref_bit  = sum_ref[15]:          expected MSB, fed to failure_holder.
//
// On the first rising edge of alarm_sync, wrong/correct are latched so the
// UART stream can report what the adder computed vs. what it should have.
//
// error_count: increments every cycle where sum_canary != sum_ref,
//              wraps at 0xFFFF so you can see errors are still occurring.
// error_any:   sticky flag set on the first mismatch, cleared only by reset.
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
    assign crit_bit = sum_canary[15];

    logic mismatch;
    assign mismatch = (sum_canary[15:0] != sum_ref[15:0]);

    logic alarm_prev;

    always_ff @(posedge clk or negedge reset) begin
        if (!reset) begin
            a           <= '0;
            ref_bit     <= 1'b0;
            wrong       <= '0;
            correct     <= '0;
            error_count <= '0;
            error_any   <= 1'b0;
            alarm_prev  <= 1'b0;
        end else begin
            a          <= a + 1'b1;
            ref_bit    <= sum_ref[15];
            alarm_prev <= alarm;

            // Snapshot wrong/correct on first alarm edge
            if (alarm && !alarm_prev) begin
                wrong   <= sum_canary[15:0];
                correct <= sum_ref[15:0];
            end

            // Running error counter (wrapping)
            if (mismatch)
                error_count <= error_count + 1'b1;

            // Sticky error flag
            if (mismatch)
                error_any <= 1'b1;
        end
    end
endmodule
