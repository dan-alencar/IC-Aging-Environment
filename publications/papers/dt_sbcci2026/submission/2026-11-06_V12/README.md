# IEEE D&T submission package (SI: SBCCI 2026)

"Burn-In Thermal Control Sets What Aging Sensors Can See", by D. Alencar et al.

| Path | Contents |
|---|---|
| `Alencar_DT_SBCCI2026.pdf` | Manuscript |
| `latex/` | Standalone LaTeX source: `main.tex`, `values.tex` (every number printed, generated) and `figures/*.pdf`. Build with `latexmk -pdf main.tex` (TeX Live 2020 or later; no extra packages). |
| `figures/` | Figures for production, in three formats: `.eps` (vector, fonts embedded as Type 3), `.tif` (600 dpi, RGB, LZW-compressed lossless, 7 × 2.35 in = 4200 × 1410 px) and `.pdf` (vector). `fig_stress` = Figure 1, `fig_detect` = Figure 2. |
| `sources/analysis/` | Python scripts that produce every number and figure from the raw logs (`run_analysis.py`, `pid_bench.py`, `derive.py`, `make_figures.py`, `dtlib.py`), plus the word-count and number-audit checks. |
| `sources/Makefile`, `sources/README.md` | One-command rebuild (`make`) from the repository. |
| `sources/SHA256SUMS`, `sources/DATA_README.md` | Checksums and map of the raw campaign logs in the repository's `data/campaigns/`. |

To regenerate everything, run `make` in `publications/papers/dt_sbcci2026/` of the IC-Aging-Environment repository, then `make package`.

Budget at packaging time: see `make check` (≤ 5,000 words including 200 per figure/table; ≤ 12 references; title ≤ 9 words).
