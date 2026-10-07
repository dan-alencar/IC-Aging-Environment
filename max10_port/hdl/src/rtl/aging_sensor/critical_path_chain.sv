// ============================================================================
// Modulo: critical_path_chain
// Descricao: Modela o "caminho critico" monitorado pelo sensor de
//            envelhecimento como uma cadeia de NUM_STAGES inversores em
//            serie (Secao II-D do artigo de referencia: "modeled, for
//            simplicity, as a chain of 50 inverter gates in series").
//
// Por que usar primitivas WYSIWYG (fiftyfivenm_lcell_comb) em vez de
// portas 'not' comuns:
//   Uma cadeia de inversores e logicamente redundante (todo par de dois
//   inversores equivale a um buffer). O otimizador logico do Quartus
//   normalmente reduziria essa cadeia a poucas LUTs (ou ate a removeria),
//   o que anularia o proposito dela aqui: gerar um atraso de propagacao
//   FISICO e controlavel, usado para simular o comportamento de um
//   caminho critico real.
//
//   Ao instanciar diretamente a primitiva do LUT (fiftyfivenm_lcell_comb,
//   especifica da familia MAX 10 / processo de 55nm) com o atributo
//   dont_touch="on", garantimos que cada estagio ocupe exatamente um LUT
//   fisico, prevenindo fusao/otimizacao entre estagios.
//
//   lut_mask = 16'h5555 implementa out = ~dataa, ignorando datab/datac/datad
//   (mantidos em 0). Essa mascara foi derivada bit a bit a partir da tabela
//   verdade de 4 entradas do LUT (ver conversa anterior sobre WYSIWYG).
// ============================================================================

module critical_path_chain #(
    parameter NUM_STAGES = 50
)(
    input  wire in,   // entrada do caminho critico (ligada ao registrador de "lancamento")
    output wire out   // saida do caminho critico (ligada ao critical_path do aging_sensor_core)
);

    wire [NUM_STAGES:0] stage;

    assign stage[0] = in;

    genvar i;
    generate
        for (i = 0; i < NUM_STAGES; i = i + 1) begin : gen_inv_stage
            fiftyfivenm_lcell_comb #(
                .lut_mask   (16'h5555),  // out = ~dataa (inversor puro)
                .dont_touch ("on")       // impede o Quartus de otimizar/fundir os estagios
            ) inv_stage (
                .dataa   (stage[i]),
                .datab   (1'b0),
                .datac   (1'b0),
                .datad   (1'b0),
                .combout (stage[i+1])
            );
        end
    endgenerate

    assign out = stage[NUM_STAGES];

endmodule
