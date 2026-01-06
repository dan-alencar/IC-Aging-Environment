`timescale 1ns / 1ps

module uart_arbiter (
    input  logic clk,
    input  logic rst_n,
    
    // Canal 1: CROC (Texto/Debug) - Prioridade Alta
    input  logic tx_croc,
    
    // Canal 2: Monitor Aging (Pacotes Binários) - Prioridade Baixa
    input  logic tx_monitor,
    input  logic monitor_active, // Sinal 'tx_active' do módulo anterior
    
    // Saída Combinada
    output logic tx_combined
);

    // Detecta se o CROC está ocupando a linha
    // O UART fica em 1 quando Idle. Se for 0, está transmitindo.
    // Vamos adicionar um pequeno timer para garantir que o CROC terminou mesmo.
    
    logic croc_busy;
    int unsigned idle_cnt;
    
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            croc_busy <= 0;
            idle_cnt <= 0;
        end else begin
            if (tx_croc == 0) begin
                croc_busy <= 1;
                idle_cnt <= 0;
            end else begin
                // Se linha em 1, conta um pouco antes de liberar
                if (idle_cnt < 1000) idle_cnt <= idle_cnt + 1;
                else croc_busy <= 0;
            end
        end
    end

    // Lógica de Mux
    always_comb begin
        if (croc_busy) begin
            // Se o CROC está falando, a saída é dele.
            // O monitor deve ter lógica interna para pausar ou perder o pacote se colidir.
            tx_combined = tx_croc;
        end else if (monitor_active) begin
            // Se o CROC está quieto e o monitor quer falar
            tx_combined = tx_monitor;
        end else begin
            // Idle
            tx_combined = 1'b1;
        end
    end

endmodule
