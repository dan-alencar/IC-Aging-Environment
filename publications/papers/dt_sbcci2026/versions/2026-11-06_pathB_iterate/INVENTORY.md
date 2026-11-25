# Phase 0 inventory: raw artifacts per campaign

Generated 2026-11-05. Descriptive statistics come from `analysis/inventory.py` → `generated/inventory.csv`.
These are full-file, unfiltered values: no soak exclusion, only link-down rows (slack = 0 or T = 0) dropped. They are for identification only and are **not** paper numbers.

## Where the raw data is

Phase 1 of the repo reorganization (`b908add`, 2026-09-30) deleted every campaign CSV from the working tree. All 98 distinct CSV blobs were recovered from git history and, per decision on 2026-11-05, are **versioned in the repository** under `data/campaigns/` (see its `README.md` and `SHA256SUMS`). Every file is byte-identical to an existing history blob.

## Campaign table

| # | Campaign | Raw file (path) | Rows / cadence / duration | Start → end | Commanded | Measured (full file) | CUT / RTL | Device |
|---|---|---|---|---|---|---|---|---|
| 1 | **SBCCI 2026 bang-bang 23.08 h** | `data/campaigns/2025-04_sbcci26_bangbang_23h/SBCCI_TCC_COMP_ESTABILIZADO.csv` | 41,499 / **2 s (0.5 Hz)** / 23.078 h | 2025-04-07 12:47:32 → 2025-04-08 11:52:14 | 115 °C die target, 1.3 V (stock thermostat, oven setpoint not logged) | T̄ = 107.73 °C, σ = 2.644; V̄ = 1.299 V, σ = 6.1 mV; slack 130.7 ± 3.23 cnt (124–138) | 50-inverter chain (SBCCI 2025 sensor; bitstream pre-dates repo) | not logged |
| 1b | (parent of #1) SBCCI 2025 **Week-1 burn-in**, bang-bang | `data/campaigns/2025-04_sbcci25_week1_bangbang/aging-plot-semana1.csv` | 295,239 / 2 s / **164.2 h** | 2025-04-07 12:47:32 → 2025-04-14 08:59:02 | 115 °C, +30 % VDD (1.3 V) | T̄ = 108.15 °C, σ = 2.71; V̄ = 1.299 V; slack 129.6 ± 3.47 | 50-inverter chain | not logged |
| 2 | **SBCCI 2026 PID 23.08 h** | `data/campaigns/2026-01_sbcci26_pid_23h/TCC_SBCCI_COMP_ESTABILIZADO.csv` | 83,086 / 1 s / 23.079 h | 2026-01-10 14:44:36 → 2026-01-11 13:49:27 | 115 °C die target; oven SP 83.0–88.0 °C (mean 83.01, *not* 80); PSU 1.450 V | T̄ = 117.04 °C, σ = 1.246; V̄ = 1.297 V, σ = 3.6 mV; slack 114.9 ± 1.46 (110–123) | 50-inverter chain: synthesized netlist at `1414f7a` (2026-01-11) has 50 `LUT1_L` in `not_series` | not logged |
| 3 | **212.6 h PID campaign** (TIP7266 "device A") | `data/campaigns/2026-05_rca_pid_212h/Tentative_1_20260524_203756.csv` (blob `dc202822`, 47 MB) | **772,484** / 1 s / 214.581 h | 2026-05-24 20:37:56 → ~2026-06-02 | oven SP 88.1–99.0 °C (mean 93.97), PSU 1.399–1.499 V | air 93.93 °C; T̄ = 125.05 °C, σ = 1.83; V̄ = 1.400 V; slack 278.5 ± 3.14 (267–321) | **16-bit ripple-carry adder** (`ripple_adder`/`adder_canary`, introduced `fa1a98a` 2026-05-17, "Bitstream works" `0c848fe` 2026-05-22) | not logged |
| 4a | 100 °C bang-bang (thesis Tab. 6) | `data/campaigns/2026-01_oven_100C_controller_tests/Forno_Sem_Controle_Setpoint100____20260110_115213.csv` | 4,004 / 1 s / 1.11 h | 2026-01-10 11:52:13 | thermostat at 100 °C | air 88.88 °C mean (whole file) | oven air only (DUT at ~37 °C, 1.0 V) | — |
| 4b | 100 °C PID tuned (thesis Tab. 5/6) | candidates in `data/campaigns/2026-01_oven_100C_controller_tests/`: `Final_Test_20260109_213200.csv`, `Final_Test_100_27.5start_20260111_161724.csv` | ~4,000 / 1 s / ~1.1 h each | 2026-01-09 / 2026-01-11 | SP 100 °C, Kp 2.78, Ki 1.06e-3, Kd 5.0 | — | oven air only | — |
| 5 | 100 °C SIMC (thesis Tab. 5) | `data/campaigns/2026-01_oven_100C_controller_tests/SIMC_20260111_181754.csv` | 4,374 / 1 s / 1.22 h | 2026-01-11 18:17:54 | SP 100 °C, Kp 2.78, **Ki 2.3e-3, Kd 0** | — | oven air only | — |
| 6 | FOPDT step test | `data/campaigns/oven_fopdt_step_test/step_test_data.csv` (1,171 rows, `Time_sec,Temperature_C`, starts 25.21 °C); shorter `step_test_data_host_app_short.csv` (323 rows) | ~5 s cadence | — | 50 % open loop | — | oven only | — |
| 7 | JICS corner sweeps / failure catcher | Week-0/1/2 table in JICS is **identical** to SBCCI 2025 Table I (April 2025, inverter chain). Raw sweep logs not found. A post-campaign sweep `data/sample_logs/Corners_20260602_191558.csv` (2026-06-02, RCA) exists. | — | — | — | — | — | — |

Smaller tuning and debug logs (e.g. `Teste_2-78_*`, `Teste_278_231_*`, `Calibrando_*`, `Comp_SBCCI_*`) are listed in `generated/inventory.csv` but aren't used by any campaign above.

## Answers to (a)–(c)

**(a) Same physical device? Yes.** Confirmed by the authors (2026-11-05): every sensor campaign ran on the same Nexys 4 DDR board, since no other boards were available. No log records the board serial. Note that the TIP7266 notes' "device A / device B" means *circuit* (bitstream/CUT), not board.

**(b) CUT per campaign: they differ.**
- 23 h bang-bang (April 2025) and 23 h PID (January 2026): **50-inverter chain** (`not_series`, 50 × `LUT1_L`), the SBCCI 2025 sensor. Slack levels are ~131 and ~115 cnt.
- 212.6 h run (May 2026): **16-bit RCA**, built after the 2026-05-17 RTL revamp. Slack is ~278 cnt.

So "same device and sensor" in the draft's Table 1 caption and Evidence section is wrong for the long run. The cross-run transfer in the projection section is also not valid as written: it takes σ_BB/σ_PID measured on the inverter chain and applies it to the RCA's σ = 0.84 cnt. The AF ratio is temperature-only and does transfer. The noise ratio is CUT-dependent (count-per-°C sensitivity differs), so it transfers only after normalizing by sensitivity, if at all.

**(c) Is the 212.6 h run JICS "Week 2"? No, not physically.**
SBCCI 2025 Week 1 (115 °C / +30 %) started 2025-04-07, and Week 2 (125 °C / +40 %) would have followed in mid-April 2025. Tentative_1 started 2026-05-24, more than a year later, with a different CUT. Its *conditions* match the Week-2 corner (125 °C, 1.4 V), which is presumably why JICS describes it as "during the Week 2 burn-in period". The draft's sentence "acquired on the same device during its second week of burn-in, after a first week at 115 °C" is therefore unsupported and must be rewritten.

## Other discrepancies found during inventory (they go to RECONCILIATION.md in Phase 1)

1. **The bang-bang run is the first 23.08 h of the SBCCI 2025 Week-1 burn-in.** The file is byte-identical to the first 41,500 lines of `aging-plot-semana1.csv`, and thesis §4.3 says the same. The device was therefore fresh at its start, while the PID run came months later on a device with accumulated stress. The two runs differ in aging state as well as in thermal loop.
2. **The bang-bang log is 0.5 Hz, not 1 Hz.** Both SBCCI 2026 and the draft say 1 Hz. τ_int must be computed in seconds, with n_eff taken from the actual cadence.
3. **The bang-bang log has no oven-air, setpoint, PSU or current columns.** "The thermostat reached its 80 °C air setpoint" can't be checked from this file.
4. **The PID 23 h run's oven setpoint was 83–88 °C, not 80 °C.** The outer DUT loop moved it, and the PSU commanded 1.45 V to hold 1.30 V on-die.
5. **The long bang-bang record exists:** 164.2 h on the inverter chain at the same 115 °C / 1.3 V commands. A *measured* bang-bang τ_int, σ, slope and T_min may be possible on the same CUT as the PID 23 h run, without any projection, but it would be a different device and aging state from the 212.6 h RCA run.
6. **SBCCI 2026 Table II was computed on the full files, without the 1 h soak exclusion its Methods claim.** Full file: 107.73 / 2.644 °C (BB) and 117.04 / 1.246 °C (PID), matching SBCCI. After dropping t ≤ 3600 s: 107.76 / 2.631 °C and 117.13 / **0.927** °C. The thesis's 108.2 / 2.63 and 117.2 / 0.91 are close to the post-soak values, which likely explains Phase 1 item 5. The exact thesis window still needs confirming.
