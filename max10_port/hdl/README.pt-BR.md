# hdl/ — Sensor de envelhecimento no MAX 10 (DE10-Lite)

*[English](README.md)*

## Alvo
- Dispositivo: **10M50DAF484C7G** (DE10-Lite)
- Ferramenta: **Quartus Prime Lite 25.1std, build 1129** (`25.1std.0 Lite Edition`). Use exatamente esta versão: mudanças do fitter entre versões invalidam comparações.

## Build (clone limpo)
```
cd max10_port/hdl
quartus_sh --flow compile max10_aging_port -c max10_aging_top   # ou abra max10_aging_port.qpf na interface
```
A saída vai para `output_files/` (ignorada pelo git). Grave `output_files/max10_aging_top.sof`.

Depois do build, confira `output_files/*.map.rpt`: os registradores do `scc_controller` **não** podem aparecer como "stuck at GND".

## Estrutura
```
max10_aging_port.qpf / .qsf   projeto + atribuições (pinos, posicionamento, fontes)
aging_pll.v / .qip / .ppf     IP da PLL (deslocamento dinâmico de fase)
src/rtl/                      top/, aging_sensor/, uart/, display/
src/constraints/max10_aging.sdc   restrições de timing
src/sim/                      testbenches + modelos comportamentais (só simulação)
scripts/run_sim.sh            roda todas as simulações (Icarus Verilog, sem Quartus)
scripts/                      demais scripts são esqueleto (não usados pelo build acima)
```

## Regras
- Versione só texto-fonte. Nunca `db/`, `output_files/`, `.sof/.pof`, `.bak` (ver `../.gitignore`).
- SignalTap está DESLIGADO no `.qsf` versionado; ligue só na sua cópia local.
- Se mudar `aging_pll.v` (períodos, fase do catcher, passo de fase), atualize os parâmetros correspondentes em `max10_aging_top.sv`.
