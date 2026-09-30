# IC Aging Environment

*[Leia em português](README.pt-BR.md)*

A central research environment for accelerated integrated circuit (IC) and FPGA aging (burn-in) experiments, characterization, and microelectronics reliability studies. Developed at **LESC — Laboratório de Engenharia de Sistemas de Computação, UFC** (Universidade Federal do Ceará).

---

## Documentation Quick Links

If you're new here, start with:
- **[`docs/onboarding/onboarding.tex`](docs/onboarding/onboarding.tex)** (or compiled **[`docs/IC_Aging_Environment.pdf`](docs/IC_Aging_Environment.pdf)**) — The full 35-page onboarding manual covering aging physics, RTL walkthrough, software architecture, serial protocols, workstation setup from scratch, running experiments, and data analysis.
- **[`CONTRIBUTING.md`](CONTRIBUTING.md)** — Guide for new students and researchers on coding standards, data hygiene, and lab workflows.
- **[`ARCHITECTURE.md`](ARCHITECTURE.md)** — Design intent and invariants behind each subsystem.
- **[`PROTOCOL.md`](PROTOCOL.md)** — Serial and byte-level communication protocols.
- **[`CLAUDE.md`](CLAUDE.md)** — Working map for AI assistants and concise reference for developers.

---

## Repository Structure

The repository is organized into distinct, modular domains:

```text
.
├── hardware/                    # Digital hardware and RTL designs
│   ├── fpga/
│   │   ├── xilinx/              # Vivado projects
│   │   │   ├── nexys4_ddr/      # Digilent Nexys4 DDR (Artix-7 xc7a100t)
│   │   │   └── ultrascale_plus/ # Custom UltraScale+ (xcau15p) SBCCI target
│   │   └── intel/               # Quartus projects
│   │       └── de10_lite/       # Terasic DE10-Lite (MAX10 10M50DA) port
│   ├── common/                  # Shared RTL modules (sensors, filters, UART)
│   └── asic/                    # ASIC PDK designs (SkyWater 130nm, GF180, etc.)
│
├── firmware/                    # Embedded microcontrollers & controllers
│   ├── thermal_chamber/         # Oven temperature PID & bang-bang controllers
│   ├── uart_router/             # ESP32 packet router (CROC / STM32 bridge)
│   └── supervisory/             # STM32L4 supervisory firmware (PMIC & OLED)
│
├── software/                    # Desktop host applications and instrumentation
│   ├── core/                    # Shared Python package (ic_aging_core)
│   ├── apps/
│   │   ├── App_Nexys/           # Single DUT (Nexys4 DDR) burn-in app
│   │   ├── App_2Nexys/          # Dual DUT (dual Nexys4 DDR) burn-in app
│   │   ├── App_CornerSweep/     # Voltage/failure-boundary sweep tool
│   │   └── App_FPGAging_Slack_Sensor/ # UltraScale+ CROC & STM32 bridge app
│   └── launcher.py              # Central Qt selector launcher
│
├── analysis/                    # Post-processing, modeling & statistics
│   ├── notebooks/               # Interactive Jupyter notebooks
│   ├── scripts/                 # Batch processing & Arrhenius extrapolation
│   ├── figures/                 # Script-generated publication figures
│   └── teoria_da_informacao/    # Information theory metrics on aging data
│
├── data/                        # Experimental campaign data standards
│   ├── README.md                # Data naming rules and schema standards
│   ├── sample_logs/             # Small (<1MB) verification logs tracked in Git
│   └── campaigns/               # Local multi-day burn-in CSVs (ignored by Git)
│
├── publications/                # Group academic production
│   ├── papers/                  # Conference & journal papers (SBCCI, JICS, IEEE)
│   ├── theses/                  # Undergraduate theses (TCC) & dissertations
│   ├── coursework/              # Academic projects & coursework materials
│   └── literature/              # BibTeX database (references.bib) & references
│
└── docs/                        # Onboarding guide, protocols & architecture specs
```

*(Note: Root-level aliases such as `vivado/`, `Arduino-ESP/`, `STM_FW_Aging/`, and `Artigos/` are symlinked to their new locations to preserve backwards compatibility with existing lab scripts).*

---

## Quick Start

### 1. Launching Desktop Applications
Run the unified launcher from the repository root:
```bash
./run.sh
```
This opens the dark-themed launcher dialog allowing you to select between:
- **App Nexys (1 DUT)**: Single Artix-7 Nexys4 DDR board with oven PID and optional ITECH PSU.
- **App 2-Nexys (2 DUTs)**: Dual Nexys4 DDR boards running concurrently in the same oven with closed-loop VCCINT regulation.
- **App CornerSweep**: Bench-characterization tool for identifying voltage failure boundaries.
- **App UltraScale+**: Custom UltraScale+ CROC board interfaced via ESP32 UART router and STM32 bridge.

Each application manages its own Python virtual environment (`.venv/`) independently.

### 2. Building FPGA Bitstreams

For **Nexys4 DDR (Artix-7)**:
```bash
cd hardware/fpga/xilinx/nexys4_ddr
scripts/check_layout.sh
scripts/create_project.sh
scripts/build_bitstream.sh --jobs 8
```

For **UltraScale+ (SBCCI target)**:
```bash
cd hardware/fpga/xilinx/ultrascale_plus
scripts/check_layout.sh
scripts/create_project.sh
scripts/build_bitstream.sh --jobs 8
```

---

## Experimental Data Policy

To prevent repository bloat, **raw campaign CSV files (>1 MB) are never committed to Git**.
- Local experiment logs land in `test_logs/` or `data/campaigns/` (locally preserved, ignored by Git).
- Curated, public campaign datasets are archived with DOIs on **Zenodo** or stored on the lab NAS.
- Lightweight sample logs for plotting tests are kept under `data/sample_logs/`.

See **[`data/README.md`](data/README.md)** and **[`CONTRIBUTING.md`](CONTRIBUTING.md)** for detailed specifications.
