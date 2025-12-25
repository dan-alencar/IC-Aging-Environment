`timescale 1ns / 1ps

module holder_button(
    input clk,
    input reset,  // <--- ADDED THIS PORT
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
    
    always@(posedge clk or posedge reset) begin // Added reset to sensitivity list
        if (reset) held <= 0;           // Handle UART Reset (0x0F)
        else if(pulse) held <= 0;       // Handle Physical Button
        else if (alarm) held <= 1;
    end
endmodule