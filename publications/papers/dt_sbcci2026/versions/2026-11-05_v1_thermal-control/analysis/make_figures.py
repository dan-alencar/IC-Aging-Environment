#!/usr/bin/env python3
"""Figures for the D&T manuscript (style kept from the contingency draft).

fig_stress.pdf : (a) PID/bang-bang AF ratio vs Ea from the measured
                 trajectories, mean-only and ripple-only; (b) tracking budget.
fig_detect.pdf : (a) cumulative-slope significance z(T) vs run length on the
                 214 h PID run, projected bang-bang, and the 164 h bang-bang
                 Week-1 log (different CUT, context); (b) BSC alarm capacity
                 vs decision window under the bound and long-run-variance models.
"""
from __future__ import annotations

import json

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

import dtlib as L  # noqa: E402

plt.rcParams.update({
    "font.family": "serif", "font.serif": ["TeX Gyre Termes", "Nimbus Roman", "Liberation Serif", "DejaVu Serif"],
    "font.size": 8, "axes.titlesize": 8, "axes.labelsize": 8, "legend.fontsize": 7, "xtick.labelsize": 7,
    "ytick.labelsize": 7, "axes.spines.top": False, "axes.spines.right": False, "axes.linewidth": 0.6,
    "grid.color": "#e3e3e0", "grid.linewidth": 0.5, "lines.linewidth": 1.6, "savefig.dpi": 600,
    "pdf.fonttype": 42, "ps.fonttype": 3, "mathtext.fontset": "stix"})
# 15 % bang-bang orange pre-blended on white: PostScript/EPS has no transparency
BB_BAND = "#f9e8dd"


def save(fig, name):
    """Write each figure as PDF (manuscript), EPS (vector, submission) and
    600 dpi LZW-compressed TIFF (raster, submission)."""
    fig.savefig(FIG / f"{name}.pdf")
    fig.savefig(FIG / f"{name}.eps")
    # TIFF: render at 600 dpi, then flatten to RGB on white (no alpha channel for print)
    fig.savefig(FIG / f"{name}.tif", dpi=600, facecolor="white", pil_kwargs={"compression": "tiff_lzw"})
    from PIL import Image
    im = Image.open(FIG / f"{name}.tif")
    if im.mode != "RGB":
        bg = Image.new("RGB", im.size, "white")
        bg.paste(im, mask=im.split()[-1] if im.mode == "RGBA" else None)
        bg.save(FIG / f"{name}.tif", compression="tiff_lzw", dpi=(600, 600))
PID, BB, INK, MUT = "#1f5fbf", "#d9661f", "#333333", "#777777"
G = L.PAPER / "generated"
FIG = L.PAPER / "manuscript" / "figures"
R = json.loads((G / "results_sensor.json").read_text())
D = json.loads((G / "results_derived.json").read_text())


def fig_stress():
    bb, pid = L.load("bb23", soak_s=0), L.load("pid23", soak_s=0)   # whole-run trajectories (SBCCI 2026 Table II)
    Ea = np.linspace(0.4, 1.0, 121)
    full = np.array([L.af(pid.T, e).mean() / L.af(bb.T, e).mean() for e in Ea])
    mean_only = np.array([L.af(pid.T.mean(), e) / L.af(bb.T.mean(), e) for e in Ea])
    ripple = np.array([L.af(bb.T, e).mean() / L.af(bb.T.mean(), e) for e in Ea])
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.35), constrained_layout=True)
    a = ax[0]
    a.plot(Ea, full, color=PID, label="Measured trajectories (mean + ripple)")
    a.plot(Ea, mean_only, color=INK, ls="--", lw=1.1, label="Mean shortfall only")
    a.plot(Ea, ripple, color=BB, ls=":", lw=1.6, label="Ripple only (bang-bang)")
    a.axhline(1, color=MUT, lw=0.6)
    a.axvspan(0.5, 0.9, color="#f1f1ee", zorder=0)
    r07 = D["af_ratio"]["0.7"]
    a.scatter([0.7], [r07], s=22, color=PID, zorder=5, edgecolor="white", linewidth=1)
    a.annotate(f"{r07:.2f}×", (0.7, r07), xytext=(0.74, r07 - 0.23), fontsize=7.5, color=INK,
               arrowprops=dict(arrowstyle="-", lw=0.5, color=MUT))
    a.set_xlabel("Activation energy $E_a$ (eV)"); a.set_ylabel("AF ratio, PID / bang-bang")
    a.set_ylim(0.9, 2.2); a.grid(True, axis="y"); a.legend(frameon=False, loc="upper left")
    a.set_title("(a) Where the AF bias comes from", loc="left")
    b = ax[1]
    eta = np.linspace(0.01, 0.4, 200)
    for E, ls in ((0.5, ":"), (0.7, "-"), (0.9, "--")):
        b.plot(eta * 100, [L.delta_budget(x, E) for x in eta], color=PID if E == 0.7 else INK, ls=ls,
               lw=1.6 if E == 0.7 else 1.0, label=f"$E_a$ = {E} eV")
    eb = abs(R["bb23"]["stress"]["T_mean_full"] - 115.0); ep = abs(R["pid23"]["stress"]["T_mean_full"] - 115.0)
    b.axhline(eb, color=BB, lw=1.4); b.text(1.5, eb + 0.28, f"Bang-bang die shortfall, {eb:.2f} °C", color=INK, fontsize=7)
    b.axhline(ep, color=PID, lw=1.0, ls="-."); b.text(19, ep - 0.7, f"PID die overshoot, {ep:.2f} °C", color=INK, fontsize=7)
    b.set_xlabel("Tolerated AF deviation $\\eta$ (%)"); b.set_ylabel("Allowed mean die error $\\delta$ (°C)")
    b.set_ylim(0, 9); b.set_xlim(0, 40); b.grid(True, axis="y")
    b.legend(frameon=False, loc="upper left", bbox_to_anchor=(0.0, 0.78))
    b.set_title("(b) Tracking budget, Eq. (2), at 115 °C", loc="left")
    save(fig, "fig_stress")
    plt.close(fig)


def z_curve(key, step_h=1.0):
    c = L.load(key)
    _, res = L.ols(L.design(c.T, c.V), c.S)
    t_h = c.t / 3600.0
    T_tot = t_h[-1] - t_h[0]
    ends = np.arange(4.0, T_tot + 1e-9, step_h)
    z = []
    for Te in ends:
        m = t_h <= t_h[0] + Te
        s, se = L.hac_slope(c.t[m], res[m], 600.0, min(8.0, Te / 4))
        z.append(-s / se)              # positive = slack decreasing (aging direction)
    return ends, np.array(z)


def fig_detect():
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.35), constrained_layout=True)
    a = ax[0]
    tp, zp = z_curve("rca212")
    pen = D["pen_mid"]["0.7"]
    a.plot(tp, zp, color=PID, label="PID, 214 h run (measured)")
    a.plot(tp, zp / pen ** 1.5, color=BB, ls="--", label="Bang-bang (projected)")
    lo, hi = zp / D["pen_low"] ** 1.5, zp / D["pen_high"] ** 1.5
    a.fill_between(tp, lo, hi, color=BB_BAND, lw=0)
    tb, zb = z_curve("bb164")
    a.plot(tb, zb, color=MUT, ls=":", lw=1.2, label="Bang-bang, 164 h log (other CUT)")
    a.axhline(3, color=INK, lw=0.7)
    a.text(150, 3.6, "3σ", fontsize=7, color=INK)
    a.axvline(22.08, color=MUT, lw=0.8, ls=":")
    a.text(23.5, 27.5, "end of a 23 h run", fontsize=7, color=INK)
    a.set_xlabel("Run length after soak (h)"); a.set_ylabel("Drift / Newey–West s.e.")
    a.set_xlim(0, 215); a.set_ylim(0, 30); a.grid(True, axis="y")
    a.legend(frameon=False, loc="upper right")
    a.set_title("(a) When the drift becomes resolvable", loc="left")
    b = ax[1]
    dr = R["rca212"]["detect"]
    sig, tau_h, beta = dr["sigma"], dr["tau_int_s"] / 3600, dr["beta"]
    tau_lrv = D["lrv8_tau_equiv_s"] / 3600
    sr, tr, af = D["sig_rev_ratio"], D["tau_ratio"], D["af_ratio"]["0.7"]
    w = np.logspace(0, 2.6, 400)
    b.semilogx(w, L.bsc_capacity(w, sig, tau_h, beta), color=PID, label="PID, white noise")
    b.semilogx(w, L.bsc_capacity(w, sig * sr, tau_h * tr, beta / af), color=BB, label="BB, white noise")
    b.semilogx(w, L.bsc_capacity(w, sig, tau_lrv, beta), color=PID, ls="--", lw=1.1, label="PID, slow wander")
    b.semilogx(w, L.bsc_capacity(w, sig * sr, tau_lrv * tr, beta / af), color=BB, ls="--", lw=1.1,
               label="BB, slow wander")
    b.axvline(24, color=MUT, lw=0.8, ls=":"); b.text(25, 0.06, "24 h", fontsize=7, color=INK)
    b.set_xlabel("Alarm decision window (h)"); b.set_ylabel("$C_{\\mathrm{BSC}}$ (bits/decision)")
    b.set_ylim(0, 1.05); b.grid(True, axis="y"); b.legend(frameon=False, loc="upper left", fontsize=6.3, handlelength=1.8)
    b.set_title("(b) Aging-alarm reliability", loc="left")
    save(fig, "fig_detect")
    plt.close(fig)
    return dict(z_pid_22=float(np.interp(22.08, tp, zp)), z_bb_proj_22=float(np.interp(22.08, tp, zp / pen ** 1.5)),
                z_bblong_22=float(np.interp(22.08, tb, zb)))


if __name__ == "__main__":
    FIG.mkdir(parents=True, exist_ok=True)
    fig_stress()
    extra = fig_detect()
    (G / "results_figs.json").write_text(json.dumps(extra, indent=1))
    print("[write] figures", extra)
