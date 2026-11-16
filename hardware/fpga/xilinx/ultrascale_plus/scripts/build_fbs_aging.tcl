# Vivado batch build of fbs_aging_top (IC-Aging on the fbs platform), no IP cores:
#   vivado -mode batch -source scripts/build_fbs_aging.tcl [-tclargs OUT_DIR]
# Outputs: OUT_DIR/fbs_aging_top.bit, reports, the routed checkpoint, chains.txt (per-chain
# delays and slack) and fabric_pnr.txt (the locked placement and routes, for diff/md5sum).
# The aged logic is placed and routed from src/constraints/fbs_aging_fixed_pnr.xdc (V19).
# Environment: FBS_AGING_FREE_PNR=1 ignores that file (a reference build to extract it from);
# FBS_AGING_PLACE_DIRECTIVE sets the placer directive (a different one perturbs the rest of the
# design, to check that the aged logic does not move).
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
source $here/fbs_aging_pnr.tcl
set fixed_xdc $top/src/constraints/fbs_aging_fixed_pnr.xdc
set free_pnr [expr {[info exists ::env(FBS_AGING_FREE_PNR)] && $::env(FBS_AGING_FREE_PNR) eq "1"}]
set place_directive [expr {[info exists ::env(FBS_AGING_PLACE_DIRECTIVE)] ? $::env(FBS_AGING_PLACE_DIRECTIVE) : "Default"}]

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
set use_fixed [expr {!$free_pnr && [file exists $fixed_xdc]}]
if {$use_fixed} {
  # applied to the synthesised netlist (the cells it names do not exist before synthesis)
  read_xdc $fixed_xdc
} else {
  puts "fixed PnR: not used ([expr {$free_pnr ? "FBS_AGING_FREE_PNR=1" : "no $fixed_xdc"}])"
}
opt_design
if {$use_fixed} {
  # checked after opt_design, which removes a few synthesis cells the routed design never had
  set loose [filter [fbs_aging_fabric_cells] {!IS_LOC_FIXED}]
  set nfr [llength [filter [get_nets -quiet -hier -filter {NAME =~ u_fabric/*}] {FIXED_ROUTE != ""}]]
  puts "fixed PnR: [expr {[llength [fbs_aging_fabric_cells]] - [llength $loose]}] of [llength [fbs_aging_fabric_cells]] fabric cells placed, $nfr nets with a directed route"
  if {[llength $loose] > 0} {
    foreach c [lrange $loose 0 19] { puts "fixed PnR: not fixed: $c ([get_property REF_NAME $c])" }
    error "fixed PnR: $fixed_xdc does not cover every fabric cell (RTL changed? re-extract it)"
  }
}
place_design -directive $place_directive
phys_opt_design
route_design
report_utilization -file $out/util_impl.txt
report_timing_summary -max_paths 20 -file $out/timing.txt
report_clock_interaction -file $out/clock_interaction.txt
report_drc -file $out/drc.txt
report_methodology -file $out/methodology.txt
write_checkpoint -force $out/fbs_aging_top_routed.dcp
fbs_aging_report_chains $out/chains.txt
fbs_aging_dump_fabric $out/fabric_pnr.txt
# a fixed build must reproduce the frozen reference's chain timing to the picosecond
set ref_chains $top/src/constraints/fbs_aging_fixed_pnr_chains.txt
if {$use_fixed && [file exists $ref_chains]} {
  if {[fbs_aging_chain_rows $out/chains.txt] eq [fbs_aging_chain_rows $ref_chains]} {
    puts "fixed PnR: chain timing equals the frozen reference"
  } else {
    error "fixed PnR: chain timing differs from $ref_chains (diff it against $out/chains.txt)"
  }
}
set_property BITSTREAM.CONFIG.USR_ACCESS TIMESTAMP [current_design]
write_bitstream -force $out/fbs_aging_top.bit
puts "WNS = [get_property SLACK [get_timing_paths -max_paths 1 -nworst 1 -setup]]"
puts "WHS = [get_property SLACK [get_timing_paths -max_paths 1 -nworst 1 -hold]]"
