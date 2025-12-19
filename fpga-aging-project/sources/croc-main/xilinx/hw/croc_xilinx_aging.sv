


`ifdef TARGET_AUP15
 // `define USE_RESETN
  //`define USE_JTAG_TRSTN
 // `define USE_STATUS
  //`define USE_SWITCHES
  //`define USE_LEDS
  //`define USE_FAN
  //`define USE_VIO
`endif



module croc_xilinx import croc_pkg::*; #(
  localparam int unsigned GpioCount = 4
) (
  input  logic  sys_clk_p,
  input  logic  sys_clk_n,

  output logic  mcu_usart1_rx,
  input  logic  mcu_usart1_tx,
  
  input  logic  fpga_button, //SW4 reset (R26) 
  output  wire   status_o, //LED D6 de status (AF14)
  
  input  logic  fpga_uart_rx, //sinal de uart novo, header J9
  output logic  fpga_uart_tx //sinal de uart novo, header J9
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



  //wire status_o;
  

  ////////////
  //  VIOs  //
  ////////////
  logic       vio_reset, vio_fetch_en, vio_gpio;
  logic [GpioCount-1:0] vio_gpio_i, vio_gpio_o;

`ifdef USE_VIO
  vio_0 i_vio (
    .clk        ( soc_clk      ),
    //.probe_out0 ( vio_reset    ),
    .probe_out0 ( vio_fetch_en ),
    .probe_out1 ( vio_gpio     ),
    .probe_out2 ( vio_gpio_i[0] ),
    .probe_out3 ( vio_gpio_i[1] ),
    .probe_out4 ( vio_gpio_i[2] ),
    .probe_out5 ( vio_gpio_i[3] ),
    //.probe_in0  ( status_o        ),
    .probe_in0  ( vio_gpio_o[0]     ),
    .probe_in1  ( vio_gpio_o[1]     ),
    .probe_in2  ( vio_gpio_o[2]     ),
    .probe_in3  ( vio_gpio_o[3]     )
  );
`else 
  assign vio_reset    = '1;
  assign vio_fetch_en = '1;
  assign vio_gpio     = '0;
  assign vio_gpio_i  = '0;
`endif 

  assign soc_rst      = ~fpga_button;




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


// Sinais internos
wire w_router_to_croc; 
wire w_router_to_stm;  
wire soc_tx_signal;    // TX saindo do CROC
wire w_heartbeat;
wire w_wd_reset_n;     // Reset vindo do Watchdog

// Conexões
assign w_heartbeat = vio_gpio_o[0]; // Bit 0 do GPIO do CROC usado como Heartbeat
assign mcu_usart1_rx = w_router_to_stm; // FPGA manda para STM RX

// Instância do Router
uart_router #(
  .CLK_FREQ(20000000), 
  .BAUD_RATE(125000),
  .WATCHDOG_MS(1000)
) u_router (
  .clk             ( soc_clk         ),
  .rst_n           ( rst_n           ),
  
  // PC Interface
  .uart_rx_phys    ( fpga_uart_rx    ), 
  .uart_tx_phys    ( fpga_uart_tx    ), 
  
  // CROC Interface
  .uart_tx_to_croc ( w_router_to_croc), 
  .uart_tx_from_croc( soc_tx_signal  ), 
  
  // STM32 Interface
  .uart_tx_to_stm  ( w_router_to_stm ), 
  .uart_tx_from_stm( mcu_usart1_tx   ), 
  
  // Segurança
  .heartbeat_pin   ( w_heartbeat     ),
  .safe_rst_n      ( w_wd_reset_n    ) 
);

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
    .rst_ni          ( rst_n          ),
    .ref_clk_i       ( rtc_clk_q      ),
    .testmode_i      ( soc_testmode_i ),
    .fetch_en_i      ( vio_fetch_en  ), //soc_fetch_en //vio_fetch_en
    .status_o        ( status_o    ),

    .jtag_tck_i      (  jtag_tck_i   ), //jtag_tck_i
    .jtag_tdi_i      (  jtag_tdi_i   ), //jtag_tdi_i
    .jtag_tdo_o      (  jtag_tdo_o   ), //jtag_tdo_o
    .jtag_tms_i      (  jtag_tms_i   ), //jtag_tms_i
    .jtag_trst_ni    (  jtag_trst_ni ),

    // O RX do CROC agora vem do Router, não mais direto de um pino externo
    .uart_rx_i       ( w_router_to_croc ), 
    
    // O TX do CROC continua saindo normalmente (para o PC ver os prints)
    .uart_tx_o       ( soc_tx_signal ),

    .gpio_i          ( vio_gpio_i        ),             
    .gpio_o          ( vio_gpio_o        ), // Ligado ao w_heartbeat lá em cima
 
    .gpio_out_en_o   ( soc_gpio_out_en_o )
);

endmodule
