// Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
// Copyright 2022-2024 Advanced Micro Devices, Inc. All Rights Reserved.
// --------------------------------------------------------------------------------
// Tool Version: Vivado v.2024.2 (lin64) Build 5239630 Fri Nov 08 22:34:34 MST 2024
// Date        : Wed Feb  5 19:12:28 2025
// Host        : pop-os running 64-bit Pop!_OS 22.04 LTS
// Command     : write_verilog -force -mode funcsim
//               /home/mirai/Documents/Projects/Aging-main/vivado_project/aging-study/aging-study.gen/sources_1/bd/design_1/ip/design_1_uart_tx_0_0/design_1_uart_tx_0_0_sim_netlist.v
// Design      : design_1_uart_tx_0_0
// Purpose     : This verilog netlist is a functional simulation representation of the design and should not be modified
//               or synthesized. This netlist cannot be used for SDF annotated simulation.
// Device      : xc7a100tcsg324-1
// --------------------------------------------------------------------------------
`timescale 1 ps / 1 ps

(* CHECK_LICENSE_TYPE = "design_1_uart_tx_0_0,uart_tx,{}" *) (* DowngradeIPIdentifiedWarnings = "yes" *) (* IP_DEFINITION_SOURCE = "module_ref" *) 
(* X_CORE_INFO = "uart_tx,Vivado 2024.2" *) 
(* NotValidForBitStream *)
module design_1_uart_tx_0_0
   (clk,
    reset,
    send,
    data,
    tx,
    tx_busy);
  (* X_INTERFACE_INFO = "xilinx.com:signal:clock:1.0 clk CLK" *) (* X_INTERFACE_MODE = "slave" *) (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME clk, ASSOCIATED_RESET reset, FREQ_HZ 100000000, FREQ_TOLERANCE_HZ 0, PHASE 0.0, CLK_DOMAIN design_1_CLK100MHZ, INSERT_VIP 0" *) input clk;
  (* X_INTERFACE_INFO = "xilinx.com:signal:reset:1.0 reset RST" *) (* X_INTERFACE_MODE = "slave" *) (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME reset, POLARITY ACTIVE_LOW, INSERT_VIP 0" *) input reset;
  input send;
  input [7:0]data;
  output tx;
  output tx_busy;

  wire clk;
  wire [7:0]data;
  wire reset;
  wire send;
  wire tx;
  wire tx_busy;

  design_1_uart_tx_0_0_uart_tx inst
       (.clk(clk),
        .data(data),
        .reset(reset),
        .send(send),
        .tx(tx),
        .tx_busy_reg_0(tx_busy));
endmodule

(* ORIG_REF_NAME = "uart_tx" *) 
module design_1_uart_tx_0_0_uart_tx
   (tx_busy_reg_0,
    tx,
    send,
    clk,
    data,
    reset);
  output tx_busy_reg_0;
  output tx;
  input send;
  input clk;
  input [7:0]data;
  input reset;

  wire clk;
  wire [13:0]counter;
  wire [13:1]counter0;
  wire counter0_carry__0_n_0;
  wire counter0_carry__0_n_1;
  wire counter0_carry__0_n_2;
  wire counter0_carry__0_n_3;
  wire counter0_carry__1_n_0;
  wire counter0_carry__1_n_1;
  wire counter0_carry__1_n_2;
  wire counter0_carry__1_n_3;
  wire counter0_carry_n_0;
  wire counter0_carry_n_1;
  wire counter0_carry_n_2;
  wire counter0_carry_n_3;
  wire \counter[13]_i_1_n_0 ;
  wire [7:0]data;
  wire [9:1]frame;
  wire \index[0]_i_1_n_0 ;
  wire \index[1]_i_1_n_0 ;
  wire \index[2]_i_1_n_0 ;
  wire \index[3]_i_1_n_0 ;
  wire \index[3]_i_2_n_0 ;
  wire [3:0]index_reg;
  wire [13:0]p_1_in;
  wire reset;
  wire send;
  wire sendant;
  wire tx;
  wire tx17_out;
  wire tx1__8;
  wire tx2_in;
  wire tx_busy4_in;
  wire tx_busy_i_1_n_0;
  wire tx_busy_i_2_n_0;
  wire tx_busy_reg_0;
  wire tx_i_1_n_0;
  wire tx_i_2_n_0;
  wire tx_i_3_n_0;
  wire tx_i_6_n_0;
  wire tx_i_7_n_0;
  wire tx_i_8_n_0;
  wire tx_i_9_n_0;
  wire [3:0]NLW_counter0_carry__2_CO_UNCONNECTED;
  wire [3:1]NLW_counter0_carry__2_O_UNCONNECTED;

  (* ADDER_THRESHOLD = "35" *) 
  CARRY4 counter0_carry
       (.CI(1'b0),
        .CO({counter0_carry_n_0,counter0_carry_n_1,counter0_carry_n_2,counter0_carry_n_3}),
        .CYINIT(counter[0]),
        .DI({1'b0,1'b0,1'b0,1'b0}),
        .O(counter0[4:1]),
        .S(counter[4:1]));
  (* ADDER_THRESHOLD = "35" *) 
  CARRY4 counter0_carry__0
       (.CI(counter0_carry_n_0),
        .CO({counter0_carry__0_n_0,counter0_carry__0_n_1,counter0_carry__0_n_2,counter0_carry__0_n_3}),
        .CYINIT(1'b0),
        .DI({1'b0,1'b0,1'b0,1'b0}),
        .O(counter0[8:5]),
        .S(counter[8:5]));
  (* ADDER_THRESHOLD = "35" *) 
  CARRY4 counter0_carry__1
       (.CI(counter0_carry__0_n_0),
        .CO({counter0_carry__1_n_0,counter0_carry__1_n_1,counter0_carry__1_n_2,counter0_carry__1_n_3}),
        .CYINIT(1'b0),
        .DI({1'b0,1'b0,1'b0,1'b0}),
        .O(counter0[12:9]),
        .S(counter[12:9]));
  (* ADDER_THRESHOLD = "35" *) 
  CARRY4 counter0_carry__2
       (.CI(counter0_carry__1_n_0),
        .CO(NLW_counter0_carry__2_CO_UNCONNECTED[3:0]),
        .CYINIT(1'b0),
        .DI({1'b0,1'b0,1'b0,1'b0}),
        .O({NLW_counter0_carry__2_O_UNCONNECTED[3:1],counter0[13]}),
        .S({1'b0,1'b0,1'b0,counter[13]}));
  LUT5 #(
    .INIT(32'h11111011)) 
    \counter[0]_i_1 
       (.I0(tx1__8),
        .I1(counter[0]),
        .I2(sendant),
        .I3(send),
        .I4(tx_busy_reg_0),
        .O(p_1_in[0]));
  LUT5 #(
    .INIT(32'h44444044)) 
    \counter[10]_i_1 
       (.I0(tx1__8),
        .I1(counter0[10]),
        .I2(sendant),
        .I3(send),
        .I4(tx_busy_reg_0),
        .O(p_1_in[10]));
  LUT5 #(
    .INIT(32'h04FF0404)) 
    \counter[11]_i_1 
       (.I0(sendant),
        .I1(send),
        .I2(tx_busy_reg_0),
        .I3(tx1__8),
        .I4(counter0[11]),
        .O(p_1_in[11]));
  LUT5 #(
    .INIT(32'h44444044)) 
    \counter[12]_i_1 
       (.I0(tx1__8),
        .I1(counter0[12]),
        .I2(sendant),
        .I3(send),
        .I4(tx_busy_reg_0),
        .O(p_1_in[12]));
  LUT3 #(
    .INIT(8'hF4)) 
    \counter[13]_i_1 
       (.I0(sendant),
        .I1(send),
        .I2(tx_busy_reg_0),
        .O(\counter[13]_i_1_n_0 ));
  LUT5 #(
    .INIT(32'h04FF0404)) 
    \counter[13]_i_2 
       (.I0(sendant),
        .I1(send),
        .I2(tx_busy_reg_0),
        .I3(tx1__8),
        .I4(counter0[13]),
        .O(p_1_in[13]));
  LUT5 #(
    .INIT(32'h44444044)) 
    \counter[1]_i_1 
       (.I0(tx1__8),
        .I1(counter0[1]),
        .I2(sendant),
        .I3(send),
        .I4(tx_busy_reg_0),
        .O(p_1_in[1]));
  LUT5 #(
    .INIT(32'h44444044)) 
    \counter[2]_i_1 
       (.I0(tx1__8),
        .I1(counter0[2]),
        .I2(sendant),
        .I3(send),
        .I4(tx_busy_reg_0),
        .O(p_1_in[2]));
  LUT5 #(
    .INIT(32'h44444044)) 
    \counter[3]_i_1 
       (.I0(tx1__8),
        .I1(counter0[3]),
        .I2(sendant),
        .I3(send),
        .I4(tx_busy_reg_0),
        .O(p_1_in[3]));
  LUT5 #(
    .INIT(32'h04FF0404)) 
    \counter[4]_i_1 
       (.I0(sendant),
        .I1(send),
        .I2(tx_busy_reg_0),
        .I3(tx1__8),
        .I4(counter0[4]),
        .O(p_1_in[4]));
  LUT5 #(
    .INIT(32'h04FF0404)) 
    \counter[5]_i_1 
       (.I0(sendant),
        .I1(send),
        .I2(tx_busy_reg_0),
        .I3(tx1__8),
        .I4(counter0[5]),
        .O(p_1_in[5]));
  LUT5 #(
    .INIT(32'h44444044)) 
    \counter[6]_i_1 
       (.I0(tx1__8),
        .I1(counter0[6]),
        .I2(sendant),
        .I3(send),
        .I4(tx_busy_reg_0),
        .O(p_1_in[6]));
  LUT5 #(
    .INIT(32'h04FF0404)) 
    \counter[7]_i_1 
       (.I0(sendant),
        .I1(send),
        .I2(tx_busy_reg_0),
        .I3(tx1__8),
        .I4(counter0[7]),
        .O(p_1_in[7]));
  LUT5 #(
    .INIT(32'h44444044)) 
    \counter[8]_i_1 
       (.I0(tx1__8),
        .I1(counter0[8]),
        .I2(sendant),
        .I3(send),
        .I4(tx_busy_reg_0),
        .O(p_1_in[8]));
  LUT5 #(
    .INIT(32'h44444044)) 
    \counter[9]_i_1 
       (.I0(tx1__8),
        .I1(counter0[9]),
        .I2(sendant),
        .I3(send),
        .I4(tx_busy_reg_0),
        .O(p_1_in[9]));
  FDCE \counter_reg[0] 
       (.C(clk),
        .CE(\counter[13]_i_1_n_0 ),
        .CLR(tx_i_2_n_0),
        .D(p_1_in[0]),
        .Q(counter[0]));
  FDCE \counter_reg[10] 
       (.C(clk),
        .CE(\counter[13]_i_1_n_0 ),
        .CLR(tx_i_2_n_0),
        .D(p_1_in[10]),
        .Q(counter[10]));
  FDCE \counter_reg[11] 
       (.C(clk),
        .CE(\counter[13]_i_1_n_0 ),
        .CLR(tx_i_2_n_0),
        .D(p_1_in[11]),
        .Q(counter[11]));
  FDCE \counter_reg[12] 
       (.C(clk),
        .CE(\counter[13]_i_1_n_0 ),
        .CLR(tx_i_2_n_0),
        .D(p_1_in[12]),
        .Q(counter[12]));
  FDCE \counter_reg[13] 
       (.C(clk),
        .CE(\counter[13]_i_1_n_0 ),
        .CLR(tx_i_2_n_0),
        .D(p_1_in[13]),
        .Q(counter[13]));
  FDCE \counter_reg[1] 
       (.C(clk),
        .CE(\counter[13]_i_1_n_0 ),
        .CLR(tx_i_2_n_0),
        .D(p_1_in[1]),
        .Q(counter[1]));
  FDCE \counter_reg[2] 
       (.C(clk),
        .CE(\counter[13]_i_1_n_0 ),
        .CLR(tx_i_2_n_0),
        .D(p_1_in[2]),
        .Q(counter[2]));
  FDCE \counter_reg[3] 
       (.C(clk),
        .CE(\counter[13]_i_1_n_0 ),
        .CLR(tx_i_2_n_0),
        .D(p_1_in[3]),
        .Q(counter[3]));
  FDCE \counter_reg[4] 
       (.C(clk),
        .CE(\counter[13]_i_1_n_0 ),
        .CLR(tx_i_2_n_0),
        .D(p_1_in[4]),
        .Q(counter[4]));
  FDCE \counter_reg[5] 
       (.C(clk),
        .CE(\counter[13]_i_1_n_0 ),
        .CLR(tx_i_2_n_0),
        .D(p_1_in[5]),
        .Q(counter[5]));
  FDCE \counter_reg[6] 
       (.C(clk),
        .CE(\counter[13]_i_1_n_0 ),
        .CLR(tx_i_2_n_0),
        .D(p_1_in[6]),
        .Q(counter[6]));
  FDCE \counter_reg[7] 
       (.C(clk),
        .CE(\counter[13]_i_1_n_0 ),
        .CLR(tx_i_2_n_0),
        .D(p_1_in[7]),
        .Q(counter[7]));
  FDCE \counter_reg[8] 
       (.C(clk),
        .CE(\counter[13]_i_1_n_0 ),
        .CLR(tx_i_2_n_0),
        .D(p_1_in[8]),
        .Q(counter[8]));
  FDCE \counter_reg[9] 
       (.C(clk),
        .CE(\counter[13]_i_1_n_0 ),
        .CLR(tx_i_2_n_0),
        .D(p_1_in[9]),
        .Q(counter[9]));
  LUT3 #(
    .INIT(8'h04)) 
    \frame[9]_i_1 
       (.I0(tx_busy_reg_0),
        .I1(send),
        .I2(sendant),
        .O(tx17_out));
  FDCE \frame_reg[1] 
       (.C(clk),
        .CE(tx17_out),
        .CLR(tx_i_2_n_0),
        .D(data[0]),
        .Q(frame[1]));
  FDCE \frame_reg[2] 
       (.C(clk),
        .CE(tx17_out),
        .CLR(tx_i_2_n_0),
        .D(data[1]),
        .Q(frame[2]));
  FDCE \frame_reg[3] 
       (.C(clk),
        .CE(tx17_out),
        .CLR(tx_i_2_n_0),
        .D(data[2]),
        .Q(frame[3]));
  FDCE \frame_reg[4] 
       (.C(clk),
        .CE(tx17_out),
        .CLR(tx_i_2_n_0),
        .D(data[3]),
        .Q(frame[4]));
  FDCE \frame_reg[5] 
       (.C(clk),
        .CE(tx17_out),
        .CLR(tx_i_2_n_0),
        .D(data[4]),
        .Q(frame[5]));
  FDCE \frame_reg[6] 
       (.C(clk),
        .CE(tx17_out),
        .CLR(tx_i_2_n_0),
        .D(data[5]),
        .Q(frame[6]));
  FDCE \frame_reg[7] 
       (.C(clk),
        .CE(tx17_out),
        .CLR(tx_i_2_n_0),
        .D(data[6]),
        .Q(frame[7]));
  FDCE \frame_reg[8] 
       (.C(clk),
        .CE(tx17_out),
        .CLR(tx_i_2_n_0),
        .D(data[7]),
        .Q(frame[8]));
  FDCE \frame_reg[9] 
       (.C(clk),
        .CE(tx17_out),
        .CLR(tx_i_2_n_0),
        .D(1'b1),
        .Q(frame[9]));
  (* SOFT_HLUTNM = "soft_lutpair0" *) 
  LUT4 #(
    .INIT(16'h5545)) 
    \index[0]_i_1 
       (.I0(index_reg[0]),
        .I1(sendant),
        .I2(send),
        .I3(tx_busy_reg_0),
        .O(\index[0]_i_1_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair0" *) 
  LUT5 #(
    .INIT(32'h66666066)) 
    \index[1]_i_1 
       (.I0(index_reg[1]),
        .I1(index_reg[0]),
        .I2(sendant),
        .I3(send),
        .I4(tx_busy_reg_0),
        .O(\index[1]_i_1_n_0 ));
  LUT6 #(
    .INIT(64'h6A6A6A6A6A006A6A)) 
    \index[2]_i_1 
       (.I0(index_reg[2]),
        .I1(index_reg[1]),
        .I2(index_reg[0]),
        .I3(sendant),
        .I4(send),
        .I5(tx_busy_reg_0),
        .O(\index[2]_i_1_n_0 ));
  LUT5 #(
    .INIT(32'hF0004444)) 
    \index[3]_i_1 
       (.I0(sendant),
        .I1(send),
        .I2(tx1__8),
        .I3(tx_busy_i_2_n_0),
        .I4(tx_busy_reg_0),
        .O(\index[3]_i_1_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair1" *) 
  LUT5 #(
    .INIT(32'h00006AAA)) 
    \index[3]_i_2 
       (.I0(index_reg[3]),
        .I1(index_reg[2]),
        .I2(index_reg[0]),
        .I3(index_reg[1]),
        .I4(tx17_out),
        .O(\index[3]_i_2_n_0 ));
  FDCE \index_reg[0] 
       (.C(clk),
        .CE(\index[3]_i_1_n_0 ),
        .CLR(tx_i_2_n_0),
        .D(\index[0]_i_1_n_0 ),
        .Q(index_reg[0]));
  FDCE \index_reg[1] 
       (.C(clk),
        .CE(\index[3]_i_1_n_0 ),
        .CLR(tx_i_2_n_0),
        .D(\index[1]_i_1_n_0 ),
        .Q(index_reg[1]));
  FDCE \index_reg[2] 
       (.C(clk),
        .CE(\index[3]_i_1_n_0 ),
        .CLR(tx_i_2_n_0),
        .D(\index[2]_i_1_n_0 ),
        .Q(index_reg[2]));
  FDCE \index_reg[3] 
       (.C(clk),
        .CE(\index[3]_i_1_n_0 ),
        .CLR(tx_i_2_n_0),
        .D(\index[3]_i_2_n_0 ),
        .Q(index_reg[3]));
  FDCE sendant_reg
       (.C(clk),
        .CE(1'b1),
        .CLR(tx_i_2_n_0),
        .D(send),
        .Q(sendant));
  LUT6 #(
    .INIT(64'hF0FF4444FFFF4444)) 
    tx_busy_i_1
       (.I0(sendant),
        .I1(send),
        .I2(tx_busy_i_2_n_0),
        .I3(tx_busy4_in),
        .I4(tx_busy_reg_0),
        .I5(tx1__8),
        .O(tx_busy_i_1_n_0));
  (* SOFT_HLUTNM = "soft_lutpair2" *) 
  LUT4 #(
    .INIT(16'h01FF)) 
    tx_busy_i_2
       (.I0(index_reg[0]),
        .I1(index_reg[1]),
        .I2(index_reg[2]),
        .I3(index_reg[3]),
        .O(tx_busy_i_2_n_0));
  (* SOFT_HLUTNM = "soft_lutpair1" *) 
  LUT4 #(
    .INIT(16'h1000)) 
    tx_busy_i_3
       (.I0(index_reg[1]),
        .I1(index_reg[2]),
        .I2(index_reg[0]),
        .I3(index_reg[3]),
        .O(tx_busy4_in));
  FDCE tx_busy_reg
       (.C(clk),
        .CE(1'b1),
        .CLR(tx_i_2_n_0),
        .D(tx_busy_i_1_n_0),
        .Q(tx_busy_reg_0));
  LUT6 #(
    .INIT(64'h2333333320000000)) 
    tx_i_1
       (.I0(tx_i_3_n_0),
        .I1(tx17_out),
        .I2(tx1__8),
        .I3(tx2_in),
        .I4(tx_busy_reg_0),
        .I5(tx),
        .O(tx_i_1_n_0));
  LUT1 #(
    .INIT(2'h1)) 
    tx_i_2
       (.I0(reset),
        .O(tx_i_2_n_0));
  LUT6 #(
    .INIT(64'hFFE200E2FFFFFFFF)) 
    tx_i_3
       (.I0(tx_i_6_n_0),
        .I1(index_reg[2]),
        .I2(tx_i_7_n_0),
        .I3(index_reg[3]),
        .I4(tx_i_8_n_0),
        .I5(tx_busy_i_2_n_0),
        .O(tx_i_3_n_0));
  LUT6 #(
    .INIT(64'hAAAAAAAA88888880)) 
    tx_i_4
       (.I0(counter[13]),
        .I1(counter[11]),
        .I2(tx_i_9_n_0),
        .I3(counter[8]),
        .I4(counter[9]),
        .I5(counter[12]),
        .O(tx1__8));
  (* SOFT_HLUTNM = "soft_lutpair2" *) 
  LUT3 #(
    .INIT(8'h57)) 
    tx_i_5
       (.I0(index_reg[3]),
        .I1(index_reg[2]),
        .I2(index_reg[1]),
        .O(tx2_in));
  LUT5 #(
    .INIT(32'hAFC0A0C0)) 
    tx_i_6
       (.I0(frame[3]),
        .I1(frame[2]),
        .I2(index_reg[1]),
        .I3(index_reg[0]),
        .I4(frame[1]),
        .O(tx_i_6_n_0));
  LUT6 #(
    .INIT(64'hAFA0CFCFAFA0C0C0)) 
    tx_i_7
       (.I0(frame[7]),
        .I1(frame[6]),
        .I2(index_reg[1]),
        .I3(frame[5]),
        .I4(index_reg[0]),
        .I5(frame[4]),
        .O(tx_i_7_n_0));
  LUT3 #(
    .INIT(8'hB8)) 
    tx_i_8
       (.I0(frame[9]),
        .I1(index_reg[0]),
        .I2(frame[8]),
        .O(tx_i_8_n_0));
  LUT5 #(
    .INIT(32'hFEEEAAAA)) 
    tx_i_9
       (.I0(counter[10]),
        .I1(counter[6]),
        .I2(counter[5]),
        .I3(counter[4]),
        .I4(counter[7]),
        .O(tx_i_9_n_0));
  FDPE tx_reg
       (.C(clk),
        .CE(1'b1),
        .D(tx_i_1_n_0),
        .PRE(tx_i_2_n_0),
        .Q(tx));
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
