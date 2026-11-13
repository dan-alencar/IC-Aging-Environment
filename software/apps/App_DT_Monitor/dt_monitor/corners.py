"""corners: slack of each board at a few VCCINT values, oven off (port of medir_corners.py).

    dt-monitor corners BENCH                         # 0.85, 0.90, 0.95, 0.85 V
    dt-monitor corners BENCH --volts 0.85 0.90 --measure-min 5 --boards A

Runs through fbs-service (BENCH = bench name or socket): it builds a run plan with one
corners step (the service's VCCINT loop holds SYSMON VCCINT on each target), waits for the
die to settle, measures, and returns every board to --back (0.85 V) at the end, also on
Ctrl+C or an error. The session folder holds the raw records; the summary goes to
corners_summary.csv in it: one row per board and voltage with the slack mean/std of every
chain over the measurement minutes.
"""
from __future__ import annotations

import argparse
import csv
import statistics as st
import sys
import time
from pathlib import Path
from typing import Dict, List

import yaml

from fpgaging_bsp.service.client import ServiceClient, ServiceError

CHAIN_COLS = ["slack_mean"] + [f"c{j}_slack_mean" for j in range(1, 9)]


def plan(boards: List[str], volts: List[float], settle_min: float, measure_min: float) -> str:
    return yaml.safe_dump({
        "name": "corners", "experiment": "ic_aging.burnin", "boards": boards,
        "pre": [{"corners": {"vccint_v": volts, "settle_min": settle_min, "measure_min": measure_min,
                             "oven": "off"}}],
        "stop_on": ["latched", "die_implausible", {"board_silent_s": 30}],
        "notify": ["alarm"]}, sort_keys=False)


def summarise(session: Path, boards: List[str]) -> List[Dict[str, object]]:
    """Per board and voltage: mean and std of each chain's window means while measuring."""
    with open(session / "summary.csv") as f:
        rows = list(csv.DictReader(line for line in f if not line.startswith("#")))
    out = []
    for b in boards:
        groups: Dict[str, List[dict]] = {}
        for r in rows:
            if r["phase"].startswith("corner_measure:"):
                groups.setdefault(r["phase"].split(":")[1], []).append(r)
        for v, rs in groups.items():
            rec: Dict[str, object] = {"board": b, "vccint_target_v": float(v), "seconds": len(rs)}
            for key, col in (("die_temp_c", f"{b}_die_temp_c"), ("sysmon_vccint_v", f"{b}_sysmon_vccint_v"),
                             ("iout_a", f"{b}_iout_a")):
                xs = [float(r[col]) for r in rs if r.get(col)]
                rec[key] = round(st.mean(xs), 4) if xs else ""
            for c in CHAIN_COLS:
                xs = [float(r[f"{b}_{c}"]) for r in rs if r.get(f"{b}_{c}")]
                name = "c0" if c == "slack_mean" else c.split("_")[0]
                rec[f"{name}_mean"] = round(st.mean(xs), 3) if xs else ""
                rec[f"{name}_std"] = round(st.pstdev(xs), 3) if len(xs) > 1 else ""
            out.append(rec)
    return out


def run(bench: str, boards: List[str], volts: List[float], settle_min: float, measure_min: float,
        back_v: float = 0.85, poll_s: float = 1.0) -> Path:
    c = ServiceClient.connect(bench)
    try:
        c.call("lease")
        st0 = c.call("status")
        boards = boards or [b["name"] for b in st0["boards"]]
        info = c.call("start_run", plan=plan(boards, volts, settle_min, measure_min), confirm_compat=True)
        session = Path(info["session"])
        try:
            while c.call("status")["run"]["state"] != "idle":
                time.sleep(poll_s)
        except KeyboardInterrupt:
            c.call("stop_run", reason="corners interrupted")
            while c.call("status")["run"]["state"] != "idle":
                time.sleep(poll_s)
        finally:
            for b in boards:
                try:
                    c.call("set_vccint", board=b, mv=int(round(back_v * 1000)))
                except ServiceError:
                    pass
        rows = summarise(session, boards)
        if rows:
            with open(session / "corners_summary.csv", "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=list(rows[0]))
                w.writeheader()
                w.writerows(rows)
        return session
    finally:
        c.close()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="dt-monitor corners", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("bench", help="bench name or service socket")
    ap.add_argument("--volts", type=float, nargs="+", default=[0.85, 0.90, 0.95, 0.85])
    ap.add_argument("--settle-min", type=float, default=2.0)
    ap.add_argument("--measure-min", type=float, default=3.0)
    ap.add_argument("--boards", nargs="+", default=[])
    ap.add_argument("--back", type=float, default=0.85, help="VCCINT at the end (V)")
    a = ap.parse_args(argv)
    try:
        d = run(a.bench, a.boards, a.volts, a.settle_min, a.measure_min, a.back)
    except ServiceError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    print(f"session: {d}")
    if (d / "corners_summary.csv").exists():
        print((d / "corners_summary.csv").read_text())
    return 0


if __name__ == "__main__":
    sys.exit(main())
