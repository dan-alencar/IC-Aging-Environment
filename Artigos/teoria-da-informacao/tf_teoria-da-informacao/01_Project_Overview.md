# Information-Theoretic Characterization of Aging Information and Noise in On-Chip Slack Sensors for Silicon Lifecycle Management

## Project Proposal — Overview Document

---

## 1. Background and Point of Departure

This project builds directly on three existing, correlated research efforts in integrated-circuit reliability:

1. **The auto-tuning aging sensor** (Nogueira et al.), which measures critical-path timing *slack* on a Xilinx Artix-7 FPGA using a dynamically phase-shifted clock, reporting one unit of slack per 19.85 ps phase increment, and which tracks delay degradation under burn-in, temperature, and voltage stress.

2. **The thermal-control fidelity study** (Alencar et al.), which compares a thermostatic bang-bang oven against a closed-loop PID oven on the *same* device and *same* sensor, and shows that the burn-in thermal architecture changes both the delivered acceleration factor and the reversible environmental noise superimposed on the sensor output.

3. **The automated burn-in platform** (Danilo Alencar, TCC), which delivers a low-cost, PID-controlled, multi-threaded acquisition system that logs slack together with synchronized temperature and voltage at 1 Hz, achieving a steady-state thermal standard deviation of σ = 0.40 °C.

Across all three works, a single physical fact recurs: the quantity a slack sensor reports is a **mixture** of a permanent, slowly-drifting aging component and a reversible component driven by instantaneous process, voltage, and temperature (PVT). The second paper formalizes this as:

$$t_{slack}(t,T,V) = t_{slack,aged}(t) - \Delta t_{PVT}(T,V)$$

The existing works quantify the reversible contamination using the **coefficient of determination** ($R^2$) of a linear regression of slack on $T$ and $V$ — for example, reporting that temperature and voltage jointly explain 92.1% of slack variance under bang-bang control but only 59.2% under PID.

## 2. The Gap This Project Addresses

The $R^2$ metric used in the prior work has two limitations that matter precisely in this physical domain:

- **It only captures linear dependence.** Yet the underlying physics is explicitly non-linear: BTI/NBTI degradation is modeled with a super-linear dependence on $V_{DD}$, and the Arrhenius acceleration factor is exponential in inverse temperature. A linear $R^2$ therefore systematically under- or mis-estimates how much of the sensor reading is actually determined by the environment.

- **It does not yield a transferable unit.** "Variance explained" is a model-dependent quantity. It does not directly answer the questions that Silicon Lifecycle Management (SLM) ultimately cares about: *How many distinct aging states can this sensor resolve? How early can a true degradation trend be detected above the reversible noise? How much aging information survives a given burn-in bench?*

Information theory answers exactly these questions, and it answers them with a single transferable currency: **bits**.

## 3. What the Project Is

This project proposes an **information-theoretic measurement layer** placed on top of the existing experimental platform and datasets. It does **not** require new silicon, a new sensor, or a new oven. Its contribution is analytical and methodological: it re-expresses the noise, the correction, and the recoverability of aging information in the language of entropy, mutual information, and channel capacity, and it uses that language to derive quantities the prior work could not.

Concretely, the project treats the on-chip slack sensor as a **noisy communication channel**:

- the **transmitter** is the true, latent physical degradation state of the device;
- the **channel** corrupts that state with reversible PVT fluctuation and with sensor quantization noise (the 19.85 ps least-significant bit);
- the **receiver** seeks to estimate the slow aging trajectory used for remaining-useful-life (RUL) prediction.

Under this framing, the project delivers four quantitative results, each grounded in data the three papers already produce:

1. **An information measure of environmental contamination** — the mutual information $I(\text{slack}; T, V)$ — replacing the linear $R^2$ and capturing the non-linear PVT coupling correctly.

2. **An entropy-based account of PVT correction** — comparing $H(\text{slack})$ to $H(\text{slack} \mid T, V)$ to measure, in bits, how much uncertainty each auxiliary measurement removes, framed as information-theoretic feature selection for sensor fusion.

3. **A channel-capacity estimate of sensor resolving power** — how many distinguishable aging levels the sensor supports per unit time under the bang-bang versus PID thermal regimes, connecting the measured noise (σ = 0.40 °C vs. 3.29 °C; residual 0.73 vs. 0.90 counts) to an effective information rate.

4. **A detectability bound for RUL** — using estimation theory to express the earliest point at which a genuine aging trend rises above the reversible noise floor, given the measured noise statistics.

## 4. Approach in Brief

The work proceeds in five stages that mirror the course's own arc — *acquire → transform → quantify → preserve → infer*:

- **Acquire:** Reuse the synchronized `(slack, T, V, time)` logs that the automated platform generates, for both the bang-bang and PID burn-in campaigns.
- **Transform:** Preprocess and normalize the streams, handle the strong serial correlation intrinsic to a 1 Hz time series, and construct the empirical joint distributions needed for information estimates.
- **Quantify:** Estimate entropy, conditional entropy, and mutual information between the sensor output and the environment; compare thermal regimes.
- **Preserve:** Build and evaluate a PVT-correction estimator, measuring how much environment-coupled information it removes and how much residual signal is genuine aging versus quantization floor (source-coding / rate–distortion view).
- **Infer:** Pose RUL as estimation of a latent monotonic degradation path; derive a noise-limited detectability bound.

## 5. How It Uses the Course

The project is not a superficial relabeling of existing results. Each core course topic — taken directly from the disciplina's *Programa* (núcleos de conteúdo 1–5) — supplies a tool that produces a result the prior reliability work could not state:

- **Probability, random variables, expectation, variance, correlation** (revisão de métricas / pré-processamento) formalize the slack/PVT decomposition and the preprocessing of autocorrelated streams.
- **Entropy, joint and conditional entropy** quantify the uncertainty in the aging estimate before and after PVT correction.
- **Mutual information** replaces $R^2$ as the correct, non-linear measure of environmental contamination.
- **KL divergence (KLD)** compares the slack distributions across thermal regimes and quantifies the distributional cost of a non-compliant bench.
- **Channel capacity and noise** turn the sensor's measured noise into an effective number of resolvable aging states; both the **continuous (Gaussian/Shannon-limit)** capacity and a **Binary Symmetric Channel (BSC)** model of the binary "aging-detected" decision are used — the latter mapping directly onto the failure-detection/prevention goal of the research.
- **Description-length model selection (MDL)** serves as the principled criterion for choosing between the linear and non-linear PVT corrections.
- **Independent Component Analysis, negentropy and blind source separation** are used to attempt an unsupervised separation of the latent aging source from the thermal and voltage sources in the mixed sensor reading — the information-theoretic counterpart of the physical $S = S_{aged} - \Delta_{PVT} + \varepsilon_q$ decomposition, requiring no regression model at all.
- **Estimation (method of moments, least squares, MLE, Bayesian) and optimization** convert all of the above into a PVT-correction estimator, an RUL detectability bound (Cramér–Rao), and an objective for "best" burn-in conditions.

These are chosen because each *correlates strongly with the aging-sensor problem and contributes a result the prior reliability work could not state* — not to tick every box on the syllabus. Topics that would only be exercised superficially (concrete source-coding codecs, Big Data/streaming tooling) are deliberately left out. (The companion documents develop the methodology and the topic-by-topic mapping in full.)

## 6. Contribution: What This Adds to the Existing Research

The application of these techniques advances the prior work in several concrete directions:

- **A correct, transferable noise metric.** Replacing $R^2$ with mutual information gives the reliability community a measure of environmental contamination that assumes no functional form and is expressed in bits rather than in model-dependent variance fractions — valid regardless of whether the underlying coupling turns out to be linear or non-linear. On the raw series (paired with the prior work's own $R^2$), measured MI exceeds the linear-equivalent by 17–26%; **this excess does not survive detrending** (Sec. 6.1 of the paper) and is therefore not demonstrated evidence of the hypothesized instantaneous non-linear PVT physics — it tracks the shared aging/environment trend instead. The metric itself, and its methodological superiority over $R^2$, are unaffected; the specific "physics is non-linear, so MI exceeds $R^2$" causal reading is retracted.

- **A principled definition of "a good burn-in bench."** The project reframes burn-in quality as the *minimization of mutual information between the environment and the sensor output*: every bit the environment writes into the slack reading is a bit of aging information lost. This gives the qualitative claim "PID is a cleaner validation environment" a rigorous unit and an optimization target.

- **A resolution limit for SLM sensors.** A channel-capacity estimate tells designers how many aging states their sensor can actually distinguish under realistic noise — a number directly relevant to adaptive voltage scaling and RUL estimation, which the original works identify as the ultimate consumers of the sensor signal.

- **An honest detectability bound for lifetime prediction.** Rather than overclaiming a prediction from a single short dataset, the project contributes a noise-limited bound on *when* aging becomes detectable, which is exactly the methodological foundation a future multi-device, long-duration RUL study would need.

- **A model-free separation of aging from environment.** Beyond regression-based PVT correction, the project tests whether blind source separation (ICA, driven by negentropy / non-Gaussianity) can recover the latent aging component *without* assuming a functional form for $\Delta_{PVT}(T,V)$. A successful separation would be a qualitatively new result: the aging signal extracted as an independent component rather than as a regression residual.

- **A reusable analysis layer.** Because the method consumes only the synchronized logs the platform already produces, it can be applied to any future campaign, turning the existing low-cost burn-in platform into a generator of information-theoretically characterized aging data.

## 7. Scope and Honesty Caveats

Three limitations are stated up front, consistent with the prior work's own disclosures:

- **The raw-series non-linearity excess does not survive detrending.** Added 2026-08-18 after a third round of independent review (`review/prompt_correcoes_finais_TF.md`): the 17–26% MI-over-$R^2$ excess is measured on the raw series (deliberately, to pair with the prior work's raw $R^2$); on the same detrended series used for PVT correction, MI sits at or below the Gaussian-equivalent (a −19% to −11% deficit, not an excess), for both the binned and KSG estimators. The excess is therefore attributable to the shared aging/environment trend, not demonstrated to be instantaneous non-linear PVT physics. See item 1 in §6 above.

- **Single device, single thermal regime for the new data; the bench comparison is a separate device.** The primary empirical substrate is one long-duration PID campaign (the `Tentative_1` log: ≈214.6 h, ≈0.77 M samples at 1 Hz, DUT held near 125 °C / 1.40 V) on the aging device (**device A**). This duration is far longer than the prior papers' ~23 h runs and *does* reveal a measurable aging drift ($\mathrm{corr}(S,t)\approx-0.35$, raw slope ≈ −0.017 counts/h), which strengthens the RUL story; but a single DUT and a single regime still cannot cross-validate a *permanent* aging trajectory against device-to-device variation. The KL bench-fidelity comparison uses two ≈24 h runs on a **different test device (device B)**; device-A and device-B results are reported separately and never mixed. Any RUL result is framed as a **methodology and a detectability bound**, not a demonstrated multi-device prediction.

- **Estimator fragility on autocorrelated data.** Mutual-information estimation from strongly autocorrelated time series is statistically delicate (MI estimators are biased; the 1 Hz series has heavy serial correlation that the prior work already corrects for with Newey–West methods). The large raw sample count is misleading — the effective sample size $n_{eff}$ is much smaller. Selecting and validating an estimator appropriate to this data, and reporting everything on $n_{eff}$ with block-bootstrap intervals, is treated as an explicit methodological contribution rather than an afterthought.
