// Parameterized inverter-chain critical path.
//
// Ported from vivado/sbcci_fpga_aging/src/rtl/aging_sensor/nand_series.v
// (module not_series) so both device projects share the same delay-chain
// architecture. Each stage is an explicit LUT1 inverter primitive, tagged
// DONT_TOUCH so Vivado cannot collapse or buffer-merge the chain -- the
// per-stage propagation delay is the whole point.
module not_series #(
    parameter int size = 50   // Number of inverter stages in the delay chain
) (
    input  logic clk,
    input  logic test_bit,
    output logic start,
    output logic critpath
);

    wire [size:0] connection;
    assign connection[0] = start;

    genvar i;
    generate
        for (i = 0; i < size; i = i + 1) begin : lut_chain
            (* DONT_TOUCH = "yes" *)
            LUT1 #(
                .INIT(2'b01) // Inverter: O = ~I0
            ) INV (
                .O(connection[i + 1]),
                .I0(connection[i])
            );
        end
    endgenerate

    always_ff @(posedge clk) begin
        start <= test_bit;
    end

    assign critpath = connection[size];

endmodule
