# Physical constraints for the aging study critical-path sensor.
#
# Instance names match nexys4_aging_top.sv:
#   u_sensor              — modern_sensible instance (top level)
#   u_adder               — adder_canary instance
#     u_adder/u_canary    — ripple_adder (canary: free-running counter)
#     u_adder/u_sensor    — ripple_adder (sensor: toggle-driven, feeds crit_bit)
#
# AND1 and BUF1 are commented out in modern_sensible.sv and must NOT
# appear here — Vivado errors on constraints referencing non-existent cells.

# --- CDC false-path: alarm_sig (FF3 / clk_en domain) → alarm_meta_reg (clk_sys) ---
# The 2-FF synchroniser in nexys4_aging_top.sv intentionally crosses this boundary.
# Without this constraint Vivado may flag a spurious timing violation because the
# two 100 MHz clocks share the same frequency but have a dynamically varying phase.
# Verify the destination name with: get_cells alarm_meta_reg
set_false_path \
    -from [get_cells u_sensor/FF3] \
    -to   [get_pins  alarm_meta_reg/D]

# --- u_sensor (modern_sensible): lock FF1, FF2, FF3, XOR1 ---
set_property BEL CFF   [get_cells u_sensor/FF2]
set_property BEL C6LUT [get_cells u_sensor/XOR1]
set_property BEL CFF   [get_cells u_sensor/FF1]
set_property BEL CFF   [get_cells u_sensor/FF3]

set_property LOC SLICE_X3Y92 [get_cells u_sensor/FF2]
set_property LOC SLICE_X2Y92 [get_cells u_sensor/XOR1]
set_property LOC SLICE_X1Y92 [get_cells u_sensor/FF1]
set_property LOC SLICE_X0Y92 [get_cells u_sensor/FF3]

# --- u_adder/u_canary + u_adder/u_sensor ripple carry chains: PBLOCK ---
# Both 16-stage LUT adder instances are co-located so they age at the same
# rate, making the timing metric (crit_bit phase count) and functional metric
# (error_count) causally comparable.  Region is placed adjacent to u_sensor
# (modern_sensible at SLICE_X0-X3, Y92) and sized for two 16-bit adders.
# After the first implementation run, open the Device view, locate
# u_adder/u_canary/FA[*] and u_adder/u_sensor/FA[*], and tighten the range.
create_pblock pblock_adders
add_cells_to_pblock [get_pblock pblock_adders] \
    [get_cells -hierarchical -filter {NAME =~ u_adder/u_canary/FA*}]
add_cells_to_pblock [get_pblock pblock_adders] \
    [get_cells -hierarchical -filter {NAME =~ u_adder/u_sensor/FA*}]
resize_pblock [get_pblock pblock_adders] -add {SLICE_X0Y74:SLICE_X5Y95}
set_property IS_SOFT FALSE [get_pblock pblock_adders]
