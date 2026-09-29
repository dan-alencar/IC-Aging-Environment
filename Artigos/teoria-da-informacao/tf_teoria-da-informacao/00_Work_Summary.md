# Work Summary — Information-Theoretic Characterization of Aging Information and Noise in On-Chip Slack Sensors

This is the entry-point summary of the final project (TF) for **Teoria da Informação (TIP7266, PGETI/UFC, 2026.1)**. It records *what was used* — the data, the course concepts and how each was applied, the results, and the deliverables.

---

## 1. What the project is

It places an **information-theoretic measurement layer** on top of an existing low-cost accelerated-aging burn-in platform and its synchronized `(slack, T, V, time)` logs. Treating the on-chip slack sensor as a **noisy communication channel** (latent aging = transmitter; reversible PVT + quantization = noise; RUL estimator = receiver), it re-expresses the noise, the PVT correction, and the recoverability of aging information in the language of entropy, mutual information, divergence, channel capacity and estimation. No new silicon, sensor or oven — the contribution is analytical and methodological.

**Central upgrade over prior work:** replace the linear coefficient of determination $R^2$ — which captures only linear dependence and yields no transferable unit — with **mutual information in bits**, valid where the physics (Arrhenius in $T$, super-linear in $V$) is non-linear.

---

## 2. Data used

| Dataset | Device | Duration | Role |
|---|---|---|---|
| `Tentative_1_20260524_203756.csv` | **Device A** (aging device), DUT ≈125 °C / 1.40 V, PID | **214.6 h**, 768,884 post-soak samples @ 1 Hz | Entropy, MI, PVT correction, capacity, BSC, RUL, ICA |
| `TCC vs SBCCI/SBCCI_TCC_…csv` | **Device B** (separate test circuit), non-PID bench | ≈24 h stabilized, 2 s | KL bench comparison (noisy bench) |
| `TCC vs SBCCI/TCC_SBCCI_…csv` | **Device B**, PID reference bench | ≈24 h stabilized, 1 Hz | KL bench comparison (reference) |

**Device A and device B are never mixed.** All entropy/MI/correction/capacity/RUL/ICA results are device A; only the KL/JS bench-fidelity comparison is device B (where the two benches share the device, so the divergence isolates the bench/environment, not device-to-device variation).

---

## 3. Course concepts used, and how each was applied

Organized by the disciplina's *núcleos de conteúdo*. Every entry produced a concrete, data-backed number (§4).

### Núcleo 1 — Principles & limits of communication
- **Communication-channel model of the sensor** — the unifying frame $S = S_{aged}(t) - \Delta_{PVT}(T,V) + \varepsilon_q$.
- **Source-coding theorem (limit only)** — used as the bound "any code ≥ $H(S)$"; no codec implemented.
- **Channel capacity (Shannon)** — converts post-correction noise into an effective number of resolvable aging states.

### Núcleo 2 — Measures of information (the core)
- **Entropy** $H(S)$ — total uncertainty budget of the sensor output.
- **Joint & conditional entropy** $H(S\mid T,V)$ — residual uncertainty once the environment is known.
- **Mutual information** $I(S;T,V)$ **(centerpiece)** — non-linear contamination measure replacing $R^2$; estimated by binned + Miller–Madow **and** KSG (Kraskov), cross-checked.
- **MI as an optimization objective** — "best burn-in" = minimize $I(S;T,V)$.

### Núcleo 3 — Transmission, denoise, divergence, capacity
- **DeNoise** — the PVT correction *is* denoising: strip reversible $\Delta_{PVT}(T,V)$ to expose latent aging.
- **Kullback–Leibler divergence** — distance between the SBCCI and PID bench distributions; demonstrates KL's asymmetry (not a metric).
- **Jensen–Shannon divergence** — symmetric, bounded "distance between validation environments."
- **Binary Symmetric Channel (BSC)** — the binary aging-alarm decision; capacity $C_{BSC}=1-H_2(p)$, mapping to the failure-detection/prevention goal.
- **Noise / Gaussianity** — Gaussian closed-form KL vs empirical reveals non-Gaussian (heavy-tailed) excursions.

### Núcleo 4 — Complexity, estimation, ICA
- **Description-length model selection (MDL/BIC), grounded in Kolmogorov complexity** — chooses linear vs non-linear PVT correction on the reversible residual using $n_{eff}$; the paper's theory section now derives the BIC-style penalty as the computable two-part-code stand-in for $K(x)=\min_{p:U(p)=x}l(p)$ and the invariance theorem, making the MDL verdict an explicit instance of Occam's razor rather than an unexplained formula.
- **Least squares (OLS / GLS)** — linear PVT correction.
- **Maximum likelihood (MLE)** — non-linear (Arrhenius / super-linear) correction.
- **Method of moments** — descriptive second-order baseline.
- **Bayesian estimation** — Student-$t$ posterior on the aging slope (Jeffreys prior, thinned to $n_{eff}$) → credible error bars on the RUL bound.
- **Cramér–Rao bound** — frequentist lower bound on the slope-estimate variance → detectability.
- **Sequential Bayesian estimation (Kalman filter) + stochastic processes — extension, beyond the core syllabus, built directly on the estimation theory above** — the latent aging level modelled as a Wiener process (the continuous-state analogue of the course's Markov-chain material), filtered/smoothed to a denoised trajectory; the rate-noise hyperparameter fit by the same MLE principle already used for the estimator ladder; RUL re-expressed as a closed-form Inverse-Gaussian first-passage-time *distribution* rather than a single bound.
- **ICA + negentropy + blind source separation** — model-free recovery of the aging source from $(S,T,V)$.
- **Independence / non-Gaussianity measures** — excess kurtosis as the ICA contrast; inter-component MI as the separation score.

### Supporting (statistical foundations, throughout)
Probability & random variables; **expectation, variance, correlation**; empirical **distributions**; **preprocessing / normalization**; **autocorrelation handling** → effective sample size $n_{eff}$; **inference** (block-bootstrap confidence intervals, **surrogate null tests**).

### Deliberately NOT used (scope decision: only what strongly correlates with the research)
- **Concrete source-coding codecs** (Huffman, Lempel–Ziv–Welch) — redundant with the entropy/autocorrelation results.
- **Channel error-correcting codes** — no application here.
- **Big Data / streaming tooling** (MapReduce/Spark) — engineering, not science, for this problem.

---

## 4. Key results (all data-backed, auto-generated into the paper)

**Device A — the information spine**
- Effective sample size: **$n_{eff}=1{,}224$** (τ_int = 314 s), despite 768,884 raw samples — the honesty linchpin.
- $H(S) = 3.43$ bits (27 levels); $H(S\mid T,V) = 2.30$ bits.
- $I(S;T,V) = 1.13$ bits binned (KSG 1.22, own 95% CI [1.16, 1.28] — overlaps the binned CI [1.09, 1.18] only narrowly); $I(S;T)=1.09$, $I(S;V)=0.11$.
- **Non-linearity result (raw series, headline):** measured MI exceeds the Gaussian-equivalent of the linear $R^2=0.738$ (0.97 bits) by **17–26 %** depending on estimator (binned/KSG), still positive after discounting the estimator's own bias floor (~10 %).
- **Non-linearity result does NOT survive detrending (honesty finding, added 2026-08-18):** on the same reversible series used for PVT correction, MI (binned 0.60 bits, KSG 0.66 bits) sits *at or below* the detrended Gaussian-equivalent (0.74 bits) — a deficit of −19 % to −11 %, not an excess. The raw-series excess is therefore attributable to the shared slow trend between aging and environment, not demonstrated to be instantaneous non-linear PVT physics. The MI-over-$R^2$ methodology stands; the specific causal claim ("non-linear because the physics is non-linear") does not, and is retracted in the paper (`sections_pt/06_results.tex` §6.1, `sections_pt/07_discussion.tex` §7.1). See `review/prompt_correcoes_finais_TF.md` Bloco A/B.
- **Surrogate null floor** (circular-shift): p95 = 0.097 bits → measured MI is **12× the floor** → real, not bias.
- **PVT correction:** reversible coupling $0.656 \to 0.046$ bits = **93 % removed**; residual σ = 0.84 counts (prior PID: 0.73 — independent cross-check); **MDL selects linear**.
- **Aging recovery:** stripping PVT strengthens corr(S, t) from **−0.35 → −0.73** — the latent aging trajectory is *exposed*, not just cleaned.
- **Capacity:** SNR 2.36 → $C = 0.87$ bits → **1.8 distinguishable aging states**.
- **BSC alarm:** 1 h ≈ coin flip (C_BSC ≈ 0); **24 h → C_BSC = 0.99 bits**; full campaign ≈ certain.
- **RUL (Cramér–Rao):** min detectable rate **1.2 m-cnt/h**; min observation time **34 h** (≪ 214 h campaign; > the prior 23 h runs — explaining why those couldn't separate aging).
- **RUL (Bayesian):** slope posterior **−18.2 m-cnt/h, 95% CrI [−19.2, −17.2]**; P(slope < 0) ≈ 100 % (reading this residual drift *as aging* is conditioned on the single-device identification assumption, §7.6); min-obs-time CrI [33, 36] h. Frequentist and Bayesian agree.
- **RUL as a distribution (Wiener/Kalman, extension):** modelling the corrected residual as a Wiener process observed through a Kalman filter (block-averaged to $n_{eff}\approx1{,}224$ quasi-independent points), the rate-noise MLE collapses to ≈0 — a second, independent confirmation of the MDL "insufficient curvature" verdict — and the smoothed rate (−15.9 m-cnt/h) agrees in order of magnitude with the CRLB/Bayesian estimate. The Wiener model gives a closed-form Inverse-Gaussian **RUL distribution** (not just a bound): at $D=\sigma_{noise}$, mean 52.9 h / median 8.0 h; at $D=\sigma_{signal}$, mean 81.3 h / median 17.5 h — the large mean/median gap (right-skew) is largest exactly in the low-SNR regime already identified by the capacity result, linking the two findings quantitatively.

**Device B — bench fidelity (KL)**
- Slack noise: SBCCI 3.23 vs PID 1.46 counts (2.2×), tracking temperature noise (2.64 vs 1.25 °C) → contamination is thermally driven.
- **KL(SBCCI‖PID) = 1.94 bits, KL(PID‖SBCCI) = 1.01 bits** (asymmetric); **JS = 0.279 bits**.
- Empirical KL (1.94) > Gaussian closed-form (1.67) → non-Gaussian heavy tails.

**ICA blind separation (device A, exploratory)**
- Model-free ICA recovers an aging component matching the regression $S_{corr}$ at **|corr| = 0.834** — independent corroboration of the PVT correction, using none of the measured $T,V$ coupling.
- Recovered sources strongly non-Gaussian (excess kurtosis +5.8 / +29.9). Separation **partial** (residual inter-IC MI 0.57 bits) — reported honestly, since the non-stationary trend + heavy tails only approximately meet ICA's assumptions.

---

## 5. Deliverables (file tree)

```
tf_teoria-da-informacao/
├── 00_Work_Summary.md          ← this file
├── 01_Project_Overview.md      proposal / contribution / caveats
├── 02_Methodology.md           5-stage arc (acquire→transform→quantify→preserve→infer)
├── 03_Course_Topic_Mapping.md  concept→application→result (rubric evidence; selective)
├── 04_Dataset.md               empirical characterization of all three logs
├── 05_Execution_Plan.md        prioritized plan + status (all core items ✓)
├── analysis/
│   ├── tier1_pipeline.py        entropy, MI, surrogate floor, PVT correction,
│   │                            capacity, BSC, CRLB + Bayesian RUL
│   ├── kl_benches.py            KL / JS divergence between benches
│   ├── ica_separation.py        FastICA blind separation
│   ├── kalman_rul.py            Wiener process + Kalman/RTS smoother +
│   │                            Inverse-Gaussian RUL distribution
│   ├── make_figures.py          generates the 6 paper figures (PDF)
│   ├── results.json, results_kalman.json   machine-readable scalars
│   └── README.md                results tables + how to run
└── latex/                       final document
    ├── main.tex, notation.tex, references.bib
    ├── generated/values.tex     ALL scalars as macros (auto-filled by the scripts)
    ├── sections/00_abstract … 08_conclusion
    ├── tables/                  dataset_summary, mi_vs_r2
    └── figures/                 6 figures (auto-generated by make_figures.py)
```

**Reproducibility contract:** numbers are never typed into prose. The scripts emit every scalar into `latex/generated/values.tex` as `\newcommand` macros and every figure into `latex/figures/`; re-running them on a new log regenerates the paper with zero transcription. (As of 2026-08-13 this is enforced end-to-end: the dataset descriptive stats, $H(S)$ and $R^2$ were previously hand-typed literals in `values.tex` — a real gap in this contract — and are now computed inside `tier1_pipeline.py`. As of 2026-08-18, three rounds of independent review — `review/prompt_correcoes_TF.md`, `review/prompt_correcoes_finais_TF.md` — added the detrended-KSG/CI macros, the floor-adjusted-excess macro, and fixed several macro-reuse and CI-ordering bugs; every macro they introduced is listed in those two files' acceptance criteria.) Build the **graded** (Portuguese) paper: `cd latex && latexmk -pdf main_pt.tex`. Build the seminar deck: `latexmk -pdf seminar.tex`. (`main.tex`, the English variant, is not synced with the 2026-08-18 fixes — see `CLAUDE.md`.) Run analyses: `cd analysis && python3 tier1_pipeline.py && python3 kl_benches.py && python3 ica_separation.py && python3 kalman_rul.py && python3 make_figures.py` (needs `numpy`, `scipy`, `matplotlib`).

---

## 6. Honesty caveats (carried in the paper)

- **The raw-series non-linearity excess (17–26 %) does not survive detrending** — on the reversible series it is a deficit (−19 % to −11 %), not an excess. It should not be read as "the reversible relation is sub-linear" either: for a residual quantized to few counts, discrete MI can legitimately sit below the continuous Gaussian-equivalent. The defensible reading is that no non-linear excess is resolvable above the estimator floor on this series; the raw-series excess is attributable to the shared aging/environment trend, not demonstrated instantaneous PVT non-linearity. See §4 above and `sections_pt/06_results.tex` §6.1.
- **Single aging device, single regime** — RUL is a *detectability bound and methodology*, not a validated multi-device lifetime prediction.
- **$n_{eff} \ll n$** — the 1 Hz series is heavily autocorrelated; all confidence/credible statements use $n_{eff}$, with block-bootstrap intervals and a surrogate null floor.
- **Capacity** is used as an effective-resolution heuristic, not a literal optimal-coding claim.
- **ICA** is corroborative, not a clean unmixing.
- **The KL comparison is a different device** than the aging analysis; the two are never mixed.
- **The Wiener/Kalman RUL distribution uses self-referential thresholds** ($D=\sigma_{noise}$, $D=\sigma_{signal}$, both already-computed Tier-1 quantities), because no independently calibrated failure threshold exists for this sensor — it is a methodology demonstration, in the same spirit as the Cramér–Rao bound, not an operational lifetime prediction.
