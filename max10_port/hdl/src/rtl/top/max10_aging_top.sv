// ============================================================================
// Modulo: max10_aging_top
// Descricao: Modulo de topo que integra a PLL (aging_pll), o caminho critico
//            (critical_path_chain) e o nucleo do sensor de envelhecimento
//            (aging_sensor_core).
//
//            Um registrador de "lancamento" (launch) alterna de valor a
//            cada borda de sys_clk, injetando uma transicao na cadeia de
//            inversores a cada ciclo -- similar ao "critical_path_start"
//            mencionado na Fig. 8 do artigo de referencia.
//
// Observacao importante sobre esta etapa:
//   O controlador SCC (scc_controller) ja esta integrado e aciona
//   dinamicamente phasestep/phaseupdown, avancando a fase do psclk
//   enquanto o alarme do sensor estiver em LOW. O passo de fase desta
//   PLL (Quartus, MAX 10) e vco_phase_shift_step = 179 ps (ver
//   aging_pll.v, defparam altpll_component.vco_phase_shift_step), NAO
//   os 96 ps / VCO 1300 MHz do artigo de referencia (que usa MMCM da
//   Xilinx). Ao converter slack_count para ps no host/UART, use
//   179 ps/incremento.
//
//   phasecounterselect = 3'b011 seleciona o contador c1 (psclk) como
//   alvo do deslocamento de fase (000=todos os C, 001=M, 010=C0,
//   011=C1, 100=C2 -- Intel MAX 10 Clocking and PLL User Guide).
//
//   u_scc_controller.pll_locked precisa estar conectado a pll_locked
//   (saida 'locked' da PLL): sem essa conexao, o Quartus amarra a
//   entrada em GND por padrao, rst_i fica preso em 1 para sempre, e a
//   FSM nunca sai de S_IDLE (sintoma: LEDs de debug presos, slack_count
//   sempre 0). O Connectivity Check do Quartus aponta isso explicitamente
//   se acontecer de novo ("port ... not connected by instance").
//
//   ATENCAO -- HISTORICO: ambas as correcoes acima (phasecounterselect
//   e a conexao de pll_locked) ja foram feitas, perdidas por uma
//   reextracao acidental do .zip original do projeto por cima da copia
//   corrigida, e reaplicadas aqui. Antes de editar este arquivo a partir
//   de uma copia nova, confirme que essas duas coisas estao presentes.
// ============================================================================

module max10_aging_top (
    input  wire clk50,               // MAX10_CLK1_50: oscilador on-board de 50 MHz
    input  wire cpu_resetn,           // KEY0: botao fisico, ATIVO EM NIVEL BAIXO
    output wire alarm,                // saida do sensor: erosao de slack / falha de timing
    output wire pll_locked,           // sinal de depuracao: indica se a PLL travou (locked)
    output wire calibrated,           // em 1 quando a calibracao terminou (alarme disparou)
    output wire uart_txd,             // saida serial (ligar a um adaptador USB-TTL externo, ou futuramente ao ESP32)
    output wire [6:0] hex0,           // display de 7 segmentos: slack_count[3:0]   (nibble 0, menos significativo)
    output wire [6:0] hex1,           // display de 7 segmentos: slack_count[7:4]   (nibble 1)
    output wire [6:0] hex2,           // display de 7 segmentos: slack_count[11:8]  (nibble 2)
    output wire [6:0] hex3,           // display de 7 segmentos: slack_count[15:12] (nibble 3, mais significativo)

    // LEDs de depuracao: mostram o estado da FSM do scc_controller e o
    // nivel bruto de phasedone, para diagnostico no hardware real
    output wire dbg_phasedone,
    output wire dbg_idle,
    output wire dbg_step,
    output wire dbg_wait_low,
    output wire dbg_wait_high,
    output wire dbg_done,
    output wire dbg_alarm_sync  // alarm ja sincronizado no dominio scanclk (compare com o LEDR1/alarm bruto)
);

    // slack_count, launch_probe e critical_path_probe agora sao fios
    // INTERNOS (nao mais portas de topo) -- sao usados apenas para
    // alimentar os displays de 7 segmentos e a UART, nao precisam de
    // pino fisico proprio. Isso tambem resolve os 18 pinos sem
    // atribuicao (16 bits de slack_count + esses 2 probes).
    wire [15:0] slack_count;
    wire launch_probe;
    wire critical_path_probe;

    // reset interno ativo em nivel ALTO, gerado a partir do botao (ativo em nivel baixo)
    wire reset = ~cpu_resetn;

    // ------------------------------------------------------------------
    // PLL: gera sys_clk (c0), psclk (c1, deslocamento dinamico) e
    // catcher_clk (c2, deslocamento fixo) a partir do clock de 50 MHz
    // ------------------------------------------------------------------
    wire sys_clk;
    wire psclk;
    wire catcher_clk;
    wire pll_phasedone;
    wire scc_phasestep;
    wire scc_phaseupdown;
    wire alarm_w;

    aging_pll u_aging_pll (
        .inclk0            (clk50),
        .areset            (reset),

        // Controle de deslocamento dinamico de fase: agora vindo do scc_controller
        .phasecounterselect (3'b011),        // seleciona o contador c1 (psclk) -- CORRIGIDO (regrediu para 3'b100=c2 numa reextracao acidental; ver nota no cabecalho)
        .phaseupdown        (scc_phaseupdown),
        .phasestep          (scc_phasestep),
        .scanclk            (clk50),         // clock do scan chain interno da PLL

        .c0                (sys_clk),
        .c1                (psclk),
        .c2                (catcher_clk),
        .phasedone         (pll_phasedone),
        .locked            (pll_locked)
    );
	 
	 // ------------------------------------------------------------------
    // Controlador SCC: avanca a fase do psclk ate o alarme disparar
    // ------------------------------------------------------------------
    scc_controller #(
        .COUNT_WIDTH (16)
    ) u_scc_controller (
        .scanclk      (clk50),
        .reset        (reset),
        .pll_locked   (pll_locked),   // RECONECTADO -- estava ausente (Connectivity Check confirmou:
                                        // porta nao conectada = amarrada em GND, prendendo rst_i em 1
                                        // para sempre; causa do travamento com reset permanente)
        .alarm        (alarm_w),
        .phasedone    (pll_phasedone),
        .phasestep    (scc_phasestep),
        .phaseupdown  (scc_phaseupdown),
        .slack_count  (slack_count),
        .calibrated   (calibrated),
        .dbg_idle       (dbg_idle),
        .dbg_step       (dbg_step),
        .dbg_wait_low   (dbg_wait_low),
        .dbg_wait_high  (dbg_wait_high),
        .dbg_done       (dbg_done),
        .dbg_alarm_sync (dbg_alarm_sync)
    );

    assign dbg_phasedone = pll_phasedone;

    // ------------------------------------------------------------------
    // Registrador de lancamento: alterna de valor a cada ciclo de sys_clk,
    // gerando uma transicao que percorre a cadeia de inversores
    // ------------------------------------------------------------------
    reg launch;

    always @(posedge sys_clk or posedge reset) begin
        if (reset)
            launch <= 1'b0;
        else
            launch <= ~launch;
    end

    wire critical_path_out;

    // Caminho critico: cadeia de 50 inversores (LUTs WYSIWYG)
    critical_path_chain #(
        .NUM_STAGES (50)
    ) u_critical_path (
        .in  (launch),
        .out (critical_path_out)
    );

    // Nucleo do sensor de envelhecimento
    aging_sensor_core u_aging_sensor (
        .critical_path (critical_path_out),
        .sys_clk       (sys_clk),
        .psclk         (psclk),
        .catcher_clk   (catcher_clk),
        .reset         (reset),
        .alarm         (alarm_w)
    );

    assign alarm = alarm_w;

    // Probes de depuracao (uteis para observar no Signal Tap depois)
    assign launch_probe          = launch;
    assign critical_path_probe   = critical_path_out;

    // ------------------------------------------------------------------
    // UART: envia slack_count, calibrated e alarm periodicamente.
    // Usa clk50 diretamente (nao sys_clk) para funcionar de forma
    // independente/robusta, mesmo se a PLL nao estiver travada ainda.
    // ------------------------------------------------------------------
    uart_packet_sender #(
        .CLK_FREQ_HZ      (50_000_000),
        .BAUD_RATE        (115200),
        .SEND_INTERVAL_MS (100)
    ) u_uart_sender (
        .clk          (clk50),
        .reset        (reset),
        .slack_count  (slack_count),
        .calibrated   (calibrated),
        .alarm        (alarm_w),
        .uart_txd     (uart_txd)
    );

    // ------------------------------------------------------------------
    // Displays de 7 segmentos: mostram os 16 bits COMPLETOS de
    // slack_count em hexadecimal (0000-FFFF), para verificacao visual
    // direto na placa, sem precisar de PC.
    //
    // ANTES, so hex0/hex1 existiam (8 bits, 0-255): com margens de
    // dezenas ou centenas de ns e passo de 179 ps, o numero real de
    // incrementos facilmente ultrapassa 255 e da a volta (wraparound)
    // silenciosamente -- o valor exibido parecia pequeno mesmo quando
    // o sensor tinha calibrado corretamente com uma contagem bem maior.
    // Com os 4 displays, o valor mostrado e sempre o slack_count real,
    // sem ambiguidade.
    // ------------------------------------------------------------------
    hex7seg u_hex0 (
        .hex_in (slack_count[3:0]),
        .seg    (hex0)
    );

    hex7seg u_hex1 (
        .hex_in (slack_count[7:4]),
        .seg    (hex1)
    );

    hex7seg u_hex2 (
        .hex_in (slack_count[11:8]),
        .seg    (hex2)
    );

    hex7seg u_hex3 (
        .hex_in (slack_count[15:12]),
        .seg    (hex3)
    );

endmodule
