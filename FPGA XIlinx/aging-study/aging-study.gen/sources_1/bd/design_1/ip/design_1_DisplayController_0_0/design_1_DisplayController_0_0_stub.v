// Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
// Copyright 2022-2024 Advanced Micro Devices, Inc. All Rights Reserved.
// --------------------------------------------------------------------------------
// Tool Version: Vivado v.2024.2 (lin64) Build 5239630 Fri Nov 08 22:34:34 MST 2024
// Date        : Wed Feb  5 19:11:24 2025
// Host        : pop-os running 64-bit Pop!_OS 22.04 LTS
// Command     : write_verilog -force -mode synth_stub
//               /home/mirai/Documents/Projects/Aging-main/vivado_project/aging-study/aging-study.gen/sources_1/bd/design_1/ip/design_1_DisplayController_0_0/design_1_DisplayController_0_0_stub.v
// Design      : design_1_DisplayController_0_0
// Purpose     : Stub declaration of top-level module interface
// Device      : xc7a100tcsg324-1
// --------------------------------------------------------------------------------

// This empty module with port declaration file causes synthesis tools to infer a black box for IP.
// The synthesis directives are for Synopsys Synplify support to prevent IO buffer insertion.
// Please paste the declaration into a Verilog source file or add the file as an additional source.
(* CHECK_LICENSE_TYPE = "design_1_DisplayController_0_0,DisplayController,{}" *) (* CORE_GENERATION_INFO = "design_1_DisplayController_0_0,DisplayController,{x_ipProduct=Vivado 2024.2,x_ipVendor=xilinx.com,x_ipLibrary=module_ref,x_ipName=DisplayController,x_ipVersion=1.0,x_ipCoreRevision=1,x_ipLanguage=VERILOG,x_ipSimLanguage=MIXED}" *) (* DowngradeIPIdentifiedWarnings = "yes" *) 
(* IP_DEFINITION_SOURCE = "module_ref" *) (* X_CORE_INFO = "DisplayController,Vivado 2024.2" *) 
module design_1_DisplayController_0_0(clk, reset, in0, in1, in2, in3, in4, in5, in6, in7, seg0, seg1, 
  seg2, seg3, seg4, seg5, seg6, dp, an)
/* synthesis syn_black_box black_box_pad_pin="reset,in0[3:0],in1[3:0],in2[3:0],in3[3:0],in4[3:0],in5[3:0],in6[3:0],in7[3:0],seg0,seg1,seg2,seg3,seg4,seg5,seg6,dp,an[7:0]" */
/* synthesis syn_force_seq_prim="clk" */;
  (* X_INTERFACE_INFO = "xilinx.com:signal:clock:1.0 clk CLK" *) (* X_INTERFACE_MODE = "slave" *) (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME clk, ASSOCIATED_RESET reset, FREQ_HZ 100000000, FREQ_TOLERANCE_HZ 0, PHASE 0.0, CLK_DOMAIN design_1_CLK100MHZ, INSERT_VIP 0" *) input clk /* synthesis syn_isclock = 1 */;
  (* X_INTERFACE_INFO = "xilinx.com:signal:reset:1.0 reset RST" *) (* X_INTERFACE_MODE = "slave" *) (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME reset, POLARITY ACTIVE_LOW, INSERT_VIP 0" *) input reset;
  input [3:0]in0;
  input [3:0]in1;
  input [3:0]in2;
  input [3:0]in3;
  input [3:0]in4;
  input [3:0]in5;
  input [3:0]in6;
  input [3:0]in7;
  output seg0;
  output seg1;
  output seg2;
  output seg3;
  output seg4;
  output seg5;
  output seg6;
  output dp;
  output [7:0]an;
endmodule
