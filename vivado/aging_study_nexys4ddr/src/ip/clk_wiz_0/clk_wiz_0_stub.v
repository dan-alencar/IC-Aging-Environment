// Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
// Copyright 2022-2025 Advanced Micro Devices, Inc. All Rights Reserved.
// --------------------------------------------------------------------------------
// Stub declaration for clk_wiz_0: 3-output MMCM with dynamic phase shift.
// Device: xc7a100tcsg324-1
// Outputs: clk_en (100°), sensor0 (0°+DPS), clk_sys (0° reference)
// --------------------------------------------------------------------------------

(* CORE_GENERATION_INFO = "clk_wiz_0,clk_wiz_v6_0_16_0_0,{component_name=clk_wiz_0,use_phase_alignment=true,use_min_o_jitter=false,use_max_i_jitter=false,use_dyn_phase_shift=true,use_inclk_switchover=false,use_dyn_reconfig=false,enable_axi=0,feedback_source=FDBK_AUTO,PRIMITIVE=MMCM,num_out_clk=3,clkin1_period=10.000,clkin2_period=10.000,use_power_down=false,use_reset=true,use_locked=true,use_inclk_stopped=false,feedback_type=SINGLE,CLOCK_MGR_TYPE=NA,manual_override=false}" *)
module clk_wiz_0 (clk_en, sensor0, clk_sys, reset, locked, clk_in1, psclk, psen, psincdec, psdone)
/* synthesis syn_black_box black_box_pad_pin="reset,locked,clk_in1,psclk,psen,psincdec,psdone" */
/* synthesis syn_force_seq_prim="clk_en,sensor0,clk_sys" */;
  output clk_en    /* synthesis syn_isclock = 1 */;
  output sensor0   /* synthesis syn_isclock = 1 */;
  output clk_sys   /* synthesis syn_isclock = 1 */;
  input  reset;
  output locked;
  input  clk_in1;
  input  psclk;
  input  psen;
  input  psincdec;
  output psdone;
endmodule
