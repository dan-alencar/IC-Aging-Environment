// ============================================================================
// Modulo: uart_packet_sender
// Descricao: Monta e envia periodicamente, via UART, um pacote de 5 bytes
//            contendo slack_count, calibrated e alarm.
//
// Formato do pacote (enviado a cada SEND_INTERVAL_MS milissegundos):
//
//   Byte 0: 0xAA                 -- marcador de sincronismo/inicio
//   Byte 1: slack_count[15:8]    -- MSB do contador de incrementos de fase
//   Byte 2: slack_count[7:0]     -- LSB do contador de incrementos de fase
//   Byte 3: status               -- bit0 = alarm, bit1 = calibrated, resto = 0
//   Byte 4: checksum             -- byte1 XOR byte2 XOR byte3
//
// Os valores de slack_count/calibrated/alarm sao capturados ("congelados")
// no instante em que a transmissao de um novo pacote comeca, evitando que
// os dados mudem no meio do envio.
// ============================================================================

module uart_packet_sender #(
    parameter integer CLK_FREQ_HZ     = 50_000_000,  // frequencia do clock de entrada
    parameter integer BAUD_RATE       = 115200,       // baud rate (ESP32 devkit default)
    parameter integer SEND_INTERVAL_MS = 100          // periodo entre pacotes enviados
)(
    input  wire        clk,
    input  wire        reset,        // reset assincrono, ativo em nivel alto
    input  wire [15:0] slack_count,
    input  wire        calibrated,
    input  wire        alarm,
    output wire        uart_txd      // linha serial de saida, ligar a um adaptador USB-TTL externo
);

    // ------------------------------------------------------------------
    // Temporizador: gera um pulso de "send_request" a cada SEND_INTERVAL_MS
    // ------------------------------------------------------------------
    localparam integer CYCLES_PER_MS        = CLK_FREQ_HZ / 1000;
    localparam integer SEND_INTERVAL_CYCLES = CYCLES_PER_MS * SEND_INTERVAL_MS;

    reg [31:0] timer;
    reg        send_request;

    always @(posedge clk or posedge reset) begin
        if (reset) begin
            timer        <= 32'd0;
            send_request <= 1'b0;
        end else if (timer >= SEND_INTERVAL_CYCLES - 1) begin
            timer        <= 32'd0;
            send_request <= 1'b1;
        end else begin
            timer        <= timer + 32'd1;
            send_request <= 1'b0;
        end
    end

    // ------------------------------------------------------------------
    // Transmissor UART de baixo nivel
    // ------------------------------------------------------------------
    wire       tx_busy;
    reg        tx_start;
    reg [7:0]  data_in;

    uart_tx #(
        .CLK_FREQ_HZ (CLK_FREQ_HZ),
        .BAUD_RATE   (BAUD_RATE)
    ) u_uart_tx (
        .clk      (clk),
        .reset    (reset),
        .data_in  (data_in),
        .tx_start (tx_start),
        .tx       (uart_txd),
        .tx_busy  (tx_busy)
    );

    // ------------------------------------------------------------------
    // Montagem do pacote e maquina de estados de envio
    // ------------------------------------------------------------------
    reg [7:0] byte1, byte2, byte3, byte4;
    reg [2:0] byte_idx;

    localparam [1:0]
        S_IDLE      = 2'd0,
        S_ASSERT    = 2'd1,
        S_WAIT_HIGH = 2'd2,
        S_WAIT_LOW  = 2'd3;

    reg [1:0] state;

    always @(posedge clk or posedge reset) begin
        if (reset) begin
            state    <= S_IDLE;
            tx_start <= 1'b0;
            byte_idx <= 3'd0;
            byte1    <= 8'h00;
            byte2    <= 8'h00;
            byte3    <= 8'h00;
            byte4    <= 8'h00;
            data_in  <= 8'h00;
        end else begin
            tx_start <= 1'b0;  // por padrao, desativado; so sobe explicitamente abaixo

            case (state)
                S_IDLE: begin
                    if (send_request) begin
                        // "Congela" os valores atuais no instante do disparo
                        // (o byte de sincronismo 0xAA e enviado direto, sem
                        // precisar de um registrador para ele)
                        byte1 <= slack_count[15:8];
                        byte2 <= slack_count[7:0];
                        byte3 <= {6'b000000, calibrated, alarm};
                        byte4 <= slack_count[15:8] ^ slack_count[7:0] ^ {6'b000000, calibrated, alarm};

                        byte_idx <= 3'd0;
                        data_in  <= 8'hAA;
                        tx_start <= 1'b1;
                        state    <= S_WAIT_HIGH;
                    end
                end

                // Aguarda o uart_tx reconhecer o pedido (tx_busy sobe)
                S_WAIT_HIGH: begin
                    if (tx_busy)
                        state <= S_WAIT_LOW;
                end

                // Aguarda o byte atual terminar de ser transmitido (tx_busy cai)
                S_WAIT_LOW: begin
                    if (!tx_busy) begin
                        if (byte_idx == 3'd4) begin
                            state <= S_IDLE;  // pacote completo
                        end else begin
                            byte_idx <= byte_idx + 3'd1;
                            case (byte_idx + 3'd1)
                                3'd1: data_in <= byte1;
                                3'd2: data_in <= byte2;
                                3'd3: data_in <= byte3;
                                3'd4: data_in <= byte4;
                                default: data_in <= 8'h00;
                            endcase
                            tx_start <= 1'b1;
                            state    <= S_WAIT_HIGH;
                        end
                    end
                end

                default: state <= S_IDLE;
            endcase
        end
    end

endmodule
