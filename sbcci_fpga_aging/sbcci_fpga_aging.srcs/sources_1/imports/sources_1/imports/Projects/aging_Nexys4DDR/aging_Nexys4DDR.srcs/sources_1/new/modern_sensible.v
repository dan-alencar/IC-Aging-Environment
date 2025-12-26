`timescale 1ns / 1ps

module modern_sensible(
    input sclk,
    input psclk, 
    input in_sensor,
    input reset,
    input clk_en,
    output alarm,
    output ff1_out
);
     
    wire xor_out;
    wire ff1;
    wire ff2;

    assign ff1_out = ff2;
    
    // XOR using LUT2_L primitive
    (* AREA_GROUP = "sensor" *)
    (* U_SET = "sensor" *)
    (* dont_touch = "true" *)
    LUT2_L #(
        .INIT(4'b0110)  // XOR: output = I0 ^ I1
    ) XOR1 (
        .LO(xor_out),
        .I0(ff1),
        .I1(ff2)
    );
    
    // FF1: Samples with phase-shifted clock
    (* AREA_GROUP = "sensor" *)
    (* U_SET = "sensor" *)
    (* dont_touch = "true" *)
    FDCE #(
        .INIT(1'b0)
    ) FF1 (
        .Q(ff1),
        .C(psclk),
        .CE(1'b1),
        .CLR(reset),
        .D(in_sensor)
    );
    
    // FF2: Samples with system clock
    (* AREA_GROUP = "sensor" *)
    (* U_SET = "sensor" *)
    (* dont_touch = "true" *)
    FDCE #(
        .INIT(1'b0)
    ) FF2 (
        .Q(ff2),
        .C(sclk),
        .CE(1'b1),
        .CLR(reset),
        .D(in_sensor)
    );
    
    // FF3: Latches XOR result
    (* AREA_GROUP = "sensor" *)
    (* U_SET = "sensor" *)
    (* dont_touch = "true" *)
    FDCE #(
        .INIT(1'b0)
    ) FF3 (
        .Q(alarm),
        .C(clk_en),
        .CE(1'b1),
        .CLR(reset),
        .D(xor_out)
    );

endmodule