#!/usr/bin/env python3
"""
Generate the figures for the paper into ../latex/figures/ (vector PDF).

Figures:
  fig_correction.pdf  raw slack + temperature, and the PVT-corrected residual
                      with the exposed aging trend (the information-recovery result)
  fig_mi.pdf          I(S;T), I(S;V), I(S;T,V) vs the linear-equivalent MI and
                      the surrogate null floor
  fig_kl.pdf          centered slack-fluctuation distributions of the two benches
  fig_ica.pdf         the ICA-recovered aging component vs the regression S_corr
  fig_capacity_rul.pdf  BSC aging-alarm capacity vs decision-window length, with
                      the CRLB minimum observation time marked

Usage: python3 make_figures.py   (needs numpy, scipy, matplotlib)
"""

import os, math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from tier1_pipeline import (load, clean, mi_binned, equiprobable_codes,
                            combine_codes, surrogate_mi_floor,
                            integrated_autocorr_time, _design_linear,
                            fit_correction, DEFAULT_CSV)
from kl_benches import (load_sbcci, load_tcc, hist_pmf, kl, js, SBCCI, TCC)
from ica_separation import whiten, fastica, align_sign, corr
from kalman_rul import (block_means, estimate_sigma_B, fit_rate_noise,
                        kalman_loglik_and_run, ig_params, ig_median)
from scipy.stats import invgauss

FIGDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "latex", "figures")
plt.rcParams.update({
    "font.size": 11, "axes.grid": True, "grid.alpha": 0.3,
    "axes.spines.top": False, "axes.spines.right": False, "figure.dpi": 110,
})
C_RAW, C_T, C_CORR, C_FIT = "#1f77b4", "#d62728", "#2ca02c", "#ff7f0e"


def save(fig, name):
    path = os.path.join(FIGDIR, name)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"[fig] {name}")


# ---------------------------------------------------------------- device A load
def load_devA():
    d, _ = load(DEFAULT_CSV)
    t, S, T, V = clean(d)
    Scorr, _ = fit_correction(S, _design_linear(T, V))
    return t, S, T, V, Scorr


# ---------------------------------------------------------------- fig_correction
def fig_correction(t, S, T, Scorr, slide=False):
    """slide=True writes a wider variant (fig_correction_slide.pdf) --- the
    paper figsize's panel (b) title was overflowing/clipping at deck column
    width, where the twinx right-axis label also crowds the title (D.3)."""
    def corr(a, b):
        a, b = a - a.mean(), b - b.mean()
        return float((a @ b) / (np.sqrt(a @ a) * np.sqrt(b @ b)))

    th = t / 3600.0
    ds = max(len(th) // 6000, 1)
    ts, Ss, Tcut, Sc = th[::ds], S[::ds], T[::ds], Scorr[::ds]
    corr_ST = corr(S, T)
    corr_St_raw, corr_St_corr = corr(S, t), corr(Scorr, t)
    figsize = (9.5, 5.8) if slide else (7, 5.2)
    fs_title, fs_legend, fs_label = (13, 10, 12) if slide else (11, 9, 10)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize, sharex=True, constrained_layout=slide)

    ax1.plot(ts, Ss, color=C_RAW, lw=0.6, label="slack $S$")
    ax1.set_ylabel("slack (contagens)", color=C_RAW, fontsize=fs_label)
    axT = ax1.twinx(); axT.grid(False)
    axT.plot(ts, Tcut, color=C_T, lw=0.5, alpha=0.7, label="temp. do die $T$")
    axT.set_ylabel("temp. do die (°C)", color=C_T, fontsize=fs_label)
    ax1.set_title(f"(a) Slack bruto vs. temperatura  (corr $={corr_ST:.2f}$)", fontsize=fs_title)

    ax2.plot(ts, Sc, color=C_CORR, lw=0.6, label="$S_{corr}=S-\\hat{\\Delta}_{PVT}$")
    b, a = np.polyfit(th, Scorr, 1)
    ax2.plot(ts, a + b * ts, color="k", lw=2.0, ls="--",
             label=f"tendência de envelhecimento  {b*1000:+.1f} m-cnt/h")
    ax2.set_xlabel("tempo (h)", fontsize=fs_label); ax2.set_ylabel("resíduo (contagens)", fontsize=fs_label)
    title_b = (f"(b) Envelhecimento exposto  (corr c/ tempo ${corr_St_raw:.2f}\\!\\to\\!{corr_St_corr:.2f}$)"
               if slide else
               f"(b) Após correção PVT: envelhecimento exposto  "
               f"(corr c/ tempo ${corr_St_raw:.2f}\\!\\to\\!{corr_St_corr:.2f}$)")
    ax2.set_title(title_b, fontsize=fs_title)
    ax2.legend(loc="upper right", fontsize=fs_legend)
    if slide:
        save(fig, "fig_correction_slide.pdf")
    else:
        save(fig, "fig_correction.pdf")


# ----------------------------------------------------------------------- fig_mi
def fig_mi(t, S, T, V, slide=False):
    """slide=False writes the paper version (fig_mi.pdf); slide=True writes a
    wider, larger-font variant for the 16:9 beamer deck (fig_mi_slide.pdf) ---
    the paper figsize is too narrow for the title at slide-projection size,
    which was overflowing/clipping (D.3)."""
    s_codes = np.unique(S.astype(int), return_inverse=True)[1]
    Tc, Vc = equiprobable_codes(T, 16), equiprobable_codes(V, 16)
    TVc = combine_codes(Tc, Vc)
    mi_st = mi_binned(s_codes, Tc)[1]
    mi_sv = mi_binned(s_codes, Vc)[1]
    mi_stv = mi_binned(s_codes, TVc)[1]
    resid = (S - np.convolve(S, np.ones(3600)/3600, mode="same"))[3600:-3600]
    tau = integrated_autocorr_time(resid)
    _, null_p95, _ = surrogate_mi_floor(s_codes, TVc, tau, B=200)
    Scorr_r2, _ = fit_correction(S, _design_linear(T, V))
    r2 = 1.0 - float(Scorr_r2.var()) / float(S.var())
    lin_equiv = -0.5 * math.log2(1 - r2)

    figsize = (8.4, 4.6) if slide else (6, 4)
    fs_title, fs_legend, fs_text = (13, 11, 12) if slide else (11, 9, 10)
    fig, ax = plt.subplots(figsize=figsize, constrained_layout=slide)
    labels = ["$I(S;T)$", "$I(S;V)$", "$I(S;T,V)$"]
    vals = [mi_st, mi_sv, mi_stv]
    bars = ax.bar(labels, vals, color=[C_T, C_RAW, C_CORR], width=0.6, zorder=3)
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 0.02, f"{v:.2f}",
                ha="center", fontsize=fs_text)
    ax.axhline(lin_equiv, color="k", ls="--", lw=1.5,
               label=f"MI linear-equiv. ($R^2{{=}}{r2:.2f}$) = {lin_equiv:.2f}")
    ax.axhline(null_p95, color="grey", ls=":", lw=1.5,
               label=f"piso nulo surrogate (p95) = {null_p95:.2f}")
    excess_pct_binned = 100.0 * (mi_stv - lin_equiv) / lin_equiv
    ax.annotate(f"+{excess_pct_binned:.0f}% (série bruta; atribuição: §7.1)", xy=(2, mi_stv),
                xytext=(1.05, mi_stv + 0.18),
                fontsize=fs_text, arrowprops=dict(arrowstyle="->", color="dimgray"))
    ax.set_ylabel("informação mútua (bits)", fontsize=fs_text)
    title = ("Acoplamento ambiental: MI vs. $R^2$ (série bruta)" if slide else
             "Acoplamento ambiental: MI vs. referência linear $R^2$ (série bruta)")
    ax.set_title(title, fontsize=fs_title)
    ax.set_ylim(0, mi_stv + 0.45)
    ax.legend(fontsize=fs_legend, loc="upper left")
    if slide:
        save(fig, "fig_mi_slide.pdf")
    else:
        save(fig, "fig_mi.pdf")


# ----------------------------------------------------------------------- fig_kl
def fig_kl():
    Ss, _, _ = load_sbcci(SBCCI)
    St, _, _ = load_tcc(TCC)
    ps = np.round(Ss - np.median(Ss)).astype(int)
    pt = np.round(St - np.median(St)).astype(int)
    lo, hi = min(ps.min(), pt.min()), max(ps.max(), pt.max())
    support = np.arange(lo, hi + 1)
    P, Q = hist_pmf(ps, support), hist_pmf(pt, support)
    kl_sp, jsd = kl(P, Q), js(P, Q)

    fig, ax = plt.subplots(figsize=(6, 4))
    w = 0.42
    ax.bar(support - w/2, P, width=w, color=C_T, alpha=0.8,
           label=f"SBCCI (não-PID), $\\sigma={Ss.std():.2f}$", zorder=3)
    ax.bar(support + w/2, Q, width=w, color=C_CORR, alpha=0.8,
           label=f"referência PID, $\\sigma={St.std():.2f}$", zorder=3)
    ax.set_xlabel("flutuação centrada de slack (contagens)")
    ax.set_ylabel("probabilidade")
    ax.set_xlim(-9, 9)
    ax.set_title(f"Fidelidade de bancada: $D_{{KL}}$(SBCCI$\\|$PID)$={kl_sp:.2f}$ bits, "
                 f"JS$={jsd:.3f}$ bits")
    ax.legend(fontsize=9)
    save(fig, "fig_kl.pdf")


# ---------------------------------------------------------------------- fig_ica
def fig_ica(t, S, T, V, Scorr, slide=False):
    """slide=True writes a wider variant (fig_ica_slide.pdf) --- the paper
    figsize's title + legend were overflowing/clipping at deck width (D.3)."""
    X = np.vstack([S, T, V])
    Xw, _ = whiten(X)
    ICs = fastica(Xw)
    ic_rows = [ICs[i] @ Xw for i in range(3)]
    aging_idx = int(np.argmax([abs(corr(r, t)) for r in ic_rows]))
    aging = align_sign(ic_rows[aging_idx], Scorr)
    c = abs(corr(aging, Scorr))

    def z(x):
        return (x - x.mean()) / x.std()
    th = t / 3600.0
    ds = max(len(th) // 5000, 1)
    figsize = (9.5, 4.2) if slide else (7, 3.6)
    fs_title, fs_legend, fs_label = (13, 10, 12) if slide else (11, 9, 10)
    fig, ax = plt.subplots(figsize=figsize, constrained_layout=slide)
    ax.plot(th[::ds], z(Scorr)[::ds], color=C_CORR, lw=0.7,
            label="resíduo da regressão $S_{corr}$")
    ax.plot(th[::ds], z(aging)[::ds], color="purple", lw=0.7, alpha=0.8,
            label="componente de envelhecimento (ICA)")
    ax.set_xlabel("tempo (h)", fontsize=fs_label); ax.set_ylabel("normalizado (z-score)", fontsize=fs_label)
    title = (f"ICA recupera o envelhecimento ($|\\mathrm{{corr}}|={c:.3f}$)" if slide else
             f"ICA livre de modelo recupera o envelhecimento  ($|\\mathrm{{corr}}|={c:.3f}$)")
    ax.set_title(title, fontsize=fs_title)
    ax.legend(fontsize=fs_legend, loc="upper right")
    if slide:
        save(fig, "fig_ica_slide.pdf")
    else:
        save(fig, "fig_ica.pdf")


# -------------------------------------------------------------- fig_capacity_rul
def fig_capacity_rul(t, S, Scorr):
    th = t / 3600.0
    # match the pipeline exactly: noise sigma from the detrended *corrected*
    # residual, but the decorrelation time from the detrended *raw* slack.
    sigma = float((Scorr - np.convolve(Scorr, np.ones(3600)/3600, mode="same"))[1800:-1800].std())
    tau = integrated_autocorr_time((S - np.convolve(S, np.ones(3600)/3600, mode="same"))[3600:-3600])
    dt = float(np.median(np.diff(t)))
    tau_c = tau * dt
    beta = abs(np.polyfit(th, Scorr, 1)[0])      # counts/h

    def qfunc(x):
        from scipy.special import erfc
        return 0.5 * erfc(x / math.sqrt(2))
    def h2(p):
        p = min(max(p, 1e-15), 1 - 1e-15)
        return -p*math.log2(p) - (1-p)*math.log2(1-p)

    W = np.logspace(np.log10(0.5), np.log10(220), 200)        # window hours
    cap = []
    for w in W:
        n_eff = w * 3600 / (2 * tau_c)
        sm = sigma / math.sqrt(n_eff)
        d = beta * w / sm
        cap.append(1 - h2(qfunc(d / 2)))
    const = sigma * math.sqrt(24 * tau_c / 3600)
    mot = (3 * const / beta) ** (2/3)

    fig, ax = plt.subplots(figsize=(6.4, 4))
    ax.semilogx(W, cap, color=C_RAW, lw=2.2, zorder=3)
    ax.axvline(mot, color="k", ls="--", lw=1.5,
               label=f"tempo mín. obs. (CRLB) $\\approx{mot:.0f}$ h")
    ax.axvline(24, color=C_CORR, ls=":", lw=1.5,
               label="janela de 24 h: $C_{BSC}=0.99$ bits")
    ax.set_xlabel("duração da janela de decisão (h)")
    ax.set_ylabel("$C_{BSC}=1-H_2(p)$  (bits/decisão)")
    ax.set_ylim(-0.03, 1.03)
    ax.set_title("Confiabilidade do alarme vs. janela de observação")
    ax.legend(fontsize=9, loc="center right")
    save(fig, "fig_capacity_rul.pdf")



# ---------------------------------------------------------------- fig_wiener_rul
def fig_wiener_rul(t, S, Scorr, slide=False):
    """slide=True writes a wider variant (fig_wiener_rul_slide.pdf) with
    bigger fonts and constrained_layout for the two-panel figure, which was
    cramped (title/legend collisions) at beamer slide size (D.3)."""
    def detrend(x):
        kern = np.ones(3600) / 3600
        return (x - np.convolve(x, kern, mode="same"))[1800:-1800]
    sigma_obs_native = float(detrend(Scorr).std())
    sigma_signal = float(np.convolve(Scorr, np.ones(3600)/3600, mode="same")[1800:-1800].std())
    tau = integrated_autocorr_time((S - np.convolve(S, np.ones(3600)/3600, mode="same"))[3600:-3600])

    t_h = t / 3600.0
    block_len = max(int(round(2 * tau)), 2)
    tm, ym, dt = block_means(t_h, Scorr, block_len)
    nb = len(ym)
    sigma_B2, R_block = estimate_sigma_B(ym, float(np.median(dt[1:])))

    A = np.column_stack([np.ones(nb), tm])
    beta_ols = float(np.linalg.lstsq(A, ym, rcond=None)[0][1])
    x0 = np.array([ym[0], beta_ols])
    P0 = np.diag([R_block * 10.0, (5.0 * abs(beta_ols) + 1.0) ** 2])
    q_rate = fit_rate_noise(ym, dt, R_block, sigma_B2, x0, P0)
    _, xs, Ps = kalman_loglik_and_run(ym, dt, R_block, sigma_B2, q_rate, x0, P0, smooth=True)
    level_s, level_sd = xs[:, 0], np.sqrt(Ps[:, 0, 0])
    mu_final = float(xs[-1, 1])

    figsize = (12.5, 4.8) if slide else (10, 4)
    fs_title, fs_legend, fs_label = (13, 9.5, 12) if slide else (11, 7.5, 10)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize, constrained_layout=slide)
    ax1.plot(tm, ym, color=C_RAW, lw=0.5, alpha=0.35, label="média de bloco $S_{corr}$")
    ax1.plot(tm, level_s, color=C_FIT, lw=1.8, label="nível suavizado Kalman/RTS")
    ax1.fill_between(tm, level_s - 1.96*level_sd, level_s + 1.96*level_sd,
                      color=C_FIT, alpha=0.25, label="banda de credibilidade 95%")
    ax1.set_xlabel("tempo (h)", fontsize=fs_label); ax1.set_ylabel("resíduo (contagens)", fontsize=fs_label)
    ax1.set_title("(a) Trajetória denoised (Wiener/Kalman)", fontsize=fs_title)
    ax1.legend(fontsize=fs_legend, loc="upper right")

    D_noise, D_signal = sigma_obs_native, sigma_signal
    mean_n, shape_n = ig_params(D_noise, mu_final, sigma_B2)
    mean_s, shape_s = ig_params(D_signal, mu_final, sigma_B2)
    xg = np.linspace(0.1, 3 * max(mean_n, mean_s), 800)
    for (mean, shape, D, color, lbl) in [
            (mean_n, shape_n, D_noise, C_T, f"$D=\\sigma_{{noise}}={D_noise:.2f}$"),
            (mean_s, shape_s, D_signal, C_CORR, f"$D=\\sigma_{{signal}}={D_signal:.2f}$")]:
        pdf = invgauss.pdf(xg, mu=mean/shape, scale=shape)
        med = ig_median(mean, shape)
        ax2.plot(xg, pdf, color=color, lw=2.0,
                 label=f"{lbl}\nmediana={med:.0f} h, média={mean:.0f} h")
    ax2.set_xlabel("tempo até o limiar $D$ (h)", fontsize=fs_label); ax2.set_ylabel("densidade", fontsize=fs_label)
    ax2.set_title("(b) RUL: 1ª passagem (Wiener)", fontsize=fs_title)
    ax2.legend(fontsize=fs_legend, loc="upper right")
    if slide:
        save(fig, "fig_wiener_rul_slide.pdf")
    else:
        save(fig, "fig_wiener_rul.pdf")


def main():
    os.makedirs(FIGDIR, exist_ok=True)
    t, S, T, V, Scorr = load_devA()
    fig_correction(t, S, T, Scorr)
    fig_correction(t, S, T, Scorr, slide=True)
    fig_mi(t, S, T, V)
    fig_mi(t, S, T, V, slide=True)
    fig_kl()
    fig_ica(t, S, T, V, Scorr)
    fig_ica(t, S, T, V, Scorr, slide=True)
    fig_capacity_rul(t, S, Scorr)
    fig_wiener_rul(t, S, Scorr)
    fig_wiener_rul(t, S, Scorr, slide=True)
    print("done.")


if __name__ == "__main__":
    main()
