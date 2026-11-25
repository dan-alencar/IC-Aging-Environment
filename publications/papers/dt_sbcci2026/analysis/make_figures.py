#!/usr/bin/env python3
"""Figures for the D&T manuscript (hybrid version).

fig_stress.pdf : (a) PID/bang-bang AF ratio vs Ea from the measured
                 trajectories (mean-only, ripple-only, setpoint-shifted); (b) tracking budget.
fig_allan.pdf  : overlapping Hadamard deviation of (a) die temperature and
                 (b) the PVT-corrected residual, all four logs.
fig_drift.pdf  : long PID run: (a) window-slope spread vs window length;
                 (b) drift for different regressor sets.
"""
from __future__ import annotations

import json
import math

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


TS = json.loads((G / "results_timescales.json").read_text())
RUNS = (("bb23", "BB-23 (inverters)", BB, "-", 1.5), ("bb164", "BB-164 (inverters)", BB, ":", 1.3),
        ("pid23", "PID-23 (inverters)", PID, "--", 1.2), ("rca212", "PID-214 (adder)", PID, "-", 1.8))


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
    # counterfactual: thermostat raised by the PID air offset; die follows air with gain 1 or the measured gain
    for g, ls_, lab in ((1.0, (0, (5, 2)), "BB raised by air offset (die gain 1)"),
                        (TS["die_vs_air"]["rca212"]["gain_ols"], (0, (1, 1.5)), "BB raised by air offset (measured gain)")):
        adj = np.array([L.af(pid.T, e).mean() / L.af(bb.T + g * D["sp_offset"], e).mean() for e in Ea])
        a.plot(Ea, adj, color=MUT, ls=ls_, lw=1.0, label=lab)
    a.axhline(1, color=MUT, lw=0.6)
    a.axvspan(0.5, 0.9, color="#f1f1ee", zorder=0)
    r07 = D["af_ratio"]["0.7"]
    a.scatter([0.7], [r07], s=22, color=PID, zorder=5, edgecolor="white", linewidth=1)
    a.annotate(f"{r07:.2f}×", (0.7, r07), xytext=(0.8, r07 - 0.32), fontsize=7.5, color=INK,
               arrowprops=dict(arrowstyle="-", lw=0.5, color=MUT))
    a.set_xlabel("Activation energy $E_a$ (eV)"); a.set_ylabel("AF ratio, PID / bang-bang")
    a.set_ylim(0.9, 2.4); a.grid(True, axis="y"); a.legend(frameon=False, loc="upper left", fontsize=6.0)
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
    b.set_title("(b) Tracking budget, Eq. (3), at 115 °C", loc="left")
    save(fig, "fig_stress")
    plt.close(fig)


def fig_allan():
    """(a) Hadamard deviation of die temperature; (b) of the PVT-corrected slack residual,
    with the long run's mean drift drawn as an Allan line |beta| tau / sqrt(2)."""
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.45), constrained_layout=True)
    for key, lab, col, ls, lw in RUNS:
        a = TS["allan"][key]
        tau_h = np.array(a["taus"]) / 3600.0
        keep = tau_h <= tau_h[-1] * 3 / 5          # at least ~5 windows per averaging time
        ax[0].loglog(tau_h[keep], np.array(a["hdev_T"])[keep], color=col, ls=ls, lw=lw, label=lab)
        ax[1].loglog(tau_h[keep], np.array(a["hdev_res"])[keep], color=col, ls=ls, lw=lw, label=lab)
    for b in ax:
        b.axvspan(1.0, 4.0, color="#f1f1ee", zorder=0)
        b.set_xlabel("Averaging time $\\tau$ (h)"); b.grid(True, which="major")
        b.set_xlim(5e-4, 80)
    ax[0].set_ylabel("Die temperature HDEV (°C)")
    ax[0].set_title("(a) What the bench does to the die", loc="left")
    ax[0].set_ylim(0.03, 12)
    ax[0].legend(frameon=False, loc="upper left", fontsize=6.3, ncol=2, columnspacing=0.8)
    beta = abs(TS["windows"]["beta"])
    th = np.logspace(0, math.log10(80), 50)
    ax[1].loglog(th, beta * th / math.sqrt(2), color=INK, lw=0.8, ls="-.")
    ax[1].text(2.2, beta * 30 / math.sqrt(2), "drift, $|\\beta|\\tau/\\sqrt{2}$", fontsize=7, color=INK)
    t0 = 2.0 / 3600
    w0 = TS["allan"]["rca212"]["hdev_res"][0]
    tw = np.logspace(math.log10(t0), 1.5, 20)
    ax[1].loglog(tw, w0 * (tw / (1 / 3600)) ** -0.5, color=MUT, lw=0.6, ls=":")
    ax[1].text(0.02, 0.012, "white, $\\tau^{-1/2}$", fontsize=7, color=MUT)
    ax[1].set_ylabel("Corrected-slack HDEV (cnt)")
    ax[1].set_ylim(5e-3, 2)
    ax[1].set_title("(b) What the sensor sees after PVT correction", loc="left")
    save(fig, "fig_allan")
    plt.close(fig)


def fig_drift():
    """(a) Spread of window slopes vs window length on the long run; (b) drift vs regressor set."""
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.35), constrained_layout=True, gridspec_kw=dict(width_ratios=[1.1, 1]))
    a = ax[0]
    W = TS["windows"]
    Ws = np.array(sorted(int(k) for k in W["table"]))
    sd = np.array([W["table"][str(w)]["sd_noise"] for w in Ws]) * 1000
    lo = np.array([W["table"][str(w)]["min"] for w in Ws]) * 1000
    hi = np.array([W["table"][str(w)]["max"] for w in Ws]) * 1000
    beta = abs(W["beta"]) * 1000
    a.loglog(Ws, 3 * sd, "o-", color=PID, ms=3.5, label="3 × noise spread of window slopes")
    a.loglog(Ws, 3 * sd[0] * (Ws / Ws[0]) ** -1.5, color=MUT, ls=":", lw=0.9, label="white-noise scaling, $W^{-3/2}$")
    a.axhline(beta, color=INK, lw=0.8, ls="-.")
    a.text(6.3, beta * 0.72, f"mean drift, {beta:.1f} m cnt/h", fontsize=7, color=INK)
    a.axvline(W["W_star_h"], color=PID, lw=0.7, ls="--")
    a.text(W["W_star_h"] * 1.05, 250, f"{W['W_star_h']:.0f} h", fontsize=7, color=PID)
    a.set_xlabel("Window length $W$ (h)"); a.set_ylabel("Slope (m cnt/h)")
    a.set_xlim(5, 110); a.set_ylim(2, 600); a.grid(True, which="major"); a.legend(frameon=False, loc="lower left", fontsize=6.3)
    a.set_title("(a) How long a window must be", loc="left")
    b = ax[1]
    rg = TS["regressors"]
    rows = (("TV", "$T$, $V$ (die)", PID), ("TVO", "+ oven air", MUT), ("TVI", "+ supply current", MUT),
            ("TVP", "+ supply voltage", MUT), ("TVOP", "+ oven air, supply voltage", MUT))
    for i, (k, lab, col) in enumerate(rows):
        x = rg[k]
        b.errorbar(-1000 * x["beta"], i, xerr=[[1000 * (x["beta"] - x["lo"]) * -1 * -1], [1000 * (x["hi"] - x["beta"])]],
                   fmt="o", color=col, ms=4, capsize=2, lw=1.2)
    b.set_yticks(range(len(rows))); b.set_yticklabels([r[1] for r in rows]); b.invert_yaxis()
    # smallest rate this run resolves under the 1-4 h floor: 2*3*sqrt(2)*floor / run length
    _R = json.loads((G / "results_sensor.json").read_text())["rca212"]
    _minres = 1000 * 2 * 3 * math.sqrt(2) * TS["allan"]["rca212"]["floor_res"] / _R["stress"]["duration_post_h"]
    b.axvline(_minres, color=INK, lw=0.8, ls="--")
    b.text(_minres - 0.4, 3.5, "not resolved in this run", fontsize=6.3, color=INK, ha="right", va="center")
    b.set_xlabel("Drift $-\\beta$ (m cnt/h), 95 % autocorrelation-robust interval"); b.set_xlim(0, 25); b.grid(True, axis="x")
    b.set_title("(b) Drift depends on what is regressed out", loc="left")
    save(fig, "fig_drift")
    plt.close(fig)


if __name__ == "__main__":
    FIG.mkdir(parents=True, exist_ok=True)
    fig_stress()
    fig_allan()
    fig_drift()
    (G / "results_figs.json").write_text(json.dumps({}, indent=1))
    print("[write] figures fig_allan, fig_drift")
