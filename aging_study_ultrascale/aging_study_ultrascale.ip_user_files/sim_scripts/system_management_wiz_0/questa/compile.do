vlib questa_lib/work
vlib questa_lib/msim

vlib questa_lib/msim/xil_defaultlib

vmap xil_defaultlib questa_lib/msim/xil_defaultlib

vlog -work xil_defaultlib -64 -incr -mfcu  "+incdir+../../../../../../../../2025.2/data/rsb/busdef" \
"../../../../aging_study_ultrascale.gen/sources_1/ip/system_management_wiz_0/system_management_wiz_0_sysmon.v" \
"../../../../aging_study_ultrascale.gen/sources_1/ip/system_management_wiz_0/system_management_wiz_0.v" \


vlog -work xil_defaultlib \
"glbl.v"

