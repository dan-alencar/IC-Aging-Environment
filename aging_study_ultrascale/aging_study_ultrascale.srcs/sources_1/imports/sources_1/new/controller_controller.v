`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Module Name: controller_controller
// Description: Controller with VIO trigger for measurements
//              - Accepts external trigger to start new slack measurement
//              - Automatically sends UART packet when measurement completes
//              - Can operate in continuous or triggered mode
//////////////////////////////////////////////////////////////////////////////////

module controller_controller(
    input clk,
    input reset,
    input alarm,              // From aging sensor
    input psdone,             // Phase shift complete
    input trigger_meas,       // External trigger to start new measurement (from VIO)
    input continuous_mode,    // 1=continuous sweeping, 0=wait for trigger
    output reg[15:0] display_value,
    output reg change,
    output reg psincdec,
    output wire send,          // UART send trigger
    output reg psen,
    output reg measuring,     // Status: 1=currently measuring, 0=idle
    output reg meas_complete  // Pulse when measurement completes
);
    
    reg change_enable;
    reg[1:0] state, next_state;
    reg[15:0] inc_count;
    reg signal, sig_ant;
    reg trigger_sync1, trigger_sync2, trigger_prev;
    wire trigger_edge;
    
    // States
    localparam IDLE         = 2'b00;  // Waiting for trigger
    localparam SWEEPING     = 2'b01;  // Actively sweeping phase
    localparam PHASE_SHIFT  = 2'b10;  // Waiting for phase shift to complete
    localparam DONE         = 2'b11;  // Measurement complete, send UART
    
    initial begin 
        change = 0; 
        signal = 0; 
        measuring = 0;
        meas_complete = 0;
    end
    
    // Synchronize trigger input to avoid metastability
    always @(posedge clk or negedge reset) begin
        if (!reset) begin
            trigger_sync1 <= 0;
            trigger_sync2 <= 0;
            trigger_prev <= 0;
        end else begin
            trigger_sync1 <= trigger_meas;
            trigger_sync2 <= trigger_sync1;
            trigger_prev <= trigger_sync2;
        end
    end
    
    // Detect rising edge of trigger
    assign trigger_edge = trigger_sync2 && !trigger_prev;
    
    // Toggle change signal when enabled
    always @(posedge clk) begin
        if (change_enable)
            change <= ~change;
    end
    
    // State register
    always @(posedge clk or negedge reset) begin
        if (!reset) begin
            state <= IDLE;
        end else begin
            state <= next_state;
        end
    end
    
    // State machine
    always @(*) begin
        // Default outputs
        change_enable = 0;
        signal = 0;
        psen = 0;
        psincdec = 0;
        measuring = 0;
        meas_complete = 0;
        next_state = state;
        
        case (state)
            IDLE: begin
                // Wait for trigger or stay in continuous mode
                if (trigger_edge || continuous_mode) begin
                    next_state = SWEEPING;
                end else begin
                    next_state = IDLE;
                end
            end
            
            SWEEPING: begin
                change_enable = 1;
                measuring = 1;
                
                if (alarm) begin
                    // Measurement complete - alarm detected
                    next_state = DONE;
                end else begin
                    // Continue phase shifting
                    next_state = PHASE_SHIFT;
                end
            end
            
            PHASE_SHIFT: begin
                psen = 1;
                measuring = 1;
                next_state = PHASE_SHIFT;
                
                if (psdone) begin
                    // Phase shift complete, go back to sweeping
                    next_state = SWEEPING;
                end
            end
            
            DONE: begin
                display_value = inc_count;
                signal = 1;
                meas_complete = 1;
                
                // In continuous mode, immediately start new measurement
                // In triggered mode, wait for next trigger
                if (continuous_mode) begin
                    next_state = IDLE;  // Will immediately restart due to continuous_mode
                end else begin
                    next_state = IDLE;  // Wait for next trigger
                end
            end
            
            default: next_state = IDLE;
        endcase
    end
    
    // Count phase shifts (slack measurement)
    always @(posedge psdone or negedge reset) begin
        if (!reset) begin
            inc_count <= 0;
        end else begin
            if (state == DONE) begin
                // Reset counter when starting new measurement
                inc_count <= 0;
            end else begin
                inc_count <= inc_count + 1;
            end
        end
    end
    
    // Generate UART send pulse
    always @(posedge clk or negedge reset) begin
        if (!reset) begin
            sig_ant <= 0;
        end else begin
            sig_ant <= signal;
        end
    end
    
    assign send = ~sig_ant && signal;
    
endmodule