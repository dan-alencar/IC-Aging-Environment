// Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
// Copyright 2022-2024 Advanced Micro Devices, Inc. All Rights Reserved.
// --------------------------------------------------------------------------------
// Tool Version: Vivado v.2024.2 (lin64) Build 5239630 Fri Nov 08 22:34:34 MST 2024
// Date        : Fri Apr 25 14:18:17 2025
// Host        : alisson.lesc.ufc.br running 64-bit unknown
// Command     : write_verilog -force -mode funcsim
//               /home/alisson/Downloads/aging_mirai_tensao/Aging-dynamic/vivado_project/aging-study/aging-study.gen/sources_1/bd/design_1/ip/design_1_controller_controller_0_0/design_1_controller_controller_0_0_sim_netlist.v
// Design      : design_1_controller_controller_0_0
// Purpose     : This verilog netlist is a functional simulation representation of the design and should not be modified
//               or synthesized. This netlist cannot be used for SDF annotated simulation.
// Device      : xc7a100tcsg324-1
// --------------------------------------------------------------------------------
`timescale 1 ps / 1 ps

(* CHECK_LICENSE_TYPE = "design_1_controller_controller_0_0,controller_controller,{}" *) (* DowngradeIPIdentifiedWarnings = "yes" *) (* IP_DEFINITION_SOURCE = "module_ref" *) 
(* X_CORE_INFO = "controller_controller,Vivado 2024.2" *) 
(* NotValidForBitStream *)
module design_1_controller_controller_0_0
   (clk,
    reset,
    alarm,
    psdone,
    display_value,
    change,
    psincdec,
    send,
    psen);
  (* X_INTERFACE_INFO = "xilinx.com:signal:clock:1.0 clk CLK" *) (* X_INTERFACE_MODE = "slave" *) (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME clk, ASSOCIATED_RESET reset, FREQ_HZ 100000000, FREQ_TOLERANCE_HZ 0, PHASE 0.0, CLK_DOMAIN /clk_wiz_0_clk_out1, INSERT_VIP 0" *) input clk;
  (* X_INTERFACE_INFO = "xilinx.com:signal:reset:1.0 reset RST" *) (* X_INTERFACE_MODE = "slave" *) (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME reset, POLARITY ACTIVE_LOW, INSERT_VIP 0" *) input reset;
  input alarm;
  input psdone;
  output [15:0]display_value;
  output change;
  output psincdec;
  output send;
  output psen;

  wire \<const0> ;
  wire alarm;
  wire change;
  wire clk;
  wire [15:0]display_value;
  wire psdone;
  wire psen;
  wire reset;
  wire send;

  assign psincdec = \<const0> ;
  GND GND
       (.G(\<const0> ));
  design_1_controller_controller_0_0_controller_controller inst
       (.alarm(alarm),
        .change(change),
        .clk(clk),
        .display_value(display_value),
        .psdone(psdone),
        .psen(psen),
        .reset(reset),
        .send(send));
endmodule

(* ORIG_REF_NAME = "controller_controller" *) 
module design_1_controller_controller_0_0_controller_controller
   (display_value,
    psen,
    send,
    change,
    clk,
    reset,
    psdone,
    alarm);
  output [15:0]display_value;
  output psen;
  output send;
  output change;
  input clk;
  input reset;
  input psdone;
  input alarm;

  wire \FSM_sequential_state[1]_i_1_n_0 ;
  wire alarm;
  wire change;
  wire change_enable;
  wire change_enable__0;
  wire change_i_1_n_0;
  wire clk;
  wire [15:0]display_value;
  wire \display_value_reg[15]_i_1_n_0 ;
  wire \inc_count[0]_i_2_n_0 ;
  wire [15:0]inc_count_reg;
  wire \inc_count_reg[0]_i_1_n_0 ;
  wire \inc_count_reg[0]_i_1_n_1 ;
  wire \inc_count_reg[0]_i_1_n_2 ;
  wire \inc_count_reg[0]_i_1_n_3 ;
  wire \inc_count_reg[0]_i_1_n_4 ;
  wire \inc_count_reg[0]_i_1_n_5 ;
  wire \inc_count_reg[0]_i_1_n_6 ;
  wire \inc_count_reg[0]_i_1_n_7 ;
  wire \inc_count_reg[12]_i_1_n_1 ;
  wire \inc_count_reg[12]_i_1_n_2 ;
  wire \inc_count_reg[12]_i_1_n_3 ;
  wire \inc_count_reg[12]_i_1_n_4 ;
  wire \inc_count_reg[12]_i_1_n_5 ;
  wire \inc_count_reg[12]_i_1_n_6 ;
  wire \inc_count_reg[12]_i_1_n_7 ;
  wire \inc_count_reg[4]_i_1_n_0 ;
  wire \inc_count_reg[4]_i_1_n_1 ;
  wire \inc_count_reg[4]_i_1_n_2 ;
  wire \inc_count_reg[4]_i_1_n_3 ;
  wire \inc_count_reg[4]_i_1_n_4 ;
  wire \inc_count_reg[4]_i_1_n_5 ;
  wire \inc_count_reg[4]_i_1_n_6 ;
  wire \inc_count_reg[4]_i_1_n_7 ;
  wire \inc_count_reg[8]_i_1_n_0 ;
  wire \inc_count_reg[8]_i_1_n_1 ;
  wire \inc_count_reg[8]_i_1_n_2 ;
  wire \inc_count_reg[8]_i_1_n_3 ;
  wire \inc_count_reg[8]_i_1_n_4 ;
  wire \inc_count_reg[8]_i_1_n_5 ;
  wire \inc_count_reg[8]_i_1_n_6 ;
  wire \inc_count_reg[8]_i_1_n_7 ;
  wire [1:0]next_state;
  wire [1:0]next_state__0;
  wire psdone;
  wire psen;
  wire psen_reg_i_1_n_0;
  wire psen_reg_i_2_n_0;
  wire reset;
  wire send;
  wire sig_ant;
  wire signal;
  wire signal__0;
  wire [1:1]state;
  wire [3:3]\NLW_inc_count_reg[12]_i_1_CO_UNCONNECTED ;

  (* XILINX_LEGACY_PRIM = "LD" *) 
  (* XILINX_TRANSFORM_PINMAP = "VCC:GE GND:CLR" *) 
  LDCE #(
    .INIT(1'b0)) 
    \FSM_sequential_next_state_reg[0] 
       (.CLR(1'b0),
        .D(next_state__0[0]),
        .G(psen_reg_i_2_n_0),
        .GE(1'b1),
        .Q(next_state[0]));
  (* SOFT_HLUTNM = "soft_lutpair0" *) 
  LUT4 #(
    .INIT(16'h7770)) 
    \FSM_sequential_next_state_reg[0]_i_1 
       (.I0(psdone),
        .I1(signal__0),
        .I2(alarm),
        .I3(state),
        .O(next_state__0[0]));
  (* XILINX_LEGACY_PRIM = "LD" *) 
  (* XILINX_TRANSFORM_PINMAP = "VCC:GE GND:CLR" *) 
  LDCE #(
    .INIT(1'b0)) 
    \FSM_sequential_next_state_reg[1] 
       (.CLR(1'b0),
        .D(next_state__0[1]),
        .G(psen_reg_i_2_n_0),
        .GE(1'b1),
        .Q(next_state[1]));
  (* SOFT_HLUTNM = "soft_lutpair0" *) 
  LUT4 #(
    .INIT(16'h7707)) 
    \FSM_sequential_next_state_reg[1]_i_1 
       (.I0(psdone),
        .I1(signal__0),
        .I2(alarm),
        .I3(state),
        .O(next_state__0[1]));
  LUT1 #(
    .INIT(2'h1)) 
    \FSM_sequential_state[1]_i_1 
       (.I0(reset),
        .O(\FSM_sequential_state[1]_i_1_n_0 ));
  (* FSM_ENCODED_STATES = "iSTATE:10,iSTATE0:01,iSTATE1:11,iSTATE2:00" *) 
  FDCE \FSM_sequential_state_reg[0] 
       (.C(clk),
        .CE(1'b1),
        .CLR(\FSM_sequential_state[1]_i_1_n_0 ),
        .D(next_state[0]),
        .Q(signal__0));
  (* FSM_ENCODED_STATES = "iSTATE:10,iSTATE0:01,iSTATE1:11,iSTATE2:00" *) 
  FDCE \FSM_sequential_state_reg[1] 
       (.C(clk),
        .CE(1'b1),
        .CLR(\FSM_sequential_state[1]_i_1_n_0 ),
        .D(next_state[1]),
        .Q(state));
  (* OPT_MODIFIED = "MLO" *) 
  (* XILINX_LEGACY_PRIM = "LD" *) 
  (* XILINX_TRANSFORM_PINMAP = "VCC:GE GND:CLR" *) 
  LDCE #(
    .INIT(1'b0),
    .IS_G_INVERTED(1'b1)) 
    change_enable_reg
       (.CLR(1'b0),
        .D(change_enable__0),
        .G(state),
        .GE(1'b1),
        .Q(change_enable));
  LUT1 #(
    .INIT(2'h1)) 
    change_enable_reg_i_1
       (.I0(signal__0),
        .O(change_enable__0));
  LUT2 #(
    .INIT(4'h6)) 
    change_i_1
       (.I0(change_enable),
        .I1(change),
        .O(change_i_1_n_0));
  FDRE #(
    .INIT(1'b0)) 
    change_reg
       (.C(clk),
        .CE(1'b1),
        .D(change_i_1_n_0),
        .Q(change),
        .R(1'b0));
  (* XILINX_LEGACY_PRIM = "LD" *) 
  (* XILINX_TRANSFORM_PINMAP = "VCC:GE GND:CLR" *) 
  LDCE #(
    .INIT(1'b0)) 
    \display_value_reg[0] 
       (.CLR(1'b0),
        .D(inc_count_reg[0]),
        .G(\display_value_reg[15]_i_1_n_0 ),
        .GE(1'b1),
        .Q(display_value[0]));
  (* XILINX_LEGACY_PRIM = "LD" *) 
  (* XILINX_TRANSFORM_PINMAP = "VCC:GE GND:CLR" *) 
  LDCE #(
    .INIT(1'b0)) 
    \display_value_reg[10] 
       (.CLR(1'b0),
        .D(inc_count_reg[10]),
        .G(\display_value_reg[15]_i_1_n_0 ),
        .GE(1'b1),
        .Q(display_value[10]));
  (* XILINX_LEGACY_PRIM = "LD" *) 
  (* XILINX_TRANSFORM_PINMAP = "VCC:GE GND:CLR" *) 
  LDCE #(
    .INIT(1'b0)) 
    \display_value_reg[11] 
       (.CLR(1'b0),
        .D(inc_count_reg[11]),
        .G(\display_value_reg[15]_i_1_n_0 ),
        .GE(1'b1),
        .Q(display_value[11]));
  (* XILINX_LEGACY_PRIM = "LD" *) 
  (* XILINX_TRANSFORM_PINMAP = "VCC:GE GND:CLR" *) 
  LDCE #(
    .INIT(1'b0)) 
    \display_value_reg[12] 
       (.CLR(1'b0),
        .D(inc_count_reg[12]),
        .G(\display_value_reg[15]_i_1_n_0 ),
        .GE(1'b1),
        .Q(display_value[12]));
  (* XILINX_LEGACY_PRIM = "LD" *) 
  (* XILINX_TRANSFORM_PINMAP = "VCC:GE GND:CLR" *) 
  LDCE #(
    .INIT(1'b0)) 
    \display_value_reg[13] 
       (.CLR(1'b0),
        .D(inc_count_reg[13]),
        .G(\display_value_reg[15]_i_1_n_0 ),
        .GE(1'b1),
        .Q(display_value[13]));
  (* XILINX_LEGACY_PRIM = "LD" *) 
  (* XILINX_TRANSFORM_PINMAP = "VCC:GE GND:CLR" *) 
  LDCE #(
    .INIT(1'b0)) 
    \display_value_reg[14] 
       (.CLR(1'b0),
        .D(inc_count_reg[14]),
        .G(\display_value_reg[15]_i_1_n_0 ),
        .GE(1'b1),
        .Q(display_value[14]));
  (* XILINX_LEGACY_PRIM = "LD" *) 
  (* XILINX_TRANSFORM_PINMAP = "VCC:GE GND:CLR" *) 
  LDCE #(
    .INIT(1'b0)) 
    \display_value_reg[15] 
       (.CLR(1'b0),
        .D(inc_count_reg[15]),
        .G(\display_value_reg[15]_i_1_n_0 ),
        .GE(1'b1),
        .Q(display_value[15]));
  (* SOFT_HLUTNM = "soft_lutpair1" *) 
  LUT2 #(
    .INIT(4'h2)) 
    \display_value_reg[15]_i_1 
       (.I0(signal__0),
        .I1(state),
        .O(\display_value_reg[15]_i_1_n_0 ));
  (* XILINX_LEGACY_PRIM = "LD" *) 
  (* XILINX_TRANSFORM_PINMAP = "VCC:GE GND:CLR" *) 
  LDCE #(
    .INIT(1'b0)) 
    \display_value_reg[1] 
       (.CLR(1'b0),
        .D(inc_count_reg[1]),
        .G(\display_value_reg[15]_i_1_n_0 ),
        .GE(1'b1),
        .Q(display_value[1]));
  (* XILINX_LEGACY_PRIM = "LD" *) 
  (* XILINX_TRANSFORM_PINMAP = "VCC:GE GND:CLR" *) 
  LDCE #(
    .INIT(1'b0)) 
    \display_value_reg[2] 
       (.CLR(1'b0),
        .D(inc_count_reg[2]),
        .G(\display_value_reg[15]_i_1_n_0 ),
        .GE(1'b1),
        .Q(display_value[2]));
  (* XILINX_LEGACY_PRIM = "LD" *) 
  (* XILINX_TRANSFORM_PINMAP = "VCC:GE GND:CLR" *) 
  LDCE #(
    .INIT(1'b0)) 
    \display_value_reg[3] 
       (.CLR(1'b0),
        .D(inc_count_reg[3]),
        .G(\display_value_reg[15]_i_1_n_0 ),
        .GE(1'b1),
        .Q(display_value[3]));
  (* XILINX_LEGACY_PRIM = "LD" *) 
  (* XILINX_TRANSFORM_PINMAP = "VCC:GE GND:CLR" *) 
  LDCE #(
    .INIT(1'b0)) 
    \display_value_reg[4] 
       (.CLR(1'b0),
        .D(inc_count_reg[4]),
        .G(\display_value_reg[15]_i_1_n_0 ),
        .GE(1'b1),
        .Q(display_value[4]));
  (* XILINX_LEGACY_PRIM = "LD" *) 
  (* XILINX_TRANSFORM_PINMAP = "VCC:GE GND:CLR" *) 
  LDCE #(
    .INIT(1'b0)) 
    \display_value_reg[5] 
       (.CLR(1'b0),
        .D(inc_count_reg[5]),
        .G(\display_value_reg[15]_i_1_n_0 ),
        .GE(1'b1),
        .Q(display_value[5]));
  (* XILINX_LEGACY_PRIM = "LD" *) 
  (* XILINX_TRANSFORM_PINMAP = "VCC:GE GND:CLR" *) 
  LDCE #(
    .INIT(1'b0)) 
    \display_value_reg[6] 
       (.CLR(1'b0),
        .D(inc_count_reg[6]),
        .G(\display_value_reg[15]_i_1_n_0 ),
        .GE(1'b1),
        .Q(display_value[6]));
  (* XILINX_LEGACY_PRIM = "LD" *) 
  (* XILINX_TRANSFORM_PINMAP = "VCC:GE GND:CLR" *) 
  LDCE #(
    .INIT(1'b0)) 
    \display_value_reg[7] 
       (.CLR(1'b0),
        .D(inc_count_reg[7]),
        .G(\display_value_reg[15]_i_1_n_0 ),
        .GE(1'b1),
        .Q(display_value[7]));
  (* XILINX_LEGACY_PRIM = "LD" *) 
  (* XILINX_TRANSFORM_PINMAP = "VCC:GE GND:CLR" *) 
  LDCE #(
    .INIT(1'b0)) 
    \display_value_reg[8] 
       (.CLR(1'b0),
        .D(inc_count_reg[8]),
        .G(\display_value_reg[15]_i_1_n_0 ),
        .GE(1'b1),
        .Q(display_value[8]));
  (* XILINX_LEGACY_PRIM = "LD" *) 
  (* XILINX_TRANSFORM_PINMAP = "VCC:GE GND:CLR" *) 
  LDCE #(
    .INIT(1'b0)) 
    \display_value_reg[9] 
       (.CLR(1'b0),
        .D(inc_count_reg[9]),
        .G(\display_value_reg[15]_i_1_n_0 ),
        .GE(1'b1),
        .Q(display_value[9]));
  LUT1 #(
    .INIT(2'h1)) 
    \inc_count[0]_i_2 
       (.I0(inc_count_reg[0]),
        .O(\inc_count[0]_i_2_n_0 ));
  FDCE \inc_count_reg[0] 
       (.C(psdone),
        .CE(1'b1),
        .CLR(\FSM_sequential_state[1]_i_1_n_0 ),
        .D(\inc_count_reg[0]_i_1_n_7 ),
        .Q(inc_count_reg[0]));
  (* ADDER_THRESHOLD = "11" *) 
  CARRY4 \inc_count_reg[0]_i_1 
       (.CI(1'b0),
        .CO({\inc_count_reg[0]_i_1_n_0 ,\inc_count_reg[0]_i_1_n_1 ,\inc_count_reg[0]_i_1_n_2 ,\inc_count_reg[0]_i_1_n_3 }),
        .CYINIT(1'b0),
        .DI({1'b0,1'b0,1'b0,1'b1}),
        .O({\inc_count_reg[0]_i_1_n_4 ,\inc_count_reg[0]_i_1_n_5 ,\inc_count_reg[0]_i_1_n_6 ,\inc_count_reg[0]_i_1_n_7 }),
        .S({inc_count_reg[3:1],\inc_count[0]_i_2_n_0 }));
  FDCE \inc_count_reg[10] 
       (.C(psdone),
        .CE(1'b1),
        .CLR(\FSM_sequential_state[1]_i_1_n_0 ),
        .D(\inc_count_reg[8]_i_1_n_5 ),
        .Q(inc_count_reg[10]));
  FDCE \inc_count_reg[11] 
       (.C(psdone),
        .CE(1'b1),
        .CLR(\FSM_sequential_state[1]_i_1_n_0 ),
        .D(\inc_count_reg[8]_i_1_n_4 ),
        .Q(inc_count_reg[11]));
  FDCE \inc_count_reg[12] 
       (.C(psdone),
        .CE(1'b1),
        .CLR(\FSM_sequential_state[1]_i_1_n_0 ),
        .D(\inc_count_reg[12]_i_1_n_7 ),
        .Q(inc_count_reg[12]));
  (* ADDER_THRESHOLD = "11" *) 
  CARRY4 \inc_count_reg[12]_i_1 
       (.CI(\inc_count_reg[8]_i_1_n_0 ),
        .CO({\NLW_inc_count_reg[12]_i_1_CO_UNCONNECTED [3],\inc_count_reg[12]_i_1_n_1 ,\inc_count_reg[12]_i_1_n_2 ,\inc_count_reg[12]_i_1_n_3 }),
        .CYINIT(1'b0),
        .DI({1'b0,1'b0,1'b0,1'b0}),
        .O({\inc_count_reg[12]_i_1_n_4 ,\inc_count_reg[12]_i_1_n_5 ,\inc_count_reg[12]_i_1_n_6 ,\inc_count_reg[12]_i_1_n_7 }),
        .S(inc_count_reg[15:12]));
  FDCE \inc_count_reg[13] 
       (.C(psdone),
        .CE(1'b1),
        .CLR(\FSM_sequential_state[1]_i_1_n_0 ),
        .D(\inc_count_reg[12]_i_1_n_6 ),
        .Q(inc_count_reg[13]));
  FDCE \inc_count_reg[14] 
       (.C(psdone),
        .CE(1'b1),
        .CLR(\FSM_sequential_state[1]_i_1_n_0 ),
        .D(\inc_count_reg[12]_i_1_n_5 ),
        .Q(inc_count_reg[14]));
  FDCE \inc_count_reg[15] 
       (.C(psdone),
        .CE(1'b1),
        .CLR(\FSM_sequential_state[1]_i_1_n_0 ),
        .D(\inc_count_reg[12]_i_1_n_4 ),
        .Q(inc_count_reg[15]));
  FDCE \inc_count_reg[1] 
       (.C(psdone),
        .CE(1'b1),
        .CLR(\FSM_sequential_state[1]_i_1_n_0 ),
        .D(\inc_count_reg[0]_i_1_n_6 ),
        .Q(inc_count_reg[1]));
  FDCE \inc_count_reg[2] 
       (.C(psdone),
        .CE(1'b1),
        .CLR(\FSM_sequential_state[1]_i_1_n_0 ),
        .D(\inc_count_reg[0]_i_1_n_5 ),
        .Q(inc_count_reg[2]));
  FDCE \inc_count_reg[3] 
       (.C(psdone),
        .CE(1'b1),
        .CLR(\FSM_sequential_state[1]_i_1_n_0 ),
        .D(\inc_count_reg[0]_i_1_n_4 ),
        .Q(inc_count_reg[3]));
  FDCE \inc_count_reg[4] 
       (.C(psdone),
        .CE(1'b1),
        .CLR(\FSM_sequential_state[1]_i_1_n_0 ),
        .D(\inc_count_reg[4]_i_1_n_7 ),
        .Q(inc_count_reg[4]));
  (* ADDER_THRESHOLD = "11" *) 
  CARRY4 \inc_count_reg[4]_i_1 
       (.CI(\inc_count_reg[0]_i_1_n_0 ),
        .CO({\inc_count_reg[4]_i_1_n_0 ,\inc_count_reg[4]_i_1_n_1 ,\inc_count_reg[4]_i_1_n_2 ,\inc_count_reg[4]_i_1_n_3 }),
        .CYINIT(1'b0),
        .DI({1'b0,1'b0,1'b0,1'b0}),
        .O({\inc_count_reg[4]_i_1_n_4 ,\inc_count_reg[4]_i_1_n_5 ,\inc_count_reg[4]_i_1_n_6 ,\inc_count_reg[4]_i_1_n_7 }),
        .S(inc_count_reg[7:4]));
  FDCE \inc_count_reg[5] 
       (.C(psdone),
        .CE(1'b1),
        .CLR(\FSM_sequential_state[1]_i_1_n_0 ),
        .D(\inc_count_reg[4]_i_1_n_6 ),
        .Q(inc_count_reg[5]));
  FDCE \inc_count_reg[6] 
       (.C(psdone),
        .CE(1'b1),
        .CLR(\FSM_sequential_state[1]_i_1_n_0 ),
        .D(\inc_count_reg[4]_i_1_n_5 ),
        .Q(inc_count_reg[6]));
  FDCE \inc_count_reg[7] 
       (.C(psdone),
        .CE(1'b1),
        .CLR(\FSM_sequential_state[1]_i_1_n_0 ),
        .D(\inc_count_reg[4]_i_1_n_4 ),
        .Q(inc_count_reg[7]));
  FDCE \inc_count_reg[8] 
       (.C(psdone),
        .CE(1'b1),
        .CLR(\FSM_sequential_state[1]_i_1_n_0 ),
        .D(\inc_count_reg[8]_i_1_n_7 ),
        .Q(inc_count_reg[8]));
  (* ADDER_THRESHOLD = "11" *) 
  CARRY4 \inc_count_reg[8]_i_1 
       (.CI(\inc_count_reg[4]_i_1_n_0 ),
        .CO({\inc_count_reg[8]_i_1_n_0 ,\inc_count_reg[8]_i_1_n_1 ,\inc_count_reg[8]_i_1_n_2 ,\inc_count_reg[8]_i_1_n_3 }),
        .CYINIT(1'b0),
        .DI({1'b0,1'b0,1'b0,1'b0}),
        .O({\inc_count_reg[8]_i_1_n_4 ,\inc_count_reg[8]_i_1_n_5 ,\inc_count_reg[8]_i_1_n_6 ,\inc_count_reg[8]_i_1_n_7 }),
        .S(inc_count_reg[11:8]));
  FDCE \inc_count_reg[9] 
       (.C(psdone),
        .CE(1'b1),
        .CLR(\FSM_sequential_state[1]_i_1_n_0 ),
        .D(\inc_count_reg[8]_i_1_n_6 ),
        .Q(inc_count_reg[9]));
  (* XILINX_LEGACY_PRIM = "LD" *) 
  (* XILINX_TRANSFORM_PINMAP = "VCC:GE GND:CLR" *) 
  LDCE #(
    .INIT(1'b0)) 
    psen_reg
       (.CLR(1'b0),
        .D(psen_reg_i_1_n_0),
        .G(psen_reg_i_2_n_0),
        .GE(1'b1),
        .Q(psen));
  (* SOFT_HLUTNM = "soft_lutpair2" *) 
  LUT2 #(
    .INIT(4'h2)) 
    psen_reg_i_1
       (.I0(state),
        .I1(signal__0),
        .O(psen_reg_i_1_n_0));
  (* SOFT_HLUTNM = "soft_lutpair1" *) 
  LUT2 #(
    .INIT(4'hB)) 
    psen_reg_i_2
       (.I0(state),
        .I1(signal__0),
        .O(psen_reg_i_2_n_0));
  LUT2 #(
    .INIT(4'h2)) 
    send_INST_0
       (.I0(signal),
        .I1(sig_ant),
        .O(send));
  FDRE sig_ant_reg
       (.C(clk),
        .CE(1'b1),
        .D(signal),
        .Q(sig_ant),
        .R(1'b0));
  (* OPT_MODIFIED = "MLO" *) 
  (* XILINX_LEGACY_PRIM = "LD" *) 
  (* XILINX_TRANSFORM_PINMAP = "VCC:GE GND:CLR" *) 
  LDCE #(
    .INIT(1'b0),
    .IS_G_INVERTED(1'b1)) 
    signal_reg
       (.CLR(1'b0),
        .D(signal__0),
        .G(state),
        .GE(1'b1),
        .Q(signal));
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
