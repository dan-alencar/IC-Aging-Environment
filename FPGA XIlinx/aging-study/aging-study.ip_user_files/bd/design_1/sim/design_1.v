//Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
//Copyright 2022-2024 Advanced Micro Devices, Inc. All Rights Reserved.
//--------------------------------------------------------------------------------
//Tool Version: Vivado v.2024.2 (lin64) Build 5239630 Fri Nov 08 22:34:34 MST 2024
//Date        : Thu May 15 18:02:49 2025
//Host        : pop-os running 64-bit Pop!_OS 24.04 LTS
//Command     : generate_target design_1.bd
//Design      : design_1
//Purpose     : IP block netlist
//--------------------------------------------------------------------------------
`timescale 1 ps / 1 ps

(* CORE_GENERATION_INFO = "design_1,IP_Integrator,{x_ipVendor=xilinx.com,x_ipLibrary=BlockDiagram,x_ipName=design_1,x_ipVersion=1.00.a,x_ipLanguage=VERILOG,numBlks=13,numReposBlks=13,numNonXlnxBlks=0,numHierBlks=0,maxHierDepth=0,numSysgenBlks=0,numHlsBlks=0,numHdlrefBlks=9,numPkgbdBlks=0,bdsource=USER,da_clkrst_cnt=1,synth_mode=Hierarchical}" *) (* HW_HANDOFF = "design_1.hwdef" *) 
module design_1
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
  (* X_INTERFACE_INFO = "xilinx.com:signal:clock:1.0 CLK.CLK100MHZ CLK" *) (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME CLK.CLK100MHZ, ASSOCIATED_RESET reset, CLK_DOMAIN design_1_CLK100MHZ, FREQ_HZ 100000000, FREQ_TOLERANCE_HZ 0, INSERT_VIP 0, PHASE 0.0" *) input CLK100MHZ;
  output DP;
  input reset;
  input rx;
  output tx;

  wire [7:0]AN;
  wire [3:0]BinToBCD_0_bil;
  wire [3:0]BinToBCD_0_cent;
  wire [3:0]BinToBCD_0_dec;
  wire [3:0]BinToBCD_0_mil;
  wire [3:0]BinToBCD_0_quadr;
  wire [3:0]BinToBCD_0_quint;
  wire [3:0]BinToBCD_0_tril;
  wire [3:0]BinToBCD_0_un;
  wire CA;
  wire CB;
  wire CC;
  wire CD;
  wire CE;
  wire CF;
  wire CG;
  wire CLK100MHZ;
  wire DP;
  wire [15:0]Dff_0_ffoutput;
  wire clk_wiz_0_clk_en;
  wire clk_wiz_0_clk_orig;
  wire clk_wiz_0_psdone;
  wire clk_wiz_0_sensor0;
  wire controller_controller_0_change;
  wire controller_controller_0_psen;
  wire controller_controller_0_psincdec;
  wire controller_controller_0_send;
  wire failure_holder_0_held;
  wire modern_sensible_0_alarm;
  wire modern_sensible_0_ff1_out;
  wire not_series_0_critpath;
  wire not_series_0_start;
  wire reset;
  wire rx;
  wire [7:0]sensor_stream_0_data;
  wire sensor_stream_0_send;
  wire [6:0]temp_catcher_0_daddr;
  wire temp_catcher_0_den;
  wire [20:0]temp_catcher_0_temp;
  wire [20:0]temp_catcher_0_vccint;
  wire tx;
  wire [0:0]util_vector_logic_0_Res;
  wire [0:0]util_vector_logic_1_Res;
  wire [15:0]xadc_wiz_0_do_out;
  wire xadc_wiz_0_drdy_out;

  design_1_BinToBCD_0_0 BinToBCD_0
       (.bil(BinToBCD_0_bil),
        .bin({1'b0,1'b0,1'b0,1'b0,1'b0,Dff_0_ffoutput}),
        .cent(BinToBCD_0_cent),
        .clk(CLK100MHZ),
        .dec(BinToBCD_0_dec),
        .mil(BinToBCD_0_mil),
        .quadr(BinToBCD_0_quadr),
        .quint(BinToBCD_0_quint),
        .tril(BinToBCD_0_tril),
        .un(BinToBCD_0_un));
  design_1_DisplayController_0_0 DisplayController_0
       (.an(AN),
        .clk(CLK100MHZ),
        .dp(DP),
        .in0(BinToBCD_0_un),
        .in1(BinToBCD_0_dec),
        .in2(BinToBCD_0_cent),
        .in3(BinToBCD_0_mil),
        .in4(BinToBCD_0_bil),
        .in5(BinToBCD_0_tril),
        .in6(BinToBCD_0_quadr),
        .in7(BinToBCD_0_quint),
        .reset(reset),
        .seg0(CA),
        .seg1(CB),
        .seg2(CC),
        .seg3(CD),
        .seg4(CE),
        .seg5(CF),
        .seg6(CG));
  design_1_clk_wiz_0_0 clk_wiz_0
       (.clk_en(clk_wiz_0_clk_en),
        .clk_in1(CLK100MHZ),
        .clk_sys(clk_wiz_0_clk_orig),
        .psclk(CLK100MHZ),
        .psdone(clk_wiz_0_psdone),
        .psen(controller_controller_0_psen),
        .psincdec(controller_controller_0_psincdec),
        .reset(util_vector_logic_1_Res),
        .sensor0(clk_wiz_0_sensor0));
  design_1_controller_controller_0_0 controller_controller_0
       (.alarm(modern_sensible_0_alarm),
        .change(controller_controller_0_change),
        .clk(clk_wiz_0_clk_orig),
        .display_value(Dff_0_ffoutput),
        .psdone(clk_wiz_0_psdone),
        .psen(controller_controller_0_psen),
        .psincdec(controller_controller_0_psincdec),
        .reset(rx),
        .send(controller_controller_0_send));
  design_1_failure_holder_0_0 failure_holder_0
       (.ff1(not_series_0_start),
        .ff2(modern_sensible_0_ff1_out),
        .held(failure_holder_0_held),
        .reset(rx));
  design_1_modern_sensible_0_0 modern_sensible_0
       (.alarm(modern_sensible_0_alarm),
        .clk_en(clk_wiz_0_clk_en),
        .ff1_out(modern_sensible_0_ff1_out),
        .in_sensor(not_series_0_critpath),
        .psclk(clk_wiz_0_sensor0),
        .reset(util_vector_logic_1_Res),
        .sclk(clk_wiz_0_clk_orig));
  design_1_not_series_0_0 not_series_0
       (.clk(clk_wiz_0_clk_orig),
        .critpath(not_series_0_critpath),
        .start(not_series_0_start),
        .test_bit(controller_controller_0_change));
  design_1_sensor_stream_0_0 sensor_stream_0
       (.clk(CLK100MHZ),
        .data(sensor_stream_0_data),
        .failure(failure_holder_0_held),
        .reset(util_vector_logic_0_Res),
        .send(sensor_stream_0_send),
        .sendin(controller_controller_0_send),
        .sensor(Dff_0_ffoutput),
        .temp({1'b0,1'b0,1'b0,temp_catcher_0_temp}),
        .vccint({1'b0,1'b0,1'b0,temp_catcher_0_vccint}));
  design_1_temp_catcher_0_0 temp_catcher_0
       (.clk(CLK100MHZ),
        .daddr(temp_catcher_0_daddr),
        .den(temp_catcher_0_den),
        .do_data(xadc_wiz_0_do_out),
        .drdy(xadc_wiz_0_drdy_out),
        .reset(util_vector_logic_0_Res),
        .temp(temp_catcher_0_temp),
        .vccint(temp_catcher_0_vccint));
  design_1_uart_tx_0_0 uart_tx_0
       (.clk(CLK100MHZ),
        .data(sensor_stream_0_data),
        .reset(util_vector_logic_0_Res),
        .send(sensor_stream_0_send),
        .tx(tx));
  design_1_util_vector_logic_0_0 util_vector_logic_0
       (.Op1(reset),
        .Res(util_vector_logic_0_Res));
  design_1_util_vector_logic_0_1 util_vector_logic_1
       (.Op1(rx),
        .Res(util_vector_logic_1_Res));
  design_1_xadc_wiz_0_0 xadc_wiz_0
       (.daddr_in(temp_catcher_0_daddr),
        .dclk_in(CLK100MHZ),
        .den_in(temp_catcher_0_den),
        .di_in({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .do_out(xadc_wiz_0_do_out),
        .drdy_out(xadc_wiz_0_drdy_out),
        .dwe_in(1'b0),
        .reset_in(reset),
        .vn_in(1'b0),
        .vp_in(1'b0));
endmodule
