#!/usr/bin/env python3
"""
Mostra o atraso da cadeia do sensor estimado pelo Timing Analyzer, para comparar
builds (relatorio C8: dispersao do atraso < passo/4 entre compilacoes).

  atraso_cadeia ~= T - slack_setup(clk[0])      (T = 200 ns)

Uso (em max10_port/hdl, depois de compilar):
    python scripts/sta_chain_delay.py
    python scripts/sta_chain_delay.py --csv builds.csv --label "ref"   # acrescenta uma linha ao CSV
"""
import argparse, csv, os, re, sys, datetime

T_NS = 200.0
STEP_PS = 96.154

ap = argparse.ArgumentParser()
ap.add_argument("--summary", default=os.path.join("output_files", "max10_aging_top.sta.summary"))
ap.add_argument("--csv")
ap.add_argument("--label", default="")
a = ap.parse_args()
if not os.path.isfile(a.summary):
    sys.exit(f"ERRO: {a.summary} nao encontrado (compile antes, e rode em max10_port/hdl).")

txt = open(a.summary, encoding="utf-8", errors="replace").read()
rows = {}
for m in re.finditer(r"Type\s*:\s*(\S.*?) Model Setup '(.*?)'\s*\nSlack\s*:\s*(-?[\d.]+)", txt):
    corner, clk, sl = m.group(1), m.group(2), float(m.group(3))
    if clk.endswith("clk[0]"):
        rows[corner] = sl
if not rows:
    sys.exit("ERRO: nao achei 'Setup ... clk[0]' no summary.")
print("Atraso da cadeia (T - slack de setup do clk[0]):")
out = {}
for corner, sl in rows.items():
    d = T_NS - sl
    out[corner] = d
    print(f"  {corner:<22} slack={sl:8.3f} ns   atraso ~ {d:7.3f} ns   (= {d*1000/STEP_PS:6.1f} passos)")
print("Criterio C8: entre builds, a variacao do atraso no corner lento 85C deve ficar < "
      f"{STEP_PS/4:.0f} ps (passo/4).")
if a.csv:
    new = not os.path.exists(a.csv)
    with open(a.csv, "a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["timestamp", "label"] + sorted(out))
        w.writerow([datetime.datetime.now().isoformat(timespec="seconds"), a.label] + [f"{out[k]:.3f}" for k in sorted(out)])
    print(f"linha acrescentada em {a.csv}")
