// Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
// Copyright 2022-2024 Advanced Micro Devices, Inc. All Rights Reserved.
// --------------------------------------------------------------------------------
// Tool Version: Vivado v.2024.2 (lin64) Build 5239630 Fri Nov 08 22:34:34 MST 2024
// Date        : Fri Apr 25 14:25:14 2025
// Host        : alisson.lesc.ufc.br running 64-bit unknown
// Command     : write_verilog -force -mode synth_stub
//               /home/alisson/Downloads/aging_mirai_tensao/Aging-dynamic/vivado_project/aging-study/aging-study.gen/sources_1/bd/design_1/ip/design_1_modern_sensible_0_0/design_1_modern_sensible_0_0_stub.v
// Design      : design_1_modern_sensible_0_0
// Purpose     : Stub declaration of top-level module interface
// Device      : xc7a100tcsg324-1
// --------------------------------------------------------------------------------

// This empty module with port declaration file causes synthesis tools to infer a black box for IP.
// The synthesis directives are for Synopsys Synplify support to prevent IO buffer insertion.
// Please paste the declaration into a Verilog source file or add the file as an additional source.
(* CHECK_LICENSE_TYPE = "design_1_modern_sensible_0_0,modern_sensible,{}" *) (* CORE_GENERATION_INFO = "design_1_modern_sensible_0_0,modern_sensible,{x_ipProduct=Vivado 2024.2,x_ipVendor=xilinx.com,x_ipLibrary=module_ref,x_ipName=modern_sensible,x_ipVersion=1.0,x_ipCoreRevision=1,x_ipLanguage=VERILOG,x_ipSimLanguage=MIXED}" *) (* DowngradeIPIdentifiedWarnings = "yes" *) 
(* IP_DEFINITION_SOURCE = "module_ref" *) (* X_CORE_INFO = "modern_sensible,Vivado 2024.2" *) 
module design_1_modern_sensible_0_0(sclk, psclk, in_sensor, reset, clk_en, alarm, 
  ff1_out)
/* synthesis syn_black_box black_box_pad_pin="in_sensor,reset,alarm,ff1_out" */
/* synthesis syn_force_seq_prim="sclk" */
/* synthesis syn_force_seq_prim="psclk" */
/* synthesis syn_force_seq_prim="clk_en" */;
  input sclk /* synthesis syn_isclock = 1 */;
  input psclk /* synthesis syn_isclock = 1 */;
  input in_sensor;
  (* X_INTERFACE_INFO = "xilinx.com:signal:reset:1.0 reset RST" *) (* X_INTERFACE_MODE = "slave" *) (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME reset, POLARITY ACTIVE_LOW, INSERT_VIP 0" *) input reset;
  input clk_en /* synthesis syn_isclock = 1 */;
  output alarm;
  output ff1_out;
endmodule
