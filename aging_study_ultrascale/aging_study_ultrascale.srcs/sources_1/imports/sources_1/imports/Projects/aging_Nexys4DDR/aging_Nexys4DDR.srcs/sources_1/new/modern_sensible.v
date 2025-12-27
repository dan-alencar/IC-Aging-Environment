`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 12/13/2024 01:29:51 PM
// Design Name: 
// Module Name: modern_sensible
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////


module modern_sensible(
    input sclk,
    input  psclk, 
    input  in_sensor,
    input reset,
    input clk_en,
    output  alarm,
    output ff1_out
    //output wire ff1_out
    );
	 
	 wire xor_out;
	 wire ff1;
	 wire ff2;
	 wire and_out;
	 wire buff_out;
	
	assign ff1_out = ff2;
	
	/*(* AREA_GROUP = "sensor" *)
	(* U_SET= "sensor" *)
	(* dont_touch = "true" *)
	 LUT1_L #(.INIT(2'b10) // Specify LUT Contents
	)BUF1 (
	.LO(buff_out), // Connect to the output of a LUT
	.I0(and_out) // Connect to the input of a LUT
	);*/
	
	(* AREA_GROUP = "sensor" *)
	(* U_SET= "sensor" *)
	(* dont_touch = "true" *)
	LUT2_L #(
	.INIT(4'b0110) // Specify LUT Contents
	) XOR1 (
	.LO(xor_out), // LUT local output
	.I0(ff1), // LUT input
	.I1(ff2) // LUT input
	);
	
	/*(* AREA_GROUP = "sensor" *)
	(* U_SET= "sensor" *)
	(* dont_touch = "true" *)
	LUT2_L #(
	.INIT(4'b1000) // Specify LUT Contents
	) AND1 (
	.LO(and_out), // LUT local output
	.I0(clk_en), // LUT input
	.I1(xor_out) // LUT input
	);*/
	
	
	(* AREA_GROUP = "sensor" *)
	(* U_SET= "sensor" *)
	(* dont_touch = "true" *)
	FDCE #(
	.INIT(1'b0) // Initial value of register (1'b0 or 1'b1)
	) FF1 (
	.Q(ff1), // Data output
	.C(psclk), // Clock input
	.CE(1'b1), // Clock enable input
	.CLR(reset), // Asynchronous clear input
	.D(in_sensor) // Data input
	);
	
	(* AREA_GROUP = "sensor" *)
	(* U_SET= "sensor" *)
	(* dont_touch = "true" *)
	FDCE #(
	.INIT(1'b0) // Initial value of register (1'b0 or 1'b1)
	) FF2 (
	.Q(ff2), // Data output
	.C(sclk), // Clock input
	.CE(1'b1), // Clock enable input
	.CLR(reset), // Asynchronous clear input
	.D(in_sensor) // Data input
	);
	
	(* AREA_GROUP = "sensor" *)
	(* U_SET= "sensor" *)
	(* dont_touch = "true" *)
	FDCE #(
	.INIT(1'b0) // Initial value of register (1'b0 or 1'b1)
	) FF3 (
	.Q(alarm), // Data output
	.C(clk_en), // Clock input
	.CE(1'b1), // Clock enable input
	.CLR(reset), // Asynchronous clear input
	.D(xor_out) // Data input
	);

    //assign ff1_out = ff1;

endmodule