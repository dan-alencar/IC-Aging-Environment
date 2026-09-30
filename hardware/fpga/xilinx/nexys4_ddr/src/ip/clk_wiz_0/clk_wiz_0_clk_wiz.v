// clk_wiz_0_clk_wiz.v — MMCME2_ADV implementation for the Nexys4 DDR aging design.
//
// Configuration (100 MHz in → 3 × 100 MHz out, VCO = 1000 MHz):
//   CLKOUT0 → clk_en   : 100 MHz, 100° fixed offset  — FF3 catcher clock
//   CLKOUT1 → sensor0  : 100 MHz, 0° + FINE_PS=TRUE  — FF1 phase-shiftable clock
//   CLKOUT2 → clk_sys  : 100 MHz, 0°                 — main system/reference clock
//
// Dynamic phase shift (DPS):
//   PSCLK is fed from clk_sys (top module connects .psclk(clk_sys)).
//   Phase steps ≈ 11–12 ps each at 1000 MHz VCO.

`timescale 1ps/1ps

module clk_wiz_0_clk_wiz (
  output clk_en,
  output sensor0,
  output clk_sys,
  output locked,
  input  reset,
  input  clk_in1,
  input  psclk,
  input  psen,
  input  psincdec,
  output psdone
);

  wire clk_in1_buf;
  wire clkfbout, clkfbout_buf;
  wire clkout0, clkout1, clkout2;

  IBUF clkin1_ibuf (
    .O (clk_in1_buf),
    .I (clk_in1)
  );

  MMCME2_ADV #(
    .BANDWIDTH            ("OPTIMIZED"),
    .CLKOUT4_CASCADE      ("FALSE"),
    .COMPENSATION         ("ZHOLD"),
    .STARTUP_WAIT         ("FALSE"),
    .DIVCLK_DIVIDE        (1),
    .CLKFBOUT_MULT_F      (10.000),
    .CLKFBOUT_PHASE       (0.000),
    .CLKFBOUT_USE_FINE_PS ("FALSE"),
    .CLKIN1_PERIOD        (10.000),
    // CLKOUT0 → clk_en (99° phase offset, catcher clock for FF3)
    // 99.0 = 4.5 * 22 — nearest valid multiple of (45/DIVIDE_F=4.5) to the intended 100°
    .CLKOUT0_DIVIDE_F     (10.000),
    .CLKOUT0_PHASE        (99.000),
    .CLKOUT0_DUTY_CYCLE   (0.500),
    .CLKOUT0_USE_FINE_PS  ("FALSE"),
    // CLKOUT1 → sensor0 / psclk (dynamically phase-shiftable via FINE_PS)
    .CLKOUT1_DIVIDE       (10),
    .CLKOUT1_PHASE        (0.000),
    .CLKOUT1_DUTY_CYCLE   (0.500),
    .CLKOUT1_USE_FINE_PS  ("TRUE"),
    // CLKOUT2 → clk_sys (reference system clock, also fed back to PSCLK)
    .CLKOUT2_DIVIDE       (10),
    .CLKOUT2_PHASE        (0.000),
    .CLKOUT2_DUTY_CYCLE   (0.500),
    .CLKOUT2_USE_FINE_PS  ("FALSE")
  ) mmcm_inst (
    .CLKFBOUT   (clkfbout),
    .CLKFBOUTB  (),
    .CLKOUT0    (clkout0),
    .CLKOUT0B   (),
    .CLKOUT1    (clkout1),
    .CLKOUT1B   (),
    .CLKOUT2    (clkout2),
    .CLKOUT2B   (),
    .CLKOUT3    (),
    .CLKOUT3B   (),
    .CLKOUT4    (),
    .CLKOUT5    (),
    .CLKOUT6    (),
    .CLKFBIN    (clkfbout_buf),
    .CLKIN1     (clk_in1_buf),
    .CLKIN2     (1'b0),
    .CLKINSEL   (1'b1),
    .DADDR      (7'h0),
    .DCLK       (1'b0),
    .DEN        (1'b0),
    .DI         (16'h0),
    .DO         (),
    .DRDY       (),
    .DWE        (1'b0),
    .PSCLK      (psclk),
    .PSEN       (psen),
    .PSINCDEC   (psincdec),
    .PSDONE     (psdone),
    .LOCKED     (locked),
    .CLKINSTOPPED (),
    .CLKFBSTOPPED (),
    .PWRDWN     (1'b0),
    .RST        (reset)
  );

  BUFG clkfb_buf   (.O (clkfbout_buf), .I (clkfbout));
  BUFG clkout0_buf (.O (clk_en),       .I (clkout0));
  BUFG clkout1_buf (.O (sensor0),      .I (clkout1));
  BUFG clkout2_buf (.O (clk_sys),      .I (clkout2));

endmodule
