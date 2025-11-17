// Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
// Copyright 2022-2024 Advanced Micro Devices, Inc. All Rights Reserved.
// --------------------------------------------------------------------------------
// Tool Version: Vivado v.2024.2 (lin64) Build 5239630 Fri Nov 08 22:34:34 MST 2024
// Date        : Wed Feb  5 19:11:33 2025
// Host        : pop-os running 64-bit Pop!_OS 22.04 LTS
// Command     : write_verilog -force -mode funcsim
//               /home/mirai/Documents/Projects/Aging-main/vivado_project/aging-study/aging-study.gen/sources_1/bd/design_1/ip/design_1_BinToBCD_0_0/design_1_BinToBCD_0_0_sim_netlist.v
// Design      : design_1_BinToBCD_0_0
// Purpose     : This verilog netlist is a functional simulation representation of the design and should not be modified
//               or synthesized. This netlist cannot be used for SDF annotated simulation.
// Device      : xc7a100tcsg324-1
// --------------------------------------------------------------------------------
`timescale 1 ps / 1 ps

(* CHECK_LICENSE_TYPE = "design_1_BinToBCD_0_0,BinToBCD,{}" *) (* DowngradeIPIdentifiedWarnings = "yes" *) (* IP_DEFINITION_SOURCE = "module_ref" *) 
(* X_CORE_INFO = "BinToBCD,Vivado 2024.2" *) 
(* NotValidForBitStream *)
module design_1_BinToBCD_0_0
   (clk,
    bin,
    un,
    dec,
    cent,
    mil,
    bil,
    tril,
    quadr,
    quint);
  (* X_INTERFACE_INFO = "xilinx.com:signal:clock:1.0 clk CLK" *) (* X_INTERFACE_MODE = "slave" *) (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME clk, FREQ_HZ 100000000, FREQ_TOLERANCE_HZ 0, PHASE 0.0, CLK_DOMAIN design_1_CLK100MHZ, INSERT_VIP 0" *) input clk;
  input [20:0]bin;
  output [3:0]un;
  output [3:0]dec;
  output [3:0]cent;
  output [3:0]mil;
  output [3:0]bil;
  output [3:0]tril;
  output [3:0]quadr;
  output [3:0]quint;

  wire \<const0> ;
  wire [3:0]bil;
  wire [20:0]bin;
  wire [3:0]cent;
  wire clk;
  wire [3:0]dec;
  wire [3:0]mil;
  wire [1:0]\^quadr ;
  wire [3:0]tril;
  wire [3:0]un;

  assign quadr[3] = \<const0> ;
  assign quadr[2] = \<const0> ;
  assign quadr[1:0] = \^quadr [1:0];
  assign quint[3] = \<const0> ;
  assign quint[2] = \<const0> ;
  assign quint[1] = \<const0> ;
  assign quint[0] = \<const0> ;
  GND GND
       (.G(\<const0> ));
  design_1_BinToBCD_0_0_BinToBCD inst
       (.bil(bil),
        .bin(bin[19:0]),
        .cent(cent),
        .clk(clk),
        .dec(dec),
        .mil(mil),
        .quadr(\^quadr ),
        .tril(tril),
        .un(un));
endmodule

(* ORIG_REF_NAME = "BinToBCD" *) 
module design_1_BinToBCD_0_0_BinToBCD
   (un,
    dec,
    cent,
    mil,
    bil,
    tril,
    quadr,
    clk,
    bin);
  output [3:0]un;
  output [3:0]dec;
  output [3:0]cent;
  output [3:0]mil;
  output [3:0]bil;
  output [3:0]tril;
  output [1:0]quadr;
  input clk;
  input [19:0]bin;

  wire [3:0]bil;
  wire \bil[3]_i_10_n_0 ;
  wire \bil[3]_i_11_n_0 ;
  wire \bil[3]_i_12_n_0 ;
  wire \bil[3]_i_13_n_0 ;
  wire \bil[3]_i_14_n_0 ;
  wire \bil[3]_i_15_n_0 ;
  wire \bil[3]_i_16_n_0 ;
  wire \bil[3]_i_17_n_0 ;
  wire \bil[3]_i_2_n_0 ;
  wire \bil[3]_i_3_n_0 ;
  wire \bil[3]_i_4_n_0 ;
  wire \bil[3]_i_5_n_0 ;
  wire \bil[3]_i_6_n_0 ;
  wire \bil[3]_i_7_n_0 ;
  wire \bil[3]_i_8_n_0 ;
  wire \bil[3]_i_9_n_0 ;
  wire [19:0]bin;
  wire [3:0]cent;
  wire \cent[3]_i_10_n_0 ;
  wire \cent[3]_i_11_n_0 ;
  wire \cent[3]_i_12_n_0 ;
  wire \cent[3]_i_13_n_0 ;
  wire \cent[3]_i_14_n_0 ;
  wire \cent[3]_i_15_n_0 ;
  wire \cent[3]_i_16_n_0 ;
  wire \cent[3]_i_17_n_0 ;
  wire \cent[3]_i_18_n_0 ;
  wire \cent[3]_i_19_n_0 ;
  wire \cent[3]_i_20_n_0 ;
  wire \cent[3]_i_21_n_0 ;
  wire \cent[3]_i_22_n_0 ;
  wire \cent[3]_i_23_n_0 ;
  wire \cent[3]_i_24_n_0 ;
  wire \cent[3]_i_2_n_0 ;
  wire \cent[3]_i_3_n_0 ;
  wire \cent[3]_i_4_n_0 ;
  wire \cent[3]_i_5_n_0 ;
  wire \cent[3]_i_6_n_0 ;
  wire \cent[3]_i_7_n_0 ;
  wire \cent[3]_i_8_n_0 ;
  wire \cent[3]_i_9_n_0 ;
  wire clk;
  wire [3:0]dec;
  wire \dec[3]_i_10_n_0 ;
  wire \dec[3]_i_11_n_0 ;
  wire \dec[3]_i_13_n_0 ;
  wire \dec[3]_i_14_n_0 ;
  wire \dec[3]_i_15_n_0 ;
  wire \dec[3]_i_16_n_0 ;
  wire \dec[3]_i_17_n_0 ;
  wire \dec[3]_i_18_n_0 ;
  wire \dec[3]_i_20_n_0 ;
  wire \dec[3]_i_22_n_0 ;
  wire \dec[3]_i_23_n_0 ;
  wire \dec[3]_i_24_n_0 ;
  wire \dec[3]_i_25_n_0 ;
  wire \dec[3]_i_2_n_0 ;
  wire \dec[3]_i_30_n_0 ;
  wire \dec[3]_i_3_n_0 ;
  wire \dec[3]_i_4_n_0 ;
  wire \dec[3]_i_5_n_0 ;
  wire \dec[3]_i_6_n_0 ;
  wire \dec[3]_i_7_n_0 ;
  wire \dec[3]_i_8_n_0 ;
  wire \dec[3]_i_9_n_0 ;
  wire [3:0]mil;
  wire \mil[3]_i_10_n_0 ;
  wire \mil[3]_i_11_n_0 ;
  wire \mil[3]_i_12_n_0 ;
  wire \mil[3]_i_13_n_0 ;
  wire \mil[3]_i_14_n_0 ;
  wire \mil[3]_i_15_n_0 ;
  wire \mil[3]_i_16_n_0 ;
  wire \mil[3]_i_17_n_0 ;
  wire \mil[3]_i_18_n_0 ;
  wire \mil[3]_i_19_n_0 ;
  wire \mil[3]_i_20_n_0 ;
  wire \mil[3]_i_21_n_0 ;
  wire \mil[3]_i_22_n_0 ;
  wire \mil[3]_i_23_n_0 ;
  wire \mil[3]_i_24_n_0 ;
  wire \mil[3]_i_25_n_0 ;
  wire \mil[3]_i_26_n_0 ;
  wire \mil[3]_i_27_n_0 ;
  wire \mil[3]_i_28_n_0 ;
  wire \mil[3]_i_29_n_0 ;
  wire \mil[3]_i_2_n_0 ;
  wire \mil[3]_i_30_n_0 ;
  wire \mil[3]_i_31_n_0 ;
  wire \mil[3]_i_32_n_0 ;
  wire \mil[3]_i_33_n_0 ;
  wire \mil[3]_i_36_n_0 ;
  wire \mil[3]_i_37_n_0 ;
  wire \mil[3]_i_38_n_0 ;
  wire \mil[3]_i_39_n_0 ;
  wire \mil[3]_i_3_n_0 ;
  wire \mil[3]_i_40_n_0 ;
  wire \mil[3]_i_41_n_0 ;
  wire \mil[3]_i_4_n_0 ;
  wire \mil[3]_i_5_n_0 ;
  wire \mil[3]_i_6_n_0 ;
  wire \mil[3]_i_7_n_0 ;
  wire \mil[3]_i_8_n_0 ;
  wire \mil[3]_i_9_n_0 ;
  wire [2:1]p_0_in__0;
  wire [2:2]p_0_in__11;
  wire [2:2]p_0_in__12;
  wire [2:2]p_0_in__13;
  wire [2:2]p_0_in__14;
  wire [2:2]p_0_in__2;
  wire [3:1]p_0_in__3;
  wire [2:1]p_0_in__5;
  wire [3:1]p_0_in__6;
  wire [2:1]p_0_in__8;
  wire [2:1]p_0_in__9;
  wire [3:1]p_0_out;
  wire [3:0]p_1_out;
  wire [3:0]p_2_out;
  wire [3:0]p_3_out;
  wire [3:0]p_4_out;
  wire [3:0]p_5_out;
  wire [1:0]p_6_out;
  wire [1:0]quadr;
  wire [3:0]tril;
  wire tril1;
  wire \tril[2]_i_2_n_0 ;
  wire \tril[2]_i_3_n_0 ;
  wire \tril[2]_i_4_n_0 ;
  wire \tril[2]_i_5_n_0 ;
  wire \tril[2]_i_6_n_0 ;
  wire \tril[2]_i_7_n_0 ;
  wire \tril[2]_i_8_n_0 ;
  wire \tril[3]_i_10_n_0 ;
  wire \tril[3]_i_11_n_0 ;
  wire \tril[3]_i_12_n_0 ;
  wire \tril[3]_i_13_n_0 ;
  wire \tril[3]_i_14_n_0 ;
  wire \tril[3]_i_15_n_0 ;
  wire \tril[3]_i_2_n_0 ;
  wire \tril[3]_i_3_n_0 ;
  wire \tril[3]_i_4_n_0 ;
  wire \tril[3]_i_5_n_0 ;
  wire \tril[3]_i_6_n_0 ;
  wire \tril[3]_i_8_n_0 ;
  wire \tril[3]_i_9_n_0 ;
  wire [3:0]un;
  wire \un[3]_i_10_n_0 ;
  wire \un[3]_i_3_n_0 ;
  wire \un[3]_i_4_n_0 ;
  wire \un[3]_i_5_n_0 ;
  wire \un[3]_i_8_n_0 ;

  LUT6 #(
    .INIT(64'h609F996600FF9F60)) 
    \bil[0]_i_1 
       (.I0(\mil[3]_i_2_n_0 ),
        .I1(\mil[3]_i_3_n_0 ),
        .I2(\mil[3]_i_4_n_0 ),
        .I3(\mil[3]_i_5_n_0 ),
        .I4(\mil[3]_i_6_n_0 ),
        .I5(\mil[3]_i_7_n_0 ),
        .O(p_4_out[0]));
  LUT6 #(
    .INIT(64'hA419941A62955686)) 
    \bil[1]_i_1 
       (.I0(\bil[3]_i_2_n_0 ),
        .I1(\bil[3]_i_3_n_0 ),
        .I2(\bil[3]_i_6_n_0 ),
        .I3(\bil[3]_i_5_n_0 ),
        .I4(\bil[3]_i_4_n_0 ),
        .I5(\bil[3]_i_7_n_0 ),
        .O(p_4_out[1]));
  LUT6 #(
    .INIT(64'h0D810643722EB89C)) 
    \bil[2]_i_1 
       (.I0(\bil[3]_i_2_n_0 ),
        .I1(\bil[3]_i_5_n_0 ),
        .I2(\bil[3]_i_3_n_0 ),
        .I3(\bil[3]_i_6_n_0 ),
        .I4(\bil[3]_i_4_n_0 ),
        .I5(\bil[3]_i_7_n_0 ),
        .O(p_4_out[2]));
  LUT6 #(
    .INIT(64'h0254152080314C08)) 
    \bil[3]_i_1 
       (.I0(\bil[3]_i_2_n_0 ),
        .I1(\bil[3]_i_3_n_0 ),
        .I2(\bil[3]_i_4_n_0 ),
        .I3(\bil[3]_i_5_n_0 ),
        .I4(\bil[3]_i_6_n_0 ),
        .I5(\bil[3]_i_7_n_0 ),
        .O(p_4_out[3]));
  LUT6 #(
    .INIT(64'h0E9336B0C8333C2C)) 
    \bil[3]_i_10 
       (.I0(\cent[3]_i_21_n_0 ),
        .I1(\mil[3]_i_23_n_0 ),
        .I2(\mil[3]_i_24_n_0 ),
        .I3(\mil[3]_i_25_n_0 ),
        .I4(\mil[3]_i_26_n_0 ),
        .I5(\mil[3]_i_20_n_0 ),
        .O(\bil[3]_i_10_n_0 ));
  LUT6 #(
    .INIT(64'hC03E03E0C0F803E0)) 
    \bil[3]_i_11 
       (.I0(\mil[3]_i_24_n_0 ),
        .I1(\bil[3]_i_16_n_0 ),
        .I2(\bil[3]_i_13_n_0 ),
        .I3(\bil[3]_i_14_n_0 ),
        .I4(\bil[3]_i_15_n_0 ),
        .I5(\bil[3]_i_12_n_0 ),
        .O(\bil[3]_i_11_n_0 ));
  LUT3 #(
    .INIT(8'hF6)) 
    \bil[3]_i_12 
       (.I0(\mil[3]_i_24_n_0 ),
        .I1(\mil[3]_i_25_n_0 ),
        .I2(\mil[3]_i_20_n_0 ),
        .O(\bil[3]_i_12_n_0 ));
  LUT3 #(
    .INIT(8'h78)) 
    \bil[3]_i_13 
       (.I0(\mil[3]_i_39_n_0 ),
        .I1(\bil[3]_i_17_n_0 ),
        .I2(\mil[3]_i_40_n_0 ),
        .O(\bil[3]_i_13_n_0 ));
  LUT6 #(
    .INIT(64'h0FC00FC00FC03F80)) 
    \bil[3]_i_14 
       (.I0(bin[14]),
        .I1(bin[17]),
        .I2(bin[18]),
        .I3(bin[19]),
        .I4(bin[16]),
        .I5(bin[15]),
        .O(\bil[3]_i_14_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair7" *) 
  LUT5 #(
    .INIT(32'hF000E000)) 
    \bil[3]_i_15 
       (.I0(bin[15]),
        .I1(bin[16]),
        .I2(bin[19]),
        .I3(bin[18]),
        .I4(bin[17]),
        .O(\bil[3]_i_15_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair5" *) 
  LUT5 #(
    .INIT(32'h9B32303C)) 
    \bil[3]_i_16 
       (.I0(\mil[3]_i_32_n_0 ),
        .I1(\mil[3]_i_39_n_0 ),
        .I2(\mil[3]_i_40_n_0 ),
        .I3(\mil[3]_i_37_n_0 ),
        .I4(\mil[3]_i_38_n_0 ),
        .O(\bil[3]_i_16_n_0 ));
  LUT6 #(
    .INIT(64'hBEBBBBBEEEEEEEEE)) 
    \bil[3]_i_17 
       (.I0(\mil[3]_i_38_n_0 ),
        .I1(p_0_in__3[3]),
        .I2(bin[13]),
        .I3(\mil[3]_i_36_n_0 ),
        .I4(bin[14]),
        .I5(p_0_in__3[2]),
        .O(\bil[3]_i_17_n_0 ));
  LUT6 #(
    .INIT(64'h0E9336B0C8333C2C)) 
    \bil[3]_i_2 
       (.I0(\mil[3]_i_7_n_0 ),
        .I1(\mil[3]_i_17_n_0 ),
        .I2(\mil[3]_i_11_n_0 ),
        .I3(\mil[3]_i_16_n_0 ),
        .I4(\mil[3]_i_18_n_0 ),
        .I5(\mil[3]_i_3_n_0 ),
        .O(\bil[3]_i_2_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \bil[3]_i_3 
       (.I0(\bil[3]_i_8_n_0 ),
        .I1(\tril[3]_i_5_n_0 ),
        .O(\bil[3]_i_3_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair10" *) 
  LUT4 #(
    .INIT(16'h581A)) 
    \bil[3]_i_4 
       (.I0(\tril[3]_i_4_n_0 ),
        .I1(\tril[3]_i_3_n_0 ),
        .I2(\tril[3]_i_2_n_0 ),
        .I3(\tril[3]_i_5_n_0 ),
        .O(\bil[3]_i_4_n_0 ));
  LUT3 #(
    .INIT(8'hF8)) 
    \bil[3]_i_5 
       (.I0(\bil[3]_i_4_n_0 ),
        .I1(\tril[2]_i_2_n_0 ),
        .I2(\tril[2]_i_3_n_0 ),
        .O(\bil[3]_i_5_n_0 ));
  LUT6 #(
    .INIT(64'h0E9336B0C8333C2C)) 
    \bil[3]_i_6 
       (.I0(\mil[3]_i_11_n_0 ),
        .I1(\bil[3]_i_9_n_0 ),
        .I2(\bil[3]_i_10_n_0 ),
        .I3(\tril[3]_i_2_n_0 ),
        .I4(\bil[3]_i_11_n_0 ),
        .I5(\mil[3]_i_9_n_0 ),
        .O(\bil[3]_i_6_n_0 ));
  LUT6 #(
    .INIT(64'h0E9336B0C8333C2C)) 
    \bil[3]_i_7 
       (.I0(\mil[3]_i_3_n_0 ),
        .I1(\mil[3]_i_8_n_0 ),
        .I2(\mil[3]_i_9_n_0 ),
        .I3(\tril[3]_i_5_n_0 ),
        .I4(\mil[3]_i_10_n_0 ),
        .I5(\mil[3]_i_11_n_0 ),
        .O(\bil[3]_i_7_n_0 ));
  LUT6 #(
    .INIT(64'h0FC00FC00FC03F80)) 
    \bil[3]_i_8 
       (.I0(\mil[3]_i_9_n_0 ),
        .I1(\tril[3]_i_9_n_0 ),
        .I2(\tril[3]_i_8_n_0 ),
        .I3(\tril[3]_i_10_n_0 ),
        .I4(\tril[3]_i_11_n_0 ),
        .I5(\bil[3]_i_10_n_0 ),
        .O(\bil[3]_i_8_n_0 ));
  LUT6 #(
    .INIT(64'h24CACD3005028F2C)) 
    \bil[3]_i_9 
       (.I0(\bil[3]_i_12_n_0 ),
        .I1(\bil[3]_i_13_n_0 ),
        .I2(\bil[3]_i_14_n_0 ),
        .I3(\bil[3]_i_15_n_0 ),
        .I4(\bil[3]_i_16_n_0 ),
        .I5(\mil[3]_i_24_n_0 ),
        .O(\bil[3]_i_9_n_0 ));
  FDRE #(
    .INIT(1'b0)) 
    \bil_reg[0] 
       (.C(clk),
        .CE(1'b1),
        .D(p_4_out[0]),
        .Q(bil[0]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \bil_reg[1] 
       (.C(clk),
        .CE(1'b1),
        .D(p_4_out[1]),
        .Q(bil[1]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \bil_reg[2] 
       (.C(clk),
        .CE(1'b1),
        .D(p_4_out[2]),
        .Q(bil[2]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \bil_reg[3] 
       (.C(clk),
        .CE(1'b1),
        .D(p_4_out[3]),
        .Q(bil[3]),
        .R(1'b0));
  LUT6 #(
    .INIT(64'h4D3AA17C4B3001EC)) 
    \cent[0]_i_1 
       (.I0(\dec[3]_i_2_n_0 ),
        .I1(\dec[3]_i_3_n_0 ),
        .I2(\dec[3]_i_4_n_0 ),
        .I3(\dec[3]_i_5_n_0 ),
        .I4(\dec[3]_i_6_n_0 ),
        .I5(\dec[3]_i_7_n_0 ),
        .O(p_2_out[0]));
  LUT6 #(
    .INIT(64'hA0C55A035B3005EC)) 
    \cent[1]_i_1 
       (.I0(\cent[3]_i_2_n_0 ),
        .I1(\cent[3]_i_3_n_0 ),
        .I2(\cent[3]_i_4_n_0 ),
        .I3(\cent[3]_i_5_n_0 ),
        .I4(\cent[3]_i_6_n_0 ),
        .I5(\cent[3]_i_7_n_0 ),
        .O(p_2_out[1]));
  LUT6 #(
    .INIT(64'h1995546642A5518A)) 
    \cent[2]_i_1 
       (.I0(\cent[3]_i_2_n_0 ),
        .I1(\cent[3]_i_3_n_0 ),
        .I2(\cent[3]_i_4_n_0 ),
        .I3(\cent[3]_i_5_n_0 ),
        .I4(\cent[3]_i_6_n_0 ),
        .I5(\cent[3]_i_7_n_0 ),
        .O(p_2_out[2]));
  LUT6 #(
    .INIT(64'h41200148070AA0D0)) 
    \cent[3]_i_1 
       (.I0(\cent[3]_i_2_n_0 ),
        .I1(\cent[3]_i_3_n_0 ),
        .I2(\cent[3]_i_4_n_0 ),
        .I3(\cent[3]_i_5_n_0 ),
        .I4(\cent[3]_i_6_n_0 ),
        .I5(\cent[3]_i_7_n_0 ),
        .O(p_2_out[3]));
  LUT6 #(
    .INIT(64'h0E9336B0C8333C2C)) 
    \cent[3]_i_10 
       (.I0(\dec[3]_i_9_n_0 ),
        .I1(\dec[3]_i_15_n_0 ),
        .I2(\dec[3]_i_16_n_0 ),
        .I3(\dec[3]_i_17_n_0 ),
        .I4(\dec[3]_i_18_n_0 ),
        .I5(\cent[3]_i_13_n_0 ),
        .O(\cent[3]_i_10_n_0 ));
  LUT6 #(
    .INIT(64'h0EB33EB0C83FFC2C)) 
    \cent[3]_i_11 
       (.I0(\cent[3]_i_10_n_0 ),
        .I1(\mil[3]_i_12_n_0 ),
        .I2(\mil[3]_i_13_n_0 ),
        .I3(\mil[3]_i_14_n_0 ),
        .I4(\mil[3]_i_15_n_0 ),
        .I5(\cent[3]_i_8_n_0 ),
        .O(\cent[3]_i_11_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair15" *) 
  LUT2 #(
    .INIT(4'h6)) 
    \cent[3]_i_12 
       (.I0(\dec[3]_i_17_n_0 ),
        .I1(\dec[3]_i_16_n_0 ),
        .O(\cent[3]_i_12_n_0 ));
  LUT6 #(
    .INIT(64'h33939333CC3636CC)) 
    \cent[3]_i_13 
       (.I0(bin[7]),
        .I1(p_0_in__8[2]),
        .I2(bin[8]),
        .I3(\cent[3]_i_24_n_0 ),
        .I4(bin[9]),
        .I5(\dec[3]_i_20_n_0 ),
        .O(\cent[3]_i_13_n_0 ));
  LUT6 #(
    .INIT(64'h3FB3B33FCCFEFECC)) 
    \cent[3]_i_14 
       (.I0(\cent[3]_i_13_n_0 ),
        .I1(\dec[3]_i_18_n_0 ),
        .I2(\dec[3]_i_16_n_0 ),
        .I3(\cent[3]_i_18_n_0 ),
        .I4(\cent[3]_i_19_n_0 ),
        .I5(\dec[3]_i_17_n_0 ),
        .O(\cent[3]_i_14_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair15" *) 
  LUT4 #(
    .INIT(16'h6966)) 
    \cent[3]_i_15 
       (.I0(\cent[3]_i_19_n_0 ),
        .I1(\cent[3]_i_18_n_0 ),
        .I2(\dec[3]_i_16_n_0 ),
        .I3(\dec[3]_i_17_n_0 ),
        .O(\cent[3]_i_15_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair13" *) 
  LUT2 #(
    .INIT(4'h6)) 
    \cent[3]_i_16 
       (.I0(\mil[3]_i_14_n_0 ),
        .I1(\mil[3]_i_13_n_0 ),
        .O(\cent[3]_i_16_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair13" *) 
  LUT4 #(
    .INIT(16'h6966)) 
    \cent[3]_i_17 
       (.I0(\cent[3]_i_21_n_0 ),
        .I1(\cent[3]_i_22_n_0 ),
        .I2(\mil[3]_i_13_n_0 ),
        .I3(\mil[3]_i_14_n_0 ),
        .O(\cent[3]_i_17_n_0 ));
  LUT6 #(
    .INIT(64'h0EB33EB0C83FFC2C)) 
    \cent[3]_i_18 
       (.I0(\cent[3]_i_19_n_0 ),
        .I1(\dec[3]_i_22_n_0 ),
        .I2(\dec[3]_i_23_n_0 ),
        .I3(\dec[3]_i_24_n_0 ),
        .I4(\dec[3]_i_25_n_0 ),
        .I5(\mil[3]_i_28_n_0 ),
        .O(\cent[3]_i_18_n_0 ));
  LUT6 #(
    .INIT(64'h0E9336B0C8333C2C)) 
    \cent[3]_i_19 
       (.I0(bin[9]),
        .I1(p_0_in__5[1]),
        .I2(bin[11]),
        .I3(\dec[3]_i_30_n_0 ),
        .I4(p_0_in__5[2]),
        .I5(bin[10]),
        .O(\cent[3]_i_19_n_0 ));
  LUT6 #(
    .INIT(64'h609F00FF99669F60)) 
    \cent[3]_i_2 
       (.I0(\dec[3]_i_8_n_0 ),
        .I1(\dec[3]_i_9_n_0 ),
        .I2(\dec[3]_i_4_n_0 ),
        .I3(\dec[3]_i_14_n_0 ),
        .I4(\dec[3]_i_10_n_0 ),
        .I5(\dec[3]_i_11_n_0 ),
        .O(\cent[3]_i_2_n_0 ));
  LUT6 #(
    .INIT(64'hA4255A9292A4495A)) 
    \cent[3]_i_20 
       (.I0(\mil[3]_i_20_n_0 ),
        .I1(\bil[3]_i_15_n_0 ),
        .I2(\bil[3]_i_14_n_0 ),
        .I3(\bil[3]_i_13_n_0 ),
        .I4(\bil[3]_i_16_n_0 ),
        .I5(\mil[3]_i_24_n_0 ),
        .O(\cent[3]_i_20_n_0 ));
  LUT6 #(
    .INIT(64'h0E9336B0C8333C2C)) 
    \cent[3]_i_21 
       (.I0(\cent[3]_i_19_n_0 ),
        .I1(\dec[3]_i_22_n_0 ),
        .I2(\dec[3]_i_23_n_0 ),
        .I3(\dec[3]_i_24_n_0 ),
        .I4(\dec[3]_i_25_n_0 ),
        .I5(\mil[3]_i_28_n_0 ),
        .O(\cent[3]_i_21_n_0 ));
  LUT6 #(
    .INIT(64'h0EB33EB0C83FFC2C)) 
    \cent[3]_i_22 
       (.I0(\cent[3]_i_21_n_0 ),
        .I1(\mil[3]_i_23_n_0 ),
        .I2(\mil[3]_i_24_n_0 ),
        .I3(\mil[3]_i_25_n_0 ),
        .I4(\mil[3]_i_26_n_0 ),
        .I5(\mil[3]_i_20_n_0 ),
        .O(\cent[3]_i_22_n_0 ));
  LUT6 #(
    .INIT(64'h92C3492CC3492C34)) 
    \cent[3]_i_23 
       (.I0(\bil[3]_i_16_n_0 ),
        .I1(\bil[3]_i_15_n_0 ),
        .I2(\bil[3]_i_13_n_0 ),
        .I3(\bil[3]_i_14_n_0 ),
        .I4(\mil[3]_i_24_n_0 ),
        .I5(\mil[3]_i_20_n_0 ),
        .O(\cent[3]_i_23_n_0 ));
  LUT6 #(
    .INIT(64'h0EB33EB0C83FFC2C)) 
    \cent[3]_i_24 
       (.I0(bin[9]),
        .I1(p_0_in__5[1]),
        .I2(bin[11]),
        .I3(\dec[3]_i_30_n_0 ),
        .I4(p_0_in__5[2]),
        .I5(bin[10]),
        .O(\cent[3]_i_24_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair12" *) 
  LUT4 #(
    .INIT(16'h6966)) 
    \cent[3]_i_3 
       (.I0(\cent[3]_i_8_n_0 ),
        .I1(\cent[3]_i_9_n_0 ),
        .I2(\cent[3]_i_10_n_0 ),
        .I3(\cent[3]_i_11_n_0 ),
        .O(\cent[3]_i_3_n_0 ));
  LUT6 #(
    .INIT(64'h0E9336B0C8333C2C)) 
    \cent[3]_i_4 
       (.I0(\dec[3]_i_10_n_0 ),
        .I1(\cent[3]_i_12_n_0 ),
        .I2(\cent[3]_i_13_n_0 ),
        .I3(\cent[3]_i_14_n_0 ),
        .I4(\cent[3]_i_15_n_0 ),
        .I5(\dec[3]_i_9_n_0 ),
        .O(\cent[3]_i_4_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair12" *) 
  LUT2 #(
    .INIT(4'h6)) 
    \cent[3]_i_5 
       (.I0(\cent[3]_i_11_n_0 ),
        .I1(\cent[3]_i_10_n_0 ),
        .O(\cent[3]_i_5_n_0 ));
  LUT6 #(
    .INIT(64'h0EB33EB0C83FFC2C)) 
    \cent[3]_i_6 
       (.I0(\cent[3]_i_4_n_0 ),
        .I1(\cent[3]_i_16_n_0 ),
        .I2(\cent[3]_i_8_n_0 ),
        .I3(\cent[3]_i_9_n_0 ),
        .I4(\cent[3]_i_17_n_0 ),
        .I5(\cent[3]_i_10_n_0 ),
        .O(\cent[3]_i_6_n_0 ));
  LUT5 #(
    .INIT(32'h933336CC)) 
    \cent[3]_i_7 
       (.I0(\dec[3]_i_2_n_0 ),
        .I1(\dec[3]_i_3_n_0 ),
        .I2(\dec[3]_i_4_n_0 ),
        .I3(\dec[3]_i_5_n_0 ),
        .I4(\dec[3]_i_6_n_0 ),
        .O(\cent[3]_i_7_n_0 ));
  LUT6 #(
    .INIT(64'h33939333CC3636CC)) 
    \cent[3]_i_8 
       (.I0(\cent[3]_i_13_n_0 ),
        .I1(\dec[3]_i_18_n_0 ),
        .I2(\dec[3]_i_16_n_0 ),
        .I3(\cent[3]_i_18_n_0 ),
        .I4(\cent[3]_i_19_n_0 ),
        .I5(\dec[3]_i_17_n_0 ),
        .O(\cent[3]_i_8_n_0 ));
  LUT6 #(
    .INIT(64'h0EB33EB0C83FFC2C)) 
    \cent[3]_i_9 
       (.I0(\cent[3]_i_8_n_0 ),
        .I1(\cent[3]_i_20_n_0 ),
        .I2(\cent[3]_i_21_n_0 ),
        .I3(\cent[3]_i_22_n_0 ),
        .I4(\cent[3]_i_23_n_0 ),
        .I5(\mil[3]_i_13_n_0 ),
        .O(\cent[3]_i_9_n_0 ));
  FDRE #(
    .INIT(1'b0)) 
    \cent_reg[0] 
       (.C(clk),
        .CE(1'b1),
        .D(p_2_out[0]),
        .Q(cent[0]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \cent_reg[1] 
       (.C(clk),
        .CE(1'b1),
        .D(p_2_out[1]),
        .Q(cent[1]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \cent_reg[2] 
       (.C(clk),
        .CE(1'b1),
        .D(p_2_out[2]),
        .Q(cent[2]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \cent_reg[3] 
       (.C(clk),
        .CE(1'b1),
        .D(p_2_out[3]),
        .Q(cent[3]),
        .R(1'b0));
  LUT6 #(
    .INIT(64'h3C93933C3C36363C)) 
    \dec[0]_i_1 
       (.I0(bin[1]),
        .I1(p_0_in__14),
        .I2(\un[3]_i_3_n_0 ),
        .I3(\un[3]_i_4_n_0 ),
        .I4(bin[3]),
        .I5(bin[2]),
        .O(p_1_out[0]));
  LUT6 #(
    .INIT(64'hA0C55A035B3005EC)) 
    \dec[1]_i_1 
       (.I0(\dec[3]_i_2_n_0 ),
        .I1(\dec[3]_i_3_n_0 ),
        .I2(\dec[3]_i_4_n_0 ),
        .I3(\dec[3]_i_5_n_0 ),
        .I4(\dec[3]_i_6_n_0 ),
        .I5(\dec[3]_i_7_n_0 ),
        .O(p_1_out[1]));
  LUT6 #(
    .INIT(64'h1995546642A5518A)) 
    \dec[2]_i_1 
       (.I0(\dec[3]_i_2_n_0 ),
        .I1(\dec[3]_i_3_n_0 ),
        .I2(\dec[3]_i_4_n_0 ),
        .I3(\dec[3]_i_5_n_0 ),
        .I4(\dec[3]_i_6_n_0 ),
        .I5(\dec[3]_i_7_n_0 ),
        .O(p_1_out[2]));
  LUT6 #(
    .INIT(64'h41200148070AA0D0)) 
    \dec[3]_i_1 
       (.I0(\dec[3]_i_2_n_0 ),
        .I1(\dec[3]_i_3_n_0 ),
        .I2(\dec[3]_i_4_n_0 ),
        .I3(\dec[3]_i_5_n_0 ),
        .I4(\dec[3]_i_6_n_0 ),
        .I5(\dec[3]_i_7_n_0 ),
        .O(p_1_out[3]));
  LUT6 #(
    .INIT(64'h0E9336B0C8333C2C)) 
    \dec[3]_i_10 
       (.I0(bin[5]),
        .I1(p_0_in__9[1]),
        .I2(bin[7]),
        .I3(\un[3]_i_10_n_0 ),
        .I4(p_0_in__9[2]),
        .I5(bin[6]),
        .O(\dec[3]_i_10_n_0 ));
  LUT6 #(
    .INIT(64'h0EB33EB0C83FFC2C)) 
    \dec[3]_i_11 
       (.I0(\dec[3]_i_10_n_0 ),
        .I1(\cent[3]_i_12_n_0 ),
        .I2(\cent[3]_i_13_n_0 ),
        .I3(\cent[3]_i_14_n_0 ),
        .I4(\cent[3]_i_15_n_0 ),
        .I5(\dec[3]_i_9_n_0 ),
        .O(\dec[3]_i_11_n_0 ));
  LUT4 #(
    .INIT(16'h6966)) 
    \dec[3]_i_12 
       (.I0(bin[7]),
        .I1(\un[3]_i_10_n_0 ),
        .I2(bin[6]),
        .I3(\dec[3]_i_13_n_0 ),
        .O(p_0_in__11));
  LUT6 #(
    .INIT(64'h0EB33EB0C83FFC2C)) 
    \dec[3]_i_13 
       (.I0(bin[6]),
        .I1(p_0_in__8[1]),
        .I2(bin[8]),
        .I3(\dec[3]_i_20_n_0 ),
        .I4(p_0_in__8[2]),
        .I5(bin[7]),
        .O(\dec[3]_i_13_n_0 ));
  LUT4 #(
    .INIT(16'h6966)) 
    \dec[3]_i_14 
       (.I0(\cent[3]_i_13_n_0 ),
        .I1(\cent[3]_i_14_n_0 ),
        .I2(\dec[3]_i_9_n_0 ),
        .I3(\dec[3]_i_8_n_0 ),
        .O(\dec[3]_i_14_n_0 ));
  LUT6 #(
    .INIT(64'hA419941A62955686)) 
    \dec[3]_i_15 
       (.I0(\cent[3]_i_19_n_0 ),
        .I1(\dec[3]_i_22_n_0 ),
        .I2(\dec[3]_i_23_n_0 ),
        .I3(\dec[3]_i_24_n_0 ),
        .I4(\dec[3]_i_25_n_0 ),
        .I5(\mil[3]_i_28_n_0 ),
        .O(\dec[3]_i_15_n_0 ));
  LUT6 #(
    .INIT(64'h0E360FB0C83CCB2C)) 
    \dec[3]_i_16 
       (.I0(bin[8]),
        .I1(p_0_in__6[1]),
        .I2(bin[10]),
        .I3(p_0_in__6[2]),
        .I4(p_0_in__6[3]),
        .I5(bin[9]),
        .O(\dec[3]_i_16_n_0 ));
  LUT6 #(
    .INIT(64'h0E3E0FB0C8FCCB2C)) 
    \dec[3]_i_17 
       (.I0(\dec[3]_i_16_n_0 ),
        .I1(\mil[3]_i_27_n_0 ),
        .I2(\mil[3]_i_28_n_0 ),
        .I3(\mil[3]_i_29_n_0 ),
        .I4(\mil[3]_i_30_n_0 ),
        .I5(\cent[3]_i_19_n_0 ),
        .O(\dec[3]_i_17_n_0 ));
  LUT6 #(
    .INIT(64'h281157EA3129C246)) 
    \dec[3]_i_18 
       (.I0(\dec[3]_i_24_n_0 ),
        .I1(\dec[3]_i_22_n_0 ),
        .I2(\dec[3]_i_23_n_0 ),
        .I3(\dec[3]_i_25_n_0 ),
        .I4(\mil[3]_i_28_n_0 ),
        .I5(\cent[3]_i_19_n_0 ),
        .O(\dec[3]_i_18_n_0 ));
  LUT6 #(
    .INIT(64'hA419941A62955686)) 
    \dec[3]_i_19 
       (.I0(bin[9]),
        .I1(p_0_in__5[1]),
        .I2(bin[11]),
        .I3(\dec[3]_i_30_n_0 ),
        .I4(p_0_in__5[2]),
        .I5(bin[10]),
        .O(p_0_in__8[1]));
  LUT6 #(
    .INIT(64'h33939333CC3636CC)) 
    \dec[3]_i_2 
       (.I0(bin[3]),
        .I1(p_0_in__12),
        .I2(bin[4]),
        .I3(\un[3]_i_8_n_0 ),
        .I4(bin[5]),
        .I5(\un[3]_i_5_n_0 ),
        .O(\dec[3]_i_2_n_0 ));
  LUT6 #(
    .INIT(64'h0E3E0FB0C8FCCB2C)) 
    \dec[3]_i_20 
       (.I0(bin[8]),
        .I1(p_0_in__6[1]),
        .I2(bin[10]),
        .I3(p_0_in__6[2]),
        .I4(p_0_in__6[3]),
        .I5(bin[9]),
        .O(\dec[3]_i_20_n_0 ));
  LUT6 #(
    .INIT(64'h281157EA3129C246)) 
    \dec[3]_i_21 
       (.I0(\dec[3]_i_30_n_0 ),
        .I1(p_0_in__5[1]),
        .I2(bin[11]),
        .I3(p_0_in__5[2]),
        .I4(bin[10]),
        .I5(bin[9]),
        .O(p_0_in__8[2]));
  (* SOFT_HLUTNM = "soft_lutpair5" *) 
  LUT5 #(
    .INIT(32'h11989A56)) 
    \dec[3]_i_22 
       (.I0(\mil[3]_i_32_n_0 ),
        .I1(\mil[3]_i_39_n_0 ),
        .I2(\mil[3]_i_40_n_0 ),
        .I3(\mil[3]_i_37_n_0 ),
        .I4(\mil[3]_i_38_n_0 ),
        .O(\dec[3]_i_22_n_0 ));
  LUT6 #(
    .INIT(64'h0E360FB0C83CCB2C)) 
    \dec[3]_i_23 
       (.I0(bin[11]),
        .I1(p_0_in__3[1]),
        .I2(bin[13]),
        .I3(p_0_in__3[2]),
        .I4(p_0_in__3[3]),
        .I5(bin[12]),
        .O(\dec[3]_i_23_n_0 ));
  LUT6 #(
    .INIT(64'h0E3E0FB0C8FCCB2C)) 
    \dec[3]_i_24 
       (.I0(\dec[3]_i_23_n_0 ),
        .I1(\mil[3]_i_38_n_0 ),
        .I2(\mil[3]_i_37_n_0 ),
        .I3(\mil[3]_i_39_n_0 ),
        .I4(\mil[3]_i_40_n_0 ),
        .I5(\mil[3]_i_32_n_0 ),
        .O(\dec[3]_i_24_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair6" *) 
  LUT5 #(
    .INIT(32'h3266318C)) 
    \dec[3]_i_25 
       (.I0(\mil[3]_i_40_n_0 ),
        .I1(\mil[3]_i_37_n_0 ),
        .I2(\mil[3]_i_38_n_0 ),
        .I3(\mil[3]_i_39_n_0 ),
        .I4(\mil[3]_i_32_n_0 ),
        .O(\dec[3]_i_25_n_0 ));
  LUT6 #(
    .INIT(64'hA494A51A62566186)) 
    \dec[3]_i_26 
       (.I0(bin[11]),
        .I1(p_0_in__3[1]),
        .I2(bin[13]),
        .I3(p_0_in__3[2]),
        .I4(p_0_in__3[3]),
        .I5(bin[12]),
        .O(p_0_in__6[1]));
  LUT6 #(
    .INIT(64'h660511F84561981A)) 
    \dec[3]_i_27 
       (.I0(p_0_in__3[1]),
        .I1(bin[13]),
        .I2(p_0_in__3[3]),
        .I3(p_0_in__3[2]),
        .I4(bin[12]),
        .I5(bin[11]),
        .O(p_0_in__6[2]));
  LUT6 #(
    .INIT(64'h2008174424011280)) 
    \dec[3]_i_28 
       (.I0(bin[11]),
        .I1(bin[12]),
        .I2(p_0_in__3[2]),
        .I3(p_0_in__3[1]),
        .I4(bin[13]),
        .I5(p_0_in__3[3]),
        .O(p_0_in__6[3]));
  LUT6 #(
    .INIT(64'h9A56119811989A56)) 
    \dec[3]_i_29 
       (.I0(bin[12]),
        .I1(p_0_in__3[2]),
        .I2(p_0_in__3[3]),
        .I3(bin[13]),
        .I4(\mil[3]_i_36_n_0 ),
        .I5(bin[14]),
        .O(p_0_in__5[1]));
  (* SOFT_HLUTNM = "soft_lutpair9" *) 
  LUT4 #(
    .INIT(16'h6966)) 
    \dec[3]_i_3 
       (.I0(\dec[3]_i_8_n_0 ),
        .I1(\dec[3]_i_9_n_0 ),
        .I2(\dec[3]_i_10_n_0 ),
        .I3(\dec[3]_i_11_n_0 ),
        .O(\dec[3]_i_3_n_0 ));
  LUT6 #(
    .INIT(64'h0E3E0FB0C8FCCB2C)) 
    \dec[3]_i_30 
       (.I0(bin[11]),
        .I1(p_0_in__3[1]),
        .I2(bin[13]),
        .I3(p_0_in__3[2]),
        .I4(p_0_in__3[3]),
        .I5(bin[12]),
        .O(\dec[3]_i_30_n_0 ));
  LUT6 #(
    .INIT(64'h233266661331C88C)) 
    \dec[3]_i_31 
       (.I0(p_0_in__3[3]),
        .I1(bin[13]),
        .I2(\mil[3]_i_36_n_0 ),
        .I3(bin[14]),
        .I4(p_0_in__3[2]),
        .I5(bin[12]),
        .O(p_0_in__5[2]));
  LUT6 #(
    .INIT(64'hA4255A9292A4495A)) 
    \dec[3]_i_32 
       (.I0(bin[14]),
        .I1(bin[19]),
        .I2(bin[18]),
        .I3(bin[17]),
        .I4(bin[16]),
        .I5(bin[15]),
        .O(p_0_in__3[1]));
  LUT6 #(
    .INIT(64'h92C3492CC3492C34)) 
    \dec[3]_i_33 
       (.I0(bin[16]),
        .I1(bin[19]),
        .I2(bin[17]),
        .I3(bin[18]),
        .I4(bin[15]),
        .I5(bin[14]),
        .O(p_0_in__3[2]));
  LUT6 #(
    .INIT(64'h0821104242088410)) 
    \dec[3]_i_34 
       (.I0(bin[14]),
        .I1(bin[15]),
        .I2(bin[16]),
        .I3(bin[19]),
        .I4(bin[18]),
        .I5(bin[17]),
        .O(p_0_in__3[3]));
  LUT6 #(
    .INIT(64'h33939333CC3636CC)) 
    \dec[3]_i_4 
       (.I0(bin[4]),
        .I1(p_0_in__11),
        .I2(bin[5]),
        .I3(\dec[3]_i_13_n_0 ),
        .I4(bin[6]),
        .I5(\un[3]_i_8_n_0 ),
        .O(\dec[3]_i_4_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair9" *) 
  LUT2 #(
    .INIT(4'h6)) 
    \dec[3]_i_5 
       (.I0(\dec[3]_i_11_n_0 ),
        .I1(\dec[3]_i_10_n_0 ),
        .O(\dec[3]_i_5_n_0 ));
  LUT6 #(
    .INIT(64'h60FF99FFFF66FF60)) 
    \dec[3]_i_6 
       (.I0(\dec[3]_i_8_n_0 ),
        .I1(\dec[3]_i_9_n_0 ),
        .I2(\dec[3]_i_4_n_0 ),
        .I3(\dec[3]_i_14_n_0 ),
        .I4(\dec[3]_i_10_n_0 ),
        .I5(\dec[3]_i_11_n_0 ),
        .O(\dec[3]_i_6_n_0 ));
  LUT6 #(
    .INIT(64'h33939333CC3636CC)) 
    \dec[3]_i_7 
       (.I0(bin[2]),
        .I1(p_0_in__13),
        .I2(bin[3]),
        .I3(\un[3]_i_5_n_0 ),
        .I4(bin[4]),
        .I5(\un[3]_i_4_n_0 ),
        .O(\dec[3]_i_7_n_0 ));
  LUT6 #(
    .INIT(64'h0EB33EB0C83FFC2C)) 
    \dec[3]_i_8 
       (.I0(\dec[3]_i_9_n_0 ),
        .I1(\dec[3]_i_15_n_0 ),
        .I2(\dec[3]_i_16_n_0 ),
        .I3(\dec[3]_i_17_n_0 ),
        .I4(\dec[3]_i_18_n_0 ),
        .I5(\cent[3]_i_13_n_0 ),
        .O(\dec[3]_i_8_n_0 ));
  LUT6 #(
    .INIT(64'h0E9336B0C8333C2C)) 
    \dec[3]_i_9 
       (.I0(bin[6]),
        .I1(p_0_in__8[1]),
        .I2(bin[8]),
        .I3(\dec[3]_i_20_n_0 ),
        .I4(p_0_in__8[2]),
        .I5(bin[7]),
        .O(\dec[3]_i_9_n_0 ));
  FDRE #(
    .INIT(1'b0)) 
    \dec_reg[0] 
       (.C(clk),
        .CE(1'b1),
        .D(p_1_out[0]),
        .Q(dec[0]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \dec_reg[1] 
       (.C(clk),
        .CE(1'b1),
        .D(p_1_out[1]),
        .Q(dec[1]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \dec_reg[2] 
       (.C(clk),
        .CE(1'b1),
        .D(p_1_out[2]),
        .Q(dec[2]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \dec_reg[3] 
       (.C(clk),
        .CE(1'b1),
        .D(p_1_out[3]),
        .Q(dec[3]),
        .R(1'b0));
  LUT6 #(
    .INIT(64'h4D3AA17C4B3001EC)) 
    \mil[0]_i_1 
       (.I0(\cent[3]_i_2_n_0 ),
        .I1(\cent[3]_i_3_n_0 ),
        .I2(\cent[3]_i_4_n_0 ),
        .I3(\cent[3]_i_5_n_0 ),
        .I4(\cent[3]_i_6_n_0 ),
        .I5(\cent[3]_i_7_n_0 ),
        .O(p_3_out[0]));
  LUT6 #(
    .INIT(64'h900F0F96690F0F90)) 
    \mil[1]_i_1 
       (.I0(\mil[3]_i_2_n_0 ),
        .I1(\mil[3]_i_3_n_0 ),
        .I2(\mil[3]_i_4_n_0 ),
        .I3(\mil[3]_i_5_n_0 ),
        .I4(\mil[3]_i_6_n_0 ),
        .I5(\mil[3]_i_7_n_0 ),
        .O(p_3_out[1]));
  LUT6 #(
    .INIT(64'h00F6F00F0FF0F900)) 
    \mil[2]_i_1 
       (.I0(\mil[3]_i_2_n_0 ),
        .I1(\mil[3]_i_3_n_0 ),
        .I2(\mil[3]_i_4_n_0 ),
        .I3(\mil[3]_i_7_n_0 ),
        .I4(\mil[3]_i_6_n_0 ),
        .I5(\mil[3]_i_5_n_0 ),
        .O(p_3_out[2]));
  LUT6 #(
    .INIT(64'h0696990000669606)) 
    \mil[3]_i_1 
       (.I0(\mil[3]_i_2_n_0 ),
        .I1(\mil[3]_i_3_n_0 ),
        .I2(\mil[3]_i_4_n_0 ),
        .I3(\mil[3]_i_5_n_0 ),
        .I4(\mil[3]_i_6_n_0 ),
        .I5(\mil[3]_i_7_n_0 ),
        .O(p_3_out[3]));
  (* SOFT_HLUTNM = "soft_lutpair2" *) 
  LUT5 #(
    .INIT(32'h6318318C)) 
    \mil[3]_i_10 
       (.I0(\tril[3]_i_9_n_0 ),
        .I1(\tril[3]_i_8_n_0 ),
        .I2(\tril[3]_i_10_n_0 ),
        .I3(\tril[3]_i_11_n_0 ),
        .I4(\bil[3]_i_10_n_0 ),
        .O(\mil[3]_i_10_n_0 ));
  LUT6 #(
    .INIT(64'h0E9336B0C8333C2C)) 
    \mil[3]_i_11 
       (.I0(\cent[3]_i_8_n_0 ),
        .I1(\cent[3]_i_20_n_0 ),
        .I2(\cent[3]_i_21_n_0 ),
        .I3(\cent[3]_i_22_n_0 ),
        .I4(\cent[3]_i_23_n_0 ),
        .I5(\mil[3]_i_13_n_0 ),
        .O(\mil[3]_i_11_n_0 ));
  LUT6 #(
    .INIT(64'hA419941A62955686)) 
    \mil[3]_i_12 
       (.I0(\cent[3]_i_21_n_0 ),
        .I1(\mil[3]_i_23_n_0 ),
        .I2(\mil[3]_i_24_n_0 ),
        .I3(\mil[3]_i_25_n_0 ),
        .I4(\mil[3]_i_26_n_0 ),
        .I5(\mil[3]_i_20_n_0 ),
        .O(\mil[3]_i_12_n_0 ));
  LUT6 #(
    .INIT(64'h0E360FB0C83CCB2C)) 
    \mil[3]_i_13 
       (.I0(\dec[3]_i_16_n_0 ),
        .I1(\mil[3]_i_27_n_0 ),
        .I2(\mil[3]_i_28_n_0 ),
        .I3(\mil[3]_i_29_n_0 ),
        .I4(\mil[3]_i_30_n_0 ),
        .I5(\cent[3]_i_19_n_0 ),
        .O(\mil[3]_i_13_n_0 ));
  LUT6 #(
    .INIT(64'h0E3E0FB0C8FCCB2C)) 
    \mil[3]_i_14 
       (.I0(\mil[3]_i_13_n_0 ),
        .I1(\mil[3]_i_19_n_0 ),
        .I2(\mil[3]_i_20_n_0 ),
        .I3(\mil[3]_i_21_n_0 ),
        .I4(\mil[3]_i_22_n_0 ),
        .I5(\cent[3]_i_21_n_0 ),
        .O(\mil[3]_i_14_n_0 ));
  LUT6 #(
    .INIT(64'h281157EA3129C246)) 
    \mil[3]_i_15 
       (.I0(\mil[3]_i_25_n_0 ),
        .I1(\mil[3]_i_23_n_0 ),
        .I2(\mil[3]_i_24_n_0 ),
        .I3(\mil[3]_i_26_n_0 ),
        .I4(\mil[3]_i_20_n_0 ),
        .I5(\cent[3]_i_21_n_0 ),
        .O(\mil[3]_i_15_n_0 ));
  LUT6 #(
    .INIT(64'h0EB33EB0C83FFC2C)) 
    \mil[3]_i_16 
       (.I0(\mil[3]_i_11_n_0 ),
        .I1(\bil[3]_i_9_n_0 ),
        .I2(\bil[3]_i_10_n_0 ),
        .I3(\tril[3]_i_2_n_0 ),
        .I4(\bil[3]_i_11_n_0 ),
        .I5(\mil[3]_i_9_n_0 ),
        .O(\mil[3]_i_16_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair17" *) 
  LUT2 #(
    .INIT(4'h6)) 
    \mil[3]_i_17 
       (.I0(\tril[3]_i_5_n_0 ),
        .I1(\mil[3]_i_9_n_0 ),
        .O(\mil[3]_i_17_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair17" *) 
  LUT3 #(
    .INIT(8'h9A)) 
    \mil[3]_i_18 
       (.I0(\mil[3]_i_8_n_0 ),
        .I1(\mil[3]_i_9_n_0 ),
        .I2(\tril[3]_i_5_n_0 ),
        .O(\mil[3]_i_18_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair3" *) 
  LUT5 #(
    .INIT(32'hA51A6186)) 
    \mil[3]_i_19 
       (.I0(\mil[3]_i_24_n_0 ),
        .I1(\bil[3]_i_14_n_0 ),
        .I2(\bil[3]_i_13_n_0 ),
        .I3(\bil[3]_i_15_n_0 ),
        .I4(\bil[3]_i_16_n_0 ),
        .O(\mil[3]_i_19_n_0 ));
  LUT6 #(
    .INIT(64'h0EB33EB0C83FFC2C)) 
    \mil[3]_i_2 
       (.I0(\mil[3]_i_3_n_0 ),
        .I1(\mil[3]_i_8_n_0 ),
        .I2(\mil[3]_i_9_n_0 ),
        .I3(\tril[3]_i_5_n_0 ),
        .I4(\mil[3]_i_10_n_0 ),
        .I5(\mil[3]_i_11_n_0 ),
        .O(\mil[3]_i_2_n_0 ));
  LUT6 #(
    .INIT(64'h33939333CC3636CC)) 
    \mil[3]_i_20 
       (.I0(\mil[3]_i_28_n_0 ),
        .I1(\dec[3]_i_25_n_0 ),
        .I2(\dec[3]_i_23_n_0 ),
        .I3(\mil[3]_i_31_n_0 ),
        .I4(\mil[3]_i_32_n_0 ),
        .I5(\dec[3]_i_24_n_0 ),
        .O(\mil[3]_i_20_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair4" *) 
  LUT5 #(
    .INIT(32'h6318318C)) 
    \mil[3]_i_21 
       (.I0(\bil[3]_i_13_n_0 ),
        .I1(\bil[3]_i_14_n_0 ),
        .I2(\bil[3]_i_15_n_0 ),
        .I3(\bil[3]_i_16_n_0 ),
        .I4(\mil[3]_i_24_n_0 ),
        .O(\mil[3]_i_21_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair3" *) 
  LUT5 #(
    .INIT(32'h21084210)) 
    \mil[3]_i_22 
       (.I0(\mil[3]_i_24_n_0 ),
        .I1(\bil[3]_i_16_n_0 ),
        .I2(\bil[3]_i_13_n_0 ),
        .I3(\bil[3]_i_14_n_0 ),
        .I4(\bil[3]_i_15_n_0 ),
        .O(\mil[3]_i_22_n_0 ));
  LUT6 #(
    .INIT(64'h20CBCD300402CF3C)) 
    \mil[3]_i_23 
       (.I0(\mil[3]_i_32_n_0 ),
        .I1(\mil[3]_i_33_n_0 ),
        .I2(p_0_in__0[1]),
        .I3(p_0_in__0[2]),
        .I4(\mil[3]_i_36_n_0 ),
        .I5(\mil[3]_i_37_n_0 ),
        .O(\mil[3]_i_23_n_0 ));
  LUT6 #(
    .INIT(64'h0E360FB0C83CCB2C)) 
    \mil[3]_i_24 
       (.I0(\dec[3]_i_23_n_0 ),
        .I1(\mil[3]_i_38_n_0 ),
        .I2(\mil[3]_i_37_n_0 ),
        .I3(\mil[3]_i_39_n_0 ),
        .I4(\mil[3]_i_40_n_0 ),
        .I5(\mil[3]_i_32_n_0 ),
        .O(\mil[3]_i_24_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair4" *) 
  LUT5 #(
    .INIT(32'h0FB0CB2C)) 
    \mil[3]_i_25 
       (.I0(\mil[3]_i_24_n_0 ),
        .I1(\bil[3]_i_14_n_0 ),
        .I2(\bil[3]_i_13_n_0 ),
        .I3(\bil[3]_i_15_n_0 ),
        .I4(\bil[3]_i_16_n_0 ),
        .O(\mil[3]_i_25_n_0 ));
  LUT6 #(
    .INIT(64'hC03E03E0C07C03E0)) 
    \mil[3]_i_26 
       (.I0(\mil[3]_i_37_n_0 ),
        .I1(\mil[3]_i_36_n_0 ),
        .I2(\mil[3]_i_33_n_0 ),
        .I3(p_0_in__0[1]),
        .I4(p_0_in__0[2]),
        .I5(\mil[3]_i_32_n_0 ),
        .O(\mil[3]_i_26_n_0 ));
  LUT6 #(
    .INIT(64'hA494A51A62566186)) 
    \mil[3]_i_27 
       (.I0(\dec[3]_i_23_n_0 ),
        .I1(\mil[3]_i_38_n_0 ),
        .I2(\mil[3]_i_37_n_0 ),
        .I3(\mil[3]_i_39_n_0 ),
        .I4(\mil[3]_i_40_n_0 ),
        .I5(\mil[3]_i_32_n_0 ),
        .O(\mil[3]_i_27_n_0 ));
  LUT6 #(
    .INIT(64'h33939333CC3636CC)) 
    \mil[3]_i_28 
       (.I0(bin[10]),
        .I1(p_0_in__5[2]),
        .I2(bin[11]),
        .I3(\mil[3]_i_41_n_0 ),
        .I4(bin[12]),
        .I5(\dec[3]_i_30_n_0 ),
        .O(\mil[3]_i_28_n_0 ));
  LUT6 #(
    .INIT(64'h660511F84561981A)) 
    \mil[3]_i_29 
       (.I0(\mil[3]_i_38_n_0 ),
        .I1(\mil[3]_i_37_n_0 ),
        .I2(\mil[3]_i_40_n_0 ),
        .I3(\mil[3]_i_39_n_0 ),
        .I4(\mil[3]_i_32_n_0 ),
        .I5(\dec[3]_i_23_n_0 ),
        .O(\mil[3]_i_29_n_0 ));
  LUT6 #(
    .INIT(64'h0E9336B0C8333C2C)) 
    \mil[3]_i_3 
       (.I0(\cent[3]_i_10_n_0 ),
        .I1(\mil[3]_i_12_n_0 ),
        .I2(\mil[3]_i_13_n_0 ),
        .I3(\mil[3]_i_14_n_0 ),
        .I4(\mil[3]_i_15_n_0 ),
        .I5(\cent[3]_i_8_n_0 ),
        .O(\mil[3]_i_3_n_0 ));
  LUT6 #(
    .INIT(64'h2008174424011280)) 
    \mil[3]_i_30 
       (.I0(\dec[3]_i_23_n_0 ),
        .I1(\mil[3]_i_32_n_0 ),
        .I2(\mil[3]_i_39_n_0 ),
        .I3(\mil[3]_i_38_n_0 ),
        .I4(\mil[3]_i_37_n_0 ),
        .I5(\mil[3]_i_40_n_0 ),
        .O(\mil[3]_i_30_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair6" *) 
  LUT5 #(
    .INIT(32'hBB3230FC)) 
    \mil[3]_i_31 
       (.I0(\mil[3]_i_32_n_0 ),
        .I1(\mil[3]_i_39_n_0 ),
        .I2(\mil[3]_i_40_n_0 ),
        .I3(\mil[3]_i_37_n_0 ),
        .I4(\mil[3]_i_38_n_0 ),
        .O(\mil[3]_i_31_n_0 ));
  LUT6 #(
    .INIT(64'h303C9B329B32303C)) 
    \mil[3]_i_32 
       (.I0(bin[12]),
        .I1(p_0_in__3[2]),
        .I2(p_0_in__3[3]),
        .I3(bin[13]),
        .I4(\mil[3]_i_36_n_0 ),
        .I5(bin[14]),
        .O(\mil[3]_i_32_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair8" *) 
  LUT5 #(
    .INIT(32'h0FB0CB2C)) 
    \mil[3]_i_33 
       (.I0(bin[15]),
        .I1(bin[18]),
        .I2(bin[17]),
        .I3(bin[19]),
        .I4(bin[16]),
        .O(\mil[3]_i_33_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair8" *) 
  LUT4 #(
    .INIT(16'hB02C)) 
    \mil[3]_i_34 
       (.I0(bin[16]),
        .I1(bin[19]),
        .I2(bin[18]),
        .I3(bin[17]),
        .O(p_0_in__0[1]));
  LUT3 #(
    .INIT(8'hE0)) 
    \mil[3]_i_35 
       (.I0(bin[17]),
        .I1(bin[18]),
        .I2(bin[19]),
        .O(p_0_in__0[2]));
  LUT6 #(
    .INIT(64'h0E8FF038380EE3F0)) 
    \mil[3]_i_36 
       (.I0(bin[14]),
        .I1(bin[19]),
        .I2(bin[18]),
        .I3(bin[17]),
        .I4(bin[16]),
        .I5(bin[15]),
        .O(\mil[3]_i_36_n_0 ));
  LUT6 #(
    .INIT(64'h33939333CC3636CC)) 
    \mil[3]_i_37 
       (.I0(bin[13]),
        .I1(p_0_in__2),
        .I2(bin[14]),
        .I3(\mil[3]_i_33_n_0 ),
        .I4(bin[15]),
        .I5(\mil[3]_i_36_n_0 ),
        .O(\mil[3]_i_37_n_0 ));
  LUT6 #(
    .INIT(64'h20CBCD300402CF3C)) 
    \mil[3]_i_38 
       (.I0(bin[14]),
        .I1(bin[17]),
        .I2(bin[18]),
        .I3(bin[19]),
        .I4(bin[16]),
        .I5(bin[15]),
        .O(\mil[3]_i_38_n_0 ));
  LUT6 #(
    .INIT(64'hC03E03E0C07C03E0)) 
    \mil[3]_i_39 
       (.I0(bin[15]),
        .I1(bin[16]),
        .I2(bin[17]),
        .I3(bin[18]),
        .I4(bin[19]),
        .I5(bin[14]),
        .O(\mil[3]_i_39_n_0 ));
  LUT5 #(
    .INIT(32'h933336CC)) 
    \mil[3]_i_4 
       (.I0(\cent[3]_i_2_n_0 ),
        .I1(\cent[3]_i_3_n_0 ),
        .I2(\cent[3]_i_4_n_0 ),
        .I3(\cent[3]_i_5_n_0 ),
        .I4(\cent[3]_i_6_n_0 ),
        .O(\mil[3]_i_4_n_0 ));
  LUT6 #(
    .INIT(64'h0E0000F000301000)) 
    \mil[3]_i_40 
       (.I0(bin[14]),
        .I1(bin[15]),
        .I2(bin[18]),
        .I3(bin[17]),
        .I4(bin[19]),
        .I5(bin[16]),
        .O(\mil[3]_i_40_n_0 ));
  LUT6 #(
    .INIT(64'h30FCBB32BB3230FC)) 
    \mil[3]_i_41 
       (.I0(bin[12]),
        .I1(p_0_in__3[2]),
        .I2(p_0_in__3[3]),
        .I3(bin[13]),
        .I4(\mil[3]_i_36_n_0 ),
        .I5(bin[14]),
        .O(\mil[3]_i_41_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair7" *) 
  LUT5 #(
    .INIT(32'h6318318C)) 
    \mil[3]_i_42 
       (.I0(bin[17]),
        .I1(bin[18]),
        .I2(bin[19]),
        .I3(bin[16]),
        .I4(bin[15]),
        .O(p_0_in__2));
  LUT4 #(
    .INIT(16'h6966)) 
    \mil[3]_i_5 
       (.I0(\mil[3]_i_11_n_0 ),
        .I1(\mil[3]_i_16_n_0 ),
        .I2(\mil[3]_i_3_n_0 ),
        .I3(\mil[3]_i_2_n_0 ),
        .O(\mil[3]_i_5_n_0 ));
  LUT6 #(
    .INIT(64'h0EB33EB0C83FFC2C)) 
    \mil[3]_i_6 
       (.I0(\mil[3]_i_7_n_0 ),
        .I1(\mil[3]_i_17_n_0 ),
        .I2(\mil[3]_i_11_n_0 ),
        .I3(\mil[3]_i_16_n_0 ),
        .I4(\mil[3]_i_18_n_0 ),
        .I5(\mil[3]_i_3_n_0 ),
        .O(\mil[3]_i_6_n_0 ));
  LUT6 #(
    .INIT(64'h0E9336B0C8333C2C)) 
    \mil[3]_i_7 
       (.I0(\cent[3]_i_4_n_0 ),
        .I1(\cent[3]_i_16_n_0 ),
        .I2(\cent[3]_i_8_n_0 ),
        .I3(\cent[3]_i_9_n_0 ),
        .I4(\cent[3]_i_17_n_0 ),
        .I5(\cent[3]_i_10_n_0 ),
        .O(\mil[3]_i_7_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair1" *) 
  LUT5 #(
    .INIT(32'hA51A6186)) 
    \mil[3]_i_8 
       (.I0(\bil[3]_i_10_n_0 ),
        .I1(\tril[3]_i_8_n_0 ),
        .I2(\tril[3]_i_9_n_0 ),
        .I3(\tril[3]_i_10_n_0 ),
        .I4(\tril[3]_i_11_n_0 ),
        .O(\mil[3]_i_8_n_0 ));
  LUT6 #(
    .INIT(64'h0E360FB0C83CCB2C)) 
    \mil[3]_i_9 
       (.I0(\mil[3]_i_13_n_0 ),
        .I1(\mil[3]_i_19_n_0 ),
        .I2(\mil[3]_i_20_n_0 ),
        .I3(\mil[3]_i_21_n_0 ),
        .I4(\mil[3]_i_22_n_0 ),
        .I5(\cent[3]_i_21_n_0 ),
        .O(\mil[3]_i_9_n_0 ));
  FDRE #(
    .INIT(1'b0)) 
    \mil_reg[0] 
       (.C(clk),
        .CE(1'b1),
        .D(p_3_out[0]),
        .Q(mil[0]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \mil_reg[1] 
       (.C(clk),
        .CE(1'b1),
        .D(p_3_out[1]),
        .Q(mil[1]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \mil_reg[2] 
       (.C(clk),
        .CE(1'b1),
        .D(p_3_out[2]),
        .Q(mil[2]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \mil_reg[3] 
       (.C(clk),
        .CE(1'b1),
        .D(p_3_out[3]),
        .Q(mil[3]),
        .R(1'b0));
  LUT6 #(
    .INIT(64'h7800FF0087870000)) 
    \quadr[0]_i_1 
       (.I0(\bil[3]_i_4_n_0 ),
        .I1(\tril[2]_i_2_n_0 ),
        .I2(\tril[2]_i_3_n_0 ),
        .I3(\tril[3]_i_6_n_0 ),
        .I4(\tril[2]_i_5_n_0 ),
        .I5(\tril[2]_i_6_n_0 ),
        .O(p_6_out[0]));
  LUT5 #(
    .INIT(32'hE3F80000)) 
    \quadr[1]_i_1 
       (.I0(\tril[2]_i_2_n_0 ),
        .I1(\tril[3]_i_2_n_0 ),
        .I2(\tril[3]_i_3_n_0 ),
        .I3(\tril[3]_i_4_n_0 ),
        .I4(\tril[2]_i_5_n_0 ),
        .O(p_6_out[1]));
  FDRE #(
    .INIT(1'b0)) 
    \quadr_reg[0] 
       (.C(clk),
        .CE(1'b1),
        .D(p_6_out[0]),
        .Q(quadr[0]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \quadr_reg[1] 
       (.C(clk),
        .CE(1'b1),
        .D(p_6_out[1]),
        .Q(quadr[1]),
        .R(1'b0));
  LUT6 #(
    .INIT(64'h0E9336B0C8333C2C)) 
    \tril[0]_i_1 
       (.I0(\bil[3]_i_2_n_0 ),
        .I1(\bil[3]_i_3_n_0 ),
        .I2(\bil[3]_i_6_n_0 ),
        .I3(\bil[3]_i_5_n_0 ),
        .I4(\bil[3]_i_4_n_0 ),
        .I5(\bil[3]_i_7_n_0 ),
        .O(p_5_out[0]));
  LUT2 #(
    .INIT(4'h6)) 
    \tril[1]_i_1 
       (.I0(tril1),
        .I1(\tril[2]_i_4_n_0 ),
        .O(p_5_out[1]));
  LUT6 #(
    .INIT(64'h8787780000877878)) 
    \tril[2]_i_1 
       (.I0(\bil[3]_i_4_n_0 ),
        .I1(\tril[2]_i_2_n_0 ),
        .I2(\tril[2]_i_3_n_0 ),
        .I3(\tril[2]_i_4_n_0 ),
        .I4(\tril[2]_i_5_n_0 ),
        .I5(\tril[2]_i_6_n_0 ),
        .O(p_5_out[2]));
  LUT6 #(
    .INIT(64'hE9D77FEEA957FFEA)) 
    \tril[2]_i_2 
       (.I0(\bil[3]_i_8_n_0 ),
        .I1(\mil[3]_i_8_n_0 ),
        .I2(\mil[3]_i_9_n_0 ),
        .I3(\tril[2]_i_7_n_0 ),
        .I4(\mil[3]_i_10_n_0 ),
        .I5(\mil[3]_i_11_n_0 ),
        .O(\tril[2]_i_2_n_0 ));
  LUT6 #(
    .INIT(64'hCDF3320C320C320C)) 
    \tril[2]_i_3 
       (.I0(\tril[3]_i_11_n_0 ),
        .I1(\tril[3]_i_10_n_0 ),
        .I2(\tril[3]_i_9_n_0 ),
        .I3(\tril[3]_i_8_n_0 ),
        .I4(\bil[3]_i_8_n_0 ),
        .I5(\tril[2]_i_8_n_0 ),
        .O(\tril[2]_i_3_n_0 ));
  LUT6 #(
    .INIT(64'h0E8FF038380EE3F0)) 
    \tril[2]_i_4 
       (.I0(\bil[3]_i_7_n_0 ),
        .I1(\tril[3]_i_4_n_0 ),
        .I2(\tril[3]_i_3_n_0 ),
        .I3(\tril[3]_i_2_n_0 ),
        .I4(\tril[3]_i_5_n_0 ),
        .I5(\bil[3]_i_6_n_0 ),
        .O(\tril[2]_i_4_n_0 ));
  LUT6 #(
    .INIT(64'hFF3CFB2C00000000)) 
    \tril[2]_i_5 
       (.I0(\tril[3]_i_11_n_0 ),
        .I1(\tril[3]_i_10_n_0 ),
        .I2(\tril[3]_i_9_n_0 ),
        .I3(\tril[3]_i_8_n_0 ),
        .I4(\bil[3]_i_10_n_0 ),
        .I5(\tril[3]_i_4_n_0 ),
        .O(\tril[2]_i_5_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair10" *) 
  LUT4 #(
    .INIT(16'hA02C)) 
    \tril[2]_i_6 
       (.I0(\tril[2]_i_8_n_0 ),
        .I1(\tril[3]_i_4_n_0 ),
        .I2(\tril[3]_i_3_n_0 ),
        .I3(\tril[3]_i_2_n_0 ),
        .O(\tril[2]_i_6_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair1" *) 
  LUT5 #(
    .INIT(32'h21084210)) 
    \tril[2]_i_7 
       (.I0(\bil[3]_i_10_n_0 ),
        .I1(\tril[3]_i_11_n_0 ),
        .I2(\tril[3]_i_9_n_0 ),
        .I3(\tril[3]_i_8_n_0 ),
        .I4(\tril[3]_i_10_n_0 ),
        .O(\tril[2]_i_7_n_0 ));
  LUT6 #(
    .INIT(64'hF9CFF3FCF18FE3F8)) 
    \tril[2]_i_8 
       (.I0(\bil[3]_i_10_n_0 ),
        .I1(\tril[3]_i_11_n_0 ),
        .I2(\tril[3]_i_9_n_0 ),
        .I3(\tril[3]_i_8_n_0 ),
        .I4(\tril[3]_i_10_n_0 ),
        .I5(\mil[3]_i_9_n_0 ),
        .O(\tril[2]_i_8_n_0 ));
  LUT6 #(
    .INIT(64'hE3E71C181C181C18)) 
    \tril[3]_i_1 
       (.I0(\tril[3]_i_2_n_0 ),
        .I1(\tril[3]_i_3_n_0 ),
        .I2(\tril[3]_i_4_n_0 ),
        .I3(\tril[3]_i_5_n_0 ),
        .I4(\tril[3]_i_6_n_0 ),
        .I5(tril1),
        .O(p_5_out[3]));
  (* SOFT_HLUTNM = "soft_lutpair0" *) 
  LUT3 #(
    .INIT(8'hE0)) 
    \tril[3]_i_10 
       (.I0(\bil[3]_i_14_n_0 ),
        .I1(\bil[3]_i_13_n_0 ),
        .I2(\bil[3]_i_15_n_0 ),
        .O(\tril[3]_i_10_n_0 ));
  LUT6 #(
    .INIT(64'h0E8FF038380EE3F0)) 
    \tril[3]_i_11 
       (.I0(\mil[3]_i_20_n_0 ),
        .I1(\bil[3]_i_15_n_0 ),
        .I2(\bil[3]_i_14_n_0 ),
        .I3(\bil[3]_i_13_n_0 ),
        .I4(\bil[3]_i_16_n_0 ),
        .I5(\mil[3]_i_24_n_0 ),
        .O(\tril[3]_i_11_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair14" *) 
  LUT4 #(
    .INIT(16'h320C)) 
    \tril[3]_i_12 
       (.I0(\bil[3]_i_16_n_0 ),
        .I1(\bil[3]_i_15_n_0 ),
        .I2(\bil[3]_i_13_n_0 ),
        .I3(\bil[3]_i_14_n_0 ),
        .O(\tril[3]_i_12_n_0 ));
  LUT6 #(
    .INIT(64'hF9CFF3FCF18FE3F8)) 
    \tril[3]_i_13 
       (.I0(\mil[3]_i_24_n_0 ),
        .I1(\bil[3]_i_16_n_0 ),
        .I2(\bil[3]_i_13_n_0 ),
        .I3(\bil[3]_i_14_n_0 ),
        .I4(\bil[3]_i_15_n_0 ),
        .I5(\mil[3]_i_20_n_0 ),
        .O(\tril[3]_i_13_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair0" *) 
  LUT5 #(
    .INIT(32'hFFEF0EF0)) 
    \tril[3]_i_14 
       (.I0(\mil[3]_i_23_n_0 ),
        .I1(\mil[3]_i_24_n_0 ),
        .I2(\bil[3]_i_15_n_0 ),
        .I3(\bil[3]_i_13_n_0 ),
        .I4(\bil[3]_i_14_n_0 ),
        .O(\tril[3]_i_14_n_0 ));
  LUT6 #(
    .INIT(64'hF9CFF3FCF18FE3F8)) 
    \tril[3]_i_15 
       (.I0(\mil[3]_i_37_n_0 ),
        .I1(\mil[3]_i_36_n_0 ),
        .I2(\mil[3]_i_33_n_0 ),
        .I3(p_0_in__0[1]),
        .I4(p_0_in__0[2]),
        .I5(\mil[3]_i_32_n_0 ),
        .O(\tril[3]_i_15_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair2" *) 
  LUT5 #(
    .INIT(32'h0FB0CB2C)) 
    \tril[3]_i_2 
       (.I0(\bil[3]_i_10_n_0 ),
        .I1(\tril[3]_i_8_n_0 ),
        .I2(\tril[3]_i_9_n_0 ),
        .I3(\tril[3]_i_10_n_0 ),
        .I4(\tril[3]_i_11_n_0 ),
        .O(\tril[3]_i_2_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair11" *) 
  LUT4 #(
    .INIT(16'h8878)) 
    \tril[3]_i_3 
       (.I0(\tril[3]_i_12_n_0 ),
        .I1(\tril[3]_i_13_n_0 ),
        .I2(\tril[3]_i_10_n_0 ),
        .I3(\tril[3]_i_14_n_0 ),
        .O(\tril[3]_i_3_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair11" *) 
  LUT2 #(
    .INIT(4'h8)) 
    \tril[3]_i_4 
       (.I0(\tril[3]_i_14_n_0 ),
        .I1(\tril[3]_i_10_n_0 ),
        .O(\tril[3]_i_4_n_0 ));
  LUT6 #(
    .INIT(64'h0E8FF038380EE3F0)) 
    \tril[3]_i_5 
       (.I0(\mil[3]_i_9_n_0 ),
        .I1(\tril[3]_i_10_n_0 ),
        .I2(\tril[3]_i_8_n_0 ),
        .I3(\tril[3]_i_9_n_0 ),
        .I4(\tril[3]_i_11_n_0 ),
        .I5(\bil[3]_i_10_n_0 ),
        .O(\tril[3]_i_5_n_0 ));
  LUT6 #(
    .INIT(64'hEFCFCBCEC3FCF3BC)) 
    \tril[3]_i_6 
       (.I0(\bil[3]_i_7_n_0 ),
        .I1(\tril[3]_i_2_n_0 ),
        .I2(\tril[3]_i_3_n_0 ),
        .I3(\tril[3]_i_4_n_0 ),
        .I4(\bil[3]_i_6_n_0 ),
        .I5(\tril[3]_i_5_n_0 ),
        .O(\tril[3]_i_6_n_0 ));
  LUT6 #(
    .INIT(64'h0FC00FC00FC03F80)) 
    \tril[3]_i_7 
       (.I0(\bil[3]_i_7_n_0 ),
        .I1(\tril[3]_i_2_n_0 ),
        .I2(\tril[3]_i_3_n_0 ),
        .I3(\tril[3]_i_4_n_0 ),
        .I4(\tril[3]_i_5_n_0 ),
        .I5(\bil[3]_i_6_n_0 ),
        .O(tril1));
  (* SOFT_HLUTNM = "soft_lutpair14" *) 
  LUT4 #(
    .INIT(16'hA02C)) 
    \tril[3]_i_8 
       (.I0(\tril[3]_i_15_n_0 ),
        .I1(\bil[3]_i_15_n_0 ),
        .I2(\bil[3]_i_14_n_0 ),
        .I3(\bil[3]_i_13_n_0 ),
        .O(\tril[3]_i_8_n_0 ));
  LUT6 #(
    .INIT(64'h00EFEE00F0EE0EF0)) 
    \tril[3]_i_9 
       (.I0(\mil[3]_i_23_n_0 ),
        .I1(\mil[3]_i_24_n_0 ),
        .I2(\bil[3]_i_14_n_0 ),
        .I3(\bil[3]_i_13_n_0 ),
        .I4(\bil[3]_i_15_n_0 ),
        .I5(\bil[3]_i_16_n_0 ),
        .O(\tril[3]_i_9_n_0 ));
  FDRE #(
    .INIT(1'b0)) 
    \tril_reg[0] 
       (.C(clk),
        .CE(1'b1),
        .D(p_5_out[0]),
        .Q(tril[0]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \tril_reg[1] 
       (.C(clk),
        .CE(1'b1),
        .D(p_5_out[1]),
        .Q(tril[1]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \tril_reg[2] 
       (.C(clk),
        .CE(1'b1),
        .D(p_5_out[2]),
        .Q(tril[2]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \tril_reg[3] 
       (.C(clk),
        .CE(1'b1),
        .D(p_5_out[3]),
        .Q(tril[3]),
        .R(1'b0));
  LUT6 #(
    .INIT(64'h9615159656949456)) 
    \un[1]_i_1 
       (.I0(bin[1]),
        .I1(p_0_in__14),
        .I2(\un[3]_i_3_n_0 ),
        .I3(\un[3]_i_4_n_0 ),
        .I4(bin[3]),
        .I5(bin[2]),
        .O(p_0_out[1]));
  LUT6 #(
    .INIT(64'h296C39683968296C)) 
    \un[2]_i_1 
       (.I0(bin[1]),
        .I1(bin[2]),
        .I2(\un[3]_i_3_n_0 ),
        .I3(p_0_in__14),
        .I4(\un[3]_i_4_n_0 ),
        .I5(bin[3]),
        .O(p_0_out[2]));
  LUT6 #(
    .INIT(64'h2C50502C08353508)) 
    \un[3]_i_1 
       (.I0(bin[1]),
        .I1(p_0_in__14),
        .I2(\un[3]_i_3_n_0 ),
        .I3(\un[3]_i_4_n_0 ),
        .I4(bin[3]),
        .I5(bin[2]),
        .O(p_0_out[3]));
  LUT6 #(
    .INIT(64'h3FB3B33FCCFEFECC)) 
    \un[3]_i_10 
       (.I0(bin[7]),
        .I1(p_0_in__8[2]),
        .I2(bin[8]),
        .I3(\cent[3]_i_24_n_0 ),
        .I4(bin[9]),
        .I5(\dec[3]_i_20_n_0 ),
        .O(\un[3]_i_10_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair16" *) 
  LUT4 #(
    .INIT(16'h6966)) 
    \un[3]_i_11 
       (.I0(bin[9]),
        .I1(\cent[3]_i_24_n_0 ),
        .I2(bin[8]),
        .I3(\dec[3]_i_20_n_0 ),
        .O(p_0_in__9[2]));
  LUT4 #(
    .INIT(16'h6966)) 
    \un[3]_i_2 
       (.I0(bin[4]),
        .I1(\un[3]_i_5_n_0 ),
        .I2(bin[3]),
        .I3(\un[3]_i_4_n_0 ),
        .O(p_0_in__14));
  LUT6 #(
    .INIT(64'h3FB3B33FCCFEFECC)) 
    \un[3]_i_3 
       (.I0(bin[2]),
        .I1(p_0_in__13),
        .I2(bin[3]),
        .I3(\un[3]_i_5_n_0 ),
        .I4(bin[4]),
        .I5(\un[3]_i_4_n_0 ),
        .O(\un[3]_i_3_n_0 ));
  LUT6 #(
    .INIT(64'h3FB3B33FCCFEFECC)) 
    \un[3]_i_4 
       (.I0(bin[3]),
        .I1(p_0_in__12),
        .I2(bin[4]),
        .I3(\un[3]_i_8_n_0 ),
        .I4(bin[5]),
        .I5(\un[3]_i_5_n_0 ),
        .O(\un[3]_i_4_n_0 ));
  LUT6 #(
    .INIT(64'h3FB3B33FCCFEFECC)) 
    \un[3]_i_5 
       (.I0(bin[4]),
        .I1(p_0_in__11),
        .I2(bin[5]),
        .I3(\dec[3]_i_13_n_0 ),
        .I4(bin[6]),
        .I5(\un[3]_i_8_n_0 ),
        .O(\un[3]_i_5_n_0 ));
  LUT4 #(
    .INIT(16'h6966)) 
    \un[3]_i_6 
       (.I0(bin[5]),
        .I1(\un[3]_i_8_n_0 ),
        .I2(bin[4]),
        .I3(\un[3]_i_5_n_0 ),
        .O(p_0_in__13));
  LUT4 #(
    .INIT(16'h6966)) 
    \un[3]_i_7 
       (.I0(bin[6]),
        .I1(\dec[3]_i_13_n_0 ),
        .I2(bin[5]),
        .I3(\un[3]_i_8_n_0 ),
        .O(p_0_in__12));
  LUT6 #(
    .INIT(64'h0EB33EB0C83FFC2C)) 
    \un[3]_i_8 
       (.I0(bin[5]),
        .I1(p_0_in__9[1]),
        .I2(bin[7]),
        .I3(\un[3]_i_10_n_0 ),
        .I4(p_0_in__9[2]),
        .I5(bin[6]),
        .O(\un[3]_i_8_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair16" *) 
  LUT2 #(
    .INIT(4'h6)) 
    \un[3]_i_9 
       (.I0(\dec[3]_i_20_n_0 ),
        .I1(bin[8]),
        .O(p_0_in__9[1]));
  FDRE #(
    .INIT(1'b0)) 
    \un_reg[0] 
       (.C(clk),
        .CE(1'b1),
        .D(bin[0]),
        .Q(un[0]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \un_reg[1] 
       (.C(clk),
        .CE(1'b1),
        .D(p_0_out[1]),
        .Q(un[1]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \un_reg[2] 
       (.C(clk),
        .CE(1'b1),
        .D(p_0_out[2]),
        .Q(un[2]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \un_reg[3] 
       (.C(clk),
        .CE(1'b1),
        .D(p_0_out[3]),
        .Q(un[3]),
        .R(1'b0));
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
