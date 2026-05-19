#####################################################################
# aging_study_nexys4ddr - reproducible Vivado project creation
# Pure RTL flow — no block design.
#
# Usage:
#   vivado -mode batch -source scripts/create_project.tcl
#
# Optional environment overrides:
#   VIVADO_PROJECT_NAME  Project name. Default: aging_study_nexys4ddr
#   VIVADO_PART          FPGA part. Default: xc7a100tcsg324-1
#   VIVADO_TOP           Top module. Default: nexys4_aging_top
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
set top_module   [env_or_default VIVADO_TOP "nexys4_aging_top"]
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
set_property ip_cache_permissions {read write} [current_project]

set active_rtl [list \
    [file join $project_root "src/rtl/top/nexys4_aging_top.sv"] \
    [file join $project_root "src/rtl/aging_sensor/adder_canary.sv"] \
    [file join $project_root "src/rtl/aging_sensor/controller_controller.sv"] \
    [file join $project_root "src/rtl/aging_sensor/failure_holder.sv"] \
    [file join $project_root "src/rtl/aging_sensor/lut_full_adder.sv"] \
    [file join $project_root "src/rtl/aging_sensor/modern_sensible.sv"] \
    [file join $project_root "src/rtl/aging_sensor/ripple_adder.sv"] \
    [file join $project_root "src/rtl/aging_sensor/temp_catcher.sv"] \
    [file join $project_root "src/rtl/display/BINtoBCD.sv"] \
    [file join $project_root "src/rtl/display/DisplayController.sv"] \
    [file join $project_root "src/rtl/uart/sensor_stream.sv"] \
    [file join $project_root "src/rtl/uart/uart_tx.sv"] \
    [file join $project_root "src/rtl/uart/uart_rx.sv"] \
    [file join $project_root "src/ip/clk_wiz_0/clk_wiz_0.v"] \
    [file join $project_root "src/ip/clk_wiz_0/clk_wiz_0_clk_wiz.v"] \
]

set constraints [list \
    [file join $project_root "src/constraints/Nexys-4-DDR-Master.xdc"] \
    [file join $project_root "src/constraints/fixed_pnr_constraints.xdc"] \
]

set ip_cores [list]

set all_inputs [concat $active_rtl $constraints]
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
if {[llength $ip_cores] > 0} {
    add_files -norecurse -fileset sources_1 $ip_cores
}

puts "Adding constraints..."
add_files -norecurse -fileset constrs_1 $constraints
set fixed_pnr_xdc [file join $project_root "src/constraints/fixed_pnr_constraints.xdc"]
set_property PROCESSING_ORDER    LATE  [get_files $fixed_pnr_xdc]
set_property USED_IN_SYNTHESIS   false [get_files $fixed_pnr_xdc]
set_property USED_IN_IMPLEMENTATION true [get_files $fixed_pnr_xdc]

puts "Creating VIO debug core..."
create_ip -name vio -vendor xilinx.com -library ip -module_name vio_0
set_property -dict [list \
    CONFIG.C_NUM_PROBE_IN  {10} \
    CONFIG.C_NUM_PROBE_OUT {0}  \
    CONFIG.C_PROBE_IN0_WIDTH {16} \
    CONFIG.C_PROBE_IN1_WIDTH {16} \
    CONFIG.C_PROBE_IN2_WIDTH {1}  \
    CONFIG.C_PROBE_IN3_WIDTH {1}  \
    CONFIG.C_PROBE_IN4_WIDTH {1}  \
    CONFIG.C_PROBE_IN5_WIDTH {21} \
    CONFIG.C_PROBE_IN6_WIDTH {21} \
    CONFIG.C_PROBE_IN7_WIDTH {16} \
    CONFIG.C_PROBE_IN8_WIDTH {16} \
    CONFIG.C_PROBE_IN9_WIDTH {1}  \
] [get_ips vio_0]
generate_target all [get_ips vio_0]
export_ip_user_files -of_objects [get_ips vio_0] -no_script -sync -force -quiet

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
