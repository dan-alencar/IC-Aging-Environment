// Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
// Copyright 2022-2024 Advanced Micro Devices, Inc. All Rights Reserved.
// --------------------------------------------------------------------------------
// Tool Version: Vivado v.2024.2 (lin64) Build 5239630 Fri Nov 08 22:34:34 MST 2024
// Date        : Fri Apr 25 14:18:17 2025
// Host        : alisson.lesc.ufc.br running 64-bit unknown
// Command     : write_verilog -force -mode synth_stub
//               /home/alisson/Downloads/aging_mirai_tensao/Aging-dynamic/vivado_project/aging-study/aging-study.gen/sources_1/bd/design_1/ip/design_1_controller_controller_0_0/design_1_controller_controller_0_0_stub.v
// Design      : design_1_controller_controller_0_0
// Purpose     : Stub declaration of top-level module interface
// Device      : xc7a100tcsg324-1
// --------------------------------------------------------------------------------

// This empty module with port declaration file causes synthesis tools to infer a black box for IP.
// The synthesis directives are for Synopsys Synplify support to prevent IO buffer insertion.
// Please paste the declaration into a Verilog source file or add the file as an additional source.
(* CHECK_LICENSE_TYPE = "design_1_controller_controller_0_0,controller_controller,{}" *) (* CORE_GENERATION_INFO = "design_1_controller_controller_0_0,controller_controller,{x_ipProduct=Vivado 2024.2,x_ipVendor=xilinx.com,x_ipLibrary=module_ref,x_ipName=controller_controller,x_ipVersion=1.0,x_ipCoreRevision=1,x_ipLanguage=VERILOG,x_ipSimLanguage=MIXED}" *) (* DowngradeIPIdentifiedWarnings = "yes" *) 
(* IP_DEFINITION_SOURCE = "module_ref" *) (* X_CORE_INFO = "controller_controller,Vivado 2024.2" *) 
module design_1_controller_controller_0_0(clk, reset, alarm, psdone, display_value, change, 
  psincdec, send, psen)
/* synthesis syn_black_box black_box_pad_pin="reset,alarm,display_value[15:0],change,psincdec,send,psen" */
/* synthesis syn_force_seq_prim="clk" */
/* synthesis syn_force_seq_prim="psdone" */;
  (* X_INTERFACE_INFO = "xilinx.com:signal:clock:1.0 clk CLK" *) (* X_INTERFACE_MODE = "slave" *) (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME clk, ASSOCIATED_RESET reset, FREQ_HZ 100000000, FREQ_TOLERANCE_HZ 0, PHASE 0.0, CLK_DOMAIN /clk_wiz_0_clk_out1, INSERT_VIP 0" *) input clk /* synthesis syn_isclock = 1 */;
  (* X_INTERFACE_INFO = "xilinx.com:signal:reset:1.0 reset RST" *) (* X_INTERFACE_MODE = "slave" *) (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME reset, POLARITY ACTIVE_LOW, INSERT_VIP 0" *) input reset;
  input alarm;
  input psdone /* synthesis syn_isclock = 1 */;
  output [15:0]display_value;
  output change;
  output psincdec;
  output send;
  output psen;
endmodule
