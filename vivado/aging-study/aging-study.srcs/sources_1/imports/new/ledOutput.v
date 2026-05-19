`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 08/01/2024 06:27:22 PM
// Design Name: 
// Module Name: ledOutput
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


module ledOutput(
    input alarm,
    output ledOut
    );
    reg holder = 1;
    assign ledOut = holder;
    
    always@(posedge alarm) holder = 0;
    
endmodule
