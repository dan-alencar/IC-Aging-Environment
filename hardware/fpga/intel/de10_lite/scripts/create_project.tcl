#####################################################################
# max10_aging_port - reproducible Quartus Prime project creation
#
# Mirrors the pattern used by vivado/*/scripts/create_project.tcl:
# a project regenerated from source-controlled RTL/constraints, never
# committed as compiled output.
#
# Usage:
#   quartus_sh -t scripts/create_project.tcl
#
# Optional environment overrides:
#   QUARTUS_PROJECT_NAME  Project name. Default: max10_aging_port
#   QUARTUS_PART          Device part. Default: 10M50DAF484C7G
#   QUARTUS_TOP           Top-level entity. Default: max10_aging_top
#   QUARTUS_BUILD_DIR     Build directory. Default: ../build
#
# STATUS: scaffold. The RTL_FILES / SDC_FILES / QSF_ASSIGNMENTS lists
# below are empty placeholders -- fill them in once F1/F2 deliver real
# design files. This script has not been run against a real Quartus
# Prime installation; verify the Tcl API (package versions, exact
# set_global_assignment names) against your installed version before
# relying on it.
#####################################################################

package require ::quartus::project

proc env_or_default {name default_value} {
    if {[info exists ::env($name)] && $::env($name) ne ""} {
        return $::env($name)
    }
    return $default_value
}

set script_dir     [file dirname [file normalize [info script]]]
set project_root   [file normalize [file join $script_dir ".."]]

set project_name   [env_or_default QUARTUS_PROJECT_NAME "max10_aging_port"]
set target_part     [env_or_default QUARTUS_PART "10M50DAF484C7G"]
set top_module      [env_or_default QUARTUS_TOP "max10_aging_top"]
set build_dir        [file normalize [env_or_default QUARTUS_BUILD_DIR [file join $project_root "build"]]]

puts "============================================================"
puts "Creating Quartus Prime project: $project_name"
puts "Project root:                  $project_root"
puts "Build directory:               $build_dir"
puts "Target part:                   $target_part"
puts "Top-level entity:              $top_module"
puts "============================================================"

file mkdir $build_dir
cd $build_dir

# TODO: once F1 delivers RTL, list files here (paths relative to $project_root):
#   src/rtl/top/max10_aging_top.sv
#   src/rtl/aging_sensor/...
set rtl_files [list \
]

# TODO: once F2 delivers constraints:
set sdc_files [list \
]

if {[project_exists $project_name]} {
    project_open $project_name -revision $project_name
} else {
    project_new $project_name -revision $project_name -overwrite
}

set_global_assignment -name FAMILY "MAX 10"
set_global_assignment -name DEVICE $target_part
set_global_assignment -name TOP_LEVEL_ENTITY $top_module
set_global_assignment -name ORIGINAL_QUARTUS_VERSION "TODO: pin the Quartus Prime version used for this project"

foreach f $rtl_files {
    set full_path [file join $project_root $f]
    if {![file exists $full_path]} {
        error "Missing required RTL file: $full_path"
    }
    if {[string match "*.sv" $f]} {
        set_global_assignment -name SYSTEMVERILOG_FILE $full_path
    } else {
        set_global_assignment -name VERILOG_FILE $full_path
    }
}

foreach f $sdc_files {
    set full_path [file join $project_root $f]
    if {![file exists $full_path]} {
        error "Missing required SDC file: $full_path"
    }
    set_global_assignment -name SDC_FILE $full_path
}

if {[llength $rtl_files] == 0} {
    puts "NOTE: no RTL files configured yet -- this created an empty project shell."
    puts "      Fill in \$rtl_files / \$sdc_files in this script once F1/F2 land."
}

export_assignments
project_close

puts "Project created at: $build_dir/$project_name.qpf"
