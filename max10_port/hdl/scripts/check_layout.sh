#!/usr/bin/env bash
# Sanity check for the hdl/ Quartus project layout -- no Quartus required.
#
# Mirrors vivado/aging_study_nexys4ddr/scripts/check_layout.sh's pattern.
# Two tiers of requirement, checked separately:
#   1. Tooling files -- must exist now (this scaffold provides them).
#   2. Design files -- expected once fronts F1/F2 deliver real RTL and
#      constraints. Missing design files are reported, not treated as a
#      hard failure, since this script is meant to be run from day one
#      (including before any RTL exists) to confirm the scaffold itself
#      is intact.
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_root="$(cd "$script_dir/.." && pwd)"

tooling_files=(
  "README.md"
  "README.pt-BR.md"
  "scripts/check_layout.sh"
  "scripts/create_project.tcl"
  "scripts/create_project.sh"
  "scripts/build_bitstream.sh"
)

# TODO: once F1/F2 land real files, update these paths to match and move
# any that should be hard requirements up into tooling_files above.
design_files=(
  "src/rtl/top/max10_aging_top.sv"
  "src/constraints/max10_aging.sdc"
  "src/constraints/max10_aging.qsf"
)

missing_tooling=0
for path in "${tooling_files[@]}"; do
  if [[ ! -f "$project_root/$path" ]]; then
    echo "Missing required tooling file: $path" >&2
    missing_tooling=1
  fi
done

if [[ "$missing_tooling" -ne 0 ]]; then
  exit 1
fi

missing_design=0
for path in "${design_files[@]}"; do
  if [[ ! -f "$project_root/$path" ]]; then
    echo "Not yet present (expected once F1/F2 deliver): $path"
    missing_design=1
  fi
done

for shell_script in "$project_root"/scripts/*.sh; do
  bash -n "$shell_script"
done

if command -v quartus_sh >/dev/null 2>&1; then
  quartus_sh --version | head -n1
else
  echo "quartus_sh not found on PATH; source Quartus's environment script before creating or building the project."
fi

echo "Tooling scaffold check passed: $project_root"
if [[ "$missing_design" -ne 0 ]]; then
  echo "(Design files above are still pending -- expected at this stage.)"
fi
