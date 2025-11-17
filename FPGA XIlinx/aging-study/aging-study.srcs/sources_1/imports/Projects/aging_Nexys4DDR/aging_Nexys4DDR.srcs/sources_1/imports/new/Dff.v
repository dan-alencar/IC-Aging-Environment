`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 10/28/2024 11:08:56 AM
// Design Name: 
// Module Name: Dff
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


module Dff(
    input[15:0] D,
    input clk,
    output reg[15:0] ffoutput,
    input reset
    );
    reg[26:0] counter;
    
    always@(posedge clk or posedge reset) begin
        if(reset) begin
            ffoutput <= 0;
            counter <= 0;
        end
        else  begin
            counter <= counter + 1;
            if(counter == 27'd50000000) begin
                ffoutput <= D;
                counter <= 0;
            end
        end
    end
    
endmodule
