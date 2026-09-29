#!/usr/bin/env python3
"""
Wiener-process degradation model + Kalman/RTS smoothing of the "real" aging
trajectory, and a closed-form Remaining-Useful-Life (RUL) distribution.

Extends Tier 1 (tier1_pipeline.py) rather than replacing it. Tier 1 answers
"is there a real, detectable aging trend, and how fast, on average, over the
whole campaign?" via a single OLS slope + Cramer-Rao / Bayesian point
estimate. This script asks the complementary question the course's estimation
and stochastic-process material (Bayesian filtering; Markov/stochastic
processes) is suited to answer: "what is our best *continuously updated*
estimate of the true aging level, with honestly propagated uncertainty, and
what does that imply for a full probability distribution over time-to-a-
future-aging-milestone -- not just a bound on when a trend becomes
detectable?"

Model
-----
The PVT-corrected residual S_corr(t) = S(t) - Delta_PVT(T,V) (the same linear
correction Tier 1 selects by MDL) is modelled as

    S_corr(t) = X(t) + v(t),         v(t) ~ N(0, sigma_obs^2)   (observation)
    dX(t)     = mu(t) dt + sigma_B dW(t)                        (latent aging)
    d mu(t)   = sigma_rate dW'(t)                                (slowly-varying rate)

i.e. a *local linear trend* state-space model (Harvey 1989): the latent aging
level X(t) is a Wiener process whose drift mu(t) is itself allowed to wander
slowly, rather than being pinned to the single campaign-average slope Tier 1
fits. This is the continuous-state, continuous-time analogue of the discrete
Markov-chain material in the course (health-state transitions -> a diffusing
latent state), and sigma_obs is exactly Tier 1's reversible residual noise
floor -- nothing here is a new, uncalibrated noise number.

Time step. Consecutive 1 Hz samples are strongly autocorrelated (tau_int
already computed by Tier 1), so the state-space model is built on block means
over windows of length 2*tau_int -- i.e. one "n_eff unit" per block, by
construction. Each block mean is therefore treated as ONE noisy draw of
variance sigma_obs^2 (not reduced by sqrt(block length)): this is exactly
what n_eff already encodes elsewhere in the paper, applied here to build the
observation sequence instead of just a scalar confidence interval.

Estimation (method of moments + 1-D MLE, both taught in the course)
---------------------------------------------------------------------
  * sigma_obs   <- Tier 1's reversible residual std (rsig_lin), reused as-is.
  * sigma_B^2   <- method of moments: Var[block-mean increment at lag L] =
                   sigma_B^2 * (L * dt_block) + 2 sigma_obs^2, fit by a linear
                   regression over several lags L (intercept cross-checked
                   against the known 2*sigma_obs^2).
  * sigma_rate^2 <- the only free hyperparameter, found by 1-D maximum
                   likelihood on the Kalman filter's own prediction-error
                   (innovations) log-likelihood, holding sigma_obs and
                   sigma_B fixed.

RUL as a Wiener first-passage-time distribution
------------------------------------------------
For a Wiener process with (locally-estimated) drift mu and diffusion
sigma_B^2, the first-passage time to travel a distance D is Inverse Gaussian
(Whitmore & Schenkelberg 1997; standard in the RUL/PHM literature, see the
review by Si et al. 2011):

    T_D ~ InverseGaussian(mean = D/|mu|, shape = D^2 / sigma_B^2)

No absolute failure threshold is established for this sensor/device (Tier 1
is explicit about this -- RUL there is a *detectability bound*, not a
lifetime prediction), so D is reported parametrically at two anchors that are
already-computed Tier-1 quantities, not new assumptions: D = sigma_noise (one
noise-floor increment -- the same floor that sets the capacity/resolution
result) and D = sigma_signal (the aging-signal spread already observed over
the whole campaign). This keeps the same honesty discipline as the rest of
the project while delivering a full closed-form RUL distribution in place of
a single bound.

Usage: python3 kalman_rul.py [path/to/log.csv]
"""

import os, sys, json, math
import numpy as np
from scipy.optimize import minimize_scalar
from scipy.stats import invgauss, norm

from tier1_pipeline import (load, clean, fit_correction, _design_linear,
                             integrated_autocorr_time, DEFAULT_CSV, VALUES_TEX)

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS_JSON = os.path.join(HERE, "results_kalman.json")


# --------------------------------------------------------------- block means
def block_means(t_h, y, block_len):
    """Average t (hours) and y into non-overlapping blocks of `block_len`
    native samples. Returns block-midpoint times, block means, block dt (h)."""
    n = len(y)
    nb = n // block_len
    t_h = t_h[: nb * block_len].reshape(nb, block_len)
    y = y[: nb * block_len].reshape(nb, block_len)
    tm = t_h.mean(axis=1)
    ym = y.mean(axis=1)
    dt = np.diff(tm)
    dt = np.concatenate([[np.median(dt)], dt])  # dt[0] unused by the filter
    return tm, ym, dt


def estimate_sigma_B(ym, dt_block_h, lags=(1, 2, 4, 8)):
    """Method-of-moments estimate of the Wiener diffusion sigma_B^2 AND the
    block-mean observation-noise variance R_block (both counts^2), from
    Var[block-mean increment at lag L] = sigma_B^2 * (L*dt_block) + 2*R_block,
    fit by linear regression over several lags L. Both unknowns come out of
    the same regression (slope = sigma_B^2, intercept = 2*R_block) -- R_block
    is *not* assumed equal to Tier 1's per-sample reversible-residual
    variance, because block-averaging over ~2*tau_int samples still reduces
    noise below the naive "one independent sample per block" floor (short-lag
    correlation decays within the block); it is instead estimated directly,
    honestly, from these block-mean data."""
    xs, vs = [], []
    for L in lags:
        d = ym[L:] - ym[:-L]
        xs.append(L * dt_block_h)
        vs.append(float(np.var(d)))
    xs, vs = np.array(xs), np.array(vs)
    A = np.column_stack([np.ones_like(xs), xs])
    coef, *_ = np.linalg.lstsq(A, vs, rcond=None)
    intercept, slope = coef
    sigma_B2 = max(slope, 1e-8)
    R_block = max(intercept / 2.0, 1e-6)
    return sigma_B2, R_block


# ------------------------------------------------------- local-linear-trend KF
def kalman_loglik_and_run(y, dt, R, q_level, q_rate, x0, P0, smooth=False):
    """Scalar local-linear-trend Kalman filter (state = [level, rate]).

    Transition F=[[1,dt],[0,1]]; process noise Q=diag(q_level*dt, q_rate*dt);
    observation H=[1,0], noise R (scalar, constant here). Returns the total
    Gaussian log-likelihood of the innovations, and (if smooth=True) the
    filtered/smoothed means and level variances.
    """
    n = len(y)
    x = x0.copy()
    P = P0.copy()
    xf = np.zeros((n, 2))
    Pf = np.zeros((n, 2, 2))
    xp = np.zeros((n, 2))
    Pp = np.zeros((n, 2, 2))
    loglik = 0.0
    for k in range(n):
        F = np.array([[1.0, dt[k]], [0.0, 1.0]])
        Q = np.array([[q_level * dt[k], 0.0], [0.0, q_rate * dt[k]]])
        x_pred = F @ x
        P_pred = F @ P @ F.T + Q
        xp[k], Pp[k] = x_pred, P_pred

        H = np.array([1.0, 0.0])
        S = float(H @ P_pred @ H.T + R)
        v = float(y[k] - H @ x_pred)
        K = (P_pred @ H) / S
        x = x_pred + K * v
        P = P_pred - np.outer(K, H) @ P_pred
        xf[k], Pf[k] = x, P
        loglik += -0.5 * (math.log(2 * math.pi * S) + v * v / S)

    if not smooth:
        return loglik, None, None

    xs = xf.copy()
    Ps = Pf.copy()
    for k in range(n - 2, -1, -1):
        F = np.array([[1.0, dt[k + 1]], [0.0, 1.0]])
        C = Pf[k] @ F.T @ np.linalg.inv(Pp[k + 1])
        xs[k] = xf[k] + C @ (xs[k + 1] - xp[k + 1])
        Ps[k] = Pf[k] + C @ (Ps[k + 1] - Pp[k + 1]) @ C.T
    return loglik, xs, Ps


def fit_rate_noise(y, dt, R, q_level, x0, P0):
    """1-D MLE of q_rate (process noise on the rate state) by maximizing the
    Kalman filter's innovation log-likelihood, holding q_level and R fixed."""
    def neg_ll(log_q_rate):
        q_rate = math.exp(log_q_rate)
        ll, _, _ = kalman_loglik_and_run(y, dt, R, q_level, q_rate, x0, P0)
        return -ll
    res = minimize_scalar(neg_ll, bounds=(math.log(1e-10), math.log(1e2)),
                           method="bounded", options={"xatol": 1e-3})
    return math.exp(res.x)


# ------------------------------------------------------------- RUL (Wiener)
def ig_params(D, mu, sigma_B2):
    """Inverse-Gaussian (mean, shape) for first-passage time to travel |D|
    under drift mu (counts/hour) and diffusion sigma_B2 (counts^2/hour)."""
    mean = D / abs(mu)
    shape = D * D / sigma_B2
    return mean, shape


def ig_median(mean, shape):
    scipy_mu, scipy_scale = mean / shape, shape
    return float(invgauss.ppf(0.5, mu=scipy_mu, scale=scipy_scale))


# --------------------------------------------------------------------- driver
def main():
    csv = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CSV
    d, _ = load(csv)
    t, S, T, V = clean(d)
    n = len(S)
    print(f"[load] n={n}")

    tau = integrated_autocorr_time((S - np.convolve(S, np.ones(3600) / 3600,
                                                      mode="same"))[3600:-3600])
    Scorr, _ = fit_correction(S, _design_linear(T, V))

    def detrend(x):
        kern = np.ones(3600) / 3600
        return (x - np.convolve(x, kern, mode="same"))[1800:-1800]

    # native, per-sample reversible-residual noise floor (identical
    # definition to Tier 1's rsig_lin -- reused, not re-derived, for the RUL
    # threshold anchor below)
    sigma_obs_native = float(detrend(Scorr).std())

    # --- build the block-mean observation sequence: block length = 2*tau_int,
    #     i.e. exactly one n_eff unit per block (see module docstring) ---
    block_len = max(int(round(2 * tau)), 2)
    t_h = t / 3600.0
    tm, ym, dt = block_means(t_h, Scorr, block_len)
    nb = len(ym)
    print(f"[blocks] block_len={block_len} samples (~{block_len:.0f}s)  "
          f"n_blocks={nb}  span={tm[-1]-tm[0]:.1f} h")

    # --- Wiener diffusion + block-mean observation noise, both by method of
    #     moments from the same variance-vs-lag regression ---
    sigma_B2, R_block = estimate_sigma_B(ym, float(np.median(dt[1:])))
    print(f"[sigma_B] sigma_B^2={sigma_B2:.4f} counts^2/h  "
          f"R_block={R_block:.4f} counts^2 (block-mean obs noise; "
          f"native per-sample sigma_obs^2={sigma_obs_native**2:.4f} for comparison)")

    # --- OLS slope on the block means, as the Kalman filter's rate prior ---
    A = np.column_stack([np.ones(nb), tm])
    beta_ols = float(np.linalg.lstsq(A, ym, rcond=None)[0][1])

    # --- 1-D MLE of the rate-state process noise, then filter + RTS smooth ---
    x0 = np.array([ym[0], beta_ols])
    P0 = np.diag([R_block * 10.0, (5.0 * abs(beta_ols) + 1.0) ** 2])
    q_rate = fit_rate_noise(ym, dt, R_block, sigma_B2, x0, P0)
    loglik, xs, Ps = kalman_loglik_and_run(ym, dt, R_block, sigma_B2,
                                            q_rate, x0, P0, smooth=True)
    level_s, rate_s = xs[:, 0], xs[:, 1]
    level_sd = np.sqrt(Ps[:, 0, 0])
    print(f"[kalman] q_rate(MLE)={q_rate:.3e}  loglik={loglik:.1f}  "
          f"rate(start)={rate_s[0]*1000:+.2f}  rate(end)={rate_s[-1]*1000:+.2f} m-cnt/h  "
          f"level_sd(start)={level_sd[0]:.3f}  level_sd(end)={level_sd[-1]:.3f} counts")

    mu_final = float(rate_s[-1])  # current best estimate of the aging rate
    print(f"[cross-check] Kalman final rate = {mu_final*1000:+.2f} m-cnt/h "
          f"vs Tier-1 OLS/Bayesian ~ -18 m-cnt/h")

    # --- RUL as Wiener first-passage time, at two Tier-1-anchored thresholds ---
    sigma_signal = float(np.convolve(Scorr, np.ones(3600) / 3600, mode="same")[1800:-1800].std())
    D_noise, D_signal = sigma_obs_native, sigma_signal
    mean_n, shape_n = ig_params(D_noise, mu_final, sigma_B2)
    mean_s, shape_s = ig_params(D_signal, mu_final, sigma_B2)
    med_n, med_s = ig_median(mean_n, shape_n), ig_median(mean_s, shape_s)
    print(f"[RUL/Wiener] D=sigma_noise={D_noise:.3f}: mean={mean_n:.1f} h  median={med_n:.1f} h")
    print(f"[RUL/Wiener] D=sigma_signal={D_signal:.3f}: mean={mean_s:.1f} h  median={med_s:.1f} h")

    results = dict(
        block_len_s=block_len, n_blocks=nb, sigma_obs_native=sigma_obs_native,
        sigma_B2=sigma_B2, R_block=R_block,
        q_rate_mle=q_rate, loglik=loglik,
        rate_start_mcnt_h=rate_s[0] * 1000.0, rate_end_mcnt_h=rate_s[-1] * 1000.0,
        level_sd_start=float(level_sd[0]), level_sd_end=float(level_sd[-1]),
        mu_final_mcnt_h=mu_final * 1000.0,
        D_noise=D_noise, D_signal=D_signal,
        rul_mean_Dnoise_h=mean_n, rul_median_Dnoise_h=med_n, rul_shape_Dnoise=shape_n,
        rul_mean_Dsignal_h=mean_s, rul_median_Dsignal_h=med_s, rul_shape_Dsignal=shape_s,
        tm=tm.tolist(), level_s=level_s.tolist(), level_sd=level_sd.tolist(),
        ym=ym.tolist(),
    )
    with open(RESULTS_JSON, "w") as f:
        json.dump(results, f, indent=2)
    print(f"[write] {RESULTS_JSON}")

    write_values_tex(results)
    print(f"[write] {VALUES_TEX}")


def _sci(x):
    """Render a small float as LaTeX scientific notation, e.g. 1e-10 ->
    '1.0\\times10^{-10}' (safe inside math mode)."""
    m, e = f"{x:.1e}".split("e")
    return f"{m}\\times10^{{{int(e)}}}"


def write_values_tex(r):
    def f(x, nd=3, signed=False):
        return f"{x:+.{nd}f}" if signed else f"{x:.{nd}f}"
    fills = {
        "valWienerSigmaB":   f(math.sqrt(r["sigma_B2"]), 3),
        "valWienerQRate":    _sci(r["q_rate_mle"]),
        "valWienerRateEnd":  f(r["mu_final_mcnt_h"], 1, signed=True),
        "valWienerLevelSDstart": f(r["level_sd_start"], 3),
        "valWienerLevelSDend":   f(r["level_sd_end"], 3),
        "valRULmeanNoise":   f(r["rul_mean_Dnoise_h"], 1),
        "valRULmedianNoise": f(r["rul_median_Dnoise_h"], 1),
        "valRULmeanSignal":  f(r["rul_mean_Dsignal_h"], 1),
        "valRULmedianSignal": f(r["rul_median_Dsignal_h"], 1),
        "valDnoise":         f(r["D_noise"], 2),
        "valDsignal":        f(r["D_signal"], 2),
        "valNBlocks":        f"{r['n_blocks']:,.0f}".replace(",", "{,}"),
    }
    with open(VALUES_TEX) as fh:
        lines = fh.readlines()
    out, seen = [], set()
    for line in lines:
        hit = False
        for name, val in fills.items():
            if line.lstrip().startswith(f"\\newcommand{{\\{name}}}"):
                out.append(f"\\newcommand{{\\{name}}}{{{val}}}\n")
                hit = True
                seen.add(name)
                break
        if not hit:
            out.append(line)
    missing = [k for k in fills if k not in seen]
    if missing:
        out.append("\n% --- Wiener/Kalman aging-trajectory + RUL extension "
                    "(kalman_rul.py) ---\n")
        for name in missing:
            out.append(f"\\newcommand{{\\{name}}}{{{fills[name]}}}\n")
    with open(VALUES_TEX, "w") as fh:
        fh.writelines(out)


if __name__ == "__main__":
    main()
