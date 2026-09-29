# Course-to-Project Topic Mapping

## How Each Information Theory Course Topic Maps onto the Project

This document demonstrates full coverage of the course syllabus by mapping each topic to a specific part of the project. For every topic it states: **what the concept is used for**, **where in the project it appears**, and **what result it produces that the prior reliability research could not state**. This is intended both as a planning aid and as evidence for the instructor that the project exercises the whole course, not a fragment of it.

---

## Part A — Statistical Foundations

### A.1 Probability and random variables
- **Use:** Treat the slack reading $S$, die temperature $T$, and core voltage $V$ as random variables, and formalize the inherited decomposition $S = S_{aged}(t) - \Delta_{PVT}(T,V) + \varepsilon_q$ as a relationship among random variables rather than a deterministic curve.
- **Where:** Methodology §1.2 (signal model), §3 (distribution construction).
- **New result:** Turns the prior work's qualitative "slack is contaminated by PVT" statement into a probabilistic object on which everything else can be computed.

### A.2 Expectation, variance, correlation
- **Use:** Baseline second-order description of the streams; reproduce the prior work's variance-based metrics so the information measures can be compared against them on equal footing.
- **Where:** Methodology §3.1, §4.2.
- **New result:** Establishes the exact correspondence between the existing σ / $R^2$ numbers (e.g., σ = 0.40 vs. 3.29 °C; residual 0.73 vs. 0.90 counts) and their information-theoretic successors, making the upgrade auditable.

### A.3 Distributions
- **Use:** Construct empirical marginal and joint distributions of $(S,T,V)$ as the substrate for entropy and mutual information; study sensitivity to discretization.
- **Where:** Methodology §3.3.
- **New result:** Provides the distributional view that the regression-based prior analysis never built, which is a prerequisite for any non-linear dependence measure.

### A.4 Preprocessing and normalization
- **Use:** Detrend to isolate the reversible component, standardize $T$ and $V$, and manage the strong serial correlation of the 1 Hz series (effective sample size, block bootstrap, thinning).
- **Where:** Methodology §3.1–§3.2.
- **New result:** Makes information estimates statistically defensible on autocorrelated sensor data — the prior work only needed this rigor for slope confidence intervals (Newey–West); the project extends it to information quantities.

### A.5 Inference
- **Use:** Attach confidence intervals (via block bootstrap on $n_{eff}$) and run surrogate/null tests to separate real dependence from estimator bias.
- **Where:** Methodology §3.2, §7 (validation).
- **New result:** A calibrated statement of how much measured information is real, which is essential given the short datasets.

---

## Part B — Core Information Measures

### B.1 Entropy
- **Use:** $H(S)$ quantifies the total uncertainty in the sensor output; the quantization LSB sets an entropy floor.
- **Where:** Methodology §4.1, §5.2.
- **New result:** A single scalar for "how much the sensor reading can vary," against which the removable (environmental) and irreducible (quantization) parts can be separated.

### B.2 Conditional entropy
- **Use:** $H(S \mid T,V)$ is the residual uncertainty once the environment is known; its gap from $H(S)$ is the environmental information.
- **Where:** Methodology §4.1.
- **New result:** Quantifies, in bits, how much of the sensor's uncertainty is "explained away" by logging temperature and voltage — a direct, model-free analogue to the prior $R^2$.

### B.3 Mutual information (the centerpiece)
- **Use:** $I(S;T,V)$ replaces the linear $R^2$ as the correct, non-linear measure of environmental contamination; per-channel $I(S;T)$ and $I(S;V)$ rank the auxiliary signals.
- **Where:** Methodology §4.2, §5.2 (residual MI), §6.3 (optimization objective).
- **New result:** Corrects and sharpens the central comparison of the thermal-fidelity paper, and defines burn-in quality as *minimization of $I(S;T,V)$* — a rigorous, optimizable target the prior work lacked.

### B.4 KL divergence
- **Use:** $D_{KL}$ measures the distance between the slack (and joint) distributions of the bang-bang and PID benches.
- **Where:** Methodology §4.3.
- **New result:** A single-number "distance between validation environments," giving the standards-compliance argument (which bench is the cleaner reference) an information-theoretic backing.

---

## Part C — Coding, Channels, and Capacity

### C.2 Channel capacity (continuous / Shannon limit)
- **Use:** Convert measured post-correction noise into an effective number of distinguishable aging states per observation window (capacity used as a resolution heuristic).
- **Where:** Methodology §6.1.
- **New result:** A noise-to-resolution link — telling SLM designers how many aging levels the sensor can actually resolve under each thermal regime, directly relevant to adaptive voltage scaling and RUL.

### C.2b Binary Symmetric Channel (BSC)
- **Use:** Model the binary "aging-alarm" decision as a BSC with crossover $p$ = empirical false-alarm/miss rate; capacity $C_{BSC}=1-H_2(p)$.
- **Where:** Methodology §6.1b.
- **New result:** A decision-level reliability figure (bits per alarm) tying the failure-prevention SLM function to a capacity the course teaches explicitly — a "medida de confiabilidade de transmissão" for the alarm channel.

### C.3 Noise
- **Use:** Treat reversible PVT fluctuation and quantization as channel noise corrupting the latent degradation message.
- **Where:** Methodology §1.2, §6.1.
- **New result:** Unifies the two noise sources the prior papers describe separately (environmental and LSB) into one channel model with one figure of merit.

---

## Part D — Complexity, Estimation and Optimization

### D.0 Description-length model selection (MDL) and Kolmogorov complexity
- **Use:** MDL / BIC criterion ($n_{eff}\ln\sigma^2_{resid}+k\ln n_{eff}$ on the reversible residual) to select between linear and non-linear PVT corrections by total description length. The paper now grounds this explicitly in Kolmogorov complexity $K(x)=\min_{p:U(p)=x}l(p)$ and the invariance theorem: MDL is the computable two-part-code stand-in for "prefer the shortest description that still explains the data" (Occam's razor, formalized).
- **Where:** `latex/sections_pt/03_theory.tex` §3.6 (theory), §4.4 (Methodology Stage 4), §6.2/§7.1 (Results/Discussion — the MDL verdict is reframed as "not enough curvature information at this single operating point to pay for the non-linear model's parameters," not a claim that the physics is linear).
- **New result:** A principled model-selection criterion tied to its information-theoretic foundation rather than used as an unexplained BIC formula — "the non-linear correction is justified only if it compresses the residual enough to pay for its parameters." On the data it selects the linear model, replacing the prior work's informal model choice.

### D.1 Estimation (moments, least squares, MLE, Bayesian)
- **Use:** Fit $\hat{\Delta}_{PVT}(T,V)$ with method of moments / OLS (linear), GLS+MLE (non-linear, serial-correlation-aware), and a Bayesian variant carrying posterior uncertainty forward. Pose RUL as estimation of a latent monotonic degradation slope; derive a Cramér–Rao lower bound on slope-estimate variance from the measured noise and $n_{eff}$.
- **Where:** Methodology §5.1, §6.2.
- **New result:** A graded estimator ladder (each method from núcleo 4 used where it fits) plus a noise-limited **minimum detectable aging rate** and **minimum observation time** — an honest detectability bound with calibrated (Bayesian) error bars that replaces an over-reaching prediction claim.

### D.1b Sequential Bayesian estimation (Kalman filter) and stochastic processes — extension beyond the core syllabus
- **Use:** The latent aging level is modelled as a Wiener process — the continuous-state, continuous-time analogue of the course's discrete-time Markov-chain material (a process whose future depends on the present alone) — observed through additive noise. A Kalman filter/RTS smoother (built on the same maximum-likelihood principle as D.1) gives a denoised, continuously-updated aging trajectory with credible bands, replacing the single campaign-wide OLS/Bayesian slope with a sequential estimate; the Wiener model's first-passage time to a threshold is a closed-form Inverse Gaussian, turning the RUL *bound* of D.1 into a full RUL *distribution*.
- **Where:** `latex/sections_pt/03_theory.tex` §3.7 (`sec:th-wiener`); Methodology §6.2 extension; Results §"A denoised aging trajectory and RUL as a distribution" (`sec:res-wiener`); `analysis/kalman_rul.py`.
- **New result:** A full RUL probability distribution (mean, median, skew) rather than a point rate + error bar, plus an independent, structurally different confirmation of the MDL "insufficient curvature" verdict (the rate-noise MLE also collapses to a constant-drift model) — and a quantitative link between the capacity/SNR result and RUL uncertainty (the same low-SNR regime that caps resolvable states also makes the RUL distribution heavy-tailed).
- **Honesty note:** This material (Kalman filtering, Wiener-process degradation, Inverse-Gaussian first-passage time) is not itself in the course syllabus; it is included as an explicit deepening of the course's own estimation-theory and stochastic-process content (método de máxima verossimilhança; cadeias de Markov/processos estocásticos), cited to the standard literature (Kalman 1960; Whitmore & Schenkelberg 1997; Si et al. 2011), not presented as core syllabus coverage.

### D.2 ICA, negentropy and blind source separation
- **Use:** Treat $S$ as a mixture and attempt model-free recovery of the aging source via ICA, using negentropy / non-Gaussianity as the contrast and residual inter-component MI as the separation score.
- **Where:** Methodology §5.6.
- **New result:** The aging component extracted as an *independent component* rather than a regression residual — a qualitatively new, assumption-light separation, plus an explicit independence/gaussianity measurement of how separable aging and PVT actually are.

### D.3 Optimization
- **Use:** Cast "best burn-in condition" as minimizing $I(S;T,V)$ subject to delivering the required Arrhenius acceleration factor.
- **Where:** Methodology §6.3.
- **New result:** A single objective that ties together the noise, correction, and capacity results and feeds directly into the SLM workflows named in the source papers.

---

## Coverage Summary Table

| Course topic | Project location | Concrete output |
|---|---|---|
| Probability / random variables | Meth. §1.2, §3 | Probabilistic signal model |
| Expectation, variance, correlation | Meth. §3.1, §4.2 | Bridge to prior σ / $R^2$ numbers |
| Distributions | Meth. §3.3 | Empirical joint $(S,T,V)$ distributions |
| Preprocessing / normalization | Meth. §3.1–§3.2 | Autocorrelation-aware estimation |
| Inference | Meth. §3.2, §7 | Confidence intervals + null tests |
| Entropy | Meth. §4.1, §5.2 | Total / floor uncertainty of sensor |
| Conditional entropy | Meth. §4.1 | Environmental uncertainty removed |
| Mutual information | Meth. §4.2, §5.2, §6.3 | Non-linear contamination metric; bench objective |
| KL divergence | Meth. §4.3 | Distance between validation benches |
| Channel capacity (continuous) | Meth. §6.1 | Distinguishable aging states |
| Binary Symmetric Channel (BSC) | Meth. §6.1b | Aging-alarm reliability $C_{BSC}=1-H_2(p)$ |
| Noise | Meth. §1.2, §6.1 | Unified channel-noise model |
| Description-length selection (MDL) / Kolmogorov complexity | Theory §3.6; Meth. §5.4 | Linear-vs-non-linear correction choice, grounded in $K(x)$ / Occam's razor |
| Estimation (moments/LS/MLE/Bayes) | Meth. §5.1, §6.2 | Estimator ladder + RUL detectability bound |
| Sequential Bayesian estimation (Kalman) / stochastic processes *(extension)* | Theory §3.7; Meth. §6.2 ext.; `sec:res-wiener` | Denoised aging trajectory + closed-form RUL distribution |
| ICA / negentropy / BSS | Meth. §5.5 | Model-free aging-source separation |
| Optimization | Meth. §6.3 | Minimize $I(S;T,V)$ objective |

This mapping is **deliberately selective**: it covers the course topics that genuinely correlate with the aging-sensor problem and contribute a result the prior reliability work could not state — not the full syllabus for its own sake. Topics that would only be exercised superficially (e.g. concrete source-coding codecs, Big Data/streaming tooling) are intentionally omitted. The centerpiece concepts (entropy, conditional entropy, mutual information, KL divergence, capacity, estimation) each map to a concrete, data-backed deliverable that materially extends the existing research.
