# hdl/ — Aging sensor on MAX 10 (DE10-Lite)

*[Português](README.pt-BR.md)*

## Target
- Device: **10M50DAF484C7G** (DE10-Lite)
- Toolchain: **Quartus Prime Lite 25.1std, build 1129** (`25.1std.0 Lite Edition`). Use this exact version: fitter changes between versions invalidate comparisons.

## Build (clean clone)
```
cd max10_port/hdl
quartus_sh --flow compile max10_aging_port -c max10_aging_top   # or open max10_aging_port.qpf in the GUI
```
Output goes to `output_files/` (git-ignored). Program `output_files/max10_aging_top.sof`.

After building, check `output_files/*.map.rpt`: it must **not** list `scc_controller` registers as "stuck at GND".

## Layout
```
max10_aging_port.qpf / .qsf   project + assignments (pins, placement, sources)
aging_pll.v / .qip / .ppf     PLL IP (dynamic phase shift)
src/rtl/                      top/, aging_sensor/, uart/, display/
src/constraints/max10_aging.sdc   timing constraints
src/sim/                      testbenches
scripts/                      scaffolding (not used by the build above)
```

## Rules
- Commit only text sources. Never commit `db/`, `output_files/`, `.sof/.pof`, `.bak` (see `../.gitignore`).
- SignalTap is OFF in the committed `.qsf`; enable it only in your local copy.
- If you change `aging_pll.v` (periods, catcher phase, phase step), update the matching parameters in `max10_aging_top.sv`.
