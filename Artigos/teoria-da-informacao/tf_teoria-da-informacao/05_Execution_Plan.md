# Execution Plan

A prioritized, deadline-aware plan that turns the methodology into the final TF (Trabalho Final) artifact: a written article (formato científico) plus a 15-minute seminar.

> **Hard dates (from the súmula):** TF presentations on **26/06** and **03/07/2026**. The evaluation rubric weights writing/clarity heavily (apresentação escrita 2.0; objetivos/problema 1.0; metodologia 2.0; clareza de argumentos 2.0; respostas 1.5). **A complete, clearly-argued subset beats a sprawling, half-run superset.** Plan accordingly.

---

## 1. Priority tiers

Scope is **deliberately selective** — only course tools that strongly correlate with the aging-sensor problem and contribute a result the prior work could not state. Items that would only be exercised superficially (Huffman/LZW source-coding codecs, Big Data/streaming tooling) are **out of scope** by decision, not omission.

> **Status (Tier 1 + KL complete):** items 1–6 and the KL comparison are implemented and data-backed in `analysis/tier1_pipeline.py` and `analysis/kl_benches.py`; all scalars flow into `latex/generated/values.tex`. Remaining: ICA (Tier 2) and optional polish.

### Tier 1 — Core spine ✓ done
These reuse the existing logs and the taught estimators; each yields a headline number.

1. ✓ **Data prep + descriptive stats** — loader, drop dropouts, drop first 1 h, autocorrelation time $\tau_{int}$, $n_{eff}=1{,}224$. *Topics: pré-processamento, momentos.*
2. ✓ **Entropy & MI core** — $H(S)=3.43$, $H(S\mid T,V)=2.30$, $I(S;T)$, $I(S;V)$, $I(S;T,V)=1.13$ bits (binned+MM **and** KSG $1.22$ — own CIs, overlapping only narrowly, a characterized estimator gap rather than agreement). *Topics: entropia, condicional, informação mútua.* **← the centerpiece.**
3. ✓ **MI-vs-$R^2$ result** — measured MI exceeds the Gaussian-equivalent of the linear $R^2=0.738$ ($0.97$ bits) by **17–26 %** on the raw series (real, survives the estimator's bias floor); **does not survive detrending** (deficit of −19% to −11% on the reversible series) — real evidence for MI's structural advantage over $R^2$, not confirmed evidence of instantaneous non-linear PVT physics. *Still the single most important result, now reported with its own honest limits.*
4. ✓ **PVT correction (linear OLS vs non-linear)** — reversible MI $0.656\to0.046$ bits (**93 % removed**); MDL selects linear; aging recovery $\mathrm{corr}(S,t)\,{-}0.35\to{-}0.73$. *Topics: mínimos quadrados, MLE, MDL.*
5. ✓ **Capacity + BSC alarm** — $1.8$ resolvable aging states; $C_{BSC}=0.99$ bits at a 24 h window. *Topics: capacidade, BSC, ruído.*
6. ✓ **RUL detectability bound** — Cramér–Rao ⇒ min detectable rate $1.2$ m-cnt/h, min observation time $34$ h. *Topics: estimação.*

### KL comparison ✓ done (uses the two SBCCI-vs-PID bench logs)
7. ✓ **KL / Jensen–Shannon divergence** between the SBCCI and PID benches — KL(SBCCI‖PID)=1.94, KL(PID‖SBCCI)=1.01 (asymmetric), JS=0.279 bits. *Topic: divergência KLD.*

### Tier 2
8. ✓ **ICA / negentropy blind separation** — model-free; recovers the aging component at |corr|=0.834 with $S_{corr}$; separation partial (residual inter-IC MI 0.57 bits). *Topic: ICA / negentropia / separação cega.*
9. ✓ **Surrogate/null tests** (circular-shift surrogates) — null MI floor p95 = 0.097 bits; measured I(S;T,V) is **12× the floor** ⇒ real, not bias.
10. ✓ **Bayesian RUL error bars** — Student-$t$ posterior on the aging slope (thinned to $n_{eff}$): $-18.2$ m-cnt/h, 95% CrI $[-19.2,-17.2]$; P(slope < 0) ≈ 100% (reading as aging is conditioned on the single-device identification assumption, not re-derived here); min-obs-time CrI $[33,36]$ h.

### Extension (2026-08, ahead of the 22/08 submission) ✓ done
11. ✓ **Wiener-process degradation + Kalman/RTS smoothing + Inverse-Gaussian RUL distribution** (`analysis/kalman_rul.py`) — block-averages the corrected residual to $n_{eff}$ quasi-independent points, fits the Wiener diffusion and observation noise by method of moments and the rate-noise hyperparameter by 1-D MLE on the filter's innovation likelihood, then RTS-smooths to a denoised aging trajectory with credible bands. Turns the single-point CRLB/Bayesian RUL bound (item 10) into a full closed-form RUL *distribution*, reported at two Tier-1-anchored thresholds since no calibrated failure threshold exists. Cross-validates against item 10 (consistent rate) and against the MDL verdict (item 4: the rate-noise MLE independently also collapses to a constant-drift model). *Topics: estimação sequencial/Bayesiana (Kalman), processos estocásticos — an explicit deepening beyond the core syllabus, built on the estimation theory already taught; see `03_Course_Topic_Mapping.md` D.1b.*

**Out of scope (by decision):** Huffman/LZW source-coding codecs; Big Data / streaming implementation. Both would only superficially touch the research problem; the source-coding *concept* is acknowledged in prose (the source-coding theorem lower-bounds any code by $H(S)$) without a redundant codec run.

## 2. Status and remaining sequencing

| Block | Work | Status |
|---|---|---|
| A | MI spine (items 1–3) | ✓ done, in paper |
| B | correction, capacity/BSC, RUL (items 4–6) | ✓ done, in paper |
| C | KL bench comparison (item 7) | ✓ done, in paper |
| D | ICA blind separation (item 8) | ✓ done, in paper |
| E | optional polish (items 9–10) + writing pass | ✓ done |
| F | Wiener/Kalman RUL-distribution extension (item 11) + writing pass | ✓ done, in paper (`sec:res-wiener`) |

Write each section of the LaTeX document *as its result is produced* — the rubric rewards the writing, and every result already has a home in the `.tex` tree (see `latex/`).

## 3. Pipeline contract (keeps analysis and paper in sync)

Each analysis script emits a machine-readable artifact the LaTeX picks up, so re-running data never means re-typing numbers:

- numbers → `latex/tables/*.tex` (or a single `\input`-able macros file, `latex/generated/values.tex`, with `\newcommand` per scalar);
- plots → `latex/figures/*.pdf`.

This is the "reusable analysis layer" deliverable and prevents transcription errors in a rushed week.

## 4. Definition of done (per the rubric)

- [x] Problem, objectives, and report structure stated up front (rubric item 02).
- [x] Methodology explicitly tied to course topics (rubric item 03 — `03_Course_Topic_Mapping.md` is the evidence).
- [x] Every reported number traceable to a script + the dataset (no orphan figures). *(Fixed 2026-08-13: `\valHs`, `\valRsqLinear`, `\valCorrST/SV/St`, `\valSlopeRaw`, and the dataset descriptive stats were hand-typed in `values.tex` and never regenerated; `tier1_pipeline.py` now computes all of them, including R² from the same OLS fit used for the PVT correction instead of a hardcoded `0.738` literal.)*
- [x] Honesty caveats present (single device/regime, $n_{eff}$, ICA exploratory).
- [x] 15-min seminar deck: one slide per Tier-1 result + one "what info theory added over $R^2$" punchline slide, plus the Wiener/Kalman RUL-distribution slide and a backup slide defending the bang-bang-vs-PID capacity scope decision. *(2026-08-18: deck updated to match the pipeline's corrected excess-pct/CI reporting and the detrended-MI honesty finding; see `06_Contribution_vs_Prior_Work.md` and `review/prompt_correcoes_TF.md`.)*

## 5. Risk register

| Risk | Mitigation |
|---|---|
| MI estimator bias on autocorrelated data invalidates headline number | report on $n_{eff}$, cross-estimator comparison (with each estimator's own CI), surrogate floor — all Tier-1/2 |
| ICA fails to separate sources | it is Tier-3 and framed as exploratory; the regression correction (Tier-1) is the fallback |
| Time runs out | Tier-1 alone is a complete, defensible paper; Tiers 2–3 are clearly optional |
| Single-regime data weakens cross-regime claims | lean on published bang-bang/PID statistics; frame new run as the long-duration anchor |
