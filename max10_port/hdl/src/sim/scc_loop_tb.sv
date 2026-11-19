// ============================================================================
// scc_loop_tb -- teste de LACO FECHADO do scc_controller v3 (C2/C3)
//
// Modelo comportamental (NAO e o modelo oficial da Intel nem timing real):
//   - PLL: cada borda de subida de phasestep soma +1 (phaseupdown=0) ou -1
//     (phaseupdown=1) ao deslocamento p, em passos de STEP_X1000/1000 ps.
//   - Sensor: alarme = (p*step > T - max(d, C)), ou seja leitura
//     k = floor((T-d)/step)+1 se C < d, e satura em T-C se C > d.
// Verifica: medicoes sucessivas, rastreio de d, retorno de fase a origem,
// saturacao (C3), at_origin, timeout, perda de lock.
// Rodar: scripts/run_sim.sh
// ============================================================================
`timescale 1ns/1ps
module scc_loop_tb;
    parameter  integer C_PS = 2500;      // 10000 reproduz o RTL ANTIGO (catcher 10 ns)
    parameter  integer TABLE7_ONLY = 0;  // 1: so a Tabela 7 do relatorio
    localparam integer T_PS = 200000, STEP_X1000 = 96154;
    localparam integer MAX_STEPS = (T_PS * 1000 + STEP_X1000 / 2) / STEP_X1000;   // 1 volta = 2080 passos

    reg scanclk = 0;  always #10 scanclk = ~scanclk;   // 50 MHz
    reg reset = 1, pll_locked = 0;

    integer d_ps = 17400;           // atraso da cadeia (ps)
    reg alarm_dead = 0, alarm_force = 0;
    integer p = 0;                  // deslocamento liquido de fase da PLL
    reg p_reset_on_relock = 1;

    wire phasestep, phaseupdown, calibrated, dbg_idle, dbg_step, dbg_wait_low,
         dbg_wait_high, dbg_done, dbg_alarm_sync;
    wire [15:0] slack_count;
    wire [5:0]  flags;

    // sensor: alarme assincrono ao scanclk (vem do dominio catcher_clk)
    integer maxdc;
    reg alarm_r;
    always @* begin
        maxdc = (d_ps > C_PS) ? d_ps : C_PS;
        alarm_r = (p * STEP_X1000 > (T_PS - maxdc) * 1000);
        if (alarm_dead)  alarm_r = 1'b0;
        if (alarm_force) alarm_r = 1'b1;
    end

    scc_controller #(.T_PS(T_PS), .C_PS(C_PS), .STEP_X1000(STEP_X1000),
                     .GAP_CYCLES(300), .SETTLE_CYCLES(64))   // MAX_STEPS: default derivado de T/passo
    dut (.scanclk(scanclk), .reset(reset), .pll_locked(pll_locked),
         .alarm(alarm_r), .phasedone(1'b1),
         .phasestep(phasestep), .phaseupdown(phaseupdown),
         .slack_count(slack_count), .calibrated(calibrated), .flags(flags),
         .dbg_idle(dbg_idle), .dbg_step(dbg_step), .dbg_wait_low(dbg_wait_low),
         .dbg_wait_high(dbg_wait_high), .dbg_done(dbg_done),
         .dbg_alarm_sync(dbg_alarm_sync));

    // PLL: um passo por borda de subida de phasestep; checa protocolo
    integer rise_cycle = -1000, cyc = 0, hi_len = 0, proto_err = 0;
    reg ps_d = 0;
    always @(posedge scanclk) begin
        cyc <= cyc + 1;
        ps_d <= phasestep;
        if (phasestep && !ps_d) begin
            if (cyc - rise_cycle < 8) begin proto_err = proto_err + 1;
                $display("ERRO protocolo: pedidos espacados por %0d ciclos", cyc-rise_cycle); end
            rise_cycle <= cyc;
            p <= p + (phaseupdown ? -1 : 1);
            hi_len <= 1;
        end else if (phasestep) hi_len <= hi_len + 1;
        if (!phasestep && ps_d && hi_len < 2) begin proto_err = proto_err + 1;
            $display("ERRO protocolo: phasestep alto so %0d ciclos", hi_len); end
    end

    // lock perdido => a PLL reinicia a fase (hipotese do modelo, ver cabecalho)
    always @(negedge pll_locked) if (p_reset_on_relock) p <= 0;

    // ---------------- verificacao ----------------
    integer errors = 0, checks = 0;
    task check(input cond, input [8*48-1:0] msg);
        begin checks = checks + 1;
            if (!cond) begin errors = errors + 1; $display("FALHA: %0s", msg); end end
    endtask

    function integer expected_k(input integer d);
        integer m;
        begin m = (d > C_PS) ? d : C_PS;
              expected_k = ((T_PS - m) * 1000) / STEP_X1000 + 1; end
    endfunction

    reg seq_prev;
    // espera a proxima medicao concluida (seq alterna) e a fase voltar a 0
    task wait_meas;
        integer guard;
        begin
            guard = 0;
            while (flags[5] == seq_prev && guard < 400000) begin
                repeat (50) @(posedge scanclk); guard = guard + 50; end
            if (guard >= 400000) begin errors = errors + 1; $display("FALHA: sem nova medicao (timeout TB)"); end
            seq_prev = flags[5];
            // aguarda o retorno de fase terminar (FSM volta a S_GAP/varre)
            guard = 0;
            while (p != 0 && guard < 300000) begin
                repeat (50) @(posedge scanclk); guard = guard + 50; end
            check(p == 0, "fase retornou a origem (p==0)");
        end
    endtask

    integer k, n20;
    initial begin
        repeat (10) @(posedge scanclk);
        reset = 0; repeat (5) @(posedge scanclk); pll_locked = 1;
        seq_prev = flags[5];

        if (!TABLE7_ONLY) begin
        // 1) medicoes sucessivas, valores estaveis
        k = expected_k(d_ps);
        check(dut.MAX_STEPS == 2080, "MAX_STEPS default = T/passo = 2080 (uma volta)");
        wait_meas;
        check(slack_count == k && flags[0] && calibrated, "T1 medida1 = formula, valid, calibrated");
        $display("T1: d=%0d ps -> k=%0d (esperado %0d) flags=%b", d_ps, slack_count, k, flags);
        // relatorio C2 (a): 20 varreduras consecutivas devolvem a mesma contagem
        for (n20 = 2; n20 <= 20; n20 = n20 + 1) begin
            wait_meas;
            if (slack_count != k || !flags[0]) begin errors = errors + 1;
                $display("FALHA: T1 varredura %0d deu %0d (esperado %0d)", n20, slack_count, k); end
        end
        check(flags[4:1] == 4'b0000, "T1 sem flags de erro apos 20 varreduras");
        $display("T1: 20 varreduras consecutivas, todas k=%0d", k);

        // relatorio C2 (b): degrau de +500 ps em d -> contagem cai de 5 ou 6 passos (500/96,154 = 5,2)
        begin : step500
            integer k0; k0 = k;
            d_ps = d_ps + 500; k = expected_k(d_ps);
            wait_meas; wait_meas;
            check(slack_count == k && (k0 - slack_count == 5 || k0 - slack_count == 6),
                  "T1b degrau +500 ps: contagem cai de 5 ou 6 passos");
            $display("T1b: d +500 ps -> k de %0d para %0d (queda %0d; 500/passo = 5,2)", k0, slack_count, k0 - slack_count);
            d_ps = d_ps - 500; k = expected_k(d_ps);
            wait_meas; wait_meas;
            check(slack_count == k, "T1b volta ao valor original");
        end

        // 2) rastreio: atraso da cadeia aumenta (envelhecimento) -> k cai (C2)
        d_ps = 19000; k = expected_k(d_ps);
        wait_meas; wait_meas;
        check(slack_count == k, "T2 acompanha d (19000 ps)");
        $display("T2: d=%0d ps -> k=%0d (esperado %0d)", d_ps, slack_count, k);
        d_ps = 17400; k = expected_k(d_ps);   // volta (resfriamento)
        wait_meas; wait_meas;
        check(slack_count == k, "T2 volta a d=17400 (sem histerese)");

        // 3) d proximo mas acima de C: nao e saturacao
        d_ps = 5000; k = expected_k(d_ps);
        wait_meas; wait_meas;
        check(slack_count == k && flags[0] && !flags[1], "T3 d=5 ns > C=2.5 ns: valido, sem sat_hi");
        $display("T3: d=%0d ps -> k=%0d flags=%b", d_ps, slack_count, flags);

        // 3b) corner lento + 10% de envelhecimento (relatorio C3, verificacao): 29,2 ns x 1,1
        d_ps = 32120; k = expected_k(d_ps);
        wait_meas; wait_meas;
        check(slack_count == k && flags[0] && !flags[1], "T3b d=32,12 ns (lento +10%): formula, valido");
        $display("T3b: d=%0d ps -> k=%0d (esperado %0d)", d_ps, slack_count, k);

        // 4) C3: cadeia mais rapida que o catcher -> satura, flag sat_hi
        d_ps = 1000; k = expected_k(d_ps);    // = leitura saturada (T-C)
        wait_meas; wait_meas;
        check(slack_count == k && flags[1] && !flags[0], "T4 d<C: saturada => sat_hi=1 e valid=0 (relatorio C3)");
        $display("T4: d=%0d ps (< C=%0d) -> k=%0d flags=%b  SAT_K=%0d", d_ps, C_PS, slack_count, flags, dut.SAT_K);

        // 5) at_origin: alarme ja alto em fase 0
        d_ps = 17400; alarm_force = 1;
        wait_meas;
        check(flags[2] && !flags[0], "T5 at_origin=1 e valid=0");
        $display("T5: flags=%b", flags);
        alarm_force = 0;
        wait_meas; wait_meas;
        check(flags[0] && !flags[2] && slack_count == expected_k(d_ps), "T5 recupera sozinho apos o alarme normalizar");

        // 6) timeout: alarme nunca sobe -> MAX_STEPS, retorno completo, dado antigo preservado
        alarm_dead = 1;
        wait_meas;
        check(flags[3] && !flags[0], "T6 timeout=1 e valid=0");
        check(slack_count == expected_k(d_ps), "T6 mantem o ultimo valor valido");
        $display("T6: flags=%b slack_count(preservado)=%0d", flags, slack_count);
        alarm_dead = 0;
        wait_meas; wait_meas;
        check(flags[0] && !flags[3], "T6 recupera apos o sensor voltar");

        // 7) perda de lock no meio da varredura
        repeat (20000) @(posedge scanclk);          // varredura em andamento
        pll_locked = 0; repeat (200) @(posedge scanclk);
        check(!flags[0], "T7 valid cai ao perder lock");
        pll_locked = 1;
        repeat (300) @(posedge scanclk);
        check(flags[4], "T7 pll_lost marcado");
        wait_meas; wait_meas;
        check(flags[0] && flags[4] && slack_count == expected_k(d_ps), "T7 mede de novo; pll_lost permanece");
        $display("T7: flags=%b k=%0d", flags, slack_count);

        end // !TABLE7_ONLY

        // 8) Tabela 7 do relatorio (L2): d = 29,2 / 20 / 12 / 10,5 / 9 / 6 ns
        begin : table7
            integer i; integer dv [0:5]; integer prev [0:5]; integer obt [0:5];
            dv[0]=29200; dv[1]=20000; dv[2]=12000; dv[3]=10500; dv[4]=9000; dv[5]=6000;
            // Valores RECALCULADOS para o passo de 96,154 ps (C4): k = (T - max(d,C))/passo + 1.
            // (No passo antigo de 178,57 ps eram 957, 1009, 1053, 1062, 1070, 1087.)
            // Com C=10 ns as duas ultimas linhas (d < C) saturam em (T-C)/passo + 1.
            for (i = 0; i < 6; i = i + 1) begin prev[i] = expected_k(dv[i]); obt[i] = expected_k(dv[i]); end
            $display("\nTabela 7 (C=%0d ps): d[ns] previsto obtido flags(seq,lost,to,orig,sat,valid)", C_PS);
            for (i = 0; i < 6; i = i + 1) begin
                d_ps = dv[i];
                wait_meas; wait_meas;
                $display("  %5.1f   %5d   %5d   %b", d_ps/1000.0, prev[i], slack_count, flags);
                if (C_PS == 2500) begin
                    check(slack_count == prev[i], "T8 (C=2,5 ns) obtido == previsto");
                    check(!flags[1] && flags[0], "T8 (C=2,5 ns) nao saturado e valido");
                end else begin
                    check(slack_count == obt[i], "T8 (C=10 ns) obtido == formula (satura em (T-C)/passo+1)");
                end
            end
            if (C_PS != 2500) begin
                // com C=10 ns o RTL antigo devolvia o patamar SILENCIOSAMENTE; o detector
                // novo precisa ao menos marcar saturacao nessas duas linhas
                check(flags[1] && !flags[0], "T8 (C=10 ns) d=6 ns: sat_hi=1 e valid=0");
            end
        end

        check(proto_err == 0, "protocolo phasestep (>=2 ciclos alto, >=8 entre pedidos)");
        $display("\nChecks: %0d  Erros: %0d", checks, errors);
        if (errors == 0) $display("PASS"); else $display("FAIL");
        $finish;
    end

    initial begin #400_000_000_000; $display("FAIL: watchdog global"); $finish; end
endmodule
