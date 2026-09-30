# Dataset Description — `Tentative_1_20260524_203756.csv`

This document characterizes the experimental log that anchors the project. It is the empirical substrate referenced throughout `02_Methodology.md`. All numbers below were computed directly from the file.

---

## 1. Provenance and acquisition

- **Source:** automated PID-controlled accelerated-aging burn-in platform (Danilo Alencar, TCC).
- **Start:** 2026-05-24 20:37:56.
- **Sampling:** 1 sample/s (intervalo de amostragem 1000 ms; SSR PWM window 5000 ms).
- **Control regime:** closed-loop PID on the oven, with identified plant model recorded in the header:

  $$G(s) = \frac{1.56\,e^{-150.6\,s}}{1307.2\,s + 1}, \qquad K=1.56\;^\circ\!C/\%,\; \theta=150.6\,s,\; \tau=1307.2\,s$$

  PID gains: $K_p = 2.78$, $K_i = 1.06\times10^{-3}$, $K_d = 5.0$. Ramp rate 1.0 °C/s.
- **Safety envelope (header):** oven ≤ 130 °C, DUT ≤ 160 °C, PSU ≤ 3.0 A.

The file begins with a commented (`#`) metadata block; the CSV body starts at the `time_sec,...` header row.

## 2. Schema

| Column | Meaning | Role in analysis |
|---|---|---|
| `time_sec` | seconds since start | index $t$ |
| `oven_temp_c` | oven chamber temperature | bench context |
| `oven_setpoint_c` | PID setpoint | regime documentation |
| `oven_output_pct` | PID actuation (SSR duty) | regime documentation |
| `psu_voltage_v` | supply voltage at PSU | bench context |
| `psu_current_a` | supply current | bench context (power/self-heating) |
| `dut_temp_c` | die temperature (XADC) | **$T$** |
| `dut_slack` | slack, integer phase-shift counts (1 ≈ 19.85 ps) | **$S$** (sensor output) |
| `dut_volt` | core voltage $V_{CCINT}$ (XADC) | **$V$** |

## 3. Size and duration

- **Raw data rows:** 772,484.
- **Duration:** 772,491.8 s ≈ **214.6 h ≈ 8.94 days**.
- **Dropout/invalid rows** (any of `dut_temp_c`, `dut_slack`, `dut_volt` = 0, i.e. FPGA link not yet up): **5 rows (≈0.0006 %)** — trivial, drop them.
- **Post-soak window** (after the first 1.0 h thermal-soak transient, matching prior-work convention): **768,884 samples** used for analysis.

## 4. Descriptive statistics (full record)

| Field | min | max | mean | std (pop) |
|---|---|---|---|---|
| `oven_temp_c` | 85.08 | 103.62 | 93.93 | 1.80 |
| `oven_setpoint_c` | 86.10 | 99.00 | 93.97 | 1.70 |
| `oven_output_pct` | 0.00 | 26.99 | 17.01 | 2.11 |
| `psu_voltage_v` | 1.399 | 1.499 | 1.492 | 0.004 |
| `psu_current_a` | 0.498 | 1.316 | 1.123 | 0.047 |
| `dut_temp_c` ($T$) | 0.00\* | 133.99 | 125.05 | 1.85 |
| `dut_slack` ($S$) | 0\* | 321 | 278.50 | 3.22 |
| `dut_volt` ($V$) | 0.00\* | 1.409 | 1.400 | 0.004 |

\* zeros are the 5 link-down dropout rows; on the post-soak valid window the slack range is **267–300 counts** and $T\approx125$ °C, $V\approx1.40$ V are held tight by the controllers.

The DUT is held in a **high-stress steady state** (≈125 °C, ≈1.40 V) — appropriate for accelerated aging — with the controller keeping $\sigma_T\approx1.85$ °C and $V$ essentially fixed.

## 5. Key relationships (post-soak window, $n=768{,}884$)

| Quantity | Value | Reading |
|---|---|---|
| $\mathrm{corr}(S, T)$ | **−0.859** | temperature is the dominant reversible driver: hotter ⇒ slower path ⇒ less slack |
| $\mathrm{corr}(S, V)$ | +0.213 | weaker, expected sign (more voltage ⇒ faster ⇒ more slack) |
| $\mathrm{corr}(S, t)$ | **−0.348** | a genuine slow downward (aging) drift over the campaign |
| LS slope $dS/dt$ (raw) | **−0.0171 counts/h** | uncorrected — confounded with $T,V$ drift; PVT correction must precede any RUL claim |
| linear $R^2(S \mid T,V)$ | **0.738** | environment explains ~74 % of slack variance *linearly* — sits between the prior PID (59 %) and bang-bang (92 %) figures |
| $H(S)$ (discrete, integer counts) | **3.43 bits** | over **27 occupied levels** (range 267–300; $\log_2 27 = 4.75$ bits if uniform) |

### Why these numbers motivate the project

- The strong, **non-linear** physics (Arrhenius in $T$, super-linear in $V$) motivated the hypothesis that the linear $R^2 = 0.738$ underestimates true environmental coupling; $I(S;T,V)$ tests that hypothesis directly. Result (2026-08-18, see `00_Work_Summary.md` §4): true on the raw series (17–26% excess, real), but the excess does **not** survive detrending, so it is not confirmed to be the hypothesized instantaneous non-linear PVT physics — see the honesty caveats.
- $H(S) = 3.43$ bits is the total sensor-output budget. The project's job is to split it: how much is environment ($I(S;T,V)$, removable), how much is the LSB quantization floor (irreducible), and how much is the recoverable aging signal — the three-way split the residual-σ metric alone cannot make.
- A measurable aging drift over 214 h is what makes the **RUL detectability bound** (Methodology §6.2) more than a formality: there is a real trend to detect above the reversible floor.

## 6. Known data hazards (carried into the pipeline)

1. **Heavy serial correlation** at 1 Hz ⇒ $n_{eff} \ll 768{,}884$; all confidence intervals use $n_{eff}$ and block bootstrap (Methodology §3.2).
2. **Quantization** of $S$ to integer counts ⇒ discrete entropy where appropriate; dither/continuity correction for kNN estimators (Methodology §3.3).
3. **Trend/seasonality confound:** the slow aging drift shares the time axis with any slow setpoint drift; detrend before computing $I(S;T,V)$ so MI measures reversible coupling, not the shared trend.
4. **Single regime:** this log is PID only; the bang-bang arm of the comparison comes from the published thermal-fidelity statistics until a matched-length bang-bang log is acquired.

## 7. Bench-comparison datasets (KL divergence) — different device

> **Important provenance note.** The two ~24 h runs below are acquired on a **different circuit/device (device B)** than the 214.6 h aging campaign of §1–§6 (**device A**). Device B is the same circuit-under-test used in the SBCCI 2025 sensor paper (`nogueira_sensor`) and in the TCC platform work; **both 24 h runs (the non-PID SBCCI bench and the PID reference) are on this same device B**, so their KL divergence isolates the bench/environment difference rather than device-to-device variation. This bang-bang-vs-PID, same-device pairing corresponds to the thermal-fidelity comparison of `alencar_fidelity` (SBCCI 2026, accepted). Their absolute slack levels and noise magnitudes are **not** comparable to device A's; no analysis mixes the two devices: all entropy/MI/correction/capacity/RUL/ICA results are device A, and only the KL/JS bench comparison is device B.

For the distributional comparison between validation environments (Methodology §4.3), two ~24 h *stabilized* runs are used, in `artigos/TCC vs SBCCI/`:

| File | Bench | Schema | Sampling | slack σ | temp σ |
|---|---|---|---|---|---|
| `SBCCI_TCC_COMP_ESTABILIZADO.csv` | SBCCI (non-PID) | `Data,Hora,Temperatura,Slack,Tensão` (temp & voltage in milli-units: `101036`→101.036 °C, `1228`→1.228 V) | 2 s | **3.23** | 2.64 °C |
| `TCC_SBCCI_COMP_ESTABILIZADO.csv` | TCC (PID reference) | standard 9-column log | 1 s | **1.46** | 1.25 °C |

The benches operate at different setpoints (SBCCI ≈108 °C / slack ≈131; PID ≈117 °C / slack ≈115), so the KL/JS comparison is performed on the **centered** slack fluctuation to isolate noise character from operating point. The slack-noise ratio (2.2×) tracks the temperature-noise ratio (2.1×), confirming the contamination is thermally driven. Result (see `analysis/kl_benches.py`): KL(SBCCI‖PID)=1.94 bits, KL(PID‖SBCCI)=1.01 bits (asymmetric), Jensen–Shannon = 0.279 bits.

## 8. Reproducibility

A small, dependency-light loader (skip `#` lines, parse the 9 columns, drop dropouts, slice `time_sec > 3600`) regenerates every number above. `analysis/tier1_pipeline.py` produces the entropy/MI/correction/capacity/RUL results and `analysis/kl_benches.py` the bench KL/JS; both emit their scalars into `latex/generated/values.tex`.
