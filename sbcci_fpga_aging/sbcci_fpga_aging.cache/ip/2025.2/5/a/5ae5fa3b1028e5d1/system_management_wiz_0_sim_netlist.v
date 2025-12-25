// Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
// Copyright 2022-2025 Advanced Micro Devices, Inc. All Rights Reserved.
// --------------------------------------------------------------------------------
// Tool Version: Vivado v.2025.2 (lin64) Build 6299465 Fri Nov 14 12:34:56 MST 2025
// Date        : Tue Dec 23 16:59:47 2025
// Host        : dan-alencar running 64-bit Linux Mint 22.2
// Command     : write_verilog -force -mode funcsim -rename_top decalper_eb_ot_sdeen_pot_pi_dehcac_xnilix -prefix
//               decalper_eb_ot_sdeen_pot_pi_dehcac_xnilix_ system_management_wiz_0_sim_netlist.v
// Design      : system_management_wiz_0
// Purpose     : This verilog netlist is a functional simulation representation of the design and should not be modified
//               or synthesized. This netlist cannot be used for SDF annotated simulation.
// Device      : xcau15p-ffvb676-1-i
// --------------------------------------------------------------------------------
`timescale 1 ps / 1 ps

(* NotValidForBitStream *)
module decalper_eb_ot_sdeen_pot_pi_dehcac_xnilix
   (daddr_in,
    dclk_in,
    den_in,
    di_in,
    dwe_in,
    reset_in,
    vp,
    vn,
    busy_out,
    channel_out,
    do_out,
    drdy_out,
    eoc_out,
    eos_out,
    ot_out,
    vccaux_alarm_out,
    vccint_alarm_out,
    user_temp_alarm_out,
    alarm_out);
  input [7:0]daddr_in;
  input dclk_in;
  input den_in;
  input [15:0]di_in;
  input dwe_in;
  input reset_in;
  input vp;
  input vn;
  output busy_out;
  output [5:0]channel_out;
  output [15:0]do_out;
  output drdy_out;
  output eoc_out;
  output eos_out;
  output ot_out;
  output vccaux_alarm_out;
  output vccint_alarm_out;
  output user_temp_alarm_out;
  output alarm_out;

  wire alarm_out;
  wire busy_out;
  wire [5:0]channel_out;
  wire [7:0]daddr_in;
  wire dclk_in;
  wire den_in;
  wire [15:0]di_in;
  wire [15:0]do_out;
  wire drdy_out;
  wire dwe_in;
  wire eoc_out;
  wire eos_out;
  wire ot_out;
  wire reset_in;
  wire user_temp_alarm_out;
  wire vccaux_alarm_out;
  wire vccint_alarm_out;
  wire vn;
  wire vp;

  decalper_eb_ot_sdeen_pot_pi_dehcac_xnilix_system_management_wiz_0_sysmon inst
       (.alarm_out(alarm_out),
        .busy_out(busy_out),
        .channel_out(channel_out),
        .daddr_in(daddr_in),
        .dclk_in(dclk_in),
        .den_in(den_in),
        .di_in(di_in),
        .do_out(do_out),
        .drdy_out(drdy_out),
        .dwe_in(dwe_in),
        .eoc_out(eoc_out),
        .eos_out(eos_out),
        .ot_out(ot_out),
        .reset_in(reset_in),
        .user_temp_alarm_out(user_temp_alarm_out),
        .vccaux_alarm_out(vccaux_alarm_out),
        .vccint_alarm_out(vccint_alarm_out),
        .vn(vn),
        .vp(vp));
endmodule

module decalper_eb_ot_sdeen_pot_pi_dehcac_xnilix_system_management_wiz_0_sysmon
   (daddr_in,
    dclk_in,
    den_in,
    di_in,
    dwe_in,
    reset_in,
    vp,
    vn,
    busy_out,
    channel_out,
    do_out,
    drdy_out,
    eoc_out,
    eos_out,
    ot_out,
    vccaux_alarm_out,
    vccint_alarm_out,
    user_temp_alarm_out,
    alarm_out);
  input [7:0]daddr_in;
  input dclk_in;
  input den_in;
  input [15:0]di_in;
  input dwe_in;
  input reset_in;
  input vp;
  input vn;
  output busy_out;
  output [5:0]channel_out;
  output [15:0]do_out;
  output drdy_out;
  output eoc_out;
  output eos_out;
  output ot_out;
  output vccaux_alarm_out;
  output vccint_alarm_out;
  output user_temp_alarm_out;
  output alarm_out;

  wire alarm_out;
  wire busy_out;
  wire [5:0]channel_out;
  wire [7:0]daddr_in;
  wire dclk_in;
  wire den_in;
  wire [15:0]di_in;
  wire [15:0]do_out;
  wire drdy_out;
  wire dwe_in;
  wire eoc_out;
  wire eos_out;
  wire ot_out;
  wire reset_in;
  wire user_temp_alarm_out;
  wire vccaux_alarm_out;
  wire vccint_alarm_out;
  wire vn;
  wire vp;
  wire NLW_inst_sysmon_I2C_SCLK_TS_UNCONNECTED;
  wire NLW_inst_sysmon_I2C_SDA_TS_UNCONNECTED;
  wire NLW_inst_sysmon_JTAGBUSY_UNCONNECTED;
  wire NLW_inst_sysmon_JTAGLOCKED_UNCONNECTED;
  wire NLW_inst_sysmon_JTAGMODIFIED_UNCONNECTED;
  wire NLW_inst_sysmon_SMBALERT_TS_UNCONNECTED;
  wire [15:0]NLW_inst_sysmon_ADC_DATA_UNCONNECTED;
  wire [15:3]NLW_inst_sysmon_ALM_UNCONNECTED;
  wire [4:0]NLW_inst_sysmon_MUXADDR_UNCONNECTED;

  (* BOX_TYPE = "PRIMITIVE" *) 
  (* DONT_TOUCH *) 
  SYSMONE4 #(
    .COMMON_N_SOURCE(16'hFFFF),
    .INIT_40(16'h0000),
    .INIT_41(16'h2F90),
    .INIT_42(16'h1400),
    .INIT_43(16'h200F),
    .INIT_44(16'h0000),
    .INIT_45(16'hE200),
    .INIT_46(16'h0000),
    .INIT_47(16'h0000),
    .INIT_48(16'h4F01),
    .INIT_49(16'h0000),
    .INIT_4A(16'h0000),
    .INIT_4B(16'h0000),
    .INIT_4C(16'h0000),
    .INIT_4D(16'h0000),
    .INIT_4E(16'h0000),
    .INIT_4F(16'h0000),
    .INIT_50(16'hB794),
    .INIT_51(16'h4E81),
    .INIT_52(16'hA147),
    .INIT_53(16'hCBA3),
    .INIT_54(16'hAB02),
    .INIT_55(16'h4963),
    .INIT_56(16'h9555),
    .INIT_57(16'hB00A),
    .INIT_58(16'h4E81),
    .INIT_59(16'h4963),
    .INIT_5A(16'h4963),
    .INIT_5B(16'h9A74),
    .INIT_5C(16'h4963),
    .INIT_5D(16'h451E),
    .INIT_5E(16'h451E),
    .INIT_5F(16'h91EB),
    .INIT_60(16'h4D39),
    .INIT_61(16'h4DA7),
    .INIT_62(16'h9A74),
    .INIT_63(16'h9A74),
    .INIT_64(16'h0000),
    .INIT_65(16'h0000),
    .INIT_66(16'h0000),
    .INIT_67(16'h0000),
    .INIT_68(16'h4C5E),
    .INIT_69(16'h4BF2),
    .INIT_6A(16'h98BF),
    .INIT_6B(16'h98BF),
    .INIT_6C(16'h0000),
    .INIT_6D(16'h0000),
    .INIT_6E(16'h0000),
    .INIT_6F(16'h0000),
    .INIT_70(16'h0000),
    .INIT_71(16'h0000),
    .INIT_72(16'h0000),
    .INIT_73(16'h0000),
    .INIT_74(16'h0000),
    .INIT_75(16'h0000),
    .INIT_76(16'h0000),
    .INIT_77(16'h0000),
    .INIT_78(16'h0000),
    .INIT_79(16'h0000),
    .INIT_7A(16'h0000),
    .INIT_7B(16'h0000),
    .INIT_7C(16'h0000),
    .INIT_7D(16'h0000),
    .INIT_7E(16'h0000),
    .INIT_7F(16'h0000),
    .IS_CONVSTCLK_INVERTED(1'b0),
    .IS_DCLK_INVERTED(1'b0),
    .SIM_DEVICE("ULTRASCALE_PLUS"),
    .SIM_MONITOR_FILE("design.dat"),
    .SYSMON_VUSER0_BANK(0),
    .SYSMON_VUSER0_MONITOR("NONE"),
    .SYSMON_VUSER1_BANK(0),
    .SYSMON_VUSER1_MONITOR("NONE"),
    .SYSMON_VUSER2_BANK(0),
    .SYSMON_VUSER2_MONITOR("NONE"),
    .SYSMON_VUSER3_BANK(0),
    .SYSMON_VUSER3_MONITOR("NONE")) 
    inst_sysmon
       (.ADC_DATA(NLW_inst_sysmon_ADC_DATA_UNCONNECTED[15:0]),
        .ALM({NLW_inst_sysmon_ALM_UNCONNECTED[15:8],alarm_out,NLW_inst_sysmon_ALM_UNCONNECTED[6:3],vccaux_alarm_out,vccint_alarm_out,user_temp_alarm_out}),
        .BUSY(busy_out),
        .CHANNEL(channel_out),
        .CONVST(1'b0),
        .CONVSTCLK(1'b0),
        .DADDR(daddr_in),
        .DCLK(dclk_in),
        .DEN(den_in),
        .DI(di_in),
        .DO(do_out),
        .DRDY(drdy_out),
        .DWE(dwe_in),
        .EOC(eoc_out),
        .EOS(eos_out),
        .I2C_SCLK(1'b0),
        .I2C_SCLK_TS(NLW_inst_sysmon_I2C_SCLK_TS_UNCONNECTED),
        .I2C_SDA(1'b0),
        .I2C_SDA_TS(NLW_inst_sysmon_I2C_SDA_TS_UNCONNECTED),
        .JTAGBUSY(NLW_inst_sysmon_JTAGBUSY_UNCONNECTED),
        .JTAGLOCKED(NLW_inst_sysmon_JTAGLOCKED_UNCONNECTED),
        .JTAGMODIFIED(NLW_inst_sysmon_JTAGMODIFIED_UNCONNECTED),
        .MUXADDR(NLW_inst_sysmon_MUXADDR_UNCONNECTED[4:0]),
        .OT(ot_out),
        .RESET(reset_in),
        .SMBALERT_TS(NLW_inst_sysmon_SMBALERT_TS_UNCONNECTED),
        .VAUXN({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .VAUXP({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .VN(vn),
        .VP(vp));
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
