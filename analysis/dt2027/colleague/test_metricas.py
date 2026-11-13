"""Autoteste do metricas_sbcci.py no formato _frames.csv do D&T Monitor, com dados sintéticos
de coeficientes conhecidos: o script tem de recuperar a deriva e os coeficientes de T e V."""
import csv
import os
import sys
import tempfile
import unittest

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import metricas_sbcci as M     # noqa: E402

COLS = ["time_sec", "wall_time", "window", "sweeps", "slack_mean", "slack_last", "slack_min",
        "slack_max", "slack_std_win", "temp_raw", "temp_c", "vccint_raw", "vccint_v",
        "vccaux_raw", "vccbram_raw", "flags", "lock_loss", "source", "stm_tick_ms"]


class TestDtmFormat(unittest.TestCase):
    def test_recovers_known_drift(self):
        rng = np.random.default_rng(7)
        n = 24 * 3600
        t = np.arange(n, dtype=float)
        h = t / 3600
        T = 110 + 1.5 * np.sin(2 * np.pi * h / 3) + rng.normal(0, 0.2, n)
        V = 0.90 + 0.002 * np.sin(2 * np.pi * h / 5) + rng.normal(0, 0.0005, n)
        drift = -0.005                       # −5 m-cnt/h
        mean = 400 - 0.9 * (T - 110) + 380 * (V - 0.9) + drift * h
        last = np.rint(mean + rng.normal(0, 1.0, n))
        d = tempfile.mkdtemp()
        path = os.path.join(d, "run_dut0_frames.csv")
        with open(path, "w", newline="") as f:
            f.write("# sintético\n")
            w = csv.writer(f)
            w.writerow(COLS)
            for i in range(n):
                w.writerow([f"{t[i]:.3f}", "", i + 1, 8000, f"{mean[i]:.4f}", int(last[i]), 0, 0, "",
                            0, f"{T[i]:.3f}", 0, f"{V[i]:.5f}", 0, 0, 67, 0, "stm", ""])
            w.writerow([f"{n}", "", n + 1, 0, "", 0, 0, 0, "", 0, "", 0, "", 0, 0, 67, 0, "stm", ""])
        for slack, tol in (("mean", 0.3), ("last", 2.0)):
            m = M.metrics(*M.load_dtm(path, slack))
            self.assertEqual(m["n"], n)                       # a janela vazia ficou de fora
            self.assertAlmostEqual(m["late"]["mcnt_h"], -5.0, delta=tol)
            self.assertAlmostEqual(m["coef_T_cnt_per_C"], -0.9, delta=0.02)
            self.assertAlmostEqual(m["coef_V_cnt_per_V"], 380, delta=25)
        self.assertGreater(M.metrics(*M.load_dtm(path, "mean"))["R2_pct"],
                           M.metrics(*M.load_dtm(path, "last"))["R2_pct"])   # média: menos ruído


if __name__ == "__main__":
    unittest.main()
