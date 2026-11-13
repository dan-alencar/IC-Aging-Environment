// IC-Aging payload on the fbs application interface (fpgaging-board-support SPEC §5.6, §6.1).
//
// Windows: every window_ms the statistics are snapshotted and sent as AGING_WINDOW (chain 0),
// one AGING_CHAIN per measured chain, and AGING_RO in measurement windows. AGING_INFO goes
// out after reset, every 60 s and on AGING_GET_INFO.
// Reference chain (index REF): not toggled (no stress) except during measurement windows:
// ref_windows windows every ref_period_s seconds. The ring oscillators run only then too.
// Commands (DST = FPGA_APP): PING, GET_INFO, AGING_SET_MODE, AGING_SET_HIST,
// AGING_GET_INFO; anything else gets ACK UNKNOWN_TYPE. Replies go first.
// Everything here runs on the platform clock; alarms and ring-oscillator counts come from
// other domains (synchronised here, or read only while the oscillators are stopped).
module aging_core
  import fbs_pkg::*;
  import fbs_aging_pkg::*;
#(
  parameter int unsigned  N            = 10,
  parameter int unsigned  REF          = N - 1,
  parameter int unsigned  R            = 2,
  parameter logic [N*8-1:0]  KINDS     = '0,     // ChainKind per chain, chain 0 in the low byte
  parameter logic [N*16-1:0] SIZES     = '0,
  parameter int unsigned  PS_STEP_FS   = 19841,
  parameter int unsigned  MAX_STEPS    = 504,    // one 10 ns period at 56 steps per VCO period, 9 periods
  parameter int unsigned  SETTLE       = 4,
  parameter int unsigned  SAMPLE       = 4,
  parameter int unsigned  INFO_PERIOD_MS = 60_000,
  parameter int unsigned  WINDOW_MS    = 1000,
  parameter int unsigned  REF_PERIOD_S = 60,
  parameter int unsigned  REF_WINDOWS  = 3,
  parameter int unsigned  REF_UNIT_MS  = 1000,   // ms per "second" of ref_period_s (simulation shortens it)
  parameter logic [31:0]  GIT_HASH     = 32'h0,
  parameter logic [31:0]  BUILD_ID     = 32'h0,
  parameter logic [127:0] NAME         = "ic-aging-app"
) (
  input  logic              clk,
  input  logic              rst_ni,
  input  logic [31:0]       t_ms_i,
  input  logic              tick_1ms_i,
  // MMCM fine phase shift (PSCLK = clk)
  input  logic              locked_i,
  output logic              psen_o,
  output logic              psincdec_o,
  input  logic              psdone_i,
  // fabric
  input  logic [N-1:0]      alarm_i,          // asynchronous (catcher clock domain)
  output logic [N-1:0]      stress_o,         // toggle enable per chain (synchronised in the fabric)
  output logic              ro_en_o,
  output logic              ro_clr_o,
  input  logic [R-1:0][31:0] ro_count_i,      // read only while the oscillators are stopped
  // platform -> app
  input  logic              rx_valid_i,
  output logic              rx_ready_o,
  input  logic [7:0]        rx_data_i,
  input  logic              rx_last_i,
  input  logic              rx_empty_i,
  input  logic [7:0]        rx_type_i,
  input  logic [3:0]        rx_src_i,
  input  logic [7:0]        rx_seq_i,
  input  logic [1:0]        rx_flags_i,
  input  logic [7:0]        rx_len_i,
  // app -> platform
  output logic              tx_valid_o,
  input  logic              tx_ready_i,
  output logic [7:0]        tx_data_o,
  output logic              tx_last_o,
  output logic [7:0]        tx_type_o,
  output logic [3:0]        tx_dst_o,
  output logic [1:0]        tx_flags_o,
  output logic [7:0]        tx_len_o
);
  localparam int unsigned PL = 64;               // largest payload sent here (AGING_WINDOW)
  localparam int unsigned CW = $clog2(N + 1);

  // ------------------------------------------------------------------ synchronisers
  (* ASYNC_REG = "TRUE" *) logic [N-1:0] alarm_m, alarm_s;
  (* ASYNC_REG = "TRUE" *) logic [1:0]   lock_m;
  logic locked, locked_d;
  always_ff @(posedge clk) begin
    alarm_m  <= alarm_i;
    alarm_s  <= alarm_m;
    lock_m   <= {lock_m[0], locked_i};
    locked_d <= locked;
  end
  assign locked = lock_m[1];

  // ------------------------------------------------------------------ configuration
  logic [1:0]  sweep_mode;
  logic [15:0] window_ms;
  logic        periodic;
  logic [15:0] ref_period_s;
  logic [7:0]  ref_windows;
  logic [15:0] hist_base;
  logic [7:0]  hist_width;

  // ------------------------------------------------------------------ windows
  logic [15:0] win_ms;
  logic [31:0] ref_ms;
  logic [7:0]  meas_left;
  logic        measure;                  // this window is a measurement window
  logic        win_end, partial, cut;
  logic [31:0] window_id;
  logic [15:0] lock_loss;
  logic        any_timeout;
  logic        snap_measure, snap_partial, snap_timeout;
  logic [15:0] snap_lock_loss;
  logic [31:0] snap_id, snap_t;

  // ------------------------------------------------------------------ sweep + stats
  logic             sw_start, sw_busy, sw_done, sw_timeout;
  logic [N-1:0][15:0] sw_count;
  logic [N-1:0]     sw_meas, sw_noalarm, active;
  logic             st_busy, st_snapped;
  logic [N-1:0][15:0] s_sweeps, s_last, s_min, s_max;
  logic [N-1:0][31:0] s_sum;
  logic [N-1:0][63:0] s_sumsq;
  logic [15:0][15:0]  s_hist;
  logic             s_noalarm0;
  logic             single_done;

  always_comb begin
    active = '1;
    if (!measure) active[REF] = 1'b0;
  end

  aging_sweep #(.N(N), .SETTLE(SETTLE), .SAMPLE(SAMPLE)) u_sweep (
    .clk, .rst_ni(rst_ni && locked), .start_i(sw_start), .active_i(active), .max_steps_i(16'(MAX_STEPS)),
    .alarm_i(alarm_s), .psen_o, .psincdec_o, .psdone_i, .busy_o(sw_busy), .done_o(sw_done),
    .count_o(sw_count), .measured_o(sw_meas), .noalarm_o(sw_noalarm), .timeout_o(sw_timeout));

  aging_stats #(.N(N), .BINS(16)) u_stats (
    .clk, .rst_ni, .add_i(sw_done), .count_i(sw_count), .measured_i(sw_meas), .noalarm_i(sw_noalarm),
    .snap_i(win_end), .hist_base_i(hist_base), .hist_width_i(hist_width), .busy_o(st_busy),
    .snapped_o(st_snapped), .s_sweeps_o(s_sweeps), .s_last_o(s_last), .s_min_o(s_min), .s_max_o(s_max),
    .s_sum_o(s_sum), .s_sumsq_o(s_sumsq), .s_hist_o(s_hist), .s_noalarm0_o(s_noalarm0));

  assign sw_start = locked && !sw_busy && !st_busy && !sw_done &&
                    (sweep_mode == 2'(FBS_AGING_SWEEP_MODE_CONTINUOUS) ||
                     (sweep_mode == 2'(FBS_AGING_SWEEP_MODE_SINGLE) && !single_done));

  // stress: every chain toggles except the reference outside measurement windows
  always_comb begin
    stress_o = '1;
    stress_o[REF] = measure;
  end

  // ring oscillators: on during a measurement window; read after they stop
  logic [4:0]  ro_wait;
  logic        ro_valid;
  logic [R-1:0][31:0] ro_q;
  logic [15:0] ro_window_ms;

  always_ff @(posedge clk) begin
    win_end <= 1'b0;
    if (!rst_ni) begin
      win_ms       <= '0;
      ref_ms       <= '0;
      meas_left    <= '0;
      measure      <= 1'b0;
      window_id    <= '0;
      lock_loss    <= '0;
      any_timeout  <= 1'b0;
      partial      <= 1'b0;
      single_done  <= 1'b0;
      snap_measure <= 1'b0;
      snap_partial <= 1'b0;
      snap_timeout <= 1'b0;
      snap_lock_loss <= '0;
      snap_id      <= '0;
      snap_t       <= '0;
      ro_en_o      <= 1'b0;
      ro_clr_o     <= 1'b1;
      ro_wait      <= '0;
      ro_valid     <= 1'b0;
      ro_q         <= '0;
      ro_window_ms <= '0;
    end else begin
      if (sw_timeout) any_timeout <= 1'b1;
      if (locked_d && !locked && lock_loss != 16'hFFFF) lock_loss <= lock_loss + 16'd1;
      if (sw_start && sweep_mode == 2'(FBS_AGING_SWEEP_MODE_SINGLE)) single_done <= 1'b1;
      if (tick_1ms_i) begin
        win_ms <= win_ms + 16'd1;
        ref_ms <= ref_ms + 32'd1;
      end
      if ((tick_1ms_i && win_ms + 16'd1 >= window_ms) || cut) begin
        // end of a window: freeze its description, start the next one
        win_end        <= 1'b1;
        win_ms         <= '0;
        snap_id        <= window_id;
        snap_t         <= t_ms_i;
        snap_measure   <= measure;
        snap_partial   <= partial || cut;
        snap_timeout   <= any_timeout || sw_timeout;
        snap_lock_loss <= lock_loss;
        window_id      <= window_id + 32'd1;
        lock_loss      <= '0;
        any_timeout    <= 1'b0;
        partial        <= 1'b0;
        single_done    <= 1'b0;
        if (measure) begin
          ro_en_o      <= 1'b0;          // stop the oscillators, read them in a moment
          ro_wait      <= 5'd16;
          ro_window_ms <= win_ms + 16'd1;
        end
        if (meas_left != '0) begin
          meas_left <= meas_left - 8'd1;
          measure   <= 1'b1;
          ro_clr_o  <= 1'b0;
          ro_en_o   <= 1'b1;
        end else if (ref_period_s != '0 && ref_ms >= 32'(ref_period_s) * 32'(REF_UNIT_MS) && ref_windows != '0) begin
          ref_ms    <= '0;
          meas_left <= ref_windows - 8'd1;
          measure   <= 1'b1;
          ro_clr_o  <= 1'b0;
          ro_en_o   <= 1'b1;
        end else begin
          measure   <= 1'b0;
        end
      end
      if (ro_wait != '0) begin
        ro_wait <= ro_wait - 5'd1;
        if (ro_wait == 5'd1) begin
          ro_q     <= ro_count_i;
          ro_valid <= 1'b1;
          if (!ro_en_o) ro_clr_o <= 1'b1;  // clear unless the next window measures again
        end
      end
      if (cut) partial <= 1'b1;
    end
  end

  // ------------------------------------------------------------------ commands
  logic [7:0]  cmd_pl[8];
  logic [7:0]  cmd_n;
  logic        rep_pend;
  logic [7:0]  rep_kind;               // FBS_T_ACK / PONG / INFO / AGING_INFO
  logic [3:0]  rep_dst;
  logic [7:0]  rep_ref_type, rep_ref_seq, rep_status;
  logic [31:0] rep_nonce;
  logic        tx_busy;
  logic        tx_reply_taken;

  assign rx_ready_o = !rep_pend;

  function automatic logic [7:0] expect_len(input logic [7:0] t);
    unique case (t)
      FBS_T_PING:                  return 8'd4;
      FBS_T_GET_INFO:              return 8'd0;
      FBS_AGING_T_AGING_SET_MODE:  return 8'(FBS_AGING_AGING_SET_MODE_LEN);
      FBS_AGING_T_AGING_SET_HIST:  return 8'(FBS_AGING_AGING_SET_HIST_LEN);
      FBS_AGING_T_AGING_GET_INFO:  return 8'd0;
      default:                     return 8'hFF;
    endcase
  endfunction

  always_ff @(posedge clk) begin
    cut <= 1'b0;
    if (!rst_ni) begin
      cmd_n        <= '0;
      rep_pend     <= 1'b0;
      rep_kind     <= '0;
      rep_dst      <= '0;
      rep_ref_type <= '0;
      rep_ref_seq  <= '0;
      rep_status   <= '0;
      rep_nonce    <= '0;
      sweep_mode   <= 2'(FBS_AGING_SWEEP_MODE_CONTINUOUS);
      window_ms    <= 16'(WINDOW_MS);
      periodic     <= 1'b1;
      ref_period_s <= 16'(REF_PERIOD_S);
      ref_windows  <= 8'(REF_WINDOWS);
      hist_base    <= 16'd300;
      hist_width   <= 8'd16;
      for (int i = 0; i < 8; i++) cmd_pl[i] <= '0;
    end else begin
      if (rx_valid_i && rx_ready_o) begin
        if (!rx_empty_i && cmd_n < 8'd8) cmd_pl[cmd_n[2:0]] <= rx_data_i;
        cmd_n <= rx_empty_i ? cmd_n : cmd_n + 8'd1;
        if (rx_last_i) begin
          cmd_n <= '0;
          if (!rx_flags_i[1]) begin                       // never answer a reply
            rep_pend     <= 1'b1;
            rep_dst      <= rx_src_i;
            rep_ref_type <= rx_type_i;
            rep_ref_seq  <= rx_seq_i;
            rep_kind     <= FBS_T_ACK;
            rep_status   <= FBS_ACK_STATUS_OK;
            if (expect_len(rx_type_i) == 8'hFF) begin
              rep_status <= FBS_ACK_STATUS_UNKNOWN_TYPE;
            end else if (rx_len_i != expect_len(rx_type_i)) begin
              rep_status <= FBS_ACK_STATUS_BAD_LEN;
            end else begin
              unique case (rx_type_i)
                FBS_T_PING: begin
                  rep_kind  <= FBS_T_PONG;
                  rep_nonce <= {rx_data_i, cmd_pl[2], cmd_pl[1], cmd_pl[0]};
                end
                FBS_T_GET_INFO:             rep_kind <= FBS_T_INFO;
                FBS_AGING_T_AGING_GET_INFO: rep_kind <= FBS_AGING_T_AGING_INFO;
                FBS_AGING_T_AGING_SET_MODE: begin
                  // payload: mode, window_ms(2), periodic, ref_period_s(2), ref_windows (last byte now)
                  if (cmd_pl[0] > 8'd2 || {cmd_pl[2], cmd_pl[1]} < 16'(FBS_AGING_AGING_WINDOW_MS_MIN) ||
                      {cmd_pl[2], cmd_pl[1]} > 16'(FBS_AGING_AGING_WINDOW_MS_MAX) || cmd_pl[3] > 8'd1 ||
                      ({cmd_pl[5], cmd_pl[4]} != '0 && rx_data_i == '0)) begin
                    rep_status <= FBS_ACK_STATUS_OUT_OF_RANGE;
                  end else begin
                    sweep_mode   <= cmd_pl[0][1:0];
                    window_ms    <= {cmd_pl[2], cmd_pl[1]};
                    periodic     <= cmd_pl[3][0];
                    ref_period_s <= {cmd_pl[5], cmd_pl[4]};
                    ref_windows  <= rx_data_i;
                    cut          <= 1'b1;
                  end
                end
                FBS_AGING_T_AGING_SET_HIST: begin
                  if (rx_data_i == '0) begin
                    rep_status <= FBS_ACK_STATUS_OUT_OF_RANGE;
                  end else begin
                    hist_base  <= {cmd_pl[1], cmd_pl[0]};
                    hist_width <= rx_data_i;
                    cut        <= 1'b1;
                  end
                end
                default: ;
              endcase
            end
          end
        end
      end
      if (rep_pend && tx_reply_taken) rep_pend <= 1'b0;
    end
  end

  // ------------------------------------------------------------------ frame builder
  typedef enum logic [2:0] {F_NONE, F_REPLY, F_WINDOW, F_CHAIN, F_RO, F_INFO} frame_e;
  logic         seq_pend;               // a window's frames are waiting
  logic [CW-1:0] seq_chain;             // next chain to send
  logic         seq_window, seq_ro;
  logic         info_pend;
  logic [31:0]  info_ms;
  frame_e       cur;
  logic [PL*8-1:0] pl;
  logic [7:0]   k;

  function automatic logic chain_sent(input int i, input logic meas);
    return (i != REF) || meas;
  endfunction

  // the payload of the next frame, built from the snapshot
  logic [PL*8-1:0] npl;
  logic [7:0] ntype, nlen;
  logic [3:0] ndst;
  logic [1:0] nflags;
  frame_e     nxt;

  function automatic logic [PL*8-1:0] put(input logic [PL*8-1:0] b, input int ofs, input logic [63:0] v,
                                           input int n);
    for (int j = 0; j < 8; j++) if (j < n) b[8*(ofs + j) +: 8] = v[8*j +: 8];
    return b;
  endfunction

  // NAME is a string parameter: right-aligned, so skip its leading zero bytes
  function automatic logic [7:0] name_byte(input int j);
    int lead;
    lead = 0;
    for (int i = 15; i >= 0; i--) if (NAME[8*i +: 8] == 8'h00 && lead == 15 - i) lead++;
    return (j + lead < 16) ? NAME[8*(15 - (j + lead)) +: 8] : 8'h00;
  endfunction

  always_comb begin
    npl = '0;
    nxt = F_NONE;
    ntype = '0;
    nlen = '0;
    ndst = FBS_NODE_HOST;
    nflags = 2'b00;
    if (rep_pend) begin
      nxt = F_REPLY;
      ndst = rep_dst;
      nflags = 2'b10;
      ntype = rep_kind;
      unique case (rep_kind)
        FBS_T_PONG: begin
          nlen = 8'(FBS_PONG_LEN);
          npl = put(npl, FBS_PONG_OFS_NONCE, 64'(rep_nonce), 4);
          npl = put(npl, FBS_PONG_OFS_UPTIME_MS, 64'(t_ms_i), 4);
        end
        FBS_T_INFO: begin
          nlen = 8'(FBS_INFO_LEN);
          npl = put(npl, FBS_INFO_OFS_PROTO_MAJOR, 64'(FBS_PROTO_MAJOR), 1);
          npl = put(npl, FBS_INFO_OFS_PROTO_MINOR, 64'(FBS_PROTO_MINOR), 1);
          npl = put(npl, FBS_INFO_OFS_FW_VERSION, 64'(FBS_AGING_AGING_RTL_VERSION), 2);
          npl = put(npl, FBS_INFO_OFS_GIT_HASH, 64'(GIT_HASH), 4);
          npl = put(npl, FBS_INFO_OFS_BUILD_ID, 64'(BUILD_ID), 4);
          npl = put(npl, FBS_INFO_OFS_CLOCK_SOURCE, 64'(FBS_CLOCK_SOURCE_FPGA_BOARD), 1);
          for (int j = 0; j < 16; j++) npl = put(npl, FBS_INFO_OFS_NAME + j, 64'(name_byte(j)), 1);
        end
        FBS_AGING_T_AGING_INFO: ;            // built below with the periodic INFO
        default: begin
          ntype = FBS_T_ACK;
          nlen = 8'(FBS_ACK_LEN);
          npl = put(npl, FBS_ACK_OFS_REF_TYPE, 64'(rep_ref_type), 1);
          npl = put(npl, FBS_ACK_OFS_REF_SEQ, 64'(rep_ref_seq), 1);
          npl = put(npl, FBS_ACK_OFS_STATUS, 64'(rep_status), 1);
        end
      endcase
    end else if (seq_pend && seq_window) begin
      nxt = F_WINDOW;
      ntype = FBS_AGING_T_AGING_WINDOW;
      nlen = 8'(FBS_AGING_AGING_WINDOW_LEN);
      npl = put(npl, FBS_AGING_AGING_WINDOW_OFS_T_MS, 64'(snap_t), 4);
      npl = put(npl, FBS_AGING_AGING_WINDOW_OFS_WINDOW_ID, 64'(snap_id), 4);
      npl = put(npl, FBS_AGING_AGING_WINDOW_OFS_SWEEPS, 64'(s_sweeps[0]), 2);
      npl = put(npl, FBS_AGING_AGING_WINDOW_OFS_LAST, 64'(s_last[0]), 2);
      npl = put(npl, FBS_AGING_AGING_WINDOW_OFS_MIN, 64'(s_min[0]), 2);
      npl = put(npl, FBS_AGING_AGING_WINDOW_OFS_MAX, 64'(s_max[0]), 2);
      npl = put(npl, FBS_AGING_AGING_WINDOW_OFS_SUM, 64'(s_sum[0]), 4);
      npl = put(npl, FBS_AGING_AGING_WINDOW_OFS_SUMSQ, s_sumsq[0], 8);
      for (int b = 0; b < 16; b++)
        npl = put(npl, FBS_AGING_AGING_WINDOW_OFS_HIST + 2 * b, 64'(s_hist[b]), 2);
      npl = put(npl, FBS_AGING_AGING_WINDOW_OFS_LOCK_LOSS, 64'(snap_lock_loss), 2);
      npl = put(npl, FBS_AGING_AGING_WINDOW_OFS_SWEEP_MODE, 64'(sweep_mode), 1);
      npl = put(npl, FBS_AGING_AGING_WINDOW_OFS_FLAGS, 64'({
          2'b00, snap_partial, snap_measure, snap_lock_loss != '0,
          s_sweeps[0] >= 16'd2 && s_min[0] == s_max[0], snap_timeout, s_noalarm0}), 1);
    end else if (seq_pend && seq_chain < CW'(N) && chain_sent(int'(seq_chain), snap_measure)) begin
      nxt = F_CHAIN;
      ntype = FBS_AGING_T_AGING_CHAIN;
      nlen = 8'(FBS_AGING_AGING_CHAIN_LEN);
      npl = put(npl, FBS_AGING_AGING_CHAIN_OFS_WINDOW_ID, 64'(snap_id), 4);
      npl = put(npl, FBS_AGING_AGING_CHAIN_OFS_CHAIN, 64'(seq_chain), 1);
      npl = put(npl, FBS_AGING_AGING_CHAIN_OFS_KIND, 64'(KINDS[8*seq_chain +: 8]), 1);
      npl = put(npl, FBS_AGING_AGING_CHAIN_OFS_SIZE, 64'(SIZES[16*seq_chain +: 16]), 2);
      npl = put(npl, FBS_AGING_AGING_CHAIN_OFS_SWEEPS, 64'(s_sweeps[seq_chain]), 2);
      npl = put(npl, FBS_AGING_AGING_CHAIN_OFS_LAST, 64'(s_last[seq_chain]), 2);
      npl = put(npl, FBS_AGING_AGING_CHAIN_OFS_MIN, 64'(s_min[seq_chain]), 2);
      npl = put(npl, FBS_AGING_AGING_CHAIN_OFS_MAX, 64'(s_max[seq_chain]), 2);
      npl = put(npl, FBS_AGING_AGING_CHAIN_OFS_SUM, 64'(s_sum[seq_chain]), 4);
      npl = put(npl, FBS_AGING_AGING_CHAIN_OFS_SUMSQ, s_sumsq[seq_chain], 8);
      npl = put(npl, FBS_AGING_AGING_CHAIN_OFS_STRESSED, 64'(seq_chain != CW'(REF)), 1);
    end else if (seq_pend && seq_ro && ro_valid && R > 0) begin
      nxt = F_RO;
      ntype = FBS_AGING_T_AGING_RO;
      nlen = 8'(FBS_AGING_AGING_RO_LEN);
      npl = put(npl, FBS_AGING_AGING_RO_OFS_WINDOW_ID, 64'(snap_id), 4);
      npl = put(npl, FBS_AGING_AGING_RO_OFS_WINDOW_MS, 64'(ro_window_ms), 2);
      npl = put(npl, FBS_AGING_AGING_RO_OFS_N_RO, 64'(R), 1);
      for (int r = 0; r < R && r < 4; r++)
        npl = put(npl, FBS_AGING_AGING_RO_OFS_COUNTS + 4 * r, 64'(ro_q[r]), 4);
    end else if (info_pend) begin
      nxt = F_INFO;
    end
    if (nxt == F_INFO || (nxt == F_REPLY && rep_kind == FBS_AGING_T_AGING_INFO)) begin
      ntype = FBS_AGING_T_AGING_INFO;
      nlen = 8'(FBS_AGING_AGING_INFO_LEN);
      npl = put(npl, FBS_AGING_AGING_INFO_OFS_RTL_VERSION, 64'(FBS_AGING_AGING_RTL_VERSION), 2);
      npl = put(npl, FBS_AGING_AGING_INFO_OFS_WINDOW_MS, 64'(window_ms), 2);
      npl = put(npl, FBS_AGING_AGING_INFO_OFS_PS_STEP_FS, 64'(PS_STEP_FS), 4);
      npl = put(npl, FBS_AGING_AGING_INFO_OFS_MAX_STEPS, 64'(MAX_STEPS), 2);
      npl = put(npl, FBS_AGING_AGING_INFO_OFS_SWEEP_MODE, 64'(sweep_mode), 1);
      npl = put(npl, FBS_AGING_AGING_INFO_OFS_PERIODIC, 64'(periodic), 1);
      npl = put(npl, FBS_AGING_AGING_INFO_OFS_REF_PERIOD_S, 64'(ref_period_s), 2);
      npl = put(npl, FBS_AGING_AGING_INFO_OFS_REF_WINDOWS, 64'(ref_windows), 1);
      npl = put(npl, FBS_AGING_AGING_INFO_OFS_HIST_BASE, 64'(hist_base), 2);
      npl = put(npl, FBS_AGING_AGING_INFO_OFS_HIST_BIN_WIDTH, 64'(hist_width), 1);
      npl = put(npl, FBS_AGING_AGING_INFO_OFS_N_CHAINS, 64'(N), 1);
      for (int i = 0; i < N && i < 10; i++) begin
        npl = put(npl, FBS_AGING_AGING_INFO_OFS_CHAINS + 4 * i + FBS_AGING_AGING_INFO_CHAINS_OFS_KIND,
            64'(KINDS[8*i +: 8]), 1);
        npl = put(npl, FBS_AGING_AGING_INFO_OFS_CHAINS + 4 * i + FBS_AGING_AGING_INFO_CHAINS_OFS_SIZE,
            64'(SIZES[16*i +: 16]), 2);
        npl = put(npl, FBS_AGING_AGING_INFO_OFS_CHAINS + 4 * i + FBS_AGING_AGING_INFO_CHAINS_OFS_STRESSED,
            64'(i != REF), 1);
      end
      npl = put(npl, FBS_AGING_AGING_INFO_OFS_N_RO, 64'(R), 1);
    end
  end

  assign tx_valid_o     = tx_busy;
  assign tx_data_o      = pl[8*k +: 8];
  assign tx_last_o      = (tx_len_o == 8'd0) || (k == tx_len_o - 8'd1);
  assign tx_reply_taken = !tx_busy && nxt == F_REPLY;

  always_ff @(posedge clk) begin
    if (!rst_ni) begin
      tx_busy    <= 1'b0;
      cur        <= F_NONE;
      k          <= '0;
      tx_type_o  <= '0;
      tx_dst_o   <= '0;
      tx_flags_o <= '0;
      tx_len_o   <= '0;
      seq_pend   <= 1'b0;
      seq_window <= 1'b0;
      seq_chain  <= '0;
      seq_ro     <= 1'b0;
      info_pend  <= 1'b1;                    // AGING_INFO after reset
      info_ms    <= '0;
      pl         <= '0;
    end else begin
      if (tick_1ms_i) begin
        info_ms <= info_ms + 32'd1;
        if (info_ms + 32'd1 >= 32'(INFO_PERIOD_MS)) begin
          info_ms   <= '0;
          info_pend <= 1'b1;
        end
      end
      if (st_snapped && periodic) begin
        // a new snapshot replaces whatever of the last window is still unsent
        seq_pend   <= 1'b1;
        seq_window <= 1'b1;
        seq_chain  <= '0;
        seq_ro     <= snap_measure;
      end
      if (!tx_busy) begin
        if (nxt != F_NONE) begin
          pl         <= npl;
          tx_type_o  <= ntype;
          tx_dst_o   <= ndst;
          tx_flags_o <= nflags;
          tx_len_o   <= nlen;
          k          <= '0;
          cur        <= nxt;
          tx_busy    <= 1'b1;
          unique case (nxt)
            F_WINDOW: seq_window <= 1'b0;
            F_CHAIN:  seq_chain <= seq_chain + 1'b1;
            F_RO: seq_ro <= 1'b0;
            F_INFO: info_pend <= 1'b0;
            default: ;
          endcase
        end else if (seq_pend && !seq_window && seq_chain >= CW'(N) && !seq_ro) begin
          seq_pend <= 1'b0;
        end
      end else if (tx_ready_i) begin
        k <= k + 8'd1;
        if (tx_last_o) begin
          tx_busy <= 1'b0;
          cur     <= F_NONE;
        end
      end
      // the reference chain is not sent outside measurement windows
      if (seq_pend && !tx_busy && seq_chain < CW'(N) && !chain_sent(int'(seq_chain), snap_measure) &&
          !(st_snapped && periodic))
        seq_chain <= seq_chain + 1'b1;
    end
  end

  wire unused = ^{cur, rx_flags_i[0]};
endmodule
