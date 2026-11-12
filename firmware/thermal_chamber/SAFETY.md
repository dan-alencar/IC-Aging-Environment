# Oven controller safety (firmware 2.0)

Firmware 2.0 of `PID_Controller` and `arduino_termostato` keeps both control laws exactly as they were. The PID gains, 5 s window, 1 °C/s ramp, ±2 °C hysteresis and 1 s decision period are all unchanged, so new runs stay comparable with SBCCI 2026. What it adds is protection. The requirements are in `fpgaging-board-support/docs/SPEC.md` §6.3.

## What the firmware does now

Each check latches a fault. The SSR stays off until `CLEAR_FAULT`, and that command is refused while the cause is still present.

| Fault | Trigger | Why |
|---|---|---|
| `SENSOR` | Averaged ADC within 1 % of either rail, or a temperature outside −20…200 °C | On 05/11/2026 the NTC read −78 °C with the oven at 49 °C. An open NTC reads very cold, so firmware 1.x would have held the heater at 100 % |
| `OVERTEMP` | Oven (or cutoff NTC) above `OVEN_CUTOFF_C` = 140 °C | 1.x had no limit of its own; only the PC apps checked 130 °C |
| `NO_RISE` | Output above 80 % for 10 min with less than 2 °C of rise | Heater, SSR or NTC placement fault |
| `HOST_SILENT` | No command for N minutes while running, if `SET_HOST_TIMEOUT,N` was sent | Optional. The default (0) holds the setpoint, so a multi-day run survives a PC crash |

Also:
- **Watchdog:** the SAMD21 hardware watchdog (~4 s) resets a hung sketch, and the SSR pin is low from reset.
- **Setpoint range:** `SET_SP` accepts 20–130 °C; anything else gets `ERR,RANGE`.
- **Live temperature:** the reading is updated while idle too. 1.x froze it at the boot value until `START_TEST`.
- **Replies:** every command is answered, with `ERR,UNKNOWN` for unknown ones.
- **Extra DATA fields:** `GET_DATA` appends `state` and `fault`. Old apps read only the first four fields.
- **Extra CONFIG fields:** `GET_CONFIG` appends `FW`, `NTC_CAL`, `CUTOFF`, `SP_MAX`, `HOSTTO` and `CUTOFF_NTC`.

## Hardware backstop (install by hand)

Firmware cannot stop a heater whose SSR has failed shorted, which is how SSRs usually fail. Two parts are needed outside the controller:

1. **Thermal cutoff in series with the heater.** Use a one-shot thermal fuse (TCO) or a normally-closed bimetal thermostat at about **150 °C**: 10 °C above the firmware cutoff, below anything that damages the oven or the boards.
   - It must be rated for the heater's mains voltage and current with margin.
   - Mount it on the oven wall or in the air near the heater, not on the NTC.
   - It switches the heater supply directly, independent of the SSR.
2. **Independent cutoff sensor (optional, recommended).** A second NTC (10 kΩ, β 3950) with its own 10 kΩ divider to 3.3 V on a free analog pin, placed near the boards.
   - Set `CUTOFF_NTC_PIN` (e.g. `A2`) in the sketch and rebuild.
   - The firmware then applies the sensor and cutoff checks to both NTCs and reports the second one as a seventh `DATA` field.
   - A thermocouple with a MAX31855 works too, but needs code.

Record what was installed, with the date, in the lab log.

## Bench checks before relying on 2.0

Run these with the oven empty and the boards unpowered. Talk to the controller with `screen /dev/ttyACM0 115200` (or the apps' oven panel).

| # | Check | Expected |
|---|---|---|
| 1 | `GET_CONFIG` | `FW=2.0.0`, the PID gains unchanged, `CUTOFF=140.0` |
| 2 | `GET_DATA` twice, 10 s apart, without `START_TEST` | The temperature follows the room (1.x showed the boot value) |
| 3 | Unplug the NTC while idle | `EVENT,FAULT,SENSOR` within 1 s; `DATA` shows `FAULT,SENSOR`; `START_TEST` → `ERR,FAULT` |
| 4 | Reconnect the NTC, `CLEAR_FAULT` | `OK,FAULT_CLEARED` |
| 5 | `SET_SP,300` | `ERR,RANGE` |
| 6 | `SET_SP,45`, `START_TEST`, then unplug the NTC while heating | `FAULT,SENSOR`, SSR off at once (LED on the SSR goes dark) |
| 7 | Temporarily build with `OVEN_CUTOFF_C` 5 °C above room temperature, warm the NTC by hand | `FAULT,OVERTEMP`. Rebuild with 140 afterwards and check `GET_CONFIG` |
| 8 | Disconnect the heater, `SET_SP,80`, `START_TEST`, wait 10 min | `FAULT,NO_RISE` |
| 9 | `SET_HOST_TIMEOUT,1`, `START_TEST`, stay silent for 70 s | `FAULT,HOST_SILENT`. Then `SET_HOST_TIMEOUT,0` |
| 10 | Run App_Nexys (or `teste_forno`) for 10 min | Readings and control as before; the extra `DATA` fields are ignored |

Checks 6 and 8 need someone present. Keep the heater supply switch at hand.

## NTC calibration (Steinhart–Hart)

The β equation (β = 3950) can be a few degrees off over 25–130 °C. To calibrate:

1. Put a reference thermometer next to the NTC. Record the averaged ADC value and the reference temperature at three stable points, for example ~25, ~75 and ~120 °C. `DATA` shows the temperature; the ADC average is `R = 10000·adc/(4095−adc)`.
2. Solve for A, B, C in `1/T = A + B·ln R + C·(ln R)³` (T in kelvin) from the three points.
3. Set `SH_A`, `SH_B`, `SH_C`, `USE_STEINHART_HART = true` and a new `NTC_CAL` name (e.g. `SH-20261120`), then rebuild.

This changes the measured temperature, and therefore what the PID regulates to, but not the control law. Note the calibration name in the run log. `GET_CONFIG` reports it, and the apps record it.

## Build and flash

```bash
./build.sh                                  # PID controller
SKETCH=arduino_termostato ./build.sh        # bang-bang controller
./build.sh upload /dev/ttyACM0              # flash the PID controller
```

`build.sh` uses `arduino-cli` with the SAMD core and ArduPID 1.0.1. ArduHelpers 0.0.1, which ArduPID pulls in, needs `-std=gnu++14 -include type_traits`, and the script passes both.
