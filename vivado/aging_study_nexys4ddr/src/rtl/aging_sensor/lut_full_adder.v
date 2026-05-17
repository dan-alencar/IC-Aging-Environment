`timescale 1ns / 1ps

// LUT3-based full adder. Explicit primitives + DONT_TOUCH prevent Vivado
// from mapping carry chains to CARRY4, keeping the path LUT-delay-based
// and aging-sensitive.
module lut_full_adder (
    input  a,
    input  b,
    input  cin,
    output sum,
    output cout
);
    // XOR3: sum = a ^ b ^ cin  →  LUT3 INIT = 8'h96
    (* DONT_TOUCH = "yes" *)
    LUT3_L #(.INIT(8'h96)) SUM_LUT (
        .LO(sum),
        .I0(a), .I1(b), .I2(cin)
    );

    // Majority: cout = (a&b)|(b&cin)|(a&cin)  →  LUT3 INIT = 8'hE8
    (* DONT_TOUCH = "yes" *)
    LUT3_L #(.INIT(8'hE8)) CARRY_LUT (
        .LO(cout),
        .I0(a), .I1(b), .I2(cin)
    );
endmodule
