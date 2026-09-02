#####################################################################
# sbcci_fpga_aging - reproducible Vivado project creation
#
# Usage:
#   vivado -mode batch -source scripts/create_project.tcl
#
# Optional environment overrides:
#   VIVADO_PROJECT_NAME  Project name. Default: sbcci_fpga_aging
#   VIVADO_PART          FPGA part. Default: xcau15p-ffvb676-1-i
#   VIVADO_TOP           Top module. Default: fpga_unified_top
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

set project_name [env_or_default VIVADO_PROJECT_NAME "sbcci_fpga_aging"]
set target_part  [env_or_default VIVADO_PART "xcau15p-ffvb676-1-i"]
set top_module   [env_or_default VIVADO_TOP "fpga_unified_top"]
set build_dir    [file normalize [env_or_default VIVADO_BUILD_DIR [file join $project_root "build"]]]
set project_dir  [file join $build_dir $project_name]
set reports_dir  [file join $project_root "artifacts"]

puts "============================================================"
puts "Creating Vivado project: $project_name"
puts "Project root:           $project_root"
puts "Build directory:        $build_dir"
puts "Target part:            $target_part"
puts "Top module:             $top_module"
puts "============================================================"

file mkdir $build_dir
file mkdir $reports_dir

if {[llength [get_projects -quiet]] > 0} {
    close_project
}

create_project $project_name $project_dir -part $target_part -force
set_property target_language Verilog [current_project]
set_property simulator_language Mixed [current_project]
set_property default_lib xil_defaultlib [current_project]

set active_rtl [list \
    [file join $project_root "src/rtl/aging_sensor/controller_controller.v"] \
    [file join $project_root "src/rtl/aging_sensor/modern_sensible.v"] \
    [file join $project_root "src/rtl/aging_sensor/nand_series.v"] \
    [file join $project_root "src/rtl/monitor/sysmon_monitor.sv"] \
    [file join $project_root "src/rtl/uart/sensor_stream.v"] \
    [file join $project_root "src/rtl/uart/uart_arbiter.sv"] \
    [file join $project_root "src/rtl/uart/uart_router.sv"] \
    [file join $project_root "src/rtl/uart/uart_tx.v"] \
    [file join $project_root "src/rtl/top/fpga_unified_top.sv"] \
]

set constraints [list \
    [file join $project_root "src/constraints/fpga_aging_constraints.xdc"] \
]

set ip_cores [list \
    [file join $project_root "src/ip/clk_wiz_0/clk_wiz_0.xci"] \
    [file join $project_root "src/ip/vio_0/vio_0.xci"] \
    [file join $project_root "src/ip/xadc_wiz_0/xadc_wiz_0.xci"] \
]

set all_inputs [concat $active_rtl $constraints $ip_cores]
foreach input_file $all_inputs {
    if {![file exists $input_file]} {
        error "Missing required project input: $input_file"
    }
}

puts "Adding RTL sources..."
add_files -norecurse -fileset sources_1 $active_rtl
foreach sv_file [get_files -quiet "*.sv"] {
    set_property file_type SystemVerilog $sv_file
}

puts "Adding IP cores..."
add_files -norecurse -fileset sources_1 $ip_cores

puts "Adding constraints..."
add_files -norecurse -fileset constrs_1 $constraints

set_property top $top_module [get_filesets sources_1]
update_compile_order -fileset sources_1

puts "Generating IP targets..."
set project_ip [get_files -quiet *.xci]
if {[llength $project_ip] > 0} {
    generate_target all $project_ip
    export_ip_user_files -of_objects $project_ip -no_script -sync -force -quiet
    report_ip_status -file [file join $reports_dir "ip_status.rpt"]
}

puts "Project created at: $project_dir/$project_name.xpr"
