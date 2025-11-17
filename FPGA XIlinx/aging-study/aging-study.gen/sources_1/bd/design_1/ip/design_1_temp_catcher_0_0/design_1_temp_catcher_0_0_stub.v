// Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
// Copyright 2022-2024 Advanced Micro Devices, Inc. All Rights Reserved.
// --------------------------------------------------------------------------------
// Tool Version: Vivado v.2024.2 (lin64) Build 5239630 Fri Nov 08 22:34:34 MST 2024
// Date        : Mon Mar 31 17:08:15 2025
// Host        : mirai-note running 64-bit Arch Linux
// Command     : write_verilog -force -mode synth_stub
//               /home/mirai/Documentos/Projects/projeto_marco/Aging-main/vivado_project/aging-study/aging-study.gen/sources_1/bd/design_1/ip/design_1_temp_catcher_0_0/design_1_temp_catcher_0_0_stub.v
// Design      : design_1_temp_catcher_0_0
// Purpose     : Stub declaration of top-level module interface
// Device      : xc7a100tcsg324-1
// --------------------------------------------------------------------------------

// This empty module with port declaration file causes synthesis tools to infer a black box for IP.
// The synthesis directives are for Synopsys Synplify support to prevent IO buffer insertion.
// Please paste the declaration into a Verilog source file or add the file as an additional source.
(* CHECK_LICENSE_TYPE = "design_1_temp_catcher_0_0,temp_catcher,{}" *) (* CORE_GENERATION_INFO = "design_1_temp_catcher_0_0,temp_catcher,{x_ipProduct=Vivado 2024.2,x_ipVendor=xilinx.com,x_ipLibrary=module_ref,x_ipName=temp_catcher,x_ipVersion=1.0,x_ipCoreRevision=1,x_ipLanguage=VERILOG,x_ipSimLanguage=MIXED,ASK_TEMP=00,GET_TEMP=01,ASK_VCC=10,GET_VCC=11}" *) (* DowngradeIPIdentifiedWarnings = "yes" *) 
(* IP_DEFINITION_SOURCE = "module_ref" *) (* X_CORE_INFO = "temp_catcher,Vivado 2024.2" *) 
module design_1_temp_catcher_0_0(clk, reset, drdy, do_data, daddr, den, temp, vccint)
/* synthesis syn_black_box black_box_pad_pin="reset,drdy,do_data[15:0],daddr[6:0],den,temp[20:0],vccint[20:0]" */
/* synthesis syn_force_seq_prim="clk" */;
  (* X_INTERFACE_INFO = "xilinx.com:signal:clock:1.0 clk CLK" *) (* X_INTERFACE_MODE = "slave" *) (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME clk, ASSOCIATED_RESET reset, FREQ_HZ 100000000, FREQ_TOLERANCE_HZ 0, PHASE 0.0, CLK_DOMAIN design_1_CLK100MHZ, INSERT_VIP 0" *) input clk /* synthesis syn_isclock = 1 */;
  (* X_INTERFACE_INFO = "xilinx.com:signal:reset:1.0 reset RST" *) (* X_INTERFACE_MODE = "slave" *) (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME reset, POLARITY ACTIVE_LOW, INSERT_VIP 0" *) input reset;
  input drdy;
  input [15:0]do_data;
  output [6:0]daddr;
  output den;
  output [20:0]temp;
  output [20:0]vccint;
endmodule
