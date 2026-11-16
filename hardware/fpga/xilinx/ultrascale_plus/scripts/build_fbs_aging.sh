#!/usr/bin/env bash
# Build fbs_aging_top (IC-Aging on the fbs platform). Vivado on PATH or VIVADO_BIN.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
vivado="${VIVADO_BIN:-vivado}"
out="$(realpath -m "${1:-$here/../build/fbs_aging}")"
mkdir -p "$out"
cd "$out"
"$vivado" -mode batch -nojournal -log "$out/vivado.log" -source "$here/build_fbs_aging.tcl" -tclargs "$out"
