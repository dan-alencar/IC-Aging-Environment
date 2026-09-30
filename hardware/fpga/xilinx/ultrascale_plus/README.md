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
