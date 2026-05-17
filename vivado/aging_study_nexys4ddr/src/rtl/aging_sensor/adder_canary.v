`timescale 1ns / 1ps

// Functional aging canary based on a 16-bit LUT ripple-carry adder.
//
// A free-running counter drives operand A; B is the fixed constant 0xAAAA.
// The ripple adder is the aging-sensitive path; a freely-synthesized
// reference adder gives the expected result.
//
// crit_bit = sum_canary[15] (MSB): path = 15 carry LUTs + 1 XOR LUT = 16 stages.
// ref_bit  = sum_ref[15]:          expected MSB, drives failure_holder/ff1.
//
// On the first rising edge of alarm, wrong/correct are latched so the UART
// stream can report what the adder computed vs. what it should have computed.
//
// error_count: increments every clock cycle where sum_canary != sum_ref,
//              saturates at 0xFFFF. Gives a running rate of functional failures.
//
// error_any: sticky flag set on the first mismatch, cleared only by reset.
//            Used to drive an LED for immediate visual indication.
//
// BD connections (replaces not_series_0):
//   crit_bit    → modern_sensible_0/in_sensor
//   ref_bit     → failure_holder_0/ff1
//   wrong       → sensor_stream_0/wrong
//   correct     → sensor_stream_0/correct
//   error_count → sensor_stream_0/error_count, BinToBCD_1/bin
//   error_any   → LED[1] top-level port
//   alarm       ← modern_sensible_0/alarm
//   clk         ← clk_wiz_0/clk_sys
//   reset       ← reset port (active-low)
module adder_canary (
    input  clk,
    input  reset,
    input  alarm,
    output wire        crit_bit,
    output reg         ref_bit,
    output reg  [15:0] wrong,
    output reg  [15:0] correct,
    output reg  [15:0] error_count,
    output reg         error_any
);
    localparam [15:0] B = 16'hAAAA;

    reg  [15:0] a;
    wire [16:0] sum_canary;  // aging-sensitive: LUT ripple carry
    wire [16:0] sum_ref;     // reference: freely synthesized (may use CARRY4)

    (* DONT_TOUCH = "yes" *)
    ripple_adder #(.N(16)) u_canary (
        .a(a),
        .b(B),
        .sum(sum_canary)
    );

    assign sum_ref = {1'b0, a} + {1'b0, B};

    assign crit_bit = sum_canary[15];

    wire mismatch = (sum_canary[15:0] != sum_ref[15:0]);

    reg alarm_prev;

    always @(posedge clk or negedge reset) begin
        if (!reset) begin
            a           <= 16'h0;
            ref_bit     <= 1'b0;
            wrong       <= 16'h0;
            correct     <= 16'h0;
            error_count <= 16'h0;
            error_any   <= 1'b0;
            alarm_prev  <= 1'b0;
        end else begin
            a          <= a + 1'b1;
            ref_bit    <= sum_ref[15];
            alarm_prev <= alarm;

            // Latch wrong/correct snapshot on first alarm edge
            if (alarm && !alarm_prev) begin
                wrong   <= sum_canary[15:0];
                correct <= sum_ref[15:0];
            end

            // Running error counter: increment every cycle with a mismatch
            if (mismatch && error_count != 16'hFFFF)
                error_count <= error_count + 1'b1;

            // Sticky error flag: set on first mismatch, never clears without reset
            if (mismatch)
                error_any <= 1'b1;
        end
    end
endmodule
