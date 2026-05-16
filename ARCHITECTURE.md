# Architecture Reference

This document describes the design intent behind each subsystem. Read it alongside `PROTOCOL.md` and `CLAUDE.md` before making structural changes.

---

## Experiment overview

The goal is accelerated aging (burn-in) of Xilinx FPGAs. The FPGA runs a timing-critical path (carry-chain adder or similar) with an on-chip slack sensor. As the FPGA ages under elevated temperature and voltage, timing slack decreases. The app monitors this degradation over hours to days.

Key variables logged per experiment:
- **Oven temperature** — controlled to a setpoint via PID + SSR + NTC
- **FPGA VCCINT** — internal supply voltage (from XADC)
- **FPGA die temperature** — from XADC
- **Timing slack** — from the on-chip sensor (increments = degradation)

---

## Python apps

### App_Nexys — single DUT

**Target:** Xilinx Artix-7, Nexys4 DDR board.  
**Bitstream source:** `vivado/aging_study_nexys4ddr/`.

Hardware topology:
```
PC ──ttyUSB(higher)──► FPGA (DUT)       [required]
PC ──ttyUSB──────────► Arduino (oven)   [optional]
PC ──USB VISA────────► IT6502D (PSU)    [optional]
```

The PSU voltage is set once at test start and held constant. There is no VCCINT closed-loop in this app — if the experiment needs voltage stability, external SCPI commands are sufficient.

### App_2Nexys — dual DUT

**Target:** Two Xilinx Artix-7 Nexys4 DDR boards, run simultaneously.  
**Bitstream source:** `vivado/aging_study_nexys4ddr/` (same for both boards).

Hardware topology:
```
PC ──ttyUSB(higher, board0)──► FPGA DUT-0     [required]
PC ──ttyUSB(higher, board1)──► FPGA DUT-1     [required]
PC ──USB VISA────────────────► IT6502D PSU-0  [optional]
PC ──USB VISA────────────────► E3634A  PSU-1  [optional]
PC ──ttyUSB──────────────────► Arduino        [optional, shared oven]
```

**Why two DUTs?** Running two boards in the same oven at the same time halves the calendar time needed to gather comparative aging data (e.g., two different voltage setpoints, or two process corners).

**Why VCCINT closed-loop?** FPGA die resistance changes with temperature. As the oven heats up, the actual VCCINT seen by the core logic drifts away from what the PSU is nominally outputting. The P-only trim (`VOLTAGE_KP = 0.1 V/V`, hardcoded in `config.py`) corrects this slowly enough to be stable. A full PID was deemed unnecessary because the dominant dynamics are slow (minutes) and the thermal closed-loop on the oven already reduces VCCINT disturbances indirectly.

**ttyUSB pairing:** Each Nexys4 board's FTDI chip creates two USB serial ports. The lower-indexed `ttyUSB*` is JTAG (used by Vivado to program the bitstream). The higher-indexed one carries UART data from the aging-study firmware. The setup dialog shows a note reminding the user to always pick the higher-numbered port.

### App_FPGAging_Slack_Sensor — UltraScale+ (SBCCI target)

**Target:** Artix UltraScale+, custom board.  
**Bitstream source:** `vivado/sbcci_fpga_aging/`.

Unlike the Nexys apps, this setup uses an **ESP32 as a UART router** between the PC and two targets (FPGA and STM32). A 1-byte routing header (`0x10` = FPGA, `0x20` = STM32) precedes each packet. This allows a single USB-serial connection to serve two physical devices.

The STM32 (STM32L4R9) controls a TPS65400 PMIC to set VCORE for the FPGA, displays status on an SSD1306 OLED, and acts as a bridge for low-level FPGA control. The Python app uses a binary CRC16-Modbus protocol to communicate with it.

---

## Firmware

### Arduino — PID oven controller (`Arduino-ESP/PID_Controller/`)

Uses **ArduPID 1.0.1**. The FOPDT model identified via step test:

```
G(s) = 1.56 * exp(-150.6s) / (1307.2s + 1)
K = 1.56 °C/%   θ = 150.6 s   τ = 1307.2 s   θ/τ = 0.115
```

SIMC tuning with `τc = θ`: Kp = 2.78, Ki = 0.00106, Kd = 5.0.  
These are **fixed constants** — do not change without a new step test and SIMC re-tuning.

SSR control uses time-proportioning (5-second window). A 1°C/s ramp prevents step overshoot when setting a new setpoint.

### ESP32 — UART router (`Arduino-ESP/esp32wroom_uart-reader/`)

Routes packets between the PC and the FPGA/STM32 based on the leading header byte. This enables a single USB connection to serve both targets without a USB hub.

### STM32 firmware (`STM_FW_Aging/`)

STM32CubeIDE project for STM32L4R9 (STM32L4xx HAL). Custom drivers:
- `TPS65400/` — PMIC I²C driver; controls FPGA VCORE via voltage register writes
- `OLED/SSD1306` — status display
- `MYMGM1R/` — board-specific module

The STM32 does not run a PID — voltage control in the UltraScale+ path is open-loop (set a target voltage via the PMIC register). Closed-loop voltage control exists only in `App_2Nexys` for the Nexys4 DDR path.

---

## FPGA bitstream projects

### `vivado/aging_study_nexys4ddr/`

**Board:** Digilent Nexys4 DDR (Artix-7, `xc7a100tcsg324-1`).  
**Top:** `design_1_wrapper`.

The critical path (carry-chain adder) is **fixed in placement and routing** via `src/constraints/fixed_pnr_constraints.xdc`. This is essential: without fixed PnR, Vivado may re-route the path on each rebuild and change its delay characteristics, making aging measurements incomparable across rebuilds.

- `LOC` / `BEL` constraints fix cell placement.
- `FIXED_ROUTE` preserves the exact interconnect path from the original `fixed_pnr.dcp` checkpoint.
- `references/fixed_pnr.dcp` is a historical reference only (not a build input).

To regenerate `fixed_pnr_constraints.xdc` from the checkpoint (e.g., if constraints are lost):
```bash
cd vivado/aging_study_nexys4ddr
scripts/extract_fixed_pnr_constraints.sh
```

### `vivado/sbcci_fpga_aging/`

**Board:** Custom UltraScale+ board (`xcau15p-ffvb676-1-i`).  
**Top:** `fpga_unified_top`.

This is the more advanced target, used for the SBCCI paper. It uses block design (IP integrator) and includes XADC IP for on-chip temperature and voltage sensing. The UART output from the FPGA is routed through the ESP32 to the PC.

---

## Data flow summary

```
Oven NTC ──► Arduino (PID) ──► SSR ──► Oven heater
                │
                │ GET_DATA / DATA,t,sp,out (ASCII serial)
                ▼
FPGA XADC ──► DUT firmware ──► 9-byte binary packet
                │
                │ 'F' trigger / 9-byte response
                ▼
PSU ──────────► VISA SCPI ──► VOLT/MEAS commands
                │
                ▼
         TestSequencer (Python QThread)
                │ log tick every LOG_INTERVAL_MS
                ▼
         DataLogger ──► test_logs/*.csv
                │
                ▼
         Qt signals ──► PlotWidget, AuxPlotWidget, MainWindow labels
```
