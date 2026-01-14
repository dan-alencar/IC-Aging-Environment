# ==============================================================================
# FPGA Reset Script via VIO (Vivado)
# Usage: vivado -mode batch -source reset_fpga.tcl -tclargs <path_to_probes.ltx>
# ==============================================================================

if { $argc > 0 } {
    set probes_file [lindex $argv 0]
} else {
    set probes_file ""
}

puts "============================================================"
puts "FPGA Soft Reset via VIO"
if { $probes_file != "" } {
    puts "Probes File: $probes_file"
}
puts "============================================================"

# Open Hardware Manager
open_hw_manager

# Connect to Server
if { [catch {connect_hw_server -url localhost:3121 -allow_non_jtag} err] } {
    if { [catch {connect_hw_server -url localhost:3121} err2] } {
        puts "ERROR: Failed to connect to hardware server: $err2"
        exit 1
    }
}

# Open Target
if { [catch {open_hw_target} err] } {
    puts "ERROR: Failed to open hardware target: $err"
    exit 1
}

# ==============================================================================
# FIX: REDUZIR FREQUÊNCIA DO JTAG
# O clock interno é ~20MHz. O JTAG precisa ser < 10MHz para estabilidade do VIO.
# ==============================================================================
set current_target [get_hw_targets]
puts "Reducing JTAG Frequency to 3 MHz for stability..."
set_property PARAM.FREQUENCY 3000000 $current_target

# Select Device
set devices [get_hw_devices]
if { [llength $devices] == 0 } {
    puts "ERROR: No FPGA devices found."
    exit 1
}
set device [lindex $devices 0]
current_hw_device $device
puts "Selected device: $device"

# CRUCIAL FIX: Associate the .ltx file BEFORE refreshing
if { $probes_file != "" && [file exists $probes_file] } {
    puts "Setting PROBES.FILE to: $probes_file"
    set_property PROBES.FILE $probes_file $device
} else {
    puts "WARNING: No probes file provided or file not found."
    puts "Vivado might not match the VIO core correctly."
}

# Refresh device to load VIO definitions
puts "Refreshing device..."
if { [catch {refresh_hw_device $device} err] } {
    puts "ERROR: Failed to refresh device: $err"
    puts "Possible causes: Clock stopped, JTAG too fast, or timing violation."
    exit 1
}

# ==============================================================================
# VIO COMMANDS
# ==============================================================================
puts "Locating VIO core (i_vio)..."

# Now Vivado knows the names, so we can filter by CELL_NAME
set vios [get_hw_vios -of_objects $device -filter {CELL_NAME=~"i_vio"}]

if { $vios == "" } {
    puts "ERROR: VIO core 'i_vio' not found."
    puts "Debug info (All VIOs): [get_hw_vios -of_objects $device]"
    exit 1
}
set vio [lindex $vios 0]
puts "Found VIO: $vio"

# Locate the reset probe
set reset_probe [get_hw_probes vio_reset -of_objects $vio]

if { $reset_probe == "" } {
    puts "ERROR: Probe 'vio_reset' not found in VIO core."
    exit 1
}

# Reset Sequence: 0 -> 1
puts "Step 1: Asserting Reset (0)..."
set_property OUTPUT_VALUE 0 $reset_probe
commit_hw_vio $reset_probe

after 100

puts "Step 2: Deasserting Reset (1)..."
set_property OUTPUT_VALUE 1 $reset_probe
commit_hw_vio $reset_probe

puts "============================================================"
puts "SUCCESS: FPGA Reset Sequence Completed."
puts "============================================================"

close_hw_target
disconnect_hw_server
close_hw_manager
exit 0
