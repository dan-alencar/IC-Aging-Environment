// Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
// Copyright 2022-2025 Advanced Micro Devices, Inc. All Rights Reserved.
// --------------------------------------------------------------------------------
// Tool Version: Vivado v.2025.2 (lin64) Build 6299465 Fri Nov 14 12:34:56 MST 2025
// Date        : Sat Dec 27 11:21:19 2025
// Host        : dan-alencar running 64-bit Linux Mint 22.2
// Command     : write_verilog -force -mode synth_stub -rename_top decalper_eb_ot_sdeen_pot_pi_dehcac_xnilix -prefix
//               decalper_eb_ot_sdeen_pot_pi_dehcac_xnilix_ clk_wiz_0_stub.v
// Design      : clk_wiz_0
// Purpose     : Stub declaration of top-level module interface
// Device      : xcau15p-ffvb676-1-i
// --------------------------------------------------------------------------------

// This empty module with port declaration file causes synthesis tools to infer a black box for IP.
// The synthesis directives are for Synopsys Synplify support to prevent IO buffer insertion.
// Please paste the declaration into a Verilog source file or add the file as an additional source.
(* CORE_GENERATION_INFO = "clk_wiz_0,clk_wiz_v6_0_17_0_0,{component_name=clk_wiz_0,use_phase_alignment=false,use_min_o_jitter=false,use_max_i_jitter=false,use_dyn_phase_shift=true,use_inclk_switchover=false,use_dyn_reconfig=false,enable_axi=0,feedback_source=FDBK_AUTO,PRIMITIVE=MMCM,num_out_clk=3,clkin1_period=10.000,clkin2_period=10.000,use_power_down=false,use_reset=true,use_locked=true,use_inclk_stopped=false,feedback_type=SINGLE,CLOCK_MGR_TYPE=NA,manual_override=false}" *) 
module decalper_eb_ot_sdeen_pot_pi_dehcac_xnilix(sys_clk, phase_clk, clk_en, psclk, psen, psincdec, 
  psdone, reset, locked, clk_in1_p, clk_in1_n)
/* synthesis syn_black_box black_box_pad_pin="psen,psincdec,psdone,reset,locked,clk_in1_p,clk_in1_n" */
/* synthesis syn_force_seq_prim="sys_clk" */
/* synthesis syn_force_seq_prim="phase_clk" */
/* synthesis syn_force_seq_prim="clk_en" */
/* synthesis syn_force_seq_prim="psclk" */;
  output sys_clk /* synthesis syn_isclock = 1 */;
  output phase_clk /* synthesis syn_isclock = 1 */;
  output clk_en /* synthesis syn_isclock = 1 */;
  input psclk /* synthesis syn_isclock = 1 */;
  input psen;
  input psincdec;
  output psdone;
  input reset;
  output locked;
  input clk_in1_p;
  input clk_in1_n;
endmodule
