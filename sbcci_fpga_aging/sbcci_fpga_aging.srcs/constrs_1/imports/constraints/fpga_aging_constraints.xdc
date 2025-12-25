# AMD Artix UltraScale+ Part Number: "xcau15p-ffvb676-1-i"

# ==============================================================================
# 1. SYSTEM CLOCK (Bank 64 - 1.2V)
# ==============================================================================
set_property PACKAGE_PIN AD20 [get_ports sys_clk_p]
set_property PACKAGE_PIN AE20 [get_ports sys_clk_n]
set_property IOSTANDARD DIFF_SSTL12 [get_ports sys_clk_p]
set_property IOSTANDARD DIFF_SSTL12 [get_ports sys_clk_n]

#create_clock -period 10.000 -name clk_sys -waveform {0.000 5.000} [get_ports sys_clk_p]

# ==============================================================================
# 2. PC INTERFACE & CONTROL (Bank 65 - 1.2V)
# ==============================================================================
# UART connected to USB-UART Bridge (PC)
set_property PACKAGE_PIN Y26 [get_ports fpga_uart_tx]
set_property IOSTANDARD LVCMOS12 [get_ports fpga_uart_tx]

set_property PACKAGE_PIN W26 [get_ports fpga_uart_rx]
set_property IOSTANDARD LVCMOS12 [get_ports fpga_uart_rx]

# FPGA Button (Reset / Alarm Clear)
set_property PACKAGE_PIN R26 [get_ports fpga_button]
set_property IOSTANDARD LVCMOS12 [get_ports fpga_button]

# ==============================================================================
# 3. STM32 MICROCONTROLLER INTERFACE (Bank 84 - 3.3V)
# ==============================================================================
# NOTE: "rx" here is from the STM32's perspective (FPGA Output)
# mcu_usart1_rx: Output from FPGA -> Input to STM32
set_property PACKAGE_PIN W12 [get_ports mcu_usart1_rx]
set_property IOSTANDARD LVCMOS33 [get_ports mcu_usart1_rx]

# mcu_usart1_tx: Input to FPGA <- Output from STM32
set_property PACKAGE_PIN AB16 [get_ports mcu_usart1_tx]
set_property IOSTANDARD LVCMOS33 [get_ports mcu_usart1_tx]

# Status LED
set_property PACKAGE_PIN AF14 [get_ports status_o]
set_property IOSTANDARD LVCMOS33 [get_ports status_o]

# ==============================================================================
# 4. CONFIGURATION & BITSTREAM
# ==============================================================================
set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets fpga_button_IBUF]
set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]
set_property CONFIG_MODE SPIx4 [current_design]
set_property BITSTREAM.CONFIG.CONFIGRATE 31.9 [current_design]