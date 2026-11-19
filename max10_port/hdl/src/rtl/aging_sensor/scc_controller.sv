// ============================================================================
// Modulo: scc_controller   (v3 -- laco de auto-ajuste CONTINUO, itens C2/C3)
// Descricao: Self-Calibration and Control Block (SCC Block), baseado na
//            maquina de estados da Fig. 4 do artigo de referencia.
//
//            v1/v2: varredura unica ate o alarme e FSM TERMINAL (S_DONE):
//            o sensor media uma vez e congelava ate o botao de reset.
//            Isso nao serve para o forno: o slack so e informativo se for
//            REMEDIDO continuamente.
//
//            v3 (esta versao): ciclo infinito
//
//              GAP -> SWEEP (phaseupdown=0, 1 passo por pedido, ate o alarme
//              filtrado) -> LATCH (trava resultado + flags + seq) ->
//              RETURN (phaseupdown=1, devolve EXATAMENTE a mesma contagem de
//              passos; a fase da PLL volta a origem) -> SETTLE -> GAP -> ...
//
//            Resultado travado: slack_count so muda quando uma medicao BOA
//            termina; durante a varredura o display/UART mostram o ultimo
//            valor valido (nao o contador intermediario).
//
//            Parametros fisicos (T_PS, C_PS, STEP_X1000) descrevem o plano
//            real do sensor e alimentam o DETECTOR DE SATURACAO (C3):
//            leitura k = floor((T-d)/step)+1 so e legitima se c < d (fase
//            do catcher menor que o atraso da cadeia). Se c > d a leitura
//            vira min(T-d, T-c) e SATURA em k ~ (T-c)/step. Leitura perto
//            desse patamar => flag sat_hi (nao confie no valor).
//
//            flags[5:0] = {seq, pll_lost, timeout, at_origin, sat_hi, valid}
//              valid     ultima medicao e utilizavel: sem timeout, k>0 e SEM
//                        saturacao (relatorio C3: saturada = invalida no pacote)
//              sat_hi    k >= SAT_K - SAT_MARGIN (leitura saturada/ambigua)
//              at_origin alarme ja alto com fase 0 (k=0; catcher>cadeia)
//              timeout   MAX_STEPS passos sem alarme (sensor/cadeia morta)
//              pll_lost  a PLL perdeu o lock alguma vez (so limpa no reset)
//              seq       alterna a cada medicao concluida (frescor)
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
//
// Observacao sobre dominios de clock:
//   'alarm' e gerado no dominio de catcher_clk (saida da PLL), enquanto
//   este controlador opera no dominio de scanclk. Por isso e
//   sincronizado internamente com duplo flip-flop.
//
// Perda de lock: rst_i = reset | ~locked_sync reinicia a FSM e zera
//   'valid'. A fase dinamica da PLL pode nao ser a de origem apos um
//   re-lock: a medicao recomeca, mas o flag pll_lost fica pendurado e o
//   dado deve ser tratado com desconfianca ate novo reset (a validar em
//   bancada: a Intel nao documenta o estado do contador de fase apos lock).
// ============================================================================

module scc_controller #(
    parameter integer COUNT_WIDTH = 16,  // largura do contador de incrementos de fase

    // Amostras CONSECUTIVAS de alarm_sync == 1 exigidas antes de
    // declarar a medicao concluida (filtra capturas metaestaveis)
    parameter integer ALARM_FILTER_CYCLES = 16,

    // [C] Temporizacao do handshake, em ciclos de scanclk (VALIDADA em placa).
    parameter integer STEP_HIGH_CYCLES = 4,
    parameter integer WAIT_CYCLES      = 32,
    parameter integer COOLDOWN_CYCLES  = 8,

    // Geometria do sensor (C3). T = periodo de sys_clk/psclk; C = fase do
    // catcher_clk (clk2_phase_shift); STEP_X1000 = vco_phase_shift_step em
    // ps*1000 (178571 = 1/8 do periodo do VCO de 700 MHz).
    parameter integer T_PS       = 200000,
    parameter integer C_PS       = 2500,
    parameter integer STEP_X1000 = 178571,
    parameter integer SAT_MARGIN = 2,       // passos de folga abaixo do patamar

    // Passos sem alarme antes de declarar timeout = UMA VOLTA COMPLETA do
    // psclk (T / passo), conforme o relatorio (C2). Alem disso a fase daria a
    // volta e a medida seria ambigua. Deve ser > SAT_K.
    parameter integer MAX_STEPS    = (T_PS * 1000) / STEP_X1000,

    // Intervalos (ciclos de scanclk): entre medicoes e apos o retorno de fase.
    parameter integer GAP_CYCLES    = 50000,   // 1 ms
    parameter integer SETTLE_CYCLES = 64
)(
    input  wire                     scanclk,      // mesmo clock usado como scanclk da PLL (clk50)
    input  wire                     reset,        // reset assincrono, ativo em nivel alto
    input  wire                     pll_locked,   // saida 'locked' da ALTPLL
    input  wire                     alarm,        // saida do aging_sensor_core (dominio catcher_clk)
    input  wire                     phasedone,    // saida da ALTPLL (so diagnostico)

    output reg                      phasestep,    // nivel alto durante S_ASSERT_STEP
    output reg                      phaseupdown,  // 0 = avanca (varredura), 1 = recua (retorno)
    output reg  [COUNT_WIDTH-1:0]   slack_count,  // ultimo numero medido (travado); so confie se flags.valid=1
    output reg                      calibrated,   // 1 apos a primeira medicao VALIDA
    output wire [5:0]               flags,        // ver cabecalho

    // Saidas de depuracao
    output wire                     dbg_idle,
    output wire                     dbg_step,
    output wire                     dbg_wait_low,   // pd_low_seen (phasedone ja caiu?)
    output wire                     dbg_wait_high,
    output wire                     dbg_done,       // = valid (ha resultado utilizavel)
    output wire                     dbg_alarm_sync
);

    // Patamar de saturacao: leitura obtida quando c > d (C3)
    localparam integer SAT_K = ((T_PS - C_PS) * 1000) / STEP_X1000;

    // ------------------------------------------------------------------
    // [A] Sincronizacao de pll_locked e reset interno
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
    // Sincronizador de 2 FFs para alarm (catcher_clk -> scanclk)
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
    // [B] Filtro de alarme: amostras CONSECUTIVAS de alarm_sync
    // ------------------------------------------------------------------
    localparam integer FILT_W = 5;

    reg [FILT_W-1:0] alarm_cnt;
    wire alarm_stable = (alarm_cnt >= ALARM_FILTER_CYCLES[FILT_W-1:0]);

    always @(posedge scanclk or posedge rst_i) begin
        if (rst_i)
            alarm_cnt <= {FILT_W{1'b0}};
        else if (alarm_sync) begin
            if (alarm_cnt != {FILT_W{1'b1}})
                alarm_cnt <= alarm_cnt + 1'b1;
        end else
            alarm_cnt <= {FILT_W{1'b0}};
    end

    // ------------------------------------------------------------------
    // Diagnostico: phasedone alguma vez caiu? (posedge e negedge)
    // ------------------------------------------------------------------
    reg pd_low_pos, pd_low_neg;

    always @(posedge scanclk or posedge rst_i) begin
        if (rst_i) pd_low_pos <= 1'b0;
        else if (!phasedone) pd_low_pos <= 1'b1;
    end

    always @(negedge scanclk or posedge rst_i) begin
        if (rst_i) pd_low_neg <= 1'b0;
        else if (!phasedone) pd_low_neg <= 1'b1;
    end

    assign dbg_wait_low = pd_low_pos | pd_low_neg;

    // ------------------------------------------------------------------
    // Maquina de estados
    // ------------------------------------------------------------------
    localparam [2:0]
        S_GAP         = 3'd0,  // espera entre medicoes (e apos reset/lock)
        S_IDLE        = 3'd1,  // decide: medir/parar/passo de retorno
        S_ASSERT_STEP = 3'd2,  // phasestep alto por STEP_HIGH_CYCLES
        S_WAIT_HIGH   = 3'd3,  // phasestep baixo, aguarda WAIT_CYCLES
        S_COOLDOWN    = 3'd4,  // espacamento antes do proximo pedido
        S_LATCH       = 3'd5,  // trava resultado e flags (1 ciclo)
        S_SETTLE      = 3'd6;  // espera o alarme baixar apos o retorno

    localparam integer TMR_W = 24;

    reg [TMR_W-1:0]       tmr;
    reg [2:0]             state, next_state;
    reg [COUNT_WIDTH-1:0] steps;        // deslocamento liquido de fase atual (passos)
    reg                   returning;    // 0 = varredura, 1 = retorno
    reg                   lat_timeout;  // causa da proxima trava: timeout

    wire tmr_zero = (tmr == {TMR_W{1'b0}});

    assign dbg_idle      = (state == S_IDLE);
    assign dbg_step      = (state == S_ASSERT_STEP);
    assign dbg_wait_high = (state == S_WAIT_HIGH);

    always @(posedge scanclk or posedge rst_i) begin
        if (rst_i) state <= S_GAP;
        else       state <= next_state;
    end

    always @(*) begin
        next_state = state;
        case (state)
            S_GAP:
                if (tmr_zero) next_state = S_IDLE;

            S_IDLE: begin
                if (!returning) begin
                    if (alarm_stable || steps >= MAX_STEPS[COUNT_WIDTH-1:0])
                        next_state = S_LATCH;
                    else
                        next_state = S_ASSERT_STEP;
                end else begin
                    if (steps == {COUNT_WIDTH{1'b0}})
                        next_state = S_SETTLE;
                    else
                        next_state = S_ASSERT_STEP;
                end
            end

            S_ASSERT_STEP:
                if (tmr_zero) next_state = S_WAIT_HIGH;

            S_WAIT_HIGH:
                if (tmr_zero) next_state = S_COOLDOWN;

            S_COOLDOWN:
                if (tmr_zero) next_state = S_IDLE;

            S_LATCH:
                next_state = S_IDLE;

            S_SETTLE:
                if (tmr_zero) next_state = S_GAP;

            default: next_state = S_GAP;
        endcase
    end

    // ------------------------------------------------------------------
    // Temporizador, passos, direcao (dominio rst_i)
    // ------------------------------------------------------------------
    reg valid;

    always @(posedge scanclk or posedge rst_i) begin
        if (rst_i) begin
            phasestep   <= 1'b0;
            phaseupdown <= 1'b0;
            returning   <= 1'b0;
            lat_timeout <= 1'b0;
            steps       <= {COUNT_WIDTH{1'b0}};
            tmr         <= GAP_CYCLES[TMR_W-1:0];
        end else begin
            phasestep <= (next_state == S_ASSERT_STEP);

            // Recarrega o temporizador a cada troca de estado
            if (state != next_state) begin
                case (next_state)
                    S_ASSERT_STEP: tmr <= STEP_HIGH_CYCLES[TMR_W-1:0] - 1'b1;
                    S_WAIT_HIGH:   tmr <= WAIT_CYCLES[TMR_W-1:0]      - 1'b1;
                    S_COOLDOWN:    tmr <= COOLDOWN_CYCLES[TMR_W-1:0]  - 1'b1;
                    S_SETTLE:      tmr <= SETTLE_CYCLES[TMR_W-1:0]    - 1'b1;
                    S_GAP:         tmr <= GAP_CYCLES[TMR_W-1:0]       - 1'b1;
                    default:       tmr <= {TMR_W{1'b0}};
                endcase
            end else if (!tmr_zero)
                tmr <= tmr - 1'b1;

            // Um passo de fase concluido ao sair de S_WAIT_HIGH
            if (state == S_WAIT_HIGH && next_state == S_COOLDOWN) begin
                if (returning) steps <= steps - 1'b1;
                else           steps <= steps + 1'b1;
            end

            // Causa da trava
            if (state == S_IDLE && next_state == S_LATCH)
                lat_timeout <= ~alarm_stable;

            // Apos a trava: inverte a direcao para o retorno
            if (state == S_LATCH) begin
                returning   <= 1'b1;
                phaseupdown <= 1'b1;
            end

            // Fim do retorno: volta a varredura (direcao estavel por GAP inteiro)
            if (state == S_SETTLE && next_state == S_GAP) begin
                returning   <= 1'b0;
                phaseupdown <= 1'b0;
            end
        end
    end

    // ------------------------------------------------------------------
    // Resultado travado e flags (zerados so pelo botao de reset; o dado
    // sobrevive a um re-lock, mas pll_lost sinaliza o evento)
    // ------------------------------------------------------------------
    reg sat_hi, at_origin, timeout_f, seq, had_lock, pll_lost;

    // num_ok : houve um numero medido (nem timeout, nem alarme na origem)
    // sat_now: leitura dentro de SAT_MARGIN passos do patamar de saturacao (C3)
    // good   : numero utilizavel = num_ok e nao saturado
    wire num_ok   = ~lat_timeout & (steps != {COUNT_WIDTH{1'b0}});
    wire sat_now  = (steps >= (SAT_K - SAT_MARGIN));
    wire good_meas = num_ok & ~sat_now;

    always @(posedge scanclk or posedge reset) begin
        if (reset) begin
            slack_count <= {COUNT_WIDTH{1'b0}};
            calibrated  <= 1'b0;
            sat_hi      <= 1'b0;
            at_origin   <= 1'b0;
            timeout_f   <= 1'b0;
            seq         <= 1'b0;
            had_lock    <= 1'b0;
            pll_lost    <= 1'b0;
        end else begin
            had_lock <= had_lock | locked_sync;
            if (had_lock & ~locked_sync)
                pll_lost <= 1'b1;

            if (state == S_LATCH) begin
                seq       <= ~seq;
                timeout_f <= lat_timeout;
                at_origin <= ~lat_timeout & (steps == {COUNT_WIDTH{1'b0}});
                sat_hi    <= num_ok & sat_now;
                if (num_ok)                      // numero medido fica visivel (inclusive saturado)...
                    slack_count <= steps;
                if (good_meas)                   // ...mas so e 'valido' se nao saturou
                    calibrated  <= 1'b1;
            end
        end
    end

    // 'valid' cai com a perda de lock (dado pode estar desalinhado)
    always @(posedge scanclk or posedge rst_i) begin
        if (rst_i)
            valid <= 1'b0;
        else if (state == S_LATCH)
            valid <= good_meas;
    end

    assign dbg_done = valid;
    assign flags    = {seq, pll_lost, timeout_f, at_origin, sat_hi, valid};

endmodule
