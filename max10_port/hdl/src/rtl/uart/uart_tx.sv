// ============================================================================
// Modulo: uart_tx
// Descricao: Transmissor UART generico, 8 bits de dados, sem paridade,
//            1 stop bit (formato 8N1). Parametrizado por frequencia do
//            clock e baud rate.
//
// Uso:
//   1) Coloque o byte a transmitir em data_in
//   2) Pulse tx_start por 1 ciclo de clock (so funciona se tx_busy=0)
//   3) Aguarde tx_busy cair para 0 antes de enviar o proximo byte
// ============================================================================

module uart_tx #(
    parameter integer CLK_FREQ_HZ = 50_000_000,  // frequencia do clock de entrada
    parameter integer BAUD_RATE   = 115200        // baud rate desejado (ESP32 devkit default)
)(
    input  wire       clk,
    input  wire       reset,      // reset assincrono, ativo em nivel alto
    input  wire [7:0] data_in,    // byte a ser transmitido
    input  wire       tx_start,   // pulso de 1 ciclo para iniciar a transmissao
    output reg        tx,         // linha serial de saida (idle = 1)
    output reg        tx_busy     // 1 enquanto uma transmissao esta em andamento
);

    // Numero de ciclos de clock por bit serial
    localparam integer CLKS_PER_BIT = CLK_FREQ_HZ / BAUD_RATE;

    localparam [1:0]
        S_IDLE  = 2'd0,
        S_START = 2'd1,
        S_DATA  = 2'd2,
        S_STOP  = 2'd3;

    reg [1:0]  state;
    reg [15:0] clk_count;
    reg [2:0]  bit_index;
    reg [7:0]  data_reg;

    always @(posedge clk or posedge reset) begin
        if (reset) begin
            state     <= S_IDLE;
            tx        <= 1'b1;   // linha em repouso fica em nivel alto
            tx_busy   <= 1'b0;
            clk_count <= 16'd0;
            bit_index <= 3'd0;
            data_reg  <= 8'h00;
        end else begin
            case (state)
                S_IDLE: begin
                    tx        <= 1'b1;
                    clk_count <= 16'd0;
                    bit_index <= 3'd0;
                    if (tx_start) begin
                        data_reg <= data_in;
                        tx_busy  <= 1'b1;
                        state    <= S_START;
                    end else begin
                        tx_busy <= 1'b0;
                    end
                end

                S_START: begin
                    tx <= 1'b0;  // bit de start
                    if (clk_count < CLKS_PER_BIT - 1)
                        clk_count <= clk_count + 16'd1;
                    else begin
                        clk_count <= 16'd0;
                        state     <= S_DATA;
                    end
                end

                S_DATA: begin
                    tx <= data_reg[bit_index];  // LSB primeiro
                    if (clk_count < CLKS_PER_BIT - 1)
                        clk_count <= clk_count + 16'd1;
                    else begin
                        clk_count <= 16'd0;
                        if (bit_index < 3'd7)
                            bit_index <= bit_index + 3'd1;
                        else begin
                            bit_index <= 3'd0;
                            state     <= S_STOP;
                        end
                    end
                end

                S_STOP: begin
                    tx <= 1'b1;  // bit de stop
                    if (clk_count < CLKS_PER_BIT - 1)
                        clk_count <= clk_count + 16'd1;
                    else begin
                        clk_count <= 16'd0;
                        tx_busy   <= 1'b0;
                        state     <= S_IDLE;
                    end
                end

                default: state <= S_IDLE;
            endcase
        end
    end

endmodule
