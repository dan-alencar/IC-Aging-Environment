# AMD Artix UltraScale+ Aging Sensor Constraints
# Part Number: xcau15p-ffvb676-1-i
####################################################################################################################################################################################

####################################################################################################################################################################################
# SYSTEM CLOCK 100MHZ - BANK 64 - VOLTAGE 1.2V VCCO_64_65
####################################################################################################################################################################################
set_property PACKAGE_PIN AD20 [get_ports sys_clk_p]
set_property PACKAGE_PIN AE20 [get_ports sys_clk_n]
set_property IOSTANDARD DIFF_SSTL12 [get_ports sys_clk_n]
set_property IOSTANDARD DIFF_SSTL12 [get_ports sys_clk_p]

# Differential clock constraint
create_clock -period 10.000 -name sys_clk_in -waveform {0.000 5.000} [get_ports sys_clk_p]

####################################################################################################################################################################################
# UART - BANK 84 - VOLTAGE 1.2V (check your board schematic for correct voltage)
####################################################################################################################################################################################
set_property PACKAGE_PIN W26 [get_ports rx]
set_property PACKAGE_PIN Y26 [get_ports tx]
set_property IOSTANDARD LVCMOS12 [get_ports rx]
set_property IOSTANDARD LVCMOS12 [get_ports tx]

####################################################################################################################################################################################
# RESET BUTTON - Active-low with pull-up (typical configuration)
####################################################################################################################################################################################
# Button pin assignment
# set_property PACKAGE_PIN R26 [get_ports fpga_button]
# set_property IOSTANDARD LVCMOS12 [get_ports fpga_button]
# set_property PULLUP true [get_ports fpga_button]

# Optional: If your button is active-high instead, comment out the PULLUP above
# and uncomment the PULLDOWN below:
# set_property PULLDOWN true [get_ports fpga_button]

####################################################################################################################################################################################
# BITSTREAM CONFIGURATION
####################################################################################################################################################################################
set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]
set_property CONFIG_MODE SPIx4 [current_design]
set_property BITSTREAM.CONFIG.CONFIGRATE 31.9 [current_design]

####################################################################################################################################################################################
# PLACEMENT CONSTRAINTS FOR AGING SENSOR (not_series module)
####################################################################################################################################################################################
# Prevent optimization of critical path inverters
set_property DONT_TOUCH true [get_cells critical_path/genblk1[*].INV]

# Aging sensor placement
set_property BEL EFF [get_cells aging_sensor/FF1]
set_property BEL DFF2 [get_cells aging_sensor/FF3]
set_property BEL D5LUT [get_cells aging_sensor/XOR1]
set_property BEL CFF2 [get_cells aging_sensor/FF2]
set_property LOC SLICE_X40Y157 [get_cells aging_sensor/FF1]
set_property LOC SLICE_X41Y156 [get_cells aging_sensor/FF3]
set_property LOC SLICE_X41Y156 [get_cells aging_sensor/XOR1]
set_property LOC SLICE_X41Y157 [get_cells aging_sensor/FF2]

# Critical path inverter chain placement
set_property BEL B6LUT [get_cells {critical_path/genblk1[19].INV}]
set_property BEL F6LUT [get_cells {critical_path/genblk1[2].INV}]
set_property BEL H6LUT [get_cells {critical_path/genblk1[0].INV}]
set_property BEL A6LUT [get_cells {critical_path/genblk1[20].INV}]
set_property BEL E6LUT [get_cells {critical_path/genblk1[22].INV}]
set_property BEL H6LUT [get_cells {critical_path/genblk1[4].INV}]
set_property BEL E6LUT [get_cells {critical_path/genblk1[6].INV}]
set_property BEL H6LUT [get_cells {critical_path/genblk1[39].INV}]
set_property BEL G6LUT [get_cells {critical_path/genblk1[40].INV}]
set_property BEL E5LUT [get_cells {critical_path/genblk1[42].INV}]
set_property BEL E6LUT [get_cells {critical_path/genblk1[44].INV}]
set_property BEL E6LUT [get_cells {critical_path/genblk1[31].INV}]
set_property BEL F6LUT [get_cells {critical_path/genblk1[33].INV}]
set_property BEL B6LUT [get_cells {critical_path/genblk1[35].INV}]
set_property BEL B6LUT [get_cells {critical_path/genblk1[37].INV}]
set_property BEL A6LUT [get_cells {critical_path/genblk1[24].INV}]
set_property BEL D6LUT [get_cells {critical_path/genblk1[26].INV}]
set_property BEL H6LUT [get_cells {critical_path/genblk1[28].INV}]
set_property BEL B6LUT [get_cells {critical_path/genblk1[8].INV}]
set_property BEL A5LUT [get_cells {critical_path/genblk1[46].INV}]
set_property BEL H6LUT [get_cells {critical_path/genblk1[48].INV}]
set_property BEL G6LUT [get_cells {critical_path/genblk1[11].INV}]
set_property BEL H6LUT [get_cells {critical_path/genblk1[12].INV}]
set_property BEL F6LUT [get_cells {critical_path/genblk1[15].INV}]
set_property BEL E6LUT [get_cells {critical_path/genblk1[17].INV}]
set_property BEL G6LUT [get_cells {critical_path/genblk1[1].INV}]
set_property BEL F5LUT [get_cells {critical_path/genblk1[3].INV}]
set_property BEL D6LUT [get_cells {critical_path/genblk1[21].INV}]
set_property BEL C5LUT [get_cells {critical_path/genblk1[23].INV}]
set_property BEL C6LUT [get_cells {critical_path/genblk1[18].INV}]
set_property BEL G6LUT [get_cells {critical_path/genblk1[29].INV}]
set_property BEL F6LUT [get_cells {critical_path/genblk1[30].INV}]
set_property BEL F6LUT [get_cells {critical_path/genblk1[25].INV}]
set_property BEL E6LUT [get_cells {critical_path/genblk1[36].INV}]
set_property BEL A6LUT [get_cells {critical_path/genblk1[38].INV}]
set_property BEL E6LUT [get_cells {critical_path/genblk1[32].INV}]
set_property BEL H5LUT [get_cells {critical_path/genblk1[45].INV}]
set_property BEL F6LUT [get_cells {critical_path/genblk1[41].INV}]
set_property BEL D6LUT [get_cells {critical_path/genblk1[43].INV}]
set_property BEL H6LUT [get_cells {critical_path/genblk1[34].INV}]
set_property BEL C6LUT [get_cells {critical_path/genblk1[27].INV}]
set_property BEL G6LUT [get_cells {critical_path/genblk1[5].INV}]
set_property BEL F6LUT [get_cells {critical_path/genblk1[7].INV}]
set_property BEL B5LUT [get_cells {critical_path/genblk1[9].INV}]
set_property BEL G5LUT [get_cells {critical_path/genblk1[47].INV}]
set_property BEL E6LUT [get_cells {critical_path/genblk1[49].INV}]
set_property BEL H6LUT [get_cells {critical_path/genblk1[10].INV}]
set_property BEL G6LUT [get_cells {critical_path/genblk1[13].INV}]
set_property BEL F6LUT [get_cells {critical_path/genblk1[14].INV}]
set_property BEL F6LUT [get_cells {critical_path/genblk1[16].INV}]

set_property LOC SLICE_X40Y157 [get_cells {critical_path/genblk1[19].INV}]
set_property LOC SLICE_X41Y158 [get_cells {critical_path/genblk1[2].INV}]
set_property LOC SLICE_X41Y158 [get_cells {critical_path/genblk1[0].INV}]
set_property LOC SLICE_X40Y157 [get_cells {critical_path/genblk1[20].INV}]
set_property LOC SLICE_X41Y157 [get_cells {critical_path/genblk1[22].INV}]
set_property LOC SLICE_X41Y156 [get_cells {critical_path/genblk1[4].INV}]
set_property LOC SLICE_X41Y156 [get_cells {critical_path/genblk1[6].INV}]
set_property LOC SLICE_X41Y159 [get_cells {critical_path/genblk1[39].INV}]
set_property LOC SLICE_X41Y159 [get_cells {critical_path/genblk1[40].INV}]
set_property LOC SLICE_X41Y158 [get_cells {critical_path/genblk1[42].INV}]
set_property LOC SLICE_X40Y156 [get_cells {critical_path/genblk1[44].INV}]
set_property LOC SLICE_X42Y157 [get_cells {critical_path/genblk1[31].INV}]
set_property LOC SLICE_X42Y158 [get_cells {critical_path/genblk1[33].INV}]
set_property LOC SLICE_X41Y158 [get_cells {critical_path/genblk1[35].INV}]
set_property LOC SLICE_X41Y159 [get_cells {critical_path/genblk1[37].INV}]
set_property LOC SLICE_X41Y158 [get_cells {critical_path/genblk1[24].INV}]
set_property LOC SLICE_X41Y157 [get_cells {critical_path/genblk1[26].INV}]
set_property LOC SLICE_X42Y157 [get_cells {critical_path/genblk1[28].INV}]
set_property LOC SLICE_X41Y157 [get_cells {critical_path/genblk1[8].INV}]
set_property LOC SLICE_X40Y157 [get_cells {critical_path/genblk1[46].INV}]
set_property LOC SLICE_X39Y157 [get_cells {critical_path/genblk1[48].INV}]
set_property LOC SLICE_X40Y157 [get_cells {critical_path/genblk1[11].INV}]
set_property LOC SLICE_X40Y156 [get_cells {critical_path/genblk1[12].INV}]
set_property LOC SLICE_X40Y157 [get_cells {critical_path/genblk1[15].INV}]
set_property LOC SLICE_X39Y157 [get_cells {critical_path/genblk1[17].INV}]
set_property LOC SLICE_X41Y158 [get_cells {critical_path/genblk1[1].INV}]
set_property LOC SLICE_X41Y158 [get_cells {critical_path/genblk1[3].INV}]
set_property LOC SLICE_X40Y157 [get_cells {critical_path/genblk1[21].INV}]
set_property LOC SLICE_X41Y157 [get_cells {critical_path/genblk1[23].INV}]
set_property LOC SLICE_X40Y157 [get_cells {critical_path/genblk1[18].INV}]
set_property LOC SLICE_X42Y157 [get_cells {critical_path/genblk1[29].INV}]
set_property LOC SLICE_X42Y157 [get_cells {critical_path/genblk1[30].INV}]
set_property LOC SLICE_X41Y157 [get_cells {critical_path/genblk1[25].INV}]
set_property LOC SLICE_X41Y158 [get_cells {critical_path/genblk1[36].INV}]
set_property LOC SLICE_X41Y159 [get_cells {critical_path/genblk1[38].INV}]
set_property LOC SLICE_X42Y158 [get_cells {critical_path/genblk1[32].INV}]
set_property LOC SLICE_X40Y156 [get_cells {critical_path/genblk1[45].INV}]
set_property LOC SLICE_X41Y159 [get_cells {critical_path/genblk1[41].INV}]
set_property LOC SLICE_X41Y156 [get_cells {critical_path/genblk1[43].INV}]
set_property LOC SLICE_X42Y158 [get_cells {critical_path/genblk1[34].INV}]
set_property LOC SLICE_X41Y157 [get_cells {critical_path/genblk1[27].INV}]
set_property LOC SLICE_X41Y156 [get_cells {critical_path/genblk1[5].INV}]
set_property LOC SLICE_X41Y156 [get_cells {critical_path/genblk1[7].INV}]
set_property LOC SLICE_X41Y157 [get_cells {critical_path/genblk1[9].INV}]
set_property LOC SLICE_X40Y157 [get_cells {critical_path/genblk1[47].INV}]
set_property LOC SLICE_X40Y157 [get_cells {critical_path/genblk1[49].INV}]
set_property LOC SLICE_X40Y157 [get_cells {critical_path/genblk1[10].INV}]
set_property LOC SLICE_X40Y156 [get_cells {critical_path/genblk1[13].INV}]
set_property LOC SLICE_X40Y156 [get_cells {critical_path/genblk1[14].INV}]
set_property LOC SLICE_X39Y157 [get_cells {critical_path/genblk1[16].INV}]

####################################################################################################################################################################################
# DEBUG HUB CONSTRAINTS
####################################################################################################################################################################################
set_property C_CLK_INPUT_FREQ_HZ 100000000 [get_debug_cores dbg_hub]
set_property C_ENABLE_CLK_DIVIDER false [get_debug_cores dbg_hub]
set_property C_USER_SCAN_CHAIN 1 [get_debug_cores dbg_hub]
connect_debug_port dbg_hub/clk [get_nets sys_clk_in]

####################################################################################################################################################################################
# TIMING CONSTRAINTS
####################################################################################################################################################################################
# False paths for asynchronous resets
set_false_path -from [get_ports fpga_button] -to [all_registers]

# Clock domain crossings (if needed)
# set_false_path -from [get_clocks phase_clk] -to [get_clocks sys_clk]