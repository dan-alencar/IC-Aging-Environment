`timescale 1ns / 1ps

module modern_sensible(
    input sclk,
    input psclk, 
    input in_sensor,
    input reset,
    input clk_en,
    output reg alarm,
    output ff1_out
    );

    wire xor_out;
    wire ff1;
    wire ff2;

    assign ff1_out = ff2;

    // REPLACEMENT: Standard XOR logic (Replaces LUT2_L)
    // The "Keep" attribute prevents optimization if you want to preserve the node
    (* keep = "true" *) 
    assign xor_out = ff1 ^ ff2;
    
    // REPLACEMENT: Standard FDCE (Attributes removed for US+ compatibility)
    FDCE #(
        .INIT(1'b0)
    ) FF1 (
        .Q(ff1), 
        .C(psclk), 
        .CE(1'b1), 
        .CLR(reset), 
        .D(in_sensor) 
    );

    FDCE #(
        .INIT(1'b0) 
    ) FF2 (
        .Q(ff2), 
        .C(sclk), 
        .CE(1'b1), 
        .CLR(reset), 
        .D(in_sensor) 
    );
    
    // Converted FF3 to behavioral to avoid primitive instantiation issues
    always @(posedge clk_en or posedge reset) begin
        if (reset) begin
            alarm <= 1'b0;
        end else begin
            alarm <= xor_out;
        end
    end

endmodule