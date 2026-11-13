// The aged logic: chains, their sensors and the ring oscillators (fbs SPEC §6.1).
//
// Chain kinds (KINDS byte per chain, SIZES 16 bits per chain):
//   INFERRED/REFERENCE  a SIZE-bit adder written as `a + b`, excited as in the colleague's
//                       fixed design: a alternates 0x55..55 / 0x55..56, b = 0xAA..AA, so the top
//                       sum bit flips only after the carry crosses all SIZE bits
//   CARRY8              SIZE/8 CARRY8 cells in a chain, every propagate input high, the carry
//                       input toggled: the toggle ripples through the whole chain
//   LUT                 SIZE LUT1 buffers in series
// Every chain toggles each clk_meas cycle while its stress input is set; a chain that does
// not toggle is not stressed (the reference chain outside measurement windows). The end of
// each chain feeds a modern_sensible-style sensor: FF1 on clk_phase, FF2 on clk_meas, their
// XOR latched by FF3 on clk_catch (the alarm). All of it is DONT_TOUCH.
// Ring oscillators: a NAND (enable) and RO_STAGES-1 inverters in a loop, each counting its
// own edges; enable and clear come from the platform clock domain and the counts are read
// only while the oscillators are stopped.
// Without FBS_XILINX a model replaces the fabric: chain i alarms once the phase has moved
// back by at least sim_slack_i[i] steps (+-1 at random), and oscillator r counts
// sim_ro_rate_i[r] / 256 edges per clock.
module aging_fabric #(
  parameter int unsigned     N         = 10,
  parameter int unsigned     R         = 2,
  parameter logic [N*8-1:0]  KINDS     = '0,
  parameter logic [N*16-1:0] SIZES     = '0,
  parameter int unsigned     RO_STAGES = 21
) (
  input  logic                clk_meas,
  input  logic                clk_phase,
  input  logic                clk_catch,
  input  logic [N-1:0]        stress_i,       // asynchronous
  output logic [N-1:0]        alarm_o,        // clk_catch domain
  input  logic                ro_en_i,        // asynchronous
  input  logic                ro_clr_i,       // asynchronous, while disabled
  output logic [R-1:0][31:0]  ro_count_o,
  // simulation model only
  input  int                  sim_phase_i,
  input  logic [N-1:0][15:0]  sim_slack_i,
  input  logic [R-1:0][15:0]  sim_ro_rate_i
);
  (* ASYNC_REG = "TRUE" *) logic [N-1:0] stress_m, stress_s;
  always_ff @(posedge clk_meas) begin
    stress_m <= stress_i;
    stress_s <= stress_m;
  end

`ifdef FBS_XILINX
  localparam logic [7:0] K_CARRY8 = 8'd0, K_LUT = 8'd1;
  for (genvar i = 0; i < N; i++) begin : g_chain
    localparam logic [7:0]  KIND = KINDS[8*i +: 8];
    localparam int unsigned SIZE = SIZES[16*i +: 16];
    logic chain_out;
    if (KIND == K_CARRY8) begin : g_c8
      localparam int unsigned NC = (SIZE + 7) / 8;
      (* DONT_TOUCH = "yes" *) logic toggle;
      (* DONT_TOUCH = "yes" *) logic [NC:0] cy;
      always_ff @(posedge clk_meas) toggle <= stress_s[i] ? !toggle : toggle;
      assign cy[0] = toggle;
      for (genvar c = 0; c < NC; c++) begin : g_cell
        logic [7:0] co;
        (* DONT_TOUCH = "yes" *)
        CARRY8 #(.CARRY_TYPE("SINGLE_CY8")) u_cy (
          .CI(cy[c]), .CI_TOP(1'b0), .DI(8'h00), .S(8'hFF), .CO(co), .O());
        assign cy[c+1] = co[7];
      end
      assign chain_out = cy[NC];
    end else if (KIND == K_LUT) begin : g_lut
      (* DONT_TOUCH = "yes" *) logic toggle;
      (* DONT_TOUCH = "yes" *) logic [SIZE:0] st;
      always_ff @(posedge clk_meas) toggle <= stress_s[i] ? !toggle : toggle;
      assign st[0] = toggle;
      for (genvar s = 0; s < SIZE; s++) begin : g_stage
        (* DONT_TOUCH = "yes" *) LUT1 #(.INIT(2'b10)) u_buf (.I0(st[s]), .O(st[s+1]));
      end
      assign chain_out = st[SIZE];
    end else begin : g_add                                   // INFERRED, REFERENCE
      localparam logic [SIZE-1:0] A0 = {(SIZE/2){2'b01}};
      localparam logic [SIZE-1:0] B0 = {(SIZE/2){2'b10}};
      (* DONT_TOUCH = "yes" *) logic toggle;
      (* DONT_TOUCH = "yes" *) logic [SIZE-1:0] op_a, op_b;
      (* DONT_TOUCH = "yes" *) logic [SIZE-1:0] sum;
      always_ff @(posedge clk_meas) begin
        if (stress_s[i]) toggle <= !toggle;
        op_a <= toggle ? A0 : A0 + 1'b1;
        op_b <= B0;
      end
      assign sum = op_a + op_b;
      assign chain_out = sum[SIZE-1];
    end

    // the sensor (modern_sensible)
    logic ff1, ff2, x;
    (* DONT_TOUCH = "true" *) FDCE #(.INIT(1'b0)) FF1 (.Q(ff1), .C(clk_phase), .CE(1'b1), .CLR(1'b0), .D(chain_out));
    (* DONT_TOUCH = "true" *) FDCE #(.INIT(1'b0)) FF2 (.Q(ff2), .C(clk_meas), .CE(1'b1), .CLR(1'b0), .D(chain_out));
    (* DONT_TOUCH = "true" *) LUT2 #(.INIT(4'b0110)) XOR1 (.O(x), .I0(ff1), .I1(ff2));
    (* DONT_TOUCH = "true" *) FDCE #(.INIT(1'b0)) FF3 (.Q(alarm_o[i]), .C(clk_catch), .CE(1'b1), .CLR(1'b0), .D(x));
  end

  for (genvar r = 0; r < R; r++) begin : g_ro
    (* DONT_TOUCH = "yes", ALLOW_COMBINATORIAL_LOOPS = "TRUE" *) logic [RO_STAGES-1:0] n;
    (* DONT_TOUCH = "yes" *) LUT2 #(.INIT(4'b0111)) u_nand (.I0(ro_en_i), .I1(n[RO_STAGES-1]), .O(n[0]));
    for (genvar s = 1; s < RO_STAGES; s++) begin : g_inv
      (* DONT_TOUCH = "yes" *) LUT1 #(.INIT(2'b01)) u_inv (.I0(n[s-1]), .O(n[s]));
    end
    // a counter clocked by the oscillator; cleared asynchronously while it is stopped
    (* DONT_TOUCH = "yes" *) logic [31:0] cnt;
    always_ff @(posedge n[RO_STAGES-1] or posedge ro_clr_i)
      if (ro_clr_i) cnt <= '0;
      else cnt <= cnt + 32'd1;
    assign ro_count_o[r] = cnt;
  end

  wire unused_sim = ^{sim_phase_i, sim_slack_i, sim_ro_rate_i};
`else
  // ---------------------------------------------------------------- simulation model
  /* verilator lint_off PROCASSINIT */
  logic [15:0] lfsr = 16'hACE1;
  /* verilator lint_on PROCASSINIT */
  always_ff @(posedge clk_catch) lfsr <= {lfsr[14:0], lfsr[15] ^ lfsr[13] ^ lfsr[12] ^ lfsr[10]};
  for (genvar i = 0; i < N; i++) begin : g_model
    int thr;
    // jitter: the threshold moves by one step now and then, like a real sensor's +-1
    assign thr = int'(sim_slack_i[i]) + ((lfsr[2*(i%8) +: 2] == 2'b00) ? 1 :
                                         (lfsr[2*(i%8) +: 2] == 2'b11) ? -1 : 0);
    always_ff @(posedge clk_catch) alarm_o[i] <= stress_s[i] && (-sim_phase_i >= thr);
  end
  logic [R-1:0][39:0] acc;
  always_ff @(posedge clk_meas) begin
    for (int r = 0; r < R; r++) begin
      if (ro_clr_i) acc[r] <= '0;
      else if (ro_en_i) acc[r] <= acc[r] + 40'(sim_ro_rate_i[r]);
    end
  end
  for (genvar r = 0; r < R; r++) begin : g_rocnt
    assign ro_count_o[r] = acc[r][39:8];
  end
  wire unused_sim = ^{clk_phase, KINDS, SIZES, 32'(RO_STAGES)};
`endif
endmodule
