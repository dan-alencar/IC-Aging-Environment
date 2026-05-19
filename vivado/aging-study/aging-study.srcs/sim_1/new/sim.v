`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 01/20/2025 03:44:05 PM
// Design Name: 
// Module Name: sim
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


module sim(
    );
    
    reg clk, reset, drdy;
    reg[15:0] do_data;
    wire[6:0] daddr;
    wire[15:0] temp;
    wire den;
    
    temp_catcher catch(
        .clk(clk),
        .reset(reset),
        .drdy(drdy),
        .den(den),
        .do_data(do_data),
        .daddr(daddr),
        .temp(temp)
    );
    
    always #5 clk = ~clk;
    
    initial begin
        clk = 0;
        reset = 0;
        do_data = 0;
        drdy = 0;
        #2 reset = 1;
        
        #103 drdy = 1; do_data = 7;
        #10 drdy = 0;
        #100 drdy = 1; do_data = 9;
    end
    
endmodule
