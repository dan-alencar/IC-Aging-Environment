`timescale 1ns / 1ps

// Binary-to-BCD converter using the double-dabble (shift-and-add-3) algorithm.
// Converts a 21-bit binary input to eight 4-bit BCD digits (max representable
// value 2,097,151 — fits in seven digits; quint is always 0 for valid inputs).
// The combinational double-dabble result is registered on posedge clk to
// prevent glitches from propagating to the 7-segment display.
module BinToBCD (
    input  logic        clk,
    input  logic [20:0] bin,
    output logic [3:0]  quint,   // 10^7 digit
    output logic [3:0]  quadr,   // 10^6 digit
    output logic [3:0]  tril,    // 10^5 digit
    output logic [3:0]  bil,     // 10^4 digit
    output logic [3:0]  mil,     // 10^3 digit
    output logic [3:0]  cent,    // 10^2 digit
    output logic [3:0]  dec,     // 10^1 digit
    output logic [3:0]  un       // 10^0 digit
);
    // Combinational double-dabble signals
    logic [3:0] quint_c, quadr_c, tril_c, bil_c, mil_c, cent_c, dec_c, un_c;

    always_comb begin
        quint_c = '0; quadr_c = '0; tril_c = '0; bil_c = '0;
        mil_c   = '0; cent_c  = '0; dec_c  = '0; un_c  = '0;

        for (int i = 20; i >= 0; i--) begin
            // Add-3 step: if any digit >= 5, add 3 before shifting
            if (quint_c >= 4'd5) quint_c = quint_c + 4'd3;
            if (quadr_c >= 4'd5) quadr_c = quadr_c + 4'd3;
            if (tril_c  >= 4'd5) tril_c  = tril_c  + 4'd3;
            if (bil_c   >= 4'd5) bil_c   = bil_c   + 4'd3;
            if (mil_c   >= 4'd5) mil_c   = mil_c   + 4'd3;
            if (cent_c  >= 4'd5) cent_c  = cent_c  + 4'd3;
            if (dec_c   >= 4'd5) dec_c   = dec_c   + 4'd3;
            if (un_c    >= 4'd5) un_c    = un_c    + 4'd3;

            // Shift chain: MSB of each lower digit feeds LSB of next upper digit
            quint_c = {quint_c[2:0], quadr_c[3]};
            quadr_c = {quadr_c[2:0], tril_c[3]};
            tril_c  = {tril_c[2:0],  bil_c[3]};
            bil_c   = {bil_c[2:0],   mil_c[3]};
            mil_c   = {mil_c[2:0],   cent_c[3]};
            cent_c  = {cent_c[2:0],  dec_c[3]};
            dec_c   = {dec_c[2:0],   un_c[3]};
            un_c    = {un_c[2:0],    bin[i]};
        end
    end

    // Register outputs to prevent display glitches
    always_ff @(posedge clk) begin
        quint <= quint_c;
        quadr <= quadr_c;
        tril  <= tril_c;
        bil   <= bil_c;
        mil   <= mil_c;
        cent  <= cent_c;
        dec   <= dec_c;
        un    <= un_c;
    end

endmodule
