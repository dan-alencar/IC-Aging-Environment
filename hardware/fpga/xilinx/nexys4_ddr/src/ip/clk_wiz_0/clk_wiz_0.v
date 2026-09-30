// clk_wiz_0.v — top-level wrapper for the Nexys4 DDR aging-study MMCM.
//
// Three 100 MHz outputs, one dynamically phase-shiftable (sensor0 / psclk).
//
// Port mapping (matches nexys4_aging_top.sv instantiation):
//   clk_en   — CLKOUT0, 100° fixed offset  (FF3 catcher clock)
//   sensor0  — CLKOUT1, 0° + DPS (FINE_PS) (FF1 phase-shifted clock)
//   clk_sys  — CLKOUT2, 0° reference        (main system clock)
//   psclk    — MMCM PSCLK input             (fed from clk_sys output)
//   psen     — MMCM PSEN
//   psincdec — MMCM PSINCDEC
//   psdone   — MMCM PSDONE
//
// Device: xc7a100tcsg324-1 (Artix-7).  VCO = 1000 MHz.

`timescale 1ps/1ps

(* CORE_GENERATION_INFO = "clk_wiz_0,clk_wiz_v6_0_16_0_0,{component_name=clk_wiz_0,use_phase_alignment=true,use_min_o_jitter=false,use_max_i_jitter=false,use_dyn_phase_shift=true,use_inclk_switchover=false,use_dyn_reconfig=false,enable_axi=0,feedback_source=FDBK_AUTO,PRIMITIVE=MMCM,num_out_clk=3,clkin1_period=10.000,clkin2_period=10.000,use_power_down=false,use_reset=true,use_locked=true,use_inclk_stopped=false,feedback_type=SINGLE,CLOCK_MGR_TYPE=NA,manual_override=false}" *)

module clk_wiz_0 (
  // Clock outputs
  output clk_en,
  output sensor0,
  output clk_sys,
  // Status / control
  input  reset,
  output locked,
  // Clock input
  input  clk_in1,
  // Dynamic phase shift
  input  psclk,
  input  psen,
  input  psincdec,
  output psdone
);

  clk_wiz_0_clk_wiz inst (
    .clk_en   (clk_en),
    .sensor0  (sensor0),
    .clk_sys  (clk_sys),
    .reset    (reset),
    .locked   (locked),
    .clk_in1  (clk_in1),
    .psclk    (psclk),
    .psen     (psen),
    .psincdec (psincdec),
    .psdone   (psdone)
  );

endmodule
