transcript off
onbreak {quit -force}
onerror {quit -force}
transcript on

vlib work
vlib riviera/xil_defaultlib

vmap xil_defaultlib riviera/xil_defaultlib

vlog -work xil_defaultlib  -incr -v2k5 "+incdir+../../../../../../../../2025.2/data/rsb/busdef" -l xil_defaultlib \
"../../../../sbcci_fpga_aging.gen/sources_1/ip/system_management_wiz_0/system_management_wiz_0_sysmon.v" \
"../../../../sbcci_fpga_aging.gen/sources_1/ip/system_management_wiz_0/system_management_wiz_0.v" \


vlog -work xil_defaultlib \
"glbl.v"

