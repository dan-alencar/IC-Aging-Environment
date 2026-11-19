// MODELO COMPORTAMENTAL da aging_pll (ALTPLL) so para simulacao.
// NAO e o modelo oficial da Intel: nao modela jitter, VCO, nem o pulso real de
// phasedone. Modela o que o laco precisa:
//   c0 = clk50/10 (200 ns); c1 = c0 adiantado de p*passo (96,154 ps) (phaseupdown=0 => p+1);
//   c2 = c0 + CATCHER_PS (fixo); so aceita passos com phasecounterselect=3'b011.
// Passos so valem com phasestep em borda de subida amostrada por scanclk.
`ifndef CATCHER_PS
 `define CATCHER_PS 2500
`endif
`timescale 1ps/1ps
module aging_pll (
    input  wire       inclk0, areset,
    input  wire [2:0] phasecounterselect,
    input  wire       phaseupdown, phasestep, scanclk,
    output reg        c0, c1, c2, phasedone, locked
);
    localparam integer T_PS = 200000, STEP_X1000 = 96154;
    integer p = 0;
    integer cnt = 0, lock_cnt = 0;
    reg ps_d = 0;

    initial begin c0 = 0; c1 = 0; c2 = 0; phasedone = 1; locked = 0; end

    always @(posedge inclk0 or posedge areset) begin
        if (areset) begin c0 <= 0; cnt <= 0; lock_cnt <= 0; locked <= 0; end
        else begin
            if (cnt == 4) begin c0 <= ~c0; cnt <= 0; end else cnt <= cnt + 1;
            if (lock_cnt < 40) lock_cnt <= lock_cnt + 1; else locked <= 1;
        end
    end

    // c1 = c0 atrasado de D = T - p*step (equivale a adiantar p*step)
    always @(c0) c1 <= #(T_PS - (p * STEP_X1000) / 1000) c0;
    always @(c0) c2 <= #(`CATCHER_PS) c0;

    always @(posedge scanclk) begin
        ps_d <= phasestep;
        if (phasestep && !ps_d && phasecounterselect == 3'b011) begin
            p <= p + (phaseupdown ? -1 : 1);
            phasedone <= 1'b0;
            #10000 phasedone <= 1'b1;
        end
    end
endmodule
