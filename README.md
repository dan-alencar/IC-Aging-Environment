# IC-Aging-Environment

## Vivado project

The cleaned SBCCI FPGA aging Vivado project is in
`vivado/sbcci_fpga_aging/`. Use its scripts to recreate the `.xpr` and build
the bitstream from source-controlled RTL, XDC, and XCI files:

```bash
cd vivado/sbcci_fpga_aging
scripts/create_project.sh
scripts/build_bitstream.sh --jobs 8
```

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
