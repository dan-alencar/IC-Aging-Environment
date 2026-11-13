// IC-Aging on RV02A with the fbs platform (fpgaging-board-support SPEC §5, §6.1).
//
//   board oscillator -> BUFG -> platform + aging core (100 MHz)
//                    -> MMCM -> measurement clocks of the chains and sensors
//   J9 <-> fbs_platform <-> STM32 USART1; FPGA_APP = aging_core
//
// Chains (the colleague's au15p_multi_B set plus a reference chain):
//   0 inferred adder 256 bits (the main sensor, AGING_WINDOW)   5..8 LUT 8/16/24/32 stages
//   1..4 CARRY8 128/256/512/1024 bits                            9 reference: as chain 0, not stressed
// No IP cores: the design builds with any Vivado version that knows the part.
module fbs_aging_top #(
  parameter logic [31:0] BUILD_ID = 32'h0,
  parameter logic [31:0] GIT_HASH = 32'h0,
  // simulation: a slower clock, a faster UART, short periods, a fixed DNA and USR_ACCESS
  parameter int unsigned CLK_FREQ_HZ    = 100_000_000,
  parameter int unsigned BAUD           = 125_000,
  parameter int unsigned REF_UNIT_MS    = 1000,
  parameter int unsigned WINDOW_MS      = 1000,
  parameter int unsigned REF_PERIOD_S   = 60,
  parameter int unsigned INFO_PERIOD_MS = 60_000,
  parameter int unsigned SYSMON_AVG_LOG2 = 10,
  parameter logic [95:0] SIM_DNA        = 96'h40020000016069492D020185,
  parameter logic [31:0] SIM_USR_ACCESS = 32'h6DB4C000
) (
  input  logic sys_clk_p,
  input  logic sys_clk_n,
  input  logic fpga_uart_rx,
  output logic fpga_uart_tx,
  output logic mcu_usart1_rx,
  input  logic mcu_usart1_tx,
  input  logic fpga_button,
  output logic status_o,
  input  logic i2c_ac13_i,        // PMBus lines (sensed only; the STM32 owns the bus)
  input  logic i2c_ac14_i,
  // simulation model only (tied off on the board)
  input  logic [9:0][15:0] sim_slack_i,
  input  logic [1:0][15:0] sim_ro_rate_i
);
  import fbs_aging_pkg::*;
  localparam int unsigned N = 10;
  localparam int unsigned R = 2;
  localparam logic [7:0] KI = FBS_AGING_CHAIN_KIND_INFERRED, KC = FBS_AGING_CHAIN_KIND_CARRY8,
                         KL = FBS_AGING_CHAIN_KIND_LUT, KR = FBS_AGING_CHAIN_KIND_REFERENCE;
  localparam logic [N*8-1:0]  KINDS = {KR, KL, KL, KL, KL, KC, KC, KC, KC, KI};
  localparam logic [N*16-1:0] SIZES = {16'd256, 16'd32, 16'd24, 16'd16, 16'd8,
                                       16'd1024, 16'd512, 16'd256, 16'd128, 16'd256};

  logic clk, clk_ibuf;
`ifdef FBS_XILINX
  IBUFDS u_ibufds (.I(sys_clk_p), .IB(sys_clk_n), .O(clk_ibuf));
  BUFG   u_bufg   (.I(clk_ibuf), .O(clk));
`else
  assign clk_ibuf = sys_clk_p;
  assign clk      = clk_ibuf;
  wire unused_n = sys_clk_n;
`endif

  /* verilator lint_off PROCASSINIT */
  logic [3:0] por = '0;
  /* verilator lint_on PROCASSINIT */
  logic rst_ni;
  always_ff @(posedge clk) if (por != 4'hF) por <= por + 4'd1;
  assign rst_ni = (por == 4'hF);

  // ---------------------------------------------------------------- platform
  logic       a_rx_valid, a_rx_ready, a_rx_last, a_rx_empty;
  logic [7:0] a_rx_data, a_rx_type, a_rx_len, a_rx_seq;
  logic [3:0] a_rx_src;
  logic [1:0] a_rx_flags;
  logic       a_tx_valid, a_tx_ready, a_tx_last;
  logic [7:0] a_tx_data, a_tx_type, a_tx_len;
  logic [3:0] a_tx_dst;
  logic [1:0] a_tx_flags;
  logic [31:0] t_ms;
  logic       tick_1ms, tick_1hz;

  fbs_platform #(
    .CLK_FREQ_HZ(CLK_FREQ_HZ), .BAUD(BAUD), .BUILD_ID(BUILD_ID), .GIT_HASH(GIT_HASH), .NAME("fbs-icaging"),
    .SYSMON_AVG_LOG2(SYSMON_AVG_LOG2), .SIM_DNA(SIM_DNA), .SIM_USR_ACCESS(SIM_USR_ACCESS)
  ) u_platform (
    .clk, .rst_ni,
    .pc_rx_i(fpga_uart_rx), .pc_tx_o(fpga_uart_tx),
    .stm_rx_i(mcu_usart1_tx), .stm_tx_o(mcu_usart1_rx),
    .raw0_rx_i(1'b1), .raw0_tx_o(), .raw0_cts_i(1'b1),
    .raw1_rx_i(1'b1), .raw1_tx_o(), .raw1_cts_i(1'b1),
    .app_tx_valid_i(a_tx_valid), .app_tx_ready_o(a_tx_ready), .app_tx_data_i(a_tx_data),
    .app_tx_last_i(a_tx_last), .app_tx_type_i(a_tx_type), .app_tx_dst_i(a_tx_dst),
    .app_tx_flags_i(a_tx_flags), .app_tx_len_i(a_tx_len),
    .app_rx_valid_o(a_rx_valid), .app_rx_ready_i(a_rx_ready), .app_rx_data_o(a_rx_data),
    .app_rx_last_o(a_rx_last), .app_rx_empty_o(a_rx_empty), .app_rx_type_o(a_rx_type),
    .app_rx_src_o(a_rx_src), .app_rx_seq_o(a_rx_seq), .app_rx_flags_o(a_rx_flags),
    .app_rx_len_o(a_rx_len),
    .t_ms_o(t_ms), .tick_1ms_o(tick_1ms), .tick_1hz_o(tick_1hz)
  );

  // ---------------------------------------------------------------- measurement clocks
  logic clk_catch, clk_phase, clk_meas, locked, psen, psincdec, psdone;
  int   sim_phase;
  aging_clocks u_clocks (
    .clk_i(clk), .rst_i(!rst_ni), .clk_catch_o(clk_catch), .clk_phase_o(clk_phase), .clk_meas_o(clk_meas),
    .locked_o(locked), .psen_i(psen), .psincdec_i(psincdec), .psdone_o(psdone), .sim_phase_o(sim_phase));

  // ---------------------------------------------------------------- payload
  logic [N-1:0]       alarm, stress;
  logic               ro_en, ro_clr;
  logic [R-1:0][31:0] ro_count;

  aging_core #(
    .N(N), .R(R), .KINDS(KINDS), .SIZES(SIZES), .WINDOW_MS(WINDOW_MS), .REF_PERIOD_S(REF_PERIOD_S),
    .REF_UNIT_MS(REF_UNIT_MS),
    .INFO_PERIOD_MS(INFO_PERIOD_MS), .GIT_HASH(GIT_HASH), .BUILD_ID(BUILD_ID)
  ) u_core (
    .clk, .rst_ni, .t_ms_i(t_ms), .tick_1ms_i(tick_1ms),
    .locked_i(locked), .psen_o(psen), .psincdec_o(psincdec), .psdone_i(psdone),
    .alarm_i(alarm), .stress_o(stress), .ro_en_o(ro_en), .ro_clr_o(ro_clr), .ro_count_i(ro_count),
    .rx_valid_i(a_rx_valid), .rx_ready_o(a_rx_ready), .rx_data_i(a_rx_data), .rx_last_i(a_rx_last),
    .rx_empty_i(a_rx_empty), .rx_type_i(a_rx_type), .rx_src_i(a_rx_src), .rx_seq_i(a_rx_seq),
    .rx_flags_i(a_rx_flags), .rx_len_i(a_rx_len),
    .tx_valid_o(a_tx_valid), .tx_ready_i(a_tx_ready), .tx_data_o(a_tx_data), .tx_last_o(a_tx_last),
    .tx_type_o(a_tx_type), .tx_dst_o(a_tx_dst), .tx_flags_o(a_tx_flags), .tx_len_o(a_tx_len)
  );

  aging_fabric #(.N(N), .R(R), .KINDS(KINDS), .SIZES(SIZES)) u_fabric (
    .clk_meas, .clk_phase, .clk_catch, .stress_i(stress), .alarm_o(alarm),
    .ro_en_i(ro_en), .ro_clr_i(ro_clr), .ro_count_o(ro_count),
    .sim_phase_i(sim_phase), .sim_slack_i(sim_slack_i), .sim_ro_rate_i(sim_ro_rate_i));

  // LED: 1 Hz blink while the MMCM is locked, steady on otherwise
  logic blink;
  always_ff @(posedge clk) begin
    if (!rst_ni) blink <= 1'b0;
    else if (tick_1hz) blink <= !blink;
  end
  assign status_o = locked ? blink : 1'b1;

  wire unused = ^{fpga_button, i2c_ac13_i, i2c_ac14_i};
endmodule
