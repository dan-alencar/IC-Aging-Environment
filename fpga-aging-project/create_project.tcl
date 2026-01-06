##################################################################
# FPGA Aging Project - Master Project Creation Script
##################################################################
# This script creates a complete Vivado project for the FPGA aging
# study using the CROC RISC-V SoC design.
#
# Usage: 
#   1. Navigate to the fpga-aging-project directory
#   2. Run: vivado -mode batch -source create_project.tcl
#      OR open Vivado and source this script from the Tcl console
##################################################################

puts "=========================================="
puts "Starting FPGA Aging Project Creation"
puts "=========================================="

##################################################################
# STEP 1: Define Paths and Project Settings
##################################################################

# Get the current working directory (should be fpga-aging-project)
set script_dir [file dirname [file normalize [info script]]]
puts "Script directory: $script_dir"

# Define the ROOT variable pointing to croc-main
set ROOT [file normalize $script_dir/sources/croc-main]
puts "ROOT directory: $ROOT"

# Project settings
set project_name "fpga_aging_build"
set project_dir [file normalize $script_dir/$project_name]
set target_part "xcau15p-ffvb676-1-i"

puts "Project will be created at: $project_dir"

##################################################################
# STEP 2: Create the Project
##################################################################

puts "\n=========================================="
puts "Creating Vivado Project"
puts "=========================================="

# Create project with force option to overwrite if exists
create_project $project_name $project_dir -part $target_part -force

puts "Project created successfully"

##################################################################
# STEP 3: Add All RTL Source Files
##################################################################

puts "\n=========================================="
puts "Adding RTL Source Files"
puts "=========================================="

# Technology-specific cells
add_files -norecurse -fileset [current_fileset] [list \
    $ROOT/rtl/tech_cells_generic/fpga/pad_functional_xilinx.sv \
    $ROOT/rtl/tech_cells_generic/fpga/tc_clk_xilinx.sv \
    $ROOT/rtl/tech_cells_generic/fpga/tc_sram_xilinx.sv \
    $ROOT/rtl/tech_cells_generic/tc_sram_impl.sv \
]

# Common cells - binary_to_gray
add_files -norecurse -fileset [current_fileset] [list \
    $ROOT/rtl/common_cells/binary_to_gray.sv \
]

# Common cells - main library
add_files -norecurse -fileset [current_fileset] [list \
    $ROOT/rtl/common_cells/cb_filter_pkg.sv \
    $ROOT/rtl/common_cells/cc_onehot.sv \
    $ROOT/rtl/common_cells/cdc_reset_ctrlr_pkg.sv \
    $ROOT/rtl/common_cells/cf_math_pkg.sv \
    $ROOT/rtl/common_cells/clk_int_div.sv \
    $ROOT/rtl/common_cells/credit_counter.sv \
    $ROOT/rtl/common_cells/delta_counter.sv \
    $ROOT/rtl/common_cells/ecc_pkg.sv \
    $ROOT/rtl/common_cells/edge_propagator_tx.sv \
    $ROOT/rtl/common_cells/exp_backoff.sv \
    $ROOT/rtl/common_cells/fifo_v3.sv \
    $ROOT/rtl/common_cells/gray_to_binary.sv \
    $ROOT/rtl/common_cells/isochronous_4phase_handshake.sv \
    $ROOT/rtl/common_cells/isochronous_spill_register.sv \
    $ROOT/rtl/common_cells/lfsr.sv \
    $ROOT/rtl/common_cells/lfsr_16bit.sv \
    $ROOT/rtl/common_cells/lfsr_8bit.sv \
    $ROOT/rtl/common_cells/lossy_valid_to_stream.sv \
    $ROOT/rtl/common_cells/mv_filter.sv \
    $ROOT/rtl/common_cells/onehot_to_bin.sv \
    $ROOT/rtl/common_cells/plru_tree.sv \
    $ROOT/rtl/common_cells/passthrough_stream_fifo.sv \
    $ROOT/rtl/common_cells/popcount.sv \
    $ROOT/rtl/common_cells/rr_arb_tree.sv \
    $ROOT/rtl/common_cells/rstgen_bypass.sv \
    $ROOT/rtl/common_cells/serial_deglitch.sv \
    $ROOT/rtl/common_cells/shift_reg.sv \
    $ROOT/rtl/common_cells/shift_reg_gated.sv \
    $ROOT/rtl/common_cells/spill_register_flushable.sv \
    $ROOT/rtl/common_cells/stream_demux.sv \
    $ROOT/rtl/common_cells/stream_filter.sv \
    $ROOT/rtl/common_cells/stream_fork.sv \
    $ROOT/rtl/common_cells/stream_intf.sv \
    $ROOT/rtl/common_cells/stream_join_dynamic.sv \
    $ROOT/rtl/common_cells/stream_mux.sv \
    $ROOT/rtl/common_cells/stream_throttle.sv \
    $ROOT/rtl/common_cells/sub_per_hash.sv \
    $ROOT/rtl/common_cells/sync.sv \
    $ROOT/rtl/common_cells/sync_wedge.sv \
    $ROOT/rtl/common_cells/unread.sv \
    $ROOT/rtl/common_cells/read.sv \
    $ROOT/rtl/common_cells/addr_decode_dync.sv \
    $ROOT/rtl/common_cells/cdc_2phase.sv \
    $ROOT/rtl/common_cells/cdc_4phase.sv \
    $ROOT/rtl/common_cells/clk_int_div_static.sv \
    $ROOT/rtl/common_cells/addr_decode.sv \
    $ROOT/rtl/common_cells/addr_decode_napot.sv \
    $ROOT/rtl/common_cells/multiaddr_decode.sv \
]

# Common cells - complex modules
add_files -norecurse -fileset [current_fileset] [list \
    $ROOT/rtl/common_cells/cb_filter.sv \
    $ROOT/rtl/common_cells/cdc_fifo_2phase.sv \
    $ROOT/rtl/common_cells/clk_mux_glitch_free.sv \
    $ROOT/rtl/common_cells/counter.sv \
    $ROOT/rtl/common_cells/ecc_decode.sv \
    $ROOT/rtl/common_cells/ecc_encode.sv \
    $ROOT/rtl/common_cells/edge_detect.sv \
    $ROOT/rtl/common_cells/lzc.sv \
    $ROOT/rtl/common_cells/max_counter.sv \
    $ROOT/rtl/common_cells/rstgen.sv \
    $ROOT/rtl/common_cells/spill_register.sv \
    $ROOT/rtl/common_cells/stream_delay.sv \
    $ROOT/rtl/common_cells/stream_fifo.sv \
    $ROOT/rtl/common_cells/stream_fork_dynamic.sv \
    $ROOT/rtl/common_cells/stream_join.sv \
    $ROOT/rtl/common_cells/cdc_reset_ctrlr.sv \
    $ROOT/rtl/common_cells/cdc_fifo_gray.sv \
    $ROOT/rtl/common_cells/fall_through_register.sv \
    $ROOT/rtl/common_cells/id_queue.sv \
    $ROOT/rtl/common_cells/stream_to_mem.sv \
    $ROOT/rtl/common_cells/stream_arbiter_flushable.sv \
    $ROOT/rtl/common_cells/stream_fifo_optimal_wrap.sv \
    $ROOT/rtl/common_cells/stream_register.sv \
    $ROOT/rtl/common_cells/stream_xbar.sv \
    $ROOT/rtl/common_cells/cdc_fifo_gray_clearable.sv \
    $ROOT/rtl/common_cells/cdc_2phase_clearable.sv \
    $ROOT/rtl/common_cells/mem_to_banks_detailed.sv \
    $ROOT/rtl/common_cells/stream_arbiter.sv \
    $ROOT/rtl/common_cells/stream_omega_net.sv \
    $ROOT/rtl/common_cells/mem_to_banks.sv \
]

# APB package
add_files -norecurse -fileset [current_fileset] [list \
    $ROOT/rtl/apb/apb_pkg.sv \
]

# Register interface
add_files -norecurse -fileset [current_fileset] [list \
    $ROOT/rtl/register_interface/reg_intf.sv \
    $ROOT/rtl/register_interface/lowrisc_opentitan/prim_subreg_arb.sv \
    $ROOT/rtl/register_interface/lowrisc_opentitan/prim_subreg_ext.sv \
    $ROOT/rtl/register_interface/periph_to_reg.sv \
    $ROOT/rtl/register_interface/reg_to_apb.sv \
    $ROOT/rtl/register_interface/lowrisc_opentitan/prim_subreg_shadow.sv \
    $ROOT/rtl/register_interface/lowrisc_opentitan/prim_subreg.sv \
]

# APB UART
add_files -norecurse -fileset [current_fileset] [list \
    $ROOT/rtl/apb_uart/slib_clock_div.sv \
    $ROOT/rtl/apb_uart/slib_counter.sv \
    $ROOT/rtl/apb_uart/slib_edge_detect.sv \
    $ROOT/rtl/apb_uart/slib_fifo.sv \
    $ROOT/rtl/apb_uart/slib_input_filter.sv \
    $ROOT/rtl/apb_uart/slib_input_sync.sv \
    $ROOT/rtl/apb_uart/slib_mv_filter.sv \
    $ROOT/rtl/apb_uart/uart_baudgen.sv \
    $ROOT/rtl/apb_uart/uart_interrupt.sv \
    $ROOT/rtl/apb_uart/uart_receiver.sv \
    $ROOT/rtl/apb_uart/uart_transmitter.sv \
    $ROOT/rtl/apb_uart/apb_uart.sv \
    $ROOT/rtl/apb_uart/apb_uart_wrap.sv \
    $ROOT/rtl/apb_uart/reg_uart_wrap.sv \
]

# CVE2 RISC-V Core
add_files -norecurse -fileset [current_fileset] [list \
    $ROOT/rtl/cve2/cve2_pkg.sv \
    $ROOT/rtl/cve2/cve2_alu.sv \
    $ROOT/rtl/cve2/cve2_compressed_decoder.sv \
    $ROOT/rtl/cve2/cve2_controller.sv \
    $ROOT/rtl/cve2/cve2_counter.sv \
    $ROOT/rtl/cve2/cve2_csr.sv \
    $ROOT/rtl/cve2/cve2_decoder.sv \
    $ROOT/rtl/cve2/cve2_fetch_fifo.sv \
    $ROOT/rtl/cve2/cve2_load_store_unit.sv \
    $ROOT/rtl/cve2/cve2_multdiv_fast.sv \
    $ROOT/rtl/cve2/cve2_multdiv_slow.sv \
    $ROOT/rtl/cve2/cve2_pmp.sv \
    $ROOT/rtl/cve2/cve2_register_file_ff.sv \
    $ROOT/rtl/cve2/cve2_wb.sv \
    $ROOT/rtl/cve2/cve2_cs_registers.sv \
    $ROOT/rtl/cve2/cve2_ex_block.sv \
    $ROOT/rtl/cve2/cve2_id_stage.sv \
    $ROOT/rtl/cve2/cve2_prefetch_buffer.sv \
    $ROOT/rtl/cve2/cve2_if_stage.sv \
    $ROOT/rtl/cve2/cve2_core.sv \
]

# OBI (Open Bus Interface)
add_files -norecurse -fileset [current_fileset] [list \
    $ROOT/rtl/obi/obi_pkg.sv \
    $ROOT/rtl/obi/obi_intf.sv \
    $ROOT/rtl/obi/obi_rready_converter.sv \
    $ROOT/rtl/obi/obi_atop_resolver.sv \
    $ROOT/rtl/obi/obi_cut.sv \
    $ROOT/rtl/obi/obi_demux.sv \
    $ROOT/rtl/obi/obi_err_sbr.sv \
    $ROOT/rtl/obi/obi_mux.sv \
    $ROOT/rtl/obi/obi_sram_shim.sv \
    $ROOT/rtl/obi/obi_xbar.sv \
]

# RISC-V Debug Module
add_files -norecurse -fileset [current_fileset] [list \
    $ROOT/rtl/riscv-dbg/dm_pkg.sv \
    $ROOT/rtl/riscv-dbg/debug_rom/debug_rom.sv \
    $ROOT/rtl/riscv-dbg/debug_rom/debug_rom_one_scratch.sv \
    $ROOT/rtl/riscv-dbg/dm_csrs.sv \
    $ROOT/rtl/riscv-dbg/dm_mem.sv \
    $ROOT/rtl/riscv-dbg/dmi_cdc.sv \
]

add_files -norecurse -fileset [current_fileset] [list \
    $ROOT/rtl/riscv-dbg/dmi_jtag_tap.sv \
]

add_files -norecurse -fileset [current_fileset] [list \
    $ROOT/rtl/riscv-dbg/dm_sba.sv \
    $ROOT/rtl/riscv-dbg/dm_top.sv \
    $ROOT/rtl/riscv-dbg/dmi_jtag.sv \
    $ROOT/rtl/riscv-dbg/dm_obi_top.sv \
]

# Timer Unit
add_files -norecurse -fileset [current_fileset] [list \
    $ROOT/rtl/timer_unit/timer_unit_counter.sv \
    $ROOT/rtl/timer_unit/timer_unit_counter_presc.sv \
    $ROOT/rtl/timer_unit/apb_timer_unit.sv \
    $ROOT/rtl/timer_unit/timer_unit.sv \
]

# CROC SoC packages and top-level modules
add_files -norecurse -fileset [current_fileset] [list \
    $ROOT/rtl/croc_pkg.sv \
    $ROOT/rtl/user_pkg.sv \
    $ROOT/rtl/soc_ctrl/soc_ctrl_reg_pkg.sv \
    $ROOT/rtl/gpio/gpio_reg_pkg.sv \
]

add_files -norecurse -fileset [current_fileset] [list \
    $ROOT/rtl/core_wrap.sv \
    $ROOT/rtl/soc_ctrl/soc_ctrl_reg_top.sv \
    $ROOT/rtl/gpio/gpio_reg_top.sv \
    $ROOT/rtl/gpio/gpio.sv \
    $ROOT/rtl/croc_domain.sv \
    $ROOT/rtl/user_domain.sv \
    $ROOT/rtl/croc_soc.sv \
]

# Xilinx top-level wrapper
add_files -norecurse -fileset [current_fileset] [list \
    $ROOT/xilinx/hw/croc_xilinx_aging.sv \
]

puts "RTL source files added successfully"

##################################################################
# STEP 4: Set Include Directories
##################################################################

puts "\n=========================================="
puts "Setting Include Directories"
puts "=========================================="

set include_dirs [list \
    $ROOT/rtl/apb/include \
    $ROOT/rtl/common_cells/include \
    $ROOT/rtl/cve2/include \
    $ROOT/rtl/obi/include \
    $ROOT/rtl/register_interface/include \
]

set_property include_dirs $include_dirs [current_fileset]
set_property include_dirs $include_dirs [current_fileset -simset]

puts "Include directories set successfully"

##################################################################
# STEP 5: Set Verilog Defines
##################################################################

puts "\n=========================================="
puts "Setting Verilog Defines"
puts "=========================================="

set synthesis_defines [list \
    TARGET_FPGA \
    TARGET_AUP15 \
    TARGET_RTL \
    TARGET_SYNTHESIS \
    TARGET_VIVADO \
    TARGET_XILINX \
    COMMON_CELLS_ASSERTS_OFF \
]

set simulation_defines [list \
    TARGET_FPGA \
    TARGET_AUP15 \
    TARGET_RTL \
    TARGET_SYNTHESIS \
    TARGET_VIVADO \
    TARGET_XILINX \
]

set_property verilog_define $synthesis_defines [current_fileset]
set_property verilog_define $simulation_defines [current_fileset -simset]

puts "Verilog defines set successfully"

##################################################################
# STEP 6: Set XPM Libraries
##################################################################

puts "\n=========================================="
puts "Setting XPM Libraries"
puts "=========================================="

set_property XPM_LIBRARIES XPM_MEMORY [current_project]

puts "XPM libraries configured"

##################################################################
# STEP 7: Add Constraints File
##################################################################

puts "\n=========================================="
puts "Adding Constraints File"
puts "=========================================="

set constraints_file [file normalize $script_dir/sources/constraints/fpga_aging_constraints.xdc]
add_files -fileset constrs_1 -norecurse $constraints_file

puts "Constraints file added: $constraints_file"

##################################################################
# STEP 8: Add Memory Initialization File
##################################################################

puts "\n=========================================="
puts "Adding Memory Initialization File"
puts "=========================================="

set mem_file [file normalize $script_dir/sources/croc-main/sw/bin/helloworld.mem]
add_files -norecurse $mem_file

puts "Memory file added: $mem_file"
puts "Note: You may need to manually assign this file to the appropriate memory instance"

##################################################################
# STEP 9: Create and Configure Clock Wizard IP
##################################################################

puts "\n=========================================="
puts "Creating Clock Wizard IP"
puts "=========================================="

set clk_wiz [create_ip -name clk_wiz -vendor xilinx.com -library ip -version 6.0 -module_name clk_wiz]

set_property -dict [list \
  CONFIG.CLKIN1_JITTER_PS {33.330000000000005} \
  CONFIG.CLKOUT1_JITTER {288.226} \
  CONFIG.CLKOUT1_PHASE_ERROR {297.237} \
  CONFIG.CLKOUT1_REQUESTED_OUT_FREQ {20.000} \
  CONFIG.MMCM_CLKFBOUT_MULT_F {52.375} \
  CONFIG.MMCM_CLKIN1_PERIOD {3.333} \
  CONFIG.MMCM_CLKIN2_PERIOD {10.0} \
  CONFIG.MMCM_CLKOUT0_DIVIDE_F {52.375} \
  CONFIG.MMCM_DIVCLK_DIVIDE {15} \
  CONFIG.PRIM_IN_FREQ {100.000} \
] [get_ips clk_wiz]

set_property -dict { 
  GENERATE_SYNTH_CHECKPOINT {1}
} $clk_wiz

puts "Clock Wizard IP created and configured"

##################################################################
# STEP 10: Create and Configure VIO IP
##################################################################

puts "\n=========================================="
puts "Creating VIO IP"
puts "=========================================="

set vio_0 [create_ip -name vio -vendor xilinx.com -library ip -version 3.0 -module_name vio_0]

set_property -dict [list \
  CONFIG.C_NUM_PROBE_IN {5} \
  CONFIG.C_NUM_PROBE_OUT {7} \
  CONFIG.C_PROBE_OUT0_INIT_VAL {0x1} \
  CONFIG.C_PROBE_OUT1_INIT_VAL {0x1} \
] [get_ips vio_0]

set_property -dict { 
  GENERATE_SYNTH_CHECKPOINT {1}
} $vio_0

puts "VIO IP created and configured"

##################################################################
# STEP 11: Generate IP Outputs
##################################################################

puts "\n=========================================="
puts "Generating IP Outputs"
puts "=========================================="

generate_target all [get_ips]

puts "IP generation complete"

##################################################################
# STEP 12: Set Top Module and Update Compile Order
##################################################################

puts "\n=========================================="
puts "Setting Top Module and Updating Compile Order"
puts "=========================================="

set_property top croc_xilinx_aging [current_fileset]
update_compile_order -fileset sources_1
update_compile_order -fileset sim_1

puts "Top module set to: croc_xilinx_aging"
puts "Compile order updated"

##################################################################
# COMPLETION
##################################################################

puts "\n=========================================="
puts "Project Creation Complete!"
puts "=========================================="
puts "Project Name: $project_name"
puts "Project Location: $project_dir"
puts "Target Part: $target_part"
puts "Top Module: croc_xilinx_aging"
puts ""
puts "Next steps:"
puts "  1. Open the project in Vivado GUI"
puts "  2. Review the design hierarchy"
puts "  3. Run synthesis and implementation"
puts "=========================================="
