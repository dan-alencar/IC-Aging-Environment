vlib modelsim_lib/work
vlib modelsim_lib/msim

vlib modelsim_lib/msim/xpm
vlib modelsim_lib/msim/xil_defaultlib
vlib modelsim_lib/msim/util_vector_logic_v2_0_4

vmap xpm modelsim_lib/msim/xpm
vmap xil_defaultlib modelsim_lib/msim/xil_defaultlib
vmap util_vector_logic_v2_0_4 modelsim_lib/msim/util_vector_logic_v2_0_4

vlog -work xpm -64 -incr -mfcu  -sv "+incdir+../../../../aging-study.gen/sources_1/bd/design_1/ipshared/3cbc" \
"/home/mirai/Xilinx/Vivado/2024.2/data/ip/xpm/xpm_cdc/hdl/xpm_cdc.sv" \

vcom -work xpm -64 -93  \
"/home/mirai/Xilinx/Vivado/2024.2/data/ip/xpm/xpm_VCOMP.vhd" \

vlog -work xil_defaultlib -64 -incr -mfcu  "+incdir+../../../../aging-study.gen/sources_1/bd/design_1/ipshared/3cbc" \
"../../../bd/design_1/ip/design_1_xadc_wiz_0_0/design_1_xadc_wiz_0_0.v" \
"../../../bd/design_1/ip/design_1_BinToBCD_0_0/sim/design_1_BinToBCD_0_0.v" \
"../../../bd/design_1/ip/design_1_DisplayController_0_0/sim/design_1_DisplayController_0_0.v" \

vlog -work util_vector_logic_v2_0_4 -64 -incr -mfcu  "+incdir+../../../../aging-study.gen/sources_1/bd/design_1/ipshared/3cbc" \
"../../../../aging-study.gen/sources_1/bd/design_1/ipshared/fd7b/hdl/util_vector_logic_v2_0_vl_rfs.v" \

vlog -work xil_defaultlib -64 -incr -mfcu  "+incdir+../../../../aging-study.gen/sources_1/bd/design_1/ipshared/3cbc" \
"../../../bd/design_1/ip/design_1_util_vector_logic_0_0/sim/design_1_util_vector_logic_0_0.v" \
"../../../bd/design_1/ip/design_1_temp_catcher_0_0/sim/design_1_temp_catcher_0_0.v" \
"../../../bd/design_1/ip/design_1_modern_sensible_0_0/sim/design_1_modern_sensible_0_0.v" \
"../../../bd/design_1/ip/design_1_clk_wiz_0_0/design_1_clk_wiz_0_0_clk_wiz.v" \
"../../../bd/design_1/ip/design_1_clk_wiz_0_0/design_1_clk_wiz_0_0.v" \
"../../../bd/design_1/ip/design_1_not_series_0_0/sim/design_1_not_series_0_0.v" \
"../../../bd/design_1/ip/design_1_sensor_stream_0_0/sim/design_1_sensor_stream_0_0.v" \
"../../../bd/design_1/ip/design_1_uart_tx_0_0/sim/design_1_uart_tx_0_0.v" \
"../../../bd/design_1/ip/design_1_controller_controller_0_0/sim/design_1_controller_controller_0_0.v" \
"../../../bd/design_1/ip/design_1_util_vector_logic_0_1/sim/design_1_util_vector_logic_0_1.v" \
"../../../bd/design_1/ip/design_1_failure_holder_0_0/sim/design_1_failure_holder_0_0.v" \
"../../../bd/design_1/sim/design_1.v" \

vlog -work xil_defaultlib \
"glbl.v"

