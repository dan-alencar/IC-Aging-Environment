// Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
// Copyright 2022-2025 Advanced Micro Devices, Inc. All Rights Reserved.
// --------------------------------------------------------------------------------
// Tool Version: Vivado v.2025.1 (lin64) Build 6140274 Wed May 21 22:58:25 MDT 2025
// Date        : Mon Nov 17 18:48:17 2025
// Host        : dan-alencar running 64-bit Linux Mint 22.1
// Command     : write_verilog -force -mode synth_stub -rename_top design_1_util_vector_logic_0_1 -prefix
//               design_1_util_vector_logic_0_1_ design_1_util_vector_logic_0_0_stub.v
// Design      : design_1_util_vector_logic_0_0
// Purpose     : Stub declaration of top-level module interface
// Device      : xc7a100tcsg324-1
// --------------------------------------------------------------------------------

// This empty module with port declaration file causes synthesis tools to infer a black box for IP.
// The synthesis directives are for Synopsys Synplify support to prevent IO buffer insertion.
// Please paste the declaration into a Verilog source file or add the file as an additional source.
(* CHECK_LICENSE_TYPE = "design_1_util_vector_logic_0_0,util_vector_logic_v2_0_5_util_vector_logic,{}" *) (* CORE_GENERATION_INFO = "design_1_util_vector_logic_0_0,util_vector_logic_v2_0_5_util_vector_logic,{x_ipProduct=Vivado 2025.1,x_ipVendor=xilinx.com,x_ipLibrary=ip,x_ipName=util_vector_logic,x_ipVersion=2.0,x_ipCoreRevision=5,x_ipLanguage=VERILOG,x_ipSimLanguage=MIXED,C_OPERATION=not,C_SIZE=1}" *) (* DowngradeIPIdentifiedWarnings = "yes" *) 
(* X_CORE_INFO = "util_vector_logic_v2_0_5_util_vector_logic,Vivado 2025.1" *) 
module design_1_util_vector_logic_0_1(Op1, Res)
/* synthesis syn_black_box black_box_pad_pin="Op1[0:0],Res[0:0]" */;
  input [0:0]Op1;
  output [0:0]Res;
endmodule
