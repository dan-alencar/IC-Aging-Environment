

`ifdef TARGET_AUP15
 // `define USE_RESETN
  //`define USE_JTAG_TRSTN
 // `define USE_STATUS
  //`define USE_SWITCHES
  //`define USE_LEDS
  //`define USE_FAN
  `define USE_VIO
`endif

/* `define ila(__name, __signal)  \
  (* dont_touch = "yes" *) (* mark_debug = "true" *) logic [$bits(__signal)-1:0] __name; \
  assign __name = __signal; */

module croc_xilinx import croc_pkg::*; #(
  localparam int unsigned GpioCount = 4
) (
  input  logic  sys_clk_p,
  input  logic  sys_clk_n,

  output logic  uart_tx_o,
  input  logic  uart_rx_i
);

  ////////////////////////
  //  Clock Generation  //
  ////////////////////////
  
 

  wire sys_clk;
  wire soc_clk;

  IBUFDS #(
    
  ) i_bufds_sys_clk (
    .I  ( sys_clk_p ),
    .IB ( sys_clk_n ),
    .O  ( sys_clk   )
  );

  clk_wiz i_clkwiz (
    .clk_in1  ( sys_clk ),
    .reset    ( '0 ),
    .locked   ( ),
    .clk_out1   ( soc_clk )
  );

  /////////////////////
  //  System Inputs  //
  /////////////////////

  logic status_o;

  ////////////
  //  VIOs  //
  ////////////
  logic       vio_reset, vio_fetch_en, vio_gpio;
  logic [GpioCount-1:0] vio_gpio_i, vio_gpio_o;

`ifdef USE_VIO
  vio_0 i_vio (
    .clk        ( soc_clk      ),
    .probe_out0 ( vio_reset    ),
    .probe_out1 ( vio_fetch_en ),
    .probe_out2 ( vio_gpio     ),
    .probe_out3 ( vio_gpio_i[0] ),
    .probe_out4 ( vio_gpio_i[1] ),
    .probe_out5 ( vio_gpio_i[2] ),
    .probe_out6 ( vio_gpio_i[3] ),
    .probe_in0  ( status_o           ),
    .probe_in1  ( vio_gpio_o[0]     ),
    .probe_in2  ( vio_gpio_o[1]     ),
    .probe_in3  ( vio_gpio_o[2]     ),
    .probe_in4  ( vio_gpio_o[3]     )
  );
`else 
  assign vio_reset    = '1;
  assign vio_fetch_en = '1;
  assign vio_gpio     = '0;
  assign vio_gpio_i  = '0;
`endif 

  assign soc_rst      = ~vio_reset;



  //////////////////
  //  Reset Sync  //
  //////////////////

  wire rst_n;

  rstgen i_rstgen (
    .clk_i        ( soc_clk     ),
    .rst_ni       ( ~soc_rst    ),
    .test_mode_i  ( '0          ),
    .rst_no       ( rst_n       ),
    .init_no      ( )
  );

  ////////////
  //  JTAG  //
  ////////////

 `ifdef USE_JTAG_VDDGND
  assign jtag_vdd_o = 1'b1;
  assign jtag_gnd_o = 1'b0;
`endif
`ifndef USE_JTAG_TRSTN
  logic jtag_trst_ni;
  assign jtag_trst_ni = 1'b1;
`endif
 

  /////////////////////////
  // "RTC" Clock Divider //
  /////////////////////////

  logic rtc_clk_d, rtc_clk_q;
  logic [15:0] counter_d, counter_q;

  // Divide soc_clk (20 MHz) by 610 => ~32.768kHz RTC Clock
  // TODO: does genesys 2 have a 32.768kHz reference clock?
  always_comb begin
    counter_d = counter_q + 1;
    rtc_clk_d = rtc_clk_q;

    if(counter_q == 610) begin
      counter_d = '0;
      rtc_clk_d = ~rtc_clk_q;
    end
  end

  always_ff @(posedge soc_clk, negedge rst_n) begin
    if(~rst_n) begin
      counter_q <= '0;
      rtc_clk_q <= 0;
    end else begin
      counter_q <= counter_d;
      rtc_clk_q <= rtc_clk_d;
    end
  end 


logic  jtag_tck_i;
logic  jtag_tms_i;
logic  jtag_tdi_i;
logic  jtag_tdo_o;
assign jtag_tck_i   = 1'b0;  
assign jtag_tdi_i   = 1'b0;   
assign jtag_tms_i   = 1'b0;  
  

  //////////////////
  // Cheshire SoC //
  //////////////////
  logic  soc_testmode_i;
  assign soc_testmode_i = '0;

  croc_soc #(
    .GpioCount( GpioCount )
  )
  i_croc_soc (
    .clk_i           ( soc_clk        ),
    .rst_ni          ( vio_reset ), //soc_rst_n        ),
    .ref_clk_i       ( rtc_clk_q      ),
    .testmode_i      ( soc_testmode_i ),
    .fetch_en_i      ( vio_fetch_en  ), //soc_fetch_en //vio_fetch_en
    .status_o        ( status_o       ),

    .jtag_tck_i      (  jtag_tck_i   ), //jtag_tck_i
    .jtag_tdi_i      (  jtag_tdi_i   ), //jtag_tdi_i
    .jtag_tdo_o      (  jtag_tdo_o   ), //jtag_tdo_o
    .jtag_tms_i      (  jtag_tms_i   ), //jtag_tms_i
    .jtag_trst_ni    (  jtag_trst_ni ),

    .uart_rx_i       ( uart_rx_i ),
    .uart_tx_o       ( uart_tx_o ),

    .gpio_i          ( vio_gpio_i        ),             
    .gpio_o          ( vio_gpio_o        ),            
    .gpio_out_en_o   ( soc_gpio_out_en_o ) 
  );

endmodule
