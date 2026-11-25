#!/usr/bin/env python3
"""Robustness checks on the long PID (RCA) run, written to generated/results_robust.json.

  * drift sensitivity to the PVT regressor set: HAC slope (10-min block means,
    Newey-West bandwidth 8 h, dtlib.hac_slope) of the residual of S on
      [T, V], [T, V, oven T], [T, V, PSU voltage], [T, V, oven T, PSU voltage];
    plus the joint fit S ~ T + V + t on the same 10-min blocks (HAC SE);
  * the supply-voltage trim range (the VCCINT loop was on in this run);
  * residual sigma about the linear trend ("full" sigma), against the fast sigma;
  * spread of slopes in sliding windows (34 h, 2 h stride) of the [T, V] residual.
"""
from __future__ import annotations

import json
import math

import numpy as np

import dtlib as L

OUT = L.PAPER / "generated" / "results_robust.json"
AGG_S, BW_H = 600.0, 8.0
WIN_H, STRIDE_H = 34.0, 2.0


def hac_joint_time_coef(c):
    """Coefficient of t (cnt/h) in S ~ T + V + t on block means, Newey-West SE."""
    b = int(round(AGG_S / c.dt))
    m = len(c.S) // b
    blk = lambda x: x[:m * b].reshape(m, b).mean(1)
    Sb, Tb, Vb, tb = blk(c.S), blk(c.T), blk(c.V), blk(c.t / 3600.0)
    X = L.design(Tb, Vb, tb)
    beta, u = L.ols(X, Sb)
    lag = min(max(int(round(BW_H * 3600.0 / AGG_S)), 1), m - 2)
    XtXi = np.linalg.inv(X.T @ X)
    Xu = X * u[:, None]
    S = Xu.T @ Xu
    for k in range(1, lag + 1):
        w = 1.0 - k / (lag + 1.0)
        G = Xu[k:].T @ Xu[:-k]
        S += w * (G + G.T)
    se = math.sqrt((XtXi @ S @ XtXi)[3, 3])
    return float(beta[3]), se


def main():
    c = L.load("rca212")
    oven, psu = c.extra["oven_temp_c"], c.extra["psu_voltage_v"]
    sets = {
        "TV": L.design(c.T, c.V),
        "TV_oven": L.design(c.T, c.V, oven),
        "TV_psu": L.design(c.T, c.V, psu),
        "TV_oven_psu": L.design(c.T, c.V, oven, psu),
    }
    out = {"regressor_sets": {}}
    for k, X in sets.items():
        _, r = L.ols(X, c.S)
        s, se = L.hac_slope(c.t, r, AGG_S, BW_H)
        out["regressor_sets"][k] = dict(slope=s, se=se, lo=s - 1.96 * se, hi=s + 1.96 * se)
    s, se = hac_joint_time_coef(c)
    out["joint_TVt"] = dict(slope=s, se=se, lo=s - 1.96 * se, hi=s + 1.96 * se)
    out["psu_v"] = dict(min=float(psu.min()), max=float(psu.max()), mean=float(psu.mean()),
                        corr_with_T=L.corr(psu, c.T))
    _, res = L.ols(sets["TV"], c.S)
    t_h = c.t / 3600.0
    _, e_lin = L.ols(np.column_stack([np.ones_like(t_h), t_h]), res)
    out["sigma_full_detrended"] = float(e_lin.std())
    slopes = []
    for a in np.arange(t_h[0], t_h[-1] - WIN_H + 1e-9, STRIDE_H):
        m = (t_h >= a) & (t_h < a + WIN_H)
        b, _ = L.ols(np.column_stack([np.ones(m.sum()), t_h[m]]), res[m])
        slopes.append(float(b[1]))
    slopes = np.array(slopes)
    out["windows"] = dict(length_h=WIN_H, stride_h=STRIDE_H, n=int(len(slopes)),
                          min=float(slopes.min()), max=float(slopes.max()),
                          frac_positive=float((slopes > 0).mean()))
    OUT.write_text(json.dumps(out, indent=1))
    print(f"[write] {OUT}")


if __name__ == "__main__":
    main()
