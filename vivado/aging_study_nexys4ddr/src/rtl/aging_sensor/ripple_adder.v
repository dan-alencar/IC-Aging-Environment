`timescale 1ns / 1ps

// N-bit LUT-based ripple carry adder. Each stage is a lut_full_adder instance
// chained through carry. DONT_TOUCH on every instance forces Vivado to keep
// the full O(N) carry chain intact — the aging-sensitive critical path.
module ripple_adder #(parameter N = 16) (
    input  [N-1:0] a,
    input  [N-1:0] b,
    output [N:0]   sum   // sum[N-1:0] = result, sum[N] = carry-out
);
    wire [N:0] carry;
    assign carry[0] = 1'b0;

    genvar i;
    generate
        for (i = 0; i < N; i = i + 1) begin : FA
            (* DONT_TOUCH = "yes" *)
            lut_full_adder fa (
                .a(a[i]),
                .b(b[i]),
                .cin(carry[i]),
                .sum(sum[i]),
                .cout(carry[i+1])
            );
        end
    endgenerate

    assign sum[N] = carry[N];
endmodule
