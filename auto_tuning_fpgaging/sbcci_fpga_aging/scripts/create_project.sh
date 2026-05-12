#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
vivado_bin="${VIVADO_BIN:-vivado}"

if ! command -v "$vivado_bin" >/dev/null 2>&1; then
  echo "Vivado executable not found: $vivado_bin" >&2
  echo "Set VIVADO_BIN=/path/to/vivado or source the Vivado settings script." >&2
  exit 127
fi

mode="batch"
if [[ "${1:-}" == "--gui" ]]; then
  mode="gui"
  shift
fi

exec "$vivado_bin" -mode "$mode" -source "$script_dir/create_project.tcl" -notrace "$@"
