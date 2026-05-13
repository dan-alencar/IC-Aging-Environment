#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_root="$(cd "$script_dir/.." && pwd)"
vivado_bin="${VIVADO_BIN:-vivado}"

usage() {
  cat <<'USAGE'
Usage: scripts/create_project.sh [--gui] [options] [-- extra-vivado-args]

Options:
  --project-name NAME  Vivado project name. Default: aging_study_nexys4ddr
  --part PART          FPGA part. Default: xc7a100tcsg324-1
  --top MODULE         Top module. Default: design_1_wrapper
  --build-dir DIR      Build directory. Default: ./build
  -h, --help           Show this help.

Environment overrides:
  VIVADO_BIN           Vivado executable. Default: vivado
  VIVADO_PROJECT_NAME  Same as --project-name
  VIVADO_PART          Same as --part
  VIVADO_TOP           Same as --top
  VIVADO_BUILD_DIR     Same as --build-dir
USAGE
}

mode="batch"
vivado_args=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --gui)
      mode="gui"
      shift
      ;;
    --project-name)
      export VIVADO_PROJECT_NAME="${2:?missing value for $1}"
      shift 2
      ;;
    --part)
      export VIVADO_PART="${2:?missing value for $1}"
      shift 2
      ;;
    --top)
      export VIVADO_TOP="${2:?missing value for $1}"
      shift 2
      ;;
    --build-dir)
      export VIVADO_BUILD_DIR="${2:?missing value for $1}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --)
      shift
      vivado_args+=("$@")
      break
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

cd "$project_root"
exec "$vivado_bin" -mode "$mode" -source "$script_dir/create_project.tcl" -notrace "${vivado_args[@]}"
