# Data Analysis & Modeling

This directory contains post-processing scripts, Jupyter notebooks, and mathematical models to extract aging parameters from raw experimental logs.

## Directory Structure

```
analysis/
├── notebooks/             # Interactive Jupyter notebooks for data visualization
├── scripts/               # Batch analysis scripts (Arrhenius fitting, BTI/HCI extraction)
├── figures/               # Output publication figures generated from scripts
└── teoria_da_informacao/  # Information theory metrics (entropy, mutual information) on aging data
```

## Typical Analysis Pipeline

1. **Load data:** Read CSV logs from `data/campaigns/` or `data/sample_logs/`.
2. **Filter & Smooth:** Remove thermal ramp transients; compute rolling averages.
3. **Model Fitting:**
   - Fit FOPDT parameters for oven control.
   - Fit Arrhenius acceleration factors:
     $$AF = \exp\left(\frac{E_a}{k_B}\left(\frac{1}{T_{use}} - \frac{1}{T_{stress}}\right)\right) \times \left(\frac{V_{stress}}{V_{use}}\right)^\gamma$$
   - Calculate timing degradation rate $d(\text{slack})/dt$.
