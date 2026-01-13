# ==============================================================================
# FPGA Programming Script for Vivado
# ==============================================================================
# Usage: vivado -mode batch -source program_fpga.tcl -tclargs <bitstream_path>
#
# This script programs an FPGA via JTAG using Vivado Hardware Manager.
# Compatible with both Vivado and Vivado Lab editions.
# ==============================================================================

# Check arguments
if { $argc < 1 } {
    puts "ERROR: Bitstream path not provided."
    puts "Usage: vivado -mode batch -source program_fpga.tcl -tclargs <bitstream.bit>"
    exit 1
}

set bit_file [lindex $argv 0]

# Verify bitstream file exists
if { ![file exists $bit_file] } {
    puts "ERROR: Bitstream file not found: $bit_file"
    exit 1
}

puts "============================================================"
puts "FPGA Programming Script"
puts "============================================================"
puts "Bitstream: $bit_file"
puts "============================================================"

# Open Hardware Manager
puts "Opening Hardware Manager..."
open_hw_manager

# Connect to local hardware server
# The -allow_non_jtag flag permits connections even if non-JTAG devices are present
puts "Connecting to hardware server (localhost:3121)..."
if { [catch {connect_hw_server -url localhost:3121 -allow_non_jtag} err] } {
    puts "WARNING: Could not connect with -allow_non_jtag, trying without..."
    if { [catch {connect_hw_server -url localhost:3121} err2] } {
        puts "ERROR: Failed to connect to hardware server: $err2"
        puts "Make sure hw_server is running or Vivado can start it."
        close_hw_manager
        exit 1
    }
}

# Open the hardware target (JTAG cable)
puts "Opening hardware target..."
if { [catch {open_hw_target} err] } {
    puts "ERROR: Failed to open hardware target: $err"
    puts "Check that the JTAG cable is connected and detected."
    disconnect_hw_server
    close_hw_manager
    exit 1
}

# Get list of devices on the JTAG chain
set devices [get_hw_devices]
if { [llength $devices] == 0 } {
    puts "ERROR: No FPGA devices found on JTAG chain."
    close_hw_target
    disconnect_hw_server
    close_hw_manager
    exit 1
}

puts "Found [llength $devices] device(s) on JTAG chain:"
foreach dev $devices {
    puts "  - $dev"
}

# Select the first device (typically the FPGA)
set device [lindex $devices 0]
puts "Selecting device: $device"
current_hw_device $device

# Refresh the device to ensure it's ready
puts "Refreshing device..."
refresh_hw_device -update_hw_probes false $device

# Configure the programming file
puts "Setting bitstream file..."
set_property PROGRAM.FILE $bit_file $device

# Program the FPGA
puts "Programming FPGA..."
puts "This may take a moment..."

if { [catch {program_hw_devices $device} err] } {
    puts "ERROR: Programming failed: $err"
    close_hw_target
    disconnect_hw_server
    close_hw_manager
    exit 1
}

# Verify programming (optional - refresh device state)
puts "Verifying..."
refresh_hw_device $device

# Clean up
puts "Closing connections..."
close_hw_target
disconnect_hw_server
close_hw_manager

puts "============================================================"
puts "FPGA Programming Completed Successfully!"
puts "============================================================"

exit 0
