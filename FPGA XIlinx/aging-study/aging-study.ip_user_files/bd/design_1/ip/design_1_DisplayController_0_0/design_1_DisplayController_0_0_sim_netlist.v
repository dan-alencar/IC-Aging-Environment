// Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
// Copyright 2022-2024 Advanced Micro Devices, Inc. All Rights Reserved.
// --------------------------------------------------------------------------------
// Tool Version: Vivado v.2024.2 (lin64) Build 5239630 Fri Nov 08 22:34:34 MST 2024
// Date        : Wed Feb  5 19:11:24 2025
// Host        : pop-os running 64-bit Pop!_OS 22.04 LTS
// Command     : write_verilog -force -mode funcsim
//               /home/mirai/Documents/Projects/Aging-main/vivado_project/aging-study/aging-study.gen/sources_1/bd/design_1/ip/design_1_DisplayController_0_0/design_1_DisplayController_0_0_sim_netlist.v
// Design      : design_1_DisplayController_0_0
// Purpose     : This verilog netlist is a functional simulation representation of the design and should not be modified
//               or synthesized. This netlist cannot be used for SDF annotated simulation.
// Device      : xc7a100tcsg324-1
// --------------------------------------------------------------------------------
`timescale 1 ps / 1 ps

(* CHECK_LICENSE_TYPE = "design_1_DisplayController_0_0,DisplayController,{}" *) (* DowngradeIPIdentifiedWarnings = "yes" *) (* IP_DEFINITION_SOURCE = "module_ref" *) 
(* X_CORE_INFO = "DisplayController,Vivado 2024.2" *) 
(* NotValidForBitStream *)
module design_1_DisplayController_0_0
   (clk,
    reset,
    in0,
    in1,
    in2,
    in3,
    in4,
    in5,
    in6,
    in7,
    seg0,
    seg1,
    seg2,
    seg3,
    seg4,
    seg5,
    seg6,
    dp,
    an);
  (* X_INTERFACE_INFO = "xilinx.com:signal:clock:1.0 clk CLK" *) (* X_INTERFACE_MODE = "slave" *) (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME clk, ASSOCIATED_RESET reset, FREQ_HZ 100000000, FREQ_TOLERANCE_HZ 0, PHASE 0.0, CLK_DOMAIN design_1_CLK100MHZ, INSERT_VIP 0" *) input clk;
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

  wire \<const1> ;
  wire [7:0]an;
  wire clk;
  wire [3:0]in0;
  wire [3:0]in1;
  wire [3:0]in2;
  wire [3:0]in3;
  wire [3:0]in4;
  wire [3:0]in5;
  wire [3:0]in6;
  wire [3:0]in7;
  wire reset;
  wire seg0;
  wire seg1;
  wire seg2;
  wire seg3;
  wire seg4;
  wire seg5;
  wire seg6;

  assign dp = \<const1> ;
  VCC VCC
       (.P(\<const1> ));
  design_1_DisplayController_0_0_DisplayController inst
       (.an(an),
        .clk(clk),
        .in0(in0),
        .in1(in1),
        .in2(in2),
        .in3(in3),
        .in4(in4),
        .in5(in5),
        .in6(in6),
        .in7(in7),
        .reset(reset),
        .seg0(seg0),
        .seg1(seg1),
        .seg2(seg2),
        .seg3(seg3),
        .seg4(seg4),
        .seg5(seg5),
        .seg6(seg6));
endmodule

(* ORIG_REF_NAME = "DisplayController" *) 
module design_1_DisplayController_0_0_DisplayController
   (seg4,
    seg2,
    seg3,
    seg5,
    seg6,
    seg0,
    seg1,
    an,
    clk,
    reset,
    in3,
    in2,
    in1,
    in0,
    in7,
    in6,
    in5,
    in4);
  output seg4;
  output seg2;
  output seg3;
  output seg5;
  output seg6;
  output seg0;
  output seg1;
  output [7:0]an;
  input clk;
  input reset;
  input [3:0]in3;
  input [3:0]in2;
  input [3:0]in1;
  input [3:0]in0;
  input [3:0]in7;
  input [3:0]in6;
  input [3:0]in5;
  input [3:0]in4;

  wire [7:0]an;
  wire clk;
  wire \count[0]_i_2_n_0 ;
  wire \count_reg[0]_i_1_n_0 ;
  wire \count_reg[0]_i_1_n_1 ;
  wire \count_reg[0]_i_1_n_2 ;
  wire \count_reg[0]_i_1_n_3 ;
  wire \count_reg[0]_i_1_n_4 ;
  wire \count_reg[0]_i_1_n_5 ;
  wire \count_reg[0]_i_1_n_6 ;
  wire \count_reg[0]_i_1_n_7 ;
  wire \count_reg[12]_i_1_n_0 ;
  wire \count_reg[12]_i_1_n_1 ;
  wire \count_reg[12]_i_1_n_2 ;
  wire \count_reg[12]_i_1_n_3 ;
  wire \count_reg[12]_i_1_n_4 ;
  wire \count_reg[12]_i_1_n_5 ;
  wire \count_reg[12]_i_1_n_6 ;
  wire \count_reg[12]_i_1_n_7 ;
  wire \count_reg[16]_i_1_n_3 ;
  wire \count_reg[16]_i_1_n_6 ;
  wire \count_reg[16]_i_1_n_7 ;
  wire \count_reg[4]_i_1_n_0 ;
  wire \count_reg[4]_i_1_n_1 ;
  wire \count_reg[4]_i_1_n_2 ;
  wire \count_reg[4]_i_1_n_3 ;
  wire \count_reg[4]_i_1_n_4 ;
  wire \count_reg[4]_i_1_n_5 ;
  wire \count_reg[4]_i_1_n_6 ;
  wire \count_reg[4]_i_1_n_7 ;
  wire \count_reg[8]_i_1_n_0 ;
  wire \count_reg[8]_i_1_n_1 ;
  wire \count_reg[8]_i_1_n_2 ;
  wire \count_reg[8]_i_1_n_3 ;
  wire \count_reg[8]_i_1_n_4 ;
  wire \count_reg[8]_i_1_n_5 ;
  wire \count_reg[8]_i_1_n_6 ;
  wire \count_reg[8]_i_1_n_7 ;
  wire \count_reg_n_0_[0] ;
  wire \count_reg_n_0_[10] ;
  wire \count_reg_n_0_[11] ;
  wire \count_reg_n_0_[12] ;
  wire \count_reg_n_0_[13] ;
  wire \count_reg_n_0_[14] ;
  wire \count_reg_n_0_[1] ;
  wire \count_reg_n_0_[2] ;
  wire \count_reg_n_0_[3] ;
  wire \count_reg_n_0_[4] ;
  wire \count_reg_n_0_[5] ;
  wire \count_reg_n_0_[6] ;
  wire \count_reg_n_0_[7] ;
  wire \count_reg_n_0_[8] ;
  wire \count_reg_n_0_[9] ;
  wire [3:0]in0;
  wire [3:0]in1;
  wire [3:0]in2;
  wire [3:0]in3;
  wire [3:0]in4;
  wire [3:0]in5;
  wire [3:0]in6;
  wire [3:0]in7;
  wire [2:0]p_0_in;
  wire reset;
  wire seg0;
  wire seg0_INST_0_i_10_n_0;
  wire seg0_INST_0_i_11_n_0;
  wire seg0_INST_0_i_12_n_0;
  wire seg0_INST_0_i_5_n_0;
  wire seg0_INST_0_i_6_n_0;
  wire seg0_INST_0_i_7_n_0;
  wire seg0_INST_0_i_8_n_0;
  wire seg0_INST_0_i_9_n_0;
  wire seg1;
  wire seg2;
  wire seg3;
  wire seg4;
  wire seg5;
  wire seg6;
  wire [3:0]sel0;
  wire [3:1]\NLW_count_reg[16]_i_1_CO_UNCONNECTED ;
  wire [3:2]\NLW_count_reg[16]_i_1_O_UNCONNECTED ;

  (* SOFT_HLUTNM = "soft_lutpair3" *) 
  LUT3 #(
    .INIT(8'hFE)) 
    \an[0]_INST_0 
       (.I0(p_0_in[1]),
        .I1(p_0_in[2]),
        .I2(p_0_in[0]),
        .O(an[0]));
  (* SOFT_HLUTNM = "soft_lutpair3" *) 
  LUT3 #(
    .INIT(8'hEF)) 
    \an[1]_INST_0 
       (.I0(p_0_in[1]),
        .I1(p_0_in[2]),
        .I2(p_0_in[0]),
        .O(an[1]));
  (* SOFT_HLUTNM = "soft_lutpair4" *) 
  LUT3 #(
    .INIT(8'hEF)) 
    \an[2]_INST_0 
       (.I0(p_0_in[2]),
        .I1(p_0_in[0]),
        .I2(p_0_in[1]),
        .O(an[2]));
  (* SOFT_HLUTNM = "soft_lutpair4" *) 
  LUT3 #(
    .INIT(8'hF7)) 
    \an[3]_INST_0 
       (.I0(p_0_in[1]),
        .I1(p_0_in[0]),
        .I2(p_0_in[2]),
        .O(an[3]));
  (* SOFT_HLUTNM = "soft_lutpair5" *) 
  LUT3 #(
    .INIT(8'hEF)) 
    \an[4]_INST_0 
       (.I0(p_0_in[1]),
        .I1(p_0_in[0]),
        .I2(p_0_in[2]),
        .O(an[4]));
  (* SOFT_HLUTNM = "soft_lutpair5" *) 
  LUT3 #(
    .INIT(8'hF7)) 
    \an[5]_INST_0 
       (.I0(p_0_in[2]),
        .I1(p_0_in[0]),
        .I2(p_0_in[1]),
        .O(an[5]));
  (* SOFT_HLUTNM = "soft_lutpair6" *) 
  LUT3 #(
    .INIT(8'hF7)) 
    \an[6]_INST_0 
       (.I0(p_0_in[1]),
        .I1(p_0_in[2]),
        .I2(p_0_in[0]),
        .O(an[6]));
  (* SOFT_HLUTNM = "soft_lutpair6" *) 
  LUT3 #(
    .INIT(8'h7F)) 
    \an[7]_INST_0 
       (.I0(p_0_in[2]),
        .I1(p_0_in[0]),
        .I2(p_0_in[1]),
        .O(an[7]));
  LUT1 #(
    .INIT(2'h1)) 
    \count[0]_i_2 
       (.I0(\count_reg_n_0_[0] ),
        .O(\count[0]_i_2_n_0 ));
  FDCE #(
    .INIT(1'b0)) 
    \count_reg[0] 
       (.C(clk),
        .CE(1'b1),
        .CLR(reset),
        .D(\count_reg[0]_i_1_n_7 ),
        .Q(\count_reg_n_0_[0] ));
  (* ADDER_THRESHOLD = "11" *) 
  CARRY4 \count_reg[0]_i_1 
       (.CI(1'b0),
        .CO({\count_reg[0]_i_1_n_0 ,\count_reg[0]_i_1_n_1 ,\count_reg[0]_i_1_n_2 ,\count_reg[0]_i_1_n_3 }),
        .CYINIT(1'b0),
        .DI({1'b0,1'b0,1'b0,1'b1}),
        .O({\count_reg[0]_i_1_n_4 ,\count_reg[0]_i_1_n_5 ,\count_reg[0]_i_1_n_6 ,\count_reg[0]_i_1_n_7 }),
        .S({\count_reg_n_0_[3] ,\count_reg_n_0_[2] ,\count_reg_n_0_[1] ,\count[0]_i_2_n_0 }));
  FDCE #(
    .INIT(1'b0)) 
    \count_reg[10] 
       (.C(clk),
        .CE(1'b1),
        .CLR(reset),
        .D(\count_reg[8]_i_1_n_5 ),
        .Q(\count_reg_n_0_[10] ));
  FDCE #(
    .INIT(1'b0)) 
    \count_reg[11] 
       (.C(clk),
        .CE(1'b1),
        .CLR(reset),
        .D(\count_reg[8]_i_1_n_4 ),
        .Q(\count_reg_n_0_[11] ));
  FDCE #(
    .INIT(1'b0)) 
    \count_reg[12] 
       (.C(clk),
        .CE(1'b1),
        .CLR(reset),
        .D(\count_reg[12]_i_1_n_7 ),
        .Q(\count_reg_n_0_[12] ));
  (* ADDER_THRESHOLD = "11" *) 
  CARRY4 \count_reg[12]_i_1 
       (.CI(\count_reg[8]_i_1_n_0 ),
        .CO({\count_reg[12]_i_1_n_0 ,\count_reg[12]_i_1_n_1 ,\count_reg[12]_i_1_n_2 ,\count_reg[12]_i_1_n_3 }),
        .CYINIT(1'b0),
        .DI({1'b0,1'b0,1'b0,1'b0}),
        .O({\count_reg[12]_i_1_n_4 ,\count_reg[12]_i_1_n_5 ,\count_reg[12]_i_1_n_6 ,\count_reg[12]_i_1_n_7 }),
        .S({p_0_in[0],\count_reg_n_0_[14] ,\count_reg_n_0_[13] ,\count_reg_n_0_[12] }));
  FDCE #(
    .INIT(1'b0)) 
    \count_reg[13] 
       (.C(clk),
        .CE(1'b1),
        .CLR(reset),
        .D(\count_reg[12]_i_1_n_6 ),
        .Q(\count_reg_n_0_[13] ));
  FDCE #(
    .INIT(1'b0)) 
    \count_reg[14] 
       (.C(clk),
        .CE(1'b1),
        .CLR(reset),
        .D(\count_reg[12]_i_1_n_5 ),
        .Q(\count_reg_n_0_[14] ));
  FDCE #(
    .INIT(1'b0)) 
    \count_reg[15] 
       (.C(clk),
        .CE(1'b1),
        .CLR(reset),
        .D(\count_reg[12]_i_1_n_4 ),
        .Q(p_0_in[0]));
  FDCE #(
    .INIT(1'b0)) 
    \count_reg[16] 
       (.C(clk),
        .CE(1'b1),
        .CLR(reset),
        .D(\count_reg[16]_i_1_n_7 ),
        .Q(p_0_in[1]));
  (* ADDER_THRESHOLD = "11" *) 
  CARRY4 \count_reg[16]_i_1 
       (.CI(\count_reg[12]_i_1_n_0 ),
        .CO({\NLW_count_reg[16]_i_1_CO_UNCONNECTED [3:1],\count_reg[16]_i_1_n_3 }),
        .CYINIT(1'b0),
        .DI({1'b0,1'b0,1'b0,1'b0}),
        .O({\NLW_count_reg[16]_i_1_O_UNCONNECTED [3:2],\count_reg[16]_i_1_n_6 ,\count_reg[16]_i_1_n_7 }),
        .S({1'b0,1'b0,p_0_in[2:1]}));
  FDCE #(
    .INIT(1'b0)) 
    \count_reg[17] 
       (.C(clk),
        .CE(1'b1),
        .CLR(reset),
        .D(\count_reg[16]_i_1_n_6 ),
        .Q(p_0_in[2]));
  FDCE #(
    .INIT(1'b0)) 
    \count_reg[1] 
       (.C(clk),
        .CE(1'b1),
        .CLR(reset),
        .D(\count_reg[0]_i_1_n_6 ),
        .Q(\count_reg_n_0_[1] ));
  FDCE #(
    .INIT(1'b0)) 
    \count_reg[2] 
       (.C(clk),
        .CE(1'b1),
        .CLR(reset),
        .D(\count_reg[0]_i_1_n_5 ),
        .Q(\count_reg_n_0_[2] ));
  FDCE #(
    .INIT(1'b0)) 
    \count_reg[3] 
       (.C(clk),
        .CE(1'b1),
        .CLR(reset),
        .D(\count_reg[0]_i_1_n_4 ),
        .Q(\count_reg_n_0_[3] ));
  FDCE #(
    .INIT(1'b0)) 
    \count_reg[4] 
       (.C(clk),
        .CE(1'b1),
        .CLR(reset),
        .D(\count_reg[4]_i_1_n_7 ),
        .Q(\count_reg_n_0_[4] ));
  (* ADDER_THRESHOLD = "11" *) 
  CARRY4 \count_reg[4]_i_1 
       (.CI(\count_reg[0]_i_1_n_0 ),
        .CO({\count_reg[4]_i_1_n_0 ,\count_reg[4]_i_1_n_1 ,\count_reg[4]_i_1_n_2 ,\count_reg[4]_i_1_n_3 }),
        .CYINIT(1'b0),
        .DI({1'b0,1'b0,1'b0,1'b0}),
        .O({\count_reg[4]_i_1_n_4 ,\count_reg[4]_i_1_n_5 ,\count_reg[4]_i_1_n_6 ,\count_reg[4]_i_1_n_7 }),
        .S({\count_reg_n_0_[7] ,\count_reg_n_0_[6] ,\count_reg_n_0_[5] ,\count_reg_n_0_[4] }));
  FDCE #(
    .INIT(1'b0)) 
    \count_reg[5] 
       (.C(clk),
        .CE(1'b1),
        .CLR(reset),
        .D(\count_reg[4]_i_1_n_6 ),
        .Q(\count_reg_n_0_[5] ));
  FDCE #(
    .INIT(1'b0)) 
    \count_reg[6] 
       (.C(clk),
        .CE(1'b1),
        .CLR(reset),
        .D(\count_reg[4]_i_1_n_5 ),
        .Q(\count_reg_n_0_[6] ));
  FDCE #(
    .INIT(1'b0)) 
    \count_reg[7] 
       (.C(clk),
        .CE(1'b1),
        .CLR(reset),
        .D(\count_reg[4]_i_1_n_4 ),
        .Q(\count_reg_n_0_[7] ));
  FDCE #(
    .INIT(1'b0)) 
    \count_reg[8] 
       (.C(clk),
        .CE(1'b1),
        .CLR(reset),
        .D(\count_reg[8]_i_1_n_7 ),
        .Q(\count_reg_n_0_[8] ));
  (* ADDER_THRESHOLD = "11" *) 
  CARRY4 \count_reg[8]_i_1 
       (.CI(\count_reg[4]_i_1_n_0 ),
        .CO({\count_reg[8]_i_1_n_0 ,\count_reg[8]_i_1_n_1 ,\count_reg[8]_i_1_n_2 ,\count_reg[8]_i_1_n_3 }),
        .CYINIT(1'b0),
        .DI({1'b0,1'b0,1'b0,1'b0}),
        .O({\count_reg[8]_i_1_n_4 ,\count_reg[8]_i_1_n_5 ,\count_reg[8]_i_1_n_6 ,\count_reg[8]_i_1_n_7 }),
        .S({\count_reg_n_0_[11] ,\count_reg_n_0_[10] ,\count_reg_n_0_[9] ,\count_reg_n_0_[8] }));
  FDCE #(
    .INIT(1'b0)) 
    \count_reg[9] 
       (.C(clk),
        .CE(1'b1),
        .CLR(reset),
        .D(\count_reg[8]_i_1_n_6 ),
        .Q(\count_reg_n_0_[9] ));
  (* SOFT_HLUTNM = "soft_lutpair2" *) 
  LUT4 #(
    .INIT(16'h2094)) 
    seg0_INST_0
       (.I0(sel0[3]),
        .I1(sel0[2]),
        .I2(sel0[0]),
        .I3(sel0[1]),
        .O(seg0));
  MUXF7 seg0_INST_0_i_1
       (.I0(seg0_INST_0_i_5_n_0),
        .I1(seg0_INST_0_i_6_n_0),
        .O(sel0[3]),
        .S(p_0_in[2]));
  LUT6 #(
    .INIT(64'hAFA0CFCFAFA0C0C0)) 
    seg0_INST_0_i_10
       (.I0(in7[0]),
        .I1(in6[0]),
        .I2(p_0_in[1]),
        .I3(in5[0]),
        .I4(p_0_in[0]),
        .I5(in4[0]),
        .O(seg0_INST_0_i_10_n_0));
  LUT6 #(
    .INIT(64'hAFA0CFCFAFA0C0C0)) 
    seg0_INST_0_i_11
       (.I0(in3[1]),
        .I1(in2[1]),
        .I2(p_0_in[1]),
        .I3(in1[1]),
        .I4(p_0_in[0]),
        .I5(in0[1]),
        .O(seg0_INST_0_i_11_n_0));
  LUT6 #(
    .INIT(64'hAFA0CFCFAFA0C0C0)) 
    seg0_INST_0_i_12
       (.I0(in7[1]),
        .I1(in6[1]),
        .I2(p_0_in[1]),
        .I3(in5[1]),
        .I4(p_0_in[0]),
        .I5(in4[1]),
        .O(seg0_INST_0_i_12_n_0));
  MUXF7 seg0_INST_0_i_2
       (.I0(seg0_INST_0_i_7_n_0),
        .I1(seg0_INST_0_i_8_n_0),
        .O(sel0[2]),
        .S(p_0_in[2]));
  MUXF7 seg0_INST_0_i_3
       (.I0(seg0_INST_0_i_9_n_0),
        .I1(seg0_INST_0_i_10_n_0),
        .O(sel0[0]),
        .S(p_0_in[2]));
  MUXF7 seg0_INST_0_i_4
       (.I0(seg0_INST_0_i_11_n_0),
        .I1(seg0_INST_0_i_12_n_0),
        .O(sel0[1]),
        .S(p_0_in[2]));
  LUT6 #(
    .INIT(64'hAFA0CFCFAFA0C0C0)) 
    seg0_INST_0_i_5
       (.I0(in3[3]),
        .I1(in2[3]),
        .I2(p_0_in[1]),
        .I3(in1[3]),
        .I4(p_0_in[0]),
        .I5(in0[3]),
        .O(seg0_INST_0_i_5_n_0));
  LUT6 #(
    .INIT(64'hAFA0CFCFAFA0C0C0)) 
    seg0_INST_0_i_6
       (.I0(in7[3]),
        .I1(in6[3]),
        .I2(p_0_in[1]),
        .I3(in5[3]),
        .I4(p_0_in[0]),
        .I5(in4[3]),
        .O(seg0_INST_0_i_6_n_0));
  LUT6 #(
    .INIT(64'hAFA0CFCFAFA0C0C0)) 
    seg0_INST_0_i_7
       (.I0(in3[2]),
        .I1(in2[2]),
        .I2(p_0_in[1]),
        .I3(in1[2]),
        .I4(p_0_in[0]),
        .I5(in0[2]),
        .O(seg0_INST_0_i_7_n_0));
  LUT6 #(
    .INIT(64'hAFA0CFCFAFA0C0C0)) 
    seg0_INST_0_i_8
       (.I0(in7[2]),
        .I1(in6[2]),
        .I2(p_0_in[1]),
        .I3(in5[2]),
        .I4(p_0_in[0]),
        .I5(in4[2]),
        .O(seg0_INST_0_i_8_n_0));
  LUT6 #(
    .INIT(64'hAFA0CFCFAFA0C0C0)) 
    seg0_INST_0_i_9
       (.I0(in3[0]),
        .I1(in2[0]),
        .I2(p_0_in[1]),
        .I3(in1[0]),
        .I4(p_0_in[0]),
        .I5(in0[0]),
        .O(seg0_INST_0_i_9_n_0));
  LUT4 #(
    .INIT(16'hAC48)) 
    seg1_INST_0
       (.I0(sel0[3]),
        .I1(sel0[2]),
        .I2(sel0[0]),
        .I3(sel0[1]),
        .O(seg1));
  (* SOFT_HLUTNM = "soft_lutpair0" *) 
  LUT4 #(
    .INIT(16'hA210)) 
    seg2_INST_0
       (.I0(sel0[3]),
        .I1(sel0[0]),
        .I2(sel0[1]),
        .I3(sel0[2]),
        .O(seg2));
  (* SOFT_HLUTNM = "soft_lutpair1" *) 
  LUT4 #(
    .INIT(16'hC214)) 
    seg3_INST_0
       (.I0(sel0[3]),
        .I1(sel0[2]),
        .I2(sel0[0]),
        .I3(sel0[1]),
        .O(seg3));
  (* SOFT_HLUTNM = "soft_lutpair0" *) 
  LUT4 #(
    .INIT(16'h5710)) 
    seg4_INST_0
       (.I0(sel0[3]),
        .I1(sel0[1]),
        .I2(sel0[2]),
        .I3(sel0[0]),
        .O(seg4));
  (* SOFT_HLUTNM = "soft_lutpair1" *) 
  LUT4 #(
    .INIT(16'h5190)) 
    seg5_INST_0
       (.I0(sel0[3]),
        .I1(sel0[2]),
        .I2(sel0[0]),
        .I3(sel0[1]),
        .O(seg5));
  (* SOFT_HLUTNM = "soft_lutpair2" *) 
  LUT4 #(
    .INIT(16'h4025)) 
    seg6_INST_0
       (.I0(sel0[3]),
        .I1(sel0[0]),
        .I2(sel0[2]),
        .I3(sel0[1]),
        .O(seg6));
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
