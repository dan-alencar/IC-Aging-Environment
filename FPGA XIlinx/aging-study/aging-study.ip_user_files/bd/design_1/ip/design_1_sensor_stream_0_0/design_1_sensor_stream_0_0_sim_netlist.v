// Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
// Copyright 2022-2024 Advanced Micro Devices, Inc. All Rights Reserved.
// --------------------------------------------------------------------------------
// Tool Version: Vivado v.2024.2 (lin64) Build 5239630 Fri Nov 08 22:34:34 MST 2024
// Date        : Wed May 14 18:07:50 2025
// Host        : pop-os running 64-bit Pop!_OS 24.04 LTS
// Command     : write_verilog -force -mode funcsim
//               /home/mirai/Documents/Projects/Aging_Fase2/failure_catch/aging_failure_holder/Aging-dynamic/vivado_project/aging-study/aging-study.gen/sources_1/bd/design_1/ip/design_1_sensor_stream_0_0/design_1_sensor_stream_0_0_sim_netlist.v
// Design      : design_1_sensor_stream_0_0
// Purpose     : This verilog netlist is a functional simulation representation of the design and should not be modified
//               or synthesized. This netlist cannot be used for SDF annotated simulation.
// Device      : xc7a100tcsg324-1
// --------------------------------------------------------------------------------
`timescale 1 ps / 1 ps

(* CHECK_LICENSE_TYPE = "design_1_sensor_stream_0_0,sensor_stream,{}" *) (* DowngradeIPIdentifiedWarnings = "yes" *) (* IP_DEFINITION_SOURCE = "module_ref" *) 
(* X_CORE_INFO = "sensor_stream,Vivado 2024.2" *) 
(* NotValidForBitStream *)
module design_1_sensor_stream_0_0
   (temp,
    vccint,
    sensor,
    failure,
    reset,
    clk,
    sendin,
    send,
    data);
  input [23:0]temp;
  input [23:0]vccint;
  input [15:0]sensor;
  input failure;
  (* X_INTERFACE_INFO = "xilinx.com:signal:reset:1.0 reset RST" *) (* X_INTERFACE_MODE = "slave" *) (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME reset, POLARITY ACTIVE_LOW, INSERT_VIP 0" *) input reset;
  (* X_INTERFACE_INFO = "xilinx.com:signal:clock:1.0 clk CLK" *) (* X_INTERFACE_MODE = "slave" *) (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME clk, ASSOCIATED_RESET reset, FREQ_HZ 100000000, FREQ_TOLERANCE_HZ 0, PHASE 0.0, CLK_DOMAIN design_1_CLK100MHZ, INSERT_VIP 0" *) input clk;
  input sendin;
  output send;
  output [7:0]data;

  wire clk;
  wire [7:0]data;
  wire failure;
  wire reset;
  wire send;
  wire sendin;
  wire [15:0]sensor;
  wire [23:0]temp;
  wire [23:0]vccint;

  design_1_sensor_stream_0_0_sensor_stream inst
       (.clk(clk),
        .data(data),
        .failure(failure),
        .reset(reset),
        .send(send),
        .sendin(sendin),
        .sensor(sensor),
        .temp(temp),
        .vccint(vccint));
endmodule

(* ORIG_REF_NAME = "sensor_stream" *) 
module design_1_sensor_stream_0_0_sensor_stream
   (data,
    send,
    sendin,
    clk,
    failure,
    temp,
    sensor,
    vccint,
    reset);
  output [7:0]data;
  output send;
  input sendin;
  input clk;
  input failure;
  input [23:0]temp;
  input [15:0]sensor;
  input [23:0]vccint;
  input reset;

  wire clk;
  wire counter;
  wire counter1__10;
  wire \counter[0]_i_3_n_0 ;
  wire \counter[0]_i_4_n_0 ;
  wire \counter[0]_i_5_n_0 ;
  wire \counter[0]_i_6_n_0 ;
  wire \counter[0]_i_7_n_0 ;
  wire \counter[12]_i_2_n_0 ;
  wire \counter[12]_i_3_n_0 ;
  wire \counter[12]_i_4_n_0 ;
  wire \counter[12]_i_5_n_0 ;
  wire \counter[16]_i_2_n_0 ;
  wire \counter[4]_i_2_n_0 ;
  wire \counter[4]_i_3_n_0 ;
  wire \counter[4]_i_4_n_0 ;
  wire \counter[4]_i_5_n_0 ;
  wire \counter[8]_i_2_n_0 ;
  wire \counter[8]_i_3_n_0 ;
  wire \counter[8]_i_4_n_0 ;
  wire \counter[8]_i_5_n_0 ;
  wire [16:5]counter_reg;
  wire \counter_reg[0]_i_2_n_0 ;
  wire \counter_reg[0]_i_2_n_1 ;
  wire \counter_reg[0]_i_2_n_2 ;
  wire \counter_reg[0]_i_2_n_3 ;
  wire \counter_reg[0]_i_2_n_4 ;
  wire \counter_reg[0]_i_2_n_5 ;
  wire \counter_reg[0]_i_2_n_6 ;
  wire \counter_reg[0]_i_2_n_7 ;
  wire \counter_reg[12]_i_1_n_0 ;
  wire \counter_reg[12]_i_1_n_1 ;
  wire \counter_reg[12]_i_1_n_2 ;
  wire \counter_reg[12]_i_1_n_3 ;
  wire \counter_reg[12]_i_1_n_4 ;
  wire \counter_reg[12]_i_1_n_5 ;
  wire \counter_reg[12]_i_1_n_6 ;
  wire \counter_reg[12]_i_1_n_7 ;
  wire \counter_reg[16]_i_1_n_7 ;
  wire \counter_reg[4]_i_1_n_0 ;
  wire \counter_reg[4]_i_1_n_1 ;
  wire \counter_reg[4]_i_1_n_2 ;
  wire \counter_reg[4]_i_1_n_3 ;
  wire \counter_reg[4]_i_1_n_4 ;
  wire \counter_reg[4]_i_1_n_5 ;
  wire \counter_reg[4]_i_1_n_6 ;
  wire \counter_reg[4]_i_1_n_7 ;
  wire \counter_reg[8]_i_1_n_0 ;
  wire \counter_reg[8]_i_1_n_1 ;
  wire \counter_reg[8]_i_1_n_2 ;
  wire \counter_reg[8]_i_1_n_3 ;
  wire \counter_reg[8]_i_1_n_4 ;
  wire \counter_reg[8]_i_1_n_5 ;
  wire \counter_reg[8]_i_1_n_6 ;
  wire \counter_reg[8]_i_1_n_7 ;
  wire \counter_reg_n_0_[0] ;
  wire \counter_reg_n_0_[1] ;
  wire \counter_reg_n_0_[2] ;
  wire \counter_reg_n_0_[3] ;
  wire \counter_reg_n_0_[4] ;
  wire [7:0]data;
  wire \data[0]_i_2_n_0 ;
  wire \data[0]_i_3_n_0 ;
  wire \data[0]_i_4_n_0 ;
  wire \data[1]_i_2_n_0 ;
  wire \data[1]_i_3_n_0 ;
  wire \data[2]_i_2_n_0 ;
  wire \data[2]_i_3_n_0 ;
  wire \data[3]_i_2_n_0 ;
  wire \data[3]_i_3_n_0 ;
  wire \data[4]_i_2_n_0 ;
  wire \data[4]_i_3_n_0 ;
  wire \data[5]_i_2_n_0 ;
  wire \data[5]_i_3_n_0 ;
  wire \data[6]_i_2_n_0 ;
  wire \data[6]_i_3_n_0 ;
  wire \data[7]_i_3_n_0 ;
  wire \data[7]_i_4_n_0 ;
  wire [7:0]data_0;
  wire enable;
  wire enable_i_1_n_0;
  wire failure;
  wire [3:0]p_0_in;
  wire reset;
  wire sel;
  wire [3:0]sel_reg;
  wire send;
  wire send_i_1_n_0;
  wire send_i_2_n_0;
  wire send_i_3_n_0;
  wire send_i_5_n_0;
  wire send_i_6_n_0;
  wire send_i_7_n_0;
  wire sendant;
  wire sendin;
  wire [15:0]sensor;
  wire [23:0]temp;
  wire [23:0]vccint;
  wire [3:0]\NLW_counter_reg[16]_i_1_CO_UNCONNECTED ;
  wire [3:1]\NLW_counter_reg[16]_i_1_O_UNCONNECTED ;

  LUT3 #(
    .INIT(8'hA2)) 
    \counter[0]_i_1 
       (.I0(enable),
        .I1(sendin),
        .I2(sendant),
        .O(counter));
  LUT2 #(
    .INIT(4'h2)) 
    \counter[0]_i_3 
       (.I0(\counter_reg_n_0_[0] ),
        .I1(counter1__10),
        .O(\counter[0]_i_3_n_0 ));
  LUT2 #(
    .INIT(4'h2)) 
    \counter[0]_i_4 
       (.I0(\counter_reg_n_0_[3] ),
        .I1(counter1__10),
        .O(\counter[0]_i_4_n_0 ));
  LUT2 #(
    .INIT(4'h2)) 
    \counter[0]_i_5 
       (.I0(\counter_reg_n_0_[2] ),
        .I1(counter1__10),
        .O(\counter[0]_i_5_n_0 ));
  LUT2 #(
    .INIT(4'h2)) 
    \counter[0]_i_6 
       (.I0(\counter_reg_n_0_[1] ),
        .I1(counter1__10),
        .O(\counter[0]_i_6_n_0 ));
  LUT2 #(
    .INIT(4'h1)) 
    \counter[0]_i_7 
       (.I0(\counter_reg_n_0_[0] ),
        .I1(counter1__10),
        .O(\counter[0]_i_7_n_0 ));
  LUT2 #(
    .INIT(4'h2)) 
    \counter[12]_i_2 
       (.I0(counter_reg[15]),
        .I1(counter1__10),
        .O(\counter[12]_i_2_n_0 ));
  LUT2 #(
    .INIT(4'h2)) 
    \counter[12]_i_3 
       (.I0(counter_reg[14]),
        .I1(counter1__10),
        .O(\counter[12]_i_3_n_0 ));
  LUT2 #(
    .INIT(4'h2)) 
    \counter[12]_i_4 
       (.I0(counter_reg[13]),
        .I1(counter1__10),
        .O(\counter[12]_i_4_n_0 ));
  LUT2 #(
    .INIT(4'h2)) 
    \counter[12]_i_5 
       (.I0(counter_reg[12]),
        .I1(counter1__10),
        .O(\counter[12]_i_5_n_0 ));
  LUT2 #(
    .INIT(4'h2)) 
    \counter[16]_i_2 
       (.I0(counter_reg[16]),
        .I1(counter1__10),
        .O(\counter[16]_i_2_n_0 ));
  LUT2 #(
    .INIT(4'h2)) 
    \counter[4]_i_2 
       (.I0(counter_reg[7]),
        .I1(counter1__10),
        .O(\counter[4]_i_2_n_0 ));
  LUT2 #(
    .INIT(4'h2)) 
    \counter[4]_i_3 
       (.I0(counter_reg[6]),
        .I1(counter1__10),
        .O(\counter[4]_i_3_n_0 ));
  LUT2 #(
    .INIT(4'h2)) 
    \counter[4]_i_4 
       (.I0(counter_reg[5]),
        .I1(counter1__10),
        .O(\counter[4]_i_4_n_0 ));
  LUT2 #(
    .INIT(4'h2)) 
    \counter[4]_i_5 
       (.I0(\counter_reg_n_0_[4] ),
        .I1(counter1__10),
        .O(\counter[4]_i_5_n_0 ));
  LUT2 #(
    .INIT(4'h2)) 
    \counter[8]_i_2 
       (.I0(counter_reg[11]),
        .I1(counter1__10),
        .O(\counter[8]_i_2_n_0 ));
  LUT2 #(
    .INIT(4'h2)) 
    \counter[8]_i_3 
       (.I0(counter_reg[10]),
        .I1(counter1__10),
        .O(\counter[8]_i_3_n_0 ));
  LUT2 #(
    .INIT(4'h2)) 
    \counter[8]_i_4 
       (.I0(counter_reg[9]),
        .I1(counter1__10),
        .O(\counter[8]_i_4_n_0 ));
  LUT2 #(
    .INIT(4'h2)) 
    \counter[8]_i_5 
       (.I0(counter_reg[8]),
        .I1(counter1__10),
        .O(\counter[8]_i_5_n_0 ));
  FDCE \counter_reg[0] 
       (.C(clk),
        .CE(counter),
        .CLR(send_i_2_n_0),
        .D(\counter_reg[0]_i_2_n_7 ),
        .Q(\counter_reg_n_0_[0] ));
  (* ADDER_THRESHOLD = "11" *) 
  CARRY4 \counter_reg[0]_i_2 
       (.CI(1'b0),
        .CO({\counter_reg[0]_i_2_n_0 ,\counter_reg[0]_i_2_n_1 ,\counter_reg[0]_i_2_n_2 ,\counter_reg[0]_i_2_n_3 }),
        .CYINIT(1'b0),
        .DI({1'b0,1'b0,1'b0,\counter[0]_i_3_n_0 }),
        .O({\counter_reg[0]_i_2_n_4 ,\counter_reg[0]_i_2_n_5 ,\counter_reg[0]_i_2_n_6 ,\counter_reg[0]_i_2_n_7 }),
        .S({\counter[0]_i_4_n_0 ,\counter[0]_i_5_n_0 ,\counter[0]_i_6_n_0 ,\counter[0]_i_7_n_0 }));
  FDCE \counter_reg[10] 
       (.C(clk),
        .CE(counter),
        .CLR(send_i_2_n_0),
        .D(\counter_reg[8]_i_1_n_5 ),
        .Q(counter_reg[10]));
  FDCE \counter_reg[11] 
       (.C(clk),
        .CE(counter),
        .CLR(send_i_2_n_0),
        .D(\counter_reg[8]_i_1_n_4 ),
        .Q(counter_reg[11]));
  FDCE \counter_reg[12] 
       (.C(clk),
        .CE(counter),
        .CLR(send_i_2_n_0),
        .D(\counter_reg[12]_i_1_n_7 ),
        .Q(counter_reg[12]));
  (* ADDER_THRESHOLD = "11" *) 
  CARRY4 \counter_reg[12]_i_1 
       (.CI(\counter_reg[8]_i_1_n_0 ),
        .CO({\counter_reg[12]_i_1_n_0 ,\counter_reg[12]_i_1_n_1 ,\counter_reg[12]_i_1_n_2 ,\counter_reg[12]_i_1_n_3 }),
        .CYINIT(1'b0),
        .DI({1'b0,1'b0,1'b0,1'b0}),
        .O({\counter_reg[12]_i_1_n_4 ,\counter_reg[12]_i_1_n_5 ,\counter_reg[12]_i_1_n_6 ,\counter_reg[12]_i_1_n_7 }),
        .S({\counter[12]_i_2_n_0 ,\counter[12]_i_3_n_0 ,\counter[12]_i_4_n_0 ,\counter[12]_i_5_n_0 }));
  FDCE \counter_reg[13] 
       (.C(clk),
        .CE(counter),
        .CLR(send_i_2_n_0),
        .D(\counter_reg[12]_i_1_n_6 ),
        .Q(counter_reg[13]));
  FDCE \counter_reg[14] 
       (.C(clk),
        .CE(counter),
        .CLR(send_i_2_n_0),
        .D(\counter_reg[12]_i_1_n_5 ),
        .Q(counter_reg[14]));
  FDCE \counter_reg[15] 
       (.C(clk),
        .CE(counter),
        .CLR(send_i_2_n_0),
        .D(\counter_reg[12]_i_1_n_4 ),
        .Q(counter_reg[15]));
  FDCE \counter_reg[16] 
       (.C(clk),
        .CE(counter),
        .CLR(send_i_2_n_0),
        .D(\counter_reg[16]_i_1_n_7 ),
        .Q(counter_reg[16]));
  (* ADDER_THRESHOLD = "11" *) 
  CARRY4 \counter_reg[16]_i_1 
       (.CI(\counter_reg[12]_i_1_n_0 ),
        .CO(\NLW_counter_reg[16]_i_1_CO_UNCONNECTED [3:0]),
        .CYINIT(1'b0),
        .DI({1'b0,1'b0,1'b0,1'b0}),
        .O({\NLW_counter_reg[16]_i_1_O_UNCONNECTED [3:1],\counter_reg[16]_i_1_n_7 }),
        .S({1'b0,1'b0,1'b0,\counter[16]_i_2_n_0 }));
  FDCE \counter_reg[1] 
       (.C(clk),
        .CE(counter),
        .CLR(send_i_2_n_0),
        .D(\counter_reg[0]_i_2_n_6 ),
        .Q(\counter_reg_n_0_[1] ));
  FDCE \counter_reg[2] 
       (.C(clk),
        .CE(counter),
        .CLR(send_i_2_n_0),
        .D(\counter_reg[0]_i_2_n_5 ),
        .Q(\counter_reg_n_0_[2] ));
  FDCE \counter_reg[3] 
       (.C(clk),
        .CE(counter),
        .CLR(send_i_2_n_0),
        .D(\counter_reg[0]_i_2_n_4 ),
        .Q(\counter_reg_n_0_[3] ));
  FDCE \counter_reg[4] 
       (.C(clk),
        .CE(counter),
        .CLR(send_i_2_n_0),
        .D(\counter_reg[4]_i_1_n_7 ),
        .Q(\counter_reg_n_0_[4] ));
  (* ADDER_THRESHOLD = "11" *) 
  CARRY4 \counter_reg[4]_i_1 
       (.CI(\counter_reg[0]_i_2_n_0 ),
        .CO({\counter_reg[4]_i_1_n_0 ,\counter_reg[4]_i_1_n_1 ,\counter_reg[4]_i_1_n_2 ,\counter_reg[4]_i_1_n_3 }),
        .CYINIT(1'b0),
        .DI({1'b0,1'b0,1'b0,1'b0}),
        .O({\counter_reg[4]_i_1_n_4 ,\counter_reg[4]_i_1_n_5 ,\counter_reg[4]_i_1_n_6 ,\counter_reg[4]_i_1_n_7 }),
        .S({\counter[4]_i_2_n_0 ,\counter[4]_i_3_n_0 ,\counter[4]_i_4_n_0 ,\counter[4]_i_5_n_0 }));
  FDCE \counter_reg[5] 
       (.C(clk),
        .CE(counter),
        .CLR(send_i_2_n_0),
        .D(\counter_reg[4]_i_1_n_6 ),
        .Q(counter_reg[5]));
  FDCE \counter_reg[6] 
       (.C(clk),
        .CE(counter),
        .CLR(send_i_2_n_0),
        .D(\counter_reg[4]_i_1_n_5 ),
        .Q(counter_reg[6]));
  FDCE \counter_reg[7] 
       (.C(clk),
        .CE(counter),
        .CLR(send_i_2_n_0),
        .D(\counter_reg[4]_i_1_n_4 ),
        .Q(counter_reg[7]));
  FDCE \counter_reg[8] 
       (.C(clk),
        .CE(counter),
        .CLR(send_i_2_n_0),
        .D(\counter_reg[8]_i_1_n_7 ),
        .Q(counter_reg[8]));
  (* ADDER_THRESHOLD = "11" *) 
  CARRY4 \counter_reg[8]_i_1 
       (.CI(\counter_reg[4]_i_1_n_0 ),
        .CO({\counter_reg[8]_i_1_n_0 ,\counter_reg[8]_i_1_n_1 ,\counter_reg[8]_i_1_n_2 ,\counter_reg[8]_i_1_n_3 }),
        .CYINIT(1'b0),
        .DI({1'b0,1'b0,1'b0,1'b0}),
        .O({\counter_reg[8]_i_1_n_4 ,\counter_reg[8]_i_1_n_5 ,\counter_reg[8]_i_1_n_6 ,\counter_reg[8]_i_1_n_7 }),
        .S({\counter[8]_i_2_n_0 ,\counter[8]_i_3_n_0 ,\counter[8]_i_4_n_0 ,\counter[8]_i_5_n_0 }));
  FDCE \counter_reg[9] 
       (.C(clk),
        .CE(counter),
        .CLR(send_i_2_n_0),
        .D(\counter_reg[8]_i_1_n_6 ),
        .Q(counter_reg[9]));
  LUT6 #(
    .INIT(64'h00000C0CFF00AAAA)) 
    \data[0]_i_1 
       (.I0(\data[0]_i_2_n_0 ),
        .I1(failure),
        .I2(\data[0]_i_3_n_0 ),
        .I3(\data[0]_i_4_n_0 ),
        .I4(sel_reg[2]),
        .I5(sel_reg[3]),
        .O(data_0[0]));
  LUT6 #(
    .INIT(64'hCCFFAAF0CC00AAF0)) 
    \data[0]_i_2 
       (.I0(temp[8]),
        .I1(sensor[0]),
        .I2(temp[0]),
        .I3(sel_reg[0]),
        .I4(sel_reg[1]),
        .I5(temp[16]),
        .O(\data[0]_i_2_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair2" *) 
  LUT2 #(
    .INIT(4'hE)) 
    \data[0]_i_3 
       (.I0(sel_reg[1]),
        .I1(sel_reg[0]),
        .O(\data[0]_i_3_n_0 ));
  LUT6 #(
    .INIT(64'hCCFFAAF0CC00AAF0)) 
    \data[0]_i_4 
       (.I0(vccint[0]),
        .I1(vccint[16]),
        .I2(sensor[8]),
        .I3(sel_reg[0]),
        .I4(sel_reg[1]),
        .I5(vccint[8]),
        .O(\data[0]_i_4_n_0 ));
  LUT4 #(
    .INIT(16'h0A0C)) 
    \data[1]_i_1 
       (.I0(\data[1]_i_2_n_0 ),
        .I1(\data[1]_i_3_n_0 ),
        .I2(sel_reg[3]),
        .I3(sel_reg[2]),
        .O(data_0[1]));
  LUT6 #(
    .INIT(64'hCCFFAAF0CC00AAF0)) 
    \data[1]_i_2 
       (.I0(vccint[1]),
        .I1(vccint[17]),
        .I2(sensor[9]),
        .I3(sel_reg[0]),
        .I4(sel_reg[1]),
        .I5(vccint[9]),
        .O(\data[1]_i_2_n_0 ));
  LUT6 #(
    .INIT(64'hCCFFAAF0CC00AAF0)) 
    \data[1]_i_3 
       (.I0(temp[9]),
        .I1(sensor[1]),
        .I2(temp[1]),
        .I3(sel_reg[0]),
        .I4(sel_reg[1]),
        .I5(temp[17]),
        .O(\data[1]_i_3_n_0 ));
  LUT4 #(
    .INIT(16'h0A0C)) 
    \data[2]_i_1 
       (.I0(\data[2]_i_2_n_0 ),
        .I1(\data[2]_i_3_n_0 ),
        .I2(sel_reg[3]),
        .I3(sel_reg[2]),
        .O(data_0[2]));
  LUT6 #(
    .INIT(64'hCCFFAAF0CC00AAF0)) 
    \data[2]_i_2 
       (.I0(vccint[2]),
        .I1(vccint[18]),
        .I2(sensor[10]),
        .I3(sel_reg[0]),
        .I4(sel_reg[1]),
        .I5(vccint[10]),
        .O(\data[2]_i_2_n_0 ));
  LUT6 #(
    .INIT(64'hCCFFAAF0CC00AAF0)) 
    \data[2]_i_3 
       (.I0(temp[10]),
        .I1(sensor[2]),
        .I2(temp[2]),
        .I3(sel_reg[0]),
        .I4(sel_reg[1]),
        .I5(temp[18]),
        .O(\data[2]_i_3_n_0 ));
  LUT4 #(
    .INIT(16'h0A0C)) 
    \data[3]_i_1 
       (.I0(\data[3]_i_2_n_0 ),
        .I1(\data[3]_i_3_n_0 ),
        .I2(sel_reg[3]),
        .I3(sel_reg[2]),
        .O(data_0[3]));
  LUT6 #(
    .INIT(64'hCCFFAAF0CC00AAF0)) 
    \data[3]_i_2 
       (.I0(vccint[3]),
        .I1(vccint[19]),
        .I2(sensor[11]),
        .I3(sel_reg[0]),
        .I4(sel_reg[1]),
        .I5(vccint[11]),
        .O(\data[3]_i_2_n_0 ));
  LUT6 #(
    .INIT(64'hCCFFAAF0CC00AAF0)) 
    \data[3]_i_3 
       (.I0(temp[11]),
        .I1(sensor[3]),
        .I2(temp[3]),
        .I3(sel_reg[0]),
        .I4(sel_reg[1]),
        .I5(temp[19]),
        .O(\data[3]_i_3_n_0 ));
  LUT4 #(
    .INIT(16'h0A0C)) 
    \data[4]_i_1 
       (.I0(\data[4]_i_2_n_0 ),
        .I1(\data[4]_i_3_n_0 ),
        .I2(sel_reg[3]),
        .I3(sel_reg[2]),
        .O(data_0[4]));
  LUT6 #(
    .INIT(64'hCCFFAAF0CC00AAF0)) 
    \data[4]_i_2 
       (.I0(vccint[4]),
        .I1(vccint[20]),
        .I2(sensor[12]),
        .I3(sel_reg[0]),
        .I4(sel_reg[1]),
        .I5(vccint[12]),
        .O(\data[4]_i_2_n_0 ));
  LUT6 #(
    .INIT(64'hCCFFAAF0CC00AAF0)) 
    \data[4]_i_3 
       (.I0(temp[12]),
        .I1(sensor[4]),
        .I2(temp[4]),
        .I3(sel_reg[0]),
        .I4(sel_reg[1]),
        .I5(temp[20]),
        .O(\data[4]_i_3_n_0 ));
  LUT4 #(
    .INIT(16'h0A0C)) 
    \data[5]_i_1 
       (.I0(\data[5]_i_2_n_0 ),
        .I1(\data[5]_i_3_n_0 ),
        .I2(sel_reg[3]),
        .I3(sel_reg[2]),
        .O(data_0[5]));
  LUT6 #(
    .INIT(64'hCCFFAAF0CC00AAF0)) 
    \data[5]_i_2 
       (.I0(vccint[5]),
        .I1(vccint[21]),
        .I2(sensor[13]),
        .I3(sel_reg[0]),
        .I4(sel_reg[1]),
        .I5(vccint[13]),
        .O(\data[5]_i_2_n_0 ));
  LUT6 #(
    .INIT(64'hCCFFAAF0CC00AAF0)) 
    \data[5]_i_3 
       (.I0(temp[13]),
        .I1(sensor[5]),
        .I2(temp[5]),
        .I3(sel_reg[0]),
        .I4(sel_reg[1]),
        .I5(temp[21]),
        .O(\data[5]_i_3_n_0 ));
  LUT4 #(
    .INIT(16'h0A0C)) 
    \data[6]_i_1 
       (.I0(\data[6]_i_2_n_0 ),
        .I1(\data[6]_i_3_n_0 ),
        .I2(sel_reg[3]),
        .I3(sel_reg[2]),
        .O(data_0[6]));
  LUT6 #(
    .INIT(64'hCCFFAAF0CC00AAF0)) 
    \data[6]_i_2 
       (.I0(vccint[6]),
        .I1(vccint[22]),
        .I2(sensor[14]),
        .I3(sel_reg[0]),
        .I4(sel_reg[1]),
        .I5(vccint[14]),
        .O(\data[6]_i_2_n_0 ));
  LUT6 #(
    .INIT(64'hCCFFAAF0CC00AAF0)) 
    \data[6]_i_3 
       (.I0(temp[14]),
        .I1(sensor[6]),
        .I2(temp[6]),
        .I3(sel_reg[0]),
        .I4(sel_reg[1]),
        .I5(temp[22]),
        .O(\data[6]_i_3_n_0 ));
  LUT4 #(
    .INIT(16'h8808)) 
    \data[7]_i_1 
       (.I0(counter1__10),
        .I1(enable),
        .I2(sendin),
        .I3(sendant),
        .O(sel));
  LUT4 #(
    .INIT(16'h0A0C)) 
    \data[7]_i_2 
       (.I0(\data[7]_i_3_n_0 ),
        .I1(\data[7]_i_4_n_0 ),
        .I2(sel_reg[3]),
        .I3(sel_reg[2]),
        .O(data_0[7]));
  LUT6 #(
    .INIT(64'hCCFFAAF0CC00AAF0)) 
    \data[7]_i_3 
       (.I0(vccint[7]),
        .I1(vccint[23]),
        .I2(sensor[15]),
        .I3(sel_reg[0]),
        .I4(sel_reg[1]),
        .I5(vccint[15]),
        .O(\data[7]_i_3_n_0 ));
  LUT6 #(
    .INIT(64'hCCFFAAF0CC00AAF0)) 
    \data[7]_i_4 
       (.I0(temp[15]),
        .I1(sensor[7]),
        .I2(temp[7]),
        .I3(sel_reg[0]),
        .I4(sel_reg[1]),
        .I5(temp[23]),
        .O(\data[7]_i_4_n_0 ));
  FDCE \data_reg[0] 
       (.C(clk),
        .CE(sel),
        .CLR(send_i_2_n_0),
        .D(data_0[0]),
        .Q(data[0]));
  FDCE \data_reg[1] 
       (.C(clk),
        .CE(sel),
        .CLR(send_i_2_n_0),
        .D(data_0[1]),
        .Q(data[1]));
  FDCE \data_reg[2] 
       (.C(clk),
        .CE(sel),
        .CLR(send_i_2_n_0),
        .D(data_0[2]),
        .Q(data[2]));
  FDCE \data_reg[3] 
       (.C(clk),
        .CE(sel),
        .CLR(send_i_2_n_0),
        .D(data_0[3]),
        .Q(data[3]));
  FDCE \data_reg[4] 
       (.C(clk),
        .CE(sel),
        .CLR(send_i_2_n_0),
        .D(data_0[4]),
        .Q(data[4]));
  FDCE \data_reg[5] 
       (.C(clk),
        .CE(sel),
        .CLR(send_i_2_n_0),
        .D(data_0[5]),
        .Q(data[5]));
  FDCE \data_reg[6] 
       (.C(clk),
        .CE(sel),
        .CLR(send_i_2_n_0),
        .D(data_0[6]),
        .Q(data[6]));
  FDCE \data_reg[7] 
       (.C(clk),
        .CE(sel),
        .CLR(send_i_2_n_0),
        .D(data_0[7]),
        .Q(data[7]));
  LUT6 #(
    .INIT(64'h7F00FFFF7F007F00)) 
    enable_i_1
       (.I0(counter1__10),
        .I1(sel_reg[3]),
        .I2(send_i_5_n_0),
        .I3(enable),
        .I4(sendant),
        .I5(sendin),
        .O(enable_i_1_n_0));
  FDCE enable_reg
       (.C(clk),
        .CE(1'b1),
        .CLR(send_i_2_n_0),
        .D(enable_i_1_n_0),
        .Q(enable));
  (* SOFT_HLUTNM = "soft_lutpair0" *) 
  LUT4 #(
    .INIT(16'h001F)) 
    \sel[0]_i_1 
       (.I0(sel_reg[1]),
        .I1(sel_reg[2]),
        .I2(sel_reg[3]),
        .I3(sel_reg[0]),
        .O(p_0_in[0]));
  (* SOFT_HLUTNM = "soft_lutpair2" *) 
  LUT3 #(
    .INIT(8'h14)) 
    \sel[1]_i_1 
       (.I0(sel_reg[3]),
        .I1(sel_reg[1]),
        .I2(sel_reg[0]),
        .O(p_0_in[1]));
  (* SOFT_HLUTNM = "soft_lutpair0" *) 
  LUT4 #(
    .INIT(16'h1444)) 
    \sel[2]_i_1 
       (.I0(sel_reg[3]),
        .I1(sel_reg[2]),
        .I2(sel_reg[1]),
        .I3(sel_reg[0]),
        .O(p_0_in[2]));
  (* SOFT_HLUTNM = "soft_lutpair1" *) 
  LUT4 #(
    .INIT(16'h4002)) 
    \sel[3]_i_1 
       (.I0(sel_reg[3]),
        .I1(sel_reg[2]),
        .I2(sel_reg[1]),
        .I3(sel_reg[0]),
        .O(p_0_in[3]));
  FDCE \sel_reg[0] 
       (.C(clk),
        .CE(sel),
        .CLR(send_i_2_n_0),
        .D(p_0_in[0]),
        .Q(sel_reg[0]));
  FDCE \sel_reg[1] 
       (.C(clk),
        .CE(sel),
        .CLR(send_i_2_n_0),
        .D(p_0_in[1]),
        .Q(sel_reg[1]));
  FDCE \sel_reg[2] 
       (.C(clk),
        .CE(sel),
        .CLR(send_i_2_n_0),
        .D(p_0_in[2]),
        .Q(sel_reg[2]));
  FDCE \sel_reg[3] 
       (.C(clk),
        .CE(sel),
        .CLR(send_i_2_n_0),
        .D(p_0_in[3]),
        .Q(sel_reg[3]));
  LUT6 #(
    .INIT(64'hEEEEEEEE04440404)) 
    send_i_1
       (.I0(send_i_3_n_0),
        .I1(counter1__10),
        .I2(sel_reg[3]),
        .I3(send_i_5_n_0),
        .I4(reset),
        .I5(send),
        .O(send_i_1_n_0));
  LUT1 #(
    .INIT(2'h1)) 
    send_i_2
       (.I0(reset),
        .O(send_i_2_n_0));
  LUT3 #(
    .INIT(8'h4F)) 
    send_i_3
       (.I0(sendant),
        .I1(sendin),
        .I2(enable),
        .O(send_i_3_n_0));
  LUT6 #(
    .INIT(64'h8888888880808000)) 
    send_i_4
       (.I0(counter_reg[16]),
        .I1(counter_reg[15]),
        .I2(counter_reg[12]),
        .I3(counter_reg[11]),
        .I4(send_i_6_n_0),
        .I5(send_i_7_n_0),
        .O(counter1__10));
  (* SOFT_HLUTNM = "soft_lutpair1" *) 
  LUT3 #(
    .INIT(8'hFE)) 
    send_i_5
       (.I0(sel_reg[0]),
        .I1(sel_reg[1]),
        .I2(sel_reg[2]),
        .O(send_i_5_n_0));
  LUT6 #(
    .INIT(64'h8880808080808080)) 
    send_i_6
       (.I0(counter_reg[10]),
        .I1(counter_reg[9]),
        .I2(counter_reg[8]),
        .I3(counter_reg[7]),
        .I4(counter_reg[6]),
        .I5(counter_reg[5]),
        .O(send_i_6_n_0));
  LUT2 #(
    .INIT(4'hE)) 
    send_i_7
       (.I0(counter_reg[13]),
        .I1(counter_reg[14]),
        .O(send_i_7_n_0));
  FDCE send_reg
       (.C(clk),
        .CE(1'b1),
        .CLR(send_i_2_n_0),
        .D(send_i_1_n_0),
        .Q(send));
  FDCE sendant_reg
       (.C(clk),
        .CE(1'b1),
        .CLR(send_i_2_n_0),
        .D(sendin),
        .Q(sendant));
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
