`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 11/05/2024 01:33:05 PM
// Design Name: 
// Module Name: uart_tx
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


module uart_tx(
    input clk,
    input reset,
    input send,
    input[7:0] data,
    output reg tx,
    output reg tx_busy
    );

    parameter BAUDRATE = 9600, CLK_FREQ = 100000000;
    parameter COUNT = CLK_FREQ/BAUDRATE;

    reg[3:0] index;
    reg[15:0] counter;
    reg[9:0] frame;
    reg sendant;
    wire send_tx;
    
    always@(posedge clk or negedge reset) begin
        if(!reset) begin
            sendant <= 0;
        end
        else begin
            sendant <= send;
        end
    end
    
    assign send_tx = !sendant && send;
    
    always@(posedge clk or negedge reset) begin
        if(!reset) begin
            tx <= 1;
            tx_busy <= 0;
            counter <= 0;
            index <= 0;
            frame <= 0;
        end
        else if(send_tx && !tx_busy) begin
                frame <= {1'b1, data, 1'b0};
                tx_busy <= 1;
                index <= 0;
                tx <= 0;
                counter <= COUNT;
        end
        else if(tx_busy) begin
            if(counter >= COUNT) begin
                if(index < 9) begin
                    index <= index + 1;
                    tx <= frame[index];
                end else if(index == 9) begin
                        tx_busy <= 0;
                        tx <= 1;
                    end
                counter <= 0;
            end
            else counter <= counter + 1;
        end
    end

endmodule