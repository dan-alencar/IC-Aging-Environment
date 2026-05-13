# Aging Study Nexys4 DDR Vivado Project

This is the cleaned, reproducible Vivado layout for the original Artix-7
Nexys4 DDR aging-study design. It replaces the old generated
`aging-study/aging-study.xpr` workflow with source-controlled inputs and
scripts.

Vivado-generated output is written only to `build/` and `artifacts/`.
Checkpoint files (`.dcp`) are not source inputs; Vivado regenerates them per
machine. The only committed checkpoint is `references/fixed_pnr.dcp`, kept as a
historical reference for the fixed-route experiment and not added to the build.

## Directory Layout

```text
aging_study_nexys4ddr/
├── README.md
├── docs/
│   └── SOURCE_MANIFEST.md
├── scripts/
│   ├── build_bitstream.sh
│   ├── build_bitstream.tcl
│   ├── check_layout.sh
│   ├── clean.sh
│   ├── create_project.sh
│   ├── create_project.tcl
│   ├── extract_fixed_pnr_constraints.sh
│   └── extract_fixed_pnr_constraints.tcl
├── references/
│   ├── README.md
│   └── fixed_pnr.dcp
└── src/
    ├── bd/
    ├── constraints/
    ├── rtl/
    └── sim/
```

## Requirements

- AMD/Xilinx Vivado with Artix-7 device support.
- The Vivado executable must be on `PATH`, or set `VIVADO_BIN`.

Example:

```bash
source /tools/Xilinx/Vivado/2025.2/settings64.sh
```

## Check the Layout

```bash
scripts/check_layout.sh
```

This check does not require Vivado. It verifies that the scripted source inputs
exist, shell wrappers parse, and no generated `.dcp` checkpoints are present in
this clean project tree.

## Fixed PnR Constraints

The aging experiment depends on a specific placed and routed critical path. The
portable build uses `src/constraints/fixed_pnr_constraints.xdc` for that:

- `LOC` and `BEL` constraints keep the studied logic in the intended FPGA cells.
- `FIXED_ROUTE` preserves the routed `design_1_i/not_series_0/inst/critpath`
  interconnect path from the old `fixed_pnr.dcp` flow.
- `references/fixed_pnr.dcp` is retained only to audit or regenerate the XDC.

To regenerate the XDC from the preserved checkpoint on a machine with Vivado:

```bash
scripts/extract_fixed_pnr_constraints.sh
```

## Create the Vivado Project

```bash
scripts/create_project.sh
```

This creates:

```text
build/aging_study_nexys4ddr/aging_study_nexys4ddr.xpr
```

To create and open the project in the Vivado GUI:

```bash
scripts/create_project.sh --gui
```

## Build the Bitstream

```bash
scripts/build_bitstream.sh --jobs 8
```

The generated bitstream and reports are copied to:

```text
artifacts/aging_study_nexys4ddr.bit
artifacts/timing_summary.rpt
artifacts/utilization.rpt
artifacts/ip_status.rpt
```

## Useful Overrides

```bash
scripts/create_project.sh --project-name aging_study_nexys4ddr
scripts/create_project.sh --part xc7a100tcsg324-1
scripts/build_bitstream.sh --jobs 16
VIVADO_BUILD_DIR=/tmp/aging_study_build scripts/build_bitstream.sh
```

Default target:

```text
Part: xc7a100tcsg324-1
Top:  design_1_wrapper
```
