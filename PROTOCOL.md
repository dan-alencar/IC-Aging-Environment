# Serial Protocol Reference

This document describes every serial protocol used in this project. Read it before modifying firmware or workers — both sides must match exactly.

---

## 1. DUT Protocol — Nexys4 DDR FPGA → PC

Used by `App_Nexys/workers.py:DUTWorker` and `App_2Nexys/workers.py:DUTWorker`.

**Physical layer:** UART, 9600 baud (configurable in setup dialog), 8N1.  
**Port:** The **higher-numbered** `ttyUSB*` of each board pair (lower is JTAG).

### Request (PC → FPGA)

Send exactly 1 byte: `0x46` (`'F'`).

### Response (FPGA → PC)

The FPGA replies with **9 binary bytes, Little Endian**, within 2 seconds:

```
Byte index:  0    1    2    3    4    5    6    7    8
             TL   TH   00   SL   SH   VL   VH   00   AL
             ↑─────↑        ↑─────↑   ↑─────↑        ↑
             raw_temp(16)   raw_slack  raw_vcc(16)    alarm
```

- Bytes [2] and [7] are always `0x00` (padding).
- Byte [8] `AL`: alarm flag (`0x01` = timing violation, `0x00` = OK).

### Conversions (firmware scales, divide by 1000)

```python
raw_temp  = int.from_bytes(data[0:3], 'little')  # 3-byte field but only lower 2 used
raw_slack = int.from_bytes(data[3:5], 'little')
raw_vcc   = int.from_bytes(data[5:8], 'little')

temp_c  = raw_temp  / 1000.0   # °C
slack   = raw_slack             # increment counter (integer)
vccint  = raw_vcc   / 1000.0   # V (XADC VCCINT)
```

Readings of (0, 0, 0) during FPGA initialization are filtered silently.

### Notes for App_FPGAging_Slack_Sensor (UltraScale+ / CROC)

The CROC sends the same 9-byte packet format, but with different XADC conversion formulas (Xilinx UltraScale+):

```python
# In App_FPGAging_Slack_Sensor/protocol.py
raw_16bit = pkt[0] | (pkt[1] << 8)
temp_c    = ((raw_16bit >> 4) * 503.975 / 4096.0) - 273.15
vccint    = ((raw_16bit >> 4) * 3.0)   / 4096.0
```

---

## 2. Arduino Protocol — PC ↔ Arduino (oven PID controller)

Used by `ArduinoWorker` in all three Python apps.

**Physical layer:** UART over USB-CDC (Arduino Nano 33 IoT / similar), 115200 baud, 8N1.

All messages are newline-terminated ASCII strings (`\n`).

### Commands (PC → Arduino)

| Command | Format | Purpose |
|---|---|---|
| `SET_SP,<value>` | `SET_SP,100.0` | Set target oven temperature (°C) |
| `START_TEST` | literal | Enable PID + SSR control |
| `STOP_TEST` | literal | Stop PID, turn off SSR |
| `GET_DATA` | literal | Request current readings |
| `GET_CONFIG` | literal | Request firmware configuration |

### Responses (Arduino → PC)

| Trigger | Response format | Example |
|---|---|---|
| `SET_SP` | `OK,SP_SET` | `OK,SP_SET` |
| `START_TEST` | `OK,TEST_STARTED\nINFO,PID_CONFIG,<Kp>,<Ki>,<Kd>` | `OK,TEST_STARTED` |
| `STOP_TEST` | `OK,TEST_STOPPED` | — |
| `GET_DATA` | `DATA,<temp>,<ramp_sp>,<pid_out>` | `DATA,45.32,44.50,75.60` |
| `GET_CONFIG` | `CONFIG,KP=<v>,KI=<v>,KD=<v>,WINDOW=<ms>,RAMP=<v>` | — |
| Power-on | Multi-line banner ending with `READY` | — |

All floats in `DATA` use 2 decimal places. PID output is 0–100 (%).

### ArduPID 1.0.1 API (PID_Controller.ino)

The sketch uses ArduPID v1.0.1 (`~/Arduino/libraries/ArduPID/`). Key calls:

```cpp
myPID.setTunings(KP, KI, KD);       // replaces begin()
myPID.setSetpoint(rampedSetpoint);   // must call before first compute()
myPID.setOutputLimits(0, 100);
myPID.setILimits(0, 100);            // replaces setWindUpLimits()
myPID.setDtMs(CONTROL_PERIOD_MS);   // replaces setSampleTime()
myPID.reset();

// In loop:
myPID.setSetpoint(rampedSetpoint);   // update ramped value each iteration
pidOutput = myPID.compute(currentCelsius);  // takes input, returns float
```

`start()` / `stop()` do not exist in 1.0.1; the `testRunning` boolean gates `compute()`.

---

## 3. PSU Protocol — SCPI over USB-VISA

Used by `PSUWorker` in all Python apps via PyVISA (`@py` backend).

Both PSU models are SCPI-compatible and use the same commands.

| Model | Assignment |
|---|---|
| IT6502D | App_Nexys PSU / App_2Nexys PSU-0 (DUT-0) |
| Agilent E3634A | App_2Nexys PSU-1 (DUT-1) |

### Commands sent by the app

```
*IDN?          → identification string (used at startup to verify connection)
CURR <A>       → set current limit (default: MAX_PSU_CURRENT_A = 1.5 A)
VOLT <V>       → set output voltage
OUTP ON        → enable output
OUTP OFF       → disable output
MEAS:VOLT?     → read measured output voltage (V)
MEAS:CURR?     → read measured output current (A)
```

### VISA resource format

USB instruments appear as `USB0::0x<VID>::0x<PID>::<serial>::INSTR`. Use `pyvisa.ResourceManager('@py').list_resources()` to discover them. The setup dialog shows all discovered USB VISA resources.

---

## 4. STM32 Protocol (App_FPGAging_Slack_Sensor only)

**Physical layer:** passed through ESP32 UART router, header byte `0x20`.

Binary framing:
```
[0x20][ctrl][len_H][len_L][payload...][CRC_L][CRC_H]
```
- `ctrl` byte: `direction(7) | error(6:4) | function(3:0)`
- CRC: CRC16-Modbus, Little Endian
- Functions: `FUNC_P=0x01` (page), `FUNC_M=0x02` (message), `FUNC_V=0x03` (voltage)

See `App_FPGAging_Slack_Sensor/protocol.py:compute_crc16_modbus` and `commands.py` for frame builders.
