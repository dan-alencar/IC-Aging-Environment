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

The root launcher offers App_Nexys, App_2Nexys, and App_CornerSweep. App_FPGAging_Slack_Sensor (SBCCI/UltraScale+ target) must be launched standalone — different hardware family, not part of the Nexys4 DUT-count selector.

### Running apps directly (standalone)

Each app also has its own `run.sh` that sets `LD_LIBRARY_PATH` to resolve Qt lib conflicts with system packages on Linux Mint:

```bash
cd App_Nexys && ./run.sh                   # 1 DUT (Artix-7 Nexys4 DDR)
cd App_2Nexys && ./run.sh                  # 2 DUTs (dual Nexys4 DDR)
cd App_FPGAging_Slack_Sensor && ./run.sh   # UltraScale+ with STM32 bridge
cd App_CornerSweep && ./run.sh             # 1 DUT, VCCINT corner/failure-boundary sweep
```

If the `.venv` does not exist, `run.sh` creates it and installs from `requirements.txt`. To rebuild, delete `.venv/` and re-run.

To package `App_Nexys` as a standalone executable:
```bash
cd App_Nexys
source .venv/bin/activate
pyinstaller AgingMonitorApp.spec
# Output: dist/AgingMonitorApp
```

## No automated test suite

There are no project-level unit or integration tests. All validation is done by running the app against real hardware. The `.venv/` directories contain third-party library tests — ignore those.

## Building the FPGA bitstreams (Vivado)

Vivado must be on `PATH` (or set `VIVADO_BIN`). Generated output goes to `build/` and `artifacts/` — never commit those.

```bash
# SBCCI UltraScale+ (xcau15p-ffvb676-1-i, top: fpga_unified_top)
# Requires Vivado 2025.2+; XCI files were last saved with 2025.2.1
cd vivado/sbcci_fpga_aging
scripts/check_layout.sh          # sanity check, no Vivado needed
scripts/create_project.sh        # generates build/*.xpr
scripts/build_bitstream.sh --jobs 8
scripts/clean.sh                 # removes build/ and artifacts/

# Nexys4 DDR Artix-7 (xc7a100tcsg324-1, top: nexys4_aging_top)
cd vivado/aging_study_nexys4ddr
scripts/check_layout.sh
scripts/create_project.sh
scripts/build_bitstream.sh --jobs 8
scripts/clean.sh
```

Bitstreams land in `artifacts/`. To open in the GUI, pass `--gui` to `create_project.sh`.

The Nexys4 project uses `src/constraints/fixed_pnr_constraints.xdc` (LOC/BEL + FIXED_ROUTE) to lock the critical path. Do not change placement or routing constraints without understanding the fixed-PnR experiment.

To regenerate `fixed_pnr_constraints.xdc` from the reference checkpoint:
```bash
cd vivado/aging_study_nexys4ddr
scripts/extract_fixed_pnr_constraints.sh
```

**App_2Nexys dependency:** Both DUTs are programmed automatically at test start from `vivado/aging_study_nexys4ddr/bitstreams/nexys4_aging_top_dual-sensor.bit` (path hardcoded in `App_2Nexys/config.py` as `BITSTREAM_PATH`). A matching `.ltx` probes file (`BITSTREAM_LTX`) enables ILA debug if present. These pre-built files are version-controlled; rebuild and copy to `bitstreams/` when the RTL changes.

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
PC ──USB-TMC─► PSU IT6502D (VISA) [optional: programmable supply]
```

The UI uses a Catppuccin Mocha dark theme (`_DARK_STYLE` in `main_window.py`). Layout: top bar (oven/PSU/test controls), tabbed area (Sensor | Temperatura | Tensão), and a `QSplitter`-pinned log panel always visible below the tabs (not a separate tab). A status bar shows per-device connection state.

**PSU — ITECH IT6502D:** Connects via USB-TMC using PyVISA with the `@py` backend (`pyvisa-py`). `config.PSU_PORT` must be a USB VISA resource string such as `USB0::0x1AB1::0x0E11::IT6502D300004::INSTR`. To find it, run: `python3 -c "import pyvisa; rm=pyvisa.ResourceManager('@py'); print(rm.list_resources())"`. The setup dialog (`setup_config.py`) lists detected USB resources automatically. Only `USB::...` strings are accepted — legacy serial paths and `ASRL::...` strings are rejected at load time in `config.load_config()` to prevent the "Could not configure port" error that occurs when pyvisa-py tries to open a serial resource.

Workers run in QThread via QObject + QTimer polling:
- `ArduinoWorker` — sends `GET_DATA\n`, receives `DATA,<temp>,<sp>,<out>` ASCII
- `PSUWorker` — ITECH IT6502D via PyVISA (`@py` backend), SCPI: `MEAS:VOLT?`, `MEAS:CURR?`, `OUTP ON/OFF`. No baud rate — USB-TMC only.
- `DUTWorker` — sends byte `'T'` (`\x54`), reads 15 binary bytes Little Endian: `[TEMP×3][SLACK×2][VCCINT×3][FAIL×1][WRONG×2][CORRECT×2][ERR_CNT×2]`, converts temp/voltage by dividing raw by 1000. **DUT baud rate is 9600, not 115200.** Adder-canary fields (`wrong`, `correct`, `error_count`) are logged to CSV but not shown in the UI.
- `TestSequencer` — orchestrates all workers, runs safety limit checks, writes CSV rows. Runs the same VCCINT P-only closed-loop trim as App_2Nexys (`VOLTAGE_KP = 0.1` V/V in `config.py`); logs both `psu_cmd_v` and `psu_voltage`.

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
PC ──serial──► PSU-1 (Agilent E3634A, RS-232)       [optional]
PC ──serial──► Arduino (shared oven)                 [optional]
```

**ttyUSB port pairing:** Each Nexys4 board enumerates two `ttyUSB*` ports via its FTDI chip. The **lower-numbered** port is JTAG (for Vivado programming) and must not be opened by the app. The **higher-numbered** port is the UART data channel. Always pick the higher one in the setup dialog.

**USB device ID auto-resolution:** `config.resolve_hw_ports()` resolves DUT-0, DUT-1, and PSU-1 ports by following `/dev/serial/by-id/` symlinks using fixed USB serial IDs (`USB_ID_DUT0`, `USB_ID_DUT1`, `USB_ID_PSU1` in `App_2Nexys/config.py`). Update these if boards are swapped.

**Both DUTs auto-programmed at test start:** Both boards' onboard flash is broken — only SRAM works. `TestSequencer._program_both_duts()` programs DUT-0 and DUT-1 in a single Vivado batch session after the PSUs stabilise (`PSU_STABILISE_DELAY_S = 5 s`). After programming, `reset_data()` flushes the serial buffers and the log timer starts immediately — the Vivado batch job itself takes 30–60 s so the FPGAs are already running by then. `DUTWorker.poll_data()` boot-rejects any remaining transient packets (temp > 200 °C or vccint > 2.5 V). The bitstream (`BITSTREAM_PATH`), optional probes file (`BITSTREAM_LTX`), and Digilent serial numbers (`DUT0_DIGILENT_SERIAL`, `DUT1_DIGILENT_SERIAL`) are hardcoded in `App_2Nexys/config.py`. Pre-built bitstreams live in `vivado/aging_study_nexys4ddr/bitstreams/` (currently `nexys4_aging_top_dual-sensor.bit`). `VIVADO_BIN` resolves in order: `VIVADO_BIN` env var → `vivado` on `PATH` → a hardcoded lab-machine fallback path in `App_2Nexys/config.py`.

**PSU-0 auto-reconnect:** `PSUWorker0._try_reconnect()` detects VISA errors (which can occur when Vivado claims the USB bus during JTAG programming) and automatically reopens the resource after a 2 s delay. PSU-1 (E3634A via RS-232) does not have this logic.

**DUT packet (App_2Nexys, 15 bytes, Little Endian):** `DUTWorker.poll_data()` sends byte `'T'` (`\x54`) and reads 15 bytes: `[TEMP×3][SLACK×2][VCCINT×3][FAIL×1][WRONG×2][CORRECT×2][ERR_CNT×2]`. The adder-canary fields (`wrong`, `correct`, `error_count`) are logged to CSV but not shown in the UI. App_Nexys (single-DUT) sends `'F'` and uses the legacy 9-byte packet.

**VCCINT closed-loop voltage control (both App_Nexys and App_2Nexys):** The FPGA XADC reports actual VCCINT (internal supply voltage) inside the DUT packet (`dut_volt` field). `TestSequencer.log_data_tick()` runs a P-only trim every tick:
```
psu_cmd += VOLTAGE_KP * (vccint_setpoint - measured_vccint)
psu_cmd  = clamp(psu_cmd, PSU_MIN_V, PSU_MAX_V)
psu.set_voltage(psu_cmd)
```
`VOLTAGE_KP = 0.1` V/V is hardcoded in `App_2Nexys/config.py`. The CSV logs both `psu*_cmd_v` (command sent) and `psu*_voltage_v` (PSU readback).

**Signal routing:** `MainWindow._forward_to_aux0/1()` remaps the `plot_data_update` dict keys before forwarding to each `AuxPlotWidget` so the widget stays generic (uses `psu_voltage`, `dut_volt`, etc.).

### App_CornerSweep (single Nexys4 DDR, voltage/failure-boundary characterization)

Not a burn-in test app — a bench-characterization tool. It steps the DUT's VCCINT down through a fixed set of "corner" voltages and, at each corner, sweeps voltage further downward in fine steps to locate where the sensor's adder canary starts producing errors. Same DUT/PSU/Arduino serial stack as `App_Nexys` (reuses the same 15-byte `'T'`-triggered packet), but driven by its own state machine instead of a continuous burn-in loop.

`corner_sequencer.py`'s `Phase` enum drives the sequence:
```
IDLE → WAITING_TEMP → CORNER_SETTLING → CORNER_SAMPLING → SWEEP_SETTLING → SWEEP_SAMPLING → DONE
                          ↑______________________________________|
                          (loops back into the next corner in CORNERS_V)
```
- `WAITING_TEMP` — waits for the DUT to reach and hold its target temperature (`TEMP_STABLE_TICKS` consecutive ticks within `TEMP_STABLE_TOL_C`) before any corner starts.
- `CORNER_SETTLING` / `CORNER_SAMPLING` — for each voltage in `CORNERS_V` (default `[1.1, 1.0, 0.9]` V, high-to-low), waits for VCCINT to settle (`VOLT_SETTLE_TOL_V`) then collects `SAMPLES_PER_CORNER` baseline ticks.
- `SWEEP_SETTLING` / `SWEEP_SAMPLING` — from each corner, steps VCCINT down by `SWEEP_STEP_V` (default 10 mV) at a time, sampling `SWEEP_SAMPLE_TICKS` ticks per step, until an adder-canary error appears or `SWEEP_MIN_V` (safety floor) is reached — this is the failure-boundary search.

Config lives in `App_CornerSweep/config.py` (own `CORNERS_V`/`SWEEP_*`/`SETTLE_*` parameters, separate from the burn-in apps' `VOLTAGE_KP` closed-loop trim — this app commands PSU voltage open-loop, step by step, rather than closed-loop tracking a fixed setpoint). Logs via `CornerSweepLogger` (`logger.py`) to its own `test_logs/`.

### Shared patterns across all apps

- `config.py` — global mutable state module; `load_config()`/`save_config()` persist to `settings.json` in the app directory.
- `SetupDialog` (`setup_config.py`) — modal Qt dialog shown at startup to configure serial ports; writes `settings.json`.
- `DataLogger` (`logger.py`) — writes timestamped CSV rows to `test_logs/` inside the app directory.
- PID parameters (Kp=2.78, Ki=0.00106, Kd=5.0) were identified via FOPDT step test and tuned with SIMC (τc = θ). Do not change without a new step test; see comments in `App_Nexys/config.py`.
- Safety limits: oven max 130°C, DUT max 140°C, PSU current max 1.5 A.
- **DUT outer temperature loop:** `TestSequencer._adjust_oven_outer_loop()` shifts the oven setpoint by ±1°C every ~30 min (1800 ticks at 1 s/tick) to bring the DUT die temperature to its target, with a ±3°C dead-band. In `App_2Nexys`, the average of both DUT temperatures is used.

## FPGA RTL structure (Nexys4 DDR)

The aging sensor design uses three clock domains driven by a single MMCM (clk_wiz_0):
- `clk_sys` — 100 MHz, 0° — main system clock
- `psclk` — 100 MHz, 0° + dynamic phase shift — FF1 of the metastability sensor (`modern_sensible`)
- `clk_en` — 100 MHz, 100° fixed offset — FF3 (alarm latch) of the sensor

The metastability sensor (`modern_sensible`) uses `DONT_TOUCH`/primitive instantiation (`LUT2_L`, `FDCE`) to prevent synthesis optimization. `alarm_sig` originates in the `clk_en` domain and is crossed to `clk_sys` via a 2-FF synchronizer (`alarm_sync`) before reaching `adder_canary` and `controller_controller`. The raw `alarm_sig` drives only the LED (no timing path).

The `adder_canary` module implements a **dual-adder** design: `u_sensor` (toggle-driven) provides `crit_bit` for timing measurement; `u_canary` (counter-driven) provides `wrong`/`correct`/`error_count` for functional error detection. Both are structurally identical `ripple_adder` instances with `DONT_TOUCH` so they age at the same rate.

The FPGA also includes `uart_rx` (receives `'T'`/0x54 trigger byte from PC) and `sensor_stream` (latches all inputs at trigger time, serialises the 15-byte packet). The trigger is: UART `'T'`, or either manual button (BTNC/BTNL).

**Current RTL only supports the 15-byte packet triggered by `'T'`.** Both App_Nexys and App_2Nexys now use the `'T'`/15-byte protocol and are compatible with the current bitstream.

### Dual-adder sensor (implemented)

`adder_canary.sv` has a `toggle` FF that inverts every `clk_sys` cycle, driving `a_sensor` between `0x5555` and `0x5556`. With `B = 0xAAAA`, `sum_sensor[15]` toggles on every clock cycle (full 16-stage carry propagation each time), giving deterministic ±2-step `display_value` jitter. This replaces the original design where `crit_bit = sum_canary[15]` fired stochastically (~9 000-step scatter).

```
toggle → a_sensor (0x5555/0x5556) → u_sensor (DONT_TOUCH) → crit_bit → modern_sensible
a (counter)                        → u_canary (DONT_TOUCH) → wrong/correct/error_count
```

Full scientific rationale: `vivado/aging_study_nexys4ddr/SENSOR_ARCHITECTURE.md`. Validation checklist (Phases 3–7 still pending): `IMPLEMENTATION_ROADMAP.md`.

## Arduino sketches

`Arduino-ESP/` contains active sketches; `Arduino-ESP/legacy/` holds superseded versions.

- `arduino_termostato/` — bang-bang oven controller (SSR + NTC).
- `PID_Controller/` — SIMC-tuned PID oven controller. Uses **ArduPID 1.0.1** (installed at `~/Arduino/libraries/ArduPID/`). Key API vs 0.2.1: `setTunings()` replaces `begin()`, `setILimits()` replaces `setWindUpLimits()`, `setDtMs()` replaces `setSampleTime()`, `compute(input)` takes input as argument and returns output (no pointer). `start()`/`stop()` were removed; `testRunning` flag controls execution.
- `esp32wroom_uart-reader/` — UART router between PC and FPGA/STM32 (SBCCI path).
- `FOPDT_Step_Test.ino/` — step-test sketch used to identify the FOPDT plant model.
- `arduino_uart_tp_sniffer/` — passive UART sniffer for debugging serial traffic.

## Reference documents

- `README.md` / `README.pt-BR.md` — repo map and quick start, for humans (this file is for Claude Code).
- `PROTOCOL.md` — serial protocol reference for DUT (Nexys4), Arduino, and PSU.
- `ARCHITECTURE.md` — design intent behind each subsystem and why decisions were made.
- `docs/onboarding.tex` (and `docs/IC_Aging_Environment.pdf`) — 35-page onboarding manual: aging physics, RTL, software, protocols, workstation setup, running an experiment, data analysis, troubleshooting.
- `vivado/aging_study_nexys4ddr/SENSOR_ARCHITECTURE.md` — scientific rationale for the dual-adder sensor design.
- `vivado/aging_study_nexys4ddr/IMPLEMENTATION_ROADMAP.md` — phased checklist; RTL phases 1–2 are done, phases 3–7 (build, validation, data collection) are pending.
- `vivado/aging_study_nexys4ddr/CLAUDE.md` — sub-project CLAUDE.md with full RTL module hierarchy, clock domains, XADC formulas, and constraint strategy.

## Related work: MAX10/DE10-Lite port (separate branch)

A second student team is porting this sensor architecture to an Intel MAX10 (10M50DAF484C7G, DE10-Lite) target using Quartus Prime, as a parallel research line — not a replacement for this Vivado/Artix codebase. That work lives on the `max10-de10lite-port` branch, under `max10_port/`, with this repository's current implementation kept there as reference-only guidance material (see `max10_port/README.md` on that branch for the full plan and status).
