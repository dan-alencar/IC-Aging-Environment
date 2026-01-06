`timescale 1ns / 1ps

module sysmon_monitor #(
    parameter int CLK_FREQ = 20000000, // Verifique se bate com seu sys_clk
    parameter int BAUD_RATE = 125000
)(
    input  logic        clk,
    input  logic        rst_n,
    
    // Entradas de Sensores Externos (Aging/Slack)
    input  logic        aging_alarm,
    
    // Saída Serial (UART TX)
    output logic        tx_out,
    output logic        tx_active // Indica para o Arbiter que estamos usando a linha
);

    // =========================================================================
    // 1. Instância da Primitiva SYSMONE4 (UltraScale+)
    // =========================================================================
    logic [15:0] do_data;
    logic        drdy;
    logic        den;
    logic [6:0]  daddr;
    
    // Configura o SYSMONE4 para ler Temp e VccInt continuamente
    SYSMONE4 #(
        .COMMON_N_SOURCE(16'hFFFF), 
        .INIT_40(16'h0000), .INIT_41(16'h2101), .INIT_42(16'h0200),
        .INIT_48(16'h0100), .INIT_49(16'h0001)
    ) sysmon_inst (
        .DCLK(clk), .RESET(!rst_n), 
        .DADDR(daddr), .DEN(den), .DWE(1'b0), .DI(16'h0),
        .DO(do_data), .DRDY(drdy), .EOS(),
        .VP(1'b0), .VN(1'b0)
    );

    // =========================================================================
    // 2. Máquina de Estados de Leitura dos Dados
    // =========================================================================
    typedef enum {IDLE, WAIT_DRDY_TEMP, STORE_TEMP, WAIT_DRDY_VCC, STORE_VCC, SEND_PACKET} state_t;
    state_t state;
    
    logic [15:0] reg_temp, reg_vcc;
    logic uart_busy_internal; // Flag declarada aqui!
    
    // Timer para leitura periódica (ex: a cada 0.5s)
    int unsigned timer;
    localparam int TIMER_LIMIT = CLK_FREQ / 2; 

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= IDLE;
            timer <= 0;
            den <= 0;
            daddr <= 0;
            reg_temp <= 0; reg_vcc <= 0;
        end else begin
            case (state)
                IDLE: begin
                    if (timer >= TIMER_LIMIT) begin
                        timer <= 0;
                        daddr <= 7'h00; // Endereço Temp
                        den <= 1;
                        state <= WAIT_DRDY_TEMP;
                    end else begin
                        timer <= timer + 1;
                    end
                end
                
                WAIT_DRDY_TEMP: begin
                    den <= 0;
                    if (drdy) begin
                        reg_temp <= do_data;
                        daddr <= 7'h01; // Endereço VccInt
                        den <= 1;
                        state <= WAIT_DRDY_VCC;
                    end
                end
                
                WAIT_DRDY_VCC: begin
                    den <= 0;
                    if (drdy) begin
                        reg_vcc <= do_data;
                        state <= SEND_PACKET;
                    end
                end
                
                SEND_PACKET: begin
                    // Só volta para IDLE quando o pacote inteiro for enviado
                    // Quem controla 'tx_active' é o bloco abaixo
                    if (!tx_active) state <= IDLE;
                end
            endcase
        end
    end

    // =========================================================================
    // 3. Montador de Pacotes (Packet Builder)
    // =========================================================================
    // Estrutura: [HEADER 0x1A] [TEMP_H] [TEMP_L] [VCC_H] [VCC_L] [ALARM]
    
    logic       uart_start;
    logic [7:0] uart_byte;
    logic [2:0] tx_idx;
    logic       sending_sequence;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            uart_start <= 0;
            tx_idx <= 0;
            tx_active <= 0;
            sending_sequence <= 0;
            uart_byte <= 0;
        end else begin
            // Início da sequência de envio
            if (state == SEND_PACKET && !sending_sequence) begin
                sending_sequence <= 1;
                tx_active <= 1;   // Reivindica o bus (Sinal para o Arbiter)
                tx_idx <= 0;
                
                // Prepara primeiro byte (Header)
                uart_byte <= 8'h1A; 
                uart_start <= 1;    // Dispara TX
            end 
            else if (sending_sequence) begin
                // Tira o sinal de start logo após 1 ciclo (pulso)
                if (uart_start) uart_start <= 0;

                // Se o transmissor terminou o byte atual e não estamos mandando start
                if (!uart_busy_internal && !uart_start) begin
                    if (tx_idx == 5) begin
                        // Fim do pacote
                        sending_sequence <= 0;
                        tx_active <= 0; 
                    end else begin
                        // Prepara próximo byte
                        tx_idx <= tx_idx + 1;
                        uart_start <= 1;
                        case (tx_idx) // Note: tx_idx ainda é o anterior aqui no case
                            0: uart_byte <= reg_temp[15:8];
                            1: uart_byte <= reg_temp[7:0];
                            2: uart_byte <= reg_vcc[15:8];
                            3: uart_byte <= reg_vcc[7:0];
                            4: uart_byte <= {7'b0, aging_alarm};
                        endcase
                    end
                end
            end
        end
    end

    // =========================================================================
    // 4. UART TX Embutido (Substitui módulo externo)
    // =========================================================================
    localparam int BIT_PERIOD = CLK_FREQ / BAUD_RATE;
    
    int unsigned baud_cnt;
    int unsigned bit_cnt;
    logic [8:0]  shifter; // 8 dados + 1 stop (Start é implícito na lógica)
    typedef enum {TX_IDLE, TX_START, TX_DATA, TX_STOP} tx_state_t;
    tx_state_t tx_state;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            tx_out <= 1; // Idle High
            uart_busy_internal <= 0;
            tx_state <= TX_IDLE;
            baud_cnt <= 0;
            bit_cnt <= 0;
            shifter <= 0;
        end else begin
            case (tx_state)
                TX_IDLE: begin
                    tx_out <= 1;
                    if (uart_start) begin
                        uart_busy_internal <= 1;
                        shifter <= {1'b1, uart_byte}; // Stop bit + Dados
                        tx_state <= TX_START;
                        baud_cnt <= 0;
                    end else begin
                        uart_busy_internal <= 0;
                    end
                end

                TX_START: begin
                    tx_out <= 0; // Start Bit (Low)
                    if (baud_cnt < BIT_PERIOD - 1) begin
                        baud_cnt <= baud_cnt + 1;
                    end else begin
                        baud_cnt <= 0;
                        bit_cnt <= 0;
                        tx_state <= TX_DATA;
                    end
                end

                TX_DATA: begin
                    tx_out <= shifter[0]; // LSB First
                    if (baud_cnt < BIT_PERIOD - 1) begin
                        baud_cnt <= baud_cnt + 1;
                    end else begin
                        baud_cnt <= 0;
                        shifter <= shifter >> 1;
                        if (bit_cnt < 7) begin
                            bit_cnt <= bit_cnt + 1;
                        end else begin
                            tx_state <= TX_STOP;
                        end
                    end
                end

                TX_STOP: begin
                    tx_out <= 1; // Stop Bit (High)
                    if (baud_cnt < BIT_PERIOD - 1) begin
                        baud_cnt <= baud_cnt + 1;
                    end else begin
                        baud_cnt <= 0;
                        tx_state <= TX_IDLE; // Fim da transmissão
                        uart_busy_internal <= 0;
                    end
                end
            endcase
        end
    end

endmodule