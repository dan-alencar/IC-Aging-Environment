# Vivado Workspace

This directory contains the organized Vivado projects for the IC aging
environment.

## Active Project

| Directory | Target | Top | Status |
| --- | --- | --- | --- |
| `sbcci_fpga_aging/` | `xcau15p-ffvb676-1-i` | `fpga_unified_top` | Active reproducible build |

The active project was consolidated from
`auto_tuning_fpgaging/sbcci_fpga_aging/`; that duplicate tree was removed so
new Vivado work has one source of truth.

Use the project-local scripts:

```bash
cd vivado/sbcci_fpga_aging
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
  `.jou`, `.log`, `.bit`, or generated checkpoints.
- If a legacy Vivado project is needed for comparison, keep it outside this
  directory or document it explicitly here before making it active.
