#!/usr/bin/env python3
"""Cross-campaign quantities and the LaTeX macro file.

Reads generated/results_sensor.json and generated/results_pid.json, computes
the ratios / projections used in the paper, writes generated/results_derived.json
and generated/values.tex (every scalar the manuscript prints).

Projection model (stated in the paper): T_min ∝ sigma^(2/3) tau^(1/3) |beta|^(-2/3)
(Eq. tmin), with beta ∝ <AF> (assumption) and the bang-bang/PID noise ratios
taken from the matched 23.08 h pair (same CUT), tau in samples so the
comparison is at equal logging cadence.
"""
from __future__ import annotations

import json
import math

import numpy as np

import dtlib as L

G = L.PAPER / "generated"
R = json.loads((G / "results_sensor.json").read_text())
P = json.loads((G / "results_pid.json").read_text())


def stress_view(r):
    """Stress-delivery statistics over the whole run (SBCCI 2026 Table II convention).
    Regression/noise/detectability statistics stay post-soak (SBCCI 2026 Table III convention)."""
    s = r["stress"]
    return dict(
        T_mean=s["T_mean_full"], T_sd=s["T_sd_full"], die_err=s["T_mean_full"] - r["die_target_c"],
        AF=s["AF_full"], AF_of_mean=s["AF_of_mean_full"], V_sd_mV=s["V_sd_full_mV"],
        ripple_pct={k: 100 * (s["AF_full"][k] / s["AF_of_mean_full"][k] - 1) for k in s["AF_full"]},
        # equivalent hours as SBCCI 2026 Table I: AF(mean T) x the stated run length (2 decimals, 23.08 h)
        eqh_meanT={k: s["AF_of_mean_full"][k] * round(s["duration_raw_h"], 2) for k in s["AF_full"]},
    )


SV = {k: stress_view(v) for k, v in R.items()}


def derived():
    bb, pid, bb164, rca = R["bb23"], R["pid23"], R["bb164"], R["rca212"]
    sbb, spid = SV["bb23"], SV["pid23"]
    d = {}
    # ---- stress
    d["dT"] = pid["stress"]["T_mean"] - bb["stress"]["T_mean"]
    d["dT_full"] = pid["stress"]["T_mean_full"] - bb["stress"]["T_mean_full"]
    d["af_ratio"] = {k: spid["AF"][k] / sbb["AF"][k] for k in sbb["AF"]}
    d["af_ratio_meanonly"] = {k: spid["AF_of_mean"][k] / sbb["AF_of_mean"][k] for k in sbb["AF"]}
    d["af_ratio_post"] = {k: pid["stress"]["AF"][k] / bb["stress"]["AF"][k] for k in bb["stress"]["AF"]}
    d["af_ratio_full"] = {k: pid["stress"]["AF_full"][k] / bb["stress"]["AF_full"][k] for k in bb["stress"]["AF"]}
    d["af_ratio_meanonly_full"] = {k: pid["stress"]["AF_of_mean_full"][k] / bb["stress"]["AF_of_mean_full"][k] for k in bb["stress"]["AF"]}
    # share of the log AF gap explained by the mean shortfall alone
    k07 = "0.7"
    d["mean_share_pct"] = 100 * math.log(d["af_ratio_meanonly"][k07]) / math.log(d["af_ratio"][k07])
    # tracking budget delta(eta) at 115 degC, 0.7 eV, and each bench's AF deviation vs target
    d["delta"] = {f"{e:g}": L.delta_budget(e) for e in (0.05, 0.10, 0.20)}
    for nm, r in (("bb", bb), ("pid", pid)):
        d[f"af_dev_{nm}_pct"] = 100 * (L.af(SV[r["key"]]["T_mean"]) / L.af(r["die_target_c"]) - 1)
    # ---- noise ratios (same CUT, matched commands)
    d["sig_raw_ratio"] = bb["noise"]["resid_sd_raw"] / pid["noise"]["resid_sd_raw"]
    d["sig_rev_ratio"] = bb["detect"]["sigma"] / pid["detect"]["sigma"]
    # tau ratio at a common 2 s sampling interval (PID log decimated to the coarser log's interval)
    tau_bb_s = bb["detect"]["tau_int_s"]
    tau_pid_s = pid["decimated_2s"]["tau_int_s"]
    d["tau_bb_s"], d["tau_pid_s"] = tau_bb_s, tau_pid_s
    d["tau_bb_samples"], d["tau_pid_samples"] = tau_bb_s / 2.0, tau_pid_s / 2.0
    d["tau_ratio"] = tau_bb_s / tau_pid_s
    d["sig_raw_ratio_common"] = bb["noise"]["resid_sd_raw"] / pid["decimated_2s"]["resid_sd_raw"]
    # ---- detectability penalty: T_min ∝ sigma^(2/3) tau^(1/3) beta^(-2/3)
    n_law = rca["detect"]["powerlaw"]["n"]
    sr23 = d["sig_raw_ratio"] ** (2 / 3)          # SBCCI 2026 residual definition (Table III)
    d["n_law"] = n_law
    d["pen_noise"] = sr23
    d["pen_noise_tau"] = sr23 * d["tau_ratio"] ** (1 / 3)
    d["pen_stress"] = {k: v ** (2 / 3) for k, v in d["af_ratio"].items()}            # beta ∝ <AF>
    d["pen_stress_pow"] = {k: v ** (2 * n_law / 3) for k, v in d["af_ratio"].items()}  # D ∝ (AF t)^n
    d["pen_low"] = sr23 * d["pen_stress_pow"][k07]
    d["pen_mid"] = {k: sr23 * v for k, v in d["pen_stress"].items()}
    d["pen_high"] = d["pen_noise_tau"] * d["pen_stress"][k07]
    d["pen_total"] = d["pen_mid"]                                                     # used by the figure band centre
    dr = rca["detect"]
    d["tmin_pid"] = dict(bound=dr["T_min"], tip=dr["T_min_tip"], tip_corr=dr["T_min_tip_corrected"],
                         lrv8=dr["T_min_lrv8"], seq=dr.get("sequential_detect_h"))
    d["tmin_bb_proj"] = {kk: [d["tmin_pid"][kk] * d["pen_low"], d["tmin_pid"][kk] * d["pen_mid"][k07], d["tmin_pid"][kk] * d["pen_high"]]
                         for kk in ("bound", "lrv8", "seq")}
    # Jensen (second-order) prediction of the ripple gain, for comparison with the exact trajectory value
    Tk = sbb["T_mean"] + 273.15
    d["jensen_bb_pct"] = 100 * 0.5 * (0.7 / L.K_B / Tk ** 2 * sbb["T_sd"]) ** 2
    # ---- alarm capacity (BSC) at the RCA operating point
    sig, tau_h, beta = dr["sigma"], dr["tau_int_s"] / 3600, dr["beta"]
    lrv8_tau_h = dr["lrv"]["8"] / (2 * sig ** 2) / 3600               # tau equivalent of the 8 h long-run variance
    def cap(w, s, t, b):
        return float(L.bsc_capacity(w, s, t, b))
    af = d["af_ratio"][k07]
    s_bb, t_bb = sig * d["sig_raw_ratio"], tau_h * d["tau_ratio"]
    d["bsc"] = {
        "pid_bound_24": cap(24, sig, tau_h, beta), "bb_bound_24": cap(24, s_bb, t_bb, beta / af),
        "pid_lrv_24": cap(24, sig, lrv8_tau_h, beta), "bb_lrv_24": cap(24, s_bb, lrv8_tau_h * d["tau_ratio"], beta / af),
        "pid_bound_1": cap(1, sig, tau_h, beta),
    }
    def perr(w, s_, t_, b_):
        return float(L.qfunc(abs(b_) * w / (s_ * math.sqrt(4 * t_ / w)) / 2))
    d["bsc"]["p_pid_bound_24"] = perr(24, sig, tau_h, beta); d["bsc"]["p_bb_bound_24"] = perr(24, s_bb, t_bb, beta / af)
    d["bsc"]["p_pid_lrv_24"] = perr(24, sig, lrv8_tau_h, beta); d["bsc"]["p_bb_lrv_24"] = perr(24, s_bb, lrv8_tau_h * d["tau_ratio"], beta / af)
    ws = np.logspace(-1, 3, 40001)
    for nm, args in (("pid_bound", (sig, tau_h, beta)), ("bb_bound", (s_bb, t_bb, beta / af)),
                     ("pid_lrv", (sig, lrv8_tau_h, beta)), ("bb_lrv", (s_bb, lrv8_tau_h * d["tau_ratio"], beta / af))):
        c = L.bsc_capacity(ws, *args)
        d["bsc"][f"{nm}_w99"] = float(ws[np.argmax(c >= 0.99)])
    d["lrv8_tau_equiv_s"] = lrv8_tau_h * 3600
    # ---- long-run stationarity of the bench noise
    d["bb164_vs_bb23_sigma"] = bb164["detect"]["sigma"] / bb["detect"]["sigma"]
    d["rca_first23_vs_full_sigma"] = rca["first23h"]["resid_sd_rev"] / rca["detect"]["sigma"]
    # ---- drift magnitude in ps, with the CUT-specific MMCM step
    d["ps_step"] = {"INV50": 1e12 / (56 * 900e6), "RCA16": 1e12 / (56 * 1000e6)}
    d["rca_drift_ps"] = abs(dr["drift_total_cnt"]) * d["ps_step"]["RCA16"]
    d["rca_drift_ps_at_19p85"] = abs(dr["drift_total_cnt"]) * 19.85   # same drift at the inverter-chain step
    d["sigma_rev_degC"] = {k: R[k]["noise"]["resid_rev_degC_equiv"] for k in R}
    return d


# ------------------------------------------------------------------ LaTeX
def fmt(x, nd):
    if x is None or (isinstance(x, float) and not math.isfinite(x)):
        return "\\textbf{??}"
    s = f"{x:,.{nd}f}" if abs(x) >= 1000 and nd == 0 else f"{x:.{nd}f}"
    return s.replace(",", "{,}").replace("-", "$-$", 1) if s.startswith("-") else s.replace(",", "{,}")


def macros(d):
    m = {}
    bb, pid, bb164, rca = R["bb23"], R["pid23"], R["bb164"], R["rca212"]
    def put(name, val, nd):
        m[name] = fmt(val, nd)
    # campaigns
    for tag, r in (("BB", bb), ("PID", pid), ("BBlong", bb164), ("RCA", rca)):
        s, n, de, mi = r["stress"], r["noise"], r["detect"], r["mi"]
        sv = SV[r["key"]]
        put(f"T{tag}", sv["T_mean"], 2); put(f"Tsd{tag}", sv["T_sd"], 2); put(f"Terr{tag}", sv["die_err"], 2)
        put(f"AF{tag}", sv["AF"]["0.7"], 1); put(f"Vsd{tag}", sv["V_sd_mV"], 1); put(f"Vmean{tag}", s["V_mean_full"], 4)
        put(f"Dur{tag}", s["duration_raw_h"], 1); put(f"DurPost{tag}", s["duration_post_h"], 1)
        put(f"Npost{tag}", s["n_post"], 0); put(f"Nraw{tag}", s["n_raw"], 0); put(f"Cad{tag}", s["cadence_s"], 0)
        put(f"Eqh{tag}", sv["eqh_meanT"]["0.7"], 0)
        put(f"Ripple{tag}", sv["ripple_pct"]["0.7"], 1)
        put(f"Rsq{tag}", 100 * n["R2_TV"], 1); put(f"RsqT{tag}", 100 * n["R2_T"], 1)
        put(f"SigRaw{tag}", n["resid_sd_raw"], 2); put(f"Sig{tag}", de["sigma"], 2)
        put(f"SigC{tag}", n["resid_rev_degC_equiv"], 2); put(f"kT{tag}", abs(n["kT_cnt_per_C"]), 2)
        put(f"Tau{tag}", de["tau_int_s"], 0); put(f"TauTip{tag}", de["tau_int_tip_s"], 0)
        put(f"Beta{tag}", 1000 * de["beta"], 1)
        put(f"BetaLo{tag}", 1000 * de["beta_hac8"]["lo"], 1); put(f"BetaHi{tag}", 1000 * de["beta_hac8"]["hi"], 1)
        put(f"PowN{tag}", de["powerlaw"]["n"], 2); put(f"dBIC{tag}", de["powerlaw"]["dbic"], 0)
        put(f"Lrv{tag}", de["lrv"]["1"], 0)
        put(f"HS{tag}", mi["H_S"], 2); put(f"MIraw{tag}", mi["I_raw"], 2); put(f"MIres{tag}", mi["I_res"], 3)
        put(f"MIresQ{tag}", mi["I_res_quant_sim"], 3); put(f"MIdt{tag}", mi["I_dt"], 2)
        put(f"Hyst{tag}", r["hysteresis"]["gap_heat_minus_cool"], 2)
        put(f"Lag{tag}", r["hysteresis"]["xcorr_lag_s"], 0)
    for tag, r in (("BB", bb), ("PID", pid)):
        for w in r["noise"]["windows"]:
            if w["a"] == 12.0:
                put(f"LateSlope{tag}", 1000 * w["slope"], 1); put(f"LateLo{tag}", 1000 * w["lo"], 1); put(f"LateHi{tag}", 1000 * w["hi"], 1)
    # RCA specifics
    dr, mr = rca["detect"], rca["mi"]
    put("RCAoven", rca["stress"]["oven_temp_c"]["mean"], 1); put("RCAovensd", rca["stress"]["oven_temp_c"]["sd"], 1)
    put("RCAovenMin", rca["stress"]["oven_temp_c"]["min"], 1); put("RCAovenMax", rca["stress"]["oven_temp_c"]["max"], 1)
    put("RCATmin", rca["stress"]["T_min"], 0); put("RCATmax", rca["stress"]["T_max"], 0)
    put("RCAspMin", rca["stress"]["oven_setpoint_c"]["min"], 0); put("RCAspMax", rca["stress"]["oven_setpoint_c"]["max"], 0)
    put("RCAspChanges", rca["controls"]["setpoint_changes"], 0)
    put("RCAneff", dr["n_eff"], 0); put("RCAcrlb", 1000 * dr["crlb_sd"], 2); put("RCAfloor", 1000 * dr["floor_3sigma"], 1)
    put("RCAbayes", 1000 * dr["bayes"]["slope"], 1); put("RCAbayesLo", 1000 * dr["bayes"]["lo"], 1); put("RCAbayesHi", 1000 * dr["bayes"]["hi"], 1)
    put("RCAfirstHalf", 1000 * dr["beta_first_half"]["slope"], 1); put("RCAsecondHalf", 1000 * dr["beta_second_half"]["slope"], 1)
    put("RCAdriftCnt", abs(dr["drift_total_cnt"]), 1); put("RCAdriftPs", d["rca_drift_ps"], 0)
    put("RCAcorrStRaw", rca["noise"]["corr_St_raw"], 2); put("RCAcorrStCorr", rca["noise"]["corr_St_corr"], 2)
    put("RCAMIrawLo", mr["I_raw_ci"][0], 2); put("RCAMIrawHi", mr["I_raw_ci"][1], 2)
    put("RCAMIksg", mr["I_raw_ksg"], 2); put("RCAnull", mr["null_p95"], 2)
    put("RCAMIremoved", mr["removed_pct_binned"], 0)
    put("RCAcurrSlope", rca["controls"]["psu_current_resid_slope_mA_per_h"]["slope"], 3)
    put("RCAlrvEight", dr["lrv"]["8"], 0); put("RCAlrvQuarter", dr["lrv"]["0.25"], 0)
    put("RCAlrvWhite", dr["lrv_white_equiv"], 0)
    put("BBlongLrvEight", bb164["detect"]["lrv"]["8"], 0)
    # derived
    for k in ("0.5", "0.7", "0.9"):
        tag = {"0.5": "Lo", "0.7": "", "0.9": "Hi"}[k]
        put(f"AFratio{tag}", d["af_ratio"][k], 2)
        put(f"AFratioFull{tag}", d["af_ratio_full"][k], 2)
        put(f"PenMid{tag}", d["pen_mid"][k], 2)
    put("PenLow", d["pen_low"], 2); put("PenHigh", d["pen_high"], 2); put("NLaw", d["n_law"], 2)
    put("PenStressPow", d["pen_stress_pow"]["0.7"], 2)
    put("Jensen", d["jensen_bb_pct"], 1)
    for tag, r in (("BB", bb), ("PID", pid)):
        s_ = r["stress"]
        put(f"Tfull{tag}", s_["T_mean_full"], 2); put(f"TsdFull{tag}", s_["T_sd_full"], 2)
        put(f"AFfull{tag}", s_["AF_full"]["0.7"], 1); put(f"VsdFull{tag}", s_["V_sd_full_mV"], 1)
        put(f"TerrFull{tag}", s_["T_mean_full"] - r["die_target_c"], 2)
    put("TsdRatioFull", bb["stress"]["T_sd_full"] / pid["stress"]["T_sd_full"], 1)
    put("AFratioMeanOnly", d["af_ratio_meanonly"]["0.7"], 2)
    put("AFratioFull", d["af_ratio_full"]["0.7"], 2)
    put("MeanShare", d["mean_share_pct"], 0)
    put("dT", d["dT"], 2); put("dTfull", d["dT_full"], 2)
    for k, tag in (("0.05", "Five"), ("0.1", "Ten"), ("0.2", "Twenty")):
        put(f"Delta{tag}", d["delta"][k], 1)
    put("AFdevBB", d["af_dev_bb_pct"], 0); put("AFdevPID", d["af_dev_pid_pct"], 0)
    put("SigRawRatio", d["sig_raw_ratio"], 2); put("SigRatio", d["sig_rev_ratio"], 2)
    put("SigRawRatioPct", 100 * (d["sig_raw_ratio"] - 1), 0); put("SigRatioPct", 100 * (d["sig_rev_ratio"] - 1), 0)
    put("TauRatio", d["tau_ratio"], 2); put("TauBBsamp", d["tau_bb_samples"], 1); put("TauPIDsamp", d["tau_pid_samples"], 1)
    b_ = d["bsc"]
    put("PenNoise", d["pen_noise"], 2); put("PenStress", d["pen_stress"]["0.7"], 2)
    put("DurPair", bb["stress"]["duration_raw_h"], 2)
    put("PIDspMin", pid["stress"]["oven_setpoint_c"]["min"], 0); put("PIDspMax", pid["stress"]["oven_setpoint_c"]["max"], 0)
    put("DurPairPost", pid["stress"]["duration_post_h"], 0)
    put("PenNoiseSigOnly", d["sig_raw_ratio"] ** (2 / 3), 2)
    put("TauBBs", d["tau_bb_s"], 1); put("TauPIDs", d["tau_pid_s"], 1)
    put("SigRawRatioCommon", d["sig_raw_ratio_common"], 2)
    put("PerrPidBound", 100 * b_["p_pid_bound_24"], 1); put("PerrBbBound", 100 * b_["p_bb_bound_24"], 1)
    put("PerrPidLrv", 100 * b_["p_pid_lrv_24"], 0); put("PerrBbLrv", 100 * b_["p_bb_lrv_24"], 0)
    pb = rca["detect"]["powerlaw_block2h"]; put("dBICblockRCA", pb["dbic"], 0); put("PowNblockRCA", pb["n"], 2)
    pb2 = bb164["detect"]["powerlaw_block2h"]; put("dBICblockBBlong", pb2["dbic"], 0)
    sj = rca["controls"]["setpoint_jump"]
    put("SPjumpFrac", 100 * sj["frac_above_null95"], 0); put("SPjumpN", sj["n"], 0)
    put("EqhMeanOnlyBB", bb["stress"]["AF_of_mean_full"]["0.7"] * 23.08, 0)
    put("EqhMeanOnlyPID", pid["stress"]["AF_of_mean_full"]["0.7"] * 23.08, 0)
    put("TsdRatio", SV["bb23"]["T_sd"] / SV["pid23"]["T_sd"], 1)
    put("AFratioLoOne", d["af_ratio"]["0.5"], 1); put("AFratioHiOne", d["af_ratio"]["0.9"], 1)
    # post-soak counterparts, used only by the internal RECONCILIATION note
    for tag, r in (("BB", bb), ("PID", pid)):
        put(f"EqhTraj{tag}", r["stress"]["eqh_full"]["0.7"], 0)
        put(f"Tpost{tag}", r["stress"]["T_mean"], 2); put(f"TsdPost{tag}", r["stress"]["T_sd"], 2)
        put(f"RipplePost{tag}", r["stress"]["ripple_pct"]["0.7"], 1)
    put("SigRevRatio", d["sig_rev_ratio"], 2); put("SigRevRatioPct", 100 * (d["sig_rev_ratio"] - 1), 0)
    put("RCAneffSeq", rca["detect"]["n_eff"], 0)
    put("RCAMIrawCIlo", rca["mi"]["I_raw_ci"][0], 2); put("RCAMIrawCIhi", rca["mi"]["I_raw_ci"][1], 2)
    put("MIexcessBB", bb["mi"]["I_res"] - bb["mi"]["I_res_quant_sim"], 2)
    put("MIexcessBBlong", bb164["mi"]["I_res"] - bb164["mi"]["I_res_quant_sim"], 2)
    put("HystPct", 100 * abs(bb["hysteresis"]["gap_heat_minus_cool"]) / bb["detect"]["sigma"], 0)
    put("DtdtGainPct", 100 * (1 - bb["hysteresis"]["resid_sd_raw_with_dTdt"] / bb["hysteresis"]["resid_sd_raw_same_slice"]), 1)
    put("SeqZpid", json.loads((G / "results_figs.json").read_text())["z_pid_22"] if (G / "results_figs.json").exists() else None, 1)
    _fz = json.loads((G / "results_figs.json").read_text()) if (G / "results_figs.json").exists() else {}
    put("SeqZbb", _fz.get("z_bb_proj_22"), 1)
    put("RCAlrvGrowth", rca["detect"]["lrv"]["8"] / rca["detect"]["lrv"]["0.25"], 0)
    t = d["tmin_pid"]; tb = d["tmin_bb_proj"]
    put("TminBound", t["bound"], 0); put("TminTip", t["tip"], 0); put("TminTipCorr", t["tip_corr"], 0)
    put("TminLrv", t["lrv8"], 0); put("TminSeq", t["seq"], 0)
    put("TminSeqBBlong", bb164["detect"].get("sequential_detect_h"), 0)
    for kk, tag in (("bound", "Bound"), ("lrv8", "Lrv"), ("seq", "Seq")):
        put(f"TminBB{tag}Lo", tb[kk][0], 0); put(f"TminBB{tag}", tb[kk][1], 0); put(f"TminBB{tag}Hi", tb[kk][2], 0)
    b = d["bsc"]
    put("CpidBound", b["pid_bound_24"], 2); put("CbbBound", b["bb_bound_24"], 2)
    put("CpidLrv", b["pid_lrv_24"], 2); put("CbbLrv", b["bb_lrv_24"], 2); put("CpidHour", b["pid_bound_1"], 2)
    put("WpidBound", b["pid_bound_w99"], 0); put("WbbBound", b["bb_bound_w99"], 0)
    put("WpidLrv", b["pid_lrv_w99"], 0); put("WbbLrv", b["bb_lrv_w99"], 0)
    put("BBlongSigRatio", d["bb164_vs_bb23_sigma"], 2); put("RCAfirstSigRatio", d["rca_first23_vs_full_sigma"], 2)
    put("PsINV", d["ps_step"]["INV50"], 2); put("PsRCA", d["ps_step"]["RCA16"], 2)
    # PID bench
    st, sm, ts = P["step"]["two_point"], P["simc"], P["tests"]
    put("FopdtK", st["K"], 2); put("FopdtTheta", st["theta"], 1); put("FopdtTau", st["tau"], 1); put("FopdtTzero", P["step"]["T0"], 2)
    put("FopdtRmse", st["rmse"], 1); put("FopdtTmax", st["T_max"], 1); put("FopdtTfinal", st["T_final"], 1)
    put("SimcKp", sm["Kp"], 2); put("SimcKiE", sm["Ki"] * 1e3, 2)
    fg = P["final_gains"]; put("FinalKp", fg["Kp"], 2); put("FinalKiE", fg["Ki"] * 1e3, 2); put("FinalKd", fg["Kd"], 1)
    for k, tag in (("thermostat", "Thermo"), ("simc", "Simc"), ("tuned", "Tuned")):
        x = ts[k]
        put(f"Sd{tag}", x["ss_sd"], 2); put(f"Ptp{tag}", x["ss_ptp"], 1); put(f"Emax{tag}", x["ss_abs_err_max"], 1)
        put(f"Over{tag}", x["overshoot"], 1)
    put("SdRatioThermo", ts["thermostat"]["ss_sd"] / ts["tuned"]["ss_sd"], 1)
    return m


def main():
    d = derived()
    (G / "results_derived.json").write_text(json.dumps(d, indent=1, default=float))
    m = macros(d)
    lines = ["% AUTO-GENERATED by analysis/derive.py -- do not edit by hand.",
             "% Every number printed in the manuscript comes from one of these macros."]
    bad = [k for k in m if not k.isalpha()]
    assert not bad, f"macro names must be letters only: {bad}"
    for k in sorted(m):
        lines.append(f"\\newcommand{{\\v{k}}}{{{m[k]}}}")
    (G / "values.tex").write_text("\n".join(lines) + "\n")
    print(f"[write] {G / 'values.tex'} ({len(m)} macros)")
    # render the human-readable reconciliation note with the same values
    tpl_path = L.PAPER / "analysis" / "RECONCILIATION.template.md"
    if not tpl_path.exists():          # internal note; not shipped in the submission package
        return
    tpl = tpl_path.read_text()
    def sub(mt):
        v = m.get(mt.group(1))
        if v is None:
            raise KeyError(f"RECONCILIATION template uses unknown macro \\v{mt.group(1)}")
        return v.replace("$-$", "−").replace("{,}", ",")
    import re
    body = re.sub(r"`?\\v([A-Za-z]+)`?", sub, tpl)
    (L.PAPER / "RECONCILIATION.md").write_text(
        "<!-- AUTO-GENERATED from analysis/RECONCILIATION.template.md by analysis/derive.py -->\n" + body)
    for k in ("AFratio", "AFratioMeanOnly", "Jensen", "RippleBB", "SigRatio", "TauRatio", "PenLow", "PenMid", "PenHigh",
              "TminBound", "TminTip", "TminTipCorr", "TminLrv", "TminSeq", "TminBBBound", "TminBBLrv", "TminBBSeq", "CpidBound", "CbbBound",
              "CpidLrv", "CbbLrv", "WpidBound", "WbbBound", "WpidLrv", "WbbLrv", "TauRCA", "TauTipRCA", "SeqZbb"):
        print(f"  {k:16s} {m[k]}")


if __name__ == "__main__":
    main()
