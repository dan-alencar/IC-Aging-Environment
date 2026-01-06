`timescale 1ns / 1ps

module uart_arbiter (
    input  logic clk,
    input  logic rst_n,
    
    input  logic tx_croc,
    input  logic tx_monitor,
    input  logic monitor_active,
    
    output logic tx_combined
);
    typedef enum logic[1:0] {
        ARB_IDLE,
        ARB_CROC,
        ARB_MONITOR
    } arb_state_t;

    arb_state_t state;
    
    logic croc_busy;
    logic [15:0] croc_idle_timer;
    logic monitor_locked;
    
    localparam CROC_IDLE_TIMEOUT = 16'd5000;
    
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= ARB_IDLE;
            croc_busy <= 0;
            croc_idle_timer <= 0;
            monitor_locked <= 0;
        end else begin
            if (tx_croc == 0) begin
                croc_busy <= 1;
                croc_idle_timer <= 0;
            end else if (croc_busy) begin
                if (croc_idle_timer < CROC_IDLE_TIMEOUT) begin
                    croc_idle_timer <= croc_idle_timer + 1;
                end else begin
                    croc_busy <= 0;
                end
            end
            
            case (state)
                ARB_IDLE: begin
                    monitor_locked <= 0;
                    
                    if (croc_busy) begin
                        state <= ARB_CROC;
                    end 
                    else if (monitor_active) begin
                        state <= ARB_MONITOR;
                        monitor_locked <= 1;
                    end
                end
                
                ARB_CROC: begin
                    if (!croc_busy) begin
                        state <= ARB_IDLE;
                    end
                end
                
                ARB_MONITOR: begin
                    if (!monitor_active) begin
                        state <= ARB_IDLE;
                        monitor_locked <= 0;
                    end
                end
                
                default: state <= ARB_IDLE;
            endcase
        end
    end

    always_comb begin
        case (state)
            ARB_CROC:    tx_combined = tx_croc;
            ARB_MONITOR: tx_combined = tx_monitor;
            default:     tx_combined = 1'b1;
        endcase
    end

endmodule