// One sensor sweep (fpgaging-board-support SPEC §6.1).
//
// The sensors' FF1 samples each chain with the phase-shiftable clock. A sweep moves that
// clock back one MMCM fine step (19.841 ps) at a time and records, for every active chain,
// the number of steps after which its sensor first alarms: the chain's slack in steps. When
// every active chain has alarmed, or after max_steps, the phase is moved forward by the
// same number of steps, so every sweep starts from the same phase (an interrupted step is
// given back too). At every phase the alarms are looked at for SAMPLE cycles, SETTLE cycles
// after PSDONE, because the sensors' alarm only fires on the cycles where the chain toggles.
module aging_sweep #(
  parameter int unsigned N          = 10,
  parameter int unsigned SETTLE     = 4,
  parameter int unsigned SAMPLE     = 4,
  parameter int unsigned PS_TIMEOUT = 255   // cycles to wait for PSDONE (the MMCM needs 12)
) (
  input  logic                 clk,
  input  logic                 rst_ni,
  input  logic                 start_i,       // begin a sweep (ignored while busy)
  input  logic [N-1:0]         active_i,      // chains to measure, sampled at start
  input  logic [15:0]          max_steps_i,
  input  logic [N-1:0]         alarm_i,       // synchronised to clk
  output logic                 psen_o,
  output logic                 psincdec_o,    // 0: back (measure), 1: forward (return)
  input  logic                 psdone_i,
  output logic                 busy_o,
  output logic                 done_o,        // one cycle; the outputs below are valid
  output logic [N-1:0][15:0]   count_o,
  output logic [N-1:0]         measured_o,
  output logic [N-1:0]         noalarm_o,     // reached max_steps without an alarm
  output logic                 timeout_o      // one cycle: PSDONE did not come
);
  typedef enum logic [2:0] {IDLE, SETTLE_S, SAMPLE_S, STEP, WAIT, RET, WAIT_RET, DONE} state_e;
  state_e      state;
  logic [15:0] steps, back;
  logic [7:0]  cnt;
  logic [N-1:0] hit, act;

  assign busy_o     = state != IDLE;
  assign measured_o = act;

  always_ff @(posedge clk) begin
    psen_o    <= 1'b0;
    done_o    <= 1'b0;
    timeout_o <= 1'b0;
    if (!rst_ni) begin
      state      <= IDLE;
      psincdec_o <= 1'b0;
      steps      <= '0;
      back       <= '0;
      cnt        <= '0;
      hit        <= '0;
      act        <= '0;
      count_o    <= '0;
      noalarm_o  <= '0;
    end else begin
      unique case (state)
        IDLE: if (start_i && active_i != '0) begin
          act   <= active_i;
          hit   <= '0;
          steps <= '0;
          cnt   <= '0;
          state <= SETTLE_S;
        end
        SETTLE_S: begin
          cnt <= cnt + 8'd1;
          if (cnt == 8'(SETTLE - 1)) begin
            cnt   <= '0;
            state <= SAMPLE_S;
          end
        end
        SAMPLE_S: begin
          for (int i = 0; i < N; i++)
            if (act[i] && !hit[i] && alarm_i[i]) begin
              hit[i]     <= 1'b1;
              count_o[i] <= steps;
            end
          cnt <= cnt + 8'd1;
          if (cnt == 8'(SAMPLE - 1)) begin
            cnt <= '0;
            if ((act & ~(hit | alarm_i)) == '0 || steps >= max_steps_i) begin
              for (int i = 0; i < N; i++)
                if (act[i] && !hit[i] && !alarm_i[i]) count_o[i] <= steps;
              noalarm_o <= act & ~(hit | alarm_i);
              back      <= '0;
              state     <= RET;
            end else begin
              state <= STEP;
            end
          end
        end
        STEP: begin
          psen_o     <= 1'b1;
          psincdec_o <= 1'b0;
          cnt        <= '0;
          state      <= WAIT;
        end
        WAIT: begin
          cnt <= cnt + 8'd1;
          if (psdone_i) begin
            steps <= steps + 16'd1;
            cnt   <= '0;
            state <= SETTLE_S;
          end else if (cnt == 8'(PS_TIMEOUT)) begin
            timeout_o <= 1'b1;            // treat it as done and carry on
            steps     <= steps + 16'd1;
            cnt       <= '0;
            state     <= SETTLE_S;
          end
        end
        RET: begin
          if (back == steps) begin
            state <= DONE;
          end else begin
            psen_o     <= 1'b1;
            psincdec_o <= 1'b1;
            cnt        <= '0;
            state      <= WAIT_RET;
          end
        end
        WAIT_RET: begin
          cnt <= cnt + 8'd1;
          if (psdone_i || cnt == 8'(PS_TIMEOUT)) begin
            if (!psdone_i) timeout_o <= 1'b1;
            back  <= back + 16'd1;
            state <= RET;
          end
        end
        DONE: begin
          done_o <= 1'b1;
          state  <= IDLE;
        end
        default: state <= IDLE;
      endcase
    end
  end
endmodule
