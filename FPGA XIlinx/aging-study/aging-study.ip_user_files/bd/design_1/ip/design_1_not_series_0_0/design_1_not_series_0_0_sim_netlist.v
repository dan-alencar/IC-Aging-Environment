// Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
// Copyright 2022-2024 Advanced Micro Devices, Inc. All Rights Reserved.
// --------------------------------------------------------------------------------
// Tool Version: Vivado v.2024.2 (lin64) Build 5239630 Fri Nov 08 22:34:34 MST 2024
// Date        : Fri Apr 25 13:46:59 2025
// Host        : alisson.lesc.ufc.br running 64-bit unknown
// Command     : write_verilog -force -mode funcsim
//               /home/alisson/Downloads/aging_mirai_tensao/Aging-dynamic/vivado_project/aging-study/aging-study.gen/sources_1/bd/design_1/ip/design_1_not_series_0_0/design_1_not_series_0_0_sim_netlist.v
// Design      : design_1_not_series_0_0
// Purpose     : This verilog netlist is a functional simulation representation of the design and should not be modified
//               or synthesized. This netlist cannot be used for SDF annotated simulation.
// Device      : xc7a100tcsg324-1
// --------------------------------------------------------------------------------
`timescale 1 ps / 1 ps

(* CHECK_LICENSE_TYPE = "design_1_not_series_0_0,not_series,{}" *) (* DowngradeIPIdentifiedWarnings = "yes" *) (* IP_DEFINITION_SOURCE = "module_ref" *) 
(* X_CORE_INFO = "not_series,Vivado 2024.2" *) 
(* NotValidForBitStream *)
module design_1_not_series_0_0
   (clk,
    test_bit,
    start,
    critpath);
  (* X_INTERFACE_INFO = "xilinx.com:signal:clock:1.0 clk CLK" *) (* X_INTERFACE_MODE = "slave" *) (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME clk, FREQ_HZ 60000000, FREQ_TOLERANCE_HZ 0, PHASE 0.0, CLK_DOMAIN /clk_wiz_0_clk_out1, INSERT_VIP 0" *) input clk;
  input test_bit;
  output start;
  output critpath;

  wire clk;
  wire critpath;
  wire start;
  wire test_bit;

  design_1_not_series_0_0_not_series inst
       (.clk(clk),
        .critpath(critpath),
        .start(start),
        .test_bit(test_bit));
endmodule

(* ORIG_REF_NAME = "not_series" *) 
module design_1_not_series_0_0_not_series
   (start,
    critpath,
    test_bit,
    clk);
  output start;
  output critpath;
  input test_bit;
  input clk;

  wire clk;
  wire connection_1;
  wire connection_10;
  wire connection_11;
  wire connection_12;
  wire connection_13;
  wire connection_14;
  wire connection_15;
  wire connection_16;
  wire connection_17;
  wire connection_18;
  wire connection_19;
  wire connection_2;
  wire connection_20;
  wire connection_21;
  wire connection_22;
  wire connection_23;
  wire connection_24;
  wire connection_25;
  wire connection_26;
  wire connection_27;
  wire connection_28;
  wire connection_29;
  wire connection_3;
  wire connection_30;
  wire connection_31;
  wire connection_32;
  wire connection_33;
  wire connection_34;
  wire connection_35;
  wire connection_36;
  wire connection_37;
  wire connection_38;
  wire connection_39;
  wire connection_4;
  wire connection_40;
  wire connection_41;
  wire connection_42;
  wire connection_43;
  wire connection_44;
  wire connection_45;
  wire connection_46;
  wire connection_47;
  wire connection_48;
  wire connection_49;
  wire connection_5;
  wire connection_6;
  wire connection_7;
  wire connection_8;
  wire connection_9;
  wire critpath;
  wire start;
  wire test_bit;

  (* BOX_TYPE = "PRIMITIVE" *) 
  (* DONT_TOUCH *) 
  (* XILINX_LEGACY_PRIM = "LUT1_L" *) 
  (* XILINX_TRANSFORM_PINMAP = "LO:O" *) 
  LUT1 #(
    .INIT(2'h1)) 
    \genblk1[0].INV 
       (.I0(start),
        .O(connection_1));
  (* BOX_TYPE = "PRIMITIVE" *) 
  (* DONT_TOUCH *) 
  (* XILINX_LEGACY_PRIM = "LUT1_L" *) 
  (* XILINX_TRANSFORM_PINMAP = "LO:O" *) 
  LUT1 #(
    .INIT(2'h1)) 
    \genblk1[10].INV 
       (.I0(connection_10),
        .O(connection_11));
  (* BOX_TYPE = "PRIMITIVE" *) 
  (* DONT_TOUCH *) 
  (* XILINX_LEGACY_PRIM = "LUT1_L" *) 
  (* XILINX_TRANSFORM_PINMAP = "LO:O" *) 
  LUT1 #(
    .INIT(2'h1)) 
    \genblk1[11].INV 
       (.I0(connection_11),
        .O(connection_12));
  (* BOX_TYPE = "PRIMITIVE" *) 
  (* DONT_TOUCH *) 
  (* XILINX_LEGACY_PRIM = "LUT1_L" *) 
  (* XILINX_TRANSFORM_PINMAP = "LO:O" *) 
  LUT1 #(
    .INIT(2'h1)) 
    \genblk1[12].INV 
       (.I0(connection_12),
        .O(connection_13));
  (* BOX_TYPE = "PRIMITIVE" *) 
  (* DONT_TOUCH *) 
  (* XILINX_LEGACY_PRIM = "LUT1_L" *) 
  (* XILINX_TRANSFORM_PINMAP = "LO:O" *) 
  LUT1 #(
    .INIT(2'h1)) 
    \genblk1[13].INV 
       (.I0(connection_13),
        .O(connection_14));
  (* BOX_TYPE = "PRIMITIVE" *) 
  (* DONT_TOUCH *) 
  (* XILINX_LEGACY_PRIM = "LUT1_L" *) 
  (* XILINX_TRANSFORM_PINMAP = "LO:O" *) 
  LUT1 #(
    .INIT(2'h1)) 
    \genblk1[14].INV 
       (.I0(connection_14),
        .O(connection_15));
  (* BOX_TYPE = "PRIMITIVE" *) 
  (* DONT_TOUCH *) 
  (* XILINX_LEGACY_PRIM = "LUT1_L" *) 
  (* XILINX_TRANSFORM_PINMAP = "LO:O" *) 
  LUT1 #(
    .INIT(2'h1)) 
    \genblk1[15].INV 
       (.I0(connection_15),
        .O(connection_16));
  (* BOX_TYPE = "PRIMITIVE" *) 
  (* DONT_TOUCH *) 
  (* XILINX_LEGACY_PRIM = "LUT1_L" *) 
  (* XILINX_TRANSFORM_PINMAP = "LO:O" *) 
  LUT1 #(
    .INIT(2'h1)) 
    \genblk1[16].INV 
       (.I0(connection_16),
        .O(connection_17));
  (* BOX_TYPE = "PRIMITIVE" *) 
  (* DONT_TOUCH *) 
  (* XILINX_LEGACY_PRIM = "LUT1_L" *) 
  (* XILINX_TRANSFORM_PINMAP = "LO:O" *) 
  LUT1 #(
    .INIT(2'h1)) 
    \genblk1[17].INV 
       (.I0(connection_17),
        .O(connection_18));
  (* BOX_TYPE = "PRIMITIVE" *) 
  (* DONT_TOUCH *) 
  (* XILINX_LEGACY_PRIM = "LUT1_L" *) 
  (* XILINX_TRANSFORM_PINMAP = "LO:O" *) 
  LUT1 #(
    .INIT(2'h1)) 
    \genblk1[18].INV 
       (.I0(connection_18),
        .O(connection_19));
  (* BOX_TYPE = "PRIMITIVE" *) 
  (* DONT_TOUCH *) 
  (* XILINX_LEGACY_PRIM = "LUT1_L" *) 
  (* XILINX_TRANSFORM_PINMAP = "LO:O" *) 
  LUT1 #(
    .INIT(2'h1)) 
    \genblk1[19].INV 
       (.I0(connection_19),
        .O(connection_20));
  (* BOX_TYPE = "PRIMITIVE" *) 
  (* DONT_TOUCH *) 
  (* XILINX_LEGACY_PRIM = "LUT1_L" *) 
  (* XILINX_TRANSFORM_PINMAP = "LO:O" *) 
  LUT1 #(
    .INIT(2'h1)) 
    \genblk1[1].INV 
       (.I0(connection_1),
        .O(connection_2));
  (* BOX_TYPE = "PRIMITIVE" *) 
  (* DONT_TOUCH *) 
  (* XILINX_LEGACY_PRIM = "LUT1_L" *) 
  (* XILINX_TRANSFORM_PINMAP = "LO:O" *) 
  LUT1 #(
    .INIT(2'h1)) 
    \genblk1[20].INV 
       (.I0(connection_20),
        .O(connection_21));
  (* BOX_TYPE = "PRIMITIVE" *) 
  (* DONT_TOUCH *) 
  (* XILINX_LEGACY_PRIM = "LUT1_L" *) 
  (* XILINX_TRANSFORM_PINMAP = "LO:O" *) 
  LUT1 #(
    .INIT(2'h1)) 
    \genblk1[21].INV 
       (.I0(connection_21),
        .O(connection_22));
  (* BOX_TYPE = "PRIMITIVE" *) 
  (* DONT_TOUCH *) 
  (* XILINX_LEGACY_PRIM = "LUT1_L" *) 
  (* XILINX_TRANSFORM_PINMAP = "LO:O" *) 
  LUT1 #(
    .INIT(2'h1)) 
    \genblk1[22].INV 
       (.I0(connection_22),
        .O(connection_23));
  (* BOX_TYPE = "PRIMITIVE" *) 
  (* DONT_TOUCH *) 
  (* XILINX_LEGACY_PRIM = "LUT1_L" *) 
  (* XILINX_TRANSFORM_PINMAP = "LO:O" *) 
  LUT1 #(
    .INIT(2'h1)) 
    \genblk1[23].INV 
       (.I0(connection_23),
        .O(connection_24));
  (* BOX_TYPE = "PRIMITIVE" *) 
  (* DONT_TOUCH *) 
  (* XILINX_LEGACY_PRIM = "LUT1_L" *) 
  (* XILINX_TRANSFORM_PINMAP = "LO:O" *) 
  LUT1 #(
    .INIT(2'h1)) 
    \genblk1[24].INV 
       (.I0(connection_24),
        .O(connection_25));
  (* BOX_TYPE = "PRIMITIVE" *) 
  (* DONT_TOUCH *) 
  (* XILINX_LEGACY_PRIM = "LUT1_L" *) 
  (* XILINX_TRANSFORM_PINMAP = "LO:O" *) 
  LUT1 #(
    .INIT(2'h1)) 
    \genblk1[25].INV 
       (.I0(connection_25),
        .O(connection_26));
  (* BOX_TYPE = "PRIMITIVE" *) 
  (* DONT_TOUCH *) 
  (* XILINX_LEGACY_PRIM = "LUT1_L" *) 
  (* XILINX_TRANSFORM_PINMAP = "LO:O" *) 
  LUT1 #(
    .INIT(2'h1)) 
    \genblk1[26].INV 
       (.I0(connection_26),
        .O(connection_27));
  (* BOX_TYPE = "PRIMITIVE" *) 
  (* DONT_TOUCH *) 
  (* XILINX_LEGACY_PRIM = "LUT1_L" *) 
  (* XILINX_TRANSFORM_PINMAP = "LO:O" *) 
  LUT1 #(
    .INIT(2'h1)) 
    \genblk1[27].INV 
       (.I0(connection_27),
        .O(connection_28));
  (* BOX_TYPE = "PRIMITIVE" *) 
  (* DONT_TOUCH *) 
  (* XILINX_LEGACY_PRIM = "LUT1_L" *) 
  (* XILINX_TRANSFORM_PINMAP = "LO:O" *) 
  LUT1 #(
    .INIT(2'h1)) 
    \genblk1[28].INV 
       (.I0(connection_28),
        .O(connection_29));
  (* BOX_TYPE = "PRIMITIVE" *) 
  (* DONT_TOUCH *) 
  (* XILINX_LEGACY_PRIM = "LUT1_L" *) 
  (* XILINX_TRANSFORM_PINMAP = "LO:O" *) 
  LUT1 #(
    .INIT(2'h1)) 
    \genblk1[29].INV 
       (.I0(connection_29),
        .O(connection_30));
  (* BOX_TYPE = "PRIMITIVE" *) 
  (* DONT_TOUCH *) 
  (* XILINX_LEGACY_PRIM = "LUT1_L" *) 
  (* XILINX_TRANSFORM_PINMAP = "LO:O" *) 
  LUT1 #(
    .INIT(2'h1)) 
    \genblk1[2].INV 
       (.I0(connection_2),
        .O(connection_3));
  (* BOX_TYPE = "PRIMITIVE" *) 
  (* DONT_TOUCH *) 
  (* XILINX_LEGACY_PRIM = "LUT1_L" *) 
  (* XILINX_TRANSFORM_PINMAP = "LO:O" *) 
  LUT1 #(
    .INIT(2'h1)) 
    \genblk1[30].INV 
       (.I0(connection_30),
        .O(connection_31));
  (* BOX_TYPE = "PRIMITIVE" *) 
  (* DONT_TOUCH *) 
  (* XILINX_LEGACY_PRIM = "LUT1_L" *) 
  (* XILINX_TRANSFORM_PINMAP = "LO:O" *) 
  LUT1 #(
    .INIT(2'h1)) 
    \genblk1[31].INV 
       (.I0(connection_31),
        .O(connection_32));
  (* BOX_TYPE = "PRIMITIVE" *) 
  (* DONT_TOUCH *) 
  (* XILINX_LEGACY_PRIM = "LUT1_L" *) 
  (* XILINX_TRANSFORM_PINMAP = "LO:O" *) 
  LUT1 #(
    .INIT(2'h1)) 
    \genblk1[32].INV 
       (.I0(connection_32),
        .O(connection_33));
  (* BOX_TYPE = "PRIMITIVE" *) 
  (* DONT_TOUCH *) 
  (* XILINX_LEGACY_PRIM = "LUT1_L" *) 
  (* XILINX_TRANSFORM_PINMAP = "LO:O" *) 
  LUT1 #(
    .INIT(2'h1)) 
    \genblk1[33].INV 
       (.I0(connection_33),
        .O(connection_34));
  (* BOX_TYPE = "PRIMITIVE" *) 
  (* DONT_TOUCH *) 
  (* XILINX_LEGACY_PRIM = "LUT1_L" *) 
  (* XILINX_TRANSFORM_PINMAP = "LO:O" *) 
  LUT1 #(
    .INIT(2'h1)) 
    \genblk1[34].INV 
       (.I0(connection_34),
        .O(connection_35));
  (* BOX_TYPE = "PRIMITIVE" *) 
  (* DONT_TOUCH *) 
  (* XILINX_LEGACY_PRIM = "LUT1_L" *) 
  (* XILINX_TRANSFORM_PINMAP = "LO:O" *) 
  LUT1 #(
    .INIT(2'h1)) 
    \genblk1[35].INV 
       (.I0(connection_35),
        .O(connection_36));
  (* BOX_TYPE = "PRIMITIVE" *) 
  (* DONT_TOUCH *) 
  (* XILINX_LEGACY_PRIM = "LUT1_L" *) 
  (* XILINX_TRANSFORM_PINMAP = "LO:O" *) 
  LUT1 #(
    .INIT(2'h1)) 
    \genblk1[36].INV 
       (.I0(connection_36),
        .O(connection_37));
  (* BOX_TYPE = "PRIMITIVE" *) 
  (* DONT_TOUCH *) 
  (* XILINX_LEGACY_PRIM = "LUT1_L" *) 
  (* XILINX_TRANSFORM_PINMAP = "LO:O" *) 
  LUT1 #(
    .INIT(2'h1)) 
    \genblk1[37].INV 
       (.I0(connection_37),
        .O(connection_38));
  (* BOX_TYPE = "PRIMITIVE" *) 
  (* DONT_TOUCH *) 
  (* XILINX_LEGACY_PRIM = "LUT1_L" *) 
  (* XILINX_TRANSFORM_PINMAP = "LO:O" *) 
  LUT1 #(
    .INIT(2'h1)) 
    \genblk1[38].INV 
       (.I0(connection_38),
        .O(connection_39));
  (* BOX_TYPE = "PRIMITIVE" *) 
  (* DONT_TOUCH *) 
  (* XILINX_LEGACY_PRIM = "LUT1_L" *) 
  (* XILINX_TRANSFORM_PINMAP = "LO:O" *) 
  LUT1 #(
    .INIT(2'h1)) 
    \genblk1[39].INV 
       (.I0(connection_39),
        .O(connection_40));
  (* BOX_TYPE = "PRIMITIVE" *) 
  (* DONT_TOUCH *) 
  (* XILINX_LEGACY_PRIM = "LUT1_L" *) 
  (* XILINX_TRANSFORM_PINMAP = "LO:O" *) 
  LUT1 #(
    .INIT(2'h1)) 
    \genblk1[3].INV 
       (.I0(connection_3),
        .O(connection_4));
  (* BOX_TYPE = "PRIMITIVE" *) 
  (* DONT_TOUCH *) 
  (* XILINX_LEGACY_PRIM = "LUT1_L" *) 
  (* XILINX_TRANSFORM_PINMAP = "LO:O" *) 
  LUT1 #(
    .INIT(2'h1)) 
    \genblk1[40].INV 
       (.I0(connection_40),
        .O(connection_41));
  (* BOX_TYPE = "PRIMITIVE" *) 
  (* DONT_TOUCH *) 
  (* XILINX_LEGACY_PRIM = "LUT1_L" *) 
  (* XILINX_TRANSFORM_PINMAP = "LO:O" *) 
  LUT1 #(
    .INIT(2'h1)) 
    \genblk1[41].INV 
       (.I0(connection_41),
        .O(connection_42));
  (* BOX_TYPE = "PRIMITIVE" *) 
  (* DONT_TOUCH *) 
  (* XILINX_LEGACY_PRIM = "LUT1_L" *) 
  (* XILINX_TRANSFORM_PINMAP = "LO:O" *) 
  LUT1 #(
    .INIT(2'h1)) 
    \genblk1[42].INV 
       (.I0(connection_42),
        .O(connection_43));
  (* BOX_TYPE = "PRIMITIVE" *) 
  (* DONT_TOUCH *) 
  (* XILINX_LEGACY_PRIM = "LUT1_L" *) 
  (* XILINX_TRANSFORM_PINMAP = "LO:O" *) 
  LUT1 #(
    .INIT(2'h1)) 
    \genblk1[43].INV 
       (.I0(connection_43),
        .O(connection_44));
  (* BOX_TYPE = "PRIMITIVE" *) 
  (* DONT_TOUCH *) 
  (* XILINX_LEGACY_PRIM = "LUT1_L" *) 
  (* XILINX_TRANSFORM_PINMAP = "LO:O" *) 
  LUT1 #(
    .INIT(2'h1)) 
    \genblk1[44].INV 
       (.I0(connection_44),
        .O(connection_45));
  (* BOX_TYPE = "PRIMITIVE" *) 
  (* DONT_TOUCH *) 
  (* XILINX_LEGACY_PRIM = "LUT1_L" *) 
  (* XILINX_TRANSFORM_PINMAP = "LO:O" *) 
  LUT1 #(
    .INIT(2'h1)) 
    \genblk1[45].INV 
       (.I0(connection_45),
        .O(connection_46));
  (* BOX_TYPE = "PRIMITIVE" *) 
  (* DONT_TOUCH *) 
  (* XILINX_LEGACY_PRIM = "LUT1_L" *) 
  (* XILINX_TRANSFORM_PINMAP = "LO:O" *) 
  LUT1 #(
    .INIT(2'h1)) 
    \genblk1[46].INV 
       (.I0(connection_46),
        .O(connection_47));
  (* BOX_TYPE = "PRIMITIVE" *) 
  (* DONT_TOUCH *) 
  (* XILINX_LEGACY_PRIM = "LUT1_L" *) 
  (* XILINX_TRANSFORM_PINMAP = "LO:O" *) 
  LUT1 #(
    .INIT(2'h1)) 
    \genblk1[47].INV 
       (.I0(connection_47),
        .O(connection_48));
  (* BOX_TYPE = "PRIMITIVE" *) 
  (* DONT_TOUCH *) 
  (* XILINX_LEGACY_PRIM = "LUT1_L" *) 
  (* XILINX_TRANSFORM_PINMAP = "LO:O" *) 
  LUT1 #(
    .INIT(2'h1)) 
    \genblk1[48].INV 
       (.I0(connection_48),
        .O(connection_49));
  (* BOX_TYPE = "PRIMITIVE" *) 
  (* DONT_TOUCH *) 
  (* XILINX_LEGACY_PRIM = "LUT1_L" *) 
  (* XILINX_TRANSFORM_PINMAP = "LO:O" *) 
  LUT1 #(
    .INIT(2'h1)) 
    \genblk1[49].INV 
       (.I0(connection_49),
        .O(critpath));
  (* BOX_TYPE = "PRIMITIVE" *) 
  (* DONT_TOUCH *) 
  (* XILINX_LEGACY_PRIM = "LUT1_L" *) 
  (* XILINX_TRANSFORM_PINMAP = "LO:O" *) 
  LUT1 #(
    .INIT(2'h1)) 
    \genblk1[4].INV 
       (.I0(connection_4),
        .O(connection_5));
  (* BOX_TYPE = "PRIMITIVE" *) 
  (* DONT_TOUCH *) 
  (* XILINX_LEGACY_PRIM = "LUT1_L" *) 
  (* XILINX_TRANSFORM_PINMAP = "LO:O" *) 
  LUT1 #(
    .INIT(2'h1)) 
    \genblk1[5].INV 
       (.I0(connection_5),
        .O(connection_6));
  (* BOX_TYPE = "PRIMITIVE" *) 
  (* DONT_TOUCH *) 
  (* XILINX_LEGACY_PRIM = "LUT1_L" *) 
  (* XILINX_TRANSFORM_PINMAP = "LO:O" *) 
  LUT1 #(
    .INIT(2'h1)) 
    \genblk1[6].INV 
       (.I0(connection_6),
        .O(connection_7));
  (* BOX_TYPE = "PRIMITIVE" *) 
  (* DONT_TOUCH *) 
  (* XILINX_LEGACY_PRIM = "LUT1_L" *) 
  (* XILINX_TRANSFORM_PINMAP = "LO:O" *) 
  LUT1 #(
    .INIT(2'h1)) 
    \genblk1[7].INV 
       (.I0(connection_7),
        .O(connection_8));
  (* BOX_TYPE = "PRIMITIVE" *) 
  (* DONT_TOUCH *) 
  (* XILINX_LEGACY_PRIM = "LUT1_L" *) 
  (* XILINX_TRANSFORM_PINMAP = "LO:O" *) 
  LUT1 #(
    .INIT(2'h1)) 
    \genblk1[8].INV 
       (.I0(connection_8),
        .O(connection_9));
  (* BOX_TYPE = "PRIMITIVE" *) 
  (* DONT_TOUCH *) 
  (* XILINX_LEGACY_PRIM = "LUT1_L" *) 
  (* XILINX_TRANSFORM_PINMAP = "LO:O" *) 
  LUT1 #(
    .INIT(2'h1)) 
    \genblk1[9].INV 
       (.I0(connection_9),
        .O(connection_10));
  FDRE start_reg
       (.C(clk),
        .CE(1'b1),
        .D(test_bit),
        .Q(start),
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
