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
    reg[2:0] state;
    reg[15:0] inc_count;
    reg signal, sig_ant;
    reg alarm_prev;
    wire alarm_edge;
    
    // Detect rising edge of alarm (not just level)
    assign alarm_edge = alarm && !alarm_prev;
    
    // States
    localparam IDLE        = 3'b000;
    localparam STABILIZE   = 3'b001;  // New: wait after reset
    localparam CHECK_ALARM = 3'b010;
    localparam INIT_SHIFT  = 3'b011;
    localparam WAIT_SHIFT  = 3'b100;
    localparam LOCKED      = 3'b101;
    localparam SEND_DATA   = 3'b110;

    reg[7:0] stab_count;  // Stabilization counter
    
    initial begin 
        change = 0; 
        signal = 0;
        state = IDLE;
        change_enable = 0;
        psen = 0;
        psincdec = 1;
        inc_count = 0;
        display_value = 0;
        alarm_prev = 0;
        stab_count = 0;
    end
    
    // Change signal generator for delay chain stimulus
    always @(posedge clk) begin
        if(change_enable) 
            change <= ~change;
    end
    
    // Track alarm transitions
    always @(posedge clk) begin
        alarm_prev <= alarm;
    end
    
    // Main FSM
    always @(posedge clk or negedge reset) begin
        if(!reset) begin
            state <= IDLE;
            change_enable <= 0;
            psen <= 0;
            psincdec <= 1;
            signal <= 0;
            inc_count <= 0;
            display_value <= 0;
            stab_count <= 0;
        end else begin
            case(state)
                IDLE: begin
                    change_enable <= 0;
                    signal <= 0;
                    psen <= 0;
                    psincdec <= 1;  // Increment direction
                    stab_count <= 0;
                    state <= STABILIZE;
                end
                
                STABILIZE: begin
                    // Wait a few clocks after reset for sensor to stabilize
                    // This prevents false alarms at startup
                    if(stab_count >= 8'd50) begin
                        change_enable <= 1;  // Start toggling
                        state <= CHECK_ALARM;
                    end else begin
                        stab_count <= stab_count + 1;
                    end
                end
                
                CHECK_ALARM: begin
                    // Only react to NEW alarm (rising edge)
                    // Ignore if alarm was already high
                    if(alarm_edge) begin
                        // Found timing violation!
                        state <= LOCKED;
                    end else begin
                        // No new violation, shift phase
                        state <= INIT_SHIFT;
                    end
                end
                
                INIT_SHIFT: begin
                    // Start phase shift
                    psen <= 1;
                    state <= WAIT_SHIFT;
                end
                
                WAIT_SHIFT: begin
                    // Wait for phase shift to complete
                    psen <= 0;
                    if(psdone) begin
                        inc_count <= inc_count + 1;
                        state <= CHECK_ALARM;
                    end
                end
                
                LOCKED: begin
                    // Found the failure point
                    display_value <= inc_count;
                    change_enable <= 0;
                    state <= SEND_DATA;
                end
                
                SEND_DATA: begin
                    // Trigger SysMon to send data
                    signal <= 1;
                    // Stay here until reset by sweep timer
                    state <= SEND_DATA;
                end
                
                default: state <= IDLE;
            endcase
        end
    end
    
    // Generate edge detector for send signal
    always @(posedge clk or negedge reset) begin
        if(!reset) 
            sig_ant <= 0;
        else 
            sig_ant <= signal;
    end
    
    // Send pulse: rising edge of signal
    assign send = (signal && !sig_ant);
    
endmodule