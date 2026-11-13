// Per-window statistics of every chain, and the histogram of chain 0 (SPEC §6.1).
//
// A sweep result is folded in one chain per cycle (one multiplier for the squares). At the
// end of a window, snap_i copies the accumulators to the snapshot read by the message
// builder and clears them; a snap that arrives while a sweep is being folded in waits for it.
// With no sweeps in a window, last/min/max read 0.
module aging_stats #(
  parameter int unsigned N    = 10,
  parameter int unsigned BINS = 16
) (
  input  logic                   clk,
  input  logic                   rst_ni,
  input  logic                   add_i,         // one sweep's results (from aging_sweep)
  input  logic [N-1:0][15:0]     count_i,
  input  logic [N-1:0]           measured_i,
  input  logic [N-1:0]           noalarm_i,
  input  logic                   snap_i,
  input  logic [15:0]            hist_base_i,
  input  logic [7:0]             hist_width_i,  // >= 1
  output logic                   busy_o,
  output logic                   snapped_o,     // one cycle after the snapshot was taken
  output logic [N-1:0][15:0]     s_sweeps_o,
  output logic [N-1:0][15:0]     s_last_o,
  output logic [N-1:0][15:0]     s_min_o,
  output logic [N-1:0][15:0]     s_max_o,
  output logic [N-1:0][31:0]     s_sum_o,
  output logic [N-1:0][63:0]     s_sumsq_o,
  output logic [BINS-1:0][15:0]  s_hist_o,
  output logic                   s_noalarm0_o   // a sweep of chain 0 found no alarm
);
  localparam int unsigned IW = $clog2(N + 1);

  logic [N-1:0][15:0] sweeps, last, mn, mx;
  logic [N-1:0][31:0] sum;
  logic [N-1:0][63:0] sumsq;
  logic [BINS-1:0][15:0] hist;
  logic               noalarm0;

  logic [N-1:0][15:0] cnt_q;
  logic [N-1:0]       meas_q;
  logic               na0_q;
  logic [IW-1:0]      idx;
  logic               folding, snap_pend;

  // histogram bin edges: e_k = base + k * width, k = 1..BINS-1
  logic [BINS-1:1][16:0] edge_q;
  always_ff @(posedge clk)
    for (int k = 1; k < BINS; k++) edge_q[k] <= 17'(hist_base_i) + 17'(k) * 17'(hist_width_i);

  function automatic logic [$clog2(BINS)-1:0] bin_of(input logic [15:0] c);
    logic [$clog2(BINS):0] b;
    b = '0;
    for (int k = 1; k < BINS; k++) if (17'(c) >= edge_q[k]) b = b + 1'b1;
    return b[$clog2(BINS)-1:0];
  endfunction

  assign busy_o = folding;

  logic [15:0] c;
  logic [31:0] sq;
  assign c  = cnt_q[idx];
  assign sq = 32'(c) * 32'(c);

  always_ff @(posedge clk) begin
    snapped_o <= 1'b0;
    if (!rst_ni) begin
      folding   <= 1'b0;
      snap_pend <= 1'b0;
      idx       <= '0;
      cnt_q     <= '0;
      meas_q    <= '0;
      na0_q     <= 1'b0;
      sweeps    <= '0;
      last      <= '0;
      mn        <= '1;
      mx        <= '0;
      sum       <= '0;
      sumsq     <= '0;
      hist      <= '0;
      noalarm0  <= 1'b0;
      s_sweeps_o <= '0;
      s_last_o   <= '0;
      s_min_o    <= '0;
      s_max_o    <= '0;
      s_sum_o    <= '0;
      s_sumsq_o  <= '0;
      s_hist_o   <= '0;
      s_noalarm0_o <= 1'b0;
    end else begin
      if (snap_i) snap_pend <= 1'b1;
      if (folding) begin
        if (meas_q[idx]) begin
          if (sweeps[idx] != 16'hFFFF) begin
            sweeps[idx] <= sweeps[idx] + 16'd1;
            sum[idx]    <= sum[idx] + 32'(c);
            sumsq[idx]  <= sumsq[idx] + 64'(sq);
          end
          last[idx] <= c;
          if (c < mn[idx]) mn[idx] <= c;
          if (c > mx[idx]) mx[idx] <= c;
          if (idx == '0) begin
            if (hist[bin_of(c)] != 16'hFFFF) hist[bin_of(c)] <= hist[bin_of(c)] + 16'd1;
            if (na0_q) noalarm0 <= 1'b1;
          end
        end
        if (idx == IW'(N - 1)) folding <= 1'b0;
        idx <= idx + 1'b1;
      end else if (add_i) begin
        cnt_q   <= count_i;
        meas_q  <= measured_i;
        na0_q   <= noalarm_i[0];
        idx     <= '0;
        folding <= 1'b1;
      end else if (snap_pend || snap_i) begin
        snap_pend <= 1'b0;
        snapped_o <= 1'b1;
        for (int i = 0; i < N; i++) begin
          s_sweeps_o[i] <= sweeps[i];
          s_last_o[i]   <= sweeps[i] != '0 ? last[i] : '0;
          s_min_o[i]    <= sweeps[i] != '0 ? mn[i] : '0;
          s_max_o[i]    <= sweeps[i] != '0 ? mx[i] : '0;
          s_sum_o[i]    <= sum[i];
          s_sumsq_o[i]  <= sumsq[i];
        end
        s_hist_o     <= hist;
        s_noalarm0_o <= noalarm0;
        sweeps   <= '0;
        last     <= '0;
        mn       <= '1;
        mx       <= '0;
        sum      <= '0;
        sumsq    <= '0;
        hist     <= '0;
        noalarm0 <= 1'b0;
      end
    end
  end
  if (N > 1) begin : g_unused
    wire unused = ^noalarm_i[N-1:1];
  end
endmodule
