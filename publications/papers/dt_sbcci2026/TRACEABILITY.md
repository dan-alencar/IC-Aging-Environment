# Traceability matrix (internal review aid, GUIDELINE_ESCRITA_CIENTIFICA §9)

Not part of the submission. It maps every commitment the opening makes to where the article develops it, the evidence, the interpretation, and the answer in the closing.

| Commitment (opening) | Method / where developed | Evidence | Interpretation | Answer in closing |
|---|---|---|---|---|
| Research question: how long must a burn-in run before a sensor sees aging, and how much does the bench change that time? | Instrument, benches, and methods → Analysis methods (Eq. 1, long-run variance, sequential test) | Detectability section; Table 2; Figure 2(a) | Detection time is a range (16–89 h, PID), set by noise model and aging law | **Met:** measured answer for PID, projected answer for thermostat (stated as projected) |
| C1: source decomposition of the stress bias + tracking budget | Eq. 2 (⟨AF⟩), Eq. 3 (δ) | Delivered stress section; Figure 1(a)–(b) | Mean shortfall dominates; ripple ≈ Jensen prediction | **Met:** "dominant error was the mean die temperature" |
| C2: 214.6 h sustained-stress campaign on a second circuit | Evidence base; Table 1 | Detectability: drift, power-law fit, ΔBIC on block means | Sublinear drift, BTI-consistent; called *drift*, not aging (no readout control; setpoint moves) | **Met, with stated scope** |
| C3: detection time three ways | Analysis methods | Table 2; Figure 2(a) | The three differ for identified reasons; none is wrong | **Met** |
| C4: measured bench penalty on detectability | Analysis methods; paired-run noise (Reversible noise) | Bench penalty paragraph; Table 2 (thermostatic column) | Noise measured; aging law bracketed; cross-circuit transfer stated as untestable | **Partly met** (projection); the first future-work item would close it |
| C5: reproducible commodity PID bench | Two benches; Is the PID a fair baseline? | FOPDT/SIMC/final gains; 100 °C comparison (thermostat vs PID, SIMC vs tuned) | Tuning matters; thermostat is the unmodified chamber | **Met** |
| C6: five-item reporting checklist | What labs should report | Table 3 | Two most-missing items change conclusions most | **Met:** closing ties the checklist to the T_min method |
| Gap: bench effect on *sensor validation* (vs industrial junction control [6, 7]) | Opening ¶2 | Whole article | Positioned against [6, 7, 8] | Closing: "the bench belongs in the measurement chain" |

## Guideline checklist (§9.1), status

- [x] Venue instructions consulted and take precedence (CEDA author page; D&T example articles).
- [x] Points not defined by the venue follow the personal guideline: contributions enumerated, explicit research question, findings preview and roadmap, concepts before use (Analysis methods), objectives answered in the closing, concrete future work.
- [ ] Numbered sections: **not applied.** It conflicts with the D&T house pattern (unnumbered sentence-case headings in all three examples).
- [x] Problem, gap, objective and contributions aligned (matrix above).
- [x] Each section has a function and prepares the next: methods → stress → noise → detectability → reporting → limitations → closing.
- [x] Figures and tables cited and interpreted in the text.
- [x] Observation, interpretation, hypothesis and projection distinguished ("drift, not aging"; "projected"; "descriptive time rather than a stopping rule").
- [x] Limitations stated without self-deprecation.
- [x] Closing answers the question and says what is met and what is projected; future work follows from the remaining gaps.
- [x] Abstract reflects the final version.
