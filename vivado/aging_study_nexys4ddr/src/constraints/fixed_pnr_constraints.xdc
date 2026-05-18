# Physical constraints for the aging study critical-path sensor.
#
# Instance names match nexys4_aging_top.sv:
#   u_sensor  — modern_sensible instance
#   u_adder   — adder_canary instance
#     u_adder/u_canary — ripple_adder inside adder_canary
#
# AND1 and BUF1 are commented out in modern_sensible.sv and must NOT
# appear here — Vivado errors on constraints referencing non-existent cells.

# --- CDC false-path: alarm_sig (FF3 / clk_en domain) → alarm_meta_reg (clk_sys) ---
# The 2-FF synchroniser in nexys4_aging_top.sv intentionally crosses this boundary.
# Without this constraint Vivado may flag a spurious timing violation because the
# two 100 MHz clocks share the same frequency but have a dynamically varying phase.
# Verify the destination name with: get_cells alarm_meta_reg
set_false_path \
    -from [get_pins  u_sensor/FF3/Q] \
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

# --- u_adder/u_canary ripple carry chain: PBLOCK ---
# Pins the 16-stage LUT carry chain adjacent to u_sensor (SLICE_X0-X3, Y91-Y92).
# After the first implementation run, open the Device view, locate
# u_adder/u_canary/FA[*]/fa, and tighten the range to the actual occupied sites.
create_pblock pblock_ripple_adder
add_cells_to_pblock [get_pblock pblock_ripple_adder] \
    [get_cells -hierarchical -filter {NAME =~ u_adder/u_canary/FA*}]
resize_pblock [get_pblock pblock_ripple_adder] -add {SLICE_X0Y80:SLICE_X5Y95}
set_property IS_SOFT FALSE [get_pblock pblock_ripple_adder]
