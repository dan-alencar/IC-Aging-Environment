`timescale 1ns / 1ps

// Sticky functional-failure latch.
//
// Triggers when the sensor path output (ff2 = sensor_ff1_out, i.e. crit_bit
// captured on clk_sys) rises while the reference output (ff1 = ref_bit,
// i.e. sum_ref[15] registered on clk_sys) disagrees.
module failure_holder (
    input  logic clk,    // clk_sys
    input  logic ff1,    // ref_bit: expected MSB of adder result
    input  logic ff2,    // sensor_ff1_out: captured MSB from canary
    input  logic reset,  // active-low asynchronous reset
    output logic held
);
    logic ff2_prev;

    always_ff @(posedge clk or negedge reset) begin
        if (!reset) begin
            held     <= 1'b0;
            ff2_prev <= 1'b0;
        end else begin
            ff2_prev <= ff2;
            if (ff2 && !ff2_prev && (ff1 != ff2))
                held <= 1'b1;
        end
    end
endmodule
