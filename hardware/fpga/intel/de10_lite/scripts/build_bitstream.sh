#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_root="$(cd "$script_dir/.." && pwd)"
quartus_bin="${QUARTUS_BIN:-quartus_sh}"

usage() {
  cat <<'USAGE'
Usage: scripts/build_bitstream.sh [options]

Runs the full Quartus Prime compile flow (synthesis through Assembler) on
a project already created by scripts/create_project.sh.

Options:
  --project-name NAME  Quartus project name. Default: max10_aging_port
  --build-dir DIR      Build directory. Default: ./build
  -h, --help           Show this help.

Environment overrides:
  QUARTUS_BIN           quartus_sh executable. Default: quartus_sh
  QUARTUS_PROJECT_NAME  Same as --project-name
  QUARTUS_BUILD_DIR     Same as --build-dir

STATUS: this wrapper is real and generic (it just invokes `quartus_sh
--flow compile`), but the project it compiles is still an empty
scaffold until F1/F2 land RTL and constraints -- see create_project.tcl.
USAGE
}

project_name="${QUARTUS_PROJECT_NAME:-max10_aging_port}"
build_dir="${QUARTUS_BUILD_DIR:-$project_root/build}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project-name)
      project_name="${2:?missing value for $1}"
      shift 2
      ;;
    --build-dir)
      build_dir="${2:?missing value for $1}"
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

if [[ ! -f "$build_dir/$project_name.qpf" ]]; then
  echo "Project not found at $build_dir/$project_name.qpf" >&2
  echo "Run scripts/create_project.sh first." >&2
  exit 1
fi

cd "$build_dir"
"$quartus_bin" --flow compile "$project_name"

echo "Build complete. Output (.sof/.pof) in $build_dir/output_files/"
