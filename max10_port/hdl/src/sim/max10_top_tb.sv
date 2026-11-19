// ============================================================================
// max10_top_tb -- integracao do TOPO com modelos comportamentais (PLL e LUT).
// Verifica de ponta a ponta: sensor -> laco continuo -> flags -> pacote UART.
//   +EXPECT_K=<n>   leitura esperada (formula, ou 1065 se saturar)
//   +EXPECT_SAT=0|1 flag sat_hi esperada
// Atraso da cadeia d = 50 * STAGE_DELAY_PS ; catcher = CATCHER_PS (macros).
// ATENCAO: modelos simplificados -- isto NAO substitui Questa+ALTPLL oficial
// nem a validacao em placa.
// ============================================================================
`timescale 1ps/1ps
module max10_top_tb;
    reg clk50 = 0, cpu_resetn = 1;   // 1 -> 0 em t=1ps gera a borda de reset (ver initial)
    always #10000 clk50 = ~clk50;

    wire alarm, pll_locked, calibrated, uart_txd;
    wire [6:0] hex0, hex1, hex2, hex3;
    wire dbg_phasedone, dbg_idle, dbg_step, dbg_wait_low, dbg_wait_high, dbg_done, dbg_alarm_sync;

    max10_aging_top dut (.clk50(clk50), .cpu_resetn(cpu_resetn), .alarm(alarm),
        .pll_locked(pll_locked), .calibrated(calibrated), .uart_txd(uart_txd),
        .hex0(hex0), .hex1(hex1), .hex2(hex2), .hex3(hex3),
        .dbg_phasedone(dbg_phasedone), .dbg_idle(dbg_idle), .dbg_step(dbg_step),
        .dbg_wait_low(dbg_wait_low), .dbg_wait_high(dbg_wait_high),
        .dbg_done(dbg_done), .dbg_alarm_sync(dbg_alarm_sync));

    defparam dut.u_uart_sender.SEND_INTERVAL_MS = 1;   // pacotes rapidos na sim
    // O detector de saturacao do controlador precisa conhecer o catcher REAL da PLL
    // (no projeto, max10_aging_top.sv repete C_PS=2500 = clk2_phase_shift de aging_pll.v).
    defparam dut.u_scc_controller.C_PS = `CATCHER_PS;

    // ---- receptor UART 115200 8N1 (434 ciclos de 20 ns por bit) ----
    localparam integer BIT_PS = 434 * 20000;
    reg [7:0] rxb; integer i;
    reg [7:0] f [0:4]; integer fi = 0;
    integer frames = 0, bad = 0, last_slack = 0, last_status = 0;
    integer seq_changes = 0, last_seq = -1;

    always begin
        @(negedge uart_txd);
        #(BIT_PS/2);
        for (i = 0; i < 8; i = i + 1) begin #(BIT_PS); rxb[i] = uart_txd; end
        #(BIT_PS);   // stop bit
        if (fi == 0 && rxb != 8'hAA) begin /* ressincroniza */ end
        else begin
            f[fi] = rxb; fi = fi + 1;
            if (fi == 5) begin
                fi = 0;
                if ((f[1] ^ f[2] ^ f[3]) != f[4]) bad = bad + 1;
                else begin
                    frames = frames + 1;
                    last_slack = {f[1], f[2]}; last_status = f[3];
                    if (f[3][7] !== last_seq[0] && last_seq != -1) seq_changes = seq_changes + 1;
                    last_seq = f[3][7];
                end
            end
        end
    end

    integer exp_k = -1, exp_sat = 0, errors = 0;
    initial begin
        if (!$value$plusargs("EXPECT_K=%d", exp_k)) exp_k = -1;
        if (!$value$plusargs("EXPECT_SAT=%d", exp_sat)) exp_sat = 0;
        #1 cpu_resetn = 0;      // borda de reset (assincrona) -- inicializa launch/FFs
        #100000 cpu_resetn = 1;
        // ~4 medicoes completas (cada uma ~3 ms)
        #14_000_000_000;
        $display("pacotes validos=%0d  checksum_ruim=%0d  mudancas_de_seq=%0d", frames, bad, seq_changes);
        $display("ultimo pacote: slack=%0d (0x%04h) status=%b  [valid=%b sat=%b origin=%b timeout=%b lost=%b seq=%b calib=%b alarm=%b]",
                 last_slack, last_slack[15:0], last_status[7:0], last_status[2], last_status[3], last_status[4],
                 last_status[5], last_status[6], last_status[7], last_status[1], last_status[0]);
        $display("d_cadeia=%0d ps  catcher=%0d ps  esperado k=%0d sat=%0d", 50*`STAGE_DELAY_PS, `CATCHER_PS, exp_k, exp_sat);
        if (frames < 5)           begin errors = errors + 1; $display("FALHA: poucos pacotes"); end
        if (bad != 0)             begin errors = errors + 1; $display("FALHA: checksum"); end
        if (seq_changes < 2)      begin errors = errors + 1; $display("FALHA: seq nao alterna (laco nao continuo)"); end
        if (exp_k >= 0 && last_slack != exp_k) begin errors = errors + 1; $display("FALHA: k"); end
        if (last_status[3] !== exp_sat[0])      begin errors = errors + 1; $display("FALHA: flag sat_hi"); end
        if (last_status[2] !== ~exp_sat[0])     begin errors = errors + 1; $display("FALHA: valid (esperado %0d: saturada => invalida)", ~exp_sat[0]); end
        if (errors == 0) $display("PASS"); else $display("FAIL");
        $finish;
    end
endmodule
