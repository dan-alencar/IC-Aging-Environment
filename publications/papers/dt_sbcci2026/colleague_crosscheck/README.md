# Independent cross-check by the colleague (branch `dt2027`, 2026-11-12)

The colleague assembled the SBCCI 2026 material on his own (branch `dt2027`, folder `D&T 2027/`)
and listed 9 points to check before the D&T version. They were found independently of
`../RECONCILIATION.md` and agree with it. Kept here as a cross-check; internal only, like the
reconciliation (the manuscript stays loyal to the SBCCI 2026 values and conventions).

| # | His point (`colleague_README_2026-11-12.md`, Portuguese) | Where it is handled here |
|---|---|---|
| 1 | Oven setpoint 83 °C in the PID log, not 80 °C; PSU at 1.45 V for VCCINT ≈ 1.297 V | RECONCILIATION item 13 |
| 2 | Statistics window: Table II uses the full run, Table III and ΔT = 9.37 °C use t ≥ 1 h | RECONCILIATION, ΔT and PID σ notes (post-soak vs full file; alignment decision) |
| 3 | Acceleration factor: Table I uses AF(mean T) (711 / 1182 h), the text defines ⟨AF⟩ (718 / 1184 h) | RECONCILIATION, equivalent-hours note; the submitted manuscript uses AF(mean T) × 23.08 h |
| 4 | PID gains: SIMC gives Kp 2.78, Ki ≈ 2.3e-3, Kd 0; the final Ki/Kd were tuned by hand | RECONCILIATION item 23; the manuscript calls the SIMC gains the starting point |
| 5 | The bang-bang run was sampled every 2 s, not 1 Hz | RECONCILIATION item 12 |
| 6 | "Same bitstream": the 2025 collector read 8-byte packets, the Nov 2025 design sends 9 | RECONCILIATION, step-size note ("step size depends on the bitstream") |
| 7 | Reference [10] of SBCCI 2026 has the wrong authors: it is Z. Li, Z. Huang, Q. Wang, J. Wang and N. Luo, *Sensors* 22(12):4439, 2022 | Not cited in the D&T manuscript. Corrected entry in `sbcci26_references_corrected.bib`, for an SBCCI erratum or any later citation |
| 8 | σ = 3.29 vs 0.40 °C (cited in the Information Theory work) is a 100 °C oven-air test from the TCC, not from the paper | Not used in the D&T manuscript |
| 9 | Jan/2026 bang-bang CSV headers say "PID parameters" (an old app limitation, fixed in `bff6174`) | Data-hygiene only; no effect on the numbers |

The rest of his folder (the SBCCI-era data, scripts and the Nexys4 project) is already in this
repository's history or under `data/campaigns/`; his AU15P bench material went to `main`.
