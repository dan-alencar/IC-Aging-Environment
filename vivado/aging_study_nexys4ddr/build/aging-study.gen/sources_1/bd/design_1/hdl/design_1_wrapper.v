//Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
//Copyright 2022-2026 Advanced Micro Devices, Inc. All Rights Reserved.
//--------------------------------------------------------------------------------
//Tool Version: Vivado v.2025.2.1 (lin64) Build 6403652 Thu Mar 19 13:47:00 MDT 2026
//Date        : Wed May 13 12:48:55 2026
//Host        : gsem running 64-bit Linux Mint 22.3
//Command     : generate_target design_1_wrapper.bd
//Design      : design_1_wrapper
//Purpose     : IP block netlist
//--------------------------------------------------------------------------------
`timescale 1 ps / 1 ps

module design_1_wrapper
   (AN,
    CA,
    CB,
    CC,
    CD,
    CE,
    CF,
    CG,
    CLK100MHZ,
    DP,
    reset,
    rx,
    tx);
  output [7:0]AN;
  output CA;
  output CB;
  output CC;
  output CD;
  output CE;
  output CF;
  output CG;
  input CLK100MHZ;
  output DP;
  input reset;
  input rx;
  output tx;

  wire [7:0]AN;
  wire CA;
  wire CB;
  wire CC;
  wire CD;
  wire CE;
  wire CF;
  wire CG;
  wire CLK100MHZ;
  wire DP;
  wire reset;
  wire rx;
  wire tx;

  design_1 design_1_i
       (.AN(AN),
        .CA(CA),
        .CB(CB),
        .CC(CC),
        .CD(CD),
        .CE(CE),
        .CF(CF),
        .CG(CG),
        .CLK100MHZ(CLK100MHZ),
        .DP(DP),
        .reset(reset),
        .rx(rx),
        .tx(tx));
endmodule
