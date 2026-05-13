# IC-Aging-Environment

## Vivado Projects

The organized Vivado workspace is in `vivado/`.

- `vivado/sbcci_fpga_aging/` is the active, reproducible Artix UltraScale+
  aging design.
- `vivado/aging_study_nexys4ddr/` is the portable version of the original
  Artix-7/Nexys4 DDR `aging-study` design.
- The previous `auto_tuning_fpgaging/sbcci_fpga_aging/` copy has been
  consolidated into `vivado/sbcci_fpga_aging/` and removed to avoid stale
  duplicate project files.
- The previous root-level `aging-study/` Vivado snapshot has been consolidated
  into `vivado/aging_study_nexys4ddr/` and removed because its `.xpr` carried
  non-portable generated run state.
- The previous `FPGA XIlinx/aging-study/` snapshot has also been consolidated
  and removed. Its `fixed_pnr.dcp` is preserved at
  `vivado/aging_study_nexys4ddr/references/fixed_pnr.dcp`, and the active build
  uses `src/constraints/fixed_pnr_constraints.xdc` for the fixed LOC/BEL and
  `FIXED_ROUTE` behavior.

Use the active project scripts to recreate the `.xpr` and build the bitstream
from source-controlled RTL, XDC, and XCI files:

```bash
cd vivado/sbcci_fpga_aging
scripts/check_layout.sh
scripts/create_project.sh
scripts/build_bitstream.sh --jobs 8
```

For the original Nexys4 DDR project:

```bash
cd vivado/aging_study_nexys4ddr
scripts/check_layout.sh
scripts/create_project.sh
scripts/build_bitstream.sh --jobs 8
```

Vivado generated output is written to project-local `build/` and `artifacts/`
directories under `vivado/`, which are ignored by Git. Do not commit generated
`.dcp` checkpoints; the scripts regenerate them on each machine. The preserved
fixed PnR checkpoint is reference-only and is not added as a Vivado build input.

Temperatura do forno* -> termostato externo
Temp. Int. da FPGA
Temp. da placa* -> não usávamos
Tensão da fonte externa
Tensão Int. da FPGA != tensão da fonte (quanto mais quente)
Slack = Período - Delay

Controle PID -> Estabilizar a temperatura do forno -> Estabilizar a temp. da placa/FPGA -> Estabilizar as tensões 

Testes de Burn-in

Problema: 

Solução:
