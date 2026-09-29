# Analysis pipeline

Tier-1 information-theoretic analysis (see `../05_Execution_Plan.md`).

## Run

```bash
cd analysis
python3 tier1_pipeline.py            # uses ../artigos/Tentative_1_20260524_203756.csv
python3 kl_benches.py                # KL/JS between the two device-B benches
python3 ica_separation.py            # FastICA blind source separation
python3 kalman_rul.py                # Wiener/Kalman denoised trajectory + RUL distribution
python3 make_figures.py              # writes all figures into ../latex/figures/
python3 tier1_pipeline.py path/to/another_log.csv
```

Run in this order: `kalman_rul.py` and `make_figures.py` both import from
`tier1_pipeline.py` (the PVT correction, autocorrelation time), and
`make_figures.py` additionally imports from `kalman_rul.py`, `kl_benches.py`
and `ica_separation.py` so every figure is generated from a single source of
truth. Requires `numpy`, `scipy`, `matplotlib` (no sklearn). `tier1_pipeline.py`
runs in ~4 s on the 768 k-sample log; `kalman_rul.py` in ~1 s (it operates on
~1,224 block-mean points, not the raw 1 Hz series).

## What it does

1. Loads the log, drops link-down dropouts and the first 1 h soak.
2. Estimates the integrated autocorrelation time `tau_int` (Sokal windowing) and
   the **effective sample size** `n_eff = n / (2 tau_int)` — the number that
   actually governs the confidence intervals.
3. `H(S)` (plug-in + Miller–Madow) over the integer slack levels.
4. `I(S;T)`, `I(S;V)`, `I(S;T,V)` by **binned + Miller–Madow**, with a bin-count
   sensitivity sweep, cross-checked by a **KSG (Kraskov)** estimator on a thinned
   subsample.
5. Converts the prior linear `R^2` to a **Gaussian-equivalent MI**
   `-1/2 log2(1-R^2)` and reports how much the measured MI exceeds it (the
   non-linearity result).
6. **Block-bootstrap** 95 % CI for `I(S;T,V)`.

## Outputs

- `results.json` — all scalars, machine-readable.
- `../latex/generated/values.tex` — the same scalars as LaTeX macros, filled in
  place (the paper picks them up automatically; re-running regenerates them).

## Headline results on `Tentative_1` (PID, 214.6 h)

| Quantity | Value |
|---|---|
| post-soak samples / `n_eff` | 768,884 / **1,224** |
| `tau_int` | 314 samples (≈5 min) |
| `H(S)` | 3.43 bits (27 levels) |
| `I(S;T)` / `I(S;V)` | 1.087 / 0.113 bits |
| `I(S;T,V)` binned (MM) | **1.132 bits**, 95% CI [1.091, 1.176] — the headline estimator |
| `I(S;T,V)` KSG | 1.221 bits, own 95% CI [1.156, 1.275] (overlaps the binned CI only narrowly — a characterized estimator gap, not agreement) |
| bin-count sensitivity (12/24/32 bins) | 1.111–1.171 bits (~0.06 bits spread, same order as the bootstrap CI width; no conclusion depends on it) |
| surrogate null floor (p95) | 0.097 bits → measured is **12× the floor** (real, not bias) |
| linear-equivalent MI (`R²=0.738`) | 0.966 bits |
| **measured MI excess over linear (raw series)** | **17 % (binned) – 26 % (KSG)**; still ≈10 % after discounting the estimator's own bias floor |

The `n_eff = 1,224` (not 768,884) is the key honesty point: the 1 Hz series is
heavily autocorrelated, so all confidence statements use `n_eff`.

### Does the raw-series excess survive detrending? (honesty finding, 2026-08-18)

The 17–26 % excess above is measured on the **raw** post-soak series, deliberately
paired with the prior work's own raw `R^2`. Repeating the same MI-vs-Gaussian-equivalent
comparison on the **detrended** series used for PVT correction below answers a
stronger question — is the excess in the *instantaneous* reversible coupling, or in the
slow trend the aging drift and `T,V` happen to share over a 214.6 h campaign?

| Quantity | Value |
|---|---|
| `R²` detrended | 0.640 |
| linear-equivalent MI (detrended) | 0.736 bits |
| `I(S;T,V)` detrended, binned (MM) | 0.596 bits, 95% CI [0.582, 0.632] |
| `I(S;T,V)` detrended, KSG | 0.656 bits, 95% CI [0.622, 0.735] |
| **excess over linear-equivalent (detrended)** | **−19 % (binned) to −11 % (KSG) — a deficit, not an excess** |

Both estimators agree in sign: on the detrended series there is **no** resolvable
non-linear excess. This does not mean the reversible relation is "sub-linear" — for
a residual quantized to a few counts, discrete MI can legitimately sit below the
continuous Gaussian-equivalent (entropy ceiling of the residual + estimator
downward bias at small MI / reduced `n_eff`). The defensible reading: **the
raw-series excess is attributable to the shared aging/environment trend, not to
demonstrated instantaneous non-linear PVT physics.** The MI-over-`R²` methodology
stands; the specific "physics is non-linear, therefore MI > R²" causal claim does
not, and is retracted in the paper (`sections_pt/06_results.tex` §6.1,
`sections_pt/07_discussion.tex` §7.1). See `review/prompt_correcoes_finais_TF.md`
Bloco A/B for the full derivation.

### PVT correction (Stage 4) — reversible coupling, detrended

| Quantity | Value |
|---|---|
| reversible coupling **before** correction | 0.656 bits |
| after **linear** OLS correction | **0.046 bits** (≈ floor) |
| after **non-linear** correction | 0.024 bits |
| **reversible coupling removed (linear)** | **93 %** |
| reversible residual σ (linear) | 0.84 counts (prior PID: 0.73) |
| post-linear `corr(S_corr,T)` / `corr(S_corr,V)` | +0.00 / −0.00 |
| MDL/BIC model selection | **linear** (−404.7 < −394.1) |
| **aging recovery** `corr(S,t) → corr(S_corr,t)` | **−0.35 → −0.73** |

Two methodological points this stage surfaced:
1. **Trend confound.** Residual MI must be measured on *detrended* signals; on
   raw `S_corr` the exposed aging drift inflates the apparent residual coupling.
2. **Aging recovery.** Removing PVT makes the permanent aging trend the dominant
   structure in the residual — the information-recovery thesis, demonstrated.

### Capacity, BSC alarm, RUL bound (Stage 5)

| Quantity | Value |
|---|---|
| corrected aging slope | −18.3 m-cnt/h |
| σ_signal / σ_noise | 1.29 / 0.84 counts → SNR 2.36 |
| effective resolution `C` | 0.87 bits → **1.8 distinguishable aging states** |
| CRLB slope SD (214 h) | 0.39 m-cnt/h |
| **min detectable rate (3σ)** | **1.2 m-cnt/h** (measured slope is ~15× above) |
| **min observation time (3σ)** | **34 h** (≪ 214 h campaign; > prior 23 h runs) |
| Bayesian slope posterior (95% CrI) | −18.2 m-cnt/h, [−19.2, −17.2]; P(slope < 0) ≈ 100% (reading as "aging" is conditioned on the single-device identification assumption) |
| Bayesian min-obs-time (95% CrI) | [33, 36] h |
| BSC alarm, 1 h window | p = 0.49, C_BSC ≈ 0 (coin flip) |
| BSC alarm, 24 h window | p = 0.001, **C_BSC = 0.99 bits** |
| BSC alarm, full campaign | p ≈ 0 (certain) |

The three results are mutually consistent: the BSC per-window reliability crosses
from useless to near-perfect right around the 34 h CRLB minimum observation time.

## KL / Jensen–Shannon between benches (`kl_benches.py`)

Compares the SBCCI (non-PID) bench against the PID reference, on the centered
slack fluctuation (operating points differ, so this isolates noise character).
**These two ~24 h runs are on a different test device than the 214 h aging
campaign** — the KL result speaks to bench fidelity, and is never mixed with the
device-A entropy/MI/RUL results.

| Quantity | Value |
|---|---|
| slack σ: SBCCI / PID | 3.23 / 1.46 counts (2.2×) |
| temp σ: SBCCI / PID | 2.64 / 1.25 °C (2.1×) |
| **KL(SBCCI‖PID)** | **1.94 bits** |
| KL(PID‖SBCCI) | 1.01 bits (asymmetric — KL is not a metric) |
| **Jensen–Shannon** | **0.279 bits** (of max 1) |
| Gaussian closed-form cross-check | 1.67 bits (empirical is higher → non-Gaussian tails) |

The slack-noise ratio tracks the temperature-noise ratio → the contamination is
thermally driven, as the project predicts.

## ICA blind source separation (`ica_separation.py`)

FastICA (negentropy/tanh contrast) on the three observed channels (S, T, V), no
functional form for Delta_PVT assumed.

| Quantity | Value |
|---|---|
| **\|corr(aging-IC, S_corr)\|** | **0.834** (model-free ICA matches the regression aging) |
| corr(aging-IC, t) | −0.575 |
| \|corr(thermal-IC, T)\| | 0.688 |
| excess kurtosis: aging / thermal IC | +5.8 / +29.9 (strongly non-Gaussian) |
| residual inter-IC MI (detrended, max) | 0.571 bits (ideal 0 → separation partial) |
| verdict | recovers |

Honest framing: ICA *corroborates* the regression correction (an assumption-light
route to the same aging component) but does not achieve clean independence,
because the non-stationary trend + heavy tails only approximately meet ICA's
i.i.d. assumptions. The inter-IC MI is measured on **detrended** fluctuations
with the binned estimator — on the raw components KSG returns ~8 bits, an
artifact of the shared slow trend and heavy tails (the same trend confound seen
in the PVT stage).

## Wiener-process degradation + Kalman filter RUL distribution (`kalman_rul.py`)

Extends Stage 5 (RUL): models the corrected residual as a Wiener process with
drift observed through i.i.d. noise, block-averaged into ~`n_eff` quasi-
independent points (block length `2*tau_int`), fits the diffusion `sigma_B^2`
and block observation noise by method of moments (variance-vs-lag), fits the
rate-noise hyperparameter by 1-D MLE on the Kalman filter's own innovation
likelihood, and runs a Kalman/RTS smoother. RUL is then the closed-form
Inverse-Gaussian first-passage time to a threshold `D`, reported at two
already-computed Tier-1 anchors (`D = sigma_noise`, `D = sigma_signal`) since
no calibrated failure threshold exists for this sensor.

| Quantity | Value |
|---|---|
| blocks (~`n_eff`) | 1,224, block length ≈ 628 s |
| Wiener diffusion `sigma_B` | 0.403 counts/√h |
| block obs. noise `R` vs. native `sigma_noise^2` | 0.126 vs. 0.706 counts² (block-averaging reduces noise further than the raw `tau_int` alone) |
| rate-noise MLE | collapses to its floor (~0) → constant-drift preferred, agreeing with the MDL verdict of Stage 4 |
| Kalman/RTS-smoothed rate (end of campaign) | −15.9 m-cnt/h (vs. −18.2/−18.3 m-cnt/h CRLB/Bayesian — consistent order of magnitude) |
| level posterior SD | ≈0.21–0.22 counts, flat across the campaign (steady-state filter) |
| **RUL, D = σ_noise (0.84 counts)** | mean 52.9 h, **median 8.0 h** (heavy right tail) |
| **RUL, D = σ_signal (1.29 counts)** | mean 81.3 h, **median 17.5 h** |

The large mean/median gap is the Inverse Gaussian's right skew, which is
largest exactly when `D` is small relative to `sigma_B` — i.e. in the same
low-SNR regime (SNR = 2.36) that limits the sensor to ~1.8 distinguishable
states in Stage 5. This is offered as a **methodology** for a full RUL
distribution, not a lifetime prediction: see `08_conclusion.tex` for what a
calibrated failure threshold would need.

## Next (optional polish)

- surrogate/null calibration of the MI bias floor; Bayesian correction with
  posterior error bars propagated to the RUL bound.

**Out of scope by decision:** Huffman/LZW codecs, Big Data/streaming tooling
(weak correlation with the research; redundant with the entropy/autocorrelation
results already computed).
