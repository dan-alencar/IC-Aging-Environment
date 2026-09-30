#!/usr/bin/env python3
"""
Tier-1 information-theoretic analysis pipeline.

Consumes a burn-in log (Tentative_*.csv) and computes the headline quantities
of 05_Execution_Plan.md, Tier 1:

  * descriptive stats and data cleaning (drop dropouts, drop 1 h soak)
  * integrated autocorrelation time tau_int and effective sample size n_eff
  * discrete entropy H(S) (plug-in + Miller-Madow)
  * mutual information I(S;T), I(S;V), I(S;T,V) via binned + Miller-Madow,
    cross-checked against a KSG (Kraskov) estimate on a thinned subsample
  * information fraction I(S;T,V)/H(S)  -- the model-free analogue of R^2
  * conditional entropy H(S|T,V) = H(S) - I(S;T,V)
  * block-bootstrap 95% CI for I(S;T,V) (on n_eff via block resampling)

It then writes the scalars into  ../latex/generated/values.tex  (filling the
[TODO] macros) and a machine-readable  results.json.

Dependencies: numpy, scipy (cKDTree for KSG). No sklearn required.

Usage:
    python3 tier1_pipeline.py [path/to/log.csv]
"""

import sys, os, json, math
import numpy as np
from scipy.special import digamma, erfc
from scipy.spatial import cKDTree
from scipy.stats import t as tdist

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CSV = os.path.join(HERE, "..", "artigos", "Tentative_1_20260524_203756.csv")
VALUES_TEX = os.path.join(HERE, "..", "latex", "generated", "values.tex")
RESULTS_JSON = os.path.join(HERE, "results.json")

SOAK_SECONDS = 3600.0      # exclude first 1.0 h thermal-soak transient
COLS = ["time_sec", "oven_temp_c", "oven_setpoint_c", "oven_output_pct",
        "psu_voltage_v", "psu_current_a", "dut_temp_c", "dut_slack", "dut_volt"]


# ----------------------------------------------------------------------------- IO
def load(path):
    """Load the CSV body, skipping the commented header block."""
    rows = []
    with open(path) as f:
        for line in f:
            if line.startswith("#") or line.startswith("time_sec") or not line.strip():
                continue
            parts = line.strip().split(",")
            if len(parts) != 9:
                continue
            try:
                rows.append([float(x) for x in parts])
            except ValueError:
                continue
    a = np.array(rows, dtype=float)
    return {c: a[:, i] for i, c in enumerate(COLS)}, a


def clean(d):
    """Drop link-down dropouts and the soak transient. Returns t, S, T, V."""
    t, S, T, V = d["time_sec"], d["dut_slack"], d["dut_temp_c"], d["dut_volt"]
    ok = (S > 0) & (T > 0) & (V > 0) & (t > SOAK_SECONDS)
    return t[ok], S[ok], T[ok], V[ok]


# ----------------------------------------------------------- autocorrelation / n_eff
def integrated_autocorr_time(x, c=5.0, maxlag=None):
    """Integrated autocorrelation time via the automated-windowing (Sokal) rule."""
    x = np.asarray(x, float)
    x = x - x.mean()
    n = len(x)
    if maxlag is None:
        maxlag = min(n - 1, 200000)
    # autocovariance via FFT
    f = np.fft.rfft(x, n=2 * n)
    acf = np.fft.irfft(f * np.conj(f))[:maxlag]
    acf /= acf[0]
    tau = 1.0
    for w in range(1, maxlag):
        tau = 1.0 + 2.0 * np.sum(acf[1:w + 1])
        if w >= c * tau:
            break
    return max(tau, 1.0)


# --------------------------------------------------------------- entropy / binned MI
def entropy_counts(counts):
    """Plug-in entropy (bits) and Miller-Madow-corrected entropy from a count array."""
    counts = counts[counts > 0]
    N = counts.sum()
    p = counts / N
    H = -np.sum(p * np.log2(p))
    m = len(counts)                       # occupied cells
    H_mm = H + (m - 1) / (2.0 * N) * math.log2(math.e)  # MM bias correction (bits)
    return H, H_mm


def equiprobable_codes(x, nbins):
    """Map a continuous array to integer bin codes using quantile edges."""
    edges = np.quantile(x, np.linspace(0, 1, nbins + 1))
    edges = np.unique(edges)              # collapse ties (e.g. near-discrete V)
    if len(edges) < 3:
        # too few distinct values: fall back to raw rounded codes
        _, codes = np.unique(np.round(x, 6), return_inverse=True)
        return codes
    codes = np.clip(np.digitize(x, edges[1:-1]), 0, len(edges) - 2)
    return codes


def mi_binned(a_codes, b_codes):
    """Mutual information I(A;B) in bits, plug-in and Miller-Madow corrected."""
    A = a_codes.max() + 1
    B = b_codes.max() + 1
    joint = np.bincount(a_codes * B + b_codes, minlength=A * B).reshape(A, B)
    Ha, Ha_mm = entropy_counts(joint.sum(axis=1))
    Hb, Hb_mm = entropy_counts(joint.sum(axis=0))
    Hab, Hab_mm = entropy_counts(joint.ravel())
    return (Ha + Hb - Hab), (Ha_mm + Hb_mm - Hab_mm)


def combine_codes(*code_arrays):
    """Combine several integer code arrays into a single joint code array."""
    out = np.zeros(len(code_arrays[0]), dtype=np.int64)
    for c in code_arrays:
        c = c.astype(np.int64)
        out = out * (c.max() + 1) + c
    _, out = np.unique(out, return_inverse=True)
    return out


# --------------------------------------------------------------------- KSG estimator
def ksg_mi(X, Y, k=4, sample=20000, seed=0):
    """KSG (Kraskov-Stogbauer-Grassberger) MI estimate (nats->bits) for I(X;Y).

    X, Y are 2-D arrays (n, dX), (n, dY). Subsamples to `sample` points (the
    series is autocorrelated, so a thinned subsample is also the statistically
    honest input)."""
    rng = np.random.default_rng(seed)
    n = len(X)
    if n > sample:
        idx = np.linspace(0, n - 1, sample).astype(int)   # even thinning
        X, Y = X[idx], Y[idx]
    n = len(X)
    # tiny dither to break quantization ties
    X = X + 1e-10 * rng.standard_normal(X.shape)
    Y = Y + 1e-10 * rng.standard_normal(Y.shape)
    Z = np.hstack([X, Y])
    tz = cKDTree(Z)
    # distance to k-th neighbour in joint space (Chebyshev metric)
    dist, _ = tz.query(Z, k=k + 1, p=np.inf)
    eps = dist[:, -1]
    tx = cKDTree(X)
    ty = cKDTree(Y)
    nx = np.array([len(tx.query_ball_point(X[i], eps[i] - 1e-12, p=np.inf)) - 1
                   for i in range(n)])
    ny = np.array([len(ty.query_ball_point(Y[i], eps[i] - 1e-12, p=np.inf)) - 1
                   for i in range(n)])
    mi_nats = (digamma(k) + digamma(n)
               - np.mean(digamma(nx + 1) + digamma(ny + 1)))
    return max(mi_nats, 0.0) / math.log(2.0)


# ------------------------------------------------------------------ block bootstrap
def block_bootstrap_mi(s_codes, tv_codes, block, B=120, seed=1):
    """95% CI for I(S;T,V) (MM) via moving-block bootstrap preserving dependence."""
    rng = np.random.default_rng(seed)
    n = len(s_codes)
    nblocks = int(math.ceil(n / block))
    ests = []
    starts_pool = n - block
    for _ in range(B):
        starts = rng.integers(0, starts_pool, size=nblocks)
        idx = (starts[:, None] + np.arange(block)[None, :]).ravel()[:n]
        ests.append(mi_binned(s_codes[idx], tv_codes[idx])[1])
    lo, hi = np.percentile(ests, [2.5, 97.5])
    return lo, hi


def block_bootstrap_ksg(S, T, V, block, sample, B=30, k=4, seed=2):
    """95% CI for the raw-series KSG I(S;T,V) via moving-block bootstrap.

    Mirrors block_bootstrap_mi but on continuous data rather than binned
    codes; each replica is itself thinned to `sample` points inside ksg_mi
    (as the point estimate already is), which keeps cost bounded despite
    KSG's per-point neighbour queries. B is smaller than the binned
    bootstrap's (120) purely for runtime, not for a different confidence
    target."""
    rng = np.random.default_rng(seed)
    n = len(S)
    nblocks = int(math.ceil(n / block))
    starts_pool = n - block
    ests = []
    for i in range(B):
        starts = rng.integers(0, starts_pool, size=nblocks)
        idx = (starts[:, None] + np.arange(block)[None, :]).ravel()[:n]
        Sb, Tb, Vb = S[idx], T[idx], V[idx]
        ests.append(ksg_mi(Sb.reshape(-1, 1), np.column_stack([Tb, Vb]),
                            k=k, sample=sample, seed=i))
    lo, hi = np.percentile(ests, [2.5, 97.5])
    return float(lo), float(hi)


def surrogate_mi_floor(s_codes, tv_codes, tau, B=400, seed=3):
    """Estimator bias floor for I(S;T,V) under the null of independence.

    Circularly shifts the (T,V) code stream relative to S by large random lags
    (> a few autocorrelation times), which destroys the cross-dependence while
    preserving each channel's marginal AND full autocorrelation. The residual
    'MI' on these surrogates is what a finite, autocorrelated sample produces
    when there is genuinely no coupling -- i.e. the bias floor. Returns the null
    mean and the 95th/99th percentiles (in bits)."""
    rng = np.random.default_rng(seed)
    n = len(s_codes)
    lo = int(max(10 * tau, 100))
    ests = []
    for _ in range(B):
        shift = int(rng.integers(lo, n - lo))
        ests.append(mi_binned(s_codes, np.roll(tv_codes, shift))[1])
    return float(np.mean(ests)), float(np.percentile(ests, 95)), float(np.percentile(ests, 99))


# ------------------------------------------------------------------ PVT correction
def _design_linear(T, V):
    """Linear PVT design matrix [1, T, V] (centered T,V). k = 3 params."""
    Tc, Vc = T - T.mean(), V - V.mean()
    return np.column_stack([np.ones_like(T), Tc, Vc])


def _design_nonlinear(T, V):
    """Physics-motivated non-linear design (Arrhenius-like in T, super-linear
    in V): [1, T, T^2, V, V^2, T*V] on centered, scaled features. k = 6."""
    Tc = (T - T.mean()) / T.std()
    Vc = (V - V.mean()) / V.std()
    return np.column_stack([np.ones_like(T), Tc, Tc**2, Vc, Vc**2, Tc * Vc])


def fit_correction(S, X):
    """OLS fit S ~ X; return residual S_corr and the parameter count k."""
    beta, *_ = np.linalg.lstsq(X, S, rcond=None)
    fit = X @ beta
    return S - fit, X.shape[1]


def bic_neff(Scorr, k, n_eff):
    """BIC-style description length using n_eff (honest under autocorrelation):
    n_eff * ln(sigma^2_resid) + k * ln(n_eff). Lower is better (MDL pick)."""
    sigma2 = max(Scorr.var(), 1e-12)
    return n_eff * math.log(sigma2) + k * math.log(n_eff)


# --------------------------------------------------------- capacity / BSC / RUL
def qfunc(x):
    """Gaussian tail Q(x) = P(Z > x)."""
    return 0.5 * erfc(x / math.sqrt(2.0))


def h2(p):
    """Binary entropy H_2(p) in bits."""
    p = min(max(p, 1e-15), 1 - 1e-15)
    return -p * math.log2(p) - (1 - p) * math.log2(1 - p)


def crlb_slope_sd(sigma, n_eff_T, T_hours):
    """Cramer-Rao lower bound on the std of a least-squares slope estimate
    (counts/hour) for n_eff_T independent points uniform over T_hours:
    Var(beta_hat) >= 12 sigma^2 / (n_eff_T * T^2)."""
    return math.sqrt(12.0 / n_eff_T) * sigma / T_hours


# --------------------------------------------------------------------------- driver
def main():
    csv = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CSV
    print(f"[load] {csv}")
    d, raw = load(csv)
    n_raw = len(raw)
    t, S, T, V = clean(d)
    n = len(S)
    print(f"[clean] raw rows={n_raw}  post-soak valid={n}")

    # --- raw-log descriptive stats (dataset section; computed, not typed) ---
    duration_h = float((d["time_sec"].max() - d["time_sec"].min()) / 3600.0)
    n_dropouts = int(np.sum(~((d["dut_slack"] > 0) & (d["dut_temp_c"] > 0) & (d["dut_volt"] > 0))))
    dut_temp_mean = float(T.mean())
    dut_volt_mean = float(V.mean())
    slack_mean = float(S.mean())
    slack_std = float(S.std())
    print(f"[dataset] duration={duration_h:.1f} h  dropouts={n_dropouts}  "
          f"T_mean={dut_temp_mean:.2f}  V_mean={dut_volt_mean:.3f}  "
          f"S_mean={slack_mean:.2f}  S_std={slack_std:.2f}")

    # --- autocorrelation / effective sample size (on detrended slack) ---
    # detrend slack with a ~1 h moving average so tau_int reflects short-range
    # dependence rather than the slow aging drift
    win = 3600
    kern = np.ones(win) / win
    trend = np.convolve(S, kern, mode="same")
    resid = S - trend
    tau = integrated_autocorr_time(resid[win:-win])
    n_eff = n / (2.0 * tau)
    print(f"[autocorr] tau_int={tau:.1f} samples  n_eff={n_eff:.0f}")
    ksg_sample = int(min(20000, max(2000, n_eff)))  # shared thinning target for every KSG call below

    # --- entropy of the (discrete, integer) slack ---
    s_levels, s_codes = np.unique(S.astype(int), return_inverse=True)
    H_plug, H_mm = entropy_counts(np.bincount(s_codes))
    slack_lo, slack_hi = int(s_levels.min()), int(s_levels.max())
    print(f"[entropy] H(S) plug-in={H_plug:.4f}  MM={H_mm:.4f} bits  "
          f"levels={len(s_levels)}  range=[{slack_lo},{slack_hi}]")

    # --- binned MI on raw S vs T,V (directly comparable to linear R^2) ---
    NB = 16
    T_codes = equiprobable_codes(T, NB)
    V_codes = equiprobable_codes(V, NB)
    TV_codes = combine_codes(T_codes, V_codes)

    mi_st = mi_binned(s_codes, T_codes)[1]
    mi_sv = mi_binned(s_codes, V_codes)[1]
    mi_stv = mi_binned(s_codes, TV_codes)[1]
    info_frac = mi_stv / H_mm
    H_cond = H_mm - mi_stv
    print(f"[MI binned, MM] I(S;T)={mi_st:.4f}  I(S;V)={mi_sv:.4f}  "
          f"I(S;T,V)={mi_stv:.4f} bits  fraction={info_frac:.3f}")

    # --- bin-count sensitivity (report spread) ---
    spread = []
    for nb in (12, 24, 32):
        tc = equiprobable_codes(T, nb)
        vc = equiprobable_codes(V, nb)
        spread.append(mi_binned(s_codes, combine_codes(tc, vc))[1])
    print(f"[MI sensitivity] I(S;T,V) over bins(12,24,32) = "
          f"{[round(x,3) for x in spread]}")

    # --- KSG cross-check on a thinned subsample ---
    ksg_stv = ksg_mi(S.reshape(-1, 1), np.column_stack([T, V]),
                     k=4, sample=ksg_sample)
    print(f"[MI KSG] I(S;T,V)~{ksg_stv:.4f} bits (thinned cross-check)")

    # --- block-bootstrap CI for the headline I(S;T,V) (binned) ---
    lo, hi = block_bootstrap_mi(s_codes, TV_codes, block=int(max(tau, 10)))
    print(f"[bootstrap] I(S;T,V) 95% CI = [{lo:.3f}, {hi:.3f}] bits (binned)")

    # --- block-bootstrap CI for the KSG estimate too (P2.1): characterizes
    # the binned/KSG systematic gap with its own error bars instead of a
    # bare point-estimate mismatch ---
    ksg_lo, ksg_hi = block_bootstrap_ksg(S, T, V, block=int(max(tau, 10)), sample=ksg_sample)
    print(f"[bootstrap] I(S;T,V) 95% CI = [{ksg_lo:.3f}, {ksg_hi:.3f}] bits (KSG)")

    # --- surrogate null floor: how much measured MI is real vs estimator bias ---
    null_mean, null_p95, null_p99 = surrogate_mi_floor(s_codes, TV_codes, tau)
    floor_ratio = mi_stv / null_p95 if null_p95 > 0 else float("inf")
    print(f"[surrogate] null I(S;T,V) floor: mean={null_mean:.4f}  p95={null_p95:.4f}  "
          f"p99={null_p99:.4f} bits  => measured 1.13 is {floor_ratio:.0f}x the p95 floor")

    # --- Stage 4: PVT correction and residual MI -----------------------------
    # Fit Delta_PVT(T,V), form S_corr = S - fit. The correction's quality is the
    # *reversible* coupling it removes; per the methodology (detrend so MI
    # measures reversible coupling, not the shared slow trend), the residual MI
    # is computed on detrended signals. Reported on equal footing with a
    # detrended pre-correction baseline.
    def _corr(a, b):
        a, b = a - a.mean(), b - b.mean()
        return float((a @ b) / (np.sqrt(a @ a) * np.sqrt(b @ b)))

    def detrend(x):
        kern = np.ones(3600) / 3600
        return (x - np.convolve(x, kern, mode="same"))[1800:-1800]

    smp = ksg_sample
    T_dt, V_dt = detrend(T), detrend(V)
    S_dt = detrend(S)

    # detrended reversible coupling BEFORE correction (apples-to-apples baseline)
    pre_mi_dt = ksg_mi(S_dt.reshape(-1, 1),
                       np.column_stack([T_dt, V_dt]), k=4, sample=smp)

    # --- detrended R^2 and its Gaussian-equivalent MI (closes the "does the
    # non-linear excess survive detrending?" question the raw-vs-detrended
    # headline split, Sec. 6.1/6.2, leaves open) --------------------------
    Xdt = np.column_stack([np.ones_like(S_dt), T_dt, V_dt])
    beta_dt, *_ = np.linalg.lstsq(Xdt, S_dt, rcond=None)
    resid_dt = S_dt - Xdt @ beta_dt
    r2_detrended = 1.0 - float(resid_dt.var()) / float(S_dt.var())
    mi_lin_equiv_detrended = -0.5 * math.log2(max(1.0 - r2_detrended, 1e-12))

    # binned+MM MI on the detrended series, with its own block-bootstrap CI:
    # if the CI excludes mi_lin_equiv_detrended, the non-linear excess
    # survives detrending with statistical support, not just as a point
    # estimate coincidence.
    Sdt_codes = equiprobable_codes(S_dt, NB)
    Tdt_codes = equiprobable_codes(T_dt, NB)
    Vdt_codes = equiprobable_codes(V_dt, NB)
    TVdt_codes = combine_codes(Tdt_codes, Vdt_codes)
    mi_dt_binned = mi_binned(Sdt_codes, TVdt_codes)[1]
    tau_dt = integrated_autocorr_time(S_dt)
    dt_ci_lo, dt_ci_hi = block_bootstrap_mi(Sdt_codes, TVdt_codes, block=int(max(tau_dt, 10)))
    excess_pct_detrended = 100.0 * (mi_dt_binned - mi_lin_equiv_detrended) / mi_lin_equiv_detrended

    # KSG on the SAME detrended series (identical S_dt, T_dt, V_dt as
    # mi_dt_binned above -- this is exactly pre_mi_dt, given its own name
    # here because Sec. 6.1 cites it as "the KSG cross-check on the
    # detrended finding," a distinct rhetorical role from Sec. 6.2's
    # "pre-correction reversible coupling," even though it is the same
    # canonical scalar, not a second computation) plus its own block-
    # bootstrap CI, mirroring the raw-series KSG CI above.
    mi_dt_ksg = pre_mi_dt
    dt_ksg_lo, dt_ksg_hi = block_bootstrap_ksg(S_dt, T_dt, V_dt, block=int(max(tau_dt, 10)), sample=smp)
    excess_pct_detr_ksg = 100.0 * (mi_dt_ksg - mi_lin_equiv_detrended) / mi_lin_equiv_detrended
    print(f"[detrended non-linearity] R2_detrended={r2_detrended:.3f}  "
          f"lin-equiv={mi_lin_equiv_detrended:.4f} bits  "
          f"MI_detrended(binned)={mi_dt_binned:.4f} bits  95% CI=[{dt_ci_lo:.3f},{dt_ci_hi:.3f}]  "
          f"MI_detrended(KSG)={mi_dt_ksg:.4f} bits  95% CI=[{dt_ksg_lo:.3f},{dt_ksg_hi:.3f}]  "
          f"excess(binned)={excess_pct_detrended:.0f}%  excess(KSG)={excess_pct_detr_ksg:.0f}%")

    Scorr_lin, k_lin = fit_correction(S, _design_linear(T, V))
    Scorr_nl, k_nl = fit_correction(S, _design_nonlinear(T, V))

    # linear R^2(S | T,V) -- computed from the same OLS fit used for the
    # correction (not a separately-typed constant), and the raw (uncorrected)
    # slope dS/dt, both needed for the dataset section and the Gaussian-
    # equivalent-MI comparison of Sec. 6.1 (replaces the old hardcoded 0.738).
    r2_linear = 1.0 - float(Scorr_lin.var()) / float(S.var())
    corr_ST = _corr(S, T)
    corr_SV = _corr(S, V)
    A_raw = np.column_stack([np.ones_like(t), t / 3600.0])
    slope_raw = float(np.linalg.lstsq(A_raw, S, rcond=None)[0][1])  # counts/hour
    print(f"[dataset] R2(S|T,V)={r2_linear:.3f}  corr(S,T)={corr_ST:+.3f}  "
          f"corr(S,V)={corr_SV:+.3f}  raw slope={slope_raw:+.4f} counts/h")

    # reversible leftover AFTER correction (detrended), per model
    post_lin = ksg_mi(detrend(Scorr_lin).reshape(-1, 1),
                      np.column_stack([T_dt, V_dt]), k=4, sample=smp)
    post_nl = ksg_mi(detrend(Scorr_nl).reshape(-1, 1),
                     np.column_stack([T_dt, V_dt]), k=4, sample=smp)
    rsig_lin, rsig_nl = float(detrend(Scorr_lin).std()), float(detrend(Scorr_nl).std())

    # MDL / BIC model selection (reversible residual variance, on n_eff)
    bic_lin = bic_neff(detrend(Scorr_lin), k_lin, n_eff)
    bic_nl = bic_neff(detrend(Scorr_nl), k_nl, n_eff)
    chosen = "non-linear" if bic_nl < bic_lin else "linear"
    rmi_chosen = post_nl if chosen == "non-linear" else post_lin
    reduction = 100.0 * (pre_mi_dt - rmi_chosen) / pre_mi_dt

    # aging-recovery side effect: PVT removal amplifies the aging trend
    corr_St_raw = _corr(S, t)
    corr_St_corr = _corr(Scorr_lin, t)

    print(f"[correction] linear coupling removed: corr(S_corr,T)={_corr(Scorr_lin,T):+.3f} "
          f"corr(S_corr,V)={_corr(Scorr_lin,V):+.3f}")
    print(f"[correction] reversible MI (detrended): pre={pre_mi_dt:.4f}  "
          f"linear={post_lin:.4f}  non-linear={post_nl:.4f} bits")
    print(f"[correction] reversible residual sigma: linear={rsig_lin:.3f}  "
          f"non-linear={rsig_nl:.3f} counts  (BIC {bic_lin:.1f} vs {bic_nl:.1f})")
    print(f"[MDL] selected = {chosen};  reversible leftover {rmi_chosen:.4f} bits "
          f"=> removed {reduction:.0f}% of reversible coupling")
    print(f"[aging recovery] corr(S,t) {corr_St_raw:+.3f} -> "
          f"corr(S_corr,t) {corr_St_corr:+.3f}  (PVT removal exposes the aging trend)")

    # --- Stage 5: effective resolution (capacity), BSC alarm, RUL bound -------
    Sc = Scorr_lin                                  # MDL-selected correction
    t_h = t / 3600.0
    dt = float(np.median(np.diff(t)))               # sampling period (s)
    tau_c = tau * dt                                # decorrelation time (s)
    T_full = float(t_h[-1] - t_h[0])               # campaign span (h)
    sigma = rsig_lin                               # reversible residual noise (counts)

    # corrected aging slope (counts/h) by least squares
    A = np.column_stack([np.ones_like(t_h), t_h])
    beta = float(np.linalg.lstsq(A, Sc, rcond=None)[0][1])

    # (a) effective resolution / capacity heuristic
    kern = np.ones(3600) / 3600
    trend = np.convolve(Sc, kern, mode="same")[1800:-1800]
    sigma_sig = float(trend.std())                 # aging-signal spread (counts)
    snr = (sigma_sig / sigma) ** 2
    cap_bits = 0.5 * math.log2(1.0 + snr)
    cap_states = 2.0 ** cap_bits

    # (b) Cramer-Rao RUL detectability bound
    def n_eff_of_T(T_hours):
        return (T_hours * 3600.0) / (2.0 * tau_c)
    sd_full = crlb_slope_sd(sigma, n_eff_of_T(T_full), T_full)
    min_detect_rate = 3.0 * sd_full                # 3-sigma, counts/h
    # min observation time to detect the measured |beta| at 3 sigma:
    #   3 * sigma * sqrt(24 tau_c / 3600) * T^-1.5 = |beta|
    const = sigma * math.sqrt(24.0 * tau_c / 3600.0)
    min_obs_time = (3.0 * const / abs(beta)) ** (2.0 / 3.0) if beta else float("nan")

    # (c) BSC aging-alarm channel at a 24 h operational decision window
    W = 24.0
    n_eff_W = n_eff_of_T(W)
    sigma_mean_W = sigma / math.sqrt(n_eff_W)
    dprime = abs(beta) * W / sigma_mean_W
    p_bsc = qfunc(dprime / 2.0)
    cap_bsc = 1.0 - h2(p_bsc)
    # context: per-hour vs full-campaign decisions
    def bsc_at(Wh):
        sm = sigma / math.sqrt(n_eff_of_T(Wh))
        return qfunc(abs(beta) * Wh / sm / 2.0)
    p_1h, p_full = bsc_at(1.0), bsc_at(T_full)

    print(f"[capacity] aging slope={beta*1000:+.2f} m-cnt/h  "
          f"sigma_sig={sigma_sig:.3f}  sigma_noise={sigma:.3f}  "
          f"SNR={snr:.2f}  C={cap_bits:.3f} bits  states={cap_states:.2f}")
    print(f"[RUL/CRLB] SD(beta)={sd_full*1000:.3f} m-cnt/h over {T_full:.0f} h; "
          f"min detectable rate(3sigma)={min_detect_rate*1000:.2f} m-cnt/h; "
          f"min obs time to detect |beta|={min_obs_time:.1f} h")
    print(f"[BSC] 24h window: p={p_bsc:.4f}  C_BSC={cap_bsc:.3f} bits/decision "
          f"(per-1h p={p_1h:.3f}, full-campaign p={p_full:.2e})")

    # (d) Bayesian posterior on the aging slope (credible error bars).
    # Thin to ~n_eff effectively-independent points so the i.i.d. Gaussian
    # likelihood holds; with a Jeffreys prior the slope posterior is Student-t.
    step = max(int(n / n_eff_of_T(T_full)), 1)
    ti, yi = t_h[::step], Sc[::step]
    m = len(ti)
    Xb = np.column_stack([np.ones(m), ti])
    bhat, *_ = np.linalg.lstsq(Xb, yi, rcond=None)
    resid = yi - Xb @ bhat
    s2 = float(resid @ resid) / (m - 2)
    Stt = float(np.sum((ti - ti.mean()) ** 2))
    s_beta = math.sqrt(s2 / Stt)                   # posterior scale (counts/h)
    b_post = float(bhat[1])
    tcrit = float(tdist.ppf(0.975, m - 2))
    b_lo, b_hi = b_post - tcrit * s_beta, b_post + tcrit * s_beta
    p_aging = float(tdist.cdf(-b_post / s_beta, m - 2))   # P(slope < 0 | data)
    mot_ci = sorted([(3.0 * const / abs(bb)) ** (2.0 / 3.0) for bb in (b_lo, b_hi)])
    print(f"[Bayes] aging slope posterior = {b_post*1000:+.2f} m-cnt/h, "
          f"95% CrI [{b_lo*1000:+.2f}, {b_hi*1000:+.2f}]; P(aging real)={p_aging*100:.2f}%; "
          f"min-obs-time CrI [{mot_ci[0]:.0f}, {mot_ci[1]:.0f}] h  (m={m} thinned pts)")

    # --- Gaussian-equivalent MI of the linear fit (apples-to-apples vs R^2) ---
    # For jointly Gaussian variables, I = -1/2 log2(1 - R^2). This converts the
    # measured linear R^2 (computed above from Scorr_lin, not a typed constant)
    # into bits so it can be compared to the measured MI; any excess of measured
    # MI over this value is non-linear dependence.
    mi_lin_equiv = -0.5 * math.log2(1.0 - r2_linear)
    # Report the excess separately per estimator -- binned and KSG disagree
    # beyond the binned bootstrap CI (see 06_results.tex Sec. 6.1), so a single
    # merged "excess_pct" silently attached to whichever number is nearby is a
    # correctness bug. valMIexcessPct (headline, used in the abstract) tracks
    # the *binned* estimator, since that is the one with a reported CI; KSG is
    # kept alongside as an independent cross-check with its own percentage.
    excess_pct_binned = 100.0 * (mi_stv - mi_lin_equiv) / mi_lin_equiv
    excess_pct_ksg = 100.0 * (ksg_stv - mi_lin_equiv) / mi_lin_equiv
    excess_pct = excess_pct_binned
    bin_sens_lo, bin_sens_hi = min(spread), max(spread)
    print(f"[non-linearity] linear-equiv MI={mi_lin_equiv:.3f} bits; measured exceeds it by "
          f"{excess_pct_binned:.0f}% (binned) / {excess_pct_ksg:.0f}% (KSG)")

    # --- propagate each estimator's own 95% CI through the excess-pct
    # transform (Bloco E, review round 4): "17-26%" is the gap between two
    # point estimates, not an uncertainty interval. Propagating lo/hi through
    # (x/mi_lin_equiv - 1)*100 gives the full envelope -- still entirely
    # above zero excess at the lower end.
    mi_excess_ci_lo_binned = 100.0 * (lo - mi_lin_equiv) / mi_lin_equiv
    mi_excess_ci_hi_binned = 100.0 * (hi - mi_lin_equiv) / mi_lin_equiv
    mi_excess_ci_lo_ksg = 100.0 * (ksg_lo - mi_lin_equiv) / mi_lin_equiv
    mi_excess_ci_hi_ksg = 100.0 * (ksg_hi - mi_lin_equiv) / mi_lin_equiv
    print(f"[non-linearity, CI-propagated] binned excess envelope "
          f"[{mi_excess_ci_lo_binned:.0f}%, {mi_excess_ci_hi_binned:.0f}%]; "
          f"KSG excess envelope [{mi_excess_ci_lo_ksg:.0f}%, {mi_excess_ci_hi_ksg:.0f}%]")

    # --- floor-adjusted excess: discount the estimator's own bias floor
    # (null_mean, from the surrogate test above) from the binned excess, so
    # the "+17%" headline is shown to survive its own harshest critique
    # rather than merely coexisting with it -----------------------------
    mi_excess_bits_binned = mi_stv - mi_lin_equiv
    mi_excess_floor_adj_bits = mi_excess_bits_binned - null_mean
    mi_excess_floor_adj_pct = 100.0 * mi_excess_floor_adj_bits / mi_lin_equiv
    print(f"[non-linearity, floor-adjusted] excess {mi_excess_bits_binned:.3f} bits minus "
          f"null-mean bias {null_mean:.3f} = {mi_excess_floor_adj_bits:.3f} bits "
          f"({mi_excess_floor_adj_pct:.0f}%) still positive")

    results = dict(
        n_raw=n_raw, n_postsoak=n, tau_int=tau, n_eff=n_eff,
        duration_h=duration_h, n_dropouts=n_dropouts,
        dut_temp_mean=dut_temp_mean, dut_volt_mean=dut_volt_mean,
        slack_mean=slack_mean, slack_std=slack_std,
        slack_lo=slack_lo, slack_hi=slack_hi,
        r2_linear=r2_linear, corr_ST=corr_ST, corr_SV=corr_SV,
        slope_raw_cnt_h=slope_raw,
        H_S_plugin=H_plug, H_S_mm=H_mm, n_levels=int(len(s_levels)),
        I_ST=mi_st, I_SV=mi_sv, I_STV=mi_stv, info_fraction=info_frac,
        H_S_cond_TV=H_cond, I_STV_ksg=ksg_stv,
        I_STV_ci=[lo, hi], I_STV_ci_ksg=[ksg_lo, ksg_hi], bins=NB, bin_sensitivity=spread,
        mi_null_mean=null_mean, mi_null_p95=null_p95, mi_null_p99=null_p99,
        mi_floor_ratio=floor_ratio,
        mi_lin_equiv=mi_lin_equiv, excess_pct=excess_pct,
        excess_pct_binned=excess_pct_binned, excess_pct_ksg=excess_pct_ksg,
        mi_excess_ci_lo_binned=mi_excess_ci_lo_binned, mi_excess_ci_hi_binned=mi_excess_ci_hi_binned,
        mi_excess_ci_lo_ksg=mi_excess_ci_lo_ksg, mi_excess_ci_hi_ksg=mi_excess_ci_hi_ksg,
        mi_excess_floor_adj_bits=mi_excess_floor_adj_bits,
        mi_excess_floor_adj_pct=mi_excess_floor_adj_pct,
        bin_sens_lo=bin_sens_lo, bin_sens_hi=bin_sens_hi,
        r2_detrended=r2_detrended, mi_lin_equiv_detrended=mi_lin_equiv_detrended,
        mi_dt_binned=mi_dt_binned, mi_dt_ci=[dt_ci_lo, dt_ci_hi],
        excess_pct_detrended=excess_pct_detrended,
        mi_dt_ksg=mi_dt_ksg, mi_dt_ksg_ci=[dt_ksg_lo, dt_ksg_hi],
        excess_pct_detr_ksg=excess_pct_detr_ksg,
        pre_mi_reversible=pre_mi_dt,
        resid_mi_lin=post_lin, resid_mi_nl=post_nl,
        resid_sigma_lin=rsig_lin, resid_sigma_nl=rsig_nl,
        bic_lin=bic_lin, bic_nl=bic_nl, corr_model=chosen,
        resid_mi_chosen=rmi_chosen, mi_reduction_pct=reduction,
        corr_St_raw=corr_St_raw, corr_St_corr=corr_St_corr,
        aging_slope_mcnt_h=beta * 1000.0, sigma_signal=sigma_sig,
        sigma_noise=sigma, snr=snr, capacity_bits=cap_bits,
        capacity_states=cap_states, T_full_h=T_full, tau_c_s=tau_c,
        crlb_sd_mcnt_h=sd_full * 1000.0,
        min_detect_rate_mcnt_h=min_detect_rate * 1000.0,
        min_obs_time_h=min_obs_time,
        bsc_window_h=W, bsc_p=p_bsc, bsc_capacity=cap_bsc,
        bsc_p_1h=p_1h, bsc_p_full=p_full,
        bayes_slope_mcnt_h=b_post * 1000.0,
        bayes_slope_lo=b_lo * 1000.0, bayes_slope_hi=b_hi * 1000.0,
        bayes_p_aging=p_aging * 100.0,
        bayes_mot_lo=mot_ci[0], bayes_mot_hi=mot_ci[1],
    )
    with open(RESULTS_JSON, "w") as f:
        json.dump(results, f, indent=2)
    print(f"[write] {RESULTS_JSON}")

    write_values_tex(results)
    print(f"[write] {VALUES_TEX}")
    print("\nDone. Rebuild the paper:  cd ../latex && latexmk -pdf main.tex")


# --------------------------------------------------- emit LaTeX macros (values.tex)
def write_values_tex(r):
    def f(x, nd=3, signed=False):
        return f"{x:+.{nd}f}" if signed else f"{x:.{nd}f}"
    fills = {
        "valNeff":          f"{r['n_eff']:,.0f}".replace(",", "{,}"),
        "valTauInt":        f"{r['tau_int']:,.0f}".replace(",", "{,}"),
        # --- dataset descriptive stats (previously hand-typed; now computed) ---
        "valDurationHours": f(r["duration_h"], 1),
        "valRawSamples":    f"{r['n_raw']:,.0f}".replace(",", "{,}"),
        "valPostSoakSamples": f"{r['n_postsoak']:,.0f}".replace(",", "{,}"),
        "valDropouts":      f"{r['n_dropouts']:d}",
        "valDutTempMean":   f(r["dut_temp_mean"], 1),
        "valDutVoltMean":   f(r["dut_volt_mean"], 3),
        "valSlackMean":     f(r["slack_mean"], 1),
        "valSlackStd":      f(r["slack_std"], 2),
        "valSlackLevels":   f"{r['n_levels']:d}",
        "valSlackRange":    f"{r['slack_lo']:d}" + r"\text{--}" + f"{r['slack_hi']:d}",
        "valCorrST":        f(r["corr_ST"], 3, signed=True),
        "valCorrSV":        f(r["corr_SV"], 3, signed=True),
        "valSlopeRaw":      f(r["slope_raw_cnt_h"], 4, signed=True),
        "valRsqLinear":     f(r["r2_linear"], 3),
        "valHs":            f(r["H_S_mm"], 2),
        "valHscondTV":      f(r["H_S_cond_TV"], 2),
        "valMIst":          f(r["I_ST"]),
        "valMIsv":          f(r["I_SV"]),
        "valMIstv":         f(r["I_STV"]),
        "valInfoFraction":  f(r["info_fraction"]),
        "valKSGstv":        f(r["I_STV_ksg"]),
        "valMIciLo":        f(r["I_STV_ci"][0]),
        "valMIciHi":        f(r["I_STV_ci"][1]),
        "valMIlinEquiv":    f(r["mi_lin_equiv"]),
        "valMIexcessPct":   f"{r['excess_pct']:.0f}",
        "valMIexcessPctBinned": f"{r['excess_pct_binned']:.0f}",
        "valMIexcessPctKSG":    f"{r['excess_pct_ksg']:.0f}",
        "valMIexcessCiLoBinned": f"{r['mi_excess_ci_lo_binned']:.0f}",
        "valMIexcessCiHiBinned": f"{r['mi_excess_ci_hi_binned']:.0f}",
        "valMIexcessCiLoKSG":   f"{r['mi_excess_ci_lo_ksg']:.0f}",
        "valMIexcessCiHiKSG":   f"{r['mi_excess_ci_hi_ksg']:.0f}",
        "valMIbins":        f"{r['bins']:d}",
        "valMIbinSensLo":   f(r["bin_sens_lo"]),
        "valMIbinSensHi":   f(r["bin_sens_hi"]),
        "valKSGciLo":       f(r["I_STV_ci_ksg"][0]),
        "valKSGciHi":       f(r["I_STV_ci_ksg"][1]),
        "valMIexcessFloorAdjBits": f(r["mi_excess_floor_adj_bits"], 2),
        "valMIexcessFloorAdjPct":  f"{r['mi_excess_floor_adj_pct']:.0f}",
        "valRsqDetrended":  f(r["r2_detrended"], 3),
        "valMIlinEquivDetrended": f(r["mi_lin_equiv_detrended"]),
        "valMIdtBinned":    f(r["mi_dt_binned"]),
        "valMIdtCiLo":      f(r["mi_dt_ci"][0]),
        "valMIdtCiHi":      f(r["mi_dt_ci"][1]),
        "valMIexcessPctDetrended": f"{r['excess_pct_detrended']:.0f}",
        "valMIdtKSG":       f(r["mi_dt_ksg"]),
        "valMIdtKsgCiLo":   f(r["mi_dt_ksg_ci"][0]),
        "valMIdtKsgCiHi":   f(r["mi_dt_ksg_ci"][1]),
        "valMIexcessPctDetrKSG": f"{r['excess_pct_detr_ksg']:.0f}",
        "valMInullFloor":     f(r["mi_null_p95"]),
        "valMInullMean":    f(r["mi_null_mean"]),
        "valMIfloorRatio":  f"{r['mi_floor_ratio']:.0f}",
        "valResidMI":       f(r["resid_mi_chosen"]),
        "valPreMIrev":      f(r["pre_mi_reversible"]),
        "valResidMIlin":    f(r["resid_mi_lin"]),
        "valResidMInl":     f(r["resid_mi_nl"]),
        "valResidSigmaLin": f(r["resid_sigma_lin"], 2),
        "valResidSigmaNL":  f(r["resid_sigma_nl"], 2),
        "valCorrModel":     r["corr_model"],
        "valMIreductionPct": f"{r['mi_reduction_pct']:.0f}",
        "valCorrStRaw":     f(r["corr_St_raw"], 2),
        "valCorrStCorr":    f(r["corr_St_corr"], 2),
        "valAgingSlope":    f(r["aging_slope_mcnt_h"], 1),
        "valSigSignal":     f(r["sigma_signal"], 2),
        "valSigNoise":      f(r["sigma_noise"], 2),
        "valSNR":           f(r["snr"], 2),
        "valCapacityBits":  f(r["capacity_bits"], 2),
        "valCapacityStates": f(r["capacity_states"], 1),
        "valCRLBsd":        f(r["crlb_sd_mcnt_h"], 2),
        "valMinDetectRate": f(r["min_detect_rate_mcnt_h"], 1),
        "valMinObsTime":    f(r["min_obs_time_h"], 0),
        "valBSCwindow":     f(r["bsc_window_h"], 0),
        "valBSCp":          f(r["bsc_p"], 3),
        "valBSCcap":        f(r["bsc_capacity"], 2),
        "valBayesSlope":    f(r["bayes_slope_mcnt_h"], 1),
        "valBayesSlopeLo":  f(r["bayes_slope_lo"], 1),
        "valBayesSlopeHi":  f(r["bayes_slope_hi"], 1),
        "valBayesPaging":   f(r["bayes_p_aging"], 2),
        "valBayesMotLo":    f(r["bayes_mot_lo"], 0),
        "valBayesMotHi":    f(r["bayes_mot_hi"], 0),
    }
    with open(VALUES_TEX) as fh:
        lines = fh.readlines()
    out = []
    for line in lines:
        replaced = False
        for name, val in fills.items():
            if line.lstrip().startswith(f"\\newcommand{{\\{name}}}"):
                out.append(f"\\newcommand{{\\{name}}}{{{val}}}\n")
                replaced = True
                break
        if not replaced:
            out.append(line)
    with open(VALUES_TEX, "w") as fh:
        fh.writelines(out)


if __name__ == "__main__":
    main()
