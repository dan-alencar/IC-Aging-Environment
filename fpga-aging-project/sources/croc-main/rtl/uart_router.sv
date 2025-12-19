`timescale 1ns / 1ps

module uart_router #(
    parameter int CLK_FREQ      = 20000000, 
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

    // =========================================================================
    // 1. WATCHDOG TIMER (Mantido original)
    // =========================================================================
    localparam int WD_CYCLES_LIMIT = (CLK_FREQ / 1000) * WATCHDOG_MS;
    int unsigned wd_counter;
    logic last_heartbeat;
    logic wd_alarm;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            wd_counter     <= 0;
            last_heartbeat <= 0;
            wd_alarm       <= 0;
            safe_rst_n     <= 0;
        end else begin
            if (heartbeat_pin != last_heartbeat) begin
                wd_counter     <= 0;
                last_heartbeat <= heartbeat_pin;
                wd_alarm       <= 0;
                safe_rst_n     <= 1;
            end else begin
                if (wd_counter < WD_CYCLES_LIMIT) begin
                    wd_counter <= wd_counter + 1;
                    safe_rst_n <= 1;
                end else begin
                    wd_alarm   <= 1;
                    safe_rst_n <= 0;
                end
            end
        end
    end

    // =========================================================================
    // 2. RX ROUTER (PC -> Dispositivos)
    // =========================================================================
    
    localparam int CLKS_PER_BIT = CLK_FREQ / BAUD_RATE;
    typedef enum logic [2:0] {RX_IDLE, RX_START, RX_DATA, RX_STOP} rx_state_t;
    rx_state_t rx_state;
    
    int unsigned rx_clk_count;
    int unsigned rx_bit_index;
    logic [7:0]  rx_byte;
    logic        rx_byte_valid;

    // Sincronizadores
    logic rx_sync, rx_temp;
    always_ff @(posedge clk) begin
        rx_temp <= uart_rx_phys;
        rx_sync <= rx_temp;
    end

    // Máquina de Estados RX (Sniffer de Header)
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            rx_state      <= RX_IDLE;
            rx_clk_count  <= 0;
            rx_bit_index  <= 0;
            rx_byte       <= 0;
            rx_byte_valid <= 0;
        end else begin
            rx_byte_valid <= 0;
            case (rx_state)
                RX_IDLE: begin
                    rx_clk_count <= 0;
                    rx_bit_index <= 0;
                    if (rx_sync == 1'b0) rx_state <= RX_START;
                end
                RX_START: begin
                    if (rx_clk_count == (CLKS_PER_BIT / 2)) begin
                        if (rx_sync == 1'b0) begin
                            rx_clk_count <= 0;
                            rx_state  <= RX_DATA;
                        end else rx_state <= RX_IDLE;
                    end else rx_clk_count <= rx_clk_count + 1;
                end
                RX_DATA: begin
                    if (rx_clk_count < CLKS_PER_BIT) rx_clk_count <= rx_clk_count + 1;
                    else begin
                        rx_clk_count <= 0;
                        rx_byte[rx_bit_index] <= rx_sync;
                        if (rx_bit_index < 7) rx_bit_index <= rx_bit_index + 1;
                        else begin
                            rx_bit_index <= 0;
                            rx_state  <= RX_STOP;
                        end
                    end
                end
                RX_STOP: begin
                    if (rx_clk_count < CLKS_PER_BIT) rx_clk_count <= rx_clk_count + 1;
                    else begin
                        rx_byte_valid <= 1;
                        rx_state      <= RX_IDLE;
                    end
                end
            endcase
        end
    end

    // Logica de Roteamento
    typedef enum logic [1:0] {ROUTE_NONE, ROUTE_CROC, ROUTE_STM} route_t;
    route_t current_route;
    
    localparam logic [7:0] HEADER_FPGA = 8'h10;
    localparam logic [7:0] HEADER_STM  = 8'h20;
    
    // Timeout para resetar rota (evita travamento se pacote incompleto)
    localparam int RX_IDLE_TIMEOUT_CYCLES = CLK_FREQ / 20; // 50ms
    int unsigned rx_idle_timer;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            current_route <= ROUTE_NONE;
            rx_idle_timer <= 0;
        end else begin
            if (rx_sync == 1'b0) rx_idle_timer <= 0; 
            else if (rx_idle_timer < RX_IDLE_TIMEOUT_CYCLES) rx_idle_timer <= rx_idle_timer + 1;

            if (wd_alarm) begin
                current_route <= ROUTE_STM; // Fail-safe
            end 
            else if (rx_idle_timer >= RX_IDLE_TIMEOUT_CYCLES) begin
                current_route <= ROUTE_NONE;
            end
            else if (rx_byte_valid) begin
                // AQUI ESTÁ A LÓGICA DE HEADER
                if (rx_byte == HEADER_FPGA) current_route <= ROUTE_CROC;
                else if (rx_byte == HEADER_STM) current_route <= ROUTE_STM;
            end
        end
    end

    // --- CORREÇÃO DO ROUTER RX ---
    always_comb begin
        // Padrão: Linha em Idle (High)
        uart_tx_to_croc = 1'b1;
        uart_tx_to_stm  = 1'b1;

        if (wd_alarm) begin
            uart_tx_to_stm = uart_rx_phys;
        end else begin
            case (current_route)
                ROUTE_CROC: uart_tx_to_croc = uart_rx_phys;
                ROUTE_STM:  uart_tx_to_stm  = uart_rx_phys; // Conexão Direta PC -> STM
                default:    ; 
            endcase
        end
        // REMOVIDO: uart_tx_to_stm = ... & uart_tx_from_croc; 
        // Isso causava colisão lógica quando o CROC imprimia logs.
    end

    // =========================================================================
    // 3. TX ARBITER (Prioridade Estrita para o STM32)
    // =========================================================================
    typedef enum logic [1:0] {TX_IDLE, TX_LOCK_CROC, TX_LOCK_STM} tx_arb_t;
    tx_arb_t tx_state;

    // Timeout reduzido para liberar o canal mais rápido entre caracteres
    localparam int TX_TIMEOUT_CYCLES = CLKS_PER_BIT * 12; // ~1 caractere + margem
    int unsigned tx_idle_timer;

    logic stm_tx_sync, croc_tx_sync;
    always_ff @(posedge clk) begin
        stm_tx_sync  <= uart_tx_from_stm;
        croc_tx_sync <= uart_tx_from_croc;
    end

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            tx_state      <= TX_IDLE;
            tx_idle_timer <= 0;
        end else begin
            case (tx_state)
                TX_IDLE: begin
                    tx_idle_timer <= 0;
                    // PRIORIDADE: Checa STM primeiro. Se STM quer falar (0), ganha o canal.
                    if (stm_tx_sync == 0) begin
                        tx_state <= TX_LOCK_STM;
                    end
                    // Só atende CROC se STM estiver quieto (1)
                    else if (croc_tx_sync == 0) begin
                        tx_state <= TX_LOCK_CROC;
                    end
                end

                TX_LOCK_CROC: begin
                    // Se CROC soltar a linha (Idle/1), conta tempo para liberar
                    if (croc_tx_sync == 1) begin
                        if (tx_idle_timer < TX_TIMEOUT_CYCLES) tx_idle_timer <= tx_idle_timer + 1;
                        else tx_state <= TX_IDLE; 
                    end else begin
                        tx_idle_timer <= 0;
                    end
                    
                    // (Opcional) Preempção: Se STM tentar falar, poderiamos cortar o CROC,
                    // mas isso corromperia o log. Melhor esperar o caractere atual acabar.
                end

                TX_LOCK_STM: begin
                    if (stm_tx_sync == 1) begin
                        if (tx_idle_timer < TX_TIMEOUT_CYCLES) tx_idle_timer <= tx_idle_timer + 1;
                        else tx_state <= TX_IDLE;
                    end else begin
                        tx_idle_timer <= 0;
                    end
                end
            endcase
        end
    end

    // Mux de Saída
    always_comb begin
        case (tx_state)
            TX_LOCK_CROC: uart_tx_phys = croc_tx_sync;
            TX_LOCK_STM:  uart_tx_phys = stm_tx_sync;
            default:      uart_tx_phys = 1'b1; 
        endcase
    end

endmodule