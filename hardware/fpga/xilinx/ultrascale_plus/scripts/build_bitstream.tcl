#####################################################################
# sbcci_fpga_aging - batch bitstream build
#
# Usage:
#   vivado -mode batch -source scripts/build_bitstream.tcl
#
# Optional environment overrides:
#   VIVADO_JOBS  Parallel jobs. Default: 8
#   See create_project.tcl for project/path/part overrides.
#####################################################################

set script_dir [file dirname [file normalize [info script]]]
source [file join $script_dir "create_project.tcl"]

proc env_or_default_local {name default_value} {
    if {[info exists ::env($name)] && $::env($name) ne ""} {
        return $::env($name)
    }
    return $default_value
}

set jobs [env_or_default_local VIVADO_JOBS 8]
set artifacts_dir [file join $project_root "artifacts"]
file mkdir $artifacts_dir

proc assert_run_complete {run_name} {
    set run_obj [get_runs $run_name]
    set progress [get_property PROGRESS $run_obj]
    set status [get_property STATUS $run_obj]
    puts "$run_name status: $status ($progress)"

    if {$progress ne "100%" || ![string match "*Complete*" $status]} {
        error "$run_name did not complete successfully: $status ($progress)"
    }
}

puts "============================================================"
puts "Building bitstream with $jobs parallel job(s)"
puts "============================================================"

reset_run synth_1
launch_runs synth_1 -jobs $jobs
wait_on_run synth_1
assert_run_complete synth_1

reset_run impl_1
launch_runs impl_1 -to_step write_bitstream -jobs $jobs
wait_on_run impl_1
assert_run_complete impl_1

set bitstream_file [file join $project_dir "$project_name.runs" "impl_1" "$top_module.bit"]
if {![file exists $bitstream_file]} {
    error "Expected bitstream not found: $bitstream_file"
}

set artifact_bitstream [file join $artifacts_dir "$project_name.bit"]
file copy -force $bitstream_file $artifact_bitstream

open_run impl_1
report_timing_summary -file [file join $artifacts_dir "timing_summary.rpt"]
report_utilization -file [file join $artifacts_dir "utilization.rpt"]

foreach debug_probe [glob -nocomplain [file join $project_dir "$project_name.runs" "impl_1" "*.ltx"]] {
    file copy -force $debug_probe [file join $artifacts_dir [file tail $debug_probe]]
}

puts "============================================================"
puts "Bitstream copied to: $artifact_bitstream"
puts "Reports copied to:   $artifacts_dir"
puts "============================================================"
