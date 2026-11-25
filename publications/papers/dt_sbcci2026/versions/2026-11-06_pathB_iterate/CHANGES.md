# CHANGES — Path B (iterate, fine adjustments), 2026-11-06

Baseline: `manuscript/main.tex` as copied from `../2026-11-05_v1_thermal-control/` (then `publications/papers/dt_sbcci2026/`) (4,967 words).
Result: `make` passes. 4,995 / 5,000 words, 12 / 12 references, title 9 words, number audit OK, no overfull boxes, 6 pages.
Structure, headings, storyline, figures and tables are unchanged. No SBCCI 2026 value is reframed as a correction, and 9.37 °C and 1.44–1.92× are not printed.

## Pipeline additions

- `analysis/robustness.py` (new, run by `make` after `pid_bench.py`) writes `generated/results_robust.json`:
  - HAC slopes (10-min blocks, Newey–West bandwidth 8 h, `dtlib.hac_slope`) for four regressor sets;
  - the joint fit S ~ T + V + t on the same blocks;
  - the supply-voltage range in the long run;
  - σ about the linear trend;
  - slopes in 34 h windows with a 2 h stride.
- `analysis/derive.py` reads that file and emits the new macros. It also emits `\vAFperK`, which is E_a/(k_B T²) at 115 °C and 0.7 eV, in % per kelvin.
- `analysis/number_whitelist.txt` no longer lists `19.85` (now `\vPsINV`) or `0.05` (the Sobas 0.05 °C was dropped).

### New numbers (all printed through macros)

| Macro | Value | Meaning |
|---|---|---|
| `\vBetaRegOven` | −14.0 m cnt/h | HAC slope, regressors T, V, oven T |
| `\vBetaRegPsu` | −5.9 m cnt/h | HAC slope, regressors T, V, PSU voltage |
| `\vBetaJoint` | −18.4 m cnt/h | t coefficient of S ~ T+V+t (10-min blocks; HAC SE 2.0) |
| `\vBetaRegOvenPsu` | −5.1 m cnt/h | T, V, oven T, PSU V (computed, not printed) |
| `\vPSUminRCA` / `\vPSUmaxRCA` | 1.399 / 1.499 V | supply range, long run (voltage loop ON) |
| `\vPSUmeanRCA` | 1.49 V | (not printed). The PSU correlates 0.88 with die T, which is why it absorbs signal. |
| `\vSigFullRCA` | 1.07 cnt | σ of the [T,V] residual about its linear trend ("full") |
| `\vWinLen`, `\vWinSlopeMin`, `\vWinSlopeMax`, `\vWinPosPct` | 34 h, −76, +44 m cnt/h, 30 % | sliding-window slopes, 2 h stride (90 windows) |
| `\vAFperK` | 5.4 % per K | first-order AF sensitivity (tutorial) |

The T, V baseline (−18.3) reproduces `\vBetaRCA`. All regressor-set slopes are negative.

---

## 1. Framing of the bang-bang vs PID comparison

- **Abstract**
  - Old: "we compare a stock thermostatic oven with a die-referenced PID oven. The thermostat under-delivers Arrhenius acceleration by 1.65×…"
  - New: "we compare a stock thermostatic oven without die feedback and a die-referenced PID oven. The thermostat delivered 1.65× less Arrhenius acceleration (1.40× at matched air setpoint)…"
- **Introduction, paragraph 3:** "…found that, as operated (only the PID used die feedback), the two benches delivered different stress…"
- **Delivered stress, first quantification:** "relative to the PID bench, whose die ran 2.04 °C above target, the thermostatic bench delivered 1.65× less acceleration (711 versus 1,182 equivalent hours…)".
- **Setpoint-adjusted ratio**
  - Old: "If the die followed the air one-for-one, a thermostat set to the PID's air temperature would still deliver 1.40× less acceleration; the bang-bang log has no oven-air channel…"
  - New: "Shifting the thermostatic die trajectory by that offset leaves a setpoint-adjusted ratio of 1.40×, assuming that the die follows the air one-for-one and that the thermostat held its dial, neither testable without an oven-air log; as self-heating amplifies the air's effect on the die, this is likely an upper bound. We therefore report the 1.65× gap as a property of the two benches as operated."
  - "80 °C setpoint" is now "nominal 80 °C dial".
- **The two 1.40 values**
  - `\vAFratioSPadj` is always labelled "setpoint-adjusted ratio" or "at matched air setpoint".
  - `\vPenStress` is now "the detection-time stress penalty $1.65^{2/3}$ = 1.40×".
- **Die telemetry wording**
  - Old: "it must know the die's mean temperature, which requires die-level telemetry."
  - New: "it must regulate the die's mean temperature, which requires die telemetry used in closed loop."
  - Conclusion, old: "…which a chamber-level log cannot reveal…"
  - Conclusion, new: "In our pair, as operated without die feedback, the thermostatic bench's dominant error was the mean die temperature, not the air ripple a chamber log shows; it logged the die but did not regulate it." The conclusion also prints "(1.40× at a matched air setpoint)".
- **Voltage sentence**
  - Old: "…despite its software compensation and the PID's fixed supply, because the die's leakage follows the thermal cycle."
  - New: "…only that bench trimmed its supply, and its 5 mV steps may add to the die leakage that follows the thermal cycle."
- **Fast-residual ratio:** "on the fast residual, which is robust to early drift on the then-unstressed device, the ratio is 1.31×."
- **Limitations:** "…with different oven setpoints and supply control; these confounders bear on the stress and noise ratios."
- **Logging cadence (stated neutrally):** "the bang-bang run, logged every 2 s, is the first day of the Week-1 burn-in…"

## 2. Standards

- **Opening**
  - Old: "The standards for accelerated stress define it at the junction: …"
  - New: "Stress standards anchor it differently. JEDEC JESD22-A108 sets operating-life stress by a minimum junction temperature, adjusting ambient and bias to reach it, and leaves the detailed application of burn-in outside its scope; MIL-STD-883 Method 1015 sets burn-in by ambient temperature, with the junction as an upper bound. Either way, a typical bench controls and logs the chamber…"
- **Checklist section**
  - Old: "The standards already define stress at the junction; the gap is in verification."
  - New: "JEDEC already defines operating-life stress at the junction and has the test specification state chamber ambient and maximum junction temperature; MIL-STD-883 sets the ambient. Either way the bench controls the air, and the gap is in verification."
  - Added: "…which adds to A108's items the die mean and trajectory, σ, τ_int and T_min."
- **Limitations**
  - Old: "Statements about JEDEC and MIL-STD conditions are interpretive and do not claim chamber certification."
  - New: "We do not claim compliance with either standard."
- **MIL reference:** title is now "Environmental Test Methods for Microcircuits, Part 1: Test Methods 1000–1999", MIL-STD-883-1, Method 1015.12, U.S. DoD, 2019.
- **Verification**
  - A108: I verified the text of revision B (third-party copy). §1 places burn-in outside the scope. §4.2.1 says that "ambient temperature and bias … shall be adjusted to result in a minimum junction temperature…". §8 "Summary" lists "Stress temperature (chamber ambient)" and "Maximum junction temperature during stress" as items the life-test specification shall specify. I did not see revision G itself; secondary sources (globalspec) show the same scope and Tj clauses in later revisions.
  - Method 1015.12: listed in MIL-STD-883L as residing in MIL-STD-883-1.
  - Method 1015's ambient-based condition (TA ≥ 125 °C, junction limited): this comes from secondary sources (vendor QM notices). I did not see the 1015.12 text itself.

## 3. Prior art (Sobas et al., MR 138, 2022)

- **Introduction**
  - Old: "dedicated FPGA aging benches regulate the die itself"
  - New: "a dedicated FPGA aging bench regulates die temperature and internal voltage precisely because its on-chip ring oscillators respond to both". This is verified against the 2022 abstract: the RO is "sensitive not only to ageing but also to temperature and voltage", so they "installed a regulation system to control the temperature and the internal voltage of the FPGA".
- **Gap sentence**
  - Old: "What has not been examined is how this gap affects the validation of on-chip sensors…"
  - New: "What has not been quantified is the cost, in delivered stress, residual noise and detection time, of the chamber-referenced benches many labs still use to validate on-chip sensors…" I used "many" instead of "most", because "most" has no support.
- **"Within 0.05 °C":** dropped. The figure is in Sobas & Marc, *Micromachines* 15(1):19, 2023, not in the cited MR 2022 paper.
- **"Seldom report"**
  - Old: "what sensor validations under burn-in seldom report is…"
  - New: "…in sensor validations under burn-in the delivered die trajectory and T_min are not routinely reported; in our data they change the conclusions most."
- **Conclusion:** "drifts below 0.1 % over 1,000 hours even at elevated stress" is kept. It is verified in the MR 2022 abstract (1000 h, 100 °C, +25 % V).

## 4. Statistics and method (214.6 h run)

- **Weatherhead et al. (1998) added:** J. Geophys. Res. 103(D14):17149–17161, doi 10.1029/98JD00995, verified via Crossref.
  - Sentence after Eq. (3): "This is the trend-detection time of environmental statistics [Weatherhead], with 2τ_int as the noise-persistence factor: T_min grows only as σ^{2/3}, because a slope's error shrinks as T^{−3/2}." This sentence also serves as tutorial content.
  - Reference slot: the Vassighi 2004 entry was dropped and Semenov 2003 kept. Semenov's title is the one about thermal management during burn-in.
- **Voltage loop ON:** Evidence base now reads "…1.4 V on-die, held by the software trim with the supply between 1.399 and 1.499 V."
- **Regressor sensitivity:** added to the drift paragraph: "The slope depends on the regressor set: adding oven temperature gives −14.0 m cnt/h; adding the supply voltage, the trim loop's actuator, which may absorb aging signal, gives −5.9 m cnt/h; the joint fit S∼T+V+t gives −18.4 m cnt/h. All are negative."
- **Noise and sequential claim**
  - Old: "…the cumulative slope crosses 3σ for good after 16 h, a descriptive time rather than a stopping rule. Table 3 collects the three; none is wrong…"
  - New: "…raises T_min to 89 h, our defensible estimate. Because the drift is fastest early, the cumulative slope stays beyond 3σ from 16 h on, but this is descriptive and a lower bound: repeated looks inflate significance, and slopes over 34-hour windows (2-hour stride) range from −76 to +44 m cnt/h, 30 % of them positive. Table 3 collects the three."
  - The full σ is stated next to the fast one: "(the full residual about the trend is 1.07 cnt)".
- **Table 2:** row renamed "Sequential (descriptive) | measured, lower bound".
- **Abstract, introduction closing and conclusion**
  - Old: "16–89 h"
  - New: "about 89 h … (16 h as a descriptive lower bound)". The abstract prints no T_min range, so it needed no change.
- **Auto-recalibration:** "in the long run's bitstream every reading is a fresh sweep from the same restored phase, with no stored baseline, so recalibration does not subtract slow drift."
  - Source: `controller_controller.sv` at commit `9d72faa` (22 May 2026, two days before the run). The FSM backs the phase off to its start after each reading (DONE → RESET_PHASE → IDLE) and latches `display_value = inc_count`, with no stored baseline.
  - `RECONCILIATION.md` and `HANDOFF.md` say nothing about this point.
- **Power-law time origin:** "The fitted exponent is apparent: time counts from this run's start on a device with prior stress history."
- **XADC accuracy:** "Its absolute offset is common to all runs, so temperature differences are robust, but errors against the die target carry its absolute accuracy of a few degrees." No number is given, because it would need a datasheet citation.
- **19.85 ps:** now `\vPsINV` (19.84 ps).
- **Burn-in definition:** "(here, HTOL-like aging stress, not infant-mortality screening)".

## 5. Editorial

- Kashyap IRPS 2021: pp. 1–4, from Crossref (DOI 10.1109/IRPS46558.2021.9405187). The TODO was removed.
- SBCCI 2025 (Nogueira et al.): DOI 10.1109/SBCCI66862.2025.11218640, pp. 1–5, from Crossref. Crossref lists 7 authors (Nogueira, Mirailton, Alencar, Alisson, Silveira, Silveira, Vargas).
- Bios: the TODOs for the co-authors are kept.
- Table 3, item 3: "Post-PVT residual σ, full and fast | Full: BB 0.90, PID 0.73 cnt (23 h); 214.6 h: full 1.07, fast 0.84 cnt".

## Tutorial content (lightly strengthened)

- **Jensen:** "A second-order (Jensen) expansion of Eq. (1) about the mean predicts a gain of ½(E_a σ_T/k_B T²)², 1.1 %: each kelvin moves AF by only about 5.4 %, so ripple averages out to second order, whereas a mean error compounds at first order."
- **Trend detection:** the Weatherhead sentence above, on the scaling of T_min with σ and the T^{−3/2} slope error.

## Cuts made to stay within budget

- Mutual information paragraph:
  - Old: "…carry I(S;T,V)=1.13 bits … inconclusive, because…"
  - New: "on the long run a linear correction removes 85 % of the short-term mutual information, and residual-MI comparisons between benches are limited by integer slack quantization. The thermostatic excess behaves as broadband variance." The old wording "which no correction removes" was too strong.
- The road-map sentence at the end of the introduction was removed.
- The contribution items were tightened. So were the PID-construction, alarm, bench-penalty and failure-catcher paragraphs, and the "23-hour runs" sentence.
- The MI methods sentence was removed.
- The Limitations clause on projections was shortened, because the bench-penalty paragraph already states that assumption.

## Open items for the authors

1. **Recalibration.** Confirm that the 214.6 h run used the `9d72faa` controller, which re-sweeps from a restored phase with no stored baseline. Also confirm that this is what SBCCI 2025 calls "recalibrates autonomously".
2. **JESD22-A108G.** I verified §1, §4.2.1 and the §8 summary on revision B only. Please check the wording against G, in particular "chamber ambient" and "maximum junction temperature" as specified items.
3. **MIL-STD-883-1.** Confirm the 2019 date and Method 1015.12. 1015.12 is listed in 883L; I did not read the method text or confirm its ambient condition.
4. **XADC absolute accuracy.** If you want a number, cite the Artix-7 datasheet (DS181) and add the value to the whitelist.
5. **Weatherhead's formula.** The full PDF returned 403. The correspondence of Eq. (3) with their n* ∝ [σ_N/|ω₀| · √((1+φ)/(1−φ))]^{2/3} is from the standard form of that paper, not re-read from the text. The abstract (verified) confirms the dependence on noise variance and autocorrelation.
6. **Word budget.** It is tight: 4,995 / 5,000. Any new sentence needs an equal cut.
7. **Bios.** The co-author bios (Nogueira, Barros, Pamplona, Grangeiro, Vargas) still lack degree and position.
