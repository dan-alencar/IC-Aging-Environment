`timescale 1ns / 1ps

// N-bit LUT-based ripple carry adder. Each stage is a lut_full_adder instance
// chained through carry. DONT_TOUCH on every instance forces Vivado to keep
// the full O(N) carry chain intact — the aging-sensitive critical path.
module ripple_adder #(parameter int N = 16) (
    input  logic [N-1:0] a,
    input  logic [N-1:0] b,
    output logic [N:0]   sum   // sum[N-1:0] = result, sum[N] = carry-out
);
    logic [N:0] carry;
    assign carry[0] = 1'b0;

    for (genvar i = 0; i < N; i++) begin : FA
        (* DONT_TOUCH = "yes" *)
        lut_full_adder fa (
            .a   (a[i]),
            .b   (b[i]),
            .cin (carry[i]),
            .sum (sum[i]),
            .cout(carry[i+1])
        );
    end

    assign sum[N] = carry[N];
endmodule
