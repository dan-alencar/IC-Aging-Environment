# Contributing Guidelines — LESC / GSEM Research Group

Welcome to the **IC-Aging Environment** central repository. This codebase is shared across research tracks in microelectronics, FPGA reliability, thermal characterization, and hardware acceleration at **LESC — Laboratório de Engenharia de Sistemas de Computação, UFC**.

To maintain codebase health, scientific reproducibility, and ease of onboarding, all contributors must follow these guidelines.

---

## 1. Repository Structure Overview

Work within the appropriate domain:

- **`hardware/`**: RTL code, timing constraints, pinouts, and EDA build scripts.
  - `hardware/fpga/xilinx/`: Vivado projects (Nexys4 DDR, UltraScale+).
  - `hardware/fpga/intel/`: Quartus projects (MAX10 DE10-Lite).
  - `hardware/common/`: Shared, vendor-agnostic RTL modules.
  - `hardware/asic/`: ASIC PDK implementations.
- **`firmware/`**: Microcontroller code.
  - `firmware/thermal_chamber/`: Oven PID and bang-bang sketches.
  - `firmware/uart_router/`: Router sketches (ESP32).
  - `firmware/supervisory/`: MCU supervisory control (STM32L4).
- **`software/`**: Host software and instrumentation.
  - `software/core/`: Shared library (`ic_aging_core`).
  - `software/apps/`: Desktop GUI applications.
- **`data/`**: Experimental campaign logs and benchmark fixtures.
- **`analysis/`**: Post-processing, statistical modeling, Arrhenius fitting, and plotting.
- **`publications/`**: Group publications, drafts, theses, and BibTeX literature.
- **`docs/`**: Onboarding manuals, hardware wiring schematics, and SOPs.

---

## 2. Experimental Data Hygiene (Critical)

> [!WARNING]
> **NEVER commit raw campaign CSV files (>1 MB) to Git.**
> Multi-day burn-in experiments generate hundreds of thousands of lines. Checking these into Git quickly causes repository bloat and slows down clones.

- **Local runs**: All desktop apps output local logs into `test_logs/` or `data/local_runs/`, which are globally ignored by `.gitignore`.
- **Sample fixtures**: If you need a log for testing or documentation, store a trimmed version (<1 MB) in `data/sample_logs/`.
- **Archiving published data**: Upload complete campaign datasets to **Zenodo** (to obtain a permanent citable DOI) or store them on the lab NAS storage under:
  ```
  CAMPAIGNS/YYYY-MM-DD_<DUT_ID>_<NOMINAL_V>_<TEMP_SP>/
  ```

---

## 3. Adding a New FPGA Target

When porting the aging sensor to a new FPGA family or board:
1. Create a dedicated directory under `hardware/fpga/<vendor>/<board_name>/`.
2. Follow the scripted build pattern:
   - `scripts/check_layout.sh` — directory sanity check.
   - `scripts/create_project.tcl` — project generation from tracked source.
   - `scripts/build_bitstream.tcl` — non-interactive synthesis and implementation.
3. **Preserve PnR Invariants**: If the sensor requires fixed placement and routing (like the carry-chain adder in Artix-7), lock the critical path cells and interconnect using constraints (`LOC`, `BEL`, `FIXED_ROUTE`).
4. Document the clock domains and telemetry protocol in a local `README.md`.

---

## 4. Adding or Modifying Instruments

When adding support for a new Power Supply (PSU), Source Measure Unit (SMU), or Temperature Controller:
1. Implement the driver inside `software/core/ic_aging_core/instruments/`.
2. Ensure communications are thread-safe and handle timeouts gracefully.
3. For VISA devices, always use the pure Python `@py` backend (`pyvisa-py`) and accept `USB::...` or `TCPIP::...` resource strings.

---

## 5. Coding Standards & Git Workflow

- **Branches**:
  - `main`: Stable, hardware-validated code.
  - `feature/<name>`: New sensor architectures, app features, or board ports.
  - Pull requests or peer review before merging into `main`.
- **Commit Messages**:
  - Use clear, prefix-based messages:
    - `hardware: add 4-channel RCA sensor wrapper for Nexys4`
    - `firmware: update oven PID sample time to 100ms`
    - `software: implement Agilent E3634A voltage clamp`
    - `docs: update pinout table for DE10-Lite`
- **Python**: Format code with standard conventions (PEP 8), use type hints where practical, and verify imports with `python3 -m py_compile <file.py>`.
- **SystemVerilog/Verilog**: Use explicit port declarations, descriptive signal names, and include clock-domain annotations in header comments.
