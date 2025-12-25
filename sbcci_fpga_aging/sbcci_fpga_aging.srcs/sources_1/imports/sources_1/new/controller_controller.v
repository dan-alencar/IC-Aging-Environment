`timescale 1ns / 1ps

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
    reg[15:0] inc_count;
    reg signal, sig_ant;
    
    // States
    localparam S_INIT = 2'b00, S_SHIFT = 2'b01, S_WAIT = 2'b10, S_LOCKED = 2'b11;

    initial begin change = 0; signal = 0; end
    
    always @(posedge clk) begin
        if(change_enable) change <= ~change;
    end
    
    always @(posedge clk or negedge reset) begin
        if(!reset) state <= S_INIT;
        else state <= next_state;
    end
    
    always @(*) begin
        case(state)
            S_INIT: begin 
                change_enable <= 1; 
                signal <= 0; psen <= 0; 
                psincdec <= 1; // <--- INCREMENT to find failure edge
                if(alarm) next_state <= S_LOCKED; 
                else next_state <= S_SHIFT;
            end
            S_SHIFT: begin 
                psen <= 1; 
                next_state <= S_WAIT; 
            end
            S_WAIT: begin 
                psen <= 0;
                if(psdone) next_state <= S_INIT;
                else next_state <= S_WAIT; 
            end
            S_LOCKED: begin 
                display_value <= inc_count; // Freeze Slack Value
                signal <= 1;                // Send UART Packet
                change_enable <= 0; 
                next_state <= S_LOCKED;     // WAIT FOR 0x0F RESET
            end
        endcase
    end
    
    always @(posedge psdone or negedge reset) begin
        if(!reset) inc_count <= 0;
        else inc_count <= inc_count + 1;
    end
    
    always @(posedge clk or negedge reset) begin
        if(!reset) sig_ant <= 0;
        else sig_ant <= signal;
    end
    
    assign send = (signal && !sig_ant);
    
endmodule