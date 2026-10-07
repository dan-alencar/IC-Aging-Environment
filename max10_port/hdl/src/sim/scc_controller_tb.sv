// ============================================================================
// Testbench: scc_controller_tb
// Descricao: Valida o protocolo de handshake e a maquina de estados do
//            scc_controller (Fig. 4 do artigo), usando um modelo
//            comportamental SIMPLIFICADO do handshake phasestep/phasedone
//            da ALTPLL (nao e a IP real -- serve apenas para verificar se
//            o controlador segue o protocolo corretamente: um pulso de
//            phasestep por vez, aguardando phasedone antes do proximo).
//
// Cenarios testados:
//   1) Reset: todas as saidas devem zerar.
//   2) Contagem de incrementos: com alarm=0 (LOW), o controlador deve
//      emitir pulsos de phasestep um de cada vez, respeitando o
//      handshake, e incrementar slack_count a cada ciclo completo.
//   3) Parada no disparo do alarme: quando alarm sobe para 1 (HIGH), o
//      controlador deve parar de emitir phasestep, marcar calibrated=1,
//      e manter slack_count congelado no valor final.
//   4) Reset no meio da operacao: deve reiniciar tudo, inclusive
//      slack_count e calibrated.
//
// IMPORTANTE: o tempo de "ocupado" do modelo fake de phasedone
// (BUSY_CYCLES) e arbitrario, so para exercitar o protocolo. O
// comportamento temporal real da ALTPLL so aparece na simulacao com a
// IP de verdade ou no hardware.
// ============================================================================

`timescale 1ns/1ps

module scc_controller_tb;

    localparam CLK_PERIOD  = 20.0;  // 50 MHz (mesmo clock usado como scanclk)
    localparam BUSY_CYCLES = 3;     // duracao fake do "processamento" da PLL apos phasestep

    reg  scanclk;
    reg  reset;
    reg  alarm;
    wire phasestep;
    wire phaseupdown;
    wire [15:0] slack_count;
    wire calibrated;

    reg  phasedone_r;
    reg  [7:0] busy_cnt;

    // ---------------------------------------------------------------
    // DUT
    // ---------------------------------------------------------------
    scc_controller #(
        .COUNT_WIDTH (16)
    ) dut (
        .scanclk      (scanclk),
        .reset        (reset),
        .alarm        (alarm),
        .phasedone    (phasedone_r),
        .phasestep    (phasestep),
        .phaseupdown  (phaseupdown),
        .slack_count  (slack_count),
        .calibrated   (calibrated)
    );

    // ---------------------------------------------------------------
    // Clock
    // ---------------------------------------------------------------
    initial scanclk = 1'b0;
    always #(CLK_PERIOD/2) scanclk = ~scanclk;

    // ---------------------------------------------------------------
    // Modelo comportamental FAKE do handshake phasedone da PLL:
    // fica em 1 (idle) ate ver phasestep=1, entao vai a 0 por
    // BUSY_CYCLES ciclos, e volta a 1 (concluido).
    // ---------------------------------------------------------------
    always @(posedge scanclk or posedge reset) begin
        if (reset) begin
            phasedone_r <= 1'b1;
            busy_cnt    <= 8'd0;
        end else begin
            if (phasestep && phasedone_r) begin
                phasedone_r <= 1'b0;
                busy_cnt    <= BUSY_CYCLES;
            end else if (!phasedone_r) begin
                if (busy_cnt == 0)
                    phasedone_r <= 1'b1;
                else
                    busy_cnt <= busy_cnt - 1'b1;
            end
        end
    end

    // ---------------------------------------------------------------
    // Monitoramento: garante que phasestep nunca fica alto por mais
    // de 1 ciclo, e nunca e reafirmado antes do handshake anterior
    // terminar (violacao de protocolo)
    // ---------------------------------------------------------------
    integer protocol_violation;
    reg mid_handshake;

    initial begin
        protocol_violation = 0;
        mid_handshake = 1'b0;
    end

    always @(posedge scanclk) begin
        if (!reset) begin
            // marca que estamos "no meio" de um handshake assim que
            // phasedone cai, ate ele subir de novo
            if (!phasedone_r)
                mid_handshake <= 1'b1;
            else
                mid_handshake <= 1'b0;

            if (phasestep && mid_handshake) begin
                protocol_violation = protocol_violation + 1;
                $display("[%0t ns] VIOLACAO DE PROTOCOLO: phasestep assertado durante handshake ja em andamento!", $time);
            end
        end
    end

    // ---------------------------------------------------------------
    // Sequencia de estimulos
    // ---------------------------------------------------------------
    reg [15:0] count_before_alarm;

    initial begin
        $dumpfile("scc_controller_tb.vcd");
        $dumpvars(0, scc_controller_tb);

        reset = 1'b1;
        alarm = 1'b0;
        repeat (3) @(posedge scanclk);
        reset = 1'b0;
        $display("[%0t ns] Reset liberado.", $time);

        // ---------------- Teste 1: estado inicial pos-reset ----------------
        #1;
        if (slack_count === 16'd0 && calibrated === 1'b0 && phasestep === 1'b0)
            $display("[%0t ns] Teste 1 OK: saidas zeradas apos reset.", $time);
        else
            $display("[%0t ns] Teste 1 FALHOU: saidas nao zeradas apos reset.", $time);

        // ---------------- Teste 2: contagem de incrementos com alarm=0 ----------------
        repeat (60) @(posedge scanclk);

        if (slack_count > 16'd0)
            $display("[%0t ns] Teste 2 OK: slack_count incrementou (%0d incrementos aplicados).", $time, slack_count);
        else
            $display("[%0t ns] Teste 2 FALHOU: slack_count nao incrementou com alarm=0.", $time);

        if (phaseupdown === 1'b1)
            $display("[%0t ns] Teste 2b OK: phaseupdown fixo em 1 (avancando fase), como esperado.", $time);
        else
            $display("[%0t ns] Teste 2b FALHOU: phaseupdown nao esta fixo em 1.", $time);

        // ---------------- Teste 3: alarme dispara, controlador deve parar ----------------
        @(posedge scanclk);
        alarm = 1'b1;
        $display("[%0t ns] Alarm elevado para 1 (simulando disparo do sensor).", $time);

        repeat (10) @(posedge scanclk);
        count_before_alarm = slack_count;

        if (calibrated === 1'b1)
            $display("[%0t ns] Teste 3 OK: calibrated foi para 1 apos o alarme disparar.", $time);
        else
            $display("[%0t ns] Teste 3 FALHOU: calibrated nao foi para 1 apos o alarme.", $time);

        repeat (20) @(posedge scanclk);
        if (slack_count === count_before_alarm)
            $display("[%0t ns] Teste 3b OK: slack_count permaneceu congelado em %0d apos calibrated.", $time, slack_count);
        else
            $display("[%0t ns] Teste 3b FALHOU: slack_count continuou mudando apos calibrated (valor atual: %0d).", $time, slack_count);

        if (phasestep === 1'b0)
            $display("[%0t ns] Teste 3c OK: phasestep parou de pulsar apos calibrated.", $time);
        else
            $display("[%0t ns] Teste 3c FALHOU: phasestep ainda ativo apos calibrated.", $time);

        // ---------------- Teste 4: reset no meio da operacao ----------------
        reset = 1'b1;
        @(posedge scanclk);
        #1;
        if (slack_count === 16'd0 && calibrated === 1'b0)
            $display("[%0t ns] Teste 4 OK: reset no meio da operacao zerou slack_count e calibrated.", $time);
        else
            $display("[%0t ns] Teste 4 FALHOU: reset nao zerou o estado corretamente.", $time);
        reset = 1'b0;
        alarm = 1'b0;

        // ---------------- Resultado final do monitor de protocolo ----------------
        #(CLK_PERIOD*5);
        if (protocol_violation == 0)
            $display("[%0t ns] Monitor de protocolo OK: nenhuma violacao detectada durante toda a simulacao.", $time);
        else
            $display("[%0t ns] Monitor de protocolo FALHOU: %0d violacoes detectadas.", $time, protocol_violation);

        $display("[%0t ns] Simulacao do scc_controller concluida.", $time);
        $finish;
    end

endmodule
