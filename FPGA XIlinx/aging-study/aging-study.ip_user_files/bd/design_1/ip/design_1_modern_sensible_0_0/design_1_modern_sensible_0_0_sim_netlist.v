// Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
// Copyright 2022-2024 Advanced Micro Devices, Inc. All Rights Reserved.
// --------------------------------------------------------------------------------
// Tool Version: Vivado v.2024.2 (lin64) Build 5239630 Fri Nov 08 22:34:34 MST 2024
// Date        : Fri Apr 25 14:25:14 2025
// Host        : alisson.lesc.ufc.br running 64-bit unknown
// Command     : write_verilog -force -mode funcsim
//               /home/alisson/Downloads/aging_mirai_tensao/Aging-dynamic/vivado_project/aging-study/aging-study.gen/sources_1/bd/design_1/ip/design_1_modern_sensible_0_0/design_1_modern_sensible_0_0_sim_netlist.v
// Design      : design_1_modern_sensible_0_0
// Purpose     : This verilog netlist is a functional simulation representation of the design and should not be modified
//               or synthesized. This netlist cannot be used for SDF annotated simulation.
// Device      : xc7a100tcsg324-1
// --------------------------------------------------------------------------------
`timescale 1 ps / 1 ps

(* CHECK_LICENSE_TYPE = "design_1_modern_sensible_0_0,modern_sensible,{}" *) (* DowngradeIPIdentifiedWarnings = "yes" *) (* IP_DEFINITION_SOURCE = "module_ref" *) 
(* X_CORE_INFO = "modern_sensible,Vivado 2024.2" *) 
(* NotValidForBitStream *)
module design_1_modern_sensible_0_0
   (sclk,
    psclk,
    in_sensor,
    reset,
    clk_en,
    alarm,
    ff1_out);
  input sclk;
  input psclk;
  input in_sensor;
  (* X_INTERFACE_INFO = "xilinx.com:signal:reset:1.0 reset RST" *) (* X_INTERFACE_MODE = "slave" *) (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME reset, POLARITY ACTIVE_LOW, INSERT_VIP 0" *) input reset;
  input clk_en;
  output alarm;
  output ff1_out;

  wire alarm;
  wire clk_en;
  wire ff1_out;
  wire in_sensor;
  wire psclk;
  wire reset;
  wire sclk;

  design_1_modern_sensible_0_0_modern_sensible inst
       (.alarm(alarm),
        .clk_en(clk_en),
        .ff1_out(ff1_out),
        .in_sensor(in_sensor),
        .psclk(psclk),
        .reset(reset),
        .sclk(sclk));
endmodule

(* ORIG_REF_NAME = "modern_sensible" *) 
module design_1_modern_sensible_0_0_modern_sensible
   (ff1_out,
    alarm,
    in_sensor,
    psclk,
    reset,
    sclk,
    clk_en);
  output ff1_out;
  output alarm;
  input in_sensor;
  input psclk;
  input reset;
  input sclk;
  input clk_en;

  wire alarm;
  wire clk_en;
  wire ff1;
  wire ff1_out;
  wire in_sensor;
  wire psclk;
  wire reset;
  wire sclk;
  wire xor_out;

  (* AREA_GROUP = "sensor" *) 
  (* BOX_TYPE = "PRIMITIVE" *) 
  (* DONT_TOUCH *) 
  (* U_SET = "sensor" *) 
  FDCE #(
    .INIT(1'b0),
    .IS_CLR_INVERTED(1'b0),
    .IS_C_INVERTED(1'b0),
    .IS_D_INVERTED(1'b0)) 
    FF1
       (.C(psclk),
        .CE(1'b1),
        .CLR(reset),
        .D(in_sensor),
        .Q(ff1));
  (* AREA_GROUP = "sensor" *) 
  (* BOX_TYPE = "PRIMITIVE" *) 
  (* DONT_TOUCH *) 
  (* U_SET = "sensor" *) 
  FDCE #(
    .INIT(1'b0),
    .IS_CLR_INVERTED(1'b0),
    .IS_C_INVERTED(1'b0),
    .IS_D_INVERTED(1'b0)) 
    FF2
       (.C(sclk),
        .CE(1'b1),
        .CLR(reset),
        .D(in_sensor),
        .Q(ff1_out));
  (* AREA_GROUP = "sensor" *) 
  (* BOX_TYPE = "PRIMITIVE" *) 
  (* DONT_TOUCH *) 
  (* U_SET = "sensor" *) 
  FDCE #(
    .INIT(1'b0),
    .IS_CLR_INVERTED(1'b0),
    .IS_C_INVERTED(1'b0),
    .IS_D_INVERTED(1'b0)) 
    FF3
       (.C(clk_en),
        .CE(1'b1),
        .CLR(reset),
        .D(xor_out),
        .Q(alarm));
  (* AREA_GROUP = "sensor" *) 
  (* BOX_TYPE = "PRIMITIVE" *) 
  (* DONT_TOUCH *) 
  (* U_SET = "sensor" *) 
  (* XILINX_LEGACY_PRIM = "LUT2_L" *) 
  (* XILINX_TRANSFORM_PINMAP = "LO:O" *) 
  LUT2 #(
    .INIT(4'h6)) 
    XOR1
       (.I0(ff1),
        .I1(ff1_out),
        .O(xor_out));
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
