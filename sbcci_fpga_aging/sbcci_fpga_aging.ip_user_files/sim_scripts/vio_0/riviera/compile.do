transcript off
onbreak {quit -force}
onerror {quit -force}
transcript on

vlib work
vlib riviera/xpm
vlib riviera/xil_defaultlib

vmap xpm riviera/xpm
vmap xil_defaultlib riviera/xil_defaultlib

vlog -work xpm  -incr "+incdir+../../../../../../../../2025.2/data/rsb/busdef" "+incdir+../../../../sbcci_fpga_aging.gen/sources_1/ip/vio_0/hdl/verilog" "+incdir+../../../../sbcci_fpga_aging.gen/sources_1/ip/vio_0/hdl" -l xpm -l xil_defaultlib \
"/home/dan-alencar/2025.2/data/ip/xpm/xpm_cdc/hdl/xpm_cdc.sv" \

vcom -work xpm -93  -incr \
"/home/dan-alencar/2025.2/data/ip/xpm/xpm_VCOMP.vhd" \

vlog -work xil_defaultlib  -incr -v2k5 "+incdir+../../../../../../../../2025.2/data/rsb/busdef" "+incdir+../../../../sbcci_fpga_aging.gen/sources_1/ip/vio_0/hdl/verilog" "+incdir+../../../../sbcci_fpga_aging.gen/sources_1/ip/vio_0/hdl" -l xpm -l xil_defaultlib \
"../../../../sbcci_fpga_aging.gen/sources_1/ip/vio_0/sim/vio_0.v" \


vlog -work xil_defaultlib \
"glbl.v"

