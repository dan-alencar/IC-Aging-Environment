# hdl/ — Quartus Prime project (MAX10 / DE10-Lite)

*[Leia em português](README.pt-BR.md)*

**Nothing here is a working design yet.** This is scaffolding: a file layout and a
set of build scripts that mirror the pattern already used by the Vivado projects in
`../../vivado/aging_study_nexys4ddr/` and `../../vivado/sbcci_fpga_aging/` — the goal
is that once front F1/F2 produce real RTL and constraints, `scripts/create_project.sh`
and `scripts/build_bitstream.sh` work the same way those Vivado scripts do:
reproducible, from source-controlled text files, no committed build output.

## Target device

- Part: **10M50DAF484C7G** (Intel MAX 10, 50K logic elements, 484-pin FBGA, speed
  grade 7).
- Board: DE10-Lite (or equivalent carrier for this part).
- Toolchain: Intel Quartus Prime **Lite** Edition. **Pin the exact version** you use
  for the whole project and record it in this file once chosen — the plan document's
  Section 6.1 explains why (fitter optimizations change between versions and silently
  invalidate compilation reproducibility, which Gate A depends on).

<!-- TODO once decided: record the exact Quartus Prime version here, e.g. "23.1std.1". -->

## Expected structure (fill in as F1/F2 progress)

```
hdl/
├── src/
│   ├── rtl/            # RTL sources — mirror vivado/aging_study_nexys4ddr/src/rtl/'s
│   │                    #  module split: top/, aging_sensor/, uart/, display/
│   └── constraints/     # .sdc (timing exceptions) and pin/location assignments
├── scripts/
│   ├── check_layout.sh       # sanity check, no Quartus needed (already works)
│   ├── create_project.tcl    # creates the .qpf/.qsf from source files (template)
│   ├── create_project.sh     # thin wrapper around create_project.tcl (already works)
│   └── build_bitstream.sh    # runs the full compile flow (template)
├── build/                # Quartus output -- gitignored, never commit
└── artifacts/            # final .pof/.sof -- gitignored, never commit
```

## Vivado → Quartus vocabulary, from the plan document (Section 2.4)

| Vivado / Artix-7 | Quartus / MAX10 |
|---|---|
| `PSEN`, `PSINCDEC`, `PSDONE` | `phasestep`, `phaseupdown`, `phasecounterselect`, `phasedone` |
| `DONT_TOUCH`, `KEEP` | `preserve`, `noprune`, `keep`, `dont_merge` (RTL attributes) |
| `LOC` / `BEL` constraints | `set_location_assignment LC_X..Y..N..` in the `.qsf` |
| Vivado Device View | Quartus Chip Planner |
| MMCM | PLL (`ALTPLL` with dynamic phase reconfiguration, or Altera PLL + Altera PLL Reconfig) |
| XADC | ADC SAR core via the Modular ADC Core IP (Platform Designer), temperature-sensing-diode mode |

The plan document's Table (Section 2.4, "Correspondência de recursos entre as
plataformas") is the authoritative version of this table — this is a quick-reference
copy, not a replacement.

## `scripts/create_project.tcl` — what's there and what isn't

The Tcl script in this directory is a real, minimal Quartus Prime project-creation
script (`quartus_sh -t create_project.tcl`) for part `10M50DAF484C7G`, following the
same environment-variable-override convention the Vivado `create_project.tcl` scripts
use (`VIVADO_PROJECT_NAME`, `VIVADO_PART`, etc. there; `QUARTUS_PROJECT_NAME`,
`QUARTUS_PART`, etc. here). It has explicit `# TODO` markers wherever it needs the
RTL/QSF/SDC file lists that only exist once F1/F2 produce them — it will not create a
useful project until those TODOs are filled in, but the scaffolding around them
(project creation, part assignment, top-level module setting) is real.
