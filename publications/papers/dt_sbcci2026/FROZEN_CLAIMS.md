# Frozen claims ledger: D&T hybrid manuscript (frozen 2026-11-06)

Internal file; not part of the submission. From here on, changes may move these sentences
or shorten them, but must not change their numbers or their hedges unless new data justify it.
Every value comes from `generated/values.tex`; the macro name is in brackets.

## 1. Thesis (stable since V7)
Read the bench by averaging time:
- **Minutes:** a temperature–voltage correction removes the thermostat ripple. The PID bench's lower
  sample-rate noise helps short-window decisions, such as AVS margins.
- **Hours:** a noise floor that neither bench removes sets how long a run must last.
- **Whole run:** the mean die temperature sets how fast drift accumulates.

## 2. Stress (SBCCI 2026 values, whole run)
- Die means: BB 107.73 °C, PID 117.04 °C. Errors vs target: −7.27 / +2.04 °C.
- ⟨AF⟩ at 0.7 eV and 55 °C: 31.1 vs 51.3, a ratio of 1.65× [AFratio].
  - Over 0.5–0.9 eV the ratio is 1.4–1.9×.
  - Over 0.1–0.3 eV it is 1.08–1.24×.
- Ripple adds 1.0 % to ⟨AF⟩ (Jensen 1.1 %). The mean shortfall alone gives 1.66×.
- Error budget at ±5/10/20 %: 0.9/1.8/3.4 °C. Sensitivity: about 5.4 % of AF per kelvin.
- Air held equal: the PID oven ran +3 °C above the dial. Die-per-air gain 0.97–1.81.
  - The 3 °C trim accounts for 1.17–1.35×.
  - The remainder is 1.22–1.41× (1.40× at gain 1).
  - Assumptions: the thermostat's air averaged its dial (not logged); the gains are closed-loop estimates;
    a shifted die-to-air offset is not excluded.
- Equivalent hours (SBCCI 2026, AF at mean T × 23.08 h): 711 / 1,182. Not printed in the
  current text; if a reviewer asks, quote these numbers.

## 3. The paired runs (fixed wording)
- **Shared:** board, oven, sensor, 50-inverter chain, 115 °C die target, 1.3 V on die.
- **BB-23:** thermostat at its 80 °C dial, supply trimmed in software in 5 mV steps, 0.5 Hz log,
  April 2025, then-unstressed device. It is the first day of BB-164.
- **PID-23:** oven set by hand to 83 °C in the first minutes (all setpoint changes fall in the first
  232 s of the log), supply fixed at 1.45 V, 1 Hz log, January 2026. It had no outer loop: the
  outer loop entered the code on 2026-05-16 (`2070e38`).
- **PID-214:** 16-bit adder, 125 °C, 1.4 V, May 2026. Supply loop active. Outer loop steps the
  setpoint by 1 °C every 30 min, beyond ±3 °C, plus two manual bursts.
- **Never write:** "differ only in thermal-control architecture" or "identical commands".

## 4. Fast time scale
- 96 % of the cycle's effect is removed at its peak (cycle 2.8 °C near 11 min).
- Residual at the sampling interval: 1.24× (0.904 / 0.726 cnt, SBCCI). At a common 2 s: 1.30×.

## 5. Floors (median HDEV over 1–4 h)
- BB-23: 0.045 cnt. PID-23: 0.040 cnt. Ratio 1.13×, inside the same-bench spread of
  BB-164's 23 h segments (0.031–0.055 cnt). Their equality is neither confirmed nor excluded.
- PID-214: 0.250 cnt (0.32 cnt over 6–30 h). That is about 6× BB-164 in ps and
  6.5× in counts. It is not a bench ranking.
- PID-214 with the 3 h after each step masked (39 % of the log): 0.15 cnt. The steps account
  for part of the excess, not all.
- Residual change near steps vs elsewhere: 0.26 vs 0.14 cnt, p < 0.01 by circular-shift permutation
  (exact p 0.006 and 0.008). This is an association, not a demonstrated cause.
- PID-23 has the smallest hour-scale wander of the four logs (0.09 °C).
- The slow residual is explained at most R² ≤ 0.25 by T, air and dT/dt. The floor's source is open.

## 6. Drift (PID-214, T and V regressors)
- −18.3 m cnt/h, 95 % interval −22.1 to −14.4. About 7.8 ps/day; total 3.9 cnt, about
  70 ps.
- Power-law exponent n = 0.35 (2 h blocks; apparent). The wording is fixed: "consistent with, though not
  diagnostic of, BTI".
- A floor-limited error model widens the interval 1.4-fold, and it still excludes zero.
- With other regressor sets: −5.1 to −14.6 m cnt/h. With supply voltage regressed out, the drift is below the
  ~10 m cnt/h this run resolves.
- Readout (XADC) drift is not excluded: the air allows it, while the current allows only 13 %.
- BB-164 drift: −6.0 m cnt/h.

## 7. Detection time
- White-noise bound, Eq. 5: PID-214 19.5 h; BB-164 12 h.
- **Headline (floor-aware estimators only):** PID-214 about 91–149 h, the bench as run; BB-164
  54–75 h. The floor stretches the run 4.5–7.6× on both logs, computed from the printed values
  (54/12 and 149/19.5) so a reader's arithmetic reproduces it.
  In the abstract: "4.5–7.6 times … on both long logs (91–149 h on the new run)".
- The long-run variance (66–96 h; BB-164 44–93 h) assumes short memory and is "shown for
  comparison". It is NOT called a lower bound, because its upper values exceed the quoted range.
  It stays in Table 1 and is never the headline.
- PID-214 with the steps masked: 71–111 h, with the masked log analyzed as separate segments.
- After removing the fitted drift, the 6–30 h level moves from 0.32 to 0.31 cnt.
- Simulation check: 300 runs of flicker noise matched to the 1–4 h floor, plus a linear drift. A
  *different* detector (the least-squares slope reaching three times its noise-only spread) gives
  122 h, against the rule's 116 h. Never write "independent".
- First day: a −74 m cnt/h slope is only a 2.0σ reading. 34 h windows: 30 % have the wrong sign.
- **Never resurrect:** "14 h" (old BB-164 sequential test), "34 h" (V1), "16 h", "z = 8.1",
  or "three independent readings agree".

## 8. Bench gain on detection (conditional; never a headline)
The gain holds only if the floors match, which is untested. It is up to 1.65× at 0.7 eV,
1.22–1.41× with the air held equal, and 1.08–1.24× at BTI activation energies.

## 9. Scope and standards
- One 28 nm board: within-device results.
- Overstress: 1.3–1.4 V is above the absolute-maximum rating. The XADC read above 125 °C in 51 % of
  PID-214's samples. The paired runs' 115 °C is below A108's default 125 °C.
- The sizing rule concerns noise statistics. Absolute rates and AF do not transfer to product burn-in.
- No compliance claim. MIL-STD-883 is no longer cited.

## 9b. Wording fixed in V11
- GPS: "clocking-path drift, against which Sobas and Marc used a GPS time reference". Never
  "removed"; always "Sobas and Marc"; the reference year is 2024.
- Overstress: "the sizing method transfers, but the floor values, drift rates, and acceleration
  factors may not carry over to product burn-in".
- Floor ratio in counts: "6.5-fold lower in counts"; in ps: "about 6× … in picoseconds of slack".
- Abstract: "often sized from the sample-rate noise".

## 9c. Added in V12
- CORRECTED (V12.2, neutral wording): detection paragraph only: "with the Allan floor, about 10 % higher for
  flicker noise, the rule gives 138 h". There is no "optimistic" sentence in the primer. Theory: (8 ln2 − 3 ln3)/(4 ln2) = 0.81 in variance, 0.90 in deviation;
  simulated 1/f noise gives 0.90; our logs give 0.85–0.94. The earlier "within 1 %" was WRONG (wrong
  formula). PID-214's Allan floor (0.30 cnt) gives 138 h, inside 91–149 h; the text states this.
- Fig. 2 uses the overlapping estimator. The tolerance is a one-sided "shortfall tolerance".
- Die-to-air offsets (34.1 vs 31.1 °C) and the 1.30× ratio at a common 2 s are restored.
- The SBCCI-extension statement appears once, in the opening; the footnote was removed.

## 9d. Planned reply if a referee calls the rule's validation circular (not in the paper)
Run an injection test: add a known linear (and power-law) drift to the real detrended residuals of
PID-214 and BB-164, and measure when the least-squares slope reaches 3× its noise-only spread,
against the rule's prediction. This needs only existing data and about a sentence in the reply
plus one in the revised text.

## 10. Open items (not edits to the claims)
- Co-author bios. Script total is now 4,583; keep ≤ about 4,600 with complete bios as a safety margin,
  in case an editor counts captions as text.
- SBCCI 2026 reference: pages and DOI.
- Check the Keane et al. abstract (reference-path claim).
- Header "Special Issue: SBCCI 2026": confirm against the invitation.
- Code and data: "available from the authors" unless a DOI is created.
