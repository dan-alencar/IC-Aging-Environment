transcript on
if {[file exists rtl_work]} {
	vdel -lib rtl_work -all
}
vlib rtl_work
vmap work rtl_work

vlog  -work work +incdir+C:/Users/Diogo/Documents/CI\ Amazonia/Fase\ 2/max10_hdl_src/repo/max10_port/hdl {C:/Users/Diogo/Documents/CI Amazonia/Fase 2/max10_hdl_src/repo/max10_port/hdl/aging_pll.v}
vlog  -work work +incdir+C:/Users/Diogo/Documents/CI\ Amazonia/Fase\ 2/max10_hdl_src/repo/max10_port/hdl/db {C:/Users/Diogo/Documents/CI Amazonia/Fase 2/max10_hdl_src/repo/max10_port/hdl/db/aging_pll_altpll.v}
vlog -sv -work work +incdir+C:/Users/Diogo/Documents/CI\ Amazonia/Fase\ 2/max10_hdl_src/repo/max10_port/hdl/src/rtl/display {C:/Users/Diogo/Documents/CI Amazonia/Fase 2/max10_hdl_src/repo/max10_port/hdl/src/rtl/display/hex7seg.sv}
vlog -sv -work work +incdir+C:/Users/Diogo/Documents/CI\ Amazonia/Fase\ 2/max10_hdl_src/repo/max10_port/hdl/src/rtl/uart {C:/Users/Diogo/Documents/CI Amazonia/Fase 2/max10_hdl_src/repo/max10_port/hdl/src/rtl/uart/uart_tx.sv}
vlog -sv -work work +incdir+C:/Users/Diogo/Documents/CI\ Amazonia/Fase\ 2/max10_hdl_src/repo/max10_port/hdl/src/rtl/uart {C:/Users/Diogo/Documents/CI Amazonia/Fase 2/max10_hdl_src/repo/max10_port/hdl/src/rtl/uart/uart_packet_sender.sv}
vlog -sv -work work +incdir+C:/Users/Diogo/Documents/CI\ Amazonia/Fase\ 2/max10_hdl_src/repo/max10_port/hdl/src/rtl/aging_sensor {C:/Users/Diogo/Documents/CI Amazonia/Fase 2/max10_hdl_src/repo/max10_port/hdl/src/rtl/aging_sensor/scc_controller.sv}
vlog -sv -work work +incdir+C:/Users/Diogo/Documents/CI\ Amazonia/Fase\ 2/max10_hdl_src/repo/max10_port/hdl/src/rtl/aging_sensor {C:/Users/Diogo/Documents/CI Amazonia/Fase 2/max10_hdl_src/repo/max10_port/hdl/src/rtl/aging_sensor/critical_path_chain.sv}
vlog -sv -work work +incdir+C:/Users/Diogo/Documents/CI\ Amazonia/Fase\ 2/max10_hdl_src/repo/max10_port/hdl/src/rtl/aging_sensor {C:/Users/Diogo/Documents/CI Amazonia/Fase 2/max10_hdl_src/repo/max10_port/hdl/src/rtl/aging_sensor/aging_sensor_core.sv}
vlog -sv -work work +incdir+C:/Users/Diogo/Documents/CI\ Amazonia/Fase\ 2/max10_hdl_src/repo/max10_port/hdl/src/rtl/top {C:/Users/Diogo/Documents/CI Amazonia/Fase 2/max10_hdl_src/repo/max10_port/hdl/src/rtl/top/max10_aging_top.sv}

vlog -sv -work work +incdir+C:/Users/Diogo/Documents/CI\ Amazonia/Fase\ 2/max10_hdl_src/repo/max10_port/hdl/../../../../../../../Downloads {C:/Users/Diogo/Documents/CI Amazonia/Fase 2/max10_hdl_src/repo/max10_port/hdl/../../../../../../../Downloads/max10_aging_top_gate_tb.sv}

vsim -t 1ps -L altera_ver -L lpm_ver -L sgate_ver -L altera_mf_ver -L altera_lnsim_ver -L fiftyfivenm_ver -L rtl_work -L work -voptargs="+acc"  max10_aging_top_gate_tb

add wave *
view structure
view signals
run -all
