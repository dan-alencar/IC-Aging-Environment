# IC-Aging-Environment

## Vivado Projects

The organized Vivado workspace is in `vivado/`.

- `vivado/sbcci_fpga_aging/` is the active, reproducible Artix UltraScale+
  aging design.
- The previous `auto_tuning_fpgaging/sbcci_fpga_aging/` copy has been
  consolidated into `vivado/sbcci_fpga_aging/` and removed to avoid stale
  duplicate project files.
- Older generated Vivado folders remain at the repository root only as legacy
  references.

Use the active project scripts to recreate the `.xpr` and build the bitstream
from source-controlled RTL, XDC, and XCI files:

```bash
cd vivado/sbcci_fpga_aging
scripts/check_layout.sh
scripts/create_project.sh
scripts/build_bitstream.sh --jobs 8
```

Vivado generated output is written to `vivado/sbcci_fpga_aging/build/` and
`vivado/sbcci_fpga_aging/artifacts/`, which are ignored by Git.

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
