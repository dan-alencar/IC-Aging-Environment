vlib modelsim_lib/work
vlib modelsim_lib/msim

vlib modelsim_lib/msim/xpm
vlib modelsim_lib/msim/xil_defaultlib

vmap xpm modelsim_lib/msim/xpm
vmap xil_defaultlib modelsim_lib/msim/xil_defaultlib

vlog -work xpm -64 -incr -mfcu  -sv "+incdir+../../../../../../../../2025.1/data/rsb/busdef" "+incdir+../../../aging-study.gen/sources_1/bd/design_1/ipshared/a9be" \
"/home/dan-alencar/2025.1/Vivado/data/ip/xpm/xpm_cdc/hdl/xpm_cdc.sv" \

vcom -work xpm -64 -93  \
"/home/dan-alencar/2025.1/data/ip/xpm/xpm_VCOMP.vhd" \

vlog -work xil_defaultlib -64 -incr -mfcu  "+incdir+../../../../../../../../2025.1/data/rsb/busdef" "+incdir+../../../aging-study.gen/sources_1/bd/design_1/ipshared/a9be" \
"../../../aging-study.srcs/sources_1/new/temp_catcher.v" \
"../../../aging-study.srcs/sim_1/new/sim.v" \

vlog -work xil_defaultlib \
"glbl.v"

