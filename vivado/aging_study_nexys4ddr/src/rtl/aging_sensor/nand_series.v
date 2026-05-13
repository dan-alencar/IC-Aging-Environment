`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 11/07/2024 04:49:58 PM
// Design Name: 
// Module Name: not_series
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


module not_series(
    input clk,
    input test_bit,
    output reg start,
    output critpath
    );
    reg inverted_bit;
    parameter size = 19;
    wire[(size):0] connection;
    assign connection[0] = start;
    
    generate genvar i;
    for(i = 0; i < (size); i = i+1) begin
        (* DONT_TOUCH = "yes" *)
		 LUT1_L #(.INIT(2'b01) // Specify LUT Contents
         )INV (
         .LO(connection[i + 1]), // Connect to the output of a LUT
         .I0(connection[i]) // Connect to the input of a LUT
         );
    end
    endgenerate
    
    always@(posedge clk) begin
        start <= test_bit;
        inverted_bit <= connection[(size)];
    end
    
    assign critpath = connection[(size)];
    
endmodule
