# PATH A: free restructuring (2026-11-06)

Internal note, not part of the submission. Every number below comes from `generated/values.tex`, `generated/results_timescales.json` or `generated/results_sensor.json`. `make` passes: 4,606 / 5,000 words, 12 references, 9-word title, number audit OK, no overfull boxes, 5 pages.

## 1. New main idea and storyline

**Main idea:** on-chip aging sensors must be validated against the bench *at the averaging time where aging lives*. The thermostat's fast ripple is large, but a linear PVT correction removes almost all of it (96 % at the cycle peak). Slow die-temperature wander is corrected much less well (about 18–22 % of its effect remains on every run that has enough of it). That wander leaves an hour-scale floor in the corrected slack, and the floor sets the detection time: about 91 h on the long PID run, against 20 h predicted under white noise. A die-referenced loop fixes the stress mean, but with a coarse outer step (±3 °C dead-band, 1 °C steps, 30 min) it can itself create the slow wander that raises the floor.

**New title (9 words):** "When Can an On-Chip Sensor See Aging Under Burn-In?"

**Storyline:**
- **Opening (4 paragraphs).**
  - The PVT-dominated sensing problem.
  - The standards: JESD22-A108 is junction-referenced; MIL-STD-883 Method 1015 is ambient-referenced, with Tj as an upper bound.
  - Prior art: Vassighi; Sobas et al. regulate die T and V because ring oscillators respond to them. Our contribution is the cost of not doing so, not the discovery of the effect.
  - The question (how long, and which bench property sets it) and the answer.
- **The instrument and the logs.**
  - Sensor, including the auto-tuning and time-zero answers.
  - The two benches, compressed. The outer-loop dead-band is now stated.
  - Table 1, with dates and conditions stated neutrally.
- **A primer (tutorial, 544 words plus five equations, 19 % of the body).**
  - Signal model Eq. (1) and the "bad control" rule.
  - Trajectory-averaged AF with Jensen, Eq. (2).
  - Tracking budget, Eq. (3).
  - Allan and Hadamard deviation and how to read the slopes, Eq. (4).
  - Trend-detection time, Eq. (5), cited to Weatherhead et al., and how a floor changes its scaling.
  - A 5-step recipe for a 1 Hz log.
- **Delivered stress is set at the die.**
  - SBCCI 2026 values, ripple vs mean, budget.
  - The A/B caveats, the setpoint-adjusted ratio, and the new die-vs-air gain.
  - Figure 1, kept, with counterfactual curves added.
- **Ripple averages out; slow wander does not.** Figure 2 (new, Allan/Hadamard).
- **How long until aging is visible.**
  - Sublinear drift.
  - Detection time three ways (Table 2, new).
  - The window-slope spread.
  - Regressor-set sensitivity (Figure 3, new).
  - The thermometer cross-check.
  - The bench penalty in the floor regime.
- **What labs should report.**
  - Checklist (Table 3, revised: Allan/Hadamard deviation replaces σ/τ_int; it now asks for the drift's regressor set and the loop that set the die).
  - Limitations.
- **Conclusion (2 paragraphs):** the lesson, then three future steps.

## 2. Removed and why

| Removed | Why |
|---|---|
| Mutual-information analysis (TIP7266 coursework) | It ended "inconclusive", since quantization alone reproduces the PID residual MI. It doesn't serve the main idea. |
| BSC alarm-capacity model and Figure 2(b) | It modelled an alarm from white-noise parameters. The Allan two-window reading is the measured, model-free version of the same alarm. |
| Sequential "crosses 3σ for good after 16 h" test, and the Week-1 sequential 14 h | Fragile: about 30 % of 34 h windows have the non-aging sign. Replaced by the window-slope distribution. |
| Six-item contribution list | Replaced by a question-and-answer opening (D&T style) to save words for the tutorial. |
| Bang-bang projected detection times (Table 3, old columns) | Built on the white-noise σ²τ model, which the Allan analysis shows doesn't govern detection. Replaced by a 3-line floor-regime penalty. |
| "From detectability to failure" paragraph (failure catcher) | Not needed for the main idea. |
| Sobas "0.05 °C" and "<0.1 % over 1,000 h" | Found only in the 2026 follow-up and Micromachines, not in the cited 2022 paper. |
| Semenov 2003 reference | Kept Vassighi 2004 only, to free slots for Allan 1966 and Weatherhead 1998. |
| FOPDT/SIMC parameter values in the text | Compressed to one sentence. The 100 °C air-regulation comparison is kept. |

The macros for the removed material are still generated (RECONCILIATION uses some of them), but the manuscript doesn't print them.

## 3. New analyses (`analysis/timescales.py` → `generated/results_timescales.json`)

All analyses use the same loading as `run_analysis.py`: link-down rows dropped, first hour excluded, PVT = OLS on centered T and V.

**1. Overlapping Allan (ADEV) and Hadamard (HDEV) deviation.** Computed on die T and the corrected residual for all four logs. The floor is the median HDEV over 1–4 h.

| | Corrected-residual floor (cnt) | Die-T floor (°C) |
|---|---|---|
| BB23 | 0.045 | 0.18 |
| PID23 | 0.040 | 0.09 |
| BB164 | 0.039 | 0.17 |
| RCA214 | 0.250 | 0.80 |

- Ratio BB/PID: 1.13 at hours, against 1.30 in ADEV at 2 s. SBCCI's raw residual ratio is 1.24 and the fast residual ratio 1.31.
- Fraction of the thermal effect left after correction:
  - at the thermostat cycle peak (2.8 °C at about 11 min): 4 % (96 % removed);
  - for hour-scale wander: 22 % (BB23), 18 % (BB164), 21 % (RCA).
  - PID23 has too little slow wander for this to be meaningful (106 %).

**2. Window-slope distribution (long run).** Sliding windows with a 2 h stride, slopes fitted on 10-min block means.

| Window | Slope range (m cnt/h) | Positive (non-aging sign) |
|---|---|---|
| 34 h | −76 to +44 | 30 % |
| 72 h | −38 to −7 | 0 % |

- The noise-only spread (power-law drift removed) scales as W^−1.13. That is a floor regime (−1), not white noise (−1.5).
- 3 × spread meets the mean drift at W* = 91 h.

**3. Allan two-window reading.** The drift line |β|τ/√2 crosses the HDEV floor at τ = 31 h and reaches 3× the two-window noise at τ = 47 h, which means a 93 h run. With the 8 h long-run variance, Eq. (5) gives 89 h.

**Convergence:** the three independent estimates agree at about 90 h, against 20 h from the white-noise bound.

**4. Regressor-set sensitivity.** β in m cnt/h (HAC, 10-min blocks):

| Regressors | β |
|---|---|
| T, V | −18.3 |
| + oven air | −14.0 |
| + PSU current | −14.6 |
| + PSU voltage | −5.9 |
| + oven air, PSU voltage | −5.1 |

- At fixed T and V (hourly), PSU current rises 0.044 mA/h (9.5 mA over the run) and PSU voltage rises 4.0 mV. Both respond to the device state, so they are "bad controls".
- Current vs die T in hourly means: corr = 0.997. Adding current or voltage inflates the variance of the time coefficient 4.8–5.1-fold.
- Reported drift: −14.0 to −18.3 m cnt/h from exogenous regressors.

**5. Thermometer cross-check.** Supply current is a leakage thermometer, at 27 mA/°C.
- Its drift at a fixed XADC reading equals 13 % of the temperature drift that would explain the slack drift (2.7 °C over the run).
- So XADC temperature-readout drift can't explain the slack drift, unless current aging cancels it.

**6. Die response to oven-air changes (long run, 30-min blocks, lags 0–2 summed).**
- OLS gain: 1.2 °C per °C of air. The setpoint-instrumented IV gives 2.6, which is unstable in closed loop. The air follows the setpoint at 0.82. Levels are decorrelated by the feedback.
- At gain 1.2, the setpoint-adjusted AF ratio is 1.35 (at gain 1: 1.40).
- Die-to-air offset: 34.1 °C on PID23 and 31.1 °C on the long run. So a chamber setting doesn't fix the die mean.

## 4. How each known issue was handled

| Issue | Handling |
|---|---|
| 23 h BB vs PID isn't an A/B comparison | Stated neutrally in Logs and Stress: dates (April 2025 unstressed vs January 2026), PID air at 83 °C (3 °C above the 80 °C dial), PSU fixed at 1.45 V vs 5 mV trim, die feedback only on PID, die logged on both ("the difference is closed-loop use"). The 1.65× is called "a comparison of two bench architectures". Setpoint-adjusted 1.40 (gain 1) and 1.35 (measured gain 1.2) are given, and Figure 1(a) shows both curves. The thermostat-held-its-dial assumption is "we cannot test". |
| Standards | JESD22-A108 is junction-min, with ambient and bias adjusted, and asks to report ambient and max Tj. MIL-STD-883 Method 1015 is ambient-defined, with Tj as an upper bound. The reference is now "MIL-STD-883-1, Environmental Test Methods for Microcircuits, Part 1: Test Methods 1000–1999, 2019, Method 1015", with ".12" dropped. Not cited: the self-regulated burn-in patent (couldn't verify). |
| Prior art (Sobas) | Positioned as "built a bench that regulates die T and internal V precisely because ROs respond to both"; our work is "its cost". "0.05 °C" removed. |
| Eq. T_min | Kept as Eq. (5), cited to Weatherhead et al., JGR 103(D14):17149–17161, 1998 (verified, doi 10.1029/98JD00995). |
| Drift depends on regressor set | Now a result (Figure 3b), with the bad-control explanation and evidence (P and I drift at fixed T, V; VIF). The voltage loop being ON in the long run (PSU 1.399–1.499 V) is stated in Logs. |
| Noise: 1.07 vs 0.84; window slopes; fragile 16 h claim | The "single σ" is no longer central. The 0.84 appears only in the white-noise bound, labelled "fast residual". The window-slope spread (−76 to +44, 30 % positive at 34 h) is now in the text. The 16 h sequential claim is removed. |
| Unused \vSigRatio (1.31) | Used: "1.31× for the fast residual", alongside 1.24 (SBCCI) and 1.30 (ADEV at 2 s). |
| Auto-recalibration | One sentence. Each reading is a fresh sweep from the MMCM reference phase, restored after each sweep (`controller_controller.sv`), with no stored baseline, so it can't absorb drift. Clocking-path drift would read as slack drift. |
| Power-law time zero | "Time zero is the start of this run; the board's earlier stress makes n an apparent exponent." |
| XADC absolute accuracy | One sentence: it enters each bench's error vs target but largely cancels in same-chip comparisons. No number is given, because the ±4 °C figure couldn't be verified from DS181 (UG480 v1.9 removed it). |
| 19.85 vs 19.84 ps | The text uses \vPsINV (19.84) and \vPsRCA (17.86). |
| Bios / Kashyap pages | Kashyap pages 1–4 verified via Crossref. Co-author bios remain placeholders (TODO in source). |
| SBCCI loyalty | Printed: 107.73/117.04 °C, ⟨AF⟩ 31.1/51.3, 711/1182 h, residual 0.90/0.73 cnt (1.24×). Not printed: 9.37 °C, 1.44–1.92×. Nothing is framed as a correction. The late-window slopes of SBCCI are described as "establish a drift within each run; whether it is aging needs the longer record". |

## 5. Open items for the authors

1. **Main-idea risk: cross-CUT floor comparison.** The long run's floor (0.25 cnt) is about 6× the inverter-chain floors. We attribute it to the long run's 4.6× larger slow die wander (outer-loop dead-band), backed by the similar share of wander left after correction (about 20 % on all runs). It is still a different circuit and date. Confirm that the outer-loop dead-band and step (±3 °C, 1 °C, 30 min, from `workers.py` at commit 3b92e9d) were active in May 2026. Also confirm whether they were active in the 23 h PID run, where the setpoint stayed at 83 °C after the soak.
2. **Die-vs-air gain.** 1.2 (OLS) vs 2.6 (IV) is closed-loop identification, and only the OLS figure is used for the 1.35 ratio. If you prefer, drop the gain and keep only 1.40 with "upper bound if gain ≥ 1".
3. **Floor band.** The floor is defined over 1–4 h, the longest band the 23 h runs support. Few windows remain at 4 h on the 23 h runs, so the 1.13 BB/PID floor ratio is uncertain (no CI is given).
4. **"Bad control" judgement.** Treating PSU current and voltage as bad controls is the defensible reading, but it isn't proven: they could also proxy on-die IR drop near the path. The paper reports both and shows the evidence.
5. **Thermostat dial assumption.** Untestable, because the bang-bang log has no air channel.
6. **Remaining checks:**
   - The 16 nm FinFET slot is still commented out.
   - The co-author bios still need completing.
   - `RECONCILIATION.template.md` was not updated for the new analyses (it still renders).
   - The `package` target in the Makefile is unchanged and was not tested.
7. **Number whitelist.** It still lists 1.44, 1.92, 0.05, 0.1 and 1,000. They no longer appear in the text, so they're harmless, but they can be removed.
