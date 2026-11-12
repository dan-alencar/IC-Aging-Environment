#!/bin/bash
# Build (and optionally upload) the oven controllers with arduino-cli.
#   ./build.sh                    compile PID_Controller for the Nano 33 IoT
#   ./build.sh upload /dev/ttyACM0
#   SKETCH=arduino_termostato ./build.sh
# Needs: arduino-cli, core arduino:samd, libraries ArduPID@1.0.1 (pulls ArduHelpers 0.0.1).
# ArduHelpers 0.0.1 uses C++14 features and does not include <type_traits>, hence the flags.
set -euo pipefail
cd "$(dirname "$0")"
CLI=${ARDUINO_CLI:-$(command -v arduino-cli || echo "$HOME/eda/arduino-cli/arduino-cli")}
FQBN=arduino:samd:nano_33_iot
FLAGS="compiler.cpp.extra_flags=-std=gnu++14 -include type_traits"
SKETCH=${SKETCH:-PID_Controller}          # SKETCH=arduino_termostato ./build.sh for the bang-bang one
"$CLI" compile -b "$FQBN" --warnings all --build-property "$FLAGS" --output-dir "build/$SKETCH" "$SKETCH"
if [ "${1:-}" = upload ]; then
  "$CLI" upload -b "$FQBN" -p "${2:?serial port}" --input-dir "build/$SKETCH" "$SKETCH"
fi
