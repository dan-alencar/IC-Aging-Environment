# AMD Artix UltraScale+ Part Number: "xcau15p-ffvb676-1-i"

####################################################################################################
# SYSTEM CLOCK 100MHZ - BANK 64 - VOLTAGE 1.2V
####################################################################################################
set_property PACKAGE_PIN AD20 [get_ports sys_clk_p]
set_property PACKAGE_PIN AE20 [get_ports sys_clk_n]
set_property IOSTANDARD DIFF_SSTL12 [get_ports sys_clk_n]
set_property IOSTANDARD DIFF_SSTL12 [get_ports sys_clk_p]
create_clock -period 10.000 -name sys_clk -waveform {0.000 5.000} [get_ports sys_clk_p]

####################################################################################################
# BANK 84 (High Density) - VOLTAGE 3.3V
####################################################################################################
# UART 1 (Original)
set_property PACKAGE_PIN W12 [get_ports mcu_usart1_rx]
set_property PACKAGE_PIN AB16 [get_ports mcu_usart1_tx]
set_property IOSTANDARD LVCMOS33 [get_ports mcu_usart1_rx]
set_property IOSTANDARD LVCMOS33 [get_ports mcu_usart1_tx]

# Status LED (Assuming AF14 is in Bank 84)
set_property PACKAGE_PIN AF14 [get_ports status_o]
set_property IOSTANDARD LVCMOS33 [get_ports status_o]

####################################################################################################
# BANK 65 (High Performance) - VOLTAGE 1.2V
####################################################################################################
# UART 2 (Mirror) - 1.2V (Going to Level Shifter)
set_property PACKAGE_PIN Y26 [get_ports mcu_usart2_rx]
set_property IOSTANDARD LVCMOS12 [get_ports mcu_usart2_rx]

# FPGA Button - 1.2V (Must match Bank 65 VCCO)
set_property PACKAGE_PIN R26 [get_ports fpga_button]
set_property IOSTANDARD LVCMOS12 [get_ports fpga_button]

####################################################################################################
# CONFIGURATION & OVERRIDES
####################################################################################################
# Allow manual button to drive global clock buffer (Manual Override)
set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets fpga_button_IBUF_inst/O]

set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]
set_property CONFIG_MODE SPIx4 [current_design]
set_property BITSTREAM.CONFIG.CONFIGRATE 31.9 [current_design]

#create_pblock pblock_left_exclude
#resize_pblock [get_pblocks pblock_left_exclude] -add {SLICE_X0Y0:SLICE_X33Y179 \
#                                                      DSP48E2_X0Y0:DSP48E2_X3Y71 \
#                                                      IOB_X0Y155:IOB_X1Y0 \
#                                                      RAMB18_X0Y0:RAMB18_X1Y71 \
#                                                      RAMB36_X0Y0:RAMB36_X1Y35 \
#}
#set_property EXCLUDE_PLACEMENT 1 [get_pblocks pblock_left_exclude]
#set_property IS_SOFT FALSE [get_pblocks pblock_left_exclude]

#create_pblock pblock_north_exclude
#resize_pblock [get_pblocks pblock_north_exclude] -add {CLOCKREGION_X0Y1:CLOCKREGION_X1Y2}
#set_property EXCLUDE_PLACEMENT 1 [get_pblocks pblock_north_exclude]
#set_property IS_SOFT FALSE [get_pblocks pblock_north_exclude]

#set_property C_CLK_INPUT_FREQ_HZ 300000000 [get_debug_cores dbg_hub]
#set_property C_ENABLE_CLK_DIVIDER false [get_debug_cores dbg_hub]
#set_property C_USER_SCAN_CHAIN 1 [get_debug_cores dbg_hub]
#connect_debug_port dbg_hub/clk [get_nets soc_clk]

#create_pblock pblock_force_exclude
#resize_pblock [get_pblocks pblock_force_exclude] -add {SLICE_X0Y0:SLICE_X16Y59 SLICE_X0Y60:SLICE_X53Y119 SLICE_X0Y120:SLICE_X19Y179 \
#                                                       BUFG_GT_X0Y24:BUFG_GT_X0Y47 \
#                                                       BUFG_GT_SYNC_X0Y15:BUFG_GT_SYNC_X0Y29 \
#                                                       CONFIG_SITE_X0Y0:CONFIG_SITE_X0Y0 \
#                                                       DSP48E2_X0Y0:DSP48E2_X0Y71 DSP48E2_X1Y24:DSP48E2_X7Y47 \
#                                                       GTHE4_CHANNEL_X0Y4:GTHE4_CHANNEL_X0Y7 \
#                                                       GTHE4_COMMON_X0Y1:GTHE4_COMMON_X0Y1 \
#                                                       IOB_X0Y104:IOB_X0Y155 IOB_X1Y52:IOB_X1Y141 \
#                                                       RAMB18_X0Y0:RAMB18_X0Y71 RAMB18_X1Y24:RAMB18_X3Y47 \
#                                                       RAMB36_X0Y0:RAMB36_X0Y35 RAMB36_X1Y12:RAMB36_X3Y23 \
#}
#set_property EXCLUDE_PLACEMENT 1 [get_pblocks pblock_force_exclude]
#set_property IS_SOFT FALSE [get_pblocks pblock_force_exclude]
