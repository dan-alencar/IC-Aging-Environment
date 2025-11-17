transcript off
onbreak {quit -force}
onerror {quit -force}
transcript on

vlib work
vlib riviera/xpm
vlib riviera/xil_defaultlib

vmap xpm riviera/xpm
vmap xil_defaultlib riviera/xil_defaultlib

vlog -work xpm  -incr "+incdir+../../../../../../../../2025.1/data/rsb/busdef" "+incdir+../../../aging-study.gen/sources_1/bd/design_1/ipshared/a9be" -l xpm -l xil_defaultlib \
"/home/dan-alencar/2025.1/Vivado/data/ip/xpm/xpm_cdc/hdl/xpm_cdc.sv" \

vcom -work xpm -93  -incr \
"/home/dan-alencar/2025.1/data/ip/xpm/xpm_VCOMP.vhd" \

vlog -work xil_defaultlib  -incr -v2k5 "+incdir+../../../../../../../../2025.1/data/rsb/busdef" "+incdir+../../../aging-study.gen/sources_1/bd/design_1/ipshared/a9be" -l xpm -l xil_defaultlib \
"../../../aging-study.srcs/sources_1/new/temp_catcher.v" \
"../../../aging-study.srcs/sim_1/new/sim.v" \

vlog -work xil_defaultlib \
"glbl.v"

