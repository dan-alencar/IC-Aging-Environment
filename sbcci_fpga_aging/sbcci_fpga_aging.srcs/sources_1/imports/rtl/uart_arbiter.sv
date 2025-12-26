`timescale 1ns / 1ps

module uart_arbiter (
    input  logic clk,
    input  logic rst_n,
    
    // Channel 1: CROC/Router (Text/Debug) - High Priority
    input  logic tx_croc,
    
    // Channel 2: Monitor (Binary Packets) - Low Priority
    input  logic tx_monitor,
    input  logic monitor_active,
    
    // Combined Output
    output logic tx_combined
);

    // State machine for arbitration
    typedef enum logic[1:0] {
        ARB_IDLE,
        ARB_CROC,
        ARB_MONITOR
    } arb_state_t;
    
    arb_state_t state;
    
    // Detect when CROC is transmitting (UART idle = 1, transmit = 0)
    logic croc_busy;
    logic [15:0] croc_idle_timer;
    
    // Small timeout to ensure CROC has finished
    localparam CROC_IDLE_TIMEOUT = 16'd5000;  // ~50us at 100MHz
    
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= ARB_IDLE;
            croc_busy <= 0;
            croc_idle_timer <= 0;
        end else begin
            // Detect CROC activity
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
            
            // Arbitration state machine
            case (state)
                ARB_IDLE: begin
                    // Priority to CROC
                    if (croc_busy) begin
                        state <= ARB_CROC;
                    end 
                    // Monitor can transmit if CROC is quiet
                    else if (monitor_active) begin
                        state <= ARB_MONITOR;
                    end
                end
                
                ARB_CROC: begin
                    // Stay locked to CROC until it finishes
                    if (!croc_busy) begin
                        state <= ARB_IDLE;
                    end
                end
                
                ARB_MONITOR: begin
                    // Monitor keeps the channel until done
                    // BUT if CROC suddenly needs it, we must handle gracefully
                    if (!monitor_active) begin
                        state <= ARB_IDLE;
                    end
                    // CROC can preempt between packets but not during
                    else if (croc_busy && tx_monitor == 1) begin
                        // Only switch if monitor is between bytes (line idle)
                        state <= ARB_CROC;
                    end
                end
                
                default: state <= ARB_IDLE;
            endcase
        end
    end

    // Output multiplexer
    always_comb begin
        case (state)
            ARB_CROC:    tx_combined = tx_croc;
            ARB_MONITOR: tx_combined = tx_monitor;
            default:     tx_combined = 1'b1;  // Idle high
        endcase
    end

endmodule