# Physical constraints for the aging study critical-path sensor.
#
# The not_series inverter chain has been replaced by adder_canary_0 (LUT
# ripple-carry adder). The old not_series_0 LOC/BEL/FIXED_ROUTE constraints
# have been removed. The modern_sensible_0 FF placement is kept so that the
# metastability sensor remains co-located with the end of the critical path.
#
# A PBLOCK pins the adder carry chain to a small, fixed region adjacent to
# modern_sensible_0 (which sits near SLICE_X0-X3, Y91-Y92). This ensures
# the carry-propagation delay is reproducible across builds. Adjust the
# coordinates after the first implementation run to a column that Vivado
# actually uses; IS_SOFT FALSE makes it a hard constraint.

# --- modern_sensible_0: keep original placement ---
set_property BEL CFF [get_cells design_1_i/modern_sensible_0/inst/FF2]
set_property BEL C6LUT [get_cells design_1_i/modern_sensible_0/inst/XOR1]
set_property BEL C6LUT [get_cells design_1_i/modern_sensible_0/inst/AND1]
set_property BEL A6LUT [get_cells design_1_i/modern_sensible_0/inst/BUF1]
set_property BEL CFF [get_cells design_1_i/modern_sensible_0/inst/FF1]
set_property BEL CFF [get_cells design_1_i/modern_sensible_0/inst/FF3]

set_property LOC SLICE_X3Y92 [get_cells design_1_i/modern_sensible_0/inst/FF2]
set_property LOC SLICE_X2Y92 [get_cells design_1_i/modern_sensible_0/inst/XOR1]
set_property LOC SLICE_X0Y92 [get_cells design_1_i/modern_sensible_0/inst/AND1]
set_property LOC SLICE_X0Y91 [get_cells design_1_i/modern_sensible_0/inst/BUF1]
set_property LOC SLICE_X1Y92 [get_cells design_1_i/modern_sensible_0/inst/FF1]
set_property LOC SLICE_X0Y92 [get_cells design_1_i/modern_sensible_0/inst/FF3]

# --- adder_canary_0 ripple carry chain: PBLOCK ---
# Pins the 16-stage LUT carry chain to a column adjacent to modern_sensible_0.
# Coordinates cover SLICE_X0-X5, Y80-Y95 — enough for 16 LUT3 stages (2 per slice).
# After the first implementation run, open the Device view, locate
# design_1_i/adder_canary_0/u_canary/FA[*]/fa, and tighten the range to the
# actual occupied sites.
create_pblock pblock_ripple_adder
add_cells_to_pblock [get_pblock pblock_ripple_adder] \
    [get_cells -hierarchical -filter {NAME =~ design_1_i/adder_canary_0/u_canary/FA*}]
resize_pblock [get_pblock pblock_ripple_adder] -add {SLICE_X0Y80:SLICE_X5Y95}
set_property IS_SOFT FALSE [get_pblock pblock_ripple_adder]
