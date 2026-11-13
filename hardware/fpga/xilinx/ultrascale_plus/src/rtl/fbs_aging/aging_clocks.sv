// Measurement clocks of the aging sensors: one MMCME4_ADV, no IP (fbs SPEC §5.1).
// The same settings as the SBCCI design's clk_wiz_0: VCO 900 MHz (100 MHz x 9), three
// 100 MHz outputs:
//   clk_catch_o  50°  FF3 of every sensor (alarm latch)
//   clk_phase_o  0° + fine phase shift: FF1 of every sensor; one step = 1/(56 x 900 MHz) = 19.841 ps
//   clk_meas_o   0°   the chains' launch registers and FF2
// PSCLK is the platform clock (clk_i). Without FBS_XILINX a behavioural model counts the
// phase in steps (sim_phase_o, negative = moved back) and answers PSEN after 12 cycles.
module aging_clocks (
  input  logic        clk_i,          // 100 MHz from the board oscillator (also the platform clock)
  input  logic        rst_i,
  output logic        clk_catch_o,
  output logic        clk_phase_o,
  output logic        clk_meas_o,
  output logic        locked_o,
  input  logic        psen_i,
  input  logic        psincdec_i,
  output logic        psdone_o,
  output int          sim_phase_o     // simulation only
);
`ifdef FBS_XILINX
  logic fb, c0, c1, c2;
  MMCME4_ADV #(
    .BANDWIDTH("HIGH"), .COMPENSATION("INTERNAL"), .CLKIN1_PERIOD(10.0), .DIVCLK_DIVIDE(1),
    .CLKFBOUT_MULT_F(9.0), .CLKFBOUT_PHASE(0.0),
    .CLKOUT0_DIVIDE_F(9.0), .CLKOUT0_PHASE(50.0), .CLKOUT0_DUTY_CYCLE(0.5),
    .CLKOUT1_DIVIDE(9), .CLKOUT1_PHASE(0.0), .CLKOUT1_DUTY_CYCLE(0.5), .CLKOUT1_USE_FINE_PS("TRUE"),
    .CLKOUT2_DIVIDE(9), .CLKOUT2_PHASE(0.0), .CLKOUT2_DUTY_CYCLE(0.5)
  ) u_mmcm (
    .CLKIN1(clk_i), .CLKIN2(1'b0), .CLKINSEL(1'b1), .CLKFBIN(fb), .CLKFBOUT(fb), .CLKFBOUTB(),
    .CLKOUT0(c0), .CLKOUT0B(), .CLKOUT1(c1), .CLKOUT1B(), .CLKOUT2(c2), .CLKOUT2B(),
    .CLKOUT3(), .CLKOUT3B(), .CLKOUT4(), .CLKOUT5(), .CLKOUT6(),
    .LOCKED(locked_o), .RST(rst_i), .PWRDWN(1'b0),
    .PSCLK(clk_i), .PSEN(psen_i), .PSINCDEC(psincdec_i), .PSDONE(psdone_o),
    .DADDR(7'd0), .DCLK(1'b0), .DEN(1'b0), .DI(16'd0), .DWE(1'b0), .DO(), .DRDY(),
    .CDDCDONE(), .CDDCREQ(1'b0), .CLKFBSTOPPED(), .CLKINSTOPPED()
  );
  BUFG u_bg0 (.I(c0), .O(clk_catch_o));
  BUFG u_bg1 (.I(c1), .O(clk_phase_o));
  BUFG u_bg2 (.I(c2), .O(clk_meas_o));
  assign sim_phase_o = 0;
`else
  logic [7:0] lock_cnt;
  logic [3:0] busy;
  logic       dir;
  assign clk_catch_o = clk_i;
  assign clk_phase_o = clk_i;
  assign clk_meas_o  = clk_i;
  assign locked_o    = lock_cnt == 8'hFF;
  always_ff @(posedge clk_i or posedge rst_i) begin
    if (rst_i) begin
      lock_cnt    <= '0;
      busy        <= '0;
      dir         <= 1'b0;
      psdone_o    <= 1'b0;
      sim_phase_o <= 0;
    end else begin
      psdone_o <= 1'b0;
      if (lock_cnt != 8'hFF) lock_cnt <= lock_cnt + 8'd1;
      if (busy != '0) begin
        busy <= busy - 4'd1;
        if (busy == 4'd1) begin
          psdone_o    <= 1'b1;
          sim_phase_o <= dir ? sim_phase_o + 1 : sim_phase_o - 1;
        end
      end else if (psen_i && locked_o) begin
        busy <= 4'd12;
        dir  <= psincdec_i;
      end
    end
  end
`endif
endmodule
