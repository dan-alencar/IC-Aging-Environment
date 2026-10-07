transcript on
if {[file exists gate_work]} {
	vdel -lib gate_work -all
}
vlib gate_work
vmap work gate_work

vlog  -work work +incdir+. {max10_aging_top.vo}

vlog -sv -work work +incdir+C:/Users/Diogo/Documents/CI\ Amazonia/Fase\ 2/max10_hdl_src/repo/max10_port/hdl/../../../../../../../Downloads {C:/Users/Diogo/Documents/CI Amazonia/Fase 2/max10_hdl_src/repo/max10_port/hdl/../../../../../../../Downloads/max10_aging_top_gate_tb.sv}

vsim -t 1ps -L altera_ver -L altera_lnsim_ver -L fiftyfivenm_ver -L gate_work -L work -voptargs="+acc"  max10_aging_top_gate_tb

add wave *
view structure
view signals
run -all
