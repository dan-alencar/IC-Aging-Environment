# D&T 2027 analysis

`sbcci_metrics.py` computes the SBCCI 2026 metrics (Tables I–III) the same way for the
paper's two runs and for new App_DT_Monitor runs (fbs session folders). It needs numpy.
It is a port of the colleague's `metricas_sbcci.py` (branch `dt2027`, `12_analises/`) with
unchanged definitions; the docstring lists them.

    python3 analysis/dt2027/sbcci_metrics.py --sbcci
    python3 analysis/dt2027/sbcci_metrics.py --session <session folder> --board A --slack last
    python3 -m pytest analysis/dt2027                 # synthetic self-test + the paper's values

`--slack last` uses the last sweep of each 1 s window, the equivalent of SBCCI's single sweep
per second and the fair comparison with the paper. `--slack mean` uses the window mean of
~9000 sweeps; the difference measures what oversampling buys.

## Check against the paper

| | Bang-bang: script | Bang-bang: paper | PID: script | PID: paper |
|---|---|---|---|---|
| T_DUT mean / sd (°C) | 107.73 / 2.64 | 107.73 / 2.64 | 117.04 / 1.25 | 117.04 / 1.25 |
| sd(VDD) (mV) | 6.1 | 6.1 | 3.6 | 3.6 |
| ⟨AF⟩ | 31.1 | 31.1 | 51.3 | 51.3 |
| Equivalent hours, AF(⟨T⟩) | 710 | 711 | 1182 | 1182 |
| R² slack ~ T, V, t ≥ 1 h (%) | 92.11 | 92.1 | 59.23 | 59.2 |
| Residual sd (count) | 0.904 | 0.904 | 0.726 | 0.726 |
| Late slope (m-count/h) | −8.4 ± 4.9 | −6.5 | −5.35 ± 2.33 | −5.3 |

The late slope is defined as the coefficient of t in slack ~ 1 + t + T + V from 12 h on, with
the Newey–West standard error. The paper does not say how it was computed. With this
definition PID matches and bang-bang does not; that discrepancy is an open item for the
paper, not for these tools. The estimate depends strongly on where the window starts
(bang-bang −8.4 to −11.9, PID −2.8 to −9.3 m-count/h for starts between 10 and 14 h), so fix
the window before looking at new data; the report prints the sensitivity.
