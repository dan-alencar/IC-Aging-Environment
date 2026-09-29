#!/usr/bin/env python3
"""
KL / Jensen-Shannon divergence between two validation benches.

Compares the slack-fluctuation distribution of the SBCCI (non-PID) bench against
the PID-controlled TCC reference, quantifying in bits how far the noisier bench
pushes the measured slack distribution from the controlled one. Because the two
benches sit at different operating points (different temperature setpoints), the
comparison is done on the *centered* slack (S - median), so the divergence
reflects noise character, not the operating-point offset.

Inputs (two different schemas, handled separately):
  * SBCCI: 'Data,Hora,Temperatura,Slack,Tensao' ; Temperatura, Tensao in
    milli-units (101036 -> 101.036 C, 1228 -> 1.228 V); 2 s sampling.
  * TCC:   the standard 9-column burn-in log; 1 s sampling.

Writes the KL/JS scalars into ../latex/generated/values.tex and prints a summary.

Usage:  python3 kl_benches.py
"""

import os, math
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BENCH_DIR = os.path.join(HERE, "..", "artigos", "TCC vs SBCCI")
SBCCI = os.path.join(BENCH_DIR, "SBCCI_TCC_COMP_ESTABILIZADO.csv")
TCC = os.path.join(BENCH_DIR, "TCC_SBCCI_COMP_ESTABILIZADO.csv")
VALUES_TEX = os.path.join(HERE, "..", "latex", "generated", "values.tex")


def load_sbcci(path):
    """SBCCI schema -> slack (counts), T (C), V (V)."""
    S, T, V = [], [], []
    with open(path) as f:
        next(f)                                   # header line
        for line in f:
            p = line.strip().split(",")
            if len(p) != 5:
                continue
            try:
                T.append(float(p[2]) / 1000.0)
                S.append(float(p[3]))
                V.append(float(p[4]) / 1000.0)
            except ValueError:
                continue
    return np.array(S), np.array(T), np.array(V)


def load_tcc(path):
    """Standard 9-column schema -> slack, T, V (drop dropouts)."""
    S, T, V = [], [], []
    with open(path) as f:
        for line in f:
            if line.startswith("#") or line.startswith("time_sec") or not line.strip():
                continue
            p = line.strip().split(",")
            if len(p) != 9:
                continue
            try:
                s, t, v = float(p[7]), float(p[6]), float(p[8])
            except ValueError:
                continue
            if s > 0 and t > 0 and v > 0:
                S.append(s); T.append(t); V.append(v)
    return np.array(S), np.array(T), np.array(V)


def hist_pmf(x_int, support, alpha=0.5):
    """Laplace-smoothed PMF of integer values over a common support."""
    counts = np.array([np.sum(x_int == k) for k in support], dtype=float)
    counts += alpha                               # avoid zero-probability bins
    return counts / counts.sum()


def kl(p, q):
    """KL(P||Q) in bits."""
    return float(np.sum(p * np.log2(p / q)))


def js(p, q):
    """Jensen-Shannon divergence in bits (symmetric, bounded [0,1])."""
    m = 0.5 * (p + q)
    return 0.5 * kl(p, m) + 0.5 * kl(q, m)


def gaussian_kl(sp, sq):
    """Closed-form KL(P||Q) in bits for two zero-mean Gaussians (cross-check)."""
    nats = math.log(sq / sp) + (sp ** 2) / (2 * sq ** 2) - 0.5
    return nats / math.log(2)


def main():
    Ss, Ts, Vs = load_sbcci(SBCCI)
    St, Tt, Vt = load_tcc(TCC)
    print(f"[load] SBCCI n={len(Ss)}  TCC n={len(St)}")

    sig_s, sig_t = float(Ss.std()), float(St.std())
    print(f"[noise] slack std: SBCCI={sig_s:.3f}  PID={sig_t:.3f} counts "
          f"(ratio {sig_s/sig_t:.2f}x);  "
          f"temp std SBCCI={Ts.std():.2f}  PID={Tt.std():.2f} C")

    # center on integer median -> integer fluctuations on a common support
    ps_int = np.round(Ss - np.median(Ss)).astype(int)
    pt_int = np.round(St - np.median(St)).astype(int)
    lo = min(ps_int.min(), pt_int.min())
    hi = max(ps_int.max(), pt_int.max())
    support = np.arange(lo, hi + 1)

    P = hist_pmf(ps_int, support)                 # SBCCI (noisy)
    Q = hist_pmf(pt_int, support)                 # PID reference

    kl_sp = kl(P, Q)                              # cost of describing SBCCI with PID model
    kl_ps = kl(Q, P)
    jsd = js(P, Q)
    kl_gauss = gaussian_kl(sig_s, sig_t)          # closed-form cross-check, unrounded sigmas
    print(f"[KL empirical] KL(SBCCI||PID)={kl_sp:.3f}  KL(PID||SBCCI)={kl_ps:.3f}  "
          f"JS={jsd:.3f} bits")
    print(f"[KL gaussian ] KL(SBCCI||PID)~{kl_gauss:.3f} bits (closed-form cross-check)")

    fills = {
        "valSlackStdSBCCI": f"{sig_s:.2f}",
        "valSlackStdPID":   f"{sig_t:.2f}",
        "valTstdSBCCI":     f"{Ts.std():.2f}",
        "valTstdPID":       f"{Tt.std():.2f}",
        "valKLsp":          f"{kl_sp:.2f}",
        "valKLps":          f"{kl_ps:.2f}",
        "valJSbench":       f"{jsd:.3f}",
        "valKLgauss":       f"{kl_gauss:.2f}",
    }
    write_values(fills)
    print(f"[write] {VALUES_TEX}")


def write_values(fills):
    with open(VALUES_TEX) as fh:
        lines = fh.readlines()
    out = []
    for line in lines:
        hit = False
        for name, val in fills.items():
            if line.lstrip().startswith(f"\\newcommand{{\\{name}}}"):
                out.append(f"\\newcommand{{\\{name}}}{{{val}}}\n")
                hit = True
                break
        if not hit:
            out.append(line)
    with open(VALUES_TEX, "w") as fh:
        fh.writelines(out)


if __name__ == "__main__":
    main()
