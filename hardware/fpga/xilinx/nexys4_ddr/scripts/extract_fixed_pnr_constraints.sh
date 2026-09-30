#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_root="$(cd "$script_dir/.." && pwd)"
vivado_bin="${VIVADO_BIN:-vivado}"

usage() {
  cat <<'USAGE'
Usage: scripts/extract_fixed_pnr_constraints.sh [--checkpoint FILE] [--output FILE]

Extract LOC, BEL, and FIXED_ROUTE constraints from the preserved fixed PnR
checkpoint. This is an audit/regeneration helper; normal builds do not use the
checkpoint.

Options:
  --checkpoint FILE   Input DCP. Default: references/fixed_pnr.dcp
  --output FILE       Output XDC. Default: src/constraints/fixed_pnr_constraints.xdc
  -h, --help          Show this help.

Environment:
  VIVADO_BIN          Vivado executable. Default: vivado
USAGE
}

checkpoint="$project_root/references/fixed_pnr.dcp"
output="$project_root/src/constraints/fixed_pnr_constraints.xdc"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --checkpoint)
      checkpoint="${2:?missing value for $1}"
      shift 2
      ;;
    --output)
      output="${2:?missing value for $1}"
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

if [[ ! -f "$checkpoint" ]]; then
  echo "Checkpoint not found: $checkpoint" >&2
  exit 1
fi

mkdir -p "$(dirname "$output")"
export FIXED_PNR_DCP="$checkpoint"
export FIXED_PNR_XDC="$output"

cd "$project_root"
exec "$vivado_bin" -mode batch -source "$script_dir/extract_fixed_pnr_constraints.tcl" -notrace
