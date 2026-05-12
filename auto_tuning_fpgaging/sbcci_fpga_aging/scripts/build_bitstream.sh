#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
vivado_bin="${VIVADO_BIN:-vivado}"

usage() {
  cat <<'USAGE'
Usage: scripts/build_bitstream.sh [--jobs N]

Environment overrides:
  VIVADO_BIN           Vivado executable. Default: vivado
  VIVADO_JOBS          Parallel jobs. Default: 8
  VIVADO_PART          FPGA part. Default: xcau15p-ffvb676-1-i
  VIVADO_BUILD_DIR     Build directory. Default: ./build
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -j|--jobs)
      export VIVADO_JOBS="${2:?missing value for $1}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if ! command -v "$vivado_bin" >/dev/null 2>&1; then
  echo "Vivado executable not found: $vivado_bin" >&2
  echo "Set VIVADO_BIN=/path/to/vivado or source the Vivado settings script." >&2
  exit 127
fi

exec "$vivado_bin" -mode batch -source "$script_dir/build_bitstream.tcl" -notrace
