#!/usr/bin/env python3
"""
Métricas do SBCCI 2026 (Tabelas I–III), calculadas do mesmo jeito para as corridas do artigo
e para as runs novas do D&T Monitor (AU15P, arquitetura B).

    # validação: recalcula as duas corridas do artigo e compara com os valores publicados
    python3 metricas_sbcci.py --sbcci

    # uma run do D&T Monitor (o arquivo _frames.csv de cada placa)
    python3 metricas_sbcci.py --dtm ../10_DT_Monitor/test_logs/<run>_dut0_frames.csv --slack last

Só precisa de numpy (o .venv do D&T Monitor serve).

Definições (iguais nas duas bancadas):
  - Estatística de T e V: média e desvio padrão amostral, na corrida inteira e com t ≥ 1 h.
  - AF: Arrhenius, AF = exp[(Ea/k)(1/T_uso − 1/T)], Ea = 0.7 eV, T_uso = 55 °C. ⟨AF⟩ é a média
    ao longo da trajetória (amostras igualmente espaçadas), AF(⟨T⟩) é o da temperatura média;
    horas equivalentes = AF × duração.
  - R²: slack ~ 1 + T + V por mínimos quadrados, com t ≥ 1 h; resíduo = desvio padrão do erro.
  - Inclinação tardia: o coeficiente de t (horas) em slack ~ 1 + t + T + V, com t ≥ 12 h, e o
    erro padrão de Newey–West (kernel de Bartlett, L = ⌊4(n/100)^(2/9)⌋). Com essa definição o
    PID dá −5.35 m-cnt/h (artigo: −5.3) e o bang-bang −8.4 (artigo: −6.5, sem explicação ainda).
    A estimativa muda muito com o início da janela; o relatório mostra essa sensibilidade.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import math
import os
import sys

import numpy as np

K_B = 8.617333262e-5          # eV/K
EA_EV = 0.7
T_USE_C = 55.0
SKIP_H = 1.0                  # a primeira hora fica de fora (método do artigo)
LATE_FROM_H = 12.0            # janela tardia
SENS_STARTS_H = (10.0, 11.0, 12.0, 13.0, 14.0)

HERE = os.path.dirname(os.path.abspath(__file__))
DADOS = os.path.join(os.path.dirname(HERE), "02_dados")
SBCCI_FILES = {
    "bang-bang": os.path.join(DADOS, "bangbang_2025-04-07", "SBCCI_TCC_COMP_ESTABILIZADO.csv"),
    "PID": os.path.join(DADOS, "pid_2026-01-10", "TCC_SBCCI_COMP_ESTABILIZADO.csv"),
}
# Valores publicados (camera-ready, Tabelas I–III; README da pasta D&T 2027)
PAPER = {
    "bang-bang": {"T_mean": 107.73, "T_sd": 2.64, "V_sd_mV": 6.1, "AF_mean": 31.1, "eq_h_T": 711,
                  "R2_pct": 92.1, "resid": 0.904, "late_mcnt_h": -6.5},
    "PID": {"T_mean": 117.04, "T_sd": 1.25, "V_sd_mV": 3.6, "AF_mean": 51.3, "eq_h_T": 1182,
            "R2_pct": 59.2, "resid": 0.726, "late_mcnt_h": -5.3},
}


# =============================================================================
#   Carregamento: (t em s, T em °C, V em V, slack em contagens)
# =============================================================================
def _rows(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(line for line in f if not line.startswith("#")))


def load_bangbang(path):
    """Coletor de 2025: Data,Hora,Temperatura (m°C),Slack,Tensão (mV), a cada 2 s."""
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
    """App_Nexys de jan/2026: time_sec, dut_temp_c, dut_volt, dut_slack (1 Hz)."""
    r = _rows(path)
    g = lambda k: np.array([float(x[k]) for x in r])          # noqa: E731
    return g("time_sec"), g("dut_temp_c"), g("dut_volt"), g("dut_slack")


def load_dtm(path, slack="last"):
    """_frames.csv do D&T Monitor: um quadro por janela de 1 s. slack = last (equivale à
    varredura única do SBCCI) ou mean (média das ~8000 varreduras da janela)."""
    col = {"last": "slack_last", "mean": "slack_mean"}[slack]
    t, T, V, S = [], [], [], []
    for r in _rows(path):
        try:
            vals = float(r["time_sec"]), float(r["temp_c"]), float(r["vccint_v"]), float(r[col])
        except (KeyError, ValueError):
            continue                       # campo vazio = sem dado (nunca 0)
        if int(r.get("sweeps") or 0) == 0:
            continue
        for lst, v in zip((t, T, V, S), vals):
            lst.append(v)
    return tuple(np.array(x) for x in (t, T, V, S))


# =============================================================================
#   Estatística
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


def metrics(t, T, V, S):
    h = t / 3600.0
    dur = float(h[-1] - h[0])
    late = h >= SKIP_H
    af_all = arrhenius(T)
    X = np.c_[np.ones(late.sum()), T[late], V[late]]
    b, e = ols(X, S[late])
    out = {
        "n": int(len(t)), "dt_s": float(np.median(np.diff(t))), "duration_h": dur,
        "T_mean": float(T.mean()), "T_sd": float(T.std(ddof=1)),
        "T_mean_1h": float(T[late].mean()), "T_sd_1h": float(T[late].std(ddof=1)),
        "V_mean": float(V.mean()), "V_sd_mV": 1000 * float(V.std(ddof=1)),
        "V_sd_mV_1h": 1000 * float(V[late].std(ddof=1)),
        "AF_mean": float(af_all.mean()), "AF_of_Tmean": float(arrhenius(T.mean())),
        "eq_h_AF": float(af_all.mean() * dur), "eq_h_T": float(arrhenius(T.mean()) * dur),
        "R2_pct": 100 * (1 - e.var() / S[late].var()), "resid": float(e.std(ddof=3)),
        "coef_T_cnt_per_C": float(b[1]), "coef_V_cnt_per_V": float(b[2]),
        "late": late_slope(h, T, V, S, LATE_FROM_H),
        "late_sensitivity": [late_slope(h, T, V, S, s) for s in SENS_STARTS_H],
    }
    return out


# =============================================================================
#   Relatório
# =============================================================================
def report(name, m, paper=None):
    lt = m["late"] or {}
    rows = [
        ("Duração (h)", f"{m['duration_h']:.2f}", None),
        ("Amostragem (s)", f"{m['dt_s']:.1f}", None),
        ("T_DUT média (°C)", f"{m['T_mean']:.2f}", "T_mean"),
        ("σ(T) (°C)", f"{m['T_sd']:.2f}  (t ≥ 1 h: {m['T_sd_1h']:.2f})", "T_sd"),
        ("σ(VDD) (mV)", f"{m['V_sd_mV']:.1f}  (t ≥ 1 h: {m['V_sd_mV_1h']:.1f})", "V_sd_mV"),
        ("⟨AF⟩", f"{m['AF_mean']:.1f}  (AF(⟨T⟩) {m['AF_of_Tmean']:.1f})", "AF_mean"),
        ("Horas equivalentes", f"{m['eq_h_AF']:.0f} por ⟨AF⟩, {m['eq_h_T']:.0f} por AF(⟨T⟩)", "eq_h_T"),
        ("R² slack ~ T, V (t ≥ 1 h, %)", f"{m['R2_pct']:.2f}", "R2_pct"),
        ("σ do resíduo (cnt)", f"{m['resid']:.3f}", "resid"),
        ("Inclinação tardia (m-cnt/h)",
         f"{lt.get('mcnt_h', float('nan')):.2f} ± {lt.get('ci95', float('nan')):.2f} (t ≥ {LATE_FROM_H:.0f} h)",
         "late_mcnt_h"),
    ]
    print(f"\n== {name}")
    for label, val, key in rows:
        ref = f"   [artigo: {paper[key]}]" if paper and key in paper else ""
        print(f"  {label:32s} {val}{ref}")
    sens = ", ".join(f"{s['from_h']:.0f} h: {s['mcnt_h']:.1f}" for s in m["late_sensitivity"] if s)
    print(f"  {'… com outro início da janela':32s} {sens}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--sbcci", action="store_true", help="recalcula as duas corridas do artigo")
    ap.add_argument("--dtm", action="append", default=[], help="_frames.csv de uma placa (pode repetir)")
    ap.add_argument("--slack", choices=("last", "mean"), default="last")
    ap.add_argument("--json", help="grava as métricas neste arquivo")
    a = ap.parse_args(argv)
    if not a.sbcci and not a.dtm:
        ap.error("use --sbcci e/ou --dtm")
    results = {}
    if a.sbcci:
        for name, path in SBCCI_FILES.items():
            series = (load_bangbang if name == "bang-bang" else load_pid)(path)
            results[name] = m = metrics(*series)
            report(f"SBCCI 2026, {name} ({os.path.basename(path)})", m, PAPER[name])
    for path in a.dtm:
        series = load_dtm(path, a.slack)
        if len(series[0]) < 200:
            print(f"\n== {path}: só {len(series[0])} janelas com dado; pouco para as métricas")
            continue
        results[path] = m = metrics(*series)
        report(f"D&T Monitor, {os.path.basename(path)} (slack_{a.slack})", m)
    if a.json:
        with open(a.json, "w") as f:
            json.dump(results, f, indent=2, default=float)
    return 0


if __name__ == "__main__":
    sys.exit(main())
