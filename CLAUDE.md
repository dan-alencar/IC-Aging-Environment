# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

A complete hardware-in-the-loop environment for accelerated FPGA aging (burn-in) experiments. The system controls oven temperature via PID, monitors internal FPGA slack sensors, and logs everything to CSV. There are two Python GUI apps depending on which FPGA target is in use.

## Running the Python apps

### Root launcher (recommended entry point)

A Qt launcher dialog lets you choose between single-DUT and dual-DUT mode. It reuses `App_Nexys/.venv` for PySide6 (creating it if absent) and spawns the selected app as a subprocess, so no config or workers are shared in memory:

```bash
./run.sh          # from repo root — shows the launcher dialog
```

### Running apps directly (standalone)

Each app also has its own `run.sh` that sets `LD_LIBRARY_PATH` to resolve Qt lib conflicts with system packages on Linux Mint:

```bash
cd App_Nexys && ./run.sh                   # 1 DUT (Artix-7 Nexys4 DDR)
cd App_2Nexys && ./run.sh                  # 2 DUTs (dual Nexys4 DDR)
cd App_FPGAging_Slack_Sensor && ./run.sh   # UltraScale+ with STM32 bridge
```

If the `.venv` does not exist, `run.sh` creates it and installs from `requirements.txt`. To rebuild, delete `.venv/` and re-run.

To package `App_Nexys` as a standalone executable:
```bash
cd App_Nexys
source .venv/bin/activate
pyinstaller AgingMonitorApp.spec
# Output: dist/AgingMonitorApp
```

To package `App_Nexys` as a standalone executable:
```bash
cd App_Nexys
source .venv/bin/activate
pyinstaller AgingMonitorApp.spec
# Output: dist/AgingMonitorApp
```

## Building the FPGA bitstreams (Vivado)

Vivado must be on `PATH` (or set `VIVADO_BIN`). Generated output goes to `build/` and `artifacts/` — never commit those.

```bash
# SBCCI UltraScale+ (xcau15p-ffvb676-1-i, top: fpga_unified_top)
cd vivado/sbcci_fpga_aging
scripts/check_layout.sh          # sanity check, no Vivado needed
scripts/create_project.sh        # generates build/*.xpr
scripts/build_bitstream.sh --jobs 8

# Nexys4 DDR Artix-7 (xc7a100tcsg324-1, top: design_1_wrapper)
cd vivado/aging_study_nexys4ddr
scripts/check_layout.sh
scripts/create_project.sh
scripts/build_bitstream.sh --jobs 8
```

Bitstreams land in `artifacts/`. To open in the GUI, pass `--gui` to `create_project.sh`.

The Nexys4 project uses `src/constraints/fixed_pnr_constraints.xdc` (LOC/BEL + FIXED_ROUTE) to lock the critical path. Do not change placement or routing constraints without understanding the fixed-PnR experiment.

## STM32 firmware

`STM_FW_Aging/` is an STM32CubeIDE project for the STM32L4R9. Open `Teste_Aging.ioc` in STM32CubeMX to regenerate HAL code or import the `.project` into STM32CubeIDE.

Custom drivers live in `STM_FW_Aging/Drivers/`:
- `TPS65400/` — PMIC I²C driver (sets VCORE for the FPGA)
- `OLED/` — SSD1306 display driver
- `MYMGM1R/` — custom module driver

## System architecture

### App_Nexys (Nexys4 DDR target)

```
PC ──serial──► DUT (FPGA Nexys)    [always required]
PC ──serial──► Arduino             [optional: oven PID + SSR]
PC ──VISA───► PSU (SCPI)          [optional: programmable supply]
```

Workers run in QThread via QObject + QTimer polling:
- `ArduinoWorker` — sends `GET_DATA\n`, receives `DATA,<temp>,<sp>,<out>` ASCII
- `PSUWorker` — PyVISA SCPI (`MEAS:VOLT?`, `MEAS:CURR?`, `OUTP ON/OFF`)
- `DUTWorker` — sends byte `'F'`, reads 9 binary bytes Little Endian: `[TEMP×3][SLACK×2][VOLT×3][FAIL×1]`, converts temp/voltage by dividing raw by 1000
- `TestSequencer` — orchestrates all workers, runs safety limit checks, writes CSV rows

### App_FPGAging_Slack_Sensor (SBCCI UltraScale+ target)

```
PC ──serial──► ESP32 (UART router) ──► CROC FPGA  (header 0x10)
                                   └──► STM32      (header 0x20)
PC ──serial──► Arduino                             [optional: oven PID]
```

Key components:
- `UARTRouter` — multiplexes one serial port to two targets using 1-byte routing headers (`0x10` → FPGA/CROC, `0x20` → STM32). Uses a 60 ms dead-time gap when switching targets. Detects 9-byte aging packets via sliding window (bytes [2] and [7] must be `0x00` as padding).
- `ProtocolParser` — parses STM32 binary frames (header `0x10`/`0x20`, CRC16-Modbus LE). Also handles plain text lines.
- `STMWorker` — sends commands (VCORE, PAGE, MESSAGE, PING) built by `commands.py`, validated with CRC16-Modbus.
- `CROCWorker` — receives decoded `aging_data_received` signals from the Router.

FPGA aging packet (9 bytes from CROC, Little Endian):
```
[TL TH 00 SL SH VL VH 00 AL]
 temp(2)    slack(2)  vcc(2)  alarm(1)
```
Conversion: `raw_to_temp` and `raw_to_vcc` in `protocol.py` use Xilinx XADC formulas (12-bit shift-right-4, then affine).

### App_2Nexys (dual Nexys4 DDR target)

```
PC ──serial──► DUT-0 (Nexys4 DDR, ttyUSB higher)   [required]
PC ──serial──► DUT-1 (Nexys4 DDR, ttyUSB higher)   [required]
PC ──VISA───► PSU-0 (IT6502D, SCPI)                 [optional]
PC ──VISA───► PSU-1 (Agilent E3634A, SCPI)          [optional]
PC ──serial──► Arduino (shared oven)                 [optional]
```

**ttyUSB port pairing:** Each Nexys4 board enumerates two `ttyUSB*` ports via its FTDI chip. The **lower-numbered** port is JTAG (for Vivado programming) and must not be opened by the app. The **higher-numbered** port is the UART data channel. Always pick the higher one in the setup dialog.

**VCCINT closed-loop voltage control:** The FPGA XADC reports actual VCCINT (internal supply voltage) inside the 9-byte DUT packet (`dut_volt` field). `TestSequencer.log_data_tick()` runs a P-only trim every tick:
```
psu_cmd += VOLTAGE_KP * (vccint_setpoint - measured_vccint)
psu_cmd  = clamp(psu_cmd, PSU_MIN_V, PSU_MAX_V)
psu.set_voltage(psu_cmd)
```
`VOLTAGE_KP = 0.1` V/V is hardcoded in `App_2Nexys/config.py`. The CSV logs both `psu*_cmd_v` (command sent) and `psu*_voltage_v` (PSU readback).

**Signal routing:** `MainWindow._forward_to_aux0/1()` remaps the `plot_data_update` dict keys before forwarding to each `AuxPlotWidget` so the widget stays generic (uses `psu_voltage`, `dut_volt`, etc.).

### Shared patterns across all apps

- `config.py` — global mutable state module; `load_config()`/`save_config()` persist to `settings.json` in the app directory.
- `SetupDialog` (`setup_config.py`) — modal Qt dialog shown at startup to configure serial ports; writes `settings.json`.
- `DataLogger` (`logger.py`) — writes timestamped CSV rows to `test_logs/` inside the app directory.
- PID parameters (Kp=2.78, Ki=0.00106, Kd=5.0) were identified via FOPDT step test and tuned with SIMC (τc = θ). Do not change without a new step test; see comments in `App_Nexys/config.py`.
- Safety limits: oven max 130°C, DUT max 140°C, PSU current max 1.5 A.

## Arduino sketches

`Arduino-ESP/` contains active sketches; `Arduino-ESP/legacy/` holds superseded versions.

- `arduino_termostato/` — bang-bang oven controller (SSR + NTC).
- `PID_Controller/` — SIMC-tuned PID oven controller. Uses **ArduPID 1.0.1** (installed at `~/Arduino/libraries/ArduPID/`). Key API vs 0.2.1: `setTunings()` replaces `begin()`, `setILimits()` replaces `setWindUpLimits()`, `setDtMs()` replaces `setSampleTime()`, `compute(input)` takes input as argument and returns output (no pointer). `start()`/`stop()` were removed; `testRunning` flag controls execution.
- `esp32wroom_uart-reader/` — UART router between PC and FPGA/STM32 (SBCCI path).
- `FOPDT_Step_Test.ino/` — step-test sketch used to identify the FOPDT plant model.

## Reference documents

- `PROTOCOL.md` — serial protocol reference for DUT (Nexys4), Arduino, and PSU.
- `ARCHITECTURE.md` — design intent behind each subsystem and why decisions were made.
