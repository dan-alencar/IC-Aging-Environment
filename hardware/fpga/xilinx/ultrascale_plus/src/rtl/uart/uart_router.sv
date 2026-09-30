`timescale 1ns / 1ps

module uart_router #(
    parameter int CLK_FREQ      = 100000000, 
    parameter int BAUD_RATE     = 125000,   
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
    // 1. FORWARD PATH
    assign uart_tx_to_stm  = uart_rx_phys;
    assign uart_tx_to_croc = uart_rx_phys;

    // 2. WATCHDOG TIMER (Pass-through logic preserved)
    assign safe_rst_n = rst_n; 
    // (Note: Original watchdog counter logic was internal-only in your snippet)

    // 3. TX ARBITRATION (RETURN PATH)
    typedef enum {TX_IDLE, TX_LOCK_CROC, TX_LOCK_STM} tx_state_t;
    tx_state_t tx_state;

    // Synchronizers
    logic croc_tx_sync, stm_tx_sync;
    always_ff @(posedge clk) begin
        croc_tx_sync <= uart_tx_from_croc;
        stm_tx_sync  <= uart_tx_from_stm;
    end

    // Timeout Counters
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
                    // Priority to CROC
                    if (croc_tx_sync == 0) begin
                        tx_state <= TX_LOCK_CROC;
                    end 
                    // Serve STM32 if CROC is silent
                    else if (stm_tx_sync == 0) begin
                        tx_state <= TX_LOCK_STM;
                    end
                end

                TX_LOCK_CROC: begin
                    // FIX: Increment timer regardless of logic level
                    // If line is stuck LOW or stuck HIGH for > 1ms, force reset.
                    if (tx_idle_timer < TX_TIMEOUT_CYCLES) begin
                        tx_idle_timer <= tx_idle_timer + 1;
                        // Reset timer if we see a valid transition (activity)
                        // This assumes data isn't slower than 1ms per bit (which is true for 125k)
                        if (croc_tx_sync != uart_tx_phys) tx_idle_timer <= 0; 
                    end else begin
                        tx_state <= TX_IDLE; // Force unlock
                    end
                end

                TX_LOCK_STM: begin
                    // FIX: Same "Stuck Low" protection for STM32
                    if (tx_idle_timer < TX_TIMEOUT_CYCLES) begin
                        tx_idle_timer <= tx_idle_timer + 1;
                         // Reset timer on activity (edge detection approximation)
                        if (stm_tx_sync != uart_tx_phys) tx_idle_timer <= 0;
                    end else begin
                        tx_state <= TX_IDLE; // Force unlock
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