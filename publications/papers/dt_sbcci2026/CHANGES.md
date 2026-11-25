# Hybrid version (2026-11-06)

Base: `versions/2026-11-06_pathA_restructure/` (new storyline: averaging time, Allan/Hadamard,
primer). Ported from `versions/2026-11-06_pathB_iterate/` and the four cross-reviews.
The PATH A change log is in `versions/2026-11-06_pathA_restructure/CHANGES.md`.

## Build state
`make` passes: 4,979 / 5,000 words, 12 references, number audit OK, no overfull boxes, 6 pages.

## New analysis
- `analysis/hybrid_checks.py` → `generated/results_hybrid.json`:
  detection-time range (long-run variance over 4/8/16 h blocks × linear/power-law
  detrending; W* over strides 1–3 h with and without the 6 h window; Allan crossing on
  a 1 h grid), same-bench floor spread (23 h segments of bb164 and rca212), first-24 h
  slope, slow-residual attribution R², air drift at fixed T and V, die/air gain over
  block lengths and lags with the resulting setpoint-adjusted AF ratio range.
- `analysis/robustness.py` (from PATH B): joint S ~ T + V + t, full sigma.
- `derive.py`: macros DetLo/DetHi, LrvLo/LrvHi, AllanCrossFine/ThreeFine/RunFine/Nwin,
  EarlySlope/EarlyZ, SlowRtwo, AirDrift, GainMin/Max, AFratioGainLo/Hi, SegBB*/SegRCA*,
  FloorPs*, PenStressPowBlock, BetaJoint, SigFullRCA, AFperK.

## Text changes vs PATH A
- Causal claim removed: the hour-scale floor's source is "not identified" (slow residual
  vs die T, air, dT/dt: R² = 0.05); the outer loop no longer "creates" the floor.
- PID 23 h run described correctly: no outer loop existed in Jan 2026 (added 2026-05-16,
  `2070e38`); oven setpoint 83 °C set by the operator in the first minutes.
- Floor ratio 1.13 reported as within same-bench spread (bb164 23 h segments 0.030–0.048).
- Detection time stated as a range, 66–96 h ("three estimators of the same noise",
  not "independent"); Allan crossing on a fine grid (25/44 h, 88 h run, 5 windows).
- Early-run resolution restored: first 24 h give −74 m cnt/h at z = 8.1.
- Bad-control rule applied consistently (oven air also drifts 2.4 °C at fixed T, V):
  primary β = −18.3 (T, V); others are sensitivity; joint fit −18.4.
- Die/air gain as a range (1.0–1.8 → AF gap 1.22–1.41×), not a single 1.2/1.35.
- Power-law exponent n = 0.35 with the ΔBIC of the same (2 h block) fit.
- Equivalent hours labelled (AF at mean die T, thermal only); "relative to the PID bench".
- Standards: A108 "has the test specification state" (not "report"); 1015 is a screen;
  non-compliance stated (abs-max voltage; 115 °C < 125 °C default Tj).
- Prior art: Xilinx patent US 8,212,576 B1 (self-regulated burn-in) added; Skogestad
  reference dropped (SIMC cited via SBCCI 2026).
- From B: hysteresis/5.4 %-per-K sentence, SIMC-vs-tuned 100 °C figures, SBCCI 2025 DOI.
- Bench penalty: floors indistinguishable → penalty is the stress shortfall only.
- Fig. 3: oven-air set grey (not primary), legend moved; conclusion rewritten.

## Round 2 (after the 4 cross-reference reviews of the hybrid)
- Early-day claim fixed: first 24 h slope −74 m cnt/h is a ~2σ reading against the
  24 h window-slope spread (36 m cnt/h), not z = 8.1 (HAC on a short window under a floor
  is miscalibrated). Intro clause "first day resolves" removed.
- Bench penalty fixed: under a floor, detection needs a fixed accumulated drift, so the
  penalty is the AF ratio for any power law (1.65×, or 1.22–1.41× setpoint-adjusted);
  the wrong 1.19× (AF^n) removed.
- Allan reading taken at the declared 1–4 h floor: 3σ at 58 h windows → 116 h run;
  detection range now 66–116 h ("tens of percent sampling error" stated).
- Floor segments recomputed with per-segment PVT fits (0.031–0.055 cnt); "indistinguishable"
  → "not resolved apart"; the 23 h BB run is the first segment (stated).
- Slow-residual attribution with fast-band sensitivities: R² ≤ 0.25 ("explains little").
- Air vs current as thermometers disagree: a drifting XADC reading is not excluded.
- Standards/reliability: Tj target 125 °C = Artix-7 absolute-max Tj (stated); "by default"
  for A108; Arrhenius wording (BTI voltage-driven); E_a 0.1–0.3 eV → 1.08–1.24×;
  "is verified most directly by die telemetry"; "set the die's mean from die telemetry".
- Editorial: PVT expanded; "autocorrelation-robust" replaces HAC in text and figure axis;
  VIF sentence and "slowing between halves" cut; roadmap paragraph shortened; Fig. 2
  caption colours; Fig. 1 caption gain range; Eq. (4) spacing fixed; Fig. 3 at 0.94 width.
- Build: 4,918 / 5,000 words, 6 pages, no overfull, audit OK.

## Round 3 (after the second 4-reviewer pass; scores 7.0 / 7.5 / 7.9 / no blocker)
- Detection upper bound: the long run's residual HDEV rises from 0.25 (1–4 h) to 0.32 cnt
  (6–30 h); that level gives a 149 h run. Range now 66–149 h; Table 2 shows 116/149;
  "flattens into a floor" → "reaches a floor".
- Autocorrelation-robust interval: a floor-limited error model widens it 1.4-fold; zero excluded.
- Tj: die above the 125 °C absolute maximum in 51 % of samples (peak 134 °C), stated.
- Penalty: "drift accumulates in equivalent time"; "about"; last sentence rewritten.
- First day: "first calendar day … only a 2.0σ reading against the 36 m cnt/h spread".
- Thermometers: "same sign and size"; gain printed 0.97–1.81; IV estimate (2.6) mentioned.
- Sobas GPS time reference cited against the clocking-path candidate.
- Conclusion: "die telemetry, not the chamber setting"; long-run mean within +0.05 °C;
  checklist adds the long-run trajectory, E_a 0.1–0.9 range, −5.1 to −18.4 across sets.
- Editorial: "as a function of averaging time"; bang-bang sentence; "requires … to state";
  "to leading order"; primer "three times the floor"; Eq. (4) on two lines; Table 2 row;
  bibitems in citation order; JESD22-A108G Nov. 2022; "after the soak"; "a day or so".
- Cuts: re-zeroing detail, abstract repetitions in the opening, lag sentence, 100 °C SIMC
  numbers, duplicate limitation. Build: 4,921 / 5,000 words, 6 pages, audit OK.

## Round 4 (author request: run names, related work, acronyms)
- Runs named BB-23, PID-23, BB-164, PID-214 (Table 1 "Name" column, text, captions, figure legends).
- New "Related work" section (FPGA aging sensors; burn-in thermal practice and standards;
  drift detection in noisy records) absorbing the opening's prior-art paragraph; no new refs.
- Acronyms expanded at first use: FPGA, PID, MMCM, VCO, XADC, SIMC, CUT, AF, ADEV/HDEV, BIC, BB.
- Cuts to stay under budget (abstract, standards wording, duplicate citations, limitation wording).
- Build: 4,994 / 5,000 words, 6 pages, audit OK. Bios still need room (see open items).

## Round 5 (author decision: treat the 23 h pair as comparable)
- BB-23/PID-23 presented as a matched pair (same board, oven, sensor, circuit, die target,
  on-die voltage), each bench "operated as a lab would run it"; the 83 °C PID setpoint is part of
  the PID practice ("to center the die on its target"); "not an A/B test" removed.
- 1.65× stays the headline as a comparison of bench practices; the air-equal decomposition
  (1.40×; 1.22–1.41×) is a sensitivity.
- "The bench penalty" → "What the bench buys": PID practice detects ~1.65× sooner (1.22–1.41×
  with air equal); sample-rate noise matters for short-window decisions (AVS), not run length.
- Limitations: one sentence (nine months apart, different stress history).
- Not written (would be false): "differ only in thermal-control architecture", omitting 83 °C/fixed supply.
- Build: 4,969 / 5,000 words, audit OK.

## Round 6 (linearity with SBCCI 2026; caveats consolidated; SLM purpose)
- Abstract and conclusion now carry the time-scale chain: seconds-minutes (PID lowers sample-rate
  noise, which serves short-window SLM functions such as AVS calibration), hours (a floor neither
  bench removes, sets 66–149 h), run length (mean die T sets drift accumulation; PID practice
  should detect up to 1.65× sooner, by the floor/AF scaling).
- Map sentence opens the noise section; "What the bench buys" cites AVS margins [niemann].
- Caveats moved to Limitations with short pointers in place: low E_a (1.08–1.24×), floor source
  candidates (gradient, clocking path vs Sobas GPS), XADC drift not excluded, inverter→adder transfer.
- "Which drift?" ends with: consistent with aging in sign and form; current allows only 13 %;
  a thermometer beside the path would settle it.
- Conclusion adds SLM deliverables (noise figures by averaging time for AVS margins; validation
  runs sized from the floor before drift feeds RUL estimates).
- Build: 4,996 / 5,000 words, 6 pages, audit OK.

## Round 7 (quick 2-reviewer pass: narrative 8.1; rigor 7.0 → ~7.7 with fixes)
- Rigor regressions from Round 6 fixed: "Which drift?" restores the air-as-thermometer reading
  (2.3–4.3 °C, enough for the whole drift) next to the current's 13 %; "up to 1.65×" replaced by
  "1.22–1.65× if the floors match" (abstract, conclusion) and "would reach … if they are equal"
  (body); "operated as a lab would run it to reach that target" replaced by how each bench was run
  (thermostat at its 80 °C dial chosen a priori; PID raised by hand to 83 °C to center the die).
- Neutral anchor to SBCCI: "That paper reports them by their nominal configuration; the logs
  record how each bench was run".
- Restored: air-equal assumption (BB-23 logged no air); stress-history assumption tied to the
  detection gain; ADEV at a common 2 s (1.30×); "continuous die loop" future step.
- Narrative: intro states SBCCI's two numbers and asks which matters and at what time scale;
  abstract ordered seconds → hours → run; "do not resolve apart" → floors agree, bench acts through
  the mean at hour scales; robustness before practice in the air-equal sensitivity.
- Table 1 removed (names defined in "Logs"); "Week-1", CUT and the IV-gain aside removed;
  m cnt/h defined; PSU → supply in Fig. 3; AVS wording "can serve"/"would matter".
- Build: ~4,880 / 5,000 words (≈120 free for bios), 6 pages, audit OK.

## Round 8 (author's "Sugestões de melhoria — paper D&T v5")
- (1) BB-164 detection measured with the same estimators: white 12 h; long-run variance 44–93 h;
  window spread 75 h; Hadamard 54/59 h → 44–93 h for its −6.0 m cnt/h drift. New BB-164 column
  in Table 1 (detection), caveat: inverter chain, then-unstressed device (favors the thermostat).
  The old "14 h" (sequential HAC on BB-164) is not in this version; it is superseded by the
  floor-aware estimators.
- (2) Long-log floor mismatch addressed in one paragraph (PID-214 vs BB-164: cnt, ps over whole
  log, wander 0.80 vs 0.17 °C, confounders). New test: within ±3 h of PID-214 setpoint steps the
  median hour-to-hour change is 0.73 vs 0.16 °C (die) and 0.26 vs 0.14 cnt (residual), Mann-Whitney
  p < 0.001; stated as association (the loop also responds to the die), pointing to a continuous
  loop. Abstract condition moved up front ("if the benches' floors match, …").
- (3) Title → "Averaging Time Defines When On-Chip Sensors Resolve Burn-In Drift"; section
  "How long until drift is resolvable"; abstract "resolving aging drift"; conclusion: the sizing
  rule holds whatever the drift's origin.
- (4) Detection paragraph opens with the sizing rule (2×3√2·floor/|β| → 116–149 h); estimator
  detail left to Table 1; first-day 2σ remark merged into the 34 h windows sentence.
- (5) Residual excess after the cycle is spread over short averaging times; −5.1 (air + voltage)
  cited in text; ps floor labelled "over each whole log"; checklist E_a range unified
  (0.5–0.9 eV, with 0.1–0.3 eV in parentheses); white-noise bound printed as 19.5 h.
- Build: 4,940 / 5,000 words, 6 pages, audit OK (0.001 whitelisted as reported threshold).
- Follow-up: added "The PID loop itself is not the issue: PID-23, run at a fixed setpoint, had the
  smallest hour-scale wander of all four logs (0.09 °C) and a floor matching BB-23's." → 4,969 words.

## Round 9 (author's final text corrections)
- BB-164 sentence: resolves sooner than PID-214 despite a 3-fold slower drift because its floor is
  6.5-fold lower in counts; confounders listed; "the long logs do not rank the benches".
  Abstract: "if the benches' floors match, as our paired runs allow but our long runs do not test".
- Setpoint decomposition: the 3 °C trim accounts for 1.17–1.35× of the 1.65×; the remaining
  1.22–1.41× needs a thermostat running below its dial or a cycling mechanism (not separable).
- SBCCI late-window slopes: "used short-memory errors; against the floor, a day-long run shows a
  slope but does not establish a drift."
- Estimators "span 66–149 h, through sampling error and the different tests they apply".
- Setpoint-step association now tested by circular-shift permutation of the step times
  (2,000 shifts): p ≤ 0.007 (die 0.006, residual 0.004); Mann-Whitney no longer quoted.
- Cuts: abstract tutorial line, "The two circuits differ", σ/τ parenthetical.
- Build: 4,996 / 5,000 words, 6 pages, audit OK.

## Round 10 (soft rewrite for coherence and readability; author request)
- One line of argument: SBCCI measured two bench effects (stress, sample-rate noise) and called
  for longer campaigns; this article is that campaign and asks which effect sets run length.
  Answer by time scale: minutes (correction removes ripple; PID's lower noise helps short-window
  decisions), hours (floor sets run length), whole run (mean die temperature sets drift rate).
- Density cut: one key number per point; regressor list, permutation details, ps comparisons,
  BIC, early-day z, window details trimmed or moved to captions/table. Drift also in ps/day (7.8).
  Floor rule moved into the primer; footnote shortened; roadmap folded into the opening.
- All caveats moved to one Limitations paragraph (scope, floor equality, aging state, low E_a,
  air-equal assumptions incl. shifted offset, floor source, XADC vs current thermometers,
  apparent exponent, flat-floor assumption, standards non-compliance).
- Reviewer fixes: "PID practice … ~1.65× at 0.7 eV" (not "centering"); air-change gains;
  residual jumps with die at setpoint steps (p < 0.01, permutation); "ripple's convexity adds
  little"; Fig. 3(b) caption: intervals not floor-widened, rates < ~10 m cnt/h unresolved;
  Fig. 2 caption: PID-214 level is not a bench ranking; "set by hand to 83 °C"; "Over minutes";
  conclusion scoped to PID-214 with units; Sobas/Xilinx credited for the continuous die loop;
  "operating life, in JESD22-A108 terms".
- BB-164 kept only where it supports the thesis: same-bench floor spread, the sizing rule on a
  second log (three to eight times the white-noise time), and same supply trim without a raised floor.
- No cover-letter declaration (author decision); facts (83 °C, fixed 1.45 V supply) stated once.
- Build: 4,331 / 5,000 words (≈670 free for bios), 5 pages, audit OK.
- Snapshot before this round: drafts/2026-11-06_before_softrewrite/.

## Round 11 (final pass; freeze)
- Detection headline: floor-aware estimators only, about 91–149 h (BB-164 54–76 h, 4.5–7.7× the
  white-noise time on both logs). Long-run variance kept in Table 1 as a short-memory lower bound.
- New analyses (analysis/hybrid_checks.py):
  - PID-214 floor with 3 h after each step masked (0.15 cnt; rule 71–111 h);
  - HDEV after power-law removal (6–30 h level 0.31 vs 0.32 cnt);
  - Monte Carlo of the floor rule (independent least-squares detector 122 h vs rule 116 h).
- Restored from V8:
  - conditional bench range with BTI (1.08–1.24×);
  - BB-164 drift and why it resolves sooner;
  - factor-2 rationale; curvature-leak note; 1.4× widened interval;
  - first-day 2σ; "association, not cause"; τ_int definition;
  - "not diagnostic of BTI";
  - few-windows caveat (from V7).
- New:
  - reference-path sensors (Keane et al. silicon odometer) in Related work; MIL-STD-883 dropped;
    Sobas 2022 replaced by Sobas & Marc 2023 (GPS and 0.05 °C verified there);
  - "what's new" sentence; overstress-transfer sentence;
  - V std-dev run labels; Table 2 drift range fixed;
  - Fig. 3(b) resolution threshold; shorter captions;
  - method-led 3-sentence abstract;
  - references reordered by first citation.
- FROZEN_CLAIMS.md written. Build: 4,583 / 5,000, 6 pages, audit OK.
- Snapshot before this round: drafts/2026-11-06_V9_before_finalpass/.

## Round 12 (V11: last text pass after V10 reviews; scores V10 7.3 and 6.5–7.0)
- Abstract: "4.6–7.7 times … on both long logs (91–149 h on the new run)"; "often sized".
- BB-164 range 54–75 h, matching Table 1; ratios properly rounded.
- Table 1 caption: long-run variance "shown for comparison", not "lower bound".
- Detection: "bench as run" (91–149 h) vs setpoint steps masked (71–111 h); after-detrending
  level 0.32 → 0.31 cnt; simulation specified (300 runs, matched flicker, linear drift,
  "a different detector").
- Floor ratio units stated; masked log handled as separate segments.
- GPS "used a GPS time reference against"; "Sobas and Marc"; ref year 2024.
- Overstress sentence softened; conclusion "a floor present in every log".
- Cuts: intro numbers, "or at the ambient", 2 s ADEV aside, offset numbers, "Which drift?"
  detail moved to the Fig. 3(b) caption, future-steps sentence, "Direct questions" line
  (inserted by the editor), Fig. 1 caption.
- Build: 4,517 / 5,000 (CEDA count), 5 pages, audit OK. V10 snapshot: drafts/2026-11-06_V10_final_pass/.

## Round 13 (V12: minor fixes after the final reviews; V11 scores 7.5 / 7.0 / 6.0 cold)
- Ratio 4.5–7.6× from the printed values; typo "−5.1 to −14.6"; Fig. 1 "1.2 from PID-214".
- Restored the 1.30× at a common 2 s and the die-to-air offsets (34.1 vs 31.1 °C).
- Shorter Fig. 2 and Fig. 3 captions.
- Hadamard ≈ Allan floor for flicker noise (within ~1 %); overlapping estimator noted;
  "shortfall tolerance".
- Duplicate extension footnote removed.
- Injection test kept as a planned referee reply (FROZEN_CLAIMS.md §9d), not added to the paper.
- Build: 4,540 / 5,000, 5 pages, audit OK. V11 snapshot: drafts/2026-11-06_V11_last_pass/.

## Round 14 (V12.1: correction after an external comment)
- The V12 sentence "Hadamard and Allan floors agree within about 1 %" was wrong: for flicker noise
  HDEV ≈ 0.90 × ADEV (theory; 1/f simulation; our logs 0.85–0.94). Replaced by "the Hadamard floor
  sits about 10 % below the Allan floor, so this rule is slightly optimistic", and the detection
  paragraph now gives the Allan-floor variant (0.30 cnt → 138 h, inside 91–149 h).
- Build: 4,550 / 5,000, 5 pages, audit OK. Package regenerated.
- V12.2: neutral wording (author choice): the primer sentence was removed; the detection paragraph says
  "with the Allan floor, about 10 % higher for flicker noise, the rule gives 138 h".

## Open items for the authors
- Read in full: Sobas 2022, JESD22-A108G, MIL-STD-883-1 Method 1015; cite the edition read
  ("w/Change 2, Apr. 2024" or "base issue, 2019").
- Bios: ~80 words of budget left; complete bios need ~100–180, so expect ~50–100 more cuts.
- Co-author bios (CEDA requires position, degree, interests, e-mail).
- Confirm the 214.6 h run used the `9d72faa` bitstream (sensor re-zeroing statement).
- RECONCILIATION template item 13 ("outer loop raised it") is wrong for Jan 2026.

