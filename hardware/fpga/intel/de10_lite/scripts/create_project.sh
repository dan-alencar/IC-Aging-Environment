#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_root="$(cd "$script_dir/.." && pwd)"
quartus_bin="${QUARTUS_BIN:-quartus_sh}"

usage() {
  cat <<'USAGE'
Usage: scripts/create_project.sh [options]

Options:
  --project-name NAME  Quartus project name. Default: max10_aging_port
  --part PART          Device part. Default: 10M50DAF484C7G
  --top MODULE         Top-level entity. Default: max10_aging_top
  --build-dir DIR      Build directory. Default: ./build
  -h, --help           Show this help.

Environment overrides:
  QUARTUS_BIN           quartus_sh executable. Default: quartus_sh
  QUARTUS_PROJECT_NAME  Same as --project-name
  QUARTUS_PART          Same as --part
  QUARTUS_TOP           Same as --top
  QUARTUS_BUILD_DIR     Same as --build-dir
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project-name)
      export QUARTUS_PROJECT_NAME="${2:?missing value for $1}"
      shift 2
      ;;
    --part)
      export QUARTUS_PART="${2:?missing value for $1}"
      shift 2
      ;;
    --top)
      export QUARTUS_TOP="${2:?missing value for $1}"
      shift 2
      ;;
    --build-dir)
      export QUARTUS_BUILD_DIR="${2:?missing value for $1}"
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

if ! command -v "$quartus_bin" >/dev/null 2>&1; then
  echo "Quartus executable not found: $quartus_bin" >&2
  echo "Set QUARTUS_BIN=/path/to/quartus_sh or source Quartus's environment script." >&2
  exit 127
fi

cd "$project_root"
exec "$quartus_bin" -t "$script_dir/create_project.tcl"
