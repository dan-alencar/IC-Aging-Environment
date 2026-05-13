# Vivado Workspace

This directory contains the organized Vivado projects for the IC aging
environment.

## Active Project

| Directory | Target | Top | Status |
| --- | --- | --- | --- |
| `sbcci_fpga_aging/` | `xcau15p-ffvb676-1-i` | `fpga_unified_top` | Active reproducible build |
| `aging_study_nexys4ddr/` | `xc7a100tcsg324-1` | `design_1_wrapper` | Portable legacy Artix-7/Nexys4 DDR build |

The UltraScale+ project was consolidated from
`auto_tuning_fpgaging/sbcci_fpga_aging/`; that duplicate tree was removed so
new Vivado work has one source of truth. The Nexys4 DDR project was
consolidated from the old `aging-study/` and `FPGA XIlinx/aging-study/`
snapshots.

Use the project-local scripts:

```bash
cd vivado/sbcci_fpga_aging
scripts/check_layout.sh
scripts/create_project.sh
scripts/build_bitstream.sh --jobs 8
```

or for the original Artix-7 project:

```bash
cd vivado/aging_study_nexys4ddr
scripts/check_layout.sh
scripts/create_project.sh
scripts/build_bitstream.sh --jobs 8
```

## Repository Policy

- Keep source-controlled Vivado inputs under `src/`: RTL, constraints, and XCI
  IP configuration files.
- Keep generated Vivado outputs under `build/` and copied build results under
  `artifacts/`.
- Do not commit `.runs`, `.gen`, `.cache`, `.hw`, `.sim`, `.ip_user_files`,
  `.jou`, `.log`, `.bit`, or generated checkpoints such as `.dcp`.
- The only `.dcp` exception is
  `aging_study_nexys4ddr/references/fixed_pnr.dcp`, retained as a reference for
  regenerating/auditing the active fixed-route XDC constraints.
- If a legacy Vivado project is needed for comparison, keep it outside this
  directory or document it explicitly here before making it active.
