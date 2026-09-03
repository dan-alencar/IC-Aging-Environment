# analysis/ — Offline analysis

*[Leia em português](README.pt-BR.md)*

Empty for now. This is front F6's workspace (caracterização, dados e produção
científica — plan document Section 4.6): PVT variance decomposition of the slack
signal, σ_resid estimation with declared uncertainty, degradation-model fitting, and
the systematic Artix-7 vs. MAX10 comparison.

**Compatibility requirement (from the plan, and worth repeating here):** the CSV
format produced by `host/` must stay compatible with whatever pipeline already
processes `App_Nexys`/`App_2Nexys` output, so σ_resid numbers from both platforms are
computed the same way and are actually comparable. If a MAX10-specific analysis
notebook diverges from the existing pipeline's assumptions, document exactly where
and why in this directory, not just in the final report.

**Provenance requirement:** every number that ends up in a report or paper must be
traceable to the raw file in `../data/` that produced it, and to the version of the
analysis code that computed it. Keep notebooks/scripts version-controlled here, not
as one-off scratch files.
