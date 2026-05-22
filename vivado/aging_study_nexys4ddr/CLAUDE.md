# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

Vivado RTL project for the Nexys4 DDR Artix-7 (xc7a100tcsg324-1) aging study. It implements a metastability-based phase-sensor that measures FPGA path timing degradation over time. All RTL is pure SystemVerilog — no block design.

## Build commands

```bash
# Sanity check (no Vivado required)
scripts/check_layout.sh

# Create Vivado project (generates build/*.xpr)
scripts/create_project.sh           # batch mode
scripts/create_project.sh --gui     # open in Vivado GUI after creation

# Build bitstream (runs create_project.tcl internally)
scripts/build_bitstream.sh --jobs 8

# Rebuild reference checkpoint + regenerate fixed_pnr_constraints.xdc
scripts/build_bitstream.sh --jobs 8 --refresh-ref

# Regenerate fixed_pnr_constraints.xdc from existing checkpoint only
scripts/extract_fixed_pnr_constraints.sh

# Remove build/ and artifacts/
scripts/clean.sh
```

Environment overrides: `VIVADO_BIN`, `VIVADO_PROJECT_NAME`, `VIVADO_PART`, `VIVADO_TOP`, `VIVADO_BUILD_DIR`, `VIVADO_JOBS`.

Bitstream lands in `artifacts/aging_study_nexys4ddr.bit`. Timing and utilization reports land alongside it.

## RTL module hierarchy

```
nexys4_aging_top                  ← top (src/rtl/top/)
├── clk_wiz_0                     ← MMCM with dynamic phase shift (src/ip/)
├── XADC                          ← on-chip temperature + VCCINT (primitive)
├── temp_catcher                  ← XADC DRP monitor → temp/vccint (milli°C / mV)
├── modern_sensible               ← 3-FF metastability sensor (aging_sensor/)
│     FF1: psclk (phase-shifted)  → samples crit_bit
│     FF2: sclk (reference)       → samples crit_bit
│     FF3: clk_en (100° fixed)    → latches XOR(FF1,FF2) = alarm_sig
├── 2-FF synchronizer             ← alarm_sig (clk_en) → alarm_sync (clk_sys)
├── adder_canary                  ← dual-adder sensor + functional canary (aging_sensor/)
│     u_sensor: toggle-driven ripple_adder → crit_bit (feeds modern_sensible)
│     u_canary: counter-driven ripple_adder → wrong/correct/error_count/error_any
├── controller_controller         ← phase-sweep FSM → display_value (aging_sensor/)
├── failure_holder                ← sticky latch for functional failure (aging_sensor/)
├── uart_rx                       ← receives 'T' (0x54) trigger byte from PC (uart/)
├── sensor_stream                 ← latches all inputs on trigger; serialises 15-byte packet (uart/)
├── uart_tx                       ← UART transmitter, 9600 baud (uart/)
├── BinToBCD × 2                  ← binary-to-BCD for display (display/)
├── DisplayController             ← 8-digit 7-segment multiplexer (display/)
└── vio_0                         ← Xilinx VIO debug core (created in create_project.tcl)
```

## Clock domains and resets

Three clocks from one MMCM (`clk_wiz_0`):
- `clk_sys` — 100 MHz, 0°. All RTL logic except modern_sensible FFs.
- `psclk` — 100 MHz, dynamically phase-shiftable. Drives FF1 in `modern_sensible`.
- `clk_en` — 100 MHz, 100° fixed. Drives FF3 (alarm latch) in `modern_sensible`.

`alarm_sig` originates in `clk_en`; it is synchronised to `clk_sys` via `alarm_meta/alarm_sync` before reaching any combinational logic. `alarm_sig` feeds only the LED directly.

`reset_p` (active-high) = `reset | ~locked`. XADC is reset only by the raw `reset` button. MMCM is reset by the button directly, not by lock-loss.

## Dual-adder sensor — current implementation status

**The dual-adder fix is already implemented** in `src/rtl/aging_sensor/adder_canary.sv`. The roadmap in `IMPLEMENTATION_ROADMAP.md` predates the actual code changes.

Design: `toggle` FF alternates every `clk_sys` cycle, driving `a_sensor` between `0x5555` and `0x5556`. With `B = 0xAAAA`, `sum_sensor[15]` toggles on every clock cycle and forces carry propagation through all 16 LUT stages — giving deterministic ±2-step `display_value` jitter instead of the original stochastic ~9 000-step values.

```
toggle → a_sensor (0x5555/0x5556) → u_sensor (DONT_TOUCH ripple_adder) → crit_bit → modern_sensible
a (counter)                        → u_canary (DONT_TOUCH ripple_adder) → wrong/correct/error_count
```

## Constraints strategy

Two XDC files, applied in order:
1. `src/constraints/Nexys-4-DDR-Master.xdc` — board pin assignments (used in synthesis + implementation).
2. `src/constraints/fixed_pnr_constraints.xdc` — LOC/BEL + FIXED_ROUTE locks for the aging-sensitive path. **Applied only during implementation, not synthesis** (see `create_project.tcl`). Do not modify placement or routing constraints without regenerating from a new checkpoint.

The reference checkpoint that `fixed_pnr_constraints.xdc` was extracted from lives at `references/fixed_pnr.dcp`. Regenerate both together with `--refresh-ref`.

## What must not change without understanding the consequences

- **`DONT_TOUCH` attributes** on `lut_full_adder` instances inside `ripple_adder` and on all primitives in `modern_sensible`. Removing them allows Vivado to replace the LUT ripple chain with CARRY4 primitives, destroying the aging-sensitive path and the `modern_sensible` topology.
- **`fixed_pnr_constraints.xdc`** — defines the fixed PnR experiment. Changing LOC/BEL or FIXED_ROUTE invalidates existing timing data. Regenerate only after a deliberate new PnR run.
- **`sensor_stream` packet layout** — the 15-byte layout (bytes 0–14) is consumed verbatim by `App_2Nexys/DUTWorker`. See `src/rtl/uart/sensor_stream.sv` for the byte map.
- **UART trigger byte** — the FPGA responds to `'T'` (0x54) to latch and transmit one packet. `App_2Nexys` sends this byte; changing it breaks the Python app.

## XADC conversion formulas (implemented in temp_catcher.sv)

- Temperature: `T_mC = (ADC_code[15:4] * 503975) >> 12`, then subtract 273150 for °C. Clamped to 0 before the XADC settles at power-on.
- VCCINT: `V_mV = (ADC_code[15:4] * 3000) >> 12`.

`temp_catcher` uses a DRP polling FSM: it asserts `DEN` with `DADDR = 0x00` (temperature status register), waits for `DRDY`, reads `DO`, then repeats for `DADDR = 0x01` (VCCINT). A 128-cycle watchdog retries if `DRDY` does not arrive. `DRDY` is a DRP-only signal — it fires only in response to `DEN` assertions, never spontaneously from conversion events (`EOC`/`EOS` serve that role). Tying `DEN = 0` silences `DRDY` permanently and breaks the module.

## Phase-sweep FSM (controller_controller.sv)

States: `CHECK_ALARM → INIT_SHIFT → WAIT_SHIFT → DONE → RESET_PHASE → WAIT_RESET → IDLE → CHECK_ALARM`.

`display_value` latches in `DONE` = number of phase-decrement steps before alarm. Higher value = more timing margin = healthier device. As the device ages, `display_value` decreases.

`psdone` edge-detected (`psdone && !psdone_prev`) rather than level-sensitive — prevents double-counting if `psdone` stays high across cycles.

## VIO debug core

`vio_0` (10 inputs, 0 outputs) is created programmatically in `create_project.tcl`. If the project is recreated, the VIO is regenerated automatically. Probes: `display_value`, `error_count`, `alarm_sync`, `locked`, `error_any_sig`, `temp_raw`, `vccint_raw`, `wrong`, `correct`, `psen_ctrl`.

## Key reference documents

- `SENSOR_ARCHITECTURE.md` — scientific rationale for the dual-adder design, why the original crit_bit source caused ~9 000-step stochastic values, and quantitative analysis.
- `IMPLEMENTATION_ROADMAP.md` — phased checklist for validation and data collection (Phases 1–2 RTL changes are done; Phases 3–7 remain).
- `references/README.md` — explains the fixed PnR checkpoint and when to refresh it.
