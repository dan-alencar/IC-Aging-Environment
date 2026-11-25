<!-- AUTO-GENERATED from analysis/RECONCILIATION.template.md by analysis/derive.py -->
# Reconciliation of cross-document discrepancies

Every value below was recomputed from the raw logs in `data/campaigns/` by `analysis/` (`run_analysis.py`, `pid_bench.py`, `derive.py`). Numbers quoted here are for audit and are **not** typed into the manuscript, which reads `generated/values.tex`.

**Common definition used in D&T (all runs):** drop link-down rows (S, T or V = 0), exclude the first 1 h as thermal soak, and compute every statistic on the remaining window. The source documents mix full-file and post-soak statistics. That one fact explains items 1, 2 and 5.

Sources: **SBCCI26** = conference paper (`publications/papers/gsem/Quantifying_…pdf`); **JICS** = unpublished draft (not cited); **TCC** = thesis (not cited); **TIP** = TIP7266 coursework (`publications/coursework/tf_teoria-da-informacao/`); **Draft** = contingency draft of 2026-11-04.

---

### 1. ΔT: 9.31 vs 9.37 °C
- **Cause:** SBCCI26 Table II (107.73 / 117.04 °C) is computed on the **full** files, so their difference is 9.31 °C. The abstract and text value of 9.37 °C is the **post-soak** difference (107.76 vs 117.13 °C). SBCCI26 therefore mixes the two windows.
- **Chosen:** post-soak, ΔT = 9.37 °C. This is consistent with the 1 h soak exclusion stated in SBCCI26 Methods. The full-file value (9.31 °C) goes in the correction footnote.

### 2. Equivalent hours: 711/1182 vs 718/1184 h
- **Cause:** SBCCI26's 711 / 1182 h is **AF(mean T) × 23.08 h** on full files (reproduced: 711 / 1182). The draft's 718 / 1184 h is **⟨AF⟩ × 23.08 h** on full files.
- **Chosen:** the trajectory integral ∫AF(T_j(t)) dt over the whole run, soak included because the soak also stresses the die: 717 / 1,184 h. It differs from 718 only because the bang-bang log is 0.5 Hz and the integral uses actual sample spacing. ⟨AF⟩ is the right estimator; AF(T̄) under-states the bang-bang ripple contribution.

### 3. Long-run duration: 212.6 vs 214.6 h
- **Facts:** 772,484 rows at 1.000 s cadence; 6 link-down rows. Raw span 214.58 h, post-soak span 213.58 h, 768,878 post-soak samples. TIP's 768,884 used a slightly different dropout rule.
- **Cause of 212.6 h:** JICS excludes "an initial transient of about two hours" (214.6 − 2 = 212.6).
- **Chosen:** report the run as 214.6 h logged (772,484 rows) and analyse 213.6 h after the common 1 h soak. "212.6 h" is no longer used, and the title/abstract say "214-hour" via macro.

### 4. Slack units: ps vs counts, and the step size
- **Facts from the CSV:** slack is an integer, 267–300 over the post-soak window (34 levels occupied, mean 278.46, σ 3.03). These are MMCM phase-step **counts**. JICS's "278.5 ± 3.0 ps within a 33 ps band" mislabels counts as ps (the band is 300 − 267 = 33 counts).
- **Step size depends on the bitstream:**
  - Inverter-chain design (Jan 2026 block design, `1414f7a`): MMCM VCO = 100 MHz × 9 = 900 MHz, so the step is 1/(56·f_VCO) = **19.84 ps**. This matches the papers' "19.85 ps".
  - RCA design used for the 214.6 h run (`clk_wiz_0_clk_wiz.v` at `9d72faa`, CLKFBOUT_MULT_F = 10): VCO = 1000 MHz, so the step is **17.86 ps**. `SENSOR_ARCHITECTURE.md` also states 17.86 ps.
- **Consequence:** the draft's "≈3.9 cnt ≈ 77 ps" used 19.85 ps. With 17.86 ps it is 3.9 cnt ≈ 70 ps.
- **Chosen:** counts everywhere, with a per-CUT step stated once. The April 2025 bitstream predates the repository; its step is assumed equal to the January 2026 inverter-chain design (same sensor IP). **Please confirm.**

### 5. σ(T_DUT) under PID: 1.25 vs 0.91 °C; mean 117.04 vs 117.2 °C
- **Cause:** same run, different windows. Full file: 117.04 / 1.246 °C (SBCCI26 Table II). Post-soak: 117.13 / 0.927 °C. The TCC's 117.2 / 0.91 and its bang-bang 108.2 / 2.63 are close to post-soak values (bang-bang post-soak 107.76 / 2.631 °C). The TCC's exact window wasn't recovered, and its 117.2 is 0.07 °C off the post-soak mean.
- **The PID σ is dominated by the first hour:** 1.25 → 0.93 °C once the soak is dropped. SBCCI26's 2.1× σ(T) ratio becomes 2.8× post-soak.
- **Chosen (first revision):** post-soak, 2.63 / 0.93. Superseded by the alignment decision at the end of this note.

### 6. TIP7266 attributing σ = 0.40 vs 3.29 °C to SBCCI
- Those are TCC **oven-air** values at 100 °C (Table 6), not SBCCI26 die values. The manuscript cites 100 °C figures only as oven-air, from this pipeline (3.38 / 0.38), never as SBCCI26 results.

### 7. JICS "PID control band 89.5–103.6 °C" and the ~50 h feature
- 89.47–103.62 °C is the full post-soak **oven-air** range (mean 93.94 ± 1.78 °C). The die was 125.07 ± 1.77 °C (range 117–134 °C).
- **The setpoint was not constant.** The DUT outer loop moved it 49 times across 91–99 °C.
- **Around 40–60 h the die cooled** to 123.7 °C mean while the oven sat near 92 °C. Slack rose accordingly (281.0 vs ~279.3 cnt). The outer loop then raised the setpoint stepwise from 91 to 99 °C over 44–102 h. This is the step visible in JICS Fig. 11A, a die-side disturbance (ambient or airflow), not a sensor event.
- **Exclusion test:** HAC slope with 45–55 h removed is −18.74 ± 1.94 m-cnt/h vs −18.27 ± 1.95 with all data. **No sub-window is excluded.**

### 8. Residual-σ ratio: "25 %" vs "~23 %"
- Raw OLS residual σ (SBCCI26 definition, post-soak) reproduces exactly: 0.904 / 0.726 cnt, ratio **1.245** (+25 %). SBCCI26's "~23 %" is not reproducible from its own table.
- D&T uses two clearly named quantities: the SBCCI26 raw residual (1.24, +24 %) and the **reversible** residual (1 h moving average removed, used for detectability), 1.31 (+31 %). The PID raw residual contains early-run drift, which the reversible one removes.

### 9. Reference [7] mis-attributed
- SBCCI26 and the draft cite "On the effect of aging on digital sensors" as Bidmeshki, Di Natale, Maurine, HOST 2020. The correct citation is **M. T. H. Anik, S. Guilley, J.-L. Danger, N. Karimi, *Proc. VLSID 2020*, pp. 189–194** (per the handoff). Its finding is that the sensor's **own aging** shifts its calibration, producing missed and false alarms, not that uncorrected PVT causes false alarms. The manuscript sentence is reworded accordingly.

---

## Further discrepancies found in Phase 0–2

10. **Different CUTs.** The 23.08 h pair and the 164 h Week-1 log use the 50-inverter chain; the 214.6 h run uses the 16-bit RCA. Same board (confirmed by authors). The draft's "same device and sensor" is true for the board and the sensor IP, false for the CUT. Cross-run transfers are limited to (i) the AF ratio, which depends on temperature only, and (ii) dimensionless noise ratios, under an explicit assumption.
11. **The bang-bang 23.08 h run is the first 23.08 h of the SBCCI 2025 Week-1 burn-in** (byte-identical prefix of `aging-plot-semana1.csv`), recorded in April 2025 on an unstressed device. The PID run is from January 2026, after the Week-1/Week-2 stress. The two runs therefore differ in prior stress history, not only in thermal loop. This is relevant to slopes, not to the stress and noise comparisons.
12. **Bang-bang logs are 0.5 Hz.** SBCCI26 and the draft say 1 Hz. All time constants are computed in seconds, and τ ratios in samples (equal-cadence comparison).
13. **PID 23 h oven setpoint was 88 °C falling to 83 °C during the soak hour and a constant 83 °C afterwards**, not "80 °C held continuously" as SBCCI26 states. The outer loop raised it, and the PSU commanded 1.45 V to hold 1.30 V on-die. The bang-bang log has no oven channel, so its "80 °C reached" cannot be checked.
14. **E_a range of the AF ratio:** SBCCI26's 1.44–1.92× is not reproduced. Post-soak gives 1.436–1.904 (1.43–1.90); full-file gives 1.433–1.898 (the draft's 1.43–1.90). The 1.92 is unexplained.
15. **Ripple contribution (second-order Jensen prediction 1.1 %, matching the exact value):** the draft's Gaussian approximation gave +1.0 % (bang-bang) and +0.2 % (PID). The exact trajectory gives 1.0 % / 0.2 % over the whole run (1.0 % / 0.1 % post-soak). The PID figure halves because the soak hour carried most of the PID variance.
16. **SBCCI26 late-window slopes** reproduce exactly (bang-bang −6.5 [−11.8, −1.2], PID −5.3 [−7.7, −2.8] m-cnt/h): the OLS residual is fitted on the post-soak window, with windows in hours since the run start.
17. **τ_int definition and a factor-2 error in the TIP/draft T_min.**
    - TIP's 314 s reproduces exactly (314 s), but it uses τ = 1 + 2Σρ (white noise = 1 sample) together with n_eff = n/(2τ) and Var(β̂) = 24σ²τ/T³. Those two formulas belong to Sokal's τ = ½ + Σρ convention (white = ½).
    - The mix double-counts the slope variance and inflates T_min by 2^(1/3). Re-run consistently, the TIP bound becomes 27 h instead of 34 h.
    - The draft's BSC formula √(2τ/w) used the TIP τ, so it is numerically equal to the correct two-window form √(4τ/w) with Sokal τ. The draft got the right capacity by compensating errors; the manuscript now writes the correct form.
    - TIP's τ is also the decorrelation time of the *uncorrected* slack minus a 1 h moving average, i.e. dominated by thermal PVT. The handoff specifies τ_int of the **corrected** residual (Sokal): 58 s on the adder, ≈ ½ sample (white) on both inverter-chain 23 h runs. With it the bound is 20 h.
18. **The white-noise bound is model-dependent.**
    - The corrected residual has slow wander. Its batch-means long-run variance grows from 464 cnt²·s at 15 min blocks to 7,793 cnt²·s at 8 h blocks, against 82 assumed by the bound.
    - With the 8 h long-run variance, T_min = 89 h. A sequential HAC test (cumulative slope, 3σ, Newey–West bandwidth ≤ 8 h) first and permanently resolves the drift after 16 h on the adder and 14 h on the inverter-chain Week-1 log. Both are earlier than the bound because both drifts are sublinear (power-law n = 0.32 and 0.24).
    - The manuscript reports all three in one table (method, assumption, value).
19. **Projected bang-bang detection penalty.**
    - Draft: raw σ ratio 1.245, equal τ, β ∝ ⟨AF⟩, giving 1.62×.
    - Now (after the alignment decision): SBCCI 2026 residual σ ratio 1.24; τ ratio 1.15 (both runs ≈ white, so it is poorly conditioned and used only for the upper end); AF ratio 1.65.
    - The aging law matters. Under β ∝ ⟨AF⟩ (linear drift in equivalent time) the stress factor is 1.40×. Under the fitted power law D ∝ (AF·t)^n with n = 0.32, the drift at fixed wall-clock time scales as AF^n and the stress factor is only 1.11×.
    - Reported range: 1.29× (equal τ, power law) – 1.62× (equal τ, β ∝ ⟨AF⟩) – 1.69× (adding the measured τ ratio). The middle value spans 1.47–1.77× over E_a 0.5–0.9 eV.
    - Remaining assumption: the inverter-chain noise ratio transfers to the RCA.
    - **The Week-1 thermostatic log resolves its own drift after 14 h**, faster than the PID adder run. It is a different circuit on an unstressed device whose early aging is fast, so it does not contradict the projection, which is made at equal aging rate. It does show that detection time depends on the device's aging state as much as on the bench. This is discussed in the main text.
20. **Per-regime residual MI is inconclusive.**
    - A quantization-only surrogate (integer-rounded linear model + white noise matched to the residual σ) produces 0.693 bits of residual MI on the PID 23 h run, more than the measured 0.335. That run's residual MI is an integer-slack artefact.
    - On the bang-bang runs the excess over the quantization surrogate is 0.05–0.07 bits.
    - Block-bootstrap intervals for residual MI are not reliable: resampling duplicates samples, which biases MI upward. They are not reported.
    - Following the handoff, the paper keeps MI to one sentence plus the adder headline.
21. **Hysteresis hypothesis not supported.** Bang-bang heating-minus-cooling residual gap is 0.11 cnt against σ ≈ 0.9 cnt. The S–T cross-correlation peak is at ≤ 1 sample lag. Adding dT/dt to the PVT model lowers the bang-bang residual σ by < 1 %.
22. **No independent readout control exists.** The logs contain no reference path or MMCM status. V_CCINT is the regulated variable. The PSU current residual (after T, V regression) rises by 0.041 mA/h, but it is strongly correlated with the slack residual at short time scales (self-heating), so it isn't independent. The paper says plainly that readout drift can't be excluded with the logged channels.
23. **PID bench (thesis) reproduction.**
    - FOPDT: the thesis used a two-point method (K = ΔT_final/u, θ at 2 % rise, τ at 63.2 % − θ, times from the step instant). This reproduces K = 1.56, θ = 150.6 s, τ = 1307.2 s exactly, and SIMC (τ_c = θ) gives Kp 2.78, Ki 2.31e-3 /s as in the thesis.
    - **The model fits poorly** (RMSE 5.1 °C): the response overshoots to 106.9 °C before settling at 103.2 °C, which no FOPDT can produce. A free least-squares FOPDT fit gives θ ≈ 371 s, τ ≈ 975 s. The paper presents SIMC as the *starting point* for tuning, which is all the thesis claims.
24. **100 °C comparisons.**
    - The thesis scripts use the last 30 % of samples, its text says the last 30 min, and the thermostat file it used is a trimmed copy (`Analysis_app/ModForno_…`, 3,672 rows).
    - The thesis σ values reproduce exactly under its script convention (3.29 / 0.40 / 1.33 °C). Its peak-to-peak (9.0 / 2.1 °C), |e|max (7.2 / 1.8 °C) and overshoot (5.2 / 0.0 °C) do **not** reproduce under any window or smoothing tried.
    - **Chosen:** original logs, last 30 min. Thermostat σ 3.38, p-p 10.5, |e|max 7.0 °C; tuned PID σ 0.38, p-p 1.8, |e|max 1.9 °C; SIMC σ 1.94 °C, overshoot 6.5 vs tuned 0.7 °C.
    - The tuned-PID run is `Final_Test_20260109` (the thesis σ matches it); `Final_Test_…20260111` is a repeat with σ 0.77 °C.

## Open questions for the authors
- (4) Confirm the April 2025 bitstream used the 900 MHz VCO (19.84 ps step).
- (24) Were the thesis's p-p / |e|max / overshoot computed from a smoothed or differently trimmed signal? If the script exists, it can be added.
- (11) Should the paper mention that the bang-bang run was on an unstressed device? Recommended: yes, one clause in the Evidence base.

## Independent review (Phase 4), 2026-11-05: what changed

A reviewer agent that hadn't seen the work recommended major revision. Addressed in the manuscript:
- **Bench asymmetry.** Only the PID bench has die feedback (an outer loop on the oven setpoint). This is now stated, and the unverifiable "die sheds heat during off phases" mechanism was removed.
- **Aging law.** β ∝ ⟨AF⟩ contradicts the fitted power law. The penalty is now bracketed (1.29–1.69×).
- **τ_int convention.** The factor-2 inconsistency was found and fixed (item 17), and the alarm SNR is now in its two-window form.
- **Changes from SBCCI.** All are in a generated table (Table 2), replacing the footnote.
- **Detection times.** One table (Table 3); "optimistic" was replaced by "model-dependent", and "aging is resolved" by "a drift is resolved", with the 49 setpoint moves disclosed.
- **Week-1 thermostatic log.** It resolved its drift after 14 h; this is now discussed in the main text.
- **Limitations.** Stress beyond datasheet absolute maximums; the SBCCI MIL-STD judgment is not repeated.
- **Figure 1 removed.** The argument chain is now one sentence, to fit the two new tables.

Rejected: "over the 5,000-word limit". `wordcount.py` already counts 200 words per float, and the total is within the limit.

## Alignment decision (authors, 2026-11-05): D&T stays loyal to SBCCI 2026

The authors decided that the D&T article will not present corrections to SBCCI 2026. It reuses SBCCI 2026's stated and computed values and its conventions. Implemented as follows:
- **Stress-delivery statistics** (mean and σ of die temperature, die error, ⟨AF⟩, σ(V), ripple, equivalent hours) are computed over the **whole run**, as SBCCI 2026 Table II actually did. They reproduce exactly: 107.73 / 117.04 °C, 2.64 / 1.25 °C, −7.27 / 2.04 °C, ⟨AF⟩ 31.1 / 51.3, σ(V) 6.1 / 3.6 mV, equivalent hours 711 / 1,182 (AF at the mean temperature × run length).
- **Regression, noise and detectability statistics** exclude the first hour, as SBCCI 2026 Table III did: R² 92.1 / 59.2 %, residual 0.90 / 0.73 cnt.
- **The manuscript states both windows truthfully** (whole run for stress, first hour excluded for regression). It never claims a soak exclusion for the stress table.
- **Not printed, because they are not reproducible from the stated means:** the 9.37 °C text value (the table means give 9.31 °C) and SBCCI's 1.44–1.92× E_a range (whole run gives 1.43–1.90). The manuscript gives the two means and "about 1.4–1.9×".
- **The bench noise ratio** used in the detectability projection is SBCCI 2026's residual ratio, 1.24. It is unchanged at a common 2 s sampling interval (1.24). The τ ratio is measured at that common interval (1.15).
- **New material** (the 214.6 h adder run, the 164 h Week-1 log, detectability, PID construction, 100 °C tests) is computed by this pipeline under the same conventions.
- **Facts that contradict SBCCI 2026 wording** (bang-bang logging interval, the PID outer loop moving the oven setpoint, the April 2025 history) are described neutrally where the new analysis needs them, without framing them as corrections. The manuscript does not claim anything false.
