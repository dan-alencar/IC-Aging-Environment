// ============================================================================
// Testbench: max10_aging_top_tb
// Descricao: Testbench de INTEGRACAO para o modulo de topo max10_aging_top.
//
// O que este testbench VALIDA:
//   1) Conectividade: o registrador de lancamento (launch) alterna e sua
//      transicao se propaga corretamente ate a saida da cadeia de
//      inversores (critical_path_probe). Como NUM_STAGES=50 (par), a
//      saida deve ter o MESMO valor logico do launch (par de inversores
//      = buffer), apenas com atraso fisico (nao visivel em RTL sim).
//   2) Reset: alarm e os probes devem voltar a 0 imediatamente apos reset.
//   3) Ausencia de falso disparo em condicao nominal: como a simulacao
//      RTL nao modela o atraso fisico das primitivas WYSIWYG (delay=0
//      em nivel comportamental), o alarm deve permanecer em 0 durante
//      toda a simulacao RTL, mesmo com psclk adiantado. Isso E O
//      ESPERADO nesta etapa.
//
// O que este testbench NAO valida (fica para gate-level sim ou hardware):
//   - O disparo real do alarm por erosao de slack / envelhecimento,
//     pois isso depende do atraso fisico real das LUTs apos o
//     place & route, que nao esta presente na simulacao RTL.
// ============================================================================

`timescale 1ns/1ps

module max10_aging_top_tb;

    localparam CLK_PERIOD    = 10.0;  // 100 MHz
    localparam PSCLK_ADVANCE = 3.0;   // psclk adiantado em relacao ao sys_clk
    localparam CATCHER_DELAY = 7.0;   // catcher_clk atrasado para dar tempo as capturas

    reg sys_clk;
    reg psclk;
    reg catcher_clk;
    reg reset;

    wire alarm;
    wire launch_probe;
    wire critical_path_probe;

    // ---------------------------------------------------------------
    // DUT: modulo de topo
    // ---------------------------------------------------------------
    max10_aging_top dut (
        .sys_clk              (sys_clk),
        .psclk                (psclk),
        .catcher_clk          (catcher_clk),
        .reset                (reset),
        .alarm                (alarm),
        .launch_probe         (launch_probe),
        .critical_path_probe  (critical_path_probe)
    );

    // ---------------------------------------------------------------
    // Geracao dos clocks (mesma estrutura do testbench anterior)
    // ---------------------------------------------------------------
    initial sys_clk = 1'b0;
    always #(CLK_PERIOD/2) sys_clk = ~sys_clk;

    initial begin
        psclk = 1'b0;
        #(CLK_PERIOD - PSCLK_ADVANCE);
        forever #(CLK_PERIOD/2) psclk = ~psclk;
    end

    initial begin
        catcher_clk = 1'b0;
        #(CATCHER_DELAY);
        forever #(CLK_PERIOD/2) catcher_clk = ~catcher_clk;
    end

    // ---------------------------------------------------------------
    // Sequencia de estimulos
    // ---------------------------------------------------------------
    integer i;
    reg launch_prev;
    reg mismatch_found;

    initial begin
        $dumpfile("max10_aging_top_tb.vcd");
        $dumpvars(0, max10_aging_top_tb);

        reset = 1'b1;
        mismatch_found = 1'b0;

        repeat (3) @(posedge sys_clk);
        reset = 1'b0;
        $display("[%0t ns] Reset liberado.", $time);

        // ---------------- Teste 1: reset limpa as saidas ----------------
        #1;
        if (alarm === 1'b0 && launch_probe === 1'b0)
            $display("[%0t ns] Teste 1 OK: saidas zeradas apos reset.", $time);
        else
            $display("[%0t ns] Teste 1 FALHOU: saidas nao zeradas apos reset.", $time);

        // ---------------- Teste 2: conectividade launch -> critical_path ----------------
        // Como NUM_STAGES=50 (par), critical_path_probe deve seguir launch_probe
        // (apos o tempo de propagacao, que em RTL sim e desprezivel/zero)
        for (i = 0; i < 10; i = i + 1) begin
            @(posedge sys_clk);
            #1; // pequena margem para a logica combinacional se propagar no simulador
            if (critical_path_probe !== launch_probe) begin
                mismatch_found = 1'b1;
                $display("[%0t ns] ATENCAO: critical_path_probe (%b) != launch_probe (%b) no ciclo %0d",
                          $time, critical_path_probe, launch_probe, i);
            end
        end

        if (!mismatch_found)
            $display("[%0t ns] Teste 2 OK: cadeia de inversores propaga launch corretamente (50 estagios = buffer).", $time);
        else
            $display("[%0t ns] Teste 2 FALHOU: divergencia entre launch e saida da cadeia.", $time);

        // ---------------- Teste 3: ausencia de falso alarme em RTL sim ----------------
        if (alarm === 1'b0)
            $display("[%0t ns] Teste 3 OK: alarm permanece em 0 (esperado em RTL sim, sem atraso fisico modelado).", $time);
        else
            $display("[%0t ns] Teste 3 ATENCAO: alarm disparou em RTL sim -- investigar conexoes/logica, pois nao era esperado nesta etapa.", $time);

        #(CLK_PERIOD*5);
        $display("[%0t ns] Simulacao de integracao concluida.", $time);
        $finish;
    end

endmodule
