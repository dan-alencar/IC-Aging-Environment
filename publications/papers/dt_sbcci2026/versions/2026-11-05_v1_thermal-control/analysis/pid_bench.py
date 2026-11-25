#!/usr/bin/env python3
"""PID bench construction: FOPDT identification, SIMC gains, 100 degC tests.

Writes generated/results_pid.json.

Definitions
  * FOPDT: T(t) = T0 + K*u*(1 - exp(-(t - theta)/tau)) for t > theta, u = 50 %,
    T0 = first logged sample; K, theta, tau by nonlinear least squares.
  * SIMC (Skogestad 2003) with tau_c = theta:  Kp = tau / (K (tau_c + theta)),
    tau_I = min(tau, 4 (tau_c + theta)), Ki = Kp / tau_I, Kd = 0.
  * 100 degC tests: steady state = last 30 min of each log (the window stated
    in the thesis text); error e = T_oven - 100; overshoot = max(T_oven) - 100
    over the whole test.
"""
from __future__ import annotations

import json
import re

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

import dtlib as L

OUT = L.PAPER / "generated" / "results_pid.json"
STEP = L.DATA / "oven_fopdt_step_test" / "step_test_data.csv"
T100 = L.DATA / "2026-01_oven_100C_controller_tests"
TESTS = {
    "thermostat": "Forno_Sem_Controle_Setpoint100____20260110_115213.csv",
    "simc": "SIMC_20260111_181754.csv",
    "tuned": "Final_Test_20260109_213200.csv",
    "tuned_repeat": "Final_Test_100_27.5start_20260111_161724.csv",
}
SP = 100.0
SS_WINDOW_S = 1800.0
U_STEP = 50.0


def fopdt(t, K, theta, tau, T0):
    y = np.full_like(t, T0, dtype=float)
    m = t > theta
    y[m] = T0 + K * U_STEP * (1.0 - np.exp(-(t[m] - theta) / tau))
    return y


def header_gains(path):
    txt = path.read_text(errors="replace")
    g = {}
    for k in ("Kp", "Ki", "Kd"):
        m = re.search(rf"{k}\s*=\s*([\d.eE+-]+)", txt)
        g[k] = float(m.group(1)) if m else None
    return g


def main():
    s = pd.read_csv(STEP)
    t, T = s.Time_sec.to_numpy(float), s.Temperature_C.to_numpy(float)
    T0 = float(T[0])
    p, cov = curve_fit(lambda tt, K, th, ta: fopdt(tt, K, th, ta, T0), t, T, p0=(1.5, 150, 1300))
    K, theta, tau = (float(v) for v in p)
    sd = [float(v) for v in np.sqrt(np.diag(cov))]
    rmse = float(np.sqrt(np.mean((T - fopdt(t, K, theta, tau, T0)) ** 2)))
    # two-point method used by the thesis (Analysis_app/fopdt_analyzer.py):
    # K = dT_final/u, theta = first time above 2 % of the rise, tau = t63.2 - theta
    dT = float(T[-1] - T0)
    K2 = dT / U_STEP
    # times are measured from the step instant (t = 0), not from the first sample
    th2 = float(t[np.flatnonzero(T > T0 + 0.02 * dT)[0]])
    t63 = float(t[np.flatnonzero(T >= T0 + 0.632 * dT)[0]])
    ta2 = t63 - th2
    rmse2 = float(np.sqrt(np.mean((T - fopdt(t, K2, th2, ta2, T0)) ** 2)))
    out_two = dict(K=K2, theta=th2, tau=ta2, rmse=rmse2, T_final=float(T[-1]), T_max=float(T.max()))
    # SIMC from the identified (two-point) model, as in the thesis
    K, theta, tau = K2, th2, ta2
    tau_c = theta
    Kp = tau / (K * (tau_c + theta))
    tauI = min(tau, 4 * (tau_c + theta))
    out = dict(
        step=dict(T0=T0, u=U_STEP, n=len(t), duration_s=float(t[-1] - t[0]), cadence_s=float(np.median(np.diff(t))),
                  lsq=dict(K=float(p[0]), theta=float(p[1]), tau=float(p[2]), K_sd=sd[0], theta_sd=sd[1], tau_sd=sd[2], rmse=rmse),
                  two_point=out_two),
        simc=dict(tau_c=tau_c, Kp=Kp, tauI=tauI, Ki=Kp / tauI, Kd=0.0),
        tests={},
    )
    for k, fn in TESTS.items():
        d = L.read_tcc9(T100 / fn)
        tt, To = d.time_sec.to_numpy(float), d.oven_temp_c.to_numpy(float)
        m = tt >= tt[-1] - SS_WINDOW_S
        x = To[m]
        out["tests"][k] = dict(
            file=str((T100 / fn).relative_to(L.REPO)), gains=header_gains(T100 / fn),
            n=len(tt), duration_h=float((tt[-1] - tt[0]) / 3600.0),
            ss_mean=float(x.mean()), ss_sd=float(x.std()), ss_ptp=float(np.ptp(x)),
            ss_abs_err_max=float(np.abs(x - SP).max()), overshoot=float(To.max() - SP),
            # thesis script convention (last 30 % of samples), for reconciliation only
            last30pct_sd=float(To[int(0.7 * len(To)):].std()),
        )
    final = header_gains(L.CAMPAIGNS["pid23"]["path"])
    out["final_gains"] = final
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
