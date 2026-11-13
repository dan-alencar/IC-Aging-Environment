## fbs_aging_top timing (board pins: external/fpgaging-board-support/fpga/constraints/rv02a_pins.xdc).
create_clock -period 10.000 -name sys_clk [get_ports sys_clk_p]

## UARTs, button and LED are asynchronous and synchronised inside the design.
set_false_path -from [get_ports {fpga_uart_rx mcu_usart1_tx fpga_button}]
set_false_path -to [get_ports {fpga_uart_tx mcu_usart1_rx status_o}]

## The MMCM outputs (Vivado derives them): catcher 50 deg, phase-shiftable, measurement.
## Between the platform clock and the measurement clocks only synchronisers (alarms, stress
## enables) and the ring-oscillator counts (read while stopped) cross: no timing between them.
set c_catch [get_clocks -of_objects [get_pins u_clocks/u_mmcm/CLKOUT0]]
set c_phase [get_clocks -of_objects [get_pins u_clocks/u_mmcm/CLKOUT1]]
set c_meas  [get_clocks -of_objects [get_pins u_clocks/u_mmcm/CLKOUT2]]
set_clock_groups -asynchronous -group [get_clocks sys_clk] -group [list $c_catch $c_phase $c_meas]

## The sensor paths are timed on purpose: chain -> FF1 (phase clock) and FF2 (measurement
## clock), FF1/FF2 -> XOR -> FF3 (catcher clock). The sweep moves the phase clock at run
## time; static timing sees phase 0, where every chain must still meet setup.

## Ring oscillators: intended combinational loops, counters clocked by their last stage.
## (generate blocks flatten to names such as u_fabric/g_ro[0].cnt_reg[5] and u_fabric/g_ro[0].n[3])
set_property ALLOW_COMBINATORIAL_LOOPS TRUE [get_nets -hierarchical -filter {NAME =~ *u_fabric/g_ro*n[*}]
set_false_path -from [get_cells -hierarchical -filter {NAME =~ *u_fabric/g_ro*cnt_reg*}]
set_false_path -to [get_pins -hierarchical -filter {NAME =~ *u_fabric/g_ro*cnt_reg*/CLR}]
