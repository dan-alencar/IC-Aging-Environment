`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 04/25/2025 01:44:02 PM
// Design Name: 
// Module Name: failure_holder
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


module failure_holder(
        input ff1,
        input ff2,
        input reset,
        output reg held
    );
    
    always@(posedge ff2 or negedge reset) begin
        if(!reset) held <= 0;
        else if(ff1 != ff2) held <= 1;
    end
    
endmodule
