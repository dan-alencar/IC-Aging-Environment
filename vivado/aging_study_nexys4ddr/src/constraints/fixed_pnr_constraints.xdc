# Fixed physical constraints extracted from the historical fixed_pnr.dcp flow.
#
# These constraints are the portable replacement for using fixed_pnr.dcp as a
# project input.  LOC and BEL keep the studied cells in the same fabric sites,
# and FIXED_ROUTE preserves the routed critpath net used for the aging study.
# Keep this file after the board XDC in the constraints set so these physical
# constraints take precedence over any older placement lines in the board file.

set_property BEL A6LUT [get_cells {design_1_i/not_series_0/inst/genblk1[6].INV}]
set_property BEL C6LUT [get_cells {design_1_i/not_series_0/inst/genblk1[12].INV}]
set_property BEL C6LUT [get_cells {design_1_i/not_series_0/inst/genblk1[0].INV}]
set_property BEL C6LUT [get_cells {design_1_i/not_series_0/inst/genblk1[1].INV}]
set_property BEL B6LUT [get_cells {design_1_i/not_series_0/inst/genblk1[7].INV}]
set_property BEL B6LUT [get_cells {design_1_i/not_series_0/inst/genblk1[2].INV}]
set_property BEL D6LUT [get_cells {design_1_i/not_series_0/inst/genblk1[11].INV}]
set_property BEL D6LUT [get_cells {design_1_i/not_series_0/inst/genblk1[5].INV}]
set_property BEL C6LUT [get_cells {design_1_i/not_series_0/inst/genblk1[8].INV}]
set_property BEL B6LUT [get_cells {design_1_i/not_series_0/inst/genblk1[9].INV}]
set_property BEL BFF [get_cells design_1_i/not_series_0/inst/start_reg]
set_property BEL D6LUT [get_cells {design_1_i/not_series_0/inst/genblk1[3].INV}]
set_property BEL B6LUT [get_cells {design_1_i/not_series_0/inst/genblk1[4].INV}]
set_property BEL B6LUT [get_cells {design_1_i/not_series_0/inst/genblk1[10].INV}]
set_property BEL BFF [get_cells design_1_i/modern_sensible_0/inst/FF2]

set_property LOC SLICE_X3Y91 [get_cells {design_1_i/not_series_0/inst/genblk1[6].INV}]
set_property LOC SLICE_X1Y92 [get_cells {design_1_i/not_series_0/inst/genblk1[12].INV}]
set_property LOC SLICE_X3Y91 [get_cells {design_1_i/not_series_0/inst/genblk1[0].INV}]
set_property LOC SLICE_X1Y91 [get_cells {design_1_i/not_series_0/inst/genblk1[1].INV}]
set_property LOC SLICE_X3Y91 [get_cells {design_1_i/not_series_0/inst/genblk1[7].INV}]
set_property LOC SLICE_X1Y91 [get_cells {design_1_i/not_series_0/inst/genblk1[2].INV}]
set_property LOC SLICE_X0Y92 [get_cells {design_1_i/not_series_0/inst/genblk1[11].INV}]
set_property LOC SLICE_X0Y91 [get_cells {design_1_i/not_series_0/inst/genblk1[5].INV}]
set_property LOC SLICE_X3Y92 [get_cells {design_1_i/not_series_0/inst/genblk1[8].INV}]
set_property LOC SLICE_X3Y92 [get_cells {design_1_i/not_series_0/inst/genblk1[9].INV}]
set_property LOC SLICE_X2Y91 [get_cells design_1_i/not_series_0/inst/start_reg]
set_property LOC SLICE_X1Y91 [get_cells {design_1_i/not_series_0/inst/genblk1[3].INV}]
set_property LOC SLICE_X0Y91 [get_cells {design_1_i/not_series_0/inst/genblk1[4].INV}]
set_property LOC SLICE_X0Y92 [get_cells {design_1_i/not_series_0/inst/genblk1[10].INV}]
set_property LOC SLICE_X3Y92 [get_cells design_1_i/modern_sensible_0/inst/FF2]

set_property FIXED_ROUTE { { CLBLL_L_C CLBLL_L_CMUX CLBLL_LOGIC_OUTS18  { NR1BEG0 BYP_ALT1 BYP_L1 CLBLL_LL_AX }  ER1BEG1 BYP_ALT5 BYP5 CLBLM_L_BX }  } [get_nets design_1_i/not_series_0/inst/critpath]

set_property BEL C6LUT [get_cells design_1_i/modern_sensible_0/inst/XOR1]
set_property BEL C6LUT [get_cells design_1_i/modern_sensible_0/inst/AND1]
set_property BEL A6LUT [get_cells design_1_i/modern_sensible_0/inst/BUF1]
set_property BEL CFF [get_cells design_1_i/modern_sensible_0/inst/FF1]
set_property BEL CFF [get_cells design_1_i/modern_sensible_0/inst/FF3]

set_property LOC SLICE_X2Y92 [get_cells design_1_i/modern_sensible_0/inst/XOR1]
set_property LOC SLICE_X0Y92 [get_cells design_1_i/modern_sensible_0/inst/AND1]
set_property LOC SLICE_X0Y91 [get_cells design_1_i/modern_sensible_0/inst/BUF1]
set_property LOC SLICE_X1Y92 [get_cells design_1_i/modern_sensible_0/inst/FF1]
set_property LOC SLICE_X0Y92 [get_cells design_1_i/modern_sensible_0/inst/FF3]
