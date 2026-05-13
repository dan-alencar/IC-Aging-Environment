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

proc collect_files {root_dir} {
    set result [list]
    foreach path [glob -nocomplain -directory $root_dir *] {
        if {[file isdirectory $path]} {
            set result [concat $result [collect_files $path]]
        } else {
            lappend result $path
        }
    }
    return $result
}

proc replace_in_file {path replacements} {
    set in [open $path r]
    set data [read $in]
    close $in

    set updated $data
    foreach {from to} $replacements {
        set updated [string map [list $from $to] $updated]
    }

    if {$updated ne $data} {
        set out [open $path w]
        puts -nonewline $out $updated
        close $out
    }
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

set source_bd_dir [file join $project_root "src/bd/design_1"]
set source_bd_file [file join $source_bd_dir "design_1.bd"]
set bd_work_dir [file join $build_dir "imported_src/bd/design_1"]
set bd_file [file join $bd_work_dir "design_1.bd"]
set bd_ip_files [glob -nocomplain [file join $source_bd_dir "ip" "*" "*" "*.xci"]]

set all_inputs [concat $active_rtl $constraints [list $source_bd_file] $bd_ip_files]
foreach input_file $all_inputs {
    if {![file exists $input_file]} {
        error "Missing required project input: $input_file"
    }
}

puts "Copying Block Design sources into build workspace..."
file delete -force [file join $build_dir "imported_src"]
file mkdir [file dirname $bd_work_dir]
file copy -force $source_bd_dir [file dirname $bd_work_dir]

set bd_gen_dir [file normalize [file join $build_dir "aging-study.gen"]]
foreach copied_file [collect_files $bd_work_dir] {
    set copied_ext [file extension $copied_file]
    if {$copied_ext eq ".bd" || $copied_ext eq ".xci"} {
        replace_in_file $copied_file [list \
            "../../../../aging-study.gen" $bd_gen_dir \
            "../../../../../../aging-study.gen" $bd_gen_dir \
        ]
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
set wrapper_result [make_wrapper -files $bd_obj -top -force]
set wrapper_file ""
foreach candidate $wrapper_result {
    set normalized_candidate [file normalize $candidate]
    if {[file exists $normalized_candidate]} {
        set wrapper_file $normalized_candidate
        break
    }
}

if {$wrapper_file eq ""} {
    set wrapper_candidates [list \
        [file join $project_dir "$project_name.gen" "sources_1" "bd" "design_1" "hdl" "design_1_wrapper.v"] \
        [file join $build_dir "aging-study.gen" "sources_1" "bd" "design_1" "hdl" "design_1_wrapper.v"] \
        [file join $project_root "aging-study.gen" "sources_1" "bd" "design_1" "hdl" "design_1_wrapper.v"] \
    ]
    foreach candidate $wrapper_candidates {
        set normalized_candidate [file normalize $candidate]
        if {[file exists $normalized_candidate]} {
            set wrapper_file $normalized_candidate
            break
        }
    }
}

if {![file exists $wrapper_file]} {
    error "Expected generated wrapper not found. Vivado returned '$wrapper_result'."
}
add_files -norecurse -fileset sources_1 $wrapper_file

set_property top $top_module [get_filesets sources_1]
update_compile_order -fileset sources_1

report_ip_status -file [file join $artifacts_dir "ip_status.rpt"]

puts "Project created at: $project_dir/$project_name.xpr"
