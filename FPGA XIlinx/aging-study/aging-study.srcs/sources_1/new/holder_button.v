`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 02/11/2025 07:08:35 PM
// Design Name: 
// Module Name: holder_button
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


module holder_button(
    input clk,
    input button,
    input alarm,
    output reg held
    );
    reg buttonant;
    wire pulse;
    
    always@(posedge clk) begin
        buttonant <= button;
    end
    
    assign pulse = button && !buttonant;
    
    always@(posedge clk or posedge pulse) begin
        if(pulse) held <= 0;
        else if (alarm) held <= 1;
    end
endmodule
