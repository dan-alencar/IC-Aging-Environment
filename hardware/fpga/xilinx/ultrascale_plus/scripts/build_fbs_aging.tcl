# Vivado batch build of fbs_aging_top (IC-Aging on the fbs platform), no IP cores:
#   vivado -mode batch -source scripts/build_fbs_aging.tcl [-tclargs OUT_DIR]
# Outputs: OUT_DIR/fbs_aging_top.bit, reports, and the routed checkpoint.
set here [file dirname [file normalize [info script]]]
set top  [file dirname $here]
set root [file normalize $top/../../../..]
set fbs  $root/external/fpgaging-board-support/fpga
set out  [expr {[llength $argv] > 0 ? [lindex $argv 0] : "$top/build/fbs_aging"}]
file mkdir $out
set part xcau15p-ffvb676-1-i

proc read_list {base flist} {
  set srcs {}
  foreach line [split [read [open $flist]] "\n"] {
    set line [string trim $line]
    if {$line ne "" && ![string match "//*" $line]} { lappend srcs $base/$line }
  }
  return $srcs
}
set srcs [concat [read_list $fbs $fbs/rtl/files.f] [read_list $top $top/src/rtl/fbs_aging/files.f]]
read_verilog -sv $srcs
read_xdc $fbs/constraints/rv02a_pins.xdc
read_xdc $top/src/constraints/fbs_aging.xdc

# identity (fbs SPEC §4.4): this repository's commit, dirty bit, commit count
set git_hash 0
set build_id 0
if {![catch {exec git -C $root rev-parse --short=7 HEAD} h]} {
  scan $h %x git_hash
  if {[string length [exec git -C $root status --porcelain --untracked-files=no]] > 0} {
    set git_hash [expr {$git_hash | 0x80000000}]
  }
  set build_id [exec git -C $root rev-list --count HEAD]
}
puts [format "GIT_HASH = 0x%08X BUILD_ID = %d" $git_hash $build_id]
synth_design -top fbs_aging_top -part $part -verilog_define FBS_XILINX \
  -generic [format "GIT_HASH=32'h%08X" $git_hash] -generic [format "BUILD_ID=32'h%08X" $build_id]
report_utilization -file $out/util_synth.txt
report_utilization -hierarchical -hierarchical_depth 3 -file $out/util_hier.txt
opt_design
place_design
phys_opt_design
route_design
report_utilization -file $out/util_impl.txt
report_timing_summary -max_paths 20 -file $out/timing.txt
report_clock_interaction -file $out/clock_interaction.txt
report_drc -file $out/drc.txt
report_methodology -file $out/methodology.txt
write_checkpoint -force $out/fbs_aging_top_routed.dcp
set_property BITSTREAM.CONFIG.USR_ACCESS TIMESTAMP [current_design]
write_bitstream -force $out/fbs_aging_top.bit
puts "WNS = [get_property SLACK [get_timing_paths -max_paths 1 -nworst 1 -setup]]"
puts "WHS = [get_property SLACK [get_timing_paths -max_paths 1 -nworst 1 -hold]]"
