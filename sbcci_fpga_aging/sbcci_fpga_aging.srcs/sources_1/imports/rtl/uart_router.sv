`timescale 1ns / 1ps

module uart_router #(
    parameter int CLK_FREQ      = 100000000, 
    parameter int BAUD_RATE     = 115200,   
    parameter int WATCHDOG_MS   = 1000      
)(
    input  logic clk,
    input  logic rst_n,

    // --- Interface com o PC (IHM) ---
    input  logic uart_rx_phys,      // PC TX -> FPGA RX
    output logic uart_tx_phys,      // FPGA TX -> PC RX

    // --- Interface com o CROC (FPGA Softcore) ---
    output logic uart_tx_to_croc,   // Router -> CROC RX
    input  logic uart_tx_from_croc, // CROC TX -> Router

    // --- Interface com o STM32 (Microcontrolador) ---
    output logic uart_tx_to_stm,    // Router -> STM RX
    input  logic uart_tx_from_stm,  // STM TX -> Router

    // --- Segurança ---
    input  logic heartbeat_pin,   
    output logic safe_rst_n       
);

    // =========================================================================
    // 1. FORWARD PATH (THE FIX)
    // =========================================================================
    // Routes PC commands directly to STM32 and Softcore.
    // Without this, the STM32 RX pin is floating/undriven.
    assign uart_tx_to_stm  = uart_rx_phys;
    assign uart_tx_to_croc = uart_rx_phys;

    // =========================================================================
    // 2. WATCHDOG TIMER (Kept from Original Source)
    // =========================================================================
    localparam int WD_CYCLES_LIMIT = (CLK_FREQ / 1000) * WATCHDOG_MS;
    int unsigned wd_counter;
    logic last_heartbeat;
    logic wd_alarm;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            wd_counter <= 0;
            last_heartbeat <= 0;
            wd_alarm <= 0;
        end else begin
            if (heartbeat_pin != last_heartbeat) begin
                wd_counter <= 0;
                last_heartbeat <= heartbeat_pin;
                wd_alarm <= 0;
            end else begin
                if (wd_counter < WD_CYCLES_LIMIT) 
                    wd_counter <= wd_counter + 1;
                else 
                    wd_alarm <= 1; // Watchdog Timeout
            end
        end
    end
    
    // For now, passthrough. Enable 'wd_alarm' logic when Softcore is ready.
    assign safe_rst_n = rst_n; 

    // =========================================================================
    // 3. TX ARBITRATION (RETURN PATH) (Kept from Original Source)
    // =========================================================================
    // Determines who talks to the PC: Softcore or STM32?
    typedef enum {TX_IDLE, TX_LOCK_CROC, TX_LOCK_STM} tx_state_t;
    tx_state_t tx_state;

    // Synchronizers
    logic croc_tx_sync, stm_tx_sync;
    always_ff @(posedge clk) begin
        croc_tx_sync <= uart_tx_from_croc;
        stm_tx_sync  <= uart_tx_from_stm;
    end

    // Timeout to release line if stuck
    int unsigned tx_idle_timer;
    localparam int TX_TIMEOUT_CYCLES = CLK_FREQ / 1000; // 1ms

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            tx_state <= TX_IDLE;
            tx_idle_timer <= 0;
        end else begin
            case (tx_state)
                TX_IDLE: begin
                    tx_idle_timer <= 0;
                    // Priority to CROC (Softcore)
                    if (croc_tx_sync == 0) begin
                        tx_state <= TX_LOCK_CROC;
                    end 
                    // Serve STM32 if CROC is silent (1)
                    else if (stm_tx_sync == 0) begin
                        tx_state <= TX_LOCK_STM;
                    end
                end

                TX_LOCK_CROC: begin
                    if (croc_tx_sync == 1) begin
                        if (tx_idle_timer < TX_TIMEOUT_CYCLES) 
                            tx_idle_timer <= tx_idle_timer + 1;
                        else 
                            tx_state <= TX_IDLE; 
                    end else begin
                        tx_idle_timer <= 0;
                    end
                end

                TX_LOCK_STM: begin
                    if (stm_tx_sync == 1) begin
                        if (tx_idle_timer < TX_TIMEOUT_CYCLES) 
                            tx_idle_timer <= tx_idle_timer + 1;
                        else 
                            tx_state <= TX_IDLE;
                    end else begin
                        tx_idle_timer <= 0;
                    end
                end
            endcase
        end
    end

    // Mux Output
    always_comb begin
        case (tx_state)
            TX_LOCK_CROC: uart_tx_phys = croc_tx_sync;
            TX_LOCK_STM:  uart_tx_phys = stm_tx_sync;
            default:      uart_tx_phys = 1'b1; // Idle
        endcase
    end

endmodule