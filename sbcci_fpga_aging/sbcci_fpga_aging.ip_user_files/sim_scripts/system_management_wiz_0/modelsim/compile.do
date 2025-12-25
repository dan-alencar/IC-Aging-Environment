vlib modelsim_lib/work
vlib modelsim_lib/msim

vlib modelsim_lib/msim/xil_defaultlib

vmap xil_defaultlib modelsim_lib/msim/xil_defaultlib

vlog -work xil_defaultlib -64 -incr -mfcu  "+incdir+../../../../../../../../2025.2/data/rsb/busdef" \
"../../../../sbcci_fpga_aging.gen/sources_1/ip/system_management_wiz_0/system_management_wiz_0_sysmon.v" \
"../../../../sbcci_fpga_aging.gen/sources_1/ip/system_management_wiz_0/system_management_wiz_0.v" \


vlog -work xil_defaultlib \
"glbl.v"

