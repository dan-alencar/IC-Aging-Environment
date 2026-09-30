# Methodology

## Information-Theoretic Characterization of Aging Information and Noise in On-Chip Slack Sensors

This document develops the methodology for the project. It is organized around the five-stage arc — **acquire, transform, quantify, preserve, infer** — and pays particular attention to the statistical hazards of estimating information-theoretic quantities from autocorrelated sensor time series.

---

## 1. Data and Notation

### 1.1 Available data

The project consumes the synchronized logs produced by the automated burn-in platform. The primary substrate is the `Tentative_1_20260524_203756.csv` log — a single PID-controlled campaign of **≈214.6 h (≈772 k samples at 1 Hz)** with the DUT held near **125 °C** and **1.40 V**. Each record contains:

| Symbol | Field | Meaning |
|---|---|---|
| $t$ | `time_sec` | seconds since test start |
| $S$ | `dut_slack` | slack reading, in phase-shift increments (1 unit ≈ 19.85 ps) |
| $T$ | `dut_temp_c` | die temperature from the XADC |
| $V$ | `dut_volt` | core voltage ($V_{CCINT}$) from the XADC |
| — | `oven_temp_c`, `oven_setpoint_c`, `oven_output_pct` | oven-side context (PID setpoint/output) |
| — | `psu_voltage_v`, `psu_current_a` | bench supply context |

The log header also records the identified plant model (FOPDT: $G(s)=1.56\,e^{-150.6s}/(1307.2s+1)$) and the PID gains, which document the thermal regime under which the data were taken. A full empirical characterization of this dataset (ranges, descriptive statistics, the measured $\mathrm{corr}(S,T)\approx-0.86$, $\mathrm{corr}(S,t)\approx-0.35$, linear $R^2(S\mid T,V)\approx0.74$, and $H(S)\approx3.43$ bits over 27 occupied levels) is given in the companion document `04_Dataset.md`.

**Two distinct devices are involved, and the analyses are kept separate accordingly:**

- The **214.6 h aging campaign** (`Tentative_1`) is run on the primary aging device (call it **device A**). All the entropy, mutual-information, PVT-correction, capacity, RUL and ICA results are computed on device A and are internally consistent.
- The **bench-fidelity comparison** (Methodology §4.3) uses two **≈24 h stabilized** runs — the non-PID SBCCI setup and the PID reference — acquired on a **dedicated test circuit/device (device B), distinct from device A**. The SBCCI and PID runs share device B, so their KL/JS divergence isolates the *bench/environment* difference; but absolute slack levels and noise magnitudes from device B do **not** transfer to device A (different circuit, operating point and bitstream), and no result mixes the two.

Because device A is a single device, the long campaign cannot by itself separate a permanent-aging trajectory from device-to-device variation; the published thermal-fidelity statistics (σ = 0.40 vs 3.29 °C; residual 0.73 vs 0.90 counts; $R^2$ = 59.2% vs 92.1%) remain the same-device bang-bang-vs-PID anchor.

### 1.2 The signal model

The physical model inherited from the prior work is

$$S(t) = S_{aged}(t) - \Delta_{PVT}(T,V) + \varepsilon_q,$$

where $S_{aged}(t)$ is the permanent, slowly-drifting aging term, $\Delta_{PVT}(T,V)$ is the reversible environmental term, and $\varepsilon_q$ is quantization noise bounded by the sensor LSB. The information-theoretic program is to measure how much of $\mathrm{Var}(S)$ — or more correctly, $H(S)$ — is attributable to the environment, how much can be removed, and how much genuine aging information remains and can be recovered.

---

## 2. Stage 1 — Acquire

No new experiments are strictly required; the project is designed to reuse existing logs. Where re-runs are available, the acquisition checklist is:

- confirm 1 Hz synchronization across all streams (the platform's `TestSequencer` guarantees a unified timestamp);
- exclude the initial thermal-soak transient (the prior work excludes the first 1.0 h) so that the analysis is performed on the post-equilibration window;
- retain both the raw slack counts and the auxiliary $T$, $V$ channels at full resolution — discretization for entropy estimation is done later and deliberately, not at acquisition time.

---

## 3. Stage 2 — Transform (Preprocessing and Distribution Construction)

### 3.1 Normalization and stationarity

Information-theoretic quantities are defined on distributions, so the streams must be put in a form where empirical distributions are meaningful.

- **Detrending for the noise analysis.** To isolate the *reversible* component, the slow aging drift is removed with a robust trend estimate (e.g., a long-window median or Theil–Sen slope over the post-equilibration window). The mutual-information-with-environment analysis is then performed on the detrended residual, so that $I(S;T,V)$ measures reversible coupling rather than being inflated by a shared time trend.
- **Normalization.** $T$ and $V$ are standardized so that binning and density estimation are not dominated by scale differences.

### 3.2 Handling serial correlation

The 1 Hz series is strongly autocorrelated. This is the single most important statistical hazard in the project, because naïve information estimators assume i.i.d. samples and will badly underestimate variance (and bias MI upward) when fed correlated data. The prior thermal-fidelity paper already confronts this for its slope estimates using Newey–West (HAC) confidence intervals; this project must confront it for the *information* estimates. Three mitigations are used together:

1. **Effective sample size.** Compute the integrated autocorrelation time $\tau_{int}$ of the residual and report an effective sample size $n_{eff} = n / (2\tau_{int})$ rather than the raw $n$. All confidence statements use $n_{eff}$.
2. **Block-based resampling.** Use a moving-block (or stationary) bootstrap to put confidence intervals on every information quantity, since block bootstrap preserves short-range dependence that an ordinary bootstrap destroys.
3. **Thinning as a cross-check.** Repeat key estimates on a thinned series (one sample per $\sim\tau_{int}$) to confirm that conclusions are not artifacts of dependence.

### 3.3 Choosing a representation for entropy/MI estimation

Two complementary estimator families are used and compared. Result: they agree on the qualitative conclusion (dependence far above the null floor; positive excess over the Gaussian-linear equivalent on the raw series) but their 95% CIs overlap only narrowly (point estimates at opposite ends of the overlap) — a characterized, reported estimator gap, not full numerical agreement:

- **Binned / plug-in with bias correction.** Adaptive (equiprobable) binning of $S$, $T$, $V$, with the Miller–Madow correction for the downward bias of plug-in entropy, and an explicit study of sensitivity to bin count.
- **k-nearest-neighbour estimators (Kozachenko–Leonenko for entropy; KSG for mutual information).** These avoid binning altogether and are well suited to the continuous, low-dimensional $(S,T,V)$ space here. KSG is the workhorse for the $I(S;T,V)$ estimate.

The quantization of $S$ to integer increments is acknowledged explicitly: where $S$ is treated as discrete, discrete entropy is used; where the kNN estimators are applied, a small dither / continuity correction is documented so that the LSB structure does not create spurious zero-distance ties.

---

## 4. Stage 3 — Quantify (The Core Information Measures)

### 4.1 Marginal and conditional entropy

Estimate $H(S)$, the total uncertainty in the slack reading, and $H(S \mid T, V)$, the residual uncertainty once the environment is known. The reduction

$$I(S; T,V) = H(S) - H(S \mid T, V)$$

is the central quantity: the information the environment carries about the sensor output. This is computed for both thermal regimes.

### 4.2 Mutual information as the replacement for $R^2$

The headline comparison re-expresses the prior work's variance-explained numbers as information:

- compute $I(S;T)$, $I(S;V)$, and $I(S;T,V)$ for bang-bang and for PID;
- compare against the published linear $R^2$ values (92.1% vs. 59.2% jointly) to demonstrate where the linear measure and the information measure diverge — the divergence is expected to be largest exactly where the physics is most non-linear.

A useful normalization for interpretability is the **information fraction** $I(S;T,V)/H(S)$, the share of the sensor's output entropy that is environmentally determined; this is the information-theoretic analogue of $R^2$ and is directly comparable across regimes.

### 4.3 Distributional comparison with KL divergence

Use $D_{KL}$ to compare the slack distribution (and the joint $(S,T,V)$ distribution) between the two benches, quantifying how far the non-compliant bang-bang environment pushes the measured distribution from the controlled PID reference. This gives a single-number "distance" between validation environments and connects to the standards-compliance argument in the prior work.

---

## 5. Stage 4 — Preserve (PVT Correction as Information Recovery)

### 5.1 The correction estimator

Build a PVT-correction function $\hat{\Delta}_{PVT}(T,V)$ and form the corrected residual $S_{corr} = S - \hat{\Delta}_{PVT}(T,V)$. The estimator is fit with the parameter-estimation methods taught in the course, used as a deliberately graded ladder so the choice is itself a result:

- **Method of moments / ordinary least squares** for the **linear** correction (reproducing the prior work's implicit model);
- **Generalized / non-linear least squares and maximum-likelihood estimation (MLE)** for a **non-linear** correction consistent with the Arrhenius / super-linear-$V_{DD}$ physics, with the GLS error model accounting for the residual serial correlation;
- a **Bayesian** variant that places priors on the correction coefficients and propagates posterior uncertainty into the downstream information and RUL estimates, so the final detectability bound carries calibrated error bars rather than point values.

### 5.2 Evaluation in information terms

The quality of each correction is judged not only by residual standard deviation (the prior work's metric: 0.73 vs. 0.90 counts) but by:

- **residual mutual information** $I(S_{corr}; T, V)$ — a good correction drives this toward zero; any leftover is information the correction failed to remove;
- **residual entropy** $H(S_{corr})$ relative to the quantization floor — distinguishing genuine recoverable aging signal from the sensor's irreducible LSB noise. This is naturally framed as a **rate–distortion / source-coding** question: how compactly can the aging-relevant signal be represented once the environment is removed, and what is the floor set by quantization?

### 5.3 Feature-selection framing

Because $T$ and $V$ are separate auxiliary channels, the analysis ranks them by information contribution: which single auxiliary measurement removes the most uncertainty per bit, and is the second one worth its acquisition cost? This is information-theoretic feature selection applied to sensor fusion, and it produces a concrete recommendation for what an SLM controller must log.

### 5.4 Model selection by description length (MDL)

The choice between the linear and non-linear $\hat{\Delta}_{PVT}$ should not be made by eye. The **Minimum Description Length (MDL)** principle selects the model by total cost $L(\text{model}) + L(\text{data}\mid\text{model})$ — operationally a BIC-style penalty $n_{eff}\ln\sigma^2_{resid} + k\ln n_{eff}$ computed on the *reversible* residual and on the effective sample size — so the non-linear model's extra parameters are adopted only if they buy enough residual compression. On the data this selects the **linear** correction: the non-linear model removes marginally more residual mutual information but reduces the residual variance negligibly, so its extra parameters are not justified. This replaces the prior work's informal model choice with a principled criterion.

### 5.5 Blind source separation of the latent aging component (ICA / negentropy)

The physical model $S = S_{aged}(t) - \Delta_{PVT}(T,V) + \varepsilon_q$ is, structurally, a **mixture of sources**. Where §5.1 removes the environment by *regressing on measured* $T,V$, this stage asks the dual, model-free question the syllabus's **Independent Component Analysis** material poses: can the independent sources be recovered from the mixed observations alone?

- Form a multi-channel observation matrix from $(S, T, V)$ (and lagged/derived channels) and run ICA, using **negentropy / non-Gaussianity** as the contrast function — the aging drift is strongly non-Gaussian (near-monotonic) while thermal fluctuation under PID is closer to Gaussian, which is precisely the asymmetry ICA exploits.
- Evaluate the recovered "aging" component against the regression-based $S_{corr}$ and against the known $T,V$ drivers (an environmental component should correlate with $T$; given $\mathrm{corr}(S,T)\approx-0.86$ in the data, a clean thermal component is expected to emerge first).
- Report this as an **independence / gaussianity** measurement: how separable are the sources, and how much mutual information remains between the recovered components (ideal ICA drives it to zero). This is the most exploratory stage and is reported honestly as such — but a partial separation is already a result the regression-only prior work could not produce.

---

## 6. Stage 5 — Infer (Channel Capacity and RUL Detectability)

### 6.1 Effective resolving power (capacity view)

Model the per-window aging estimate as a value transmitted through a Gaussian-like channel whose noise variance is the measured post-correction residual variance. The (Shannon) capacity-style expression

$$C \approx \tfrac{1}{2}\log_2\!\left(1 + \frac{\sigma^2_{signal}}{\sigma^2_{noise}}\right)$$

is used **as an effective-resolution heuristic**, not as a literal communication-rate claim: it converts the measured noise (different for bang-bang and PID) into an effective number of distinguishable aging states per observation window. The two regimes are compared on this basis, giving a noise-to-resolution link the prior work did not provide.

### 6.1b The aging decision as a Binary Symmetric Channel

The course develops channel capacity through the **Binary Symmetric Channel (BSC)**, and the SLM use-case has a natural binary form: at each decision epoch the monitor must declare **"aging exceeds threshold"** or **"not yet."** Model this declaration as a BSC whose crossover probability $p$ is the empirical error rate of the thresholded estimator — false alarms (reversible noise pushed $S$ past the threshold) and misses (true drift masked by noise). Its capacity

$$C_{BSC} = 1 - H_2(p), \qquad H_2(p) = -p\log_2 p - (1-p)\log_2(1-p)$$

gives, in bits per decision, how reliably the sensor can carry a single aging-alarm bit under each thermal regime. Because $p$ is directly set by the post-correction noise (which differs for bang-bang vs PID), this connects the continuous-resolution result of §6.1 to a discrete, decision-level reliability figure — the "medida de confiabilidade de transmissão" of the syllabus, applied to failure-prevention alarms.

### 6.2 Estimation-theoretic detectability bound

Pose RUL as estimation of a latent monotonic degradation slope from noisy observations. Using the measured noise statistics and $n_{eff}$, derive a Cramér–Rao-style lower bound on the variance of the slope estimate, and translate it into a **minimum detectable aging rate** and a **minimum observation time** before a true trend rises above the reversible fluctuation. The prior work's windowed slope estimates with HAC confidence intervals (−6.5 vs. −5.3 m-cnt/h) provide the empirical anchor for this bound.

### 6.3 Optimization framing

Finally, cast "best burn-in condition" as an optimization: choose the thermal-control regime (and, in principle, setpoint policy) that **minimizes $I(S;T,V)$** — i.e., minimizes the environmental information injected into the sensor — subject to delivering the required Arrhenius acceleration factor. This unifies the project's measurements into a single objective and directly serves the SLM functions (adaptive voltage scaling, RUL) named as the end consumers in the source papers.

---

## 7. Validation Strategy

- **Cross-estimator comparison:** binned-with-Miller–Madow vs. KSG estimates, each with its own bootstrap CI. Result: they agree qualitatively but not numerically (CIs overlap only narrowly) — reported as an estimator-uncertainty range (e.g. 17–26% excess) rather than a single point value.
- **Cross-regime sanity:** the information fraction $I(S;T,V)/H(S)$ should order the two benches consistently with the published $R^2$ ordering, while revealing the non-linear gap.
- **Surrogate / null tests:** time-shifted and phase-randomized surrogates of $T,V$ should drive $I(S;T,V)$ to its bias floor, calibrating how much measured MI is real.
- **Quantization control:** repeat key estimates with and without dither to confirm the LSB structure is not driving results.

---

## 8. Expected Deliverables

1. A table of $I(S;T)$, $I(S;V)$, $I(S;T,V)$, and the information fraction, set beside the prior $R^2$ values, with the measured MI quantified as an excess over the Gaussian-equivalent of the linear fit.
2. A KL / Jensen–Shannon divergence comparison of the two validation benches (SBCCI vs. PID), including the directional asymmetry of KL.
3. Pre- and post-correction reversible residual MI, with linear vs. non-linear correction selected by MDL, and the aging-recovery effect (strengthening of $\mathrm{corr}(S_{corr},t)$).
4. An ICA / negentropy attempt at blind separation of the aging component, with residual inter-component MI as the separation score.
5. An effective-resolution / continuous-capacity figure **and** a BSC capacity $C_{BSC}=1-H_2(p)$ for the binary aging-alarm decision, linking measured noise to distinguishable aging states and to alarm reliability.
6. A noise-limited RUL detectability bound (minimum detectable rate, minimum observation time) via Cramér–Rao.
7. A documented, reusable analysis pipeline that consumes the platform's standard logs.

---

## 9. Known Limitations (Methodological Honesty)

- The new long run (≈214 h) does expose an aging drift, but it is **single-device, single-regime**; permanent-aging separability across devices remains out of reach, so RUL outputs are detectability bounds, not validated multi-device predictions.
- MI estimates on autocorrelated series are bias-prone *despite* the large raw sample count, because $n_{eff}\ll n$; this is mitigated, not eliminated, by the estimator choices and surrogate tests above, and all results are reported with block-bootstrap intervals on $n_{eff}$.
- The capacity expression is used as an effective-resolution heuristic; it is not a claim that the sensor is an optimally coded channel.
- ICA/blind separation is exploratory: with only three primary channels and dominant thermal coupling, full recovery of the aging source is not guaranteed; a partial or failed separation is reported as such, not forced.
