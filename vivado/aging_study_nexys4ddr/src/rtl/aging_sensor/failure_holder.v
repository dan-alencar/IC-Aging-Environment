`timescale 1ns / 1ps

// Sticky functional-failure latch.
//
// Triggers when the sensor path output (ff2 = sensor_ff1_out, i.e. crit_bit
// captured on clk_sys) rises while the reference output (ff1 = ref_bit,
// i.e. sum_ref[15] registered on clk_sys) disagrees.  This detects the case
// where the aging-sensitive adder computes 1 when the reference says 0 (or
// vice-versa) at the moment the sensor captures a rising transition.
//
// The original design used posedge ff2 directly as a clock edge, which
// creates a "clock from logic" DRC error in Vivado and leaves the path
// unconstrained for timing.  This version uses a proper synchronous edge
// detector on clk_sys instead.
module failure_holder (
    input      clk,    // clk_sys — system clock
    input      ff1,    // ref_bit: expected MSB of adder result (clk_sys domain)
    input      ff2,    // sensor_ff1_out: captured MSB from canary  (clk_sys domain)
    input      reset,  // active-low asynchronous reset
    output reg held
);
    reg ff2_prev;

    always @(posedge clk or negedge reset) begin
        if (!reset) begin
            held     <= 1'b0;
            ff2_prev <= 1'b0;
        end else begin
            ff2_prev <= ff2;
            // Rising edge of ff2: sensor just captured a 1.
            // If ff1 disagrees at this moment, record a functional failure.
            if (ff2 && !ff2_prev && (ff1 != ff2))
                held <= 1'b1;
        end
    end
endmodule
