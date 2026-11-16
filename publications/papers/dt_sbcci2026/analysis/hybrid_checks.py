#!/usr/bin/env python3
"""Robustness checks requested by the cross-review of the hybrid version.

    python analysis/hybrid_checks.py      -> generated/results_hybrid.json

  1. Detection time as a range: long-run-variance T_min over block lengths
     4/8/16 h with linear or power-law detrending; window-slope W* over strides
     1/2/3 h, with and without the 6 h window; Allan two-window crossing on a
     fine (1 h) averaging-time grid, with the number of windows at each point.
  2. Floor uncertainty: hour-scale HDEV floor of consecutive 23 h segments of
     the week-long thermostatic log and of the long PID run (same-bench spread),
     against the 23 h BB/PID floor ratio.
  3. Early-run detection: HAC slope of the first 24 h of the long run.
  4. Attribution of the slow residual: 30-min block means of the residual
     regressed on die T, oven air and dT/dt (long run) / die T and dT/dt (week log).
  5. Does oven air drift at fixed die T and V (bad-control test applied to air)?
  6. Die-follows-air gain over block length and lag choices, and the resulting
     setpoint-adjusted AF ratio range.
"""
from __future__ import annotations

import json
import math

import numpy as np

import dtlib as L
import timescales as TSM

OUT = L.PAPER / "generated" / "results_hybrid.json"


def detrend_fit(t_h, r, n_pow=None):
    X = np.column_stack([np.ones_like(t_h), t_h if n_pow is None else (t_h + 1.0) ** n_pow])
    return L.ols(X, r)[1]


def lrv_range(c, r, beta, n_pow):
    t_h = (c.t - c.t[0]) / 3600.0
    out = {}
    for name, npw in (("linear", None), ("power", n_pow)):
        e = detrend_fit(t_h, r, npw)
        for bh in (4.0, 8.0, 16.0):
            lrv = L.long_run_variance(c.t, e, bh)
            out[f"{name}_{bh:g}"] = float(L.t_min_lrv(lrv, beta))
    return out


def wstar_variants(c, r, n_pow, beta):
    out = {}
    for stride in (1.0, 2.0, 3.0):
        for drop6 in (False, True):
            Wl = (12, 24, 34, 48, 72, 96) if drop6 else (6, 12, 24, 34, 48, 72, 96)
            _, _, Ws, sd = TSM.window_slopes(c, r, n_pow, W_list=Wl, stride_h=stride)
            lw, ls_ = np.log(Ws), np.log(3 * sd)
            tgt = math.log(abs(beta)); w = float("nan")
            for i in range(len(Ws) - 1):
                if ls_[i] >= tgt >= ls_[i + 1]:
                    f = (ls_[i] - tgt) / (ls_[i] - ls_[i + 1]); w = float(math.exp(lw[i] + f * (lw[i + 1] - lw[i]))); break
            out[f"s{stride:g}_{'no6' if drop6 else 'all'}"] = w
    return out


def allan_fine(c, r, beta):
    T_s = c.t[-1] - c.t[0]
    taus = np.arange(3600.0, T_s / 3.0, 3600.0)
    h = TSM.ohdev(r, c.dt, taus)
    z = abs(beta) / 3600.0 * taus / (math.sqrt(2.0) * h)
    ok = np.isfinite(z)
    taus, z = taus[ok], z[ok]
    i1 = int(np.argmax(z >= 1)); i3 = int(np.argmax(z >= 3)) if (z >= 3).any() else None
    nwin = lambda tau: T_s / tau
    return dict(cross_h=taus[i1] / 3600, three_h=(taus[i3] / 3600) if i3 is not None else float("nan"),
                n_windows_three=nwin(taus[i3]) if i3 is not None else float("nan"))


def segment_floors(key, seg_h=23.0):
    c = L.load(key)
    t_h = (c.t - c.t[0]) / 3600.0
    floors = []
    a = 0.0
    while a + seg_h <= t_h[-1] + 1e-9:
        m = (t_h >= a) & (t_h < a + seg_h)
        rm = L.ols(L.design(c.T[m], c.V[m]), c.S[m])[1]          # PVT fit within the segment
        taus = TSM.tau_grid(c.dt, seg_h * 3600)
        h = TSM.ohdev(rm, c.dt, taus)
        floors.append(TSM.band_median(taus, h, *TSM.FLOOR_BAND_H))
        a += seg_h
    return floors


def early_slope(c, r, hours=24.0):
    m = (c.t - c.t[0]) <= hours * 3600
    s, se = L.hac_slope(c.t[m], r[m], 600.0, 8.0)
    return dict(slope=s, se=se, z=abs(s) / se)


def slow_attribution(c, r, with_air=True, block_s=1800.0):
    tb, rb = L.block_means(c.t, r, block_s)
    Tb = L.block_means(c.t, c.T, block_s)[1]
    cols = [Tb, np.gradient(Tb, tb)]
    if with_air:
        cols.append(L.block_means(c.t, c.extra["oven_temp_c"], block_s)[1])
    rb = rb - np.polyval(np.polyfit(tb, rb, 1), tb)          # slow residual about its trend
    return dict(r2=float(L.r2(rb, L.design(*cols))), corr_T=L.corr(rb, Tb))


def slow_attribution_fastband(c, block_s=1800.0):
    """PVT sensitivities estimated on the fast band only (1 h moving average removed),
    so the slow residual is not orthogonal to T by construction."""
    w = int(round(3600.0 / c.dt))
    hp = lambda x: x - L.moving_average(x, w)
    b = L.ols(L.design(hp(c.T), hp(c.V)), hp(c.S))[0]
    r = c.S - b[1] * c.T - b[2] * c.V
    tb, rb = L.block_means(c.t, r, block_s)
    Tb = L.block_means(c.t, c.T, block_s)[1]
    Ob = L.block_means(c.t, c.extra["oven_temp_c"], block_s)[1]
    rb = rb - np.polyval(np.polyfit(tb, rb, 1), tb)
    return dict(r2_T=float(L.r2(rb, L.design(Tb))), r2_all=float(L.r2(rb, L.design(Tb, np.gradient(Tb, tb), Ob))))


def af_ratio_low_ea():
    bb, pid = L.load("bb23", soak_s=0), L.load("pid23", soak_s=0)
    return {f"{ea:g}": float(L.af(pid.T, ea).mean() / L.af(bb.T, ea).mean()) for ea in (0.1, 0.2, 0.3)}


def air_drift_at_fixed_TV(c):
    tb = L.block_means(c.t, c.S, 3600.0)[0] / 3600.0
    bm = lambda x: L.block_means(c.t, x, 3600.0)[1]
    Tb, Vb, Ob = bm(c.T), bm(c.V), bm(c.extra["oven_temp_c"])
    X = np.column_stack([np.ones_like(tb), Tb - Tb.mean(), Vb - Vb.mean(), tb - tb.mean()])
    b = L.ols(X, Ob)[0]
    return dict(per_h=float(b[3]), total=float(b[3] * (tb[-1] - tb[0])))


def gain_range(c, sp_offset):
    O = c.extra["oven_temp_c"]
    gains = {}
    for bs in (900.0, 1800.0, 3600.0):
        tb, Tb = L.block_means(c.t, c.T, bs)
        Ob = L.block_means(c.t, O, bs)[1]
        dT, dO = np.diff(Tb), np.diff(Ob)
        for lag in range(0, 5):
            Y = dT[lag:]
            X = np.column_stack([np.ones(len(Y))] + [dO[lag - k:len(dO) - k] for k in range(lag + 1)])
            gains[f"{bs:g}_{lag}"] = float(L.ols(X, Y)[0][1:].sum())
    bb = L.load("bb23", soak_s=0)
    R = json.loads((L.PAPER / "generated" / "results_sensor.json").read_text())
    af_pid = R["pid23"]["stress"]["AF_full"]["0.7"]
    ratio = {k: af_pid / float(L.af(bb.T + g * sp_offset, 0.7).mean()) for k, g in gains.items()}
    return dict(gains=gains, gain_min=min(gains.values()), gain_max=max(gains.values()),
                ratio_min=min(ratio.values()), ratio_max=max(ratio.values()),
                ratio_gain1=af_pid / float(L.af(bb.T + sp_offset, 0.7).mean()))


def detection_suite(key):
    """Same detection estimators as for PID-214, applied to another log (used for BB-164)."""
    R = json.loads((L.PAPER / "generated" / "results_sensor.json").read_text())
    det = R[key]["detect"]
    beta, n_pow = det["beta_hac8"]["slope"], det["powerlaw_block2h"]["n"]
    c = L.load(key)
    _, r = TSM.residual(c)
    out = dict(beta=beta, n=n_pow, sigma=det["sigma"], tau_s=det["tau_int_s"])
    out["t_white"] = float(L.t_min(det["sigma"], det["tau_int_s"] / 3600.0, beta))
    out["lrv"] = lrv_range(c, r, beta, n_pow)
    out["wstar"] = wstar_variants(c, r, n_pow, beta)
    T_s = c.t[-1] - c.t[0]
    taus = TSM.tau_grid(c.dt, T_s)
    h = TSM.ohdev(r, c.dt, taus)
    fl = TSM.band_median(taus, h, *TSM.FLOOR_BAND_H); pl = TSM.band_median(taus, h, 6.0, 30.0)
    k = 3 * math.sqrt(2) / abs(beta)
    out.update(floor=fl, plateau=pl, run_floor=2 * k * fl, run_plateau=2 * k * pl, duration_h=T_s / 3600.0)
    vals = list(out["lrv"].values()) + [v for v in out["wstar"].values() if math.isfinite(v)] + [out["run_floor"], out["run_plateau"]]
    out["det_lo"], out["det_hi"] = min(vals), max(vals)
    return out


def wander_vs_setpoint(block_s=3600.0, win_h=3.0):
    """Is PID-214's hour-scale die wander concentrated near outer-loop setpoint moves?
    Hourly die-temperature means, detrended; |hour-to-hour change| inside +-win_h of a move vs. elsewhere."""
    from scipy.stats import mannwhitneyu
    c = L.load("rca212")
    tb, Tb = L.block_means(c.t, c.T, block_s)
    rb = L.block_means(c.t, TSM.residual(c)[1], block_s)[1]
    sp = c.extra["oven_setpoint_c"]
    moves = c.t[1:][np.diff(sp) != 0]
    near = np.array([np.any(np.abs(moves - t) <= win_h * 3600) for t in tb[1:]])
    dT, dr = np.abs(np.diff(Tb)), np.abs(np.diff(rb))
    out = dict(n_near=int(near.sum()), n_far=int((~near).sum()),
               dT_near=float(np.median(dT[near])), dT_far=float(np.median(dT[~near])),
               dr_near=float(np.median(dr[near])), dr_far=float(np.median(dr[~near])))
    out["p_T"] = float(mannwhitneyu(dT[near], dT[~near]).pvalue)
    out["p_r"] = float(mannwhitneyu(dr[near], dr[~near]).pvalue)
    # circular-shift permutation: shift all step times by one random offset (mod run length),
    # which keeps the steps' clustering and the series' autocorrelation; statistic = median gap
    T0, T1 = c.t[0], c.t[-1]; span = T1 - T0
    tt = tb[1:]
    def gap(mv, x):
        nr = np.array([np.any(np.abs(mv - t) <= win_h * 3600) for t in tt])
        if nr.all() or (~nr).all():
            return 0.0
        return float(np.median(x[nr]) - np.median(x[~nr]))
    obsT, obsR = gap(moves, dT), gap(moves, dr)
    rng = np.random.default_rng(7); B = 2000; geT = geR = 0
    for _ in range(B):
        off = rng.uniform(0, span)
        mv = T0 + ((moves - T0 + off) % span)
        geT += gap(mv, dT) >= obsT; geR += gap(mv, dr) >= obsR
    out.update(perm_B=B, perm_p_T=(geT + 1) / (B + 1), perm_p_r=(geR + 1) / (B + 1))
    return out


def floor_excluding_steps(after_h=3.0):
    """PID-214 floor and Hadamard run length with the hours after each setpoint step masked:
    HDEV computed on contiguous segments that avoid [step, step + after_h], pooled by
    averaging the squared second differences across segments."""
    c = L.load("rca212")
    _, r = TSM.residual(c)
    sp = c.extra["oven_setpoint_c"]
    steps = c.t[1:][np.diff(sp) != 0]
    bad = np.zeros(len(c.t), bool)
    for s0 in steps:
        bad |= (c.t >= s0) & (c.t < s0 + after_h * 3600)
    taus = np.array([3600.0 * h for h in (1, 1.5, 2, 3, 4, 6, 8, 12, 16, 24, 30)])
    num = np.zeros(len(taus)); den = np.zeros(len(taus))
    # contiguous good segments
    idx = np.where(~bad)[0]
    br = np.where(np.diff(idx) > 1)[0]
    segs = np.split(idx, br + 1)
    for sg in segs:
        y = r[sg]
        cs = np.concatenate([[0.0], np.cumsum(y)])
        for k, tau in enumerate(taus):
            m = int(round(tau / c.dt))
            if 3 * m > len(y) - 1:
                continue
            yb = (cs[m:] - cs[:-m]) / m
            d = yb[2 * m:] - 2 * yb[m:-m] + yb[:-2 * m]
            num[k] += np.sum(d ** 2); den[k] += len(d)
    h = np.sqrt(num / np.maximum(den, 1) / 6.0); h[den == 0] = np.nan
    fl = float(np.nanmedian(h[(taus >= 3600) & (taus <= 4 * 3600)]))
    pl = float(np.nanmedian(h[(taus >= 6 * 3600) & (taus <= 30 * 3600)]))
    R = json.loads((L.PAPER / "generated" / "results_sensor.json").read_text())
    beta = abs(R["rca212"]["detect"]["beta_hac8"]["slope"])
    k = 2 * 3 * math.sqrt(2) / beta
    return dict(frac_masked=float(bad.mean()), floor=fl, plateau=pl, run_floor=k * fl, run_plateau=k * pl)


def floor_after_powerlaw():
    """PID-214 HDEV levels after subtracting the fitted power-law drift from the residual."""
    c = L.load("rca212")
    _, r = TSM.residual(c)
    R = json.loads((L.PAPER / "generated" / "results_sensor.json").read_text())
    n = R["rca212"]["detect"]["powerlaw_block2h"]["n"]
    t_h = (c.t - c.t[0]) / 3600.0
    e = L.ols(np.column_stack([np.ones_like(t_h), (t_h + 1.0) ** n]), r)[1]
    taus = TSM.tau_grid(c.dt, c.t[-1] - c.t[0])
    h = TSM.ohdev(e, c.dt, taus)
    return dict(floor=TSM.band_median(taus, h, *TSM.FLOOR_BAND_H), plateau=TSM.band_median(taus, h, 6.0, 30.0))


def rule_simulation(floor=0.25, beta_h=0.0183, dt_s=60.0, T_max_h=400.0, B=300, seed=11):
    """Check the floor rule run = 2*3*sqrt(2)*floor/|beta| against an independent detector:
    the least-squares slope over a run of length T, with its noise-only spread from simulation.
    Noise: flicker-like (sum of AR(1) processes with log-spaced time constants, 1 min to 1000 h),
    scaled so its median HDEV over 1-4 h equals `floor`. Detection time = shortest T at which
    |beta| reaches 3 noise-only slope standard deviations (median detection, ~50% power)."""
    rng = np.random.default_rng(seed)
    n = int(T_max_h * 3600 / dt_s)
    taus_c = np.logspace(np.log10(60.0), np.log10(1000 * 3600.0), 12)
    from scipy.signal import lfilter
    def flicker():
        x = np.zeros(n)
        for tc in taus_c:
            a = math.exp(-dt_s / tc)
            e = rng.standard_normal(n) * math.sqrt(1 - a * a)
            e[0] = rng.standard_normal()
            x += lfilter([1.0], [1.0, -a], e)
        return x
    # scale from one long realisation
    x0 = flicker()
    tg = np.array([3600.0 * h for h in (1, 2, 3, 4)])
    s = floor / np.median(TSM.ohdev(x0, dt_s, tg))
    Ts = np.array([24, 36, 48, 72, 96, 120, 150, 200, 250, 300, 400], float)
    slopes = {T: [] for T in Ts}
    for _ in range(B):
        x = flicker() * s
        for T in Ts:
            m = int(T * 3600 / dt_s); t = np.arange(m) * dt_s / 3600
            slopes[T].append(np.polyfit(t, x[:m], 1)[0])
    sd = np.array([np.std(slopes[T]) for T in Ts])
    z = beta_h / sd
    T_det = float(np.interp(3.0, z, Ts)) if (z >= 3).any() else float("nan")
    return dict(T_rule=2 * 3 * math.sqrt(2) * floor / beta_h, T_ols=T_det, B=B, Ts=Ts.tolist(), z=z.tolist())


def main():
    R = json.loads((L.PAPER / "generated" / "results_sensor.json").read_text())
    det = R["rca212"]["detect"]
    beta, n_pow = det["beta_hac8"]["slope"], det["powerlaw_block2h"]["n"]
    c = L.load("rca212")
    _, r = TSM.residual(c)
    pid = R["pid23"]["stress"]["oven_setpoint_c"]["max"]
    res = dict(
        lrv=lrv_range(c, r, beta, n_pow),
        wstar=wstar_variants(c, r, n_pow, beta),
        allan_fine=allan_fine(c, r, beta),
        early24=early_slope(c, r),
        slow_attr_rca=slow_attribution(c, r, True),
        air_drift=air_drift_at_fixed_TV(c),
        gain=gain_range(c, pid - 80.0),
        seg_bb164=segment_floors("bb164"),
        seg_rca=segment_floors("rca212"),
    )
    cw = L.load("bb164"); _, rw = TSM.residual(cw)
    res["slow_attr_bb164"] = slow_attribution(cw, rw, False)
    res["slow_attr_fast"] = slow_attribution_fastband(c)
    res["af_low_ea"] = af_ratio_low_ea()
    res["det_bb164"] = detection_suite("bb164")
    res["wander_sp"] = wander_vs_setpoint()
    res["floor_excl_steps"] = floor_excluding_steps()
    res["floor_after_pow"] = floor_after_powerlaw()
    res["rule_sim"] = rule_simulation()
    # hour-to-day plateau of the long run's residual HDEV (6-30 h), against the declared 1-4 h floor
    a = json.loads((L.PAPER / "generated" / "results_timescales.json").read_text())["allan"]["rca212"]
    taus, h = np.array(a["taus"]), np.array(a["hdev_res"])
    res["plateau_rca"] = TSM.band_median(taus, h, 6.0, 30.0)
    # die above the device's absolute-maximum junction temperature (125 C), whole run
    cf = L.load("rca212", soak_s=0)
    res["tj_above125"] = dict(frac=float(np.mean(cf.T > 125.0)), peak=float(cf.T.max()))
    OUT.write_text(json.dumps(res, indent=1, default=float))
    print(f"[write] {OUT}")
    print(json.dumps({k: v for k, v in res.items() if k not in ("gain",)}, indent=1, default=float)[:3000])
    print("gain", res["gain"]["gain_min"], res["gain"]["gain_max"], res["gain"]["ratio_min"], res["gain"]["ratio_max"])


if __name__ == "__main__":
    main()
