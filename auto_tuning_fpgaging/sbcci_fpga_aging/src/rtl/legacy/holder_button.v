`timescale 1ns / 1ps

module holder_button(
    input clk,
    input reset,
    input button,
    input alarm,
    output reg held
);
    
    reg buttonant;
    wire button_pulse;
    
    // Button edge detection
    always @(posedge clk) begin
        buttonant <= button;
    end
    assign button_pulse = button && !buttonant;
    
    // Simplified latch: no edge detection on alarm
    // Just latch whenever alarm is HIGH
    always @(posedge clk or posedge reset) begin
        if (reset) begin
            held <= 0;
        end
        else if (button_pulse) begin
            held <= 0;
        end
        else if (alarm) begin
            held <= 1;  // Latch on alarm HIGH (not edge)
        end
    end
    
endmodule