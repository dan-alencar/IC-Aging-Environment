`timescale 1ns / 1ps

// Three-FF metastability sensor with XOR comparator across phase-shifted domains.
//
//   FF1 (psclk domain) : samples in_sensor on the phase-shifted clock.
//   FF2 (sclk domain)  : samples in_sensor on the reference system clock.
//   XOR1               : combinational XOR of FF1 and FF2 outputs.
//   FF3 (clk_en domain): latches XOR result on the 100°-offset clock → alarm.
//
// ff1_out exports FF2's Q (sclk domain) so that failure_holder can compare it
// against the reference adder output on the same clock domain.
// Note: the port name reflects its role in the original design convention.
//
// AND1 and BUF1 are commented out — do NOT add LOC/BEL constraints for them.
module modern_sensible (
    input  logic sclk,
    input  logic psclk,
    input  logic in_sensor,
    input  logic reset,    // active-high (FDCE CLR)
    input  logic clk_en,
    output logic alarm,
    output logic ff1_out
);
    logic xor_out;
    logic ff1, ff2;

    assign ff1_out = ff2;  // exports the sclk-domain capture (FF2)

    (* AREA_GROUP = "sensor" *)
    (* U_SET = "sensor" *)
    (* dont_touch = "true" *)
    LUT2_L #(.INIT(4'b0110)) XOR1 (  // XOR: a^b
        .LO(xor_out),
        .I0(ff1),
        .I1(ff2)
    );

    (* AREA_GROUP = "sensor" *)
    (* U_SET = "sensor" *)
    (* dont_touch = "true" *)
    FDCE #(.INIT(1'b0)) FF1 (
        .Q  (ff1),
        .C  (psclk),
        .CE (1'b1),
        .CLR(reset),
        .D  (in_sensor)
    );

    (* AREA_GROUP = "sensor" *)
    (* U_SET = "sensor" *)
    (* dont_touch = "true" *)
    FDCE #(.INIT(1'b0)) FF2 (
        .Q  (ff2),
        .C  (sclk),
        .CE (1'b1),
        .CLR(reset),
        .D  (in_sensor)
    );

    (* AREA_GROUP = "sensor" *)
    (* U_SET = "sensor" *)
    (* dont_touch = "true" *)
    FDCE #(.INIT(1'b0)) FF3 (
        .Q  (alarm),
        .C  (clk_en),
        .CE (1'b1),
        .CLR(reset),
        .D  (xor_out)
    );

endmodule
