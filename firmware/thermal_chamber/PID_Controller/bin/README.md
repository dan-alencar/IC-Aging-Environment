# Oven controller binary of the SBCCI 2026 runs (reference only)

`PID_Controller_SBCCI2026_nano33iot.bin`: the PID controller firmware 1.x as built for the
Arduino Nano 33 IoT and used for the SBCCI 2026 PID run (from the colleague's
`D&T 2027/10_DT_Monitor/firmware_forno`). Firmware 2.0 (`../PID_Controller.ino`, `../../SAFETY.md`)
keeps the same control law and adds the safety checks; build it with `../../build.sh`.
