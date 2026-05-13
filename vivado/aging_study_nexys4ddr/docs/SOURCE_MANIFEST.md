# Source Manifest

This file lists the reproducible inputs used by `scripts/create_project.tcl`.
Generated Vivado folders such as `.runs`, `.gen`, `.cache`, `.hw`, `.sim`,
`ip_user_files`, and all `.dcp` checkpoints are intentionally excluded.

This project is the portable version of the former root-level `aging-study/`
Vivado snapshot.

## Active Build Inputs

| Path | Purpose |
| --- | --- |
| `src/bd/design_1/design_1.bd` | Main Vivado Block Design |
| `src/bd/design_1/ip/**/*.xci` | Block Design IP and module-reference configuration |
| `src/constraints/Nexys-4-DDR-Master.xdc` | Nexys4 DDR pins, timing, and board constraints |
| `src/constraints/fixed_pnr_constraints.xdc` | Portable fixed placement and `FIXED_ROUTE` constraints extracted from the historical fixed PnR flow |
| `src/rtl/aging_sensor/` | Aging sensor, controller, temp catcher, and support RTL |
| `src/rtl/display/` | Seven-segment display conversion/display RTL |
| `src/rtl/uart/` | UART packet stream and transmitter RTL |

## Preserved Reference Inputs

| Path | Reason |
| --- | --- |
| `references/fixed_pnr.dcp` | Historical routed checkpoint for auditing/regenerating the fixed-route XDC; not used as a Vivado build input |
| `src/bd/design_2_legacy/` | Unused legacy Block Design copied from the old project for reference |
| `src/rtl/legacy/` | Older imported DRP/MMCM/LED helper RTL not added to the active build |
| `src/sim/sim.v` | Original behavioral simulation source |

## DCP Policy

Do not commit generated `.dcp` files. Old Vivado `.xpr` files often store
`IncrementalCheckpoint` or imported checkpoint paths, which breaks on another
computer when that local checkpoint is missing. The scripts here create a fresh
project and regenerate checkpoints under `build/` on each machine.

The exception is `references/fixed_pnr.dcp`, which is source-controlled only as
a reference artifact for the aging experiment. The build consumes the extracted
XDC constraints instead of opening that checkpoint.
