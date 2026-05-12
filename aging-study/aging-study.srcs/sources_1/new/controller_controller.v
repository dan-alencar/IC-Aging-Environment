`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 03/07/2025 04:41:54 PM
// Design Name: 
// Module Name: controller_controller
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


module controller_controller(
    input clk,
    input reset,
    input alarm,
    input psdone,
    output reg[15:0] display_value,
    output reg change,
    output reg psincdec,
    output send,
    output reg psen
    );
    
    reg change_enable;
    reg[1:0] state, next_state;
    reg[63:0] timeout;
    reg[15:0] inc_count;
    reg signal, sig_ant;
    
    initial begin change = 0; signal <= 0; end
    
    always@(posedge clk) begin
        if(change_enable)
        change <= ~change;
    end
    
    always@(posedge clk or negedge reset) begin
        if(!reset) begin
            state <= 2'b00;
        end
        else state <= next_state;
    end
    
    always@(state or psdone) begin
        case(state)
            2'b00: begin change_enable <= 1; signal <= 0; psen <= 0; psincdec <= 0; if(alarm) next_state <= 2'b11; else begin next_state <= 2'b01; end end
            2'b01: begin psen <= 1; next_state <= 2'b10; end
            2'b10: begin psen <= 0;
                        if(psdone) next_state <= 2'b00;
                        else begin next_state <= 2'b10; end
            end
            2'b11: begin display_value <= inc_count; signal <= 1; change_enable <= 0; end
        endcase
    end
    
    always@(posedge psdone or negedge reset) begin
        if(!reset) inc_count <= 0;
        else begin
            inc_count <= inc_count + 1;
        end
    end
    
    always@(posedge clk or negedge reset) begin
        if(!reset) sig_ant <= 0;
        sig_ant <= signal;
    end
    
    assign send = ~sig_ant && signal;
    
endmodule
