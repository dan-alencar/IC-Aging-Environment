`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Module Name: modern_sensible
// Description: Aging sensor with debug outputs and glitch filtering
//////////////////////////////////////////////////////////////////////////////////

module modern_sensible(
    input sclk,         // System clock (FF2)
    input psclk,        // Phase-shifted clock (FF1)
    input in_sensor,    // Critical path output
    input reset,        // Active-high reset (unused, kept for compatibility)
    input clk_en,       // Catcher clock (FF3)
    output alarm,       // Filtered alarm output
    output ff1_out,     // Debug: FF1 output
    output ff2_out,     // Debug: FF2 output  
    output raw_alarm    // Debug: Unfiltered XOR result
);
     
    wire xor_out;
    wire ff1;
    wire ff2;
    wire ff3_out;

    assign ff1_out = ff1;
    assign ff2_out = ff2;
    assign raw_alarm = xor_out;
    
    // XOR gate detects difference between FF1 and FF2
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
        .CLR(1'b0),     // Never clear - let it run freely
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
        .CLR(1'b0),     // Never clear
        .D(in_sensor)
    );
    
    // FF3: Latches XOR result on catcher clock
    (* AREA_GROUP = "sensor" *)
    (* U_SET = "sensor" *)
    (* dont_touch = "true" *)
    FDCE #(
        .INIT(1'b0)
    ) FF3 (
        .Q(alarm),
        .C(clk_en),
        .CE(1'b1),
        .CLR(1'b0),     // Never clear
        .D(xor_out)
    );

endmodule