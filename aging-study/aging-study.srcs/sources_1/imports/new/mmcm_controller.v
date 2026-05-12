`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 02/10/2025 04:39:00 PM
// Design Name: 
// Module Name: mmcm_controller
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


module mmcm_controller( 
    input clk,
    input psdone,
    input reset,
    input change,
    input direction,
    output reg psen,
    output psincdec,
    output reg[9:0] inc_count    
    );
    
    reg state;
    reg changeant;
    wire pulse;
    
    assign psincdec = !direction;
    
    
    
    always@(posedge clk or posedge reset) begin
        if(reset) changeant <= 0;
        else begin
            changeant <= change;
        end
    end
    
    assign pulse = change && !changeant;
    
    always@(posedge clk or posedge reset) begin
        if(reset) begin
            psen <= 0;
            state <= 0;
        end
        else begin
            if(!state) begin
                psen <= 0;
                if(pulse) state <= 1;
            end
            else begin
                psen <= 1;
                state <= 0;
            end
        end
    end
    
    always@(posedge psdone or posedge reset) begin
        if(reset) inc_count <= 0;
        else if(!psincdec)inc_count <= inc_count + 1;
        else inc_count <= inc_count - 1;
    end
    
endmodule
