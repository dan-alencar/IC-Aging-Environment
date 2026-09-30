// Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
// Copyright 2022-2026 Advanced Micro Devices, Inc. All Rights Reserved.
// --------------------------------------------------------------------------------
// Tool Version: Vivado v.2025.2.1 (lin64) Build 6403652 Thu Mar 19 13:47:00 MDT 2026
// Date        : Thu Jun 11 11:44:27 2026
// Host        : marceau-lesc running 64-bit Linux Mint 22.3
// Command     : write_verilog -force -mode synth_stub
//               /home/marceau/Documents/GitHub/IC-Aging-Environment/vivado/aging_study_nexys4ddr/src/ip/clk_wiz_0/clk_wiz_0_stub.v
// Design      : clk_wiz_0
// Purpose     : Stub declaration of top-level module interface
// Device      : xcau15p-ubva368-2-e
// --------------------------------------------------------------------------------

// This empty module with port declaration file causes synthesis tools to infer a black box for IP.
// The synthesis directives are for Synopsys Synplify support to prevent IO buffer insertion.
// Please paste the declaration into a Verilog source file or add the file as an additional source.
(* CORE_GENERATION_INFO = "clk_wiz_0,clk_wiz_v6_0_16_0_0,{component_name=clk_wiz_0,use_phase_alignment=true,use_min_o_jitter=false,use_max_i_jitter=false,use_dyn_phase_shift=true,use_inclk_switchover=false,use_dyn_reconfig=false,enable_axi=0,feedback_source=FDBK_AUTO,PRIMITIVE=MMCM,num_out_clk=3,clkin1_period=10.000,clkin2_period=10.000,use_power_down=false,use_reset=true,use_locked=true,use_inclk_stopped=false,feedback_type=SINGLE,CLOCK_MGR_TYPE=NA,manual_override=false}" *) 
module clk_wiz_0(clk_en, sensor0, clk_sys, reset, locked, clk_in1, 
  psclk, psen, psincdec, psdone)
/* synthesis syn_black_box black_box_pad_pin="reset,locked,clk_in1,psen,psincdec,psdone" */
/* synthesis syn_force_seq_prim="clk_en" */
/* synthesis syn_force_seq_prim="sensor0" */
/* synthesis syn_force_seq_prim="clk_sys" */
/* synthesis syn_force_seq_prim="psclk" */;
  output clk_en /* synthesis syn_isclock = 1 */;
  output sensor0 /* synthesis syn_isclock = 1 */;
  output clk_sys /* synthesis syn_isclock = 1 */;
  input reset;
  output locked;
  input clk_in1;
  input psclk /* synthesis syn_isclock = 1 */;
  input psen;
  input psincdec;
  output psdone;
endmodule
