`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 01/20/2025 02:03:02 PM
// Design Name: 
// Module Name: temp_catcher
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


module temp_catcher(
    input clk,
    input reset,
    input wire drdy,
    input wire[15:0] do_data,
    output reg[6:0] daddr,
    output reg den,
    output wire[20:0] temp,
    output wire[20:0] vccint
    );
    
    reg[1:0] state;
    reg[31:0] placeholder[1:0];
    reg[7:0] timeout;
    
    parameter ASK_TEMP = 2'b00, GET_TEMP = 2'b01, ASK_VCC = 2'b10, GET_VCC = 2'b11;
    
    always@(posedge clk or negedge reset) begin
        if(!reset) begin
            state <= ASK_TEMP;
            daddr <= 7'h0;
            den <= 1'b1;
            placeholder[0] <= 32'b0;
            placeholder[1] <= 32'b0;
            timeout <= 7'b0;
        end
        else begin
            case(state)
            ASK_TEMP: begin
                den <= 1'b1;
                daddr <= 7'h0;
                timeout <= 0;
                state <= GET_TEMP;
                end
            GET_TEMP: begin
                den <= 1'b0;
                if(timeout == 7'b1111111) state <= ASK_TEMP;
                else timeout <= timeout + 1;
                    if (drdy) begin
                    state <= ASK_VCC;
                    placeholder[0] <= (do_data[15:4] * 503975) >> 12;
                    end
                end
            ASK_VCC: begin
                den <= 1'b1;
                timeout <= 0;
                daddr <= 7'h01;
                state <= GET_VCC;
            end
            GET_VCC: begin
                den <= 1'b0;
                if(timeout == 7'b1111111) state <= ASK_VCC;
                else timeout <= timeout + 1;
                if(drdy) begin
                    state <= ASK_TEMP;
                    placeholder[1] <= {do_data[15:4] * 3000} >> 12;
                end
            end
            endcase
        end
    end
    
    assign temp = placeholder[0] - 273150; 
    assign vccint = placeholder[1];
    
endmodule
