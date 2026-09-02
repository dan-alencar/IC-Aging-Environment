// Portable, self-contained aging-sensor channel.
//
// One self-checking ripple-carry-style adder (the aging-sensitive critical
// path, plus a built-in functional mismatch check) driving a 3-FF
// metastability sampler, structurally identical to what the single-sensor
// branches use (modern_sensible + ripple_carry_adder), but folded into one
// module with no dependency on any other file in this repo -- copy this
// file wholesale into another Vivado project (e.g. a CROC CVE2 SoC) to get
// one full aging-sensor channel with zero other setup.
//
// Multiple instances of this module, each independent, are what the
// experimental-multi-sensor top levels array up via `generate` to build an
// N-channel sensor. clk_sys/clk_phase/clk_en are shared across all
// instances (one MMCM per device); rst_n is per-instance so channels can
// be independently held in reset if ever needed.
module rca_sensor_channel #(
    parameter int WIDTH = 64   // Adder width -- the aging-sensitive carry-chain length
) (
    input  logic clk_sys,      // System clock -- drives the adder and FF2
    input  logic clk_phase,    // Phase-shiftable clock -- drives FF1
    input  logic clk_en,       // 100 deg fixed-offset clock -- drives FF3 (alarm latch)
    input  logic rst_n,

    output logic sensor_alarm,      // Filtered alarm (XOR of FF1/FF2, latched on clk_en)
    output logic sensor_ff1,        // Debug: FF1 (clk_phase domain)
    output logic sensor_ff2,        // Debug: FF2 (clk_sys domain)
    output logic sensor_raw_alarm,  // Debug: unfiltered XOR
    output logic adder_error_flag   // This channel's own functional mismatch flag (not
                                     // part of the multi-sensor packet by default -- wired
                                     // to a VIO probe only; extend the packet to log it)
);

    // -------------------------------------------------------------------
    // Self-checking ripple-carry adder: the aging-sensitive critical path.
    // Same construction as ripple_carry_adder.sv (free-running counter +
    // all-ones operand, redundant recompute compared every cycle), folded
    // in here so this module has no external dependency.
    // -------------------------------------------------------------------
    logic [WIDTH-1:0] op_a, op_b;
    logic [WIDTH-1:0] combined_sum;

    (* DONT_TOUCH = "yes" *)
    assign combined_sum = op_a + op_b;

    always_ff @(posedge clk_sys) begin
        if (!rst_n) begin
            op_a             <= '0;
            op_b             <= '0;
            adder_error_flag <= 1'b0;
        end else begin
            op_a             <= op_a + 1'b1;
            op_b             <= '1;
            adder_error_flag <= (combined_sum != (op_a + op_b));
        end
    end

    // -------------------------------------------------------------------
    // 3-FF metastability sampler -- same topology as modern_sensible.
    // Samples the registered error flag (not the raw combinational adder
    // output) on two differently-phased clocks; the XOR reveals whether
    // that register violated setup/hold relative to the phase-shifted
    // clock, which is the actual metastability measurement.
    // -------------------------------------------------------------------
    logic xor_out, ff1, ff2;

    (* dont_touch = "true" *)
    LUT2_L #(.INIT(4'b0110)) u_xor (
        .LO(xor_out), .I0(ff1), .I1(ff2)
    );

    (* dont_touch = "true" *)
    FDCE #(.INIT(1'b0)) u_ff1 (
        .Q(ff1), .C(clk_phase), .CE(1'b1), .CLR(~rst_n), .D(adder_error_flag)
    );

    (* dont_touch = "true" *)
    FDCE #(.INIT(1'b0)) u_ff2 (
        .Q(ff2), .C(clk_sys), .CE(1'b1), .CLR(~rst_n), .D(adder_error_flag)
    );

    (* dont_touch = "true" *)
    FDCE #(.INIT(1'b0)) u_ff3 (
        .Q(sensor_alarm), .C(clk_en), .CE(1'b1), .CLR(~rst_n), .D(xor_out)
    );

    assign sensor_ff1       = ff1;
    assign sensor_ff2       = ff2;
    assign sensor_raw_alarm = xor_out;

endmodule
