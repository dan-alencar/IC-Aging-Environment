"""Phase 0 inventory: scan every recovered campaign CSV and summarise it.

Reads data/campaigns/** (raw logs recovered from git history,
see data/campaigns/README.md), and
writes generated/inventory.csv. Descriptive only: no analysis choices here.

Two schemas exist:
  * "tcc9"   - '#' metadata header, then time_sec,oven_temp_c,...,dut_volt (1 Hz)
  * "legacy" - Data,Hora,Temperatura,Slack,Tensão with milli-units (0.5 Hz)
"""
from __future__ import annotations

import csv
import io
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
PAPER = HERE.parent
REPO = PAPER.parents[2]
SOURCES = [
    REPO / "data" / "campaigns",
]
OUT = PAPER / "generated" / "inventory.csv"


def read_log(path: Path):
    text = path.read_text(encoding="utf-8", errors="replace")
    meta = {}
    for line in text.splitlines():
        if not line.startswith("#"):
            continue
        for key, pat in {
            "start": r"In[ií]cio:\s*(.+)$",
            "end": r"Fim:\s*(.+)$",
            "kp": r"Kp\s*=\s*([\d.eE+-]+)",
            "ki": r"Ki\s*=\s*([\d.eE+-]+)",
            "kd": r"Kd\s*=\s*([\d.eE+-]+)",
            "controller": r"CONTROLADOR DO FORNO:\s*(.+)$",
            "dut_max": r"Temp\. M[aá]x\. DUT:\s*([\d.]+)",
        }.items():
            m = re.search(pat, line)
            if m and key not in meta:
                meta[key] = m.group(1).strip()
    body = "\n".join(l for l in text.splitlines() if l and not l.startswith("#"))
    if not body:
        return None, meta, "empty"
    head = body.splitlines()[0]
    if head.startswith("time_sec"):
        df = pd.read_csv(io.StringIO(body))
        return df, meta, "tcc9"
    if head.startswith("Data,Hora"):
        df = pd.read_csv(io.StringIO(body))
        df.columns = ["date", "hour", "temp_m", "slack", "volt_m"][: len(df.columns)]
        ts = pd.to_datetime(df["date"] + " " + df["hour"], dayfirst=True, errors="coerce")
        out = pd.DataFrame({
            "time_sec": (ts - ts.iloc[0]).dt.total_seconds(),
            "dut_temp_c": pd.to_numeric(df["temp_m"], errors="coerce") / 1000.0,
            "dut_slack": pd.to_numeric(df["slack"], errors="coerce"),
            "dut_volt": pd.to_numeric(df["volt_m"], errors="coerce") / 1000.0,
        })
        meta.setdefault("start", str(ts.iloc[0]))
        meta.setdefault("end", str(ts.iloc[-1]))
        return out, meta, "legacy"
    return None, meta, "other:" + head[:40]


def summarise(path: Path):
    df, meta, schema = read_log(path)
    row = {"file": str(path.relative_to(REPO)), "schema": schema, **meta}
    if df is None or "time_sec" not in df or len(df) < 2:
        row["rows"] = 0 if df is None else len(df)
        return row
    t = pd.to_numeric(df["time_sec"], errors="coerce").to_numpy()
    row["rows"] = len(df)
    row["dur_h"] = round((t[-1] - t[0]) / 3600, 3)
    row["cadence_s"] = round(float(np.median(np.diff(t))), 3)
    valid = (df.get("dut_slack", 0) != 0) & (df.get("dut_temp_c", 0) != 0)
    v = df[valid]
    row["rows_valid"] = int(valid.sum())
    for col, nd in [("oven_setpoint_c", 2), ("oven_temp_c", 2), ("psu_voltage_v", 3),
                    ("dut_temp_c", 2), ("dut_volt", 3), ("dut_slack", 1)]:
        if col in v and len(v):
            x = pd.to_numeric(v[col], errors="coerce")
            row[f"{col}_mean"] = round(float(x.mean()), nd)
            row[f"{col}_std"] = round(float(x.std(ddof=0)), nd + 1)
            if col in ("oven_setpoint_c", "dut_slack", "psu_voltage_v"):
                row[f"{col}_min"] = float(x.min())
                row[f"{col}_max"] = float(x.max())
    return row


def main(argv):
    files = sorted({p for s in SOURCES if s.exists() for p in s.rglob("*.csv")})
    rows = [summarise(p) for p in files]
    df = pd.DataFrame(rows)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)
    cols = ["file", "schema", "start", "rows", "dur_h", "cadence_s", "oven_setpoint_c_mean",
            "oven_temp_c_mean", "psu_voltage_v_mean", "dut_temp_c_mean", "dut_temp_c_std",
            "dut_volt_mean", "dut_slack_mean", "dut_slack_min", "dut_slack_max", "kp", "ki", "kd"]
    with pd.option_context("display.width", 250, "display.max_rows", 200, "display.max_colwidth", 70):
        print(df[[c for c in cols if c in df]].to_string(index=False))


if __name__ == "__main__":
    main(sys.argv)
