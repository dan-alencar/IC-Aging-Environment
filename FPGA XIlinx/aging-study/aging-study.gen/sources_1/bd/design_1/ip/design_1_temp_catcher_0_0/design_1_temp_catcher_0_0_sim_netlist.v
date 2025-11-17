// Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
// Copyright 2022-2024 Advanced Micro Devices, Inc. All Rights Reserved.
// --------------------------------------------------------------------------------
// Tool Version: Vivado v.2024.2 (lin64) Build 5239630 Fri Nov 08 22:34:34 MST 2024
// Date        : Mon Mar 31 17:08:15 2025
// Host        : mirai-note running 64-bit Arch Linux
// Command     : write_verilog -force -mode funcsim
//               /home/mirai/Documentos/Projects/projeto_marco/Aging-main/vivado_project/aging-study/aging-study.gen/sources_1/bd/design_1/ip/design_1_temp_catcher_0_0/design_1_temp_catcher_0_0_sim_netlist.v
// Design      : design_1_temp_catcher_0_0
// Purpose     : This verilog netlist is a functional simulation representation of the design and should not be modified
//               or synthesized. This netlist cannot be used for SDF annotated simulation.
// Device      : xc7a100tcsg324-1
// --------------------------------------------------------------------------------
`timescale 1 ps / 1 ps

(* CHECK_LICENSE_TYPE = "design_1_temp_catcher_0_0,temp_catcher,{}" *) (* DowngradeIPIdentifiedWarnings = "yes" *) (* IP_DEFINITION_SOURCE = "module_ref" *) 
(* X_CORE_INFO = "temp_catcher,Vivado 2024.2" *) 
(* NotValidForBitStream *)
module design_1_temp_catcher_0_0
   (clk,
    reset,
    drdy,
    do_data,
    daddr,
    den,
    temp,
    vccint);
  (* X_INTERFACE_INFO = "xilinx.com:signal:clock:1.0 clk CLK" *) (* X_INTERFACE_MODE = "slave" *) (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME clk, ASSOCIATED_RESET reset, FREQ_HZ 100000000, FREQ_TOLERANCE_HZ 0, PHASE 0.0, CLK_DOMAIN design_1_CLK100MHZ, INSERT_VIP 0" *) input clk;
  (* X_INTERFACE_INFO = "xilinx.com:signal:reset:1.0 reset RST" *) (* X_INTERFACE_MODE = "slave" *) (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME reset, POLARITY ACTIVE_LOW, INSERT_VIP 0" *) input reset;
  input drdy;
  input [15:0]do_data;
  output [6:0]daddr;
  output den;
  output [20:0]temp;
  output [20:0]vccint;

  wire \<const0> ;
  wire clk;
  wire [0:0]\^daddr ;
  wire den;
  wire [15:0]do_data;
  wire drdy;
  wire inst_n_1;
  wire inst_n_25;
  wire inst_n_3;
  wire inst_n_4;
  wire p_0_out__0_n_100;
  wire p_0_out__0_n_101;
  wire p_0_out__0_n_102;
  wire p_0_out__0_n_103;
  wire p_0_out__0_n_104;
  wire p_0_out__0_n_105;
  wire p_0_out__0_n_82;
  wire p_0_out__0_n_83;
  wire p_0_out__0_n_84;
  wire p_0_out__0_n_85;
  wire p_0_out__0_n_86;
  wire p_0_out__0_n_87;
  wire p_0_out__0_n_88;
  wire p_0_out__0_n_89;
  wire p_0_out__0_n_90;
  wire p_0_out__0_n_91;
  wire p_0_out__0_n_92;
  wire p_0_out__0_n_93;
  wire p_0_out__0_n_94;
  wire p_0_out__0_n_95;
  wire p_0_out__0_n_96;
  wire p_0_out__0_n_97;
  wire p_0_out__0_n_98;
  wire p_0_out__0_n_99;
  wire [30:12]p_0_out__1;
  wire p_0_out_n_100;
  wire p_0_out_n_101;
  wire p_0_out_n_102;
  wire p_0_out_n_103;
  wire p_0_out_n_104;
  wire p_0_out_n_105;
  wire p_0_out_n_94;
  wire p_0_out_n_95;
  wire p_0_out_n_96;
  wire p_0_out_n_97;
  wire p_0_out_n_98;
  wire p_0_out_n_99;
  wire placeholder;
  wire reset;
  wire [20:0]\^temp ;
  wire \temp[16]_INST_0_i_6_n_0 ;
  wire [11:0]\^vccint ;
  wire \vccint[11]_INST_0_i_1_n_0 ;
  wire NLW_p_0_out_CARRYCASCOUT_UNCONNECTED;
  wire NLW_p_0_out_MULTSIGNOUT_UNCONNECTED;
  wire NLW_p_0_out_OVERFLOW_UNCONNECTED;
  wire NLW_p_0_out_PATTERNBDETECT_UNCONNECTED;
  wire NLW_p_0_out_PATTERNDETECT_UNCONNECTED;
  wire NLW_p_0_out_UNDERFLOW_UNCONNECTED;
  wire [29:0]NLW_p_0_out_ACOUT_UNCONNECTED;
  wire [17:0]NLW_p_0_out_BCOUT_UNCONNECTED;
  wire [3:0]NLW_p_0_out_CARRYOUT_UNCONNECTED;
  wire [47:31]NLW_p_0_out_P_UNCONNECTED;
  wire [47:0]NLW_p_0_out_PCOUT_UNCONNECTED;
  wire NLW_p_0_out__0_CARRYCASCOUT_UNCONNECTED;
  wire NLW_p_0_out__0_MULTSIGNOUT_UNCONNECTED;
  wire NLW_p_0_out__0_OVERFLOW_UNCONNECTED;
  wire NLW_p_0_out__0_PATTERNBDETECT_UNCONNECTED;
  wire NLW_p_0_out__0_PATTERNDETECT_UNCONNECTED;
  wire NLW_p_0_out__0_UNDERFLOW_UNCONNECTED;
  wire [29:0]NLW_p_0_out__0_ACOUT_UNCONNECTED;
  wire [17:0]NLW_p_0_out__0_BCOUT_UNCONNECTED;
  wire [3:0]NLW_p_0_out__0_CARRYOUT_UNCONNECTED;
  wire [47:24]NLW_p_0_out__0_P_UNCONNECTED;
  wire [47:0]NLW_p_0_out__0_PCOUT_UNCONNECTED;

  assign daddr[6] = \<const0> ;
  assign daddr[5] = \<const0> ;
  assign daddr[4] = \<const0> ;
  assign daddr[3] = \<const0> ;
  assign daddr[2] = \<const0> ;
  assign daddr[1] = \<const0> ;
  assign daddr[0] = \^daddr [0];
  assign temp[20] = \^temp [20];
  assign temp[19] = \^temp [20];
  assign temp[18:0] = \^temp [18:0];
  assign vccint[20] = \<const0> ;
  assign vccint[19] = \<const0> ;
  assign vccint[18] = \<const0> ;
  assign vccint[17] = \<const0> ;
  assign vccint[16] = \<const0> ;
  assign vccint[15] = \<const0> ;
  assign vccint[14] = \<const0> ;
  assign vccint[13] = \<const0> ;
  assign vccint[12] = \<const0> ;
  assign vccint[11:0] = \^vccint [11:0];
  GND GND
       (.G(\<const0> ));
  design_1_temp_catcher_0_0_temp_catcher inst
       (.\FSM_sequential_state_reg[0]_0 (inst_n_25),
        .\FSM_sequential_state_reg[1]_0 (inst_n_3),
        .P(p_0_out__1),
        .clk(clk),
        .daddr(\^daddr ),
        .den(den),
        .drdy(drdy),
        .drdy_0(inst_n_4),
        .placeholder(placeholder),
        .reset(reset),
        .reset_0(inst_n_1),
        .temp({\^temp [20],\^temp [18:0]}),
        .\temp[16]_INST_0_i_6 (\temp[16]_INST_0_i_6_n_0 ),
        .\vccint[11]_INST_0_i_1 (\vccint[11]_INST_0_i_1_n_0 ));
  (* METHODOLOGY_DRC_VIOS = "{SYNTH-12 {cell *THIS*}}" *) 
  DSP48E1 #(
    .ACASCREG(0),
    .ADREG(1),
    .ALUMODEREG(0),
    .AREG(0),
    .AUTORESET_PATDET("NO_RESET"),
    .A_INPUT("DIRECT"),
    .BCASCREG(0),
    .BREG(0),
    .B_INPUT("DIRECT"),
    .CARRYINREG(0),
    .CARRYINSELREG(0),
    .CREG(1),
    .DREG(1),
    .INMODEREG(0),
    .MASK(48'h3FFFFFFFFFFF),
    .MREG(0),
    .OPMODEREG(0),
    .PATTERN(48'h000000000000),
    .PREG(1),
    .SEL_MASK("MASK"),
    .SEL_PATTERN("PATTERN"),
    .USE_DPORT("FALSE"),
    .USE_MULT("MULTIPLY"),
    .USE_PATTERN_DETECT("NO_PATDET"),
    .USE_SIMD("ONE48")) 
    p_0_out
       (.A({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b1,1'b1,1'b1,1'b1,1'b0,1'b1,1'b1,1'b0,1'b0,1'b0,1'b0,1'b1,1'b0,1'b1,1'b0,1'b0,1'b1,1'b1,1'b1}),
        .ACIN({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .ACOUT(NLW_p_0_out_ACOUT_UNCONNECTED[29:0]),
        .ALUMODE({1'b0,1'b0,1'b0,1'b0}),
        .B({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,do_data[15:4]}),
        .BCIN({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .BCOUT(NLW_p_0_out_BCOUT_UNCONNECTED[17:0]),
        .C({1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1}),
        .CARRYCASCIN(1'b0),
        .CARRYCASCOUT(NLW_p_0_out_CARRYCASCOUT_UNCONNECTED),
        .CARRYIN(1'b0),
        .CARRYINSEL({1'b0,1'b0,1'b0}),
        .CARRYOUT(NLW_p_0_out_CARRYOUT_UNCONNECTED[3:0]),
        .CEA1(1'b0),
        .CEA2(1'b0),
        .CEAD(1'b0),
        .CEALUMODE(1'b0),
        .CEB1(1'b0),
        .CEB2(1'b0),
        .CEC(1'b0),
        .CECARRYIN(1'b0),
        .CECTRL(1'b0),
        .CED(1'b0),
        .CEINMODE(1'b0),
        .CEM(1'b0),
        .CEP(inst_n_25),
        .CLK(clk),
        .D({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .INMODE({1'b0,1'b0,1'b0,1'b0,1'b0}),
        .MULTSIGNIN(1'b0),
        .MULTSIGNOUT(NLW_p_0_out_MULTSIGNOUT_UNCONNECTED),
        .OPMODE({1'b0,1'b0,1'b0,1'b0,1'b1,1'b0,1'b1}),
        .OVERFLOW(NLW_p_0_out_OVERFLOW_UNCONNECTED),
        .P({NLW_p_0_out_P_UNCONNECTED[47:31],p_0_out__1,p_0_out_n_94,p_0_out_n_95,p_0_out_n_96,p_0_out_n_97,p_0_out_n_98,p_0_out_n_99,p_0_out_n_100,p_0_out_n_101,p_0_out_n_102,p_0_out_n_103,p_0_out_n_104,p_0_out_n_105}),
        .PATTERNBDETECT(NLW_p_0_out_PATTERNBDETECT_UNCONNECTED),
        .PATTERNDETECT(NLW_p_0_out_PATTERNDETECT_UNCONNECTED),
        .PCIN({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .PCOUT(NLW_p_0_out_PCOUT_UNCONNECTED[47:0]),
        .RSTA(1'b0),
        .RSTALLCARRYIN(1'b0),
        .RSTALUMODE(1'b0),
        .RSTB(1'b0),
        .RSTC(1'b0),
        .RSTCTRL(1'b0),
        .RSTD(1'b0),
        .RSTINMODE(1'b0),
        .RSTM(1'b0),
        .RSTP(1'b0),
        .UNDERFLOW(NLW_p_0_out_UNDERFLOW_UNCONNECTED));
  (* METHODOLOGY_DRC_VIOS = "{SYNTH-12 {cell *THIS*}}" *) 
  DSP48E1 #(
    .ACASCREG(0),
    .ADREG(1),
    .ALUMODEREG(0),
    .AREG(0),
    .AUTORESET_PATDET("NO_RESET"),
    .A_INPUT("DIRECT"),
    .BCASCREG(0),
    .BREG(0),
    .B_INPUT("DIRECT"),
    .CARRYINREG(0),
    .CARRYINSELREG(0),
    .CREG(1),
    .DREG(1),
    .INMODEREG(0),
    .MASK(48'h3FFFFFFFFFFF),
    .MREG(0),
    .OPMODEREG(0),
    .PATTERN(48'h000000000000),
    .PREG(1),
    .SEL_MASK("MASK"),
    .SEL_PATTERN("PATTERN"),
    .USE_DPORT("FALSE"),
    .USE_MULT("MULTIPLY"),
    .USE_PATTERN_DETECT("NO_PATDET"),
    .USE_SIMD("ONE48")) 
    p_0_out__0
       (.A({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,do_data[15:4]}),
        .ACIN({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .ACOUT(NLW_p_0_out__0_ACOUT_UNCONNECTED[29:0]),
        .ALUMODE({1'b0,1'b0,1'b0,1'b0}),
        .B({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b1,1'b0,1'b1,1'b1,1'b1,1'b0,1'b1,1'b1,1'b1,1'b0,1'b0,1'b0}),
        .BCIN({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .BCOUT(NLW_p_0_out__0_BCOUT_UNCONNECTED[17:0]),
        .C({1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1}),
        .CARRYCASCIN(1'b0),
        .CARRYCASCOUT(NLW_p_0_out__0_CARRYCASCOUT_UNCONNECTED),
        .CARRYIN(1'b0),
        .CARRYINSEL({1'b0,1'b0,1'b0}),
        .CARRYOUT(NLW_p_0_out__0_CARRYOUT_UNCONNECTED[3:0]),
        .CEA1(1'b0),
        .CEA2(1'b0),
        .CEAD(1'b0),
        .CEALUMODE(1'b0),
        .CEB1(1'b0),
        .CEB2(1'b0),
        .CEC(1'b0),
        .CECARRYIN(1'b0),
        .CECTRL(1'b0),
        .CED(1'b0),
        .CEINMODE(1'b0),
        .CEM(1'b0),
        .CEP(placeholder),
        .CLK(clk),
        .D({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .INMODE({1'b0,1'b0,1'b0,1'b0,1'b0}),
        .MULTSIGNIN(1'b0),
        .MULTSIGNOUT(NLW_p_0_out__0_MULTSIGNOUT_UNCONNECTED),
        .OPMODE({1'b0,1'b0,1'b0,1'b0,1'b1,1'b0,1'b1}),
        .OVERFLOW(NLW_p_0_out__0_OVERFLOW_UNCONNECTED),
        .P({NLW_p_0_out__0_P_UNCONNECTED[47:24],p_0_out__0_n_82,p_0_out__0_n_83,p_0_out__0_n_84,p_0_out__0_n_85,p_0_out__0_n_86,p_0_out__0_n_87,p_0_out__0_n_88,p_0_out__0_n_89,p_0_out__0_n_90,p_0_out__0_n_91,p_0_out__0_n_92,p_0_out__0_n_93,p_0_out__0_n_94,p_0_out__0_n_95,p_0_out__0_n_96,p_0_out__0_n_97,p_0_out__0_n_98,p_0_out__0_n_99,p_0_out__0_n_100,p_0_out__0_n_101,p_0_out__0_n_102,p_0_out__0_n_103,p_0_out__0_n_104,p_0_out__0_n_105}),
        .PATTERNBDETECT(NLW_p_0_out__0_PATTERNBDETECT_UNCONNECTED),
        .PATTERNDETECT(NLW_p_0_out__0_PATTERNDETECT_UNCONNECTED),
        .PCIN({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .PCOUT(NLW_p_0_out__0_PCOUT_UNCONNECTED[47:0]),
        .RSTA(1'b0),
        .RSTALLCARRYIN(1'b0),
        .RSTALUMODE(1'b0),
        .RSTB(1'b0),
        .RSTC(1'b0),
        .RSTCTRL(1'b0),
        .RSTD(1'b0),
        .RSTINMODE(1'b0),
        .RSTM(1'b0),
        .RSTP(1'b0),
        .UNDERFLOW(NLW_p_0_out__0_UNDERFLOW_UNCONNECTED));
  FDCE \temp[16]_INST_0_i_6 
       (.C(clk),
        .CE(1'b1),
        .CLR(inst_n_1),
        .D(inst_n_3),
        .Q(\temp[16]_INST_0_i_6_n_0 ));
  LUT2 #(
    .INIT(4'h8)) 
    \vccint[0]_INST_0 
       (.I0(p_0_out__0_n_93),
        .I1(\vccint[11]_INST_0_i_1_n_0 ),
        .O(\^vccint [0]));
  LUT2 #(
    .INIT(4'h8)) 
    \vccint[10]_INST_0 
       (.I0(p_0_out__0_n_83),
        .I1(\vccint[11]_INST_0_i_1_n_0 ),
        .O(\^vccint [10]));
  LUT2 #(
    .INIT(4'h8)) 
    \vccint[11]_INST_0 
       (.I0(p_0_out__0_n_82),
        .I1(\vccint[11]_INST_0_i_1_n_0 ),
        .O(\^vccint [11]));
  FDCE \vccint[11]_INST_0_i_1 
       (.C(clk),
        .CE(1'b1),
        .CLR(inst_n_1),
        .D(inst_n_4),
        .Q(\vccint[11]_INST_0_i_1_n_0 ));
  LUT2 #(
    .INIT(4'h8)) 
    \vccint[1]_INST_0 
       (.I0(p_0_out__0_n_92),
        .I1(\vccint[11]_INST_0_i_1_n_0 ),
        .O(\^vccint [1]));
  LUT2 #(
    .INIT(4'h8)) 
    \vccint[2]_INST_0 
       (.I0(p_0_out__0_n_91),
        .I1(\vccint[11]_INST_0_i_1_n_0 ),
        .O(\^vccint [2]));
  LUT2 #(
    .INIT(4'h8)) 
    \vccint[3]_INST_0 
       (.I0(p_0_out__0_n_90),
        .I1(\vccint[11]_INST_0_i_1_n_0 ),
        .O(\^vccint [3]));
  LUT2 #(
    .INIT(4'h8)) 
    \vccint[4]_INST_0 
       (.I0(p_0_out__0_n_89),
        .I1(\vccint[11]_INST_0_i_1_n_0 ),
        .O(\^vccint [4]));
  LUT2 #(
    .INIT(4'h8)) 
    \vccint[5]_INST_0 
       (.I0(p_0_out__0_n_88),
        .I1(\vccint[11]_INST_0_i_1_n_0 ),
        .O(\^vccint [5]));
  LUT2 #(
    .INIT(4'h8)) 
    \vccint[6]_INST_0 
       (.I0(p_0_out__0_n_87),
        .I1(\vccint[11]_INST_0_i_1_n_0 ),
        .O(\^vccint [6]));
  LUT2 #(
    .INIT(4'h8)) 
    \vccint[7]_INST_0 
       (.I0(p_0_out__0_n_86),
        .I1(\vccint[11]_INST_0_i_1_n_0 ),
        .O(\^vccint [7]));
  LUT2 #(
    .INIT(4'h8)) 
    \vccint[8]_INST_0 
       (.I0(p_0_out__0_n_85),
        .I1(\vccint[11]_INST_0_i_1_n_0 ),
        .O(\^vccint [8]));
  LUT2 #(
    .INIT(4'h8)) 
    \vccint[9]_INST_0 
       (.I0(p_0_out__0_n_84),
        .I1(\vccint[11]_INST_0_i_1_n_0 ),
        .O(\^vccint [9]));
endmodule

(* ORIG_REF_NAME = "temp_catcher" *) 
module design_1_temp_catcher_0_0_temp_catcher
   (den,
    reset_0,
    daddr,
    \FSM_sequential_state_reg[1]_0 ,
    drdy_0,
    temp,
    \FSM_sequential_state_reg[0]_0 ,
    placeholder,
    clk,
    reset,
    drdy,
    \temp[16]_INST_0_i_6 ,
    \vccint[11]_INST_0_i_1 ,
    P);
  output den;
  output reset_0;
  output [0:0]daddr;
  output \FSM_sequential_state_reg[1]_0 ;
  output drdy_0;
  output [19:0]temp;
  output \FSM_sequential_state_reg[0]_0 ;
  output placeholder;
  input clk;
  input reset;
  input drdy;
  input \temp[16]_INST_0_i_6 ;
  input \vccint[11]_INST_0_i_1 ;
  input [18:0]P;

  wire \FSM_sequential_state[0]_i_1_n_0 ;
  wire \FSM_sequential_state[0]_i_2_n_0 ;
  wire \FSM_sequential_state[1]_i_1_n_0 ;
  wire \FSM_sequential_state_reg[0]_0 ;
  wire \FSM_sequential_state_reg[1]_0 ;
  wire \FSM_sequential_state_reg_n_0_[1] ;
  wire [18:0]P;
  wire clk;
  wire [0:0]daddr;
  wire \daddr[0]_i_1_n_0 ;
  wire den;
  wire den_i_1_n_0;
  wire drdy;
  wire drdy_0;
  wire placeholder;
  wire reset;
  wire reset_0;
  wire [6:0]sel0;
  wire [0:0]state;
  wire [19:0]temp;
  wire \temp[0]_INST_0_i_1_n_0 ;
  wire \temp[0]_INST_0_i_2_n_0 ;
  wire \temp[0]_INST_0_i_3_n_0 ;
  wire \temp[0]_INST_0_i_4_n_0 ;
  wire \temp[0]_INST_0_i_5_n_0 ;
  wire \temp[0]_INST_0_n_0 ;
  wire \temp[0]_INST_0_n_1 ;
  wire \temp[0]_INST_0_n_2 ;
  wire \temp[0]_INST_0_n_3 ;
  wire \temp[12]_INST_0_i_1_n_0 ;
  wire \temp[12]_INST_0_i_2_n_0 ;
  wire \temp[12]_INST_0_i_3_n_0 ;
  wire \temp[12]_INST_0_i_4_n_0 ;
  wire \temp[12]_INST_0_i_5_n_0 ;
  wire \temp[12]_INST_0_i_6_n_0 ;
  wire \temp[12]_INST_0_i_7_n_0 ;
  wire \temp[12]_INST_0_n_0 ;
  wire \temp[12]_INST_0_n_1 ;
  wire \temp[12]_INST_0_n_2 ;
  wire \temp[12]_INST_0_n_3 ;
  wire \temp[16]_INST_0_i_1_n_0 ;
  wire \temp[16]_INST_0_i_2_n_0 ;
  wire \temp[16]_INST_0_i_3_n_0 ;
  wire \temp[16]_INST_0_i_4_n_0 ;
  wire \temp[16]_INST_0_i_5_n_0 ;
  wire \temp[16]_INST_0_i_6 ;
  wire \temp[16]_INST_0_n_1 ;
  wire \temp[16]_INST_0_n_2 ;
  wire \temp[16]_INST_0_n_3 ;
  wire \temp[4]_INST_0_i_1_n_0 ;
  wire \temp[4]_INST_0_i_2_n_0 ;
  wire \temp[4]_INST_0_i_3_n_0 ;
  wire \temp[4]_INST_0_i_4_n_0 ;
  wire \temp[4]_INST_0_n_0 ;
  wire \temp[4]_INST_0_n_1 ;
  wire \temp[4]_INST_0_n_2 ;
  wire \temp[4]_INST_0_n_3 ;
  wire \temp[8]_INST_0_i_1_n_0 ;
  wire \temp[8]_INST_0_i_2_n_0 ;
  wire \temp[8]_INST_0_i_3_n_0 ;
  wire \temp[8]_INST_0_i_4_n_0 ;
  wire \temp[8]_INST_0_i_5_n_0 ;
  wire \temp[8]_INST_0_i_6_n_0 ;
  wire \temp[8]_INST_0_n_0 ;
  wire \temp[8]_INST_0_n_1 ;
  wire \temp[8]_INST_0_n_2 ;
  wire \temp[8]_INST_0_n_3 ;
  wire [5:0]timeout;
  wire \timeout[5]_i_1_n_0 ;
  wire \timeout[5]_i_3_n_0 ;
  wire \timeout[6]_i_1_n_0 ;
  wire \vccint[11]_INST_0_i_1 ;
  wire [3:3]\NLW_temp[16]_INST_0_CO_UNCONNECTED ;

  (* SOFT_HLUTNM = "soft_lutpair2" *) 
  LUT4 #(
    .INIT(16'h0BFF)) 
    \FSM_sequential_state[0]_i_1 
       (.I0(\FSM_sequential_state[0]_i_2_n_0 ),
        .I1(sel0[6]),
        .I2(drdy),
        .I3(state),
        .O(\FSM_sequential_state[0]_i_1_n_0 ));
  LUT6 #(
    .INIT(64'h7FFFFFFFFFFFFFFF)) 
    \FSM_sequential_state[0]_i_2 
       (.I0(sel0[4]),
        .I1(sel0[2]),
        .I2(sel0[0]),
        .I3(sel0[1]),
        .I4(sel0[3]),
        .I5(sel0[5]),
        .O(\FSM_sequential_state[0]_i_2_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair3" *) 
  LUT3 #(
    .INIT(8'h78)) 
    \FSM_sequential_state[1]_i_1 
       (.I0(state),
        .I1(drdy),
        .I2(\FSM_sequential_state_reg_n_0_[1] ),
        .O(\FSM_sequential_state[1]_i_1_n_0 ));
  (* FSM_ENCODED_STATES = "GET_TEMP:01,GET_VCC:11,ASK_VCC:10,ASK_TEMP:00" *) 
  FDCE \FSM_sequential_state_reg[0] 
       (.C(clk),
        .CE(1'b1),
        .CLR(reset_0),
        .D(\FSM_sequential_state[0]_i_1_n_0 ),
        .Q(state));
  (* FSM_ENCODED_STATES = "GET_TEMP:01,GET_VCC:11,ASK_VCC:10,ASK_TEMP:00" *) 
  FDCE \FSM_sequential_state_reg[1] 
       (.C(clk),
        .CE(1'b1),
        .CLR(reset_0),
        .D(\FSM_sequential_state[1]_i_1_n_0 ),
        .Q(\FSM_sequential_state_reg_n_0_[1] ));
  (* SOFT_HLUTNM = "soft_lutpair3" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \daddr[0]_i_1 
       (.I0(daddr),
        .I1(state),
        .I2(\FSM_sequential_state_reg_n_0_[1] ),
        .O(\daddr[0]_i_1_n_0 ));
  LUT1 #(
    .INIT(2'h1)) 
    \daddr[0]_i_2 
       (.I0(reset),
        .O(reset_0));
  FDCE \daddr_reg[0] 
       (.C(clk),
        .CE(1'b1),
        .CLR(reset_0),
        .D(\daddr[0]_i_1_n_0 ),
        .Q(daddr));
  LUT1 #(
    .INIT(2'h1)) 
    den_i_1
       (.I0(state),
        .O(den_i_1_n_0));
  FDPE den_reg
       (.C(clk),
        .CE(1'b1),
        .D(den_i_1_n_0),
        .PRE(reset_0),
        .Q(den));
  LUT3 #(
    .INIT(8'h80)) 
    p_0_out__0_i_1
       (.I0(\FSM_sequential_state_reg_n_0_[1] ),
        .I1(state),
        .I2(drdy),
        .O(placeholder));
  LUT3 #(
    .INIT(8'h08)) 
    p_0_out_i_1
       (.I0(state),
        .I1(drdy),
        .I2(\FSM_sequential_state_reg_n_0_[1] ),
        .O(\FSM_sequential_state_reg[0]_0 ));
  CARRY4 \temp[0]_INST_0 
       (.CI(1'b0),
        .CO({\temp[0]_INST_0_n_0 ,\temp[0]_INST_0_n_1 ,\temp[0]_INST_0_n_2 ,\temp[0]_INST_0_n_3 }),
        .CYINIT(1'b0),
        .DI({1'b0,1'b0,\temp[0]_INST_0_i_1_n_0 ,1'b0}),
        .O(temp[3:0]),
        .S({\temp[0]_INST_0_i_2_n_0 ,\temp[0]_INST_0_i_3_n_0 ,\temp[0]_INST_0_i_4_n_0 ,\temp[0]_INST_0_i_5_n_0 }));
  LUT2 #(
    .INIT(4'h8)) 
    \temp[0]_INST_0_i_1 
       (.I0(P[1]),
        .I1(\temp[16]_INST_0_i_6 ),
        .O(\temp[0]_INST_0_i_1_n_0 ));
  LUT2 #(
    .INIT(4'h8)) 
    \temp[0]_INST_0_i_2 
       (.I0(P[3]),
        .I1(\temp[16]_INST_0_i_6 ),
        .O(\temp[0]_INST_0_i_2_n_0 ));
  LUT2 #(
    .INIT(4'h8)) 
    \temp[0]_INST_0_i_3 
       (.I0(P[2]),
        .I1(\temp[16]_INST_0_i_6 ),
        .O(\temp[0]_INST_0_i_3_n_0 ));
  LUT2 #(
    .INIT(4'h7)) 
    \temp[0]_INST_0_i_4 
       (.I0(\temp[16]_INST_0_i_6 ),
        .I1(P[1]),
        .O(\temp[0]_INST_0_i_4_n_0 ));
  LUT2 #(
    .INIT(4'h8)) 
    \temp[0]_INST_0_i_5 
       (.I0(P[0]),
        .I1(\temp[16]_INST_0_i_6 ),
        .O(\temp[0]_INST_0_i_5_n_0 ));
  CARRY4 \temp[12]_INST_0 
       (.CI(\temp[8]_INST_0_n_0 ),
        .CO({\temp[12]_INST_0_n_0 ,\temp[12]_INST_0_n_1 ,\temp[12]_INST_0_n_2 ,\temp[12]_INST_0_n_3 }),
        .CYINIT(1'b0),
        .DI({\temp[12]_INST_0_i_1_n_0 ,\temp[12]_INST_0_i_2_n_0 ,1'b0,\temp[12]_INST_0_i_3_n_0 }),
        .O(temp[15:12]),
        .S({\temp[12]_INST_0_i_4_n_0 ,\temp[12]_INST_0_i_5_n_0 ,\temp[12]_INST_0_i_6_n_0 ,\temp[12]_INST_0_i_7_n_0 }));
  LUT2 #(
    .INIT(4'h8)) 
    \temp[12]_INST_0_i_1 
       (.I0(P[15]),
        .I1(\temp[16]_INST_0_i_6 ),
        .O(\temp[12]_INST_0_i_1_n_0 ));
  LUT2 #(
    .INIT(4'h8)) 
    \temp[12]_INST_0_i_2 
       (.I0(P[14]),
        .I1(\temp[16]_INST_0_i_6 ),
        .O(\temp[12]_INST_0_i_2_n_0 ));
  LUT2 #(
    .INIT(4'h8)) 
    \temp[12]_INST_0_i_3 
       (.I0(P[12]),
        .I1(\temp[16]_INST_0_i_6 ),
        .O(\temp[12]_INST_0_i_3_n_0 ));
  LUT2 #(
    .INIT(4'h7)) 
    \temp[12]_INST_0_i_4 
       (.I0(\temp[16]_INST_0_i_6 ),
        .I1(P[15]),
        .O(\temp[12]_INST_0_i_4_n_0 ));
  LUT2 #(
    .INIT(4'h7)) 
    \temp[12]_INST_0_i_5 
       (.I0(\temp[16]_INST_0_i_6 ),
        .I1(P[14]),
        .O(\temp[12]_INST_0_i_5_n_0 ));
  LUT2 #(
    .INIT(4'h8)) 
    \temp[12]_INST_0_i_6 
       (.I0(P[13]),
        .I1(\temp[16]_INST_0_i_6 ),
        .O(\temp[12]_INST_0_i_6_n_0 ));
  LUT2 #(
    .INIT(4'h7)) 
    \temp[12]_INST_0_i_7 
       (.I0(\temp[16]_INST_0_i_6 ),
        .I1(P[12]),
        .O(\temp[12]_INST_0_i_7_n_0 ));
  CARRY4 \temp[16]_INST_0 
       (.CI(\temp[12]_INST_0_n_0 ),
        .CO({\NLW_temp[16]_INST_0_CO_UNCONNECTED [3],\temp[16]_INST_0_n_1 ,\temp[16]_INST_0_n_2 ,\temp[16]_INST_0_n_3 }),
        .CYINIT(1'b0),
        .DI({1'b0,1'b0,\temp[16]_INST_0_i_1_n_0 ,\temp[16]_INST_0_i_2_n_0 }),
        .O(temp[19:16]),
        .S({1'b1,\temp[16]_INST_0_i_3_n_0 ,\temp[16]_INST_0_i_4_n_0 ,\temp[16]_INST_0_i_5_n_0 }));
  LUT2 #(
    .INIT(4'h8)) 
    \temp[16]_INST_0_i_1 
       (.I0(P[17]),
        .I1(\temp[16]_INST_0_i_6 ),
        .O(\temp[16]_INST_0_i_1_n_0 ));
  LUT2 #(
    .INIT(4'h8)) 
    \temp[16]_INST_0_i_2 
       (.I0(P[16]),
        .I1(\temp[16]_INST_0_i_6 ),
        .O(\temp[16]_INST_0_i_2_n_0 ));
  LUT2 #(
    .INIT(4'h8)) 
    \temp[16]_INST_0_i_3 
       (.I0(P[18]),
        .I1(\temp[16]_INST_0_i_6 ),
        .O(\temp[16]_INST_0_i_3_n_0 ));
  LUT2 #(
    .INIT(4'h7)) 
    \temp[16]_INST_0_i_4 
       (.I0(\temp[16]_INST_0_i_6 ),
        .I1(P[17]),
        .O(\temp[16]_INST_0_i_4_n_0 ));
  LUT2 #(
    .INIT(4'h7)) 
    \temp[16]_INST_0_i_5 
       (.I0(\temp[16]_INST_0_i_6 ),
        .I1(P[16]),
        .O(\temp[16]_INST_0_i_5_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair1" *) 
  LUT4 #(
    .INIT(16'hFF40)) 
    \temp[16]_INST_0_i_7 
       (.I0(\FSM_sequential_state_reg_n_0_[1] ),
        .I1(drdy),
        .I2(state),
        .I3(\temp[16]_INST_0_i_6 ),
        .O(\FSM_sequential_state_reg[1]_0 ));
  CARRY4 \temp[4]_INST_0 
       (.CI(\temp[0]_INST_0_n_0 ),
        .CO({\temp[4]_INST_0_n_0 ,\temp[4]_INST_0_n_1 ,\temp[4]_INST_0_n_2 ,\temp[4]_INST_0_n_3 }),
        .CYINIT(1'b0),
        .DI({1'b0,1'b0,1'b0,1'b0}),
        .O(temp[7:4]),
        .S({\temp[4]_INST_0_i_1_n_0 ,\temp[4]_INST_0_i_2_n_0 ,\temp[4]_INST_0_i_3_n_0 ,\temp[4]_INST_0_i_4_n_0 }));
  LUT2 #(
    .INIT(4'h8)) 
    \temp[4]_INST_0_i_1 
       (.I0(P[7]),
        .I1(\temp[16]_INST_0_i_6 ),
        .O(\temp[4]_INST_0_i_1_n_0 ));
  LUT2 #(
    .INIT(4'h8)) 
    \temp[4]_INST_0_i_2 
       (.I0(P[6]),
        .I1(\temp[16]_INST_0_i_6 ),
        .O(\temp[4]_INST_0_i_2_n_0 ));
  LUT2 #(
    .INIT(4'h8)) 
    \temp[4]_INST_0_i_3 
       (.I0(P[5]),
        .I1(\temp[16]_INST_0_i_6 ),
        .O(\temp[4]_INST_0_i_3_n_0 ));
  LUT2 #(
    .INIT(4'h8)) 
    \temp[4]_INST_0_i_4 
       (.I0(P[4]),
        .I1(\temp[16]_INST_0_i_6 ),
        .O(\temp[4]_INST_0_i_4_n_0 ));
  CARRY4 \temp[8]_INST_0 
       (.CI(\temp[4]_INST_0_n_0 ),
        .CO({\temp[8]_INST_0_n_0 ,\temp[8]_INST_0_n_1 ,\temp[8]_INST_0_n_2 ,\temp[8]_INST_0_n_3 }),
        .CYINIT(1'b0),
        .DI({1'b0,\temp[8]_INST_0_i_1_n_0 ,1'b0,\temp[8]_INST_0_i_2_n_0 }),
        .O(temp[11:8]),
        .S({\temp[8]_INST_0_i_3_n_0 ,\temp[8]_INST_0_i_4_n_0 ,\temp[8]_INST_0_i_5_n_0 ,\temp[8]_INST_0_i_6_n_0 }));
  LUT2 #(
    .INIT(4'h8)) 
    \temp[8]_INST_0_i_1 
       (.I0(P[10]),
        .I1(\temp[16]_INST_0_i_6 ),
        .O(\temp[8]_INST_0_i_1_n_0 ));
  LUT2 #(
    .INIT(4'h8)) 
    \temp[8]_INST_0_i_2 
       (.I0(P[8]),
        .I1(\temp[16]_INST_0_i_6 ),
        .O(\temp[8]_INST_0_i_2_n_0 ));
  LUT2 #(
    .INIT(4'h8)) 
    \temp[8]_INST_0_i_3 
       (.I0(P[11]),
        .I1(\temp[16]_INST_0_i_6 ),
        .O(\temp[8]_INST_0_i_3_n_0 ));
  LUT2 #(
    .INIT(4'h7)) 
    \temp[8]_INST_0_i_4 
       (.I0(\temp[16]_INST_0_i_6 ),
        .I1(P[10]),
        .O(\temp[8]_INST_0_i_4_n_0 ));
  LUT2 #(
    .INIT(4'h8)) 
    \temp[8]_INST_0_i_5 
       (.I0(P[9]),
        .I1(\temp[16]_INST_0_i_6 ),
        .O(\temp[8]_INST_0_i_5_n_0 ));
  LUT2 #(
    .INIT(4'h7)) 
    \temp[8]_INST_0_i_6 
       (.I0(\temp[16]_INST_0_i_6 ),
        .I1(P[8]),
        .O(\temp[8]_INST_0_i_6_n_0 ));
  LUT2 #(
    .INIT(4'h2)) 
    \timeout[0]_i_1 
       (.I0(state),
        .I1(sel0[0]),
        .O(timeout[0]));
  (* SOFT_HLUTNM = "soft_lutpair4" *) 
  LUT3 #(
    .INIT(8'h48)) 
    \timeout[1]_i_1 
       (.I0(sel0[0]),
        .I1(state),
        .I2(sel0[1]),
        .O(timeout[1]));
  (* SOFT_HLUTNM = "soft_lutpair0" *) 
  LUT4 #(
    .INIT(16'h7080)) 
    \timeout[2]_i_1 
       (.I0(sel0[0]),
        .I1(sel0[1]),
        .I2(state),
        .I3(sel0[2]),
        .O(timeout[2]));
  (* SOFT_HLUTNM = "soft_lutpair0" *) 
  LUT5 #(
    .INIT(32'h7F008000)) 
    \timeout[3]_i_1 
       (.I0(sel0[1]),
        .I1(sel0[0]),
        .I2(sel0[2]),
        .I3(state),
        .I4(sel0[3]),
        .O(timeout[3]));
  LUT6 #(
    .INIT(64'h7FFF000080000000)) 
    \timeout[4]_i_1 
       (.I0(sel0[2]),
        .I1(sel0[0]),
        .I2(sel0[1]),
        .I3(sel0[3]),
        .I4(state),
        .I5(sel0[4]),
        .O(timeout[4]));
  LUT3 #(
    .INIT(8'hDF)) 
    \timeout[5]_i_1 
       (.I0(sel0[6]),
        .I1(\FSM_sequential_state[0]_i_2_n_0 ),
        .I2(state),
        .O(\timeout[5]_i_1_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair4" *) 
  LUT3 #(
    .INIT(8'h84)) 
    \timeout[5]_i_2 
       (.I0(\timeout[5]_i_3_n_0 ),
        .I1(state),
        .I2(sel0[5]),
        .O(timeout[5]));
  LUT5 #(
    .INIT(32'h7FFFFFFF)) 
    \timeout[5]_i_3 
       (.I0(sel0[3]),
        .I1(sel0[1]),
        .I2(sel0[0]),
        .I3(sel0[2]),
        .I4(sel0[4]),
        .O(\timeout[5]_i_3_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair2" *) 
  LUT3 #(
    .INIT(8'hB0)) 
    \timeout[6]_i_1 
       (.I0(sel0[6]),
        .I1(\FSM_sequential_state[0]_i_2_n_0 ),
        .I2(state),
        .O(\timeout[6]_i_1_n_0 ));
  FDCE \timeout_reg[0] 
       (.C(clk),
        .CE(\timeout[5]_i_1_n_0 ),
        .CLR(reset_0),
        .D(timeout[0]),
        .Q(sel0[0]));
  FDCE \timeout_reg[1] 
       (.C(clk),
        .CE(\timeout[5]_i_1_n_0 ),
        .CLR(reset_0),
        .D(timeout[1]),
        .Q(sel0[1]));
  FDCE \timeout_reg[2] 
       (.C(clk),
        .CE(\timeout[5]_i_1_n_0 ),
        .CLR(reset_0),
        .D(timeout[2]),
        .Q(sel0[2]));
  FDCE \timeout_reg[3] 
       (.C(clk),
        .CE(\timeout[5]_i_1_n_0 ),
        .CLR(reset_0),
        .D(timeout[3]),
        .Q(sel0[3]));
  FDCE \timeout_reg[4] 
       (.C(clk),
        .CE(\timeout[5]_i_1_n_0 ),
        .CLR(reset_0),
        .D(timeout[4]),
        .Q(sel0[4]));
  FDCE \timeout_reg[5] 
       (.C(clk),
        .CE(\timeout[5]_i_1_n_0 ),
        .CLR(reset_0),
        .D(timeout[5]),
        .Q(sel0[5]));
  FDCE \timeout_reg[6] 
       (.C(clk),
        .CE(1'b1),
        .CLR(reset_0),
        .D(\timeout[6]_i_1_n_0 ),
        .Q(sel0[6]));
  (* SOFT_HLUTNM = "soft_lutpair1" *) 
  LUT4 #(
    .INIT(16'hFF80)) 
    \vccint[11]_INST_0_i_2 
       (.I0(drdy),
        .I1(state),
        .I2(\FSM_sequential_state_reg_n_0_[1] ),
        .I3(\vccint[11]_INST_0_i_1 ),
        .O(drdy_0));
endmodule
`ifndef GLBL
`define GLBL
`timescale  1 ps / 1 ps

module glbl ();

    parameter ROC_WIDTH = 100000;
    parameter TOC_WIDTH = 0;
    parameter GRES_WIDTH = 10000;
    parameter GRES_START = 10000;

//--------   STARTUP Globals --------------
    wire GSR;
    wire GTS;
    wire GWE;
    wire PRLD;
    wire GRESTORE;
    tri1 p_up_tmp;
    tri (weak1, strong0) PLL_LOCKG = p_up_tmp;

    wire PROGB_GLBL;
    wire CCLKO_GLBL;
    wire FCSBO_GLBL;
    wire [3:0] DO_GLBL;
    wire [3:0] DI_GLBL;
   
    reg GSR_int;
    reg GTS_int;
    reg PRLD_int;
    reg GRESTORE_int;

//--------   JTAG Globals --------------
    wire JTAG_TDO_GLBL;
    wire JTAG_TCK_GLBL;
    wire JTAG_TDI_GLBL;
    wire JTAG_TMS_GLBL;
    wire JTAG_TRST_GLBL;

    reg JTAG_CAPTURE_GLBL;
    reg JTAG_RESET_GLBL;
    reg JTAG_SHIFT_GLBL;
    reg JTAG_UPDATE_GLBL;
    reg JTAG_RUNTEST_GLBL;

    reg JTAG_SEL1_GLBL = 0;
    reg JTAG_SEL2_GLBL = 0 ;
    reg JTAG_SEL3_GLBL = 0;
    reg JTAG_SEL4_GLBL = 0;

    reg JTAG_USER_TDO1_GLBL = 1'bz;
    reg JTAG_USER_TDO2_GLBL = 1'bz;
    reg JTAG_USER_TDO3_GLBL = 1'bz;
    reg JTAG_USER_TDO4_GLBL = 1'bz;

    assign (strong1, weak0) GSR = GSR_int;
    assign (strong1, weak0) GTS = GTS_int;
    assign (weak1, weak0) PRLD = PRLD_int;
    assign (strong1, weak0) GRESTORE = GRESTORE_int;

    initial begin
	GSR_int = 1'b1;
	PRLD_int = 1'b1;
	#(ROC_WIDTH)
	GSR_int = 1'b0;
	PRLD_int = 1'b0;
    end

    initial begin
	GTS_int = 1'b1;
	#(TOC_WIDTH)
	GTS_int = 1'b0;
    end

    initial begin 
	GRESTORE_int = 1'b0;
	#(GRES_START);
	GRESTORE_int = 1'b1;
	#(GRES_WIDTH);
	GRESTORE_int = 1'b0;
    end

endmodule
`endif
