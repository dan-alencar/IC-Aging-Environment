`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Module Name: controller_controller
// Description: Original controller with phase reset capability
//              After measurement, shifts phase back to starting position
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
    output reg psen,
    output wire [2:0] debug_state
    );
    
    reg change_enable;
    reg[2:0] state, next_state;
    reg[15:0] inc_count;
    reg[15:0] reset_count;  // Counter for resetting phase
    reg signal, sig_ant;
    
    // States
    localparam CHECK_ALARM  = 3'b000;  // Check alarm, shift if no alarm
    localparam INIT_SHIFT   = 3'b001;  // Assert psen for measurement
    localparam WAIT_SHIFT   = 3'b010;  // Wait for psdone
    localparam DONE         = 3'b011;  // Measurement complete, start reset
    localparam RESET_PHASE  = 3'b100;  // Shift phase back (increment)
    localparam WAIT_RESET   = 3'b101;  // Wait for reset shift to complete
    localparam IDLE         = 3'b110;  // Waiting for next trigger
    
    assign debug_state = state;
    
    initial begin 
        change = 0; 
        signal = 0; 
        state = CHECK_ALARM;
        next_state = CHECK_ALARM;
        change_enable = 0;
        psen = 0;
        psincdec = 0;
        inc_count = 0;
        reset_count = 0;
        display_value = 0;
        sig_ant = 0;
    end
    
    // Toggle generator for critical path
    always @(posedge clk) begin
        if(change_enable)
            change <= ~change;
    end
    
    // State register
    always @(posedge clk or negedge reset) begin
        if(!reset)
            state <= CHECK_ALARM;
        else 
            state <= next_state;
    end
    
    // Next state and output logic (combinational)
    always @(*) begin
        // Defaults
        change_enable = 0;
        signal = 0;
        psen = 0;
        psincdec = 0;
        
        case(state)
            CHECK_ALARM: begin  // Check alarm, shift if no alarm
                change_enable = 1;
                psincdec = 0;  // Decrement direction (shift left)
                if(alarm) 
                    next_state = DONE;
                else 
                    next_state = INIT_SHIFT;
            end
            
            INIT_SHIFT: begin  // Assert psen for measurement shift
                change_enable = 1;
                psen = 1;
                psincdec = 0;  // Decrement
                next_state = WAIT_SHIFT;
            end
            
            WAIT_SHIFT: begin  // Wait for psdone
                change_enable = 1;
                psincdec = 0;
                if(psdone) 
                    next_state = CHECK_ALARM;
                else 
                    next_state = WAIT_SHIFT;
            end
            
            DONE: begin  // Measurement complete
                display_value = inc_count;
                signal = 1;
                change_enable = 0;
                next_state = RESET_PHASE;  // Start resetting phase
            end
            
            RESET_PHASE: begin  // Shift phase back (increment direction)
                change_enable = 0;
                psincdec = 1;  // INCREMENT direction (opposite of measurement)
                if(reset_count >= inc_count) begin
                    next_state = IDLE;  // Done resetting
                end else begin
                    psen = 1;
                    next_state = WAIT_RESET;
                end
            end
            
            WAIT_RESET: begin  // Wait for reset shift to complete
                change_enable = 0;
                psincdec = 1;  // Keep increment direction
                if(psdone)
                    next_state = RESET_PHASE;  // Do next reset shift
                else
                    next_state = WAIT_RESET;
            end
            
            IDLE: begin  // Waiting - phase is reset, ready for next measurement
                change_enable = 0;
                next_state = IDLE;  // Stay here until reset
            end
            
            default: next_state = CHECK_ALARM;
        endcase
    end
    
    // Phase shift counter - counts on psdone rising edge during measurement
    always @(posedge psdone or negedge reset) begin
        if(!reset) begin
            inc_count <= 16'd0;
            reset_count <= 16'd0;
        end else begin
            // Count based on direction
            if(psincdec == 0)  // Decrementing (measuring)
                inc_count <= inc_count + 1;
            else  // Incrementing (resetting)
                reset_count <= reset_count + 1;
        end
    end
    
    // Send pulse generation
    always @(posedge clk or negedge reset) begin
        if(!reset) 
            sig_ant <= 0;
        else
            sig_ant <= signal;
    end
    
    assign send = ~sig_ant && signal;
    
endmodule