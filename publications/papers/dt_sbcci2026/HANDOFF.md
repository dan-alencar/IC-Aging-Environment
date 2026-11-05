# Handoff: IEEE D&T Special Issue paper (SBCCI 2026 extension), contingency version

## Who I am and what this is

I'm Danilo Alencar (UFC / LESC). Our SBCCI 2026 paper ("Quantifying the Effect of Burn-In Thermal Control on Delivered Acceleration Factor and On-Chip Slack-Sensor Fidelity in an FPGA Target") was invited to the IEEE Design & Test Special Issue. The manuscript is due **23 November 2026** (submission type "SI: SBCCI 2026"). I plan to submit on 22 November.

A previous session produced a **contingency draft**. It uses only the existing Artix-7 data and none of the in-progress Artix UltraScale+ runs. Its LaTeX source, figure scripts and calculation script are in `DT_contingency_source.zip` (I'll put it at `<PATH_TO_DRAFT>`; ask me if you can't find it). That draft derived several numbers from *reported summary values* in the source documents because the raw data wasn't available. **This repository has the raw artifacts.** Your job is to replace every derived or projected number you can with numbers computed from the raw logs, reconcile the inconsistencies between documents, and improve the paper.

## Ground rules (non-negotiable)

1. **Never invent or estimate a number.** Every scalar in the paper must come from a script in the repo, written to one generated file (e.g. `dt/generated/values.tex` as `\newcommand` macros) and used in the LaTeX through those macros. No hand-typed results.
2. **Report discrepancies; don't silently pick a side.** When two sources disagree, write it in `dt/RECONCILIATION.md` with both values, the cause you found, and the value you chose and why. Ask me if the cause isn't determinable.
3. **The JICS draft is unpublished and stays a draft. Do not cite it.** The 212.6 h campaign and failure-catcher material are presented as our own data. The failure catcher is citable through SBCCI 2025. Don't reproduce JICS figures or tables verbatim.
4. **My undergraduate thesis (TCC) cannot be cited** (not an academic publication for this purpose). Its PID construction and the 100 °C comparisons are presented as methods and results of this paper.
5. **D&T limits:** ≤ 5,000 words *including* references and bios, each figure/table counting as 200 words; ≤ 12 references; title ≤ 9 words; abstract ~100 words; keywords and author bios required. Keep a script that computes the count and print it at the end.
6. **Single-device honesty.** No population claims, no lifetime extrapolation, and JEDEC/MIL statements stay interpretive (no compliance claims).
7. Don't commit or push unless I ask. Work on a branch.

## Repository artifacts to locate (Phase 0: inventory first, analyze second)

Find and list, with paths, for each campaign: the raw CSV(s), the bitstream/RTL version, the monitored circuit (CUT), the board/device identity, the commanded setpoints, and the start/end timestamps. Expected campaigns:

| Campaign | Expected content |
|---|---|
| SBCCI 2026 bang-bang run | 23.08 h, 80 °C oven air, 1.3 V, 115 °C die target, stock thermostat + V-compensation loop |
| SBCCI 2026 PID run | 23.08 h, same commands, PID oven |
| 212.6 h PID campaign | ~94 °C oven air, 1.400 V on-die, ~125 °C die; the TIP7266 file was `Tentative_1_20260524_203756.csv` (772,484 raw rows, 768,884 post-soak) |
| 100 °C bang-bang vs PID | ~1 h each, oven air only (thesis Table 6) |
| 100 °C SIMC vs fine-tuned PID | thesis Table 5 |
| FOPDT step test | 50% open-loop step from 25.21 °C |
| JICS week-0/1/2 corner sweeps and failure-catcher test | context only |
| SBCCI 2025 sensor runs | context only |

CSV schema should be: `time, oven_temp_c, oven_setpoint_c, oven_output_pct, psu_voltage_v, psu_current_a, dut_temp_c, dut_slack, dut_volt`, at 1 Hz, slack in integer MMCM phase counts (19.85 ps/count).

**Deliver the inventory table to me before running analyses.** Explicitly answer:
- (a) Were all sensor campaigns on the **same physical device**?
- (b) Which **CUT** did each use: the 50-inverter chain (SBCCI) or the 16-bit RCA (JICS)? If they differ, the paper's "same device and sensor" wording and the cross-run ratio transfer must change.
- (c) Is the 212.6 h run the JICS "Week 2" burn-in run (after a Week 1 at 115 °C / +30% VDD)?

## Phase 1: reconcile known inconsistencies

Resolve each from the raw data and record it in `RECONCILIATION.md`:

1. **ΔT:** 9.31 °C (= 117.04 − 107.73 in SBCCI Table II) vs 9.37 °C (SBCCI abstract and text). The current draft uses 9.31.
2. **Equivalent hours:** 711/1182 h (SBCCI, apparently AF(mean T) × 23.08 h) vs 718/1184 h (⟨AF⟩ × 23.08 h). Confirm which definition each used; the draft uses ⟨AF⟩.
3. **Long-run duration:** 212.6 h (JICS, brief) vs 214.6 h (TIP7266). Use 772,484 rows at 1 Hz minus 1 h soak, and state the definition.
4. **Slack units:** JICS says "278.5 ± 3.0 ps within a 33 ps band"; TIP7266 says 278.5 / 3.03 *counts*, 27 levels over 267–300 counts. Determine the truth from the CSV and the RTL. This also affects the "≈3.9 cnt ≈ 77 ps total drift" sentence.
5. **σ(T_DUT) under PID:** 1.25 °C / mean 117.04 °C (SBCCI) vs 0.91 °C / 117.2 °C (thesis Table 7, "24 h"). Are these the same runs with different windows or filters? Also the thesis's bang-bang 2.63 °C / 108.2 °C vs SBCCI's 2.64 / 107.73.
6. **TIP7266** labels σ = 0.40 vs 3.29 °C as the SBCCI result; those are actually thesis oven-air numbers at 100 °C. Make sure the paper doesn't repeat that.
7. **JICS "PID control band 89.5–103.6 °C"** is the oven-air range during the 212.6 h run, with die 125.1 ± 1.8 °C (range 117–134). Check for setpoint changes or a disturbance (there's a visible step near ~50 h in JICS Fig. 11A) and decide whether a sub-window should be excluded.
8. **Residual-σ ratio:** 0.904/0.726 = 1.245 ("25%") vs SBCCI's "~23%". Recompute.
9. **Reference [7] in SBCCI 2026 and the draft is mis-attributed.** "On the Effect of Aging on Digital Sensors" is by M. T. H. Anik, S. Guilley, J.-L. Danger, N. Karimi, *Proc. VLSID 2020*, pp. 189–194. Its finding is that the sensor's *own aging* shifts calibration (missed and false alarms), not uncorrected PVT. Fix the citation and the sentence that uses it.

## Phase 2: one reproducible analysis pipeline

Build `dt/analysis/` (Python; numpy/scipy/pandas/matplotlib). Run it on every relevant campaign with **identical** code paths and the same 1 h soak exclusion. For each sensor campaign compute:

**Delivered stress**
- Exact ⟨AF⟩ = mean over samples of AF(T_j(t)) for E_a ∈ {0.5, 0.6, 0.7, 0.8, 0.9} eV, T_use = 55 °C.
- AF(mean T_j), and the ripple contribution (⟨AF⟩/AF(T̄) − 1). The draft used a Gaussian approximation from summary stats (+1.0% bang-bang, +0.2% PID). Replace it with the exact trajectory value.
- Equivalent hours, mean die error vs target, and σ(V_DD).

**Reversible noise**
- R² for T, V, and T+V; residual σ after joint linear regression; Newey–West windowed slopes (reproduce SBCCI's 1–6, 6–12, 12–22.5 h windows).
- **Mutual information per regime.** For each campaign, reuse TIP7266's estimators: Miller–Madow with T, V in 16 equiprobable bins, plus a KSG cross-check; circular-shift surrogate null (mean and p95); moving-block bootstrap 95% CI; and a bin-count sensitivity check (12/16/24/32). Report:
  1. raw I(S;T,V);
  2. detrended I(S;T,V);
  3. **residual MI after linear PVT correction (detrended)**, the key bench-quality number;
  4. normalized I/H(S).

  Hypothesis to test, not assume: bang-bang leaves more residual MI than PID (e.g., from XADC-to-path thermal lag making slack-vs-T hysteretic). Check for hysteresis directly by plotting slack residual vs T split by heating/cooling phase in the bang-bang run.

**Detectability**
- Integrated autocorrelation time τ_int of the corrected residual (Sokal automatic windowing; state the method), n_eff = n/(2τ_int).
- OLS slope with Newey–West CI, Bayesian slope on decimated samples (Jeffreys prior, Student-t posterior), CRLB σ_β = sqrt(24 σ² τ_int / T³), and T_min = (216 σ² τ_int / β²)^(1/3).
- Reproduce on the 212.6 h run: σ = 0.84 cnt, τ_int = 314 s, n_eff ≈ 1,224, β = −18.3 m-cnt/h, T_min ≈ 34 h, 3σ floor 1.2 m-cnt/h. Flag any mismatch.
- **For the 23 h bang-bang and PID runs, measure σ and τ_int directly.** This replaces the draft's assumption that bang-bang has the same τ_int as PID. The projected bang-bang T_min (draft: ≈55 h, 1.62×) should then use measured σ_BB/σ_PID and τ_BB/τ_PID. The only remaining assumption is β ∝ ⟨AF⟩; state it explicitly.
- BSC alarm capacity vs window w, using the model p = Q(SNR_w/2) with SNR_w = β·w / (σ·sqrt(2τ_int/w)) and C = 1 − H₂(p). The draft got C(24 h) = 0.99 for PID and 0.64 for projected bang-bang. Recompute with measured parameters.

**Measurement-chain sanity**
- Is there any channel in the logs that can serve as a control (a reference path, MMCM lock/status, XADC drift of a stable rail, supply current trend)? Use it to argue the −18.3 m-cnt/h drift is not readout drift, or tell me plainly that no control exists.
- Check BTI-consistent sign and shape (sublinear, power-law fit vs linear) on the 212.6 h residual. Report it, but don't over-claim from one device.

**PID construction (from thesis artifacts)**
- Re-derive the FOPDT fit (K = 1.56 °C/%, θ = 150.6 s, τ = 1307.2 s), SIMC gains and final gains (Kp 2.78, Ki 1.06e-3 /s, Kd 5.0 s).
- Recompute the 100 °C comparisons (σ 3.29 vs 0.40 °C, peak-to-peak 9.0 vs 2.1, |e|max 7.2 vs 1.8; SIMC vs tuned σ 1.33 vs 0.40, overshoot 5.2 vs 0.0) from raw logs.
- Consider one compact step-response figure if the word budget allows.

All figures are generated by scripts from these results. Keep the existing visual style (two-series palette #1F5FBF PID / #D9661F bang-bang, with line style as secondary encoding, serif fonts, no dual axes).

## Phase 3: revise the manuscript

Start from the contingency draft (`main.tex`, figures, `figs.py`, `calc.py`) and keep its structure: Introduction with six enumerated contributions, Instrument/Benches/Evidence, Delivered Stress, Reversible Noise, Detectability, What Labs Should Report (5-item checklist), Limitations, Conclusion. Changes:

1. Switch every number to generated macros. Replace "projected" bang-bang detectability with the measured-parameter version, and update contribution 4's wording to match what is now measured vs assumed.
2. Expand Reversible Noise into the **per-regime MI** comparison (table or small figure), while staying in the word budget. Cut MI to one sentence if the per-regime results are inconclusive.
3. **Reposition the novelty against the industrial burn-in literature.** Self-heating makes junction temperature differ from chamber temperature, which is known and handled industrially with per-device thermal control. The novelty is what this does to *on-chip sensor validation*: delivered stress, residual noise and detection time. Add:
   - A. Vassighi, O. Semenov, M. Sachdev, A. Keshavarzi, C. Hawkins, "CMOS IC technology scaling and its impact on burn-in," *IEEE Trans. Device Mater. Reliab.*, 4(2):208–221, 2004, doi:10.1109/TDMR.2004.826591
   - O. Semenov, A. Vassighi, M. Sachdev, A. Keshavarzi, C. F. Hawkins, "Effect of CMOS technology scaling on thermal management during burn-in," *IEEE Trans. Semicond. Manuf.*, 16(4):686–695, 2003, doi:10.1109/TSM.2003.818985

   To stay at 12 references, propose which to drop (candidates: Lanzieri 2024 survey, Agarwal VTS 2007) and confirm with me.
4. Fix ref [7] (see Phase 1, item 9) and reword its sentence.
5. Fill missing DOIs and pages for Kashyap (IRPS 2021), Niemann (*Integration* 75, 2020) and Agarwal (VTS 2007) if they stay. Verified: Valdés-Peña doi:10.1109/TNANO.2013.2253795; Lanzieri doi:10.1145/3695247; Sobas *MR* 138, doi:10.1016/j.microrel.2022.114698; Skogestad *JPC* 13(4):291–309, 2003. For the 16 nm drift sentence in Limitations, Sobas & Marc, *Micromachines* 15(1):19, 2023, doi:10.3390/mi15010019 is the better source if a slot frees up.
6. Add a footnote noting the corrected SBCCI values (ΔT, equivalent hours, residual-floor percentage), so reviewers comparing papers see the correction is deliberate.
7. Update the "same device / same sensor" wording according to Phase 0 answers (a)–(c).
8. Leave a clearly marked, commented-out slot for a future "16 nm FinFET transfer" section (Artix US+ runs; go/no-go decision on 15 Nov). The contingency paper must compile and read complete without it.
9. Bios: mine is drafted. Leave others as they are and list them for me to complete; don't invent degrees or titles.

## Phase 4: verification

- Rebuild the PDF; view every page and check for float placement, overlaps and overfull boxes.
- Run the word-count script (body + references + bios + 200 per figure/table) and the reference count.
- **Number audit:** every number in the `.tex` either comes from `values.tex` or is a commanded/spec value listed in a whitelist file. Print any orphan numbers.
- Spawn an independent reviewer agent that hasn't seen your work. Give it the PDF, the SBCCI 2026 paper and `RECONCILIATION.md`, and have it review as a D&T reviewer from the industrial test/reliability community: novelty vs prior art, unsupported claims, consistency with SBCCI, and any number it can't trace. Address what it finds.

## Deliverables

- `dt/main.pdf` and full LaTeX source, with figures generated from scripts
- `dt/analysis/` pipeline plus a one-command `make` (or script) that regenerates everything from raw CSVs
- `dt/generated/values.tex`
- `dt/RECONCILIATION.md`
- `dt/INVENTORY.md` (Phase 0 table)
- a short summary for me: what changed, which claims got stronger or weaker with real data, open questions, and the final word and reference counts

## Baseline numbers from the current draft (to verify, not trust)

- 23.08 h pair:
  - mean T_DUT 107.73 (BB) / 117.04 °C (PID); σ 2.64 / 1.25 °C; mean die error −7.27 / +2.04 °C
  - ⟨AF⟩ 31.1 / 51.3 at 0.7 eV (ratio 1.65, range 1.43–1.90 over 0.5–0.9 eV)
  - σ(V_DD) 6.1 / 3.6 mV
  - R²(T,V) 92.11% / 59.23%; residual σ 0.904 / 0.726 cnt
  - late-window slopes −6.5 [−11.8, −1.2] / −5.3 [−7.7, −2.8] m-cnt/h
- δ budget at 115 °C, 0.7 eV: 0.91 / 1.77 / 3.38 °C for ±5 / ±10 / ±20%
- 212.6 h PID run:
  - 93.9 ± 1.8 °C air, 125.1 ± 1.8 °C die, 1.400 V
  - H(S) 3.43 bits; I(S;T,V) 1.132 bits [1.091, 1.176], KSG 1.221; null p95 0.097; R² 0.738
  - detrended MI 0.656 → 0.046 bits after linear correction (93% removed); residual σ 0.84 cnt
  - corr(S,t) −0.35 → −0.73
  - β −18.3 m-cnt/h (Bayesian −18.2 [−19.2, −17.2]); τ_int 314 s; n_eff 1,224; CRLB 0.39 m-cnt/h; T_min 34 h [33, 36]
- Projection (to be replaced): bang-bang T_min ≈ 55 h (1.62×; 50–61 h over E_a); C_BSC(24 h) 0.99 PID vs 0.64 bang-bang

## Before you start

Ask me only what you can't determine from the repository. Otherwise begin with Phase 0, show me the inventory, then proceed.
