#!/usr/bin/env python3
"""D&T analysis pipeline: identical code path for every sensor campaign.

    python analysis/run_analysis.py            # all campaigns
    python analysis/run_analysis.py rca212     # one campaign (for debugging)

Writes generated/results_sensor.json. Definitions (applied to every run):
  * dropouts (S, T or V == 0) removed; first SOAK_S = 1 h excluded;
  * stress stats on the post-soak window; equivalent hours also as the
    full-run trajectory integral (soak included, since it also stresses);
  * PVT model: OLS of S on centered [T, V] over the post-soak window;
  * "raw residual sigma" = std of that OLS residual (SBCCI 2026 definition);
    "reversible sigma" = std of the residual after removing its 1 h moving
    average (TIP7266 definition; used for detectability);
  * tau_int: Sokal windowing (c = 5) on the reversible residual, converted to
    seconds with the run's own cadence;
  * MI: Miller-Madow on integer slack codes vs 16x16 equiprobable (T, V)
    codes; KSG k = 4; surrogate null by circular shift (> 10 tau);
    moving-block bootstrap with block = tau.
"""
from __future__ import annotations

import json
import math
import sys
import time

import numpy as np

import dtlib as L

OUT = L.PAPER / "generated" / "results_sensor.json"
WINDOWS_H = [(1.0, 6.0), (6.0, 12.0), (12.0, 22.5)]   # SBCCI 2026 windows (h since start)
BINS = (12, 16, 24, 32)
NB = 16
B_BOOT = 120
B_KSG = 30
B_NULL = 400


def sbcci_lag(n):
    return int(4 * (n / 100.0) ** (2.0 / 9.0))


# ------------------------------------------------------------------ stress
def stress(c: L.Campaign) -> dict:
    full = L.load(c.key, soak_s=0)
    out = dict(
        n_raw=c.n_raw, n_dropout=c.n_dropout, n_post=len(c.S), cadence_s=c.dt,
        duration_raw_h=c.extra["duration_raw_h"],
        duration_post_h=float((c.t[-1] - c.t[0]) / 3600.0),
        T_mean=float(c.T.mean()), T_sd=float(c.T.std()), T_min=float(c.T.min()), T_max=float(c.T.max()),
        T_mean_full=float(full.T.mean()), T_sd_full=float(full.T.std()),
        die_err=float(c.T.mean() - c.die_target_c),
        V_mean=float(c.V.mean()), V_sd_mV=float(1000 * c.V.std()),
        V_mean_full=float(full.V.mean()), V_sd_full_mV=float(1000 * full.V.std()),
        AF={}, AF_of_mean={}, ripple_pct={}, eqh_full={}, eqh_post={}, AF_full={}, AF_of_mean_full={},
    )
    dt_full = np.diff(full.t, append=full.t[-1] + full.dt)
    dt_post = np.diff(c.t, append=c.t[-1] + c.dt)
    for ea in L.EA_LIST:
        a = L.af(c.T, ea)
        af_full = L.af(full.T, ea)
        k = f"{ea:.1f}"
        out["AF"][k] = float(a.mean())
        out["AF_of_mean"][k] = float(L.af(c.T.mean(), ea))
        out["ripple_pct"][k] = 100.0 * (a.mean() / L.af(c.T.mean(), ea) - 1.0)
        out["AF_full"][k] = float(af_full.mean())
        out["AF_of_mean_full"][k] = float(L.af(full.T.mean(), ea))
        out["eqh_full"][k] = float(np.sum(af_full * dt_full) / 3600.0)
        out["eqh_post"][k] = float(np.sum(a * dt_post) / 3600.0)
    for col in ("oven_temp_c", "oven_setpoint_c", "psu_voltage_v", "psu_current_a"):
        if col in c.extra:
            x = c.extra[col]
            out[col] = dict(mean=float(x.mean()), sd=float(x.std()), min=float(x.min()), max=float(x.max()))
    return out


# ------------------------------------------------------------------- noise
def noise(c: L.Campaign) -> dict:
    t_h = c.t / 3600.0
    X = L.design(c.T, c.V)
    beta, res = L.ols(X, c.S)
    rev = L.detrend(res, c.dt)
    out = dict(
        R2_T=L.r2(c.S, L.design(c.T)), R2_V=L.r2(c.S, L.design(c.V)), R2_TV=L.r2(c.S, X),
        kT_cnt_per_C=float(beta[1]), kV_cnt_per_V=float(beta[2]),
        resid_sd_raw=float(res.std()), resid_sd_rev=float(rev.std()),
        S_mean=float(c.S.mean()), S_sd=float(c.S.std()), S_min=float(c.S.min()), S_max=float(c.S.max()),
        S_levels=int(len(np.unique(c.S))),
        corr_ST=L.corr(c.S, c.T), corr_SV=L.corr(c.S, c.V),
        corr_St_raw=L.corr(c.S, c.t), corr_St_corr=L.corr(res, c.t),
    )
    # sensitivity-normalised (degC-equivalent) reversible noise: transferable across CUTs
    out["resid_rev_degC_equiv"] = out["resid_sd_rev"] / abs(out["kT_cnt_per_C"])
    out["resid_raw_degC_equiv"] = out["resid_sd_raw"] / abs(out["kT_cnt_per_C"])
    wins = []
    for a, b in WINDOWS_H:
        m = (t_h >= a) & (t_h < b)
        if m.sum() < 100 or t_h[m].max() - t_h[m].min() < 0.8 * (b - a):
            continue
        lag = sbcci_lag(int(m.sum()))
        s, se = L.newey_west_slope(t_h[m], res[m], lag)
        wins.append(dict(a=a, b=b, n=int(m.sum()), lag=lag, slope=s, lo=s - 1.96 * se, hi=s + 1.96 * se))
    out["windows"] = wins
    return out, res, rev


# --------------------------------------------------------------- hysteresis
def hysteresis(c: L.Campaign, res: np.ndarray) -> dict:
    """Thermal lag and heating/cooling asymmetry of the PVT residual."""
    w = int(round(300.0 / c.dt))                       # 5-min smoothing for dT/dt sign
    Ts = L.moving_average(c.T, w)
    dTdt = np.gradient(Ts, c.t) * 3600.0               # degC/h
    h = w
    sl = slice(h, len(c.T) - h)
    heat = dTdt[sl] > 0
    T, r = c.T[sl], res[sl]
    edges = np.arange(math.floor(T.min()), math.ceil(T.max()) + 1, 1.0)
    gaps, wts = [], []
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (T >= lo) & (T < hi)
        mh, mc = m & heat, m & ~heat
        if mh.sum() > 200 and mc.sum() > 200:
            gaps.append(r[mh].mean() - r[mc].mean())
            wts.append(m.sum())
    gap = float(np.average(gaps, weights=wts)) if gaps else float("nan")
    # cross-correlation lag of detrended S vs detrended T (slack lags die temperature?)
    Sd = L.detrend(c.S, c.dt)
    Td = L.detrend(c.T, c.dt)
    max_lag = int(round(900.0 / c.dt))
    lags = np.arange(-max_lag, max_lag + 1)
    cc = []
    for k in lags:
        if k >= 0:
            cc.append(L.corr(Sd[k:], Td[:len(Td) - k]))
        else:
            cc.append(L.corr(Sd[:k], Td[-k:]))
    cc = np.array(cc)
    kbest = int(lags[np.argmax(np.abs(cc))])
    # does a dT/dt regressor (first-order thermal-lag model) shrink the residual?
    X2 = L.design(c.T, c.V, dTdt)
    _, res2 = L.ols(X2[sl], c.S[sl])
    return dict(
        gap_heat_minus_cool=gap, n_bins=len(gaps),
        frac_heating=float(heat.mean()),
        xcorr_lag_s=kbest * c.dt, xcorr_at_lag=float(cc[np.argmax(np.abs(cc))]), xcorr_at_0=float(cc[max_lag]),
        resid_sd_raw_with_dTdt=float(res2.std()),
        resid_sd_rev_with_dTdt=float(L.detrend(res2, c.dt).std()),
        resid_sd_raw_same_slice=float(res[sl].std()),
    )


# ---------------------------------------------------------------------- MI
def mutual_information(c: L.Campaign, res: np.ndarray, tau_s: float) -> dict:
    tau_samp = tau_s / c.dt
    blk = int(max(tau_samp, 10))
    n_eff = len(c.S) / (2.0 * tau_samp)
    ksg_n = int(min(20000, max(2000, n_eff)))
    s = L.integer_codes(c.S)
    H_plug, H_mm = L.entropy_counts(np.bincount(s))
    tv = L.combine_codes(L.equiprobable_codes(c.T, NB), L.equiprobable_codes(c.V, NB))
    I_raw = L.mi_binned(s, tv)
    sens = {}
    for nb in BINS:
        sens[str(nb)] = L.mi_binned(s, L.combine_codes(L.equiprobable_codes(c.T, nb), L.equiprobable_codes(c.V, nb)))
    ci = L.block_bootstrap(lambda i: L.mi_binned(s[i], tv[i]), len(s), blk, B_BOOT, 1, point=I_raw)
    null_mean, null_p95 = L.surrogate_null(s, tv, tau_samp, B_NULL)
    ksg_raw = L.ksg_mi(c.S, np.column_stack([c.T, c.V]), sample=ksg_n)

    # detrended (reversible) coupling, before and after linear PVT correction
    Sd, Td, Vd = L.detrend(c.S, c.dt), L.detrend(c.T, c.dt), L.detrend(c.V, c.dt)
    Rd = L.detrend(res, c.dt)
    sdc = L.equiprobable_codes(Sd, NB)
    rdc = L.equiprobable_codes(Rd, NB)
    tvd = L.combine_codes(L.equiprobable_codes(Td, NB), L.equiprobable_codes(Vd, NB))
    I_dt = L.mi_binned(sdc, tvd)
    I_res = L.mi_binned(rdc, tvd)
    ci_dt = L.block_bootstrap(lambda i: L.mi_binned(sdc[i], tvd[i]), len(sdc), blk, B_BOOT, 4, point=I_dt)
    ci_res = L.block_bootstrap(lambda i: L.mi_binned(rdc[i], tvd[i]), len(rdc), blk, B_BOOT, 5, point=I_res)
    null_res_mean, null_res_p95 = L.surrogate_null(rdc, tvd, tau_samp, B_NULL, seed=6)
    ksg_dt = L.ksg_mi(Sd, np.column_stack([Td, Vd]), sample=ksg_n)
    ksg_res = L.ksg_mi(Rd, np.column_stack([Td, Vd]), sample=ksg_n)
    ksg_res_ci = L.block_bootstrap(
        lambda i: L.ksg_mi(Rd[i], np.column_stack([Td[i], Vd[i]]), sample=ksg_n, seed=int(i[0]) % 997),
        len(Rd), blk, B_KSG, 7, point=ksg_res)
    # quantisation-only control: integer-rounded linear PVT model + white noise
    # sized so its residual sigma matches the measured raw residual. Any residual
    # MI it shows is an artefact of integer slack, not physics.
    beta, _ = L.ols(L.design(c.T, c.V), c.S)
    rng = np.random.default_rng(11)
    lin = L.design(c.T, c.V) @ beta
    target = float(res.std())
    sd = target
    for _ in range(6):                                  # match residual sigma after rounding
        Ssim = np.round(lin + sd * rng.standard_normal(len(lin)))
        _, rsim = L.ols(L.design(c.T, c.V), Ssim)
        sd *= target / max(float(rsim.std()), 1e-9)
    Rsim = L.detrend(rsim, c.dt)
    I_res_qsim = L.mi_binned(L.equiprobable_codes(Rsim, NB), tvd)
    H_sd = L.entropy_counts(np.bincount(sdc))[1]
    return dict(
        H_S=H_mm, H_S_plugin=H_plug, I_raw=I_raw, I_raw_ci=ci, I_raw_ksg=ksg_raw,
        I_raw_norm=I_raw / H_mm, bin_sensitivity=sens,
        null_mean=null_mean, null_p95=null_p95,
        I_dt=I_dt, I_dt_ci=ci_dt, I_dt_ksg=ksg_dt,
        I_res=I_res, I_res_ci=ci_res, I_res_ksg=ksg_res, I_res_ksg_ci=ksg_res_ci,
        I_res_null_mean=null_res_mean, I_res_null_p95=null_res_p95,
        I_res_minus_null=I_res - null_res_mean,
        I_res_quant_sim=I_res_qsim, I_res_excess_over_quant=I_res - I_res_qsim,
        H_S_dt=H_sd, I_dt_norm=I_dt / H_sd, I_res_norm=I_res / H_sd,
        removed_pct_ksg=100.0 * (ksg_dt - ksg_res) / ksg_dt if ksg_dt > 0 else float("nan"),
        removed_pct_binned=100.0 * (I_dt - I_res) / I_dt if I_dt > 0 else float("nan"),
        ksg_sample=ksg_n,
    )


# ----------------------------------------------------------- detectability
def detectability(c: L.Campaign, res: np.ndarray, rev: np.ndarray) -> dict:
    t_h = c.t / 3600.0
    tau_samp = L.tau_int_samples(rev)
    tau_s = tau_samp * c.dt
    # TIP7266 definition (raw slack minus 1 h MA, edges trimmed by one window) for cross-check
    w = int(round(L.DETREND_S / c.dt))
    raw_dt = (c.S - L.moving_average(c.S, w))[w:-w]
    tau_tip_s = L.tau_int_samples_tip(raw_dt) * c.dt
    sigma = float(rev.std())
    T_h = float(t_h[-1] - t_h[0])
    n_eff = len(c.S) / (2.0 * tau_samp)
    nw_lag = int(math.ceil(10 * tau_samp))
    b, se = L.newey_west_slope(t_h, res, nw_lag)
    step = max(int(round(2 * tau_samp)), 1)
    bay = L.bayes_slope(t_h, res, step)
    tau_h = tau_s / 3600.0
    crlb = L.crlb_sd(sigma, tau_h, T_h)
    out = dict(
        tau_int_s=tau_s, tau_int_tip_s=tau_tip_s, n_eff=n_eff, sigma=sigma, T_h=T_h,
        beta=b, beta_nw_lo=b - 1.96 * se, beta_nw_hi=b + 1.96 * se, nw_lag=nw_lag,
        bayes=bay, crlb_sd=crlb, floor_3sigma=3 * crlb,
        drift_total_cnt=b * T_h,
        T_min=L.t_min(sigma, tau_h, b),
        T_min_lo=L.t_min(sigma, tau_h, max(abs(bay["lo"]), abs(bay["hi"]))),
        T_min_hi=L.t_min(sigma, tau_h, min(abs(bay["lo"]), abs(bay["hi"]))),
    )
    # long-run variance of the residual about its linear trend (slow wander)
    _, e_lin = L.ols(np.column_stack([np.ones_like(t_h), t_h]), res)
    out["lrv"] = {f"{bh:g}": L.long_run_variance(c.t, e_lin, bh) for bh in (0.25, 1.0, 4.0, 8.0, 16.0)}
    out["lrv_white_equiv"] = 2.0 * sigma ** 2 * tau_s           # what the CRLB model assumes
    out["tau_tip_white_equiv_lrv"] = 2.0 * sigma ** 2 * tau_tip_s
    out["T_min_tip"] = L.t_min(sigma, tau_tip_s / 3600.0, b)          # reproduces TIP (double-counted)
    out["T_min_tip_corrected"] = L.t_min(sigma, tau_tip_s / 2 / 3600.0, b)
    lrv8 = out["lrv"]["8"]
    out["T_min_lrv8"] = L.t_min_lrv(lrv8, b) if lrv8 == lrv8 else float("nan")
    hb, hse = L.hac_slope(c.t, res, 600.0, 8.0)
    out["beta_hac8"] = dict(slope=hb, lo=hb - 1.96 * hse, hi=hb + 1.96 * hse, se=hse)
    # sequential detection: first run length T after which the cumulative
    # slope's HAC 3-sigma interval excludes zero and keeps excluding it
    if T_h > 30:
        ends = np.arange(6.0, T_h + 1e-9, 1.0)
        ok = []
        for Te in ends:
            m = t_h <= t_h[0] + Te
            s_, se_ = L.hac_slope(c.t[m], res[m], 600.0, min(8.0, Te / 4))
            ok.append(abs(s_) > 3 * se_ and np.sign(s_) == np.sign(b))
        ok = np.array(ok)
        first = next((float(ends[i]) for i in range(len(ok)) if ok[i:].all()), float("nan"))
        out["sequential_detect_h"] = first
    # stability of beta: halves, and with the windows around large oven-setpoint moves removed
    mid = t_h[0] + T_h / 2
    for nm, m in (("first_half", t_h < mid), ("second_half", t_h >= mid)):
        s, e = L.newey_west_slope(t_h[m], res[m], nw_lag)
        out[f"beta_{nm}"] = dict(slope=s, lo=s - 1.96 * e, hi=s + 1.96 * e)
    # sublinear (power-law) vs linear drift on decimated samples
    ti, yi = t_h[::step], res[::step]
    best = None
    for n_exp in np.linspace(0.05, 1.5, 146):
        X = np.column_stack([np.ones_like(ti), ti ** n_exp])
        _, r = L.ols(X, yi)
        sse = float(r @ r)
        if best is None or sse < best[1]:
            best = (float(n_exp), sse)
    _, rl = L.ols(np.column_stack([np.ones_like(ti), ti]), yi)
    m = len(ti)
    bic_lin = m * math.log(float(rl @ rl) / m) + 2 * math.log(m)
    bic_pow = m * math.log(best[1] / m) + 3 * math.log(m)
    out["powerlaw"] = dict(n=best[0], bic_linear=bic_lin, bic_power=bic_pow, dbic=bic_lin - bic_pow, m=m)
    # same comparison on 2 h block means (reduces the serial dependence the BIC ignores)
    tb, yb = L.block_means(c.t, res, 7200.0)
    tb = tb / 3600.0
    best_b = None
    for n_exp in np.linspace(0.05, 1.5, 146):
        _, r = L.ols(np.column_stack([np.ones_like(tb), tb ** n_exp]), yb)
        if best_b is None or float(r @ r) < best_b[1]:
            best_b = (float(n_exp), float(r @ r))
    _, rl = L.ols(np.column_stack([np.ones_like(tb), tb]), yb)
    mb = len(tb)
    out["powerlaw_block2h"] = dict(n=best_b[0], m=mb,
                                   dbic=(mb * math.log(float(rl @ rl) / mb) + 2 * math.log(mb))
                                        - (mb * math.log(best_b[1] / mb) + 3 * math.log(mb)))
    return out


# ---------------------------------------------------------- control channels
def controls(c: L.Campaign, res: np.ndarray) -> dict:
    """Is there any logged channel that could act as a readout-drift control?"""
    t_h = c.t / 3600.0
    out = {"available": [k for k in ("oven_temp_c", "oven_setpoint_c", "psu_voltage_v", "psu_current_a") if k in c.extra]}
    if "psu_current_a" in c.extra:
        I = c.extra["psu_current_a"]
        _, rI = L.ols(L.design(c.T, c.V), I)          # current with its T,V dependence removed
        s, se = L.newey_west_slope(t_h, rI, 600)
        out["psu_current_resid_slope_mA_per_h"] = dict(slope=1000 * s, lo=1000 * (s - 1.96 * se), hi=1000 * (s + 1.96 * se))
        out["corr_resid_slack_vs_resid_current"] = L.corr(L.detrend(res, c.dt), L.detrend(rI, c.dt))
    if "oven_setpoint_c" in c.extra:
        sp = c.extra["oven_setpoint_c"]
        steps = np.flatnonzero(np.abs(np.diff(sp)) > 0)
        out["setpoint_changes"] = int(len(steps))
        hrs = np.unique(np.round(t_h[steps + 1], 1))
        out["setpoint_change_hours"] = [float(x) for x in hrs[:200]]
        out["setpoint_levels"] = sorted(float(x) for x in np.unique(sp))[:50]
        # event study: residual mean 30 min after minus 30 min before each setpoint move,
        # against the same statistic at random times (null)
        w = int(round(1800.0 / c.dt))
        def jump(i):
            return float(res[i + 1:i + 1 + w].mean() - res[i + 1 - w:i + 1].mean())
        ok = [i for i in steps if w < i < len(res) - w - 1]
        jumps = np.array([jump(i) for i in ok])
        rng = np.random.default_rng(21)
        null = np.array([jump(int(i)) for i in rng.integers(w + 1, len(res) - w - 2, 2000)])
        out["setpoint_jump"] = dict(n=len(jumps), mean_abs=float(np.abs(jumps).mean()),
                                    null_mean_abs=float(np.abs(null).mean()),
                                    null_p95_abs=float(np.percentile(np.abs(null), 95)),
                                    frac_above_null95=float(np.mean(np.abs(jumps) > np.percentile(np.abs(null), 95))))
    # XADC VCCINT is the regulated variable (PSU trim loop), so it cannot serve as a control
    out["vccint_is_regulated"] = True
    return out


def analyse(key: str) -> dict:
    t0 = time.time()
    c = L.load(key)
    r = dict(key=key, label=c.label, bench=c.bench, cut=c.cut, die_target_c=c.die_target_c,
             commanded_v=c.commanded_v, file=str(c.path.relative_to(L.REPO)))
    r["stress"] = stress(c)
    nz, res, rev = noise(c)
    r["noise"] = nz
    r["detect"] = detectability(c, res, rev)
    r["hysteresis"] = hysteresis(c, res)
    # MI blocks/null shifts use the raw-slack decorrelation time (joint S,T,V
    # dependence is set by the thermal PVT component, not by the white residual)
    r["mi"] = mutual_information(c, res, r["detect"]["tau_int_tip_s"])
    r["controls"] = controls(c, res)
    # first-23.08 h subset of long runs: is the 23 h noise representative?
    if r["stress"]["duration_raw_h"] > 30:
        m = c.t <= c.t[0] + 22.08 * 3600
        X = L.design(c.T[m], c.V[m])
        _, rs = L.ols(X, c.S[m])
        rv = L.detrend(rs, c.dt)
        r["first23h"] = dict(resid_sd_raw=float(rs.std()), resid_sd_rev=float(rv.std()),
                             tau_int_s=L.tau_int_samples(rv) * c.dt, T_mean=float(c.T[m].mean()),
                             T_sd=float(c.T[m].std()), R2_TV=L.r2(c.S[m], X))
    # common-sampling check: decimate 1 Hz logs to 2 s (the coarsest log interval)
    if c.dt < 1.5:
        k = int(round(2.0 / c.dt))
        Sd_, Td_, Vd_ = c.S[::k], c.T[::k], c.V[::k]
        _, rr = L.ols(L.design(Td_, Vd_), Sd_)
        rv = L.detrend(rr, 2.0)
        r["decimated_2s"] = dict(resid_sd_raw=float(rr.std()), resid_sd_rev=float(rv.std()),
                                 tau_int_s=L.tau_int_samples(rv) * 2.0)
    print(f"[{key}] done in {time.time() - t0:.1f} s", flush=True)
    return r


def main(argv):
    keys = argv[1:] or list(L.CAMPAIGNS)
    old = json.loads(OUT.read_text()) if OUT.exists() else {}
    for k in keys:
        old[k] = analyse(k)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(old, indent=1, default=float))
    print(f"[write] {OUT}")


if __name__ == "__main__":
    main(sys.argv)
