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

puts "============================================================"
puts "Building bitstream with $jobs parallel job(s)"
puts "============================================================"

reset_run synth_1
launch_runs synth_1 -jobs $jobs
wait_on_run synth_1

set synth_progress [get_property PROGRESS [get_runs synth_1]]
set synth_status [get_property STATUS [get_runs synth_1]]
puts "Synthesis status: $synth_status ($synth_progress)"
if {$synth_progress ne "100%"} {
    error "Synthesis did not complete successfully"
}

reset_run impl_1
launch_runs impl_1 -to_step write_bitstream -jobs $jobs
wait_on_run impl_1

set impl_progress [get_property PROGRESS [get_runs impl_1]]
set impl_status [get_property STATUS [get_runs impl_1]]
puts "Implementation status: $impl_status ($impl_progress)"
if {$impl_progress ne "100%"} {
    error "Implementation did not complete successfully"
}

set bitstream_file [file join $project_dir "$project_name.runs" "impl_1" "$top_module.bit"]
if {![file exists $bitstream_file]} {
    error "Expected bitstream not found: $bitstream_file"
}

set artifact_bitstream [file join $artifacts_dir "$project_name.bit"]
file copy -force $bitstream_file $artifact_bitstream

puts "============================================================"
puts "Bitstream copied to: $artifact_bitstream"
puts "============================================================"
