#!/usr/bin/env python3
"""SBCCI 2026 metrics (Tables I-III), computed the same way for the paper's two runs and for
new runs recorded by App_DT_Monitor (AU15P on the fbs platform). fbs SPEC §6.2.

    # check: recompute the paper's two runs and compare with the published values
    python3 analysis/dt2027/sbcci_metrics.py --sbcci

    # a new run: its session folder and the board
    python3 analysis/dt2027/sbcci_metrics.py --session data/campaigns/sessions/<run> --board A --slack last

    # the colleague's earlier D&T Monitor format (one _frames.csv per board)
    python3 analysis/dt2027/sbcci_metrics.py --dtm <run>_dut0_frames.csv

Needs numpy. Ported from the colleague's metricas_sbcci.py (branch dt2027, 12_analises) with
the same definitions:
  - T and V statistics: mean and sample standard deviation, over the whole run and for t >= 1 h.
  - AF: Arrhenius, AF = exp[(Ea/k)(1/T_use - 1/T)], Ea = 0.7 eV, T_use = 55 degC. <AF> is the
    mean along the trajectory (equally spaced samples), AF(<T>) the factor of the mean
    temperature; equivalent hours = AF x duration.
  - R^2: slack ~ 1 + T + V by least squares, t >= 1 h; residual = standard deviation of the error.
  - Late slope: the coefficient of t (hours) in slack ~ 1 + t + T + V for t >= 12 h, with the
    Newey-West standard error (Bartlett kernel, L = floor(4 (n/100)^(2/9))). With this
    definition PID gives -5.35 m-count/h (paper: -5.3) and bang-bang -8.4 (paper: -6.5,
    unexplained: an open item for the paper, not for the tools). The estimate moves a lot
    with the start of the window; the report shows that sensitivity.
Slack choice for new runs: `last` is the last sweep of each 1 s window, the equivalent of
SBCCI's single sweep per second and the fair comparison with the paper; `mean` is the mean of
the ~9000 sweeps of the window. The difference between the two measures what oversampling buys.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import math
import os
import sys
from pathlib import Path

import numpy as np

K_B = 8.617333262e-5          # eV/K
EA_EV = 0.7
T_USE_C = 55.0
SKIP_H = 1.0                  # the first hour is left out (the paper's method)
LATE_FROM_H = 12.0            # late window
SENS_STARTS_H = (10.0, 11.0, 12.0, 13.0, 14.0)

ROOT = Path(__file__).resolve().parents[2]
SBCCI_DIR = ROOT / "publications" / "coursework" / "tf_teoria-da-informacao" / "artigos" / "TCC vs SBCCI"
SBCCI_FILES = {
    "bang-bang": SBCCI_DIR / "SBCCI_TCC_COMP_ESTABILIZADO.csv",     # 2025-04-07, 0.5 Hz
    "PID": SBCCI_DIR / "TCC_SBCCI_COMP_ESTABILIZADO.csv",           # 2026-01-10, 1 Hz
}
# published values (camera-ready, Tables I-III)
PAPER = {
    "bang-bang": {"T_mean": 107.73, "T_sd": 2.64, "V_sd_mV": 6.1, "AF_mean": 31.1, "eq_h_T": 711,
                  "R2_pct": 92.1, "resid": 0.904, "late_mcnt_h": -6.5},
    "PID": {"T_mean": 117.04, "T_sd": 1.25, "V_sd_mV": 3.6, "AF_mean": 51.3, "eq_h_T": 1182,
            "R2_pct": 59.2, "resid": 0.726, "late_mcnt_h": -5.3},
}


# =============================================================================
#   Loading: (t in s, T in degC, V in V, slack in counts)
# =============================================================================
def _rows(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(line for line in f if not line.startswith("#")))


def load_bangbang(path):
    """The 2025 collector: Data, Hora, Temperatura (m-degC), Slack, Tensão (mV), every 2 s."""
    t, T, V, S, t0 = [], [], [], [], None
    for r in _rows(path):
        ts = dt.datetime.strptime(f"{r['Data']} {r['Hora']}", "%d/%m/%Y %H:%M:%S")
        t0 = t0 or ts
        t.append((ts - t0).total_seconds())
        T.append(float(r["Temperatura"]) / 1000.0)
        V.append(float(r["Tensão"]) / 1000.0)
        S.append(float(r["Slack"]))
    return tuple(np.array(x) for x in (t, T, V, S))


def load_pid(path):
    """App_Nexys, January 2026: time_sec, dut_temp_c, dut_volt, dut_slack (1 Hz)."""
    r = _rows(path)
    g = lambda k: np.array([float(x[k]) for x in r])          # noqa: E731
    return g("time_sec"), g("dut_temp_c"), g("dut_volt"), g("dut_slack")


def load_dtm(path, slack="last"):
    """The colleague's D&T Monitor _frames.csv: one row per 1 s window."""
    col = {"last": "slack_last", "mean": "slack_mean"}[slack]
    t, T, V, S = [], [], [], []
    for r in _rows(path):
        try:
            vals = float(r["time_sec"]), float(r["temp_c"]), float(r["vccint_v"]), float(r[col])
        except (KeyError, ValueError):
            continue                       # an empty field means no data (never 0)
        if int(r.get("sweeps") or 0) == 0:
            continue
        for lst, v in zip((t, T, V, S), vals):
            lst.append(v)
    return tuple(np.array(x) for x in (t, T, V, S))


def load_session(folder, board="A", slack="last", phase="stress"):
    """An fbs session (App_DT_Monitor): summary.csv (one row per second) for time, die
    temperature and SYSMON VCCINT, and <board>_AGING_WINDOW.csv for the slack of each window
    (last sweep, or the window mean from sum/sweeps). Only rows of the given run phase
    (prefix; "" = all)."""
    folder = Path(folder)
    windows = {}
    for r in _rows(folder / f"{board}_AGING_WINDOW.csv"):
        n = int(r["sweeps"] or 0)
        if n:
            windows[int(r["window_id"])] = float(r["last"]) if slack == "last" else int(r["sum"]) / n
    t, T, V, S = [], [], [], []
    for r in _rows(folder / "summary.csv"):
        if phase and not r["phase"].startswith(phase):
            continue
        try:
            wid = int(r[f"{board}_window_id"])
            vals = float(r["t_host_s"]), float(r[f"{board}_die_temp_c"]), float(r[f"{board}_sysmon_vccint_v"]), \
                windows[wid]
        except (KeyError, ValueError):
            continue
        for lst, v in zip((t, T, V, S), vals):
            lst.append(v)
    t = np.array(t)
    return (t - t[0] if len(t) else t), np.array(T), np.array(V), np.array(S)


# =============================================================================
#   Statistics
# =============================================================================
def arrhenius(temp_c):
    return np.exp(EA_EV / K_B * (1.0 / (T_USE_C + 273.15) - 1.0 / (np.asarray(temp_c) + 273.15)))


def ols(X, y):
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    return b, y - X @ b


def newey_west(X, e, lag):
    Xe = X * e[:, None]
    S = Xe.T @ Xe
    for k in range(1, lag + 1):
        w = 1.0 - k / (lag + 1.0)
        G = Xe[k:].T @ Xe[:-k]
        S += w * (G + G.T)
    inv = np.linalg.inv(X.T @ X)
    return inv @ S @ inv


def late_slope(h, T, V, S, start_h):
    m = h >= start_h
    n = int(m.sum())
    if n < 100:
        return None
    X = np.c_[np.ones(n), h[m], T[m], V[m]]
    b, e = ols(X, S[m])
    lag = int(math.floor(4 * (n / 100.0) ** (2.0 / 9.0)))
    se = math.sqrt(newey_west(X, e, lag)[1, 1])
    return {"from_h": start_h, "n": n, "lag": lag, "mcnt_h": 1000 * b[1], "ci95": 1000 * 1.96 * se}


def metrics(t, T, V, S, skip_h=SKIP_H, late_from_h=LATE_FROM_H, sens=SENS_STARTS_H):
    h = t / 3600.0
    dur = float(h[-1] - h[0])
    late = h >= skip_h
    af_all = arrhenius(T)
    X = np.c_[np.ones(late.sum()), T[late], V[late]]
    b, e = ols(X, S[late])
    return {
        "n": int(len(t)), "dt_s": float(np.median(np.diff(t))), "duration_h": dur,
        "T_mean": float(T.mean()), "T_sd": float(T.std(ddof=1)),
        "T_mean_1h": float(T[late].mean()), "T_sd_1h": float(T[late].std(ddof=1)),
        "V_mean": float(V.mean()), "V_sd_mV": 1000 * float(V.std(ddof=1)),
        "V_sd_mV_1h": 1000 * float(V[late].std(ddof=1)),
        "AF_mean": float(af_all.mean()), "AF_of_Tmean": float(arrhenius(T.mean())),
        "eq_h_AF": float(af_all.mean() * dur), "eq_h_T": float(arrhenius(T.mean()) * dur),
        "R2_pct": 100 * (1 - e.var() / S[late].var()), "resid": float(e.std(ddof=3)),
        "coef_T_cnt_per_C": float(b[1]), "coef_V_cnt_per_V": float(b[2]),
        "late": late_slope(h, T, V, S, late_from_h),
        "late_sensitivity": [late_slope(h, T, V, S, s) for s in sens],
    }


# =============================================================================
#   Report
# =============================================================================
def report(name, m, paper=None, late_from_h=LATE_FROM_H):
    lt = m["late"] or {}
    rows = [
        ("Duration (h)", f"{m['duration_h']:.2f}", None),
        ("Sampling (s)", f"{m['dt_s']:.1f}", None),
        ("T_DUT mean (degC)", f"{m['T_mean']:.2f}", "T_mean"),
        ("sd(T) (degC)", f"{m['T_sd']:.2f}  (t >= 1 h: {m['T_sd_1h']:.2f})", "T_sd"),
        ("sd(VDD) (mV)", f"{m['V_sd_mV']:.1f}  (t >= 1 h: {m['V_sd_mV_1h']:.1f})", "V_sd_mV"),
        ("<AF>", f"{m['AF_mean']:.1f}  (AF(<T>) {m['AF_of_Tmean']:.1f})", "AF_mean"),
        ("Equivalent hours", f"{m['eq_h_AF']:.0f} by <AF>, {m['eq_h_T']:.0f} by AF(<T>)", "eq_h_T"),
        ("R^2 slack ~ T, V (t >= 1 h, %)", f"{m['R2_pct']:.2f}", "R2_pct"),
        ("Residual sd (count)", f"{m['resid']:.3f}", "resid"),
        ("Late slope (m-count/h)",
         f"{lt.get('mcnt_h', float('nan')):.2f} ± {lt.get('ci95', float('nan')):.2f} (t >= {late_from_h:.0f} h)",
         "late_mcnt_h"),
    ]
    print(f"\n== {name}")
    for label, val, key in rows:
        ref = f"   [paper: {paper[key]}]" if paper and key in paper else ""
        print(f"  {label:32s} {val}{ref}")
    sens = ", ".join(f"{s['from_h']:.0f} h: {s['mcnt_h']:.1f}" for s in m["late_sensitivity"] if s)
    print(f"  {'... other window starts':32s} {sens}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--sbcci", action="store_true", help="recompute the paper's two runs")
    ap.add_argument("--session", action="append", default=[], help="an fbs session folder (repeatable)")
    ap.add_argument("--board", default="A", help="board name in the session")
    ap.add_argument("--phase", default="stress", help="run phase to use (prefix; '' = all)")
    ap.add_argument("--dtm", action="append", default=[], help="a colleague-format _frames.csv")
    ap.add_argument("--slack", choices=("last", "mean"), default="last")
    ap.add_argument("--json", help="write the metrics to this file")
    a = ap.parse_args(argv)
    if not (a.sbcci or a.session or a.dtm):
        ap.error("use --sbcci, --session and/or --dtm")
    results = {}
    if a.sbcci:
        for name, path in SBCCI_FILES.items():
            series = (load_bangbang if name == "bang-bang" else load_pid)(path)
            results[name] = m = metrics(*series)
            report(f"SBCCI 2026, {name} ({os.path.basename(path)})", m, PAPER[name])
    sources = [(p, load_session(p, a.board, a.slack, a.phase), f"session {p} board {a.board}") for p in a.session]
    sources += [(p, load_dtm(p, a.slack), f"D&T Monitor {os.path.basename(p)}") for p in a.dtm]
    for path, series, label in sources:
        if len(series[0]) < 200:
            print(f"\n== {label}: only {len(series[0])} windows with data; too few for the metrics")
            continue
        results[str(path)] = m = metrics(*series)
        report(f"{label} (slack_{a.slack})", m)
    if a.json:
        with open(a.json, "w") as f:
            json.dump(results, f, indent=2, default=float)
    return 0


if __name__ == "__main__":
    sys.exit(main())
