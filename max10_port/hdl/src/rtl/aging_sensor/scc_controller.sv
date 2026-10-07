// ============================================================================
// Modulo: scc_controller
// Descricao: Self-Calibration and Control Block (SCC Block), baseado na
//            maquina de estados da Fig. 4 do artigo de referencia.
//
//            Enquanto o alarme do sensor estiver em LOW, o controlador
//            emite pulsos de 'phasestep' para avancar a fase do psclk
//            (contador c1 da PLL). Cada incremento corresponde ao
//            vco_phase_shift_step reportado pelo Quartus para esta PLL
//            (aging_pll.v: 179 ps). Quando o alarme dispara de forma
//            sustentada, o controlador para e mantem a contagem --
//            multiplicando por 179 ps obtem-se o slack estimado.
//
// ============================================================================
// HISTORICO DE CORRECOES (depuracao incremental em hardware real)
// ============================================================================
//
// [A] GATING POR pll_locked  -- (revisao anterior, JA VALIDADA)
//     A FSM comecava a rodar durante a aquisicao de lock, quando
//     sys_clk/psclk/catcher_clk ainda sao invalidos. Agora o controlador
//     so sai do reset com pll_locked estavel.
//
// [B] FILTRO DE ALARME  -- (revisao anterior, JA VALIDADA)
//     O ff_alarm_q do aging_sensor_core nao e latching, e o antigo
//     S_IDLE fazia uma unica leitura de alarm_sync antes de cair em
//     S_DONE (terminal). Um unico bit espurio congelava a calibracao.
//     Agora exige-se ALARM_FILTER_CYCLES amostras consecutivas. Isso e
//     seguro porque um alarme legitimo e persistente (o registrador
//     'launch' comuta a cada ciclo, entao a divergencia se repete em
//     todo ciclo).
//     >> Confirmado em placa: alarm, alarm_sync, calibrated e dbg_done
//        permaneceram em 0. O falso alarme acabou.
//
// [C] SEQUENCIAMENTO POR TEMPO DO HANDSHAKE  -- (ESTA REVISAO)
//     Sintoma observado em placa: LEDs 0 (pll_locked), 3 (phasedone) e
//     5 (dbg_step) acesos, display em 00. Ou seja: a FSM travava em
//     S_ASSERT_STEP com phasestep alto indefinidamente, aguardando um
//     phasedone baixo que nunca era observado.
//
//     Causa provavel: a documentacao da Intel descreve que phasedone
//     DE-ASSERTA NA BORDA DE DESCIDA do scanclk. Com um passo de apenas
//     179 ps, o deslocamento se completa em pouquissimos ciclos de VCO,
//     e o pulso baixo de phasedone pode caber inteiramente ENTRE duas
//     bordas de subida do scanclk -- ficando invisivel para uma FSM que
//     so amostra em posedge. Nesse cenario a fase pode ate estar sendo
//     deslocada corretamente, mas a FSM nunca percebe e nunca avanca.
//
//     Correcao: nao depender mais de OBSERVAR phasedone. O handshake
//     passa a ser sequenciado por TEMPO, exatamente como a Intel
//     especifica:
//       1) Assertar phasestep por >= 2 ciclos de scanclk
//          (STEP_HIGH_CYCLES, com folga).
//       2) Desassertar phasestep.
//       3) Aguardar a conclusao do deslocamento (WAIT_CYCLES).
//       4) Aguardar >= 1 ciclo antes do proximo pedido (COOLDOWN_CYCLES).
//     Isso garante PROGRESSO PARA FRENTE incondicionalmente, e cobre
//     tanto o caso "pulso curto demais para ser visto" quanto qualquer
//     outra anomalia na observacao do phasedone.
//
//     Diagnostico adicional: pd_low_seen e um flag STICKY que registra
//     se phasedone alguma vez caiu, amostrado nas DUAS bordas do scanclk
//     (posedge e negedge) justamente para capturar pulsos curtos. Ele e
//     exposto em dbg_wait_low. Interpretacao na placa:
//       - LEDR6 ACENDE  -> a PLL ESTA respondendo aos pedidos de fase.
//       - LEDR6 APAGADO -> a PLL nunca reagiu; o problema esta na IP ou
//                          na selecao de contador, nao no handshake.
//
// Observacao sobre dominios de clock:
//   'alarm' e gerado no dominio de catcher_clk (saida da PLL), enquanto
//   este controlador opera no dominio de scanclk. Por isso e
//   sincronizado internamente com duplo flip-flop.
// ============================================================================

module scc_controller #(
    parameter integer COUNT_WIDTH = 16,  // largura do contador de incrementos de fase

    // Amostras CONSECUTIVAS de alarm_sync == 1 exigidas antes de
    // declarar a calibracao concluida (filtra capturas metaestaveis)
    parameter integer ALARM_FILTER_CYCLES = 16,

    // [C] Temporizacao do handshake, em ciclos de scanclk.
    // Intel exige phasestep alto por >= 2 ciclos; usamos 4 por folga.
    parameter integer STEP_HIGH_CYCLES = 4,
    // Tempo para a PLL concluir o deslocamento apos phasestep cair.
    parameter integer WAIT_CYCLES      = 32,
    // Espacamento minimo antes do proximo pedido (Intel exige >= 1).
    parameter integer COOLDOWN_CYCLES  = 8
)(
    input  wire                     scanclk,      // mesmo clock usado como scanclk da PLL (clk50)
    input  wire                     reset,        // reset assincrono, ativo em nivel alto
    input  wire                     pll_locked,   // saida 'locked' da ALTPLL
    input  wire                     alarm,        // saida do aging_sensor_core (dominio catcher_clk)
    input  wire                     phasedone,    // saida da ALTPLL (agora usado so p/ diagnostico)

    output reg                      phasestep,    // nivel alto durante S_ASSERT_STEP
    output wire                     phaseupdown,  // direcao do deslocamento (fixo: avanca)
    output reg  [COUNT_WIDTH-1:0]   slack_count,  // incrementos aplicados ate o alarme disparar
    output reg                      calibrated,   // 1 quando a calibracao terminou

    // Saidas de depuracao
    output wire                     dbg_idle,
    output wire                     dbg_step,
    output wire                     dbg_wait_low,   // [C] REDEFINIDO: pd_low_seen (phasedone ja caiu?)
    output wire                     dbg_wait_high,
    output wire                     dbg_done,
    output wire                     dbg_alarm_sync
);

    // Direcao fixa: sempre avancando a fase ("shift psclk to the left",
    // Secao II-A do artigo)
    assign phaseupdown = 1'b1;

    // ------------------------------------------------------------------
    // [A] Sincronizacao de pll_locked e reset interno
    // Resetado APENAS por 'reset' (nao por rst_i), para evitar
    // dependencia circular.
    // ------------------------------------------------------------------
    reg locked_meta, locked_sync;

    always @(posedge scanclk or posedge reset) begin
        if (reset) begin
            locked_meta <= 1'b0;
            locked_sync <= 1'b0;
        end else begin
            locked_meta <= pll_locked;
            locked_sync <= locked_meta;
        end
    end

    wire rst_i = reset | ~locked_sync;

    // ------------------------------------------------------------------
    // Sincronizador de 2 FFs para o sinal alarm (catcher_clk -> scanclk)
    // ------------------------------------------------------------------
    reg alarm_meta, alarm_sync;

    always @(posedge scanclk or posedge rst_i) begin
        if (rst_i) begin
            alarm_meta <= 1'b0;
            alarm_sync <= 1'b0;
        end else begin
            alarm_meta <= alarm;
            alarm_sync <= alarm_meta;
        end
    end

    assign dbg_alarm_sync = alarm_sync;

    // ------------------------------------------------------------------
    // [B] Filtro de alarme: conta amostras CONSECUTIVAS de alarm_sync.
    // Qualquer 0 zera o contador.
    // ------------------------------------------------------------------
    localparam integer FILT_W = 5;   // suporta ate 31 ciclos de filtro

    reg [FILT_W-1:0] alarm_cnt;

    wire alarm_stable = (alarm_cnt >= ALARM_FILTER_CYCLES[FILT_W-1:0]);

    always @(posedge scanclk or posedge rst_i) begin
        if (rst_i)
            alarm_cnt <= {FILT_W{1'b0}};
        else if (alarm_sync) begin
            if (alarm_cnt != {FILT_W{1'b1}})   // satura, nunca da wrap
                alarm_cnt <= alarm_cnt + 1'b1;
        end else
            alarm_cnt <= {FILT_W{1'b0}};
    end

    // ------------------------------------------------------------------
    // [C] Diagnostico: flag STICKY indicando se phasedone ja caiu alguma
    // vez. Amostrado nas DUAS bordas do scanclk, porque o pulso baixo
    // pode ser curto demais para aparecer so em posedge.
    // ------------------------------------------------------------------
    reg pd_low_pos;   // capturado na borda de subida
    reg pd_low_neg;   // capturado na borda de descida

    always @(posedge scanclk or posedge rst_i) begin
        if (rst_i)
            pd_low_pos <= 1'b0;
        else if (!phasedone)
            pd_low_pos <= 1'b1;
    end

    always @(negedge scanclk or posedge rst_i) begin
        if (rst_i)
            pd_low_neg <= 1'b0;
        else if (!phasedone)
            pd_low_neg <= 1'b1;
    end

    // LEDR6 aceso => a PLL ESTA respondendo aos pedidos de fase.
    assign dbg_wait_low = pd_low_pos | pd_low_neg;

    // ------------------------------------------------------------------
    // Maquina de estados (Fig. 4 do artigo), agora sequenciada por tempo
    // ------------------------------------------------------------------
    localparam [2:0]
        S_IDLE        = 3'd0,  // checa o alarme filtrado
        S_ASSERT_STEP = 3'd1,  // phasestep alto por STEP_HIGH_CYCLES
        S_WAIT_HIGH   = 3'd2,  // phasestep baixo, aguarda WAIT_CYCLES
        S_COOLDOWN    = 3'd3,  // espacamento antes do proximo pedido
        S_DONE        = 3'd4;  // calibracao concluida, aguardando reset

    localparam integer TMR_W = 7;  // comporta ate 127 ciclos

    reg [TMR_W-1:0] tmr;
    reg [2:0] state, next_state;

    assign dbg_idle      = (state == S_IDLE);
    assign dbg_step      = (state == S_ASSERT_STEP);
    assign dbg_wait_high = (state == S_WAIT_HIGH);
    assign dbg_done      = (state == S_DONE);

    always @(posedge scanclk or posedge rst_i) begin
        if (rst_i)
            state <= S_IDLE;
        else
            state <= next_state;
    end

    always @(*) begin
        next_state = state;
        case (state)
            S_IDLE: begin
                if (alarm_stable)
                    next_state = S_DONE;
                else
                    next_state = S_ASSERT_STEP;
            end

            // phasestep mantido alto por STEP_HIGH_CYCLES ciclos.
            // Nao depende mais de observar phasedone cair.
            S_ASSERT_STEP: begin
                if (tmr == {TMR_W{1'b0}})
                    next_state = S_WAIT_HIGH;
            end

            // phasestep ja baixo. Aguarda a PLL concluir o deslocamento.
            S_WAIT_HIGH: begin
                if (tmr == {TMR_W{1'b0}})
                    next_state = S_COOLDOWN;
            end

            S_COOLDOWN: begin
                if (tmr == {TMR_W{1'b0}})
                    next_state = S_IDLE;
            end

            S_DONE: begin
                next_state = S_DONE;
            end

            default: next_state = S_IDLE;
        endcase
    end

    // ------------------------------------------------------------------
    // Temporizador, saidas e contador de incrementos
    // ------------------------------------------------------------------
    always @(posedge scanclk or posedge rst_i) begin
        if (rst_i) begin
            phasestep   <= 1'b0;
            slack_count <= {COUNT_WIDTH{1'b0}};
            calibrated  <= 1'b0;
            tmr         <= {TMR_W{1'b0}};
        end else begin
            // phasestep alto durante todo o estado S_ASSERT_STEP
            phasestep <= (next_state == S_ASSERT_STEP);

            // Recarrega o temporizador a cada entrada de estado
            if (state == S_IDLE && next_state == S_ASSERT_STEP)
                tmr <= STEP_HIGH_CYCLES[TMR_W-1:0] - 1'b1;
            else if (state == S_ASSERT_STEP && next_state == S_WAIT_HIGH)
                tmr <= WAIT_CYCLES[TMR_W-1:0] - 1'b1;
            else if (state == S_WAIT_HIGH && next_state == S_COOLDOWN)
                tmr <= COOLDOWN_CYCLES[TMR_W-1:0] - 1'b1;
            else if (tmr != {TMR_W{1'b0}})
                tmr <= tmr - 1'b1;

            // Um incremento de fase foi concluido ao sair de S_WAIT_HIGH
            if (state == S_WAIT_HIGH && next_state == S_COOLDOWN)
                slack_count <= slack_count + 1'b1;

            calibrated <= (state == S_DONE);
        end
    end

endmodule
