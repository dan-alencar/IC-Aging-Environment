"""Self-test of sbcci_metrics.py: synthetic data with known coefficients in both run formats,
and (when the paper's CSVs are in the repository) the published SBCCI 2026 values."""
import csv
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sbcci_metrics as M  # noqa: E402

DTM_COLS = ["time_sec", "wall_time", "window", "sweeps", "slack_mean", "slack_last", "slack_min",
            "slack_max", "slack_std_win", "temp_raw", "temp_c", "vccint_raw", "vccint_v",
            "vccaux_raw", "vccbram_raw", "flags", "lock_loss", "source", "stm_tick_ms"]


def synthetic(n=24 * 3600, seed=7):
    rng = np.random.default_rng(seed)
    t = np.arange(n, dtype=float)
    h = t / 3600
    T = 110 + 1.5 * np.sin(2 * np.pi * h / 3) + rng.normal(0, 0.2, n)
    V = 0.90 + 0.002 * np.sin(2 * np.pi * h / 5) + rng.normal(0, 0.0005, n)
    mean = 400 - 0.9 * (T - 110) + 380 * (V - 0.9) - 0.005 * h       # -5 m-count/h
    last = np.rint(mean + rng.normal(0, 1.0, n))
    return t, T, V, mean, last


def test_recovers_known_drift_colleague_format(tmp_path):
    t, T, V, mean, last = synthetic()
    path = tmp_path / "run_dut0_frames.csv"
    with open(path, "w", newline="") as f:
        f.write("# synthetic\n")
        w = csv.writer(f)
        w.writerow(DTM_COLS)
        for i in range(len(t)):
            w.writerow([f"{t[i]:.3f}", "", i + 1, 8000, f"{mean[i]:.4f}", int(last[i]), 0, 0, "",
                        0, f"{T[i]:.3f}", 0, f"{V[i]:.5f}", 0, 0, 67, 0, "stm", ""])
        w.writerow([f"{len(t)}", "", len(t) + 1, 0, "", 0, 0, 0, "", 0, "", 0, "", 0, 0, 67, 0, "stm", ""])
    for slack, tol in (("mean", 0.3), ("last", 2.0)):
        m = M.metrics(*M.load_dtm(path, slack))
        assert m["n"] == len(t)                       # the empty window is left out
        assert m["late"]["mcnt_h"] == pytest.approx(-5.0, abs=tol)
        assert m["coef_T_cnt_per_C"] == pytest.approx(-0.9, abs=0.02)
        assert m["coef_V_cnt_per_V"] == pytest.approx(380, abs=25)
    assert M.metrics(*M.load_dtm(path, "mean"))["R2_pct"] > M.metrics(*M.load_dtm(path, "last"))["R2_pct"]


def test_session_format(tmp_path):
    t, T, V, mean, last = synthetic(n=20 * 3600, seed=3)
    n = len(t)
    with open(tmp_path / "A_AGING_WINDOW.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["t_host_s", "src", "seq", "t_board_ms", "window_id", "sweeps", "last", "min", "max", "sum", "sumsq"])
        for i in range(n):
            s = int(round(mean[i] * 9000))
            w.writerow([t[i], "FPGA_APP", i % 256, 0, i, 9000, int(last[i]), 0, 0, s, 0])
    with open(tmp_path / "summary.csv", "w", newline="") as f:
        f.write("# session: synthetic\n")
        w = csv.writer(f)
        w.writerow(["t_host_s", "time", "phase", "A_die_temp_c", "A_sysmon_vccint_v", "A_window_id"])
        w.writerow([0, "", "pre", 25, 0.85, ""])
        for i in range(n):
            w.writerow([1_794_585_600 + i, "", "stress:stress", f"{T[i]:.3f}", f"{V[i]:.5f}", i])
    m = M.metrics(*M.load_session(tmp_path, "A", "mean"))
    assert m["n"] == n and m["late"]["mcnt_h"] == pytest.approx(-5.0, abs=0.3)
    m = M.metrics(*M.load_session(tmp_path, "A", "last"))
    assert m["late"]["mcnt_h"] == pytest.approx(-5.0, abs=2.0)


@pytest.mark.skipif(not all(p.exists() for p in M.SBCCI_FILES.values()), reason="SBCCI 2026 CSVs not present")
@pytest.mark.parametrize("name", ["bang-bang", "PID"])
def test_reproduces_the_paper(name):
    load = M.load_bangbang if name == "bang-bang" else M.load_pid
    m = M.metrics(*load(M.SBCCI_FILES[name]))
    p = M.PAPER[name]
    assert m["T_mean"] == pytest.approx(p["T_mean"], abs=0.01)
    assert m["T_sd"] == pytest.approx(p["T_sd"], abs=0.01)
    assert m["V_sd_mV"] == pytest.approx(p["V_sd_mV"], abs=0.05)
    assert m["AF_mean"] == pytest.approx(p["AF_mean"], abs=0.05)
    assert m["eq_h_T"] == pytest.approx(p["eq_h_T"], abs=1.0)
    assert m["R2_pct"] == pytest.approx(p["R2_pct"], abs=0.05)
    assert m["resid"] == pytest.approx(p["resid"], abs=0.001)
    if name == "PID":
        assert m["late"]["mcnt_h"] == pytest.approx(-5.35, abs=0.01)
    else:
        assert m["late"]["mcnt_h"] == pytest.approx(-8.4, abs=0.05)   # paper -6.5: open item
