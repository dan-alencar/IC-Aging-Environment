# ==============================================================================
# FPGA Programming Script for Vivado (JTAG & FLASH Support)
# ==============================================================================
# Usage: 
#   SRAM:  vivado -mode batch -source program_fpga.tcl -tclargs <file.bit>
#   FLASH: vivado -mode batch -source program_fpga.tcl -tclargs <file.bin> -flash
# ==============================================================================

# --- Configuration ---
set FLASH_PART "mt25qu01g-spi-x1_x2_x4"

# --- Argument Parsing ---
if { $argc < 1 } {
    puts "ERROR: File path not provided."
    exit 1
}

set file_path [lindex $argv 0]
set mode "sram"

if { $argc > 1 && [lindex $argv 1] == "-flash" } {
    set mode "flash"
}

# Verify file exists
if { ![file exists $file_path] } {
    puts "ERROR: File not found: $file_path"
    exit 1
}

puts "============================================================"
puts "FPGA Programming Script ($mode mode)"
puts "File: $file_path"
puts "============================================================"

# Open Hardware Manager
puts "Opening Hardware Manager..."
open_hw_manager

# Connect to Server
puts "Connecting to hardware server..."
# Try connecting allowing non-JTAG devices (sometimes needed for xvc/bridges)
if { [catch {connect_hw_server -url localhost:3121 -allow_non_jtag} err] } {
    if { [catch {connect_hw_server -url localhost:3121} err2] } {
        puts "ERROR: Failed to connect to hardware server: $err2"
        exit 1
    }
}

# Open Target
puts "Opening hardware target..."
if { [catch {open_hw_target} err] } {
    puts "ERROR: Failed to open hardware target: $err"
    exit 1
}

# Select Device
set devices [get_hw_devices]
if { [llength $devices] == 0 } {
    puts "ERROR: No FPGA devices found."
    exit 1
}
set device [lindex $devices 0]
current_hw_device $device
puts "Selected device: $device"

# Initial Refresh
refresh_hw_device -update_hw_probes false $device

if { $mode == "sram" } {
    # ==============================================================
    # SRAM Programming (Bitstream .bit)
    # ==============================================================
    puts "Configuring SRAM programming..."
    set_property PROGRAM.FILE $file_path $device
    
    puts "Programming FPGA (SRAM)..."
    if { [catch {program_hw_devices $device} err] } {
        puts "ERROR: Programming failed: $err"
        exit 1
    }

} else {
    # ==============================================================
    # FLASH Programming (Configuration Memory .bin)
    # ==============================================================
    puts "Configuring FLASH programming ($FLASH_PART)..."

    # 1. CLEANUP: Delete existing cfgmem object if it exists (Crucial fix!)
    set existing_mem [get_property PROGRAM.HW_CFGMEM $device]
    if { $existing_mem != "" } {
        puts "Cleaning up previous memory configuration..."
        delete_hw_cfgmem $existing_mem
    }

    # 2. Create configuration memory device (Explicit SPIx4 interface)
    puts "Creating configuration memory device..."
    create_hw_cfgmem -hw_device $device -interface SPIx4 -size 1024 [lindex [get_cfgmem_parts $FLASH_PART] 0]
    
    # Refresh to get the handle properly
    set mem_obj [get_property PROGRAM.HW_CFGMEM $device]

    if { $mem_obj == "" } {
        puts "ERROR: Failed to create hardware configuration memory object."
        exit 1
    }

    # 3. Configure Programming Properties
    set_property PROGRAM.BLANK_CHECK  0 $mem_obj
    set_property PROGRAM.ERASE        1 $mem_obj
    set_property PROGRAM.CFG_PROGRAM  1 $mem_obj
    set_property PROGRAM.VERIFY       1 $mem_obj
    set_property PROGRAM.CHECKSUM     0 $mem_obj
    
    # 4. Set the file
    set_property PROGRAM.ADDRESS_RANGE {use_file} $mem_obj
    set_property PROGRAM.FILES [list $file_path] $mem_obj
    set_property PROGRAM.PRM_FILE {} $mem_obj
    set_property PROGRAM.UNUSED_PIN_TERMINATION {pull-none} $mem_obj

    # 5. Refresh device before programming (Ensures indirect core is ready)
    puts "Refreshing device state..."
    refresh_hw_device $device

    # 6. Program Flash
    puts "Starting Flash Erase/Program/Verify cycle..."
    puts "This takes significantly longer than SRAM programming. Please wait."
    
    if { [catch {program_hw_cfgmem -hw_cfgmem $mem_obj} err] } {
        puts "ERROR: Flash programming failed: $err"
        exit 1
    }
}

# Cleanup
puts "Verifying state..."
refresh_hw_device $device
puts "Closing connections..."
close_hw_target
disconnect_hw_server
close_hw_manager

puts "============================================================"
puts "SUCCESS: Operation Complete."
puts "============================================================"
exit 0
