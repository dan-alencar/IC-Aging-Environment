// MODELO COMPORTAMENTAL so para simulacao (NAO entra no projeto Quartus).
// Substitui a primitiva fiftyfivenm_lcell_comb por uma LUT com atraso fixo
// STAGE_DELAY_PS por estagio (nao e o atraso real de silicio).
`ifndef STAGE_DELAY_PS
 `define STAGE_DELAY_PS 348
`endif
`timescale 1ps/1ps
module fiftyfivenm_lcell_comb #(
    parameter [15:0] lut_mask   = 16'hFFFF,
    parameter        dont_touch = "off"
)(
    input  wire dataa, datab, datac, datad,
    output wire combout
);
    wire [3:0] sel = {datad, datac, datab, dataa};
    assign #(`STAGE_DELAY_PS) combout = lut_mask[sel];
endmodule
