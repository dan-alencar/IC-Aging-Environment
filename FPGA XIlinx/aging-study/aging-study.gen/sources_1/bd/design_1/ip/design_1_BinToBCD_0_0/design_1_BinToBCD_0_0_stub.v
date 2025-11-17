// Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
// Copyright 2022-2024 Advanced Micro Devices, Inc. All Rights Reserved.
// --------------------------------------------------------------------------------
// Tool Version: Vivado v.2024.2 (lin64) Build 5239630 Fri Nov 08 22:34:34 MST 2024
// Date        : Wed Feb  5 19:11:33 2025
// Host        : pop-os running 64-bit Pop!_OS 22.04 LTS
// Command     : write_verilog -force -mode synth_stub
//               /home/mirai/Documents/Projects/Aging-main/vivado_project/aging-study/aging-study.gen/sources_1/bd/design_1/ip/design_1_BinToBCD_0_0/design_1_BinToBCD_0_0_stub.v
// Design      : design_1_BinToBCD_0_0
// Purpose     : Stub declaration of top-level module interface
// Device      : xc7a100tcsg324-1
// --------------------------------------------------------------------------------

// This empty module with port declaration file causes synthesis tools to infer a black box for IP.
// The synthesis directives are for Synopsys Synplify support to prevent IO buffer insertion.
// Please paste the declaration into a Verilog source file or add the file as an additional source.
(* CHECK_LICENSE_TYPE = "design_1_BinToBCD_0_0,BinToBCD,{}" *) (* CORE_GENERATION_INFO = "design_1_BinToBCD_0_0,BinToBCD,{x_ipProduct=Vivado 2024.2,x_ipVendor=xilinx.com,x_ipLibrary=module_ref,x_ipName=BinToBCD,x_ipVersion=1.0,x_ipCoreRevision=1,x_ipLanguage=VERILOG,x_ipSimLanguage=MIXED}" *) (* DowngradeIPIdentifiedWarnings = "yes" *) 
(* IP_DEFINITION_SOURCE = "module_ref" *) (* X_CORE_INFO = "BinToBCD,Vivado 2024.2" *) 
module design_1_BinToBCD_0_0(clk, bin, un, dec, cent, mil, bil, tril, quadr, quint)
/* synthesis syn_black_box black_box_pad_pin="bin[20:0],un[3:0],dec[3:0],cent[3:0],mil[3:0],bil[3:0],tril[3:0],quadr[3:0],quint[3:0]" */
/* synthesis syn_force_seq_prim="clk" */;
  (* X_INTERFACE_INFO = "xilinx.com:signal:clock:1.0 clk CLK" *) (* X_INTERFACE_MODE = "slave" *) (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME clk, FREQ_HZ 100000000, FREQ_TOLERANCE_HZ 0, PHASE 0.0, CLK_DOMAIN design_1_CLK100MHZ, INSERT_VIP 0" *) input clk /* synthesis syn_isclock = 1 */;
  input [20:0]bin;
  output [3:0]un;
  output [3:0]dec;
  output [3:0]cent;
  output [3:0]mil;
  output [3:0]bil;
  output [3:0]tril;
  output [3:0]quadr;
  output [3:0]quint;
endmodule
