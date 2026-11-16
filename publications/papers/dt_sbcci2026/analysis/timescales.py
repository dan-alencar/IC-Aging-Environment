#!/usr/bin/env python3
"""Time-scale analyses added in the PATH A restructuring.

    python analysis/timescales.py

Writes generated/results_timescales.json. Same loading and soak convention as
run_analysis.py (dropouts removed, first hour excluded, PVT model = OLS of S on
centered [T, V]). Analyses:

  1. Overlapping Allan deviation (ADEV) and overlapping Hadamard deviation
     (HDEV, insensitive to a linear drift) of the die temperature and of the
     PVT-corrected slack residual, for every sensor campaign. The "hour-scale
     floor" is the median HDEV over averaging times 1-4 h (the band every run,
     including the 23 h ones, can resolve with at least ~6 windows).
  2. Distribution of least-squares slopes of the corrected residual over
     sliding windows of length W (stride 2 h) on the long PID run; spread versus
     W, before and after removing the fitted power-law drift (noise-only spread),
     and the shortest window whose 3-sigma noise spread is below the mean drift.
  3. Sensitivity of the long-run drift to the regressor set, and whether the
     candidate extra regressors (PSU voltage, PSU current) themselves drift at
     fixed die temperature and voltage (i.e. are affected by the device state).
  4. Thermometer cross-check: the supply current is a second, leakage-based
     thermometer; its drift at fixed XADC temperature bounds how much of the
     slack drift a drifting XADC temperature reading could explain.
  5. Die-temperature response to oven-air changes in the long run (block-mean
     first differences, with the oven setpoint as instrument).
"""
from __future__ import annotations

import json
import math

import numpy as np

import dtlib as L

OUT = L.PAPER / "generated" / "results_timescales.json"
KEYS = ("bb23", "pid23", "bb164", "rca212")
FLOOR_BAND_H = (1.0, 4.0)


# ------------------------------------------------------------ Allan family
def oadev(y, dt, taus):
    """Overlapping Allan deviation of a sampled series y (units of y)."""
    y = np.asarray(y, float)
    cs = np.concatenate([[0.0], np.cumsum(y)])
    out = []
    for tau in taus:
        m = int(round(tau / dt))
        if m < 1 or 2 * m > len(y) - 1:
            out.append(float("nan")); continue
        ybar = (cs[m:] - cs[:-m]) / m
        d = ybar[m:] - ybar[:-m]
        out.append(float(math.sqrt(0.5 * np.mean(d ** 2))))
    return np.array(out)


def ohdev(y, dt, taus):
    """Overlapping Hadamard deviation: second difference of adjacent means,
    so a linear drift does not contribute (normalised to equal ADEV for white noise)."""
    y = np.asarray(y, float)
    cs = np.concatenate([[0.0], np.cumsum(y)])
    out = []
    for tau in taus:
        m = int(round(tau / dt))
        if m < 1 or 3 * m > len(y) - 1:
            out.append(float("nan")); continue
        ybar = (cs[m:] - cs[:-m]) / m
        d = ybar[2 * m:] - 2 * ybar[m:-m] + ybar[:-2 * m]
        out.append(float(math.sqrt(np.mean(d ** 2) / 6.0)))
    return np.array(out)


def tau_grid(dt, T_s):
    g = np.unique(np.round(np.logspace(math.log10(dt), math.log10(T_s / 3.0), 60) / dt) * dt)
    return g[g >= dt]


def band_median(taus, dev, lo_h, hi_h):
    m = (taus >= lo_h * 3600 - 1) & (taus <= hi_h * 3600 + 1) & np.isfinite(dev)
    return float(np.median(dev[m]))


def residual(c, cols=None):
    cols = cols if cols is not None else [c.T, c.V]
    b, r = L.ols(L.design(*cols), c.S)
    return b, r


# ------------------------------------------------------------ 1. ADEV / HDEV
def allan_all():
    out = {}
    for k in KEYS:
        c = L.load(k)
        b, r = residual(c)
        T_s = c.t[-1] - c.t[0]
        taus = tau_grid(c.dt, T_s)
        a_r, h_r = oadev(r, c.dt, taus), ohdev(r, c.dt, taus)
        a_T, h_T = oadev(c.T, c.dt, taus), ohdev(c.T, c.dt, taus)
        kT = abs(float(b[1]))
        fr = band_median(taus, h_r, *FLOOR_BAND_H)
        fT = band_median(taus, h_T, *FLOOR_BAND_H)
        # thermostat/oven cycle: largest die-temperature HDEV below 1 h
        m = taus < 3600
        i_pk = int(np.nanargmax(np.where(m, h_T, np.nan)))
        out[k] = dict(
            taus=taus.tolist(), adev_res=a_r.tolist(), hdev_res=h_r.tolist(),
            adev_T=a_T.tolist(), hdev_T=h_T.tolist(), kT=kT, dt=c.dt,
            floor_res=fr, floor_T=fT,
            floor_res_degC=fr / kT,
            leftover_pct=100.0 * fr / (kT * fT),           # share of the slow die wander's effect left after PVT
            T_peak_tau_s=float(taus[i_pk]), T_peak=float(h_T[i_pk]), res_at_T_peak=float(h_r[i_pk]),
            leftover_at_peak_pct=100.0 * float(h_r[i_pk]) / (kT * float(h_T[i_pk])),
            adev_res_first=float(a_r[0]),
        )
        # fixed short averaging time common to both cadences (2 s)
        if c.dt < 1.5:
            k2 = int(round(2.0 / c.dt))
            _, r2 = L.ols(L.design(c.T[::k2], c.V[::k2]), c.S[::k2])
            out[k]["adev_res_2s"] = float(oadev(r2, 2.0, [2.0])[0])
        else:
            out[k]["adev_res_2s"] = float(oadev(r, c.dt, [2.0])[0])
    return out


# ------------------------------------------------------------ 2. window slopes
def window_slopes(c, r, n_pow, W_list=(6, 12, 24, 34, 48, 72, 96), stride_h=2.0):
    t_h = (c.t - c.t[0]) / 3600.0
    tb, rb = L.block_means(c.t - c.t[0], r, 600.0)
    tb = tb / 3600.0
    # power-law drift fitted on the 10-min block means; noise = residual about it
    X = np.column_stack([np.ones_like(tb), (tb + 1.0) ** n_pow])
    bp, e = L.ols(X, rb)
    out = {}
    for W in W_list:
        s_raw, s_noise = [], []
        st = 0.0
        while st + W <= tb[-1] + 1e-9:
            m = (tb >= st) & (tb < st + W)
            Xw = np.column_stack([np.ones(m.sum()), tb[m]])
            s_raw.append(float(L.ols(Xw, rb[m])[0][1]))
            s_noise.append(float(L.ols(Xw, e[m])[0][1]))
            st += stride_h
        s_raw, s_noise = np.array(s_raw), np.array(s_noise)
        out[str(W)] = dict(n=len(s_raw), min=float(s_raw.min()), max=float(s_raw.max()),
                           frac_pos=float(np.mean(s_raw > 0)), sd_raw=float(s_raw.std()),
                           sd_noise=float(s_noise.std()), mean=float(s_raw.mean()))
    Ws = np.array([float(w) for w in out])
    sd = np.array([out[str(int(w))]["sd_noise"] for w in Ws])
    slope_exp = float(np.polyfit(np.log(Ws), np.log(sd), 1)[0])     # -1.5 white, -1 flicker floor
    return out, slope_exp, Ws, sd


# ------------------------------------------------------------ 3./4. regressors
def regressor_sets(c):
    P, O, I = c.extra["psu_voltage_v"], c.extra["oven_temp_c"], c.extra["psu_current_a"]
    sets = {"TV": [c.T, c.V], "TVO": [c.T, c.V, O], "TVP": [c.T, c.V, P], "TVI": [c.T, c.V, I],
            "TVOP": [c.T, c.V, O, P]}
    out = {}
    for nm, cols in sets.items():
        _, r = L.ols(L.design(*cols), c.S)
        s, se = L.hac_slope(c.t, r, 600.0, 8.0)
        out[nm] = dict(beta=s, lo=s - 1.96 * se, hi=s + 1.96 * se)
    # hourly joint model S ~ regressors + t, with the variance inflation of t
    tb = L.block_means(c.t, c.S, 3600.0)[0] / 3600.0
    bm = lambda x: L.block_means(c.t, x, 3600.0)[1]
    Sb, Tb, Vb, Pb, Ob, Ib = map(bm, (c.S, c.T, c.V, P, O, I))
    vif = {}
    for nm, cols in (("TV", [Tb, Vb]), ("TVO", [Tb, Vb, Ob]), ("TVP", [Tb, Vb, Pb]), ("TVI", [Tb, Vb, Ib])):
        Z = np.column_stack([np.ones_like(tb)] + [x - x.mean() for x in cols])
        _, rt = L.ols(Z, tb - tb.mean())
        vif[nm] = float(tb.var() / rt.var())
    out["vif_t"] = vif
    out["corr_T_I_hourly"] = L.corr(Tb, Ib)
    out["corr_T_O_hourly"] = L.corr(Tb, Ob)
    # do P and I drift at fixed die T and V?  (hourly, OLS on [T, V, t])
    drift = {}
    for nm, y in (("P", Pb), ("I", Ib)):
        X = np.column_stack([np.ones_like(tb), Tb - Tb.mean(), Vb - Vb.mean(), tb - tb.mean()])
        b, _ = L.ols(X, y)
        drift[nm] = dict(per_h=float(b[3]), per_degC=float(b[1]))
    out["drift_at_fixed_TV"] = drift
    # thermometer cross-check (4): express both drifts as an XADC-temperature drift
    _, r = L.ols(L.design(c.T, c.V), c.S)
    beta = L.hac_slope(c.t, r, 600.0, 8.0)[0]
    kT = abs(float(L.ols(L.design(c.T, c.V), c.S)[0][1]))
    slack_degC_h = abs(beta) / kT
    cur_degC_h = drift["I"]["per_h"] / drift["I"]["per_degC"]
    out["thermo_check"] = dict(slack_equiv_degC_per_h=slack_degC_h, current_equiv_degC_per_h=cur_degC_h,
                               slack_equiv_total_degC=slack_degC_h * (c.t[-1] - c.t[0]) / 3600,
                               max_share_pct=100.0 * cur_degC_h / slack_degC_h)
    return out


# ------------------------------------------------------------ 5. die vs air
def die_vs_air(c, block_s=1800.0):
    O, SP = c.extra["oven_temp_c"], c.extra["oven_setpoint_c"]
    tb, Tb = L.block_means(c.t, c.T, block_s)
    Ob = L.block_means(c.t, O, block_s)[1]
    Sb = L.block_means(c.t, SP, block_s)[1]
    dT, dO, dS = np.diff(Tb), np.diff(Ob), np.diff(Sb)
    # OLS gain of die on air, lags 0..2 blocks summed
    def lagmat(x, L_):
        return np.column_stack([x[L_ - k:len(x) - k] for k in range(L_ + 1)])
    Lg = 2
    Y = dT[Lg:]
    Xo = lagmat(dO, Lg)
    b_ols = L.ols(np.column_stack([np.ones(len(Y)), Xo]), Y)[0][1:]
    # IV: instrument the air changes by setpoint changes (same lags)
    Zs = lagmat(dS, Lg)
    Z = np.column_stack([np.ones(len(Y)), Zs])
    X = np.column_stack([np.ones(len(Y)), Xo])
    Xhat = Z @ np.linalg.lstsq(Z, X, rcond=None)[0]
    b_iv = np.linalg.lstsq(Xhat, Y, rcond=None)[0][1:]
    # first stage strength: does the air follow the setpoint?
    b_fs = L.ols(np.column_stack([np.ones(len(Y)), Zs]), dO[Lg:])[0][1:]
    # long-run relation of block means (levels)
    g_lvl = float(np.polyfit(Ob, Tb, 1)[0])
    return dict(gain_ols=float(b_ols.sum()), gain_iv=float(b_iv.sum()), air_per_sp=float(b_fs.sum()),
                gain_levels=g_lvl, corr_levels=L.corr(Ob, Tb), n_blocks=int(len(Y)),
                offset_mean=float(np.mean(c.T) - np.mean(O)))


def main():
    res = {"allan": allan_all()}
    c = L.load("rca212")
    _, r = residual(c)
    R = json.loads((L.PAPER / "generated" / "results_sensor.json").read_text())
    n_pow = R["rca212"]["detect"]["powerlaw_block2h"]["n"]
    beta = R["rca212"]["detect"]["beta_hac8"]["slope"]
    ws, slope_exp, Ws, sd = window_slopes(c, r, n_pow)
    # shortest window whose 3-sigma noise spread falls below the mean drift (log-log interpolation)
    lw, ls_ = np.log(Ws), np.log(3 * sd)
    target = math.log(abs(beta))
    W_star = float("nan")
    for i in range(len(Ws) - 1):
        if ls_[i] >= target >= ls_[i + 1]:
            f = (ls_[i] - target) / (ls_[i] - ls_[i + 1])
            W_star = float(math.exp(lw[i] + f * (lw[i + 1] - lw[i])))
            break
    res["windows"] = dict(table=ws, sd_exponent=slope_exp, W_star_h=W_star, beta=beta, n_pow=n_pow)
    # whole-run slope uncertainty extrapolated from the noise-only spread (power law in W)
    T_h = (c.t[-1] - c.t[0]) / 3600.0
    p = np.polyfit(np.log(Ws), np.log(sd), 1)
    res["windows"]["sd_extrap_full"] = float(math.exp(np.polyval(p, math.log(T_h))))
    res["windows"]["z_full_extrap"] = abs(beta) / res["windows"]["sd_extrap_full"]
    # Allan picture of the drift: two adjacent windows differ by beta*tau, noise sqrt(2)*HDEV(tau)
    a = res["allan"]["rca212"]
    taus, h = np.array(a["taus"]), np.array(a["hdev_res"])
    bs = abs(beta) / 3600.0
    ok = np.isfinite(h)
    z2 = bs * taus[ok] / (math.sqrt(2.0) * h[ok])
    i1 = int(np.argmax(z2 >= 1.0)) if (z2 >= 1.0).any() else None
    i3 = int(np.argmax(z2 >= 3.0)) if (z2 >= 3.0).any() else None
    res["allan_drift"] = dict(tau_cross_h=float(taus[ok][i1] / 3600) if i1 is not None else float("nan"),
                              tau_3sig_h=float(taus[ok][i3] / 3600) if i3 is not None else float("nan"))
    res["regressors"] = regressor_sets(c)
    res["die_vs_air"] = dict(rca212=die_vs_air(c))
    pid = L.load("pid23")
    res["die_vs_air"]["pid23_offset_mean"] = float(np.mean(pid.T) - np.mean(pid.extra["oven_temp_c"]))
    OUT.write_text(json.dumps(res, indent=1, default=float))
    print(f"[write] {OUT}")
    for k in KEYS:
        x = res["allan"][k]
        print(f"  {k:7s} floor_res {x['floor_res']:.3f} cnt  floor_T {x['floor_T']:.3f} C  left {x['leftover_pct']:.0f}%  "
              f"Tpeak {x['T_peak']:.2f}C@{x['T_peak_tau_s']:.0f}s left@peak {x['leftover_at_peak_pct']:.1f}%  adev2s {x['adev_res_2s']:.3f}")
    print("  windows", {k: (round(1e3 * v['min'], 0), round(1e3 * v['max'], 0), round(v['frac_pos'], 2), round(1e3 * v['sd_noise'], 1)) for k, v in ws.items()})
    print("  sd exponent", round(slope_exp, 2), "W*", round(W_star, 1), "z_full_extrap", round(res["windows"]["z_full_extrap"], 1))
    print("  allan drift", res["allan_drift"])
    print("  regressors", {k: round(1e3 * v["beta"], 1) for k, v in res["regressors"].items() if isinstance(v, dict) and "beta" in v})
    print("  vif", res["regressors"]["vif_t"], "drift", res["regressors"]["drift_at_fixed_TV"])
    print("  thermo", res["regressors"]["thermo_check"])
    print("  die_vs_air", res["die_vs_air"])


if __name__ == "__main__":
    main()
