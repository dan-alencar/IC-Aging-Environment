// ============================================================================
// Modulo: aging_sensor_core
// Descricao: Nucleo logico do sensor de envelhecimento (aging sensor),
//            baseado na arquitetura da Fig. 1 do artigo de referencia:
//            2 flip-flops de captura (FF_sys_clk, FF_psclk) + XOR +
//            1 flip-flop de alarme (FF_alarm).
//
// Funcionamento:
//   O sinal do caminho critico (critical_path) e amostrado por dois
//   flip-flops em bordas de clock diferentes: uma pelo clock de
//   referencia do sistema (sys_clk) e outra por um clock defasado
//   (psclk). Se o atraso de propagacao do caminho critico aumentar
//   (por envelhecimento, queda de tensao ou aumento de temperatura),
//   as duas capturas podem divergir, o que e detectado pela porta XOR
//   e registrado no flip-flop de alarme (capturado por catcher_clk).
// ============================================================================

module aging_sensor_core (
    input  wire critical_path,   // saida do caminho critico monitorado
    input  wire sys_clk,         // clock de referencia do sistema
    input  wire psclk,           // clock defasado (phase-shifted), gerado pelo PLL
    input  wire catcher_clk,     // clock de captura do sinal de alarme
    input  wire reset,           // reset assincrono, ativo em nivel alto
    output wire alarm            // sinalizador de erosao de slack / falha de timing
);

    reg ff_sys_clk_q;
    reg ff_psclk_q;
    reg ff_alarm_q;

    wire xor_out;

    // FF_sys_clk: captura o caminho critico na borda de subida do sys_clk
    always @(posedge sys_clk or posedge reset) begin
        if (reset)
            ff_sys_clk_q <= 1'b0;
        else
            ff_sys_clk_q <= critical_path;
    end

    // FF_psclk: captura o mesmo sinal na borda de subida do psclk (defasado)
    always @(posedge psclk or posedge reset) begin
        if (reset)
            ff_psclk_q <= 1'b0;
        else
            ff_psclk_q <= critical_path;
    end

    // XOR: compara as duas capturas. Diferenca == sinal ainda em transicao
    // entre as duas bordas de amostragem (indicativo de slack insuficiente)
    assign xor_out = ff_sys_clk_q ^ ff_psclk_q;

    // FF_alarm: registra o resultado da comparacao, sincronizado pelo catcher_clk
    always @(posedge catcher_clk or posedge reset) begin
        if (reset)
            ff_alarm_q <= 1'b0;
        else
            ff_alarm_q <= xor_out;
    end

    assign alarm = ff_alarm_q;

endmodule
