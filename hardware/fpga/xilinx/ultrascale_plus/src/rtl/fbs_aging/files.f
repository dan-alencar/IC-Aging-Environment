// Compile order for fbs_aging_top; paths relative to hardware/fpga/xilinx/ultrascale_plus.
// The fbs platform RTL comes first, from the submodule (its own files.f, prefixed).
src/rtl/fbs_aging/fbs_aging_pkg.sv
src/rtl/fbs_aging/aging_sweep.sv
src/rtl/fbs_aging/aging_stats.sv
src/rtl/fbs_aging/aging_core.sv
src/rtl/fbs_aging/aging_clocks.sv
src/rtl/fbs_aging/aging_fabric.sv
src/rtl/fbs_aging/fbs_aging_top.sv
