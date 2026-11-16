# RV02A (xcau15p) FPGA designs

Two designs live here:

- **`fbs_aging_top`** (`src/rtl/fbs_aging/`): the IC-Aging payload on the fpgaging-board-support
  platform (fbs SPEC §6.1), used by App_DT_Monitor. No IP cores, so any Vivado that knows the
  part builds it (checked with 2024.2: WNS +1.25 ns, 8.75 % LUTs, 583 CARRY8).
  - Continuous sweeps of one MMCM fine-phase clock (19.841 ps steps, about 9000 sweeps/s at
    400 steps), statistics per window (count, last, min, max, sum, sum of squares) for every
    chain, and a 16-bin histogram of chain 0 (`AGING_WINDOW`, `AGING_CHAIN`).
  - Chains: 0 inferred 256-bit adder (the main sensor), 1–4 CARRY8 128/256/512/1024 bits,
    5–8 LUT 8/16/24/32 stages (the colleague's au15p_multi_B set), 9 a reference copy of
    chain 0 that toggles only in measurement windows (3 windows a minute by default).
  - Two ring oscillators counted in measurement windows (`AGING_RO`), for the die-temperature
    cross-check of boards B and C (V12).
  - Commands: `AGING_SET_MODE`, `AGING_SET_HIST`, `AGING_GET_INFO`, `PING`, `GET_INFO`.
  - Build: `scripts/build_fbs_aging.sh` → `build/fbs_aging/`. Simulation: `sim/test_rtl.py`
    (cocotb + Verilator, behavioural MMCM and fabric models).
  - **Fixed placement and routing (fbs V19).** The aged logic is placed and routed from
    `src/constraints/fbs_aging_fixed_pnr.xdc` (generated, about 1 MB): LOC/BEL/LOCK_PINS for all
    2670 cells under `u_fabric` (chains, sensors, ring oscillators), FIXED_ROUTE for every net
    inside it, and the MMCM, the three BUFGCEs, their clock roots and their clock routes. The
    build writes `chains.txt` (per-chain delays, skew and predicted steps) and `fabric_pnr.txt`
    (everything locked), and fails unless `chains.txt` equals the frozen
    `src/constraints/fbs_aging_fixed_pnr_chains.txt` to the picosecond. Checked 2026-11-16: a
    rebuild with the default placer and one with `AltSpreadLogic_high` (WNS +1.25 / +0.83 ns,
    so the rest of the design moved) both reproduce every chain exactly. Without the clock
    routes, the sensor skew still moved by up to 6 ps (one step on two chains); without any of
    it, a free rebuild moved chain 8 from 124 to 62 predicted steps.
  - To freeze a new placement (only when the aged logic changes, never during a campaign):
    `FBS_AGING_FREE_PNR=1 scripts/build_fbs_aging.sh build/fbs_aging_ref`, then
    `scripts/extract_fbs_aging_pnr.sh`, then a normal build. New placement = new baselines.
- **`fpga_unified_top`** (below): the SBCCI 2026 design with its Vivado IP, unchanged.

# SBCCI FPGA Aging Vivado Project

This is the cleaned, reproducible Vivado layout for the SBCCI FPGA aging
design. It keeps only source-controlled inputs plus scripts. Vivado-generated
output is written to `build/` and `artifacts/`.

Older generated Vivado projects still exist elsewhere in the repository for
reference. This directory is the active buildable source of truth.

The latest source updates from the former
`auto_tuning_fpgaging/sbcci_fpga_aging/` copy have been moved here. That old
duplicate project tree was removed.

## Directory Layout

```text
sbcci_fpga_aging/
├── README.md
├── docs/
│   └── SOURCE_MANIFEST.md
├── scripts/
│   ├── build_bitstream.sh
│   ├── build_bitstream.tcl
│   ├── check_layout.sh
│   ├── clean.sh
│   ├── create_project.sh
│   └── create_project.tcl
└── src/
    ├── constraints/
    ├── ip/
    └── rtl/
        ├── aging_sensor/
        ├── legacy/
        ├── monitor/
        ├── top/
        └── uart/
```

## Requirements

- AMD Vivado 2025.2 or newer is recommended because the XCI files were last
  saved with Vivado 2025.2.1.
- The Vivado executable must be on `PATH`, or set `VIVADO_BIN`.

Example:

```bash
source /tools/Xilinx/Vivado/2025.2/settings64.sh
```

## Check the Layout

This check does not require Vivado. It verifies that all scripted project inputs
exist and that the shell wrappers parse correctly:

```bash
scripts/check_layout.sh
```

## Create the Vivado Project

From this directory:

```bash
scripts/create_project.sh
```

This creates:

```text
build/sbcci_fpga_aging/sbcci_fpga_aging.xpr
```

To create and open the project in the Vivado GUI:

```bash
scripts/create_project.sh --gui
```

Useful options:

```bash
scripts/create_project.sh --project-name sbcci_fpga_aging
scripts/create_project.sh --part xcau15p-ffvb676-1-i
scripts/create_project.sh --build-dir /tmp/sbcci_fpga_build
```

## Build the Bitstream

```bash
scripts/build_bitstream.sh --jobs 8
```

The generated bitstream and reports are copied to:

```text
artifacts/sbcci_fpga_aging.bit
artifacts/timing_summary.rpt
artifacts/utilization.rpt
```

## Clean Generated Output

```bash
scripts/clean.sh
```

## Useful Overrides

```bash
VIVADO_BIN=/opt/Xilinx/Vivado/2025.2/bin/vivado scripts/create_project.sh
VIVADO_JOBS=16 scripts/build_bitstream.sh
VIVADO_BUILD_DIR=/tmp/sbcci_fpga_build scripts/build_bitstream.sh
```

The default target is:

```text
Part: xcau15p-ffvb676-1-i
Top:  fpga_unified_top
```

Equivalent command-line options are also supported by the wrappers:

```bash
scripts/build_bitstream.sh --jobs 16 --part xcau15p-ffvb676-1-i
```
