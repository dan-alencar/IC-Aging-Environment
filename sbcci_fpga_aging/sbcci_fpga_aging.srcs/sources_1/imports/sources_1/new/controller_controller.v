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
    reg signal;
    
    localparam IDLE        = 3'b000;
    localparam STABILIZE   = 3'b001;
    localparam CHECK_ALARM = 3'b010;
    localparam INIT_SHIFT  = 3'b011;
    localparam WAIT_SHIFT  = 3'b100;
    localparam LOCKED      = 3'b101;
    localparam SEND_DATA   = 3'b110;

    reg[7:0] stab_count;
    reg[15:0] send_pulse_cnt;
    reg[15:0] phase_limit_cnt;  // NEW: Count phase shifts
    localparam SEND_PULSE_WIDTH = 16'd1000;
    localparam MAX_PHASE_SHIFTS = 16'd500;  // Give up after 500 shifts

    // Add keep attribute to prevent optimization
    (* keep = "true" *)
    reg[15:0] inc_count_safe;

    initial begin 
        change = 0;
        signal = 0;
        state = IDLE;
        change_enable = 0;
        psen = 0;
        psincdec = 1;
        inc_count = 0;
        inc_count_safe = 0;
        display_value = 0;
        stab_count = 0;
        send_pulse_cnt = 0;
        phase_limit_cnt = 0;
    end
    
    // Toggle generator
    always @(posedge clk) begin
        if(change_enable) 
            change <= ~change;
    end
    
    // Counter on psdone edge
    always @(posedge psdone or negedge reset) begin
        if(!reset) begin
            inc_count <= 0;
            inc_count_safe <= 0;
        end else begin
            inc_count <= inc_count + 1;
            inc_count_safe <= inc_count_safe + 1;
        end
    end
    
    // Main FSM
    always @(posedge clk or negedge reset) begin
        if(!reset) begin
            state <= IDLE;
            change_enable <= 0;
            psen <= 0;
            psincdec <= 1;
            signal <= 0;
            display_value <= 0;
            stab_count <= 0;
            send_pulse_cnt <= 0;
            phase_limit_cnt <= 0;
        end else begin
            case(state)
                IDLE: begin
                    change_enable <= 0;
                    signal <= 0;
                    psen <= 0;
                    psincdec <= 1;
                    stab_count <= 0;
                    send_pulse_cnt <= 0;
                    phase_limit_cnt <= 0;
                    state <= STABILIZE;
                end
                
                STABILIZE: begin
                    if(stab_count >= 8'd100) begin
                        change_enable <= 1;
                        state <= CHECK_ALARM;
                    end else begin
                        stab_count <= stab_count + 1;
                    end
                end
                
                CHECK_ALARM: begin
                    // Check alarm OR if we've done too many shifts
                    if(alarm || phase_limit_cnt >= MAX_PHASE_SHIFTS) begin
                        state <= LOCKED;
                    end else begin
                        state <= INIT_SHIFT;
                        phase_limit_cnt <= phase_limit_cnt + 1;
                    end
                end
                
                INIT_SHIFT: begin
                    psen <= 1;
                    state <= WAIT_SHIFT;
                end
                
                WAIT_SHIFT: begin
                    psen <= 0;
                    if(psdone) begin
                        state <= CHECK_ALARM;
                    end
                end
                
                LOCKED: begin
                    // Use the safe counter that has keep attribute
                    display_value <= inc_count_safe;
                    change_enable <= 0;
                    state <= SEND_DATA;
                    send_pulse_cnt <= 0;
                end
                
                SEND_DATA: begin
                    if(send_pulse_cnt < SEND_PULSE_WIDTH) begin
                        signal <= 1;
                        send_pulse_cnt <= send_pulse_cnt + 1;
                    end else begin
                        signal <= 0;
                    end
                end
                
                default: state <= IDLE;
            endcase
        end
    end
    
    assign send = signal;

endmodule