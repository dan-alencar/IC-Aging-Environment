# MAX10 / DE10-Lite Port — Aging Sensor Research (New Track)

*[Leia em português](README.pt-BR.md)*

This directory is the workspace for a **separate, parallel research line**: porting
the slack-based aging sensor from this repository's Artix-7/Artix UltraScale+
implementation to an **Intel MAX10 (10M50DAF484C7G)** device on a **DE10-Lite** board
(or equivalent), using **Intel Quartus Prime Lite** instead of Vivado.

Read **[`docs/plano-port-max10.pdf`](docs/plano-port-max10.pdf)** (or the LaTeX
source, `docs/plano-port-max10.tex`) first — it is the actual project plan: the
mandatory Phase 0 study tracks (E1–E6), the six implementation fronts (F1–F6), the
16-week schedule with decision gates, the risk register, and the acceptance criteria
for every deliverable. Everything below is scaffolding to help you start executing
that plan, not a summary that replaces reading it.

## How this relates to the rest of the repository

**The rest of this repository (everything outside `max10_port/`) is reference
material for this branch, not a foundation you build on top of.** It's the validated,
published implementation on different silicon (Artix-7, 28 nm planar) with a
different toolchain (Vivado). Read it to understand *why* the architecture is shaped
the way it is — the plan document's Section 2 ("Diagnóstico técnico de
portabilidade" / technical portability diagnosis) explains in detail what carries
over and what doesn't. Do not assume you can reuse RTL, constraint files, or IP
directly; the plan document is explicit about where the platforms diverge (clock
phase-shift granularity, PVT telemetry, configuration memory, transport).

Specifically worth reading before you start:
- **`../CLAUDE.md`** — dense, accurate map of the existing codebase.
- **`../docs/onboarding.tex`** — the 35-page onboarding manual (aging physics, RTL,
  software, protocols) for the reference implementation.
- **`../vivado/aging_study_nexys4ddr/`** — the specific reference implementation this
  port targets (per the plan's own Table 1): single-sensor, dual-adder RCA design on
  `main`. Not the experimental multi-sensor or inverter-chain branches.
- **`../vivado/aging_study_nexys4ddr/SENSOR_ARCHITECTURE.md`** — why the sensor is
  built the way it is; the reasoning here is exactly what Phase 0 track E3 asks you
  to re-derive from the MAX10 side.
- **`../App_Nexys/`** — the reference host application (protocol, worker threads, PID
  loop, CSV logging) that front F4 (telemetry) will need to either port or replace.

## Layout

Following the plan document's own recommended convention (Section 6.2, "Repositório
e convenções"):

| Directory | Purpose | Status |
|---|---|---|
| `docs/` | This branch's own documents: the project plan, and whatever Phase 0 study-track artifacts and technical notes the team produces. | Plan document in place |
| `hdl/` | Quartus Prime project: RTL, constraints (`.sdc`, `.qsf`), and build scripts. | Scaffold only — see `hdl/README.md` |
| `host/` | PC-side acquisition software (protocol, telemetry, logging, live plots). | Empty — see `host/README.md` |
| `analysis/` | Offline analysis: PVT variance decomposition, σ_resid estimation, degradation model fitting. | Empty — see `analysis/README.md` |
| `data/` | Raw campaign data. Immutable once written — see the plan's data-provenance requirement (Section 6.3). | Empty — see `data/README.md` |
| `minutes/` | Weekly meeting minutes (the plan requires these versioned, per Section 5.3). | Template only — see `minutes/README.md` |

## Before you write any code

The plan is explicit and bears repeating here: **Phase 0 (four weeks, six parallel
study tracks) is mandatory and blocking.** Nobody opens Quartus before their track's
study artifact is written and defended. If you're reading this file because you want
to start on the FPGA side, go read `docs/plano-port-max10.pdf` Section 3 first.
