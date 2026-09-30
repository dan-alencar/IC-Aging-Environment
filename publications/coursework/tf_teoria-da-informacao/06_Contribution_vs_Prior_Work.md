# Objectives, Applied Techniques, and Contribution Relative to Prior Work

Companion note to `00_Work_Summary.md`, written to answer directly: *what is this
project trying to do, what did each course technique achieve, and how exactly
does it improve on each of the three prior papers in `artigos/`?*

---

## 1. Objectives

Place an **information-theoretic measurement layer** on top of an existing,
already-built accelerated-aging burn-in platform and its `(slack, T, V, time)`
logs — no new silicon, sensor, or oven. The specific goals:

1. Replace the prior work's linear coefficient of determination ($R^2$) with
   **mutual information** as the correct measure of environment→sensor
   contamination, valid where the physics (Arrhenius in $T$, super-linear in
   $V$) is non-linear.
2. Quantify, in bits, how much uncertainty is removed once temperature and
   voltage are logged (an entropy account of PVT correction).
3. Convert the sensor's post-correction noise into an effective **resolution**
   (distinguishable aging states) and an **alarm reliability** figure.
4. Derive a noise-limited **detectability bound** for remaining-useful-life
   (RUL) estimation — a bound and a methodology, not a lifetime prediction.
5. Do all of this with a statistically honest treatment of a short, heavily
   autocorrelated dataset (effective sample size $n_{eff}$, not raw sample
   count).

The unifying idea: treat the slack sensor as a **noisy communication channel**
— latent aging is the transmitter, reversible PVT + quantization is channel
noise, the RUL estimator is the receiver — and let entropy, mutual
information, and capacity do the work that variance-based metrics cannot.

---

## 2. Techniques applied, and what each achieved

| Course technique | Applied to | Result |
|---|---|---|
| **Entropy** $H(S)$ | Total uncertainty of the raw slack reading | $H(S) = 3.43$ bits over 27 discrete slack levels — the uncertainty budget everything else is carved out of |
| **Conditional entropy / mutual information** $I(S;T,V)$ | Environment-sensor coupling (replaces $R^2$) | $1.13$ bits binned (KSG cross-check $1.22$); **exceeds** the Gaussian-equivalent of the prior linear $R^2=0.738$ by **17–26%** on the raw series — real (survives the estimator's bias floor) but does **not** survive detrending (deficit of −19% to −11% on the reversible series), so it demonstrates MI's structural advantage over $R^2$ without demonstrating the hypothesized instantaneous non-linear PVT physics |
| **KL / Jensen–Shannon divergence** | Distributional gap between the SBCCI and PID validation benches | $D_{KL}(\text{SBCCI}\|\text{PID}) = 1.94$ bits (asymmetric, illustrating KL is not a metric); JS $=0.279$ bits — a single transferable "distance between validation environments" |
| **Channel capacity (Gaussian heuristic) + Binary Symmetric Channel** | Post-correction noise floor; the binary aging-alarm decision | SNR $2.36\Rightarrow C=0.87$ bits $\Rightarrow$ **1.8 distinguishable aging states**; alarm reliability climbs from a coin flip (1 h) to $C_{BSC}=0.99$ bits (24 h) |
| **MDL, grounded in Kolmogorov complexity / Occam's razor** | Choosing linear vs. non-linear PVT correction | Selects the **linear** model — reframed not as "the physics is linear" but as "not enough curvature information yet at this single stress point to pay for the extra parameters" |
| **Cramér–Rao bound + Bayesian estimation** | RUL as estimation of a latent aging slope | Min detectable rate **1.2 m-cnt/h**, min observation time **≈34 h** (frequentist); Bayesian posterior agrees (slope $-18.2$ m-cnt/h, 95% CrI, $P(\text{slope}<0)\approx100\%$ — reading as aging is conditioned on the single-device identification assumption) |
| **ICA + negentropy (blind source separation)** | Model-free recovery of the aging component from $(S,T,V)$ alone | Recovered component matches the regression-based correction at $|corr|=0.834$, using none of the measured $T,V$ coupling — independent corroboration |
| **Surrogate/null tests, $n_{eff}$, block-bootstrap** | Statistical honesty on a short, autocorrelated series | Measured MI is **12×** the estimator's own bias floor — proven real, not artifact; every CI and credible interval uses $n_{eff}=1{,}224$, not the raw 768,884 samples |

Deliberately **out of scope**: concrete source-coding codecs (Huffman/LZW),
channel error-correcting codes, and Big Data/streaming tooling — judged to
correlate weakly with this specific research question and redundant with
results already computed.

---

## 3. How it differs from and improves on each prior paper

### `Auto_Tuning_Aging_Sensor_...` (Nogueira et al. — the sensor itself)
That paper **builds and validates the on-chip slack sensor**: it shows the
sensor tracks critical-path delay degradation under burn-in, temperature, and
voltage stress, at $19.85$ ps per slack count on an Artix-7 FPGA. It is a
hardware/validation contribution.

**This work does not touch the sensor.** It takes the sensor's output as a
given noisy signal and asks a question that paper never poses: *how much
information does this reading actually carry, and how much of it is
recoverable noise?* It is a purely analytical layer sitting on top of that
sensor's data.

### `Quantifying_the_Effect_of_Burn_In_Thermal_Control_...` (Alencar et al. — thermal-fidelity study)
This is the paper **most directly superseded on its central metric**. It
compares a bang-bang oven against a closed-loop PID oven on the same device
and sensor, using **linear $R^2$** ($92.1\%$ bang-bang vs.\ $59.2\%$ PID) and
residual standard deviation ($\sigma=0.90$ vs.\ $0.73$ counts) as its figures
of merit for "how clean is this validation environment."

This work shows, formally, why that comparison is incomplete: $\mathrm{Cov}(X,Y)=0$
does not imply independence, so a regression $R^2$ can read as "mostly
explained" a variable that is, in fact, non-linearly and near-fully
determined by its inputs — exactly the case here, since BTI aging is
super-linear in $V_{core}$ and Arrhenius acceleration is exponential in
$1/T$. Mutual information is built from the full joint distribution rather
than a second-moment summary, so it does not have this blind spot, and it is
measured in a **transferable unit (bits)** rather than a variance fraction.
On the raw series, the measured MI exceeds the prior paper's
Gaussian-equivalent MI by 17–26% — real, but (checked honestly on the
detrended, reversible series) not demonstrated to be the specific
super-linear/Arrhenius non-linearity motivating this comparison, since that
excess does not survive removing the shared aging/environment trend. The
argument that stands is the structural one: MI has no linearity blind spot
regardless of whether *this* dataset's coupling turns out to be linear or
not, which is already enough to correct the methodology of the prior
comparison even though this dataset does not settle its physical cause.
On top of that, this work adds three figures of merit the thermal-fidelity
paper never had: a capacity/resolution estimate, a BSC alarm-reliability
model, and a Cramér–Rao/Bayesian RUL detectability bound.

### `Sistema Automatizado de Monitoramento...` (Alencar — TCC / burn-in platform thesis)
That thesis is the **data-generation infrastructure**: the PID-controlled,
multi-threaded acquisition platform that logs slack, temperature, and voltage
synchronized at 1 Hz. Its contribution is the instrument, described and
validated on its own engineering terms (control loop, logging reliability,
automation).

**This work consumes that platform's output as raw material** for an
entirely different kind of analysis — it never modifies or re-validates the
platform itself. Where the TCC treats the logged data descriptively (as a
record that the automation worked), this work treats the same kind of log as
the empirical substrate for entropy, mutual information, capacity, and
RUL-detectability estimation — a new analytical use of data the TCC only
needed to demonstrate acquisition worked.

---

## 4. One-line summary

The three prior papers **built the sensor**, **validated its thermal
fidelity with a linear metric**, and **built the platform that generates its
data**. This work adds the **measurement theory** on top of all three:
turning "variance explained" into bits, and giving an SLM designer a
resolution limit, an alarm-reliability curve, and an honest RUL detectability
bound that none of the three could state.
