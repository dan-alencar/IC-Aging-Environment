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
# BANK 84 (High Density) - VOLTAGE 3.3V - STM32 INTERFACE
####################################################################################################
# UART 1 - Conexão com STM32
# mcu_usart1_rx: Output da FPGA -> RX do STM32
set_property PACKAGE_PIN W12 [get_ports mcu_usart1_rx]
set_property IOSTANDARD LVCMOS33 [get_ports mcu_usart1_rx]

# mcu_usart1_tx: Input da FPGA <- TX do STM32
set_property PACKAGE_PIN AB16 [get_ports mcu_usart1_tx]
set_property IOSTANDARD LVCMOS33 [get_ports mcu_usart1_tx]

# Status LED (Assuming AF14 is in Bank 84)
set_property PACKAGE_PIN AF14 [get_ports status_o]
set_property IOSTANDARD LVCMOS33 [get_ports status_o]

####################################################################################################
# BANK 65 (High Performance) - VOLTAGE 1.2V - PC/IHM INTERFACE (Header J9)
####################################################################################################
# ATENÇÃO: Estes pinos são 1.2V e passam por Level Shifter na placa.

set_property PACKAGE_PIN Y26 [get_ports fpga_uart_tx]
set_property IOSTANDARD LVCMOS12 [get_ports fpga_uart_tx]

set_property PACKAGE_PIN W26 [get_ports fpga_uart_rx]
set_property IOSTANDARD LVCMOS12 [get_ports fpga_uart_rx]

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

set_property C_CLK_INPUT_FREQ_HZ 300000000 [get_debug_cores dbg_hub]
set_property C_ENABLE_CLK_DIVIDER false [get_debug_cores dbg_hub]
set_property C_USER_SCAN_CHAIN 1 [get_debug_cores dbg_hub]
connect_debug_port dbg_hub/clk [get_nets soc_clk]