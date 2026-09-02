# Physical constraints for the aging study critical-path sensor.
#
# inverter-chain-sensor branch: instance names match nexys4_aging_top.sv:
#   u_sensor              — modern_sensible instance (top level)
#   u_delay_line          — not_series instance (50-stage inverter chain)
#     u_delay_line/lut_chain[*].INV — one LUT1 inverter per chain stage
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

# --- u_delay_line inverter chain: PBLOCK ---
# NOTE: this region is a first-cut placeholder, not a derived constraint.
# The 50-stage inverter chain is a linear/delay-critical structure, very
# different in shape from the two 16-bit adders this pblock used to cover
# (a-priori shot in the dark on the width). Placed adjacent to u_sensor
# (modern_sensible at SLICE_X0-X3, Y92) so both age together. After the
# first real implementation run, open the Device view, locate
# u_delay_line/lut_chain[*].INV, and re-derive this region with
# scripts/extract_fixed_pnr_constraints.sh rather than trusting this range.
create_pblock pblock_delay_line
add_cells_to_pblock [get_pblock pblock_delay_line] \
    [get_cells -hierarchical -filter {NAME =~ u_delay_line/lut_chain*}]
resize_pblock [get_pblock pblock_delay_line] -add {SLICE_X0Y74:SLICE_X5Y95}
set_property IS_SOFT FALSE [get_pblock pblock_delay_line]
