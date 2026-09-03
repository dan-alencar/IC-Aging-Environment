# IC Aging Environment

*[Leia em português](README.pt-BR.md)*

A hardware-in-the-loop environment for accelerated FPGA aging (burn-in) experiments.
The system drives oven temperature via PID, programs and polls an on-chip slack sensor
that tracks timing degradation, and logs everything for later analysis. Developed at
**LESC — Laboratório de Engenharia de Sistemas de Computação, UFC** (Universidade
Federal do Ceará).

If you're new here, this file is the map. For depth, see:
- **[`docs/onboarding.tex`](docs/onboarding.tex)** (or the compiled
  [`docs/IC_Aging_Environment.pdf`](docs/IC_Aging_Environment.pdf)) — the full
  35-page manual: aging physics, RTL walkthrough, software architecture, protocols,
  workstation setup from scratch, running an experiment, and data analysis.
- **[`ARCHITECTURE.md`](ARCHITECTURE.md)** — design intent behind each subsystem.
- **[`PROTOCOL.md`](PROTOCOL.md)** — every serial protocol byte-for-byte.
- **[`CLAUDE.md`](CLAUDE.md)** — the working reference for AI coding assistants
  (Claude Code); also a very dense, accurate map of the codebase for humans in a hurry.

## Branches — which sensor architecture is where

This repo hosts more than one variant of the aging sensor. Pick the branch that
matches what you're doing:

| Branch | Architecture | Status |
|---|---|---|
| `main` | **Single-sensor, dual-adder RCA.** One ripple-carry-adder critical path, sampled by the `modern_sensible` metastability sensor, with a second identical adder (`adder_canary`) as a functional-error canary. This is the validated, published (SBCCI 2025/2026) design. | Reference / production |
| `inverter-chain-sensor` | Same single-sensor architecture, but the critical path is a parameterized inverter chain (`not_series`) instead of an adder — timing-only, no functional canary. | Experimental |
| `experimental-multi-sensor` | Four independent `rca_sensor_channel` instances sharing one phase-sweep controller, reporting all channels every tick. New protocol, new multi-channel UI. | Experimental, not yet hardware-validated |
| `max10-de10lite-port` | A **separate research line**: porting this sensor to an Intel MAX10 (DE10-Lite) target with Quartus Prime. Everything under `max10_port/`; the rest of this repo is kept there as reference material. See `max10_port/README.md` on that branch. | New team, exploratory |

Unless you're specifically working on one of the experimental variants or the MAX10
port, you want `main`.

## What's in this repository

| Path | What it is |
|---|---|
| `vivado/aging_study_nexys4ddr/` | Vivado project for the **Nexys4 DDR (Artix-7, xc7a100t)** target — the primary, best-documented hardware target. Pure RTL, no block design. |
| `vivado/sbcci_fpga_aging/` | Vivado project for the **SBCCI / Artix UltraScale+ (xcau15p)** target — a custom board, routes UART to both the sensor FPGA and an STM32. |
| `App_Nexys/` | PySide6 desktop app for a single Nexys4 DDR DUT: oven PID, PSU control, live plots, CSV logging. The reference app — read this one first. |
| `App_2Nexys/` | Same as `App_Nexys`, doubled for two independent Nexys4 DDR DUTs with independent PSU voltage control. |
| `App_FPGAging_Slack_Sensor/` | Desktop app for the SBCCI/UltraScale+ target; routes serial traffic between the FPGA and an STM32 bridge. Must be launched standalone (different hardware family). |
| `App_CornerSweep/` | Bench-characterization tool (not a burn-in app): sweeps VCCINT down through fixed "corners," then fine-steps voltage at each to locate the failure boundary. |
| `STM_FW_Aging/` | STM32L4R9 firmware (STM32CubeIDE project) for the SBCCI target's supervisory MCU — PMIC control, OLED display. |
| `Arduino-ESP/` | Arduino/ESP32 sketches: oven PID controller, UART router (SBCCI path), FOPDT step-test tool, UART sniffer. `legacy/` holds superseded versions. |
| `Artigos/` | Papers: group publications and drafts (`Artigos_GSEM/`), TCC materials (`Artigos_TCC/`), and literature review references organized by topic (`Artigos_refs_SBCCI_2025/`). |
| `docs/` | The onboarding manual (LaTeX source + compiled PDF). |
| `run.sh` / `launcher.py` | Root launcher — a dialog to pick which Nexys4 app to run. |

## Quick start

```bash
./run.sh
```

This shows a dialog to choose between `App_Nexys` (1 DUT), `App_2Nexys` (2 DUTs), and
`App_CornerSweep` (voltage characterization). Each app manages its own Python virtual
environment (created automatically on first run) and its own hardware connections —
nothing is shared between them. `App_FPGAging_Slack_Sensor` targets different hardware
and is launched standalone:

```bash
cd App_FPGAging_Slack_Sensor && ./run.sh
```

For first-time workstation setup (installing Vivado, udev rules for serial/JTAG
devices, identifying which `ttyUSB*` is which), see Chapter 8 of
`docs/onboarding.tex` — this is the part most worth reading before touching hardware.

## Building an FPGA bitstream

```bash
cd vivado/aging_study_nexys4ddr    # or vivado/sbcci_fpga_aging
scripts/check_layout.sh            # sanity check, no Vivado needed
scripts/create_project.sh          # generates build/*.xpr from source-controlled RTL/XDC
scripts/build_bitstream.sh --jobs 8
```

Generated output (`build/`, `artifacts/`) is never committed — everything needed to
reproduce a bitstream is version-controlled source (RTL, XDC, XCI).

## No automated test suite

All validation is against real hardware — oven, DUT, PSU. There is no CI. When in
doubt, read `CLAUDE.md`'s "No automated test suite" section before assuming something
should have unit tests.

## Contributing

There is no formal contribution process yet — this is a research lab codebase. If
you're a new team member: read `docs/onboarding.tex` end to end before your first
hardware session, and check with whoever's supervising your track before changing
`fixed_pnr_constraints.xdc`, `SENSOR_ARCHITECTURE.md`-documented invariants, or
anything already running a multi-day campaign.
