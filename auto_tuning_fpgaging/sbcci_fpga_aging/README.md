# sbcci_fpga_aging Vivado Project

This is the cleaned, reproducible Vivado layout for the SBCCI FPGA aging design.
The original Vivado project remains in `../../sbcci_fpga_aging`; this folder keeps
only source-controlled inputs plus scripts. Vivado-generated output is written to
`build/` and `artifacts/`.

## Directory Layout

```text
sbcci_fpga_aging/
├── README.md
├── docs/
│   └── SOURCE_MANIFEST.md
├── scripts/
│   ├── build_bitstream.sh
│   ├── build_bitstream.tcl
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

- AMD Vivado 2025.2 or newer is recommended because the source project was last
  saved with Vivado 2025.2.1.
- The Vivado executable must be on `PATH`, or set `VIVADO_BIN`.

Example:

```bash
source /tools/Xilinx/Vivado/2025.2/settings64.sh
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

## Build the Bitstream

```bash
scripts/build_bitstream.sh --jobs 8
```

The generated bitstream is copied to:

```text
artifacts/sbcci_fpga_aging.bit
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
