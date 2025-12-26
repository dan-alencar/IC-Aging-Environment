`timescale 1ns / 1ps

module holder_button(
    input clk,
    input reset,
    input button,
    input alarm,
    output reg held
    );
    
    reg buttonant;
    reg alarm_prev;
    wire button_pulse;
    wire alarm_edge;
    
    // Detect button press (rising edge)
    always@(posedge clk) begin
        buttonant <= button;
    end
    assign button_pulse = button && !buttonant;
    
    // Detect alarm rising edge (not just level)
    always@(posedge clk) begin
        alarm_prev <= alarm;
    end
    assign alarm_edge = alarm && !alarm_prev;
    
    // Latch logic
    always@(posedge clk or posedge reset) begin
        if (reset) begin
            held <= 0;  // Clear on reset
        end
        else if(button_pulse) begin
            held <= 0;  // Clear on button press
        end
        else if (alarm_edge) begin
            held <= 1;  // Latch on alarm rising edge
        end
        // Otherwise hold current value
    end
    
endmodule