#####################################################################
# aging_study_nexys4ddr - reproducible Vivado project creation
#
# Usage:
#   vivado -mode batch -source scripts/create_project.tcl
#
# Optional environment overrides:
#   VIVADO_PROJECT_NAME  Project name. Default: aging_study_nexys4ddr
#   VIVADO_PART          FPGA part. Default: xc7a100tcsg324-1
#   VIVADO_TOP           Top module. Default: design_1_wrapper
#   VIVADO_BUILD_DIR     Build directory. Default: ../build
#####################################################################

set script_dir [file dirname [file normalize [info script]]]
set project_root [file normalize [file join $script_dir ".."]]

proc env_or_default {name default_value} {
    if {[info exists ::env($name)] && $::env($name) ne ""} {
        return $::env($name)
    }
    return $default_value
}

set project_name [env_or_default VIVADO_PROJECT_NAME "aging_study_nexys4ddr"]
set target_part  [env_or_default VIVADO_PART "xc7a100tcsg324-1"]
set top_module   [env_or_default VIVADO_TOP "design_1_wrapper"]
set build_dir    [file normalize [env_or_default VIVADO_BUILD_DIR [file join $project_root "build"]]]
set project_dir  [file join $build_dir $project_name]
set artifacts_dir [file join $project_root "artifacts"]

puts "============================================================"
puts "Creating Vivado project: $project_name"
puts "Project root:           $project_root"
puts "Build directory:        $build_dir"
puts "Target part:            $target_part"
puts "Top module:             $top_module"
puts "============================================================"

file mkdir $build_dir
file mkdir $artifacts_dir

if {[llength [get_projects -quiet]] > 0} {
    close_project
}

create_project $project_name $project_dir -part $target_part -force
set_property target_language Verilog [current_project]
set_property simulator_language Mixed [current_project]
set_property default_lib xil_defaultlib [current_project]
set_property ip_cache_permissions {read write} [current_project]

set active_rtl [list \
    [file join $project_root "src/rtl/display/BINtoBCD.v"] \
    [file join $project_root "src/rtl/display/DisplayController.v"] \
    [file join $project_root "src/rtl/aging_sensor/Dff.v"] \
    [file join $project_root "src/rtl/aging_sensor/controller_controller.v"] \
    [file join $project_root "src/rtl/aging_sensor/failure_holder.v"] \
    [file join $project_root "src/rtl/aging_sensor/holder_button.v"] \
    [file join $project_root "src/rtl/aging_sensor/modern_sensible.v"] \
    [file join $project_root "src/rtl/aging_sensor/nand_series.v"] \
    [file join $project_root "src/rtl/aging_sensor/temp_catcher.v"] \
    [file join $project_root "src/rtl/aging_sensor/xadc_raw.v"] \
    [file join $project_root "src/rtl/uart/sensor_stream.v"] \
    [file join $project_root "src/rtl/uart/uart_tx.v"] \
]

set constraints [list \
    [file join $project_root "src/constraints/Nexys-4-DDR-Master.xdc"] \
    [file join $project_root "src/constraints/fixed_pnr_constraints.xdc"] \
]

set bd_file [file join $project_root "src/bd/design_1/design_1.bd"]
set bd_ip_files [glob -nocomplain [file join $project_root "src/bd/design_1/ip" "*" "*" "*.xci"]]

set all_inputs [concat $active_rtl $constraints [list $bd_file] $bd_ip_files]
foreach input_file $all_inputs {
    if {![file exists $input_file]} {
        error "Missing required project input: $input_file"
    }
}

puts "Adding RTL sources..."
add_files -norecurse -fileset sources_1 $active_rtl

puts "Adding constraints..."
add_files -norecurse -fileset constrs_1 $constraints
set fixed_pnr_xdc [file join $project_root "src/constraints/fixed_pnr_constraints.xdc"]
set_property PROCESSING_ORDER LATE [get_files $fixed_pnr_xdc]

puts "Adding Block Design..."
add_files -norecurse -fileset sources_1 $bd_file
set bd_obj [get_files $bd_file]
open_bd_design $bd_file

# Do not depend on imported or incremental DCP files from the old project.
catch {set_property synth_checkpoint_mode None $bd_obj}
catch {set_property generate_synth_checkpoint false $bd_obj}

update_compile_order -fileset sources_1

puts "Regenerating Block Design targets..."
validate_bd_design
save_bd_design
generate_target all $bd_obj
export_ip_user_files -of_objects $bd_obj -no_script -sync -force -quiet

puts "Creating generated HDL wrapper..."
make_wrapper -files $bd_obj -top -force
set wrapper_file [file join $project_dir "$project_name.gen" "sources_1" "bd" "design_1" "hdl" "design_1_wrapper.v"]
if {![file exists $wrapper_file]} {
    error "Expected generated wrapper not found: $wrapper_file"
}
add_files -norecurse -fileset sources_1 $wrapper_file

set_property top $top_module [get_filesets sources_1]
update_compile_order -fileset sources_1

report_ip_status -file [file join $artifacts_dir "ip_status.rpt"]

puts "Project created at: $project_dir/$project_name.xpr"
