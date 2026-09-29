#!/usr/bin/env python3
"""
Blind source separation of the latent aging component via FastICA (negentropy).

The physical model S = S_aged(t) - Delta_PVT(T,V) + eps is a mixture of sources.
Where the regression correction removes the environment by fitting measured T,V,
this asks the dual, model-free question: feeding only the observed channels
(S, T, V) to ICA, can the aging source be recovered as an independent component?

Rationale: ICA maximizes non-Gaussianity (negentropy). The aging drift is a slow
near-monotonic ramp -> strongly non-Gaussian (sub-Gaussian, uniform-like)
marginal, whereas PID-controlled thermal/voltage fluctuation is closer to
Gaussian. ICA should therefore peel the aging signal off as a distinct source.

Evaluation:
  * align each recovered IC to a reference (time, T, regression residual S_corr);
  * corr(aging-IC, S_corr) -> does model-free ICA agree with the regression aging?
  * pairwise KSG MI between ICs -> was independence actually achieved?
  * excess kurtosis -> the non-Gaussianity ICA exploited.

Writes scalars into ../latex/generated/values.tex.  Usage: python3 ica_separation.py
"""

import os, math
import numpy as np
from scipy.stats import kurtosis

from tier1_pipeline import (load, clean, ksg_mi, mi_binned, equiprobable_codes,
                            DEFAULT_CSV, VALUES_TEX)


def whiten(X):
    """Zero-mean + PCA-whiten rows of X (d, n). Returns Xw and the whiten matrix."""
    Xc = X - X.mean(axis=1, keepdims=True)
    cov = (Xc @ Xc.T) / Xc.shape[1]
    d, E = np.linalg.eigh(cov)
    K = np.diag(1.0 / np.sqrt(d)) @ E.T
    return K @ Xc, K


def fastica(X, n_iter=400, tol=1e-9, seed=0):
    """FastICA by deflation with the tanh (logcosh) negentropy contrast.
    X is pre-whitened (d, n). Returns unmixing W (d, d) s.t. sources = W @ X."""
    rng = np.random.default_rng(seed)
    d, n = X.shape
    W = np.zeros((d, d))
    for p in range(d):
        w = rng.standard_normal(d)
        w /= np.linalg.norm(w)
        for _ in range(n_iter):
            wx = w @ X
            g = np.tanh(wx)
            gp = 1.0 - g ** 2                      # g'(u) = 1 - tanh^2(u)
            w_new = (X * g).mean(axis=1) - gp.mean() * w
            # Gram-Schmidt deflation against earlier components
            for j in range(p):
                w_new -= (w_new @ W[j]) * W[j]
            w_new /= np.linalg.norm(w_new)
            if abs(abs(w_new @ w) - 1.0) < tol:
                w = w_new
                break
            w = w_new
        W[p] = w
    return W


def align_sign(ic, ref):
    """Flip an IC's sign so it correlates positively with a reference."""
    return ic if np.corrcoef(ic, ref)[0, 1] >= 0 else -ic


def corr(a, b):
    return float(np.corrcoef(a, b)[0, 1])


def main():
    d, _ = load(DEFAULT_CSV)
    t, S, T, V = clean(d)
    print(f"[load] n={len(S)}")

    # regression residual (linear OLS on centered T,V) = reference aging signal
    Tc, Vc = T - T.mean(), V - V.mean()
    A = np.column_stack([np.ones_like(S), Tc, Vc])
    beta, *_ = np.linalg.lstsq(A, S, rcond=None)
    S_corr = S - A @ beta

    # --- FastICA on the three observed channels ---
    X = np.vstack([S, T, V])
    Xw, K = whiten(X)
    W = fastica(Xw)
    ICs = W @ Xw                                   # (3, n) recovered sources

    # identify components by what they track
    ics = [ICs[i] for i in range(3)]
    aging_idx = int(np.argmax([abs(corr(ic, t)) for ic in ics]))
    therm_idx = int(np.argmax([abs(corr(ic, T)) for ic in ics]))
    aging = align_sign(ics[aging_idx], -t)         # aging: slack falls with time
    thermal = align_sign(ics[therm_idx], T)

    c_aging_scorr = abs(corr(aging, S_corr))
    var_expl_pct = 100.0 * c_aging_scorr ** 2     # shared-variance reading of |corr|, not "% of signal recovered"
    c_aging_time = corr(aging, t)
    c_therm_T = abs(corr(thermal, T))
    kurt_aging = float(kurtosis(aging))            # excess kurtosis (Gaussian = 0)
    kurt_therm = float(kurtosis(thermal))

    # independence check: pairwise MI between the recovered components.
    # Measured on detrended fluctuations (the shared slow non-stationary trend
    # would otherwise dominate and violate ICA's i.i.d. assumption), with the
    # robust binned+Miller-Madow estimator (the components are heavy-tailed,
    # which biases kNN estimators).
    def detrend(x):
        kern = np.ones(3600) / 3600
        return (x - np.convolve(x, kern, mode="same"))[1800:-1800]
    codes = [equiprobable_codes(detrend(ic), 16) for ic in ics]
    pairs = [(0, 1), (0, 2), (1, 2)]
    mis = [mi_binned(codes[i], codes[j])[1] for i, j in pairs]
    max_mi = max(mis)

    print(f"[ICA] aging IC = component {aging_idx}: "
          f"corr(aging,t)={c_aging_time:+.3f}  |corr(aging,S_corr)|={c_aging_scorr:.3f}  "
          f"excess kurtosis={kurt_aging:+.2f}")
    print(f"[ICA] thermal IC = component {therm_idx}: |corr(thermal,T)|={c_therm_T:.3f}  "
          f"excess kurtosis={kurt_therm:+.2f}")
    print(f"[ICA] pairwise inter-IC MI (bits): {[round(m,3) for m in mis]}  -> max {max_mi:.3f}")
    verdict = ("recovers" if c_aging_scorr > 0.8 else
               "partially recovers" if c_aging_scorr > 0.5 else "fails to recover")
    print(f"[verdict] model-free ICA {verdict} the regression aging signal "
          f"(|corr|={c_aging_scorr:.3f})")

    fills = {
        "valICAagingScorr": f"{c_aging_scorr:.3f}",
        "valICAagingVarExpl": f"{var_expl_pct:.0f}",
        "valICAagingTime":  f"{c_aging_time:.3f}",
        "valICAthermalT":   f"{c_therm_T:.3f}",
        "valICAkurtAging":  f"{kurt_aging:+.2f}",
        "valICAkurtThermal": f"{kurt_therm:+.2f}",
        "valICAresidMI":    f"{max_mi:.3f}",
        "valICAverdict":    verdict,
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
