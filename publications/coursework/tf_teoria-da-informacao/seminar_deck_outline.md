# Seminar deck outline — TF Teoria da Informação (TIP7266)

**Talk:** Information-Theoretic Characterization of Aging Information and Noise in On-Chip Slack Sensors
**Budget:** 15 min (~14 slides, ~1 min/slide + Q&A). Numbers are from `latex/generated/values.tex` — keep them in sync by re-running the pipeline, never retype.
**Rubric anchors:** problem/objectives up front (item 02), methodology tied to course topics (item 03), clarity of argument (2.0), honest answers (1.5). Each slide tags its *núcleo* in **[brackets]**.

---

### 1 — Title (0:15)
Title, name, discipline, advisor. One-line hook: *"We re-express an aging sensor's noise as a communication channel and measure aging information in bits."*

### 2 — Problem & objective (1:00) **[N1: limits of communication]**
- Prior work measures environment→slack contamination with linear **R² = \valRsqLinear**.
- Two flaws: (i) captures **only linear** dependence, but the physics is non-linear (Arrhenius in T, super-linear in V); (ii) "variance explained" has **no transferable unit**.
- **Objective:** treat the slack sensor as a noisy channel and re-express contamination, correction, and recoverability in **bits**.

### 3 — The channel model + the data (1:00) **[N1, N2: entropy]**
- One equation: **S = S_aged(t) − Δ_PVT(T,V) + ε_q** (transmitter / channel noise / receiver = RUL).
- Device A: **\valDurationHours h**, **\valPostSoakSamples** post-soak samples @ 1 Hz, **\valSlackLevels** slack levels, **H(S) = \valHs bits** total uncertainty budget to split.

### 4 — ★ PUNCHLINE: mutual information replaces R² (2:00) **[N2: mutual information]**
- **I(S;T,V) = \valMIstv bits** (binned), **\valKSGstv bits** (KSG) — own CIs overlap only narrowly; a characterized estimator gap, not agreement.
- vs linear-equivalent of R²: **\valMIlinEquiv bits → measured exceeds it by \valMIexcessPctBinned–\valMIexcessPctKSG %.**
- Surrogate null floor p95 = **\valMInullFloor bits → \valMIfloorRatio× the floor** = real, not bias.
- **Honesty update (2026-08-18):** this excess does NOT survive detrending (\valMIexcessPctDetrended% on the reversible series) — see the honesty-caveats slide.
- *Say out loud:* "That excess is real, but on the reversible series alone it doesn't survive — so what we can claim is that MI has no linearity blind spot, not that we've proven this specific coupling is non-linear. That's still the contribution."

### 5 — The honesty linchpin: n_eff (1:00) **[N4: inference; autocorrelation]**
- 768,884 raw samples is **misleading**: τ_int = **\valTauInt s** → **n_eff = \valNeff**.
- Every CI, the surrogate floor, and the Bayesian fit use n_eff — not the raw count. *This is a methodological selling point; lead with the honesty.*

### 6 — PVT correction = denoising + aging recovery (1:30) **[N3: denoise; N4: OLS/MLE/MDL]**
- Reversible coupling **\valPreMIrev → \valResidMI bits (\valMIreductionPct % removed)**; MDL selects the **\valCorrModel** model.
- Key result: stripping PVT **exposes** aging — corr(S,t) **\valCorrStRaw → \valCorrStCorr**. (Figure: `fig_correction.pdf`.)

### 7 — Effective resolution & alarm (1:30) **[N1: capacity; N3: BSC]**
- SNR **\valSNR** → **C = \valCapacityBits bits → \valCapacityStates distinguishable aging states**.
- BSC aging alarm: 1 h ≈ coin flip; **\valBSCwindow h → C_BSC = \valBSCcap bits** (near-perfect). (Figure: `fig_capacity_rul.pdf`.)

### 8 — RUL detectability bound (1:30) **[N4: CRLB, Bayesian]**
- CRLB: min detectable rate **\valMinDetectRate m-cnt/h**, min observation time **\valMinObsTime h** (explains why prior ~23 h runs couldn't separate aging).
- Bayesian slope **\valBayesSlope m-cnt/h, 95% CrI [\valBayesSlopeLo, \valBayesSlopeHi]**, P(slope < 0) ≈ **\valBayesPaging %** (reading as aging conditioned on the single-device identification assumption). *Frequentist = Bayesian → robust.*
- *Frame as a bound + methodology, NOT a lifetime prediction.*

### 8b — RUL as a distribution: Wiener/Kalman (1:00) **[N4: sequential Bayesian estimation, stochastic processes]**
- Same corrected residual, second estimation route: block-average to $n_{eff}$ points, Kalman/RTS-smooth a Wiener-process aging trajectory (denoising, continuously updated).
- Rate-noise MLE collapses to ≈0 — **independently agrees with the MDL "insufficient curvature" verdict** — smoothed rate −15.9 m-cnt/h, consistent with the CRLB/Bayesian −18 m-cnt/h.
- Closed-form **Inverse-Gaussian RUL distribution** (not just a bound): mean/median 52.9h/8.0h at $D=\sigma_{noise}$; 81.3h/17.5h at $D=\sigma_{signal}$ — heavy right skew, largest exactly in the low-SNR regime of slide 7. (Figure: `fig_wiener_rul.pdf`.)
- *Say out loud:* "Same estimation toolbox, asked sequentially instead of once: not just when aging becomes detectable, but the full probability distribution of when it reaches the next resolvable level."

### 9 — Bench fidelity: KL / JS (1:00) **[N3: KL, JS divergence]**
- **Different device (Device B)** — say this explicitly. SBCCI vs PID bench.
- **KL(SBCCI‖PID) = \valKLsp bits vs KL(PID‖SBCCI) = \valKLps bits** (asymmetric → not a metric); **JS = \valJSbench bits**.
- Empirical > Gaussian closed form → non-Gaussian heavy tails. (Figure: `fig_kl.pdf`.)

### 10 — Blind source separation: ICA (1:00) **[N4: ICA, negentropy]**
- Model-free ICA recovers an aging component matching the regression at **|corr| = \valICAagingScorr** — using none of the measured T,V coupling.
- Strongly non-Gaussian (kurtosis +\valICAkurtAging / +\valICAkurtThermal); **partial** separation (residual MI \valICAresidMI bits). *Corroborative, reported honestly.* (Figure: `fig_ica.pdf`.)

### 11 — Honesty caveats (0:45) **[rubric item: honest answers]**
Single aging device & single regime → RUL is a detectability *bound*, not a validated prediction · n_eff ≪ n · capacity is an effective-resolution heuristic · ICA corroborative, not clean unmixing · KL is a **separate device**, never mixed with Device A.

### 12 — Contributions & takeaway (1:00)
- A **transferable noise metric in bits** (MI) that sees non-linear coupling R² misses.
- A **principled definition of burn-in quality** = minimize I(S;T,V).
- A sensor **resolution limit** + an **honest RUL bound** + a **model-free aging recovery (ICA)**.
- Closing line: *"R² says the environment explains 74% of the variance. Information theory says it writes 1.13 bits into every reading — and we can remove 93% of them. Bits transfer; variance fractions don't."*

---

### Backup slide — núcleo → result map (for Q&A, rubric item 03)
| Núcleo | Tool | Result on slide |
|---|---|---|
| N1 Limits | channel model, capacity, source-coding bound | 3, 4, 7 |
| N2 Measures | H(S), H(S\|T,V), **I(S;T,V)** | 3, 4 |
| N3 Transmission/divergence | denoise, **KL/JS**, BSC | 6, 7, 9 |
| N4 Complexity/estimation | MDL, OLS/MLE, **CRLB, Bayesian, ICA** | 6, 8, 10 |
| Foundations | n_eff, block-bootstrap, surrogate null | 5 (used throughout) |

### Backup slides to have ready
- Bin-count sensitivity / KSG-vs-binned table (robustness questions).
- Why MDL picks linear at this stress point (the non-linear model removes only \valResidMInl vs \valResidMIlin bits).
- "Why not run bang-bang on Device A too?" → it would upgrade the bench claim to a within-device, in-bits result; out of scope for this single-regime study (the Device-B KL is the proxy).

### Delivery tips (aligned to the rubric)
- Spend the most time on **slide 4** (the contribution) and **slide 5** (the honesty) — graders weight clarity and honest answers.
- State problem → objective → structure within the first 90 s (slide 2).
- Every figure on a slide must trace to a script + the dataset (no orphan numbers).
