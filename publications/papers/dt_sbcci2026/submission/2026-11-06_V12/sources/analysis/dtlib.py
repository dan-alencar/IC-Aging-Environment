"""Shared loaders and estimators for the D&T analysis pipeline.

Every estimator here is cadence-aware: windows and correlation times are given
in SECONDS and converted with each campaign's own sample period, because the
bang-bang logs are 0.5 Hz and the PID logs 1 Hz.

The MI / tau_int / CRLB estimators reproduce
publications/coursework/tf_teoria-da-informacao/analysis/tier1_pipeline.py
(Miller-Madow binned MI on equiprobable bins, KSG k=4 on an evenly thinned
subsample, circular-shift surrogate null, moving-block bootstrap, Sokal
automatic windowing with c=5) so that the 212.6 h numbers can be checked
against TIP7266.
"""
from __future__ import annotations

import io
import math
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.special import digamma, erfc
from scipy.spatial import cKDTree
from scipy.stats import t as tdist

HERE = Path(__file__).resolve().parent
PAPER = HERE.parent
REPO = PAPER.parents[2]
DATA = REPO / "data" / "campaigns"

K_B = 8.617333262e-5          # eV/K
T_USE_C = 55.0                 # use condition (SBCCI 2026 convention)
EA_LIST = (0.5, 0.6, 0.7, 0.8, 0.9)
EA_REF = 0.7
SOAK_S = 3600.0                # thermal-soak exclusion, identical for every run
DETREND_S = 3600.0             # moving-average window used for detrending
PS_PER_COUNT = 19.85           # MMCM dynamic phase-shift step (from sensor spec)


@dataclass
class Campaign:
    key: str
    label: str
    path: Path
    schema: str                # "tcc9" | "legacy"
    bench: str                 # "BB" | "PID"
    cut: str                   # "INV50" | "RCA16"
    die_target_c: float
    commanded_v: float
    note: str = ""
    t: np.ndarray = field(default=None, repr=False)
    S: np.ndarray = field(default=None, repr=False)
    T: np.ndarray = field(default=None, repr=False)
    V: np.ndarray = field(default=None, repr=False)
    extra: dict = field(default_factory=dict, repr=False)
    n_raw: int = 0
    n_dropout: int = 0
    dt: float = 1.0


CAMPAIGNS = {
    "bb23": dict(label="SBCCI 2026 bang-bang 23.08 h", bench="BB", cut="INV50", schema="legacy",
                 path=DATA / "2025-04_sbcci26_bangbang_23h" / "SBCCI_TCC_COMP_ESTABILIZADO.csv",
                 die_target_c=115.0, commanded_v=1.3),
    "pid23": dict(label="SBCCI 2026 PID 23.08 h", bench="PID", cut="INV50", schema="tcc9",
                  path=DATA / "2026-01_sbcci26_pid_23h" / "TCC_SBCCI_COMP_ESTABILIZADO.csv",
                  die_target_c=115.0, commanded_v=1.3),
    "bb164": dict(label="SBCCI 2025 Week-1 bang-bang 164 h", bench="BB", cut="INV50", schema="legacy",
                  path=DATA / "2025-04_sbcci25_week1_bangbang" / "aging-plot-semana1.csv",
                  die_target_c=115.0, commanded_v=1.3),
    "rca212": dict(label="RCA PID 212.6 h", bench="PID", cut="RCA16", schema="tcc9",
                   path=DATA / "2026-05_rca_pid_212h" / "Tentative_1_20260524_203756.csv",
                   die_target_c=125.0, commanded_v=1.4),
}


# --------------------------------------------------------------------------- IO
def _body(path: Path) -> str:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return "\n".join(l for l in lines if l.strip() and not l.startswith("#"))


def read_tcc9(path: Path) -> pd.DataFrame:
    df = pd.read_csv(io.StringIO(_body(path)))
    return df.apply(pd.to_numeric, errors="coerce").dropna()


def read_legacy(path: Path) -> pd.DataFrame:
    df = pd.read_csv(io.StringIO(_body(path)))
    df.columns = ["date", "hour", "temp_m", "slack", "volt_m"]
    ts = pd.to_datetime(df["date"] + " " + df["hour"], format="%d/%m/%Y %H:%M:%S")
    return pd.DataFrame({
        "time_sec": (ts - ts.iloc[0]).dt.total_seconds().to_numpy(),
        "dut_temp_c": df["temp_m"].to_numpy(float) / 1000.0,
        "dut_slack": df["slack"].to_numpy(float),
        "dut_volt": df["volt_m"].to_numpy(float) / 1000.0,
    })


def load(key: str, soak_s: float = SOAK_S) -> Campaign:
    spec = CAMPAIGNS[key]
    c = Campaign(key=key, **spec)
    df = read_tcc9(c.path) if c.schema == "tcc9" else read_legacy(c.path)
    c.n_raw = len(df)
    ok = (df.dut_slack > 0) & (df.dut_temp_c > 0) & (df.dut_volt > 0)
    c.n_dropout = int((~ok).sum())
    df = df[ok]
    c.extra["duration_raw_h"] = float((df.time_sec.max() - df.time_sec.min()) / 3600.0)
    df = df[df.time_sec > df.time_sec.min() + soak_s] if soak_s else df
    c.t = df.time_sec.to_numpy(float)
    c.S = df.dut_slack.to_numpy(float)
    c.T = df.dut_temp_c.to_numpy(float)
    c.V = df.dut_volt.to_numpy(float)
    c.dt = float(np.median(np.diff(c.t)))
    for col in ("oven_temp_c", "oven_setpoint_c", "oven_output_pct", "psu_voltage_v", "psu_current_a"):
        if col in df:
            c.extra[col] = df[col].to_numpy(float)
    return c


# ---------------------------------------------------------------- stress / AF
def af(T_c, ea=EA_REF, tuse_c=T_USE_C):
    return np.exp(ea / K_B * (1.0 / (tuse_c + 273.15) - 1.0 / (np.asarray(T_c) + 273.15)))


def delta_budget(eta, ea=EA_REF, tset_c=115.0):
    """First-order allowed mean die error for AF within a fraction eta (Eq. 2)."""
    Tk = tset_c + 273.15
    return K_B * Tk ** 2 / ea * math.log(1.0 + eta)


# ------------------------------------------------------------- basic helpers
def moving_average(x, win):
    win = max(int(round(win)), 1)
    return np.convolve(x, np.ones(win) / win, mode="same")


def detrend(x, dt, window_s=DETREND_S):
    """x minus its centered moving average; edges (half a window) trimmed."""
    w = int(round(window_s / dt))
    h = w // 2
    return (x - moving_average(x, w))[h:-h]


def ols(X, y):
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    r = y - X @ beta
    return beta, r


def r2(y, X):
    _, r = ols(X, y)
    return 1.0 - r.var() / y.var()


def design(*cols):
    cols = [np.asarray(c, float) - np.mean(c) for c in cols]
    return np.column_stack([np.ones_like(cols[0])] + cols)


def corr(a, b):
    a, b = a - a.mean(), b - b.mean()
    return float(a @ b / math.sqrt((a @ a) * (b @ b)))


# ---------------------------------------------------------- autocorrelation
def _acf(x, maxlag):
    x = np.asarray(x, float) - np.mean(x)
    n = len(x)
    f = np.fft.rfft(x, n=2 * n)
    acf = np.fft.irfft(f * np.conj(f))[:min(n - 1, maxlag)]
    return acf / acf[0]


def tau_int_samples(x, c=5.0, maxlag=200000):
    """Integrated autocorrelation time in samples, Sokal convention:
    tau_int = 1/2 + sum_{k=1}^{M} rho(k), smallest M >= c*tau_int.
    White noise gives 0.5; Var(mean of n) = 2 tau_int sigma^2 / n, so
    n_eff = n / (2 tau_int) and Var(OLS slope over T) = 24 sigma^2 tau_int / T^3."""
    acf = _acf(x, maxlag)
    cs = np.cumsum(acf[1:])
    for w in range(1, len(acf)):
        tau = 0.5 + cs[w - 1]
        if w >= c * tau:
            return max(tau, 0.5)
    return max(0.5 + cs[-1], 0.5)


def tau_int_samples_tip(x, c=5.0, maxlag=200000):
    """TIP7266 convention, kept ONLY to reproduce its published 314 s:
    tau = 1 + 2 sum rho (white = 1), window w >= c*tau. Note: TIP then used
    n_eff = n/(2 tau), which double-counts relative to this convention."""
    acf = _acf(x, maxlag)
    cs = np.cumsum(acf[1:])
    for w in range(1, len(acf)):
        tau = 1.0 + 2.0 * cs[w - 1]
        if w >= c * tau:
            return max(tau, 1.0)
    return max(1.0 + 2.0 * cs[-1], 1.0)


# ------------------------------------------------------------- slopes
def newey_west_slope(t_h, y, lag):
    """OLS slope of y on t (per hour) with Newey-West (Bartlett) SE."""
    X = np.column_stack([np.ones_like(t_h), t_h])
    beta, u = ols(X, y)
    n = len(y)
    XtX_inv = np.linalg.inv(X.T @ X)
    Xu = X * u[:, None]
    S = Xu.T @ Xu
    for L in range(1, lag + 1):
        w = 1.0 - L / (lag + 1.0)
        G = Xu[L:].T @ Xu[:-L]
        S += w * (G + G.T)
    cov = XtX_inv @ S @ XtX_inv
    se = math.sqrt(cov[1, 1])
    return float(beta[1]), se


def bayes_slope(t_h, y, step):
    """Jeffreys-prior slope posterior on decimated samples (Student-t)."""
    ti, yi = t_h[::step], y[::step]
    m = len(ti)
    X = np.column_stack([np.ones(m), ti])
    b, r = ols(X, yi)
    s2 = float(r @ r) / (m - 2)
    sb = math.sqrt(s2 / float(np.sum((ti - ti.mean()) ** 2)))
    tc = float(tdist.ppf(0.975, m - 2))
    return dict(slope=float(b[1]), lo=float(b[1] - tc * sb), hi=float(b[1] + tc * sb), scale=sb, m=m,
                p_neg=float(tdist.cdf(-b[1] / sb, m - 2)))


def crlb_sd(sigma, tau_h, T_h):
    """sqrt(Var(beta)) >= sqrt(24 sigma^2 tau / T^3)  (counts/h)."""
    return math.sqrt(24.0 * sigma ** 2 * tau_h / T_h ** 3)


def t_min(sigma, tau_h, beta):
    """Duration for |beta| to exceed 3 CRLB standard errors (h)."""
    return (216.0 * sigma ** 2 * tau_h / beta ** 2) ** (1.0 / 3.0)


def qfunc(x):
    return 0.5 * erfc(np.asarray(x) / math.sqrt(2.0))


def h2(p):
    p = np.clip(p, 1e-15, 1 - 1e-15)
    return -(p * np.log2(p) + (1 - p) * np.log2(1 - p))


def bsc_capacity(w_h, sigma, tau_h, beta):
    w_h = np.asarray(w_h, float)
    # threshold alarm comparing two adjacent windows of length w: the mean
    # difference is beta*w, each window mean has variance 2 sigma^2 tau / w
    snr = abs(beta) * w_h / (sigma * np.sqrt(4.0 * tau_h / w_h))
    return 1.0 - h2(qfunc(snr / 2.0))


# ---------------------------------------------------------------- entropy / MI
def entropy_counts(counts):
    counts = counts[counts > 0]
    N = counts.sum()
    p = counts / N
    H = -np.sum(p * np.log2(p))
    return H, H + (len(counts) - 1) / (2.0 * N) * math.log2(math.e)


def equiprobable_codes(x, nbins):
    edges = np.unique(np.quantile(x, np.linspace(0, 1, nbins + 1)))
    if len(edges) < 3:
        return np.unique(np.round(x, 6), return_inverse=True)[1]
    return np.clip(np.digitize(x, edges[1:-1]), 0, len(edges) - 2)


def integer_codes(x):
    return np.unique(np.round(x).astype(int), return_inverse=True)[1]


def combine_codes(*arrs):
    out = np.zeros(len(arrs[0]), dtype=np.int64)
    for c in arrs:
        c = c.astype(np.int64)
        out = out * (c.max() + 1) + c
    return np.unique(out, return_inverse=True)[1]


def mi_binned(a, b):
    A, B = a.max() + 1, b.max() + 1
    j = np.bincount(a * B + b, minlength=A * B).reshape(A, B)
    Ha = entropy_counts(j.sum(1))[1]
    Hb = entropy_counts(j.sum(0))[1]
    Hab = entropy_counts(j.ravel())[1]
    return float(Ha + Hb - Hab)


def ksg_mi(X, Y, k=4, sample=20000, seed=0):
    rng = np.random.default_rng(seed)
    X = np.asarray(X, float).reshape(len(X), -1)
    Y = np.asarray(Y, float).reshape(len(Y), -1)
    n = len(X)
    if n > sample:
        idx = np.linspace(0, n - 1, sample).astype(int)
        X, Y = X[idx], Y[idx]
    n = len(X)
    X = X + 1e-10 * rng.standard_normal(X.shape)
    Y = Y + 1e-10 * rng.standard_normal(Y.shape)
    Z = np.hstack([X, Y])
    eps = cKDTree(Z).query(Z, k=k + 1, p=np.inf)[0][:, -1]
    tx, ty = cKDTree(X), cKDTree(Y)
    nx = np.array([len(v) - 1 for v in tx.query_ball_point(X, eps - 1e-12, p=np.inf)])
    ny = np.array([len(v) - 1 for v in ty.query_ball_point(Y, eps - 1e-12, p=np.inf)])
    mi = digamma(k) + digamma(n) - np.mean(digamma(nx + 1) + digamma(ny + 1))
    return max(float(mi), 0.0) / math.log(2.0)


def block_bootstrap(fn, n, block, B, seed, point=None):
    """Moving-block bootstrap 95% CI.

    Resampling duplicates samples, which biases plug-in and KSG MI upward, so
    when the point estimate is given the *basic* interval
    [2*point - q97.5, 2*point - q2.5] is returned (bias-reflected); otherwise
    the percentile interval."""
    rng = np.random.default_rng(seed)
    nb = int(math.ceil(n / block))
    out = []
    for _ in range(B):
        st = rng.integers(0, n - block, size=nb)
        idx = (st[:, None] + np.arange(block)[None, :]).ravel()[:n]
        out.append(fn(idx))
    lo, hi = np.percentile(out, [2.5, 97.5])
    if point is None:
        return [float(lo), float(hi)]
    return [float(max(2 * point - hi, 0.0)), float(2 * point - lo)]


# --------------------------------------------- aggregated-series HAC slopes
def block_means(t, y, agg_s):
    """Non-overlapping block means (reduces 1 Hz series for long-bandwidth HAC)."""
    dt = float(np.median(np.diff(t)))
    b = max(int(round(agg_s / dt)), 1)
    m = len(y) // b
    return t[:m * b].reshape(m, b).mean(1), y[:m * b].reshape(m, b).mean(1)


def hac_slope(t_s, y, agg_s=600.0, bandwidth_h=8.0):
    """OLS slope (per hour) on block means, Newey-West SE with a long bandwidth
    so that slow (hours-scale) residual wander is included in the error."""
    tb, yb = block_means(t_s, y, agg_s)
    lag = max(int(round(bandwidth_h * 3600.0 / agg_s)), 1)
    lag = min(lag, len(yb) - 2)
    return newey_west_slope(tb / 3600.0, yb, lag)


def long_run_variance(t_s, e, block_h):
    """Batch-means long-run variance (cnt^2 * s) = 2 sigma^2 tau for this block."""
    dt = float(np.median(np.diff(t_s)))
    b = int(round(block_h * 3600.0 / dt))
    m = len(e) // b
    if m < 8:
        return float("nan")
    mu = e[:m * b].reshape(m, b).mean(1)
    return float(b * mu.var() * dt)


def t_min_lrv(lrv_cnt2s, beta_cnt_h):
    """3-sigma detection time (h) from a long-run variance: 3*sqrt(12 LRV/T^3) = |beta|."""
    b = abs(beta_cnt_h) / 3600.0
    return (108.0 * lrv_cnt2s / b ** 2) ** (1.0 / 3.0) / 3600.0


def surrogate_null(s, tv, tau_samples, B=400, seed=3):
    rng = np.random.default_rng(seed)
    n = len(s)
    lo = int(max(10 * tau_samples, 100))
    est = [mi_binned(s, np.roll(tv, int(rng.integers(lo, n - lo)))) for _ in range(B)]
    return float(np.mean(est)), float(np.percentile(est, 95))
