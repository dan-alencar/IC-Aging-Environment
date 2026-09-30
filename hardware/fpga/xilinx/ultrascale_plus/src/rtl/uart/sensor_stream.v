`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 01/17/2025 06:50:07 PM
// Design Name: 
// Module Name: sensor_stream
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


module sensor_stream(
    input wire[23:0] temp,
    input wire[23:0] vccint,
    input wire[15:0] sensor,
    input wire failure,
    input wire reset,
    input wire clk,
    input wire sendin,
    output reg send,
    output reg[7:0] data
    );
    
    parameter BAUDRATE = 9600, CLK_FREQ = 100000000;
    parameter COUNT = (CLK_FREQ/BAUDRATE)*10;
    reg[16:0] counter;
    reg[3:0] sel;
    
    reg sendant;
    wire send_tx;
    
    always@(posedge clk or negedge reset) begin
        if(!reset) begin
            sendant <= 0;
        end
        else begin
            sendant <= sendin;
        end
    end
    
    assign send_tx = !sendant && sendin;
    
    reg enable;
    
    always@(posedge clk or negedge reset) begin
        if(!reset) begin
            counter <= 0;
            sel <= 0;
            send <= 0;
            data <= 0;
            enable <= 0;
        end
        else if(send_tx) enable <= 1;
        else if(enable) begin
            if(counter >= COUNT) begin
                if(sel > 8) sel <= 0;
                else sel <= sel + 1;
                counter <= 0;
                case(sel)
                    4'b0000: begin data <= temp[7:0]; send <= 1; end
                    4'b0001: begin data <= temp[15:8]; send <= 1; end
                    4'b0010: begin data <= temp[23:16]; send <= 1; end
                    4'b0011: begin data <= sensor[7:0]; send <= 1; end
                    4'b0100: begin data <= sensor[15:8]; send <= 1; end
                    4'b0101: begin data <= vccint[7:0]; send <= 1; end
                    4'b0110: begin data <= vccint[15:8]; send <= 1; end
                    4'b0111: begin data <= vccint[23:16]; send <= 1; end
                    4'b1000: begin data <= { 7'b0000000, failure }; send = 1; end
                    default: begin data <= 0; enable <= 0; end
                endcase
            end
            else begin counter <= counter + 1; send <= 0; end
        end
    end
    
endmodule