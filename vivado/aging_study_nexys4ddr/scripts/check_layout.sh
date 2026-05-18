#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_root="$(cd "$script_dir/.." && pwd)"

# Pure-RTL project — no block design.
required_files=(
  "README.md"
  "docs/SOURCE_MANIFEST.md"
  "scripts/create_project.sh"
  "scripts/create_project.tcl"
  "scripts/build_bitstream.sh"
  "scripts/build_bitstream.tcl"
  "scripts/clean.sh"
  "scripts/check_layout.sh"
  "scripts/extract_fixed_pnr_constraints.sh"
  "scripts/extract_fixed_pnr_constraints.tcl"
  "references/README.md"
  "references/fixed_pnr.dcp"
  "src/ip/clk_wiz_0/clk_wiz_0.xci"
  "src/constraints/Nexys-4-DDR-Master.xdc"
  "src/constraints/fixed_pnr_constraints.xdc"
  "src/rtl/top/nexys4_aging_top.sv"
  "src/rtl/aging_sensor/adder_canary.sv"
  "src/rtl/aging_sensor/controller_controller.sv"
  "src/rtl/aging_sensor/failure_holder.sv"
  "src/rtl/aging_sensor/lut_full_adder.sv"
  "src/rtl/aging_sensor/modern_sensible.sv"
  "src/rtl/aging_sensor/ripple_adder.sv"
  "src/rtl/aging_sensor/temp_catcher.sv"
  "src/rtl/display/BINtoBCD.sv"
  "src/rtl/display/DisplayController.sv"
  "src/rtl/uart/sensor_stream.sv"
  "src/rtl/uart/uart_tx.sv"
)

missing=0
for path in "${required_files[@]}"; do
  if [[ ! -f "$project_root/$path" ]]; then
    echo "Missing required file: $path" >&2
    missing=1
  fi
done

if [[ -d "$project_root/src/bd" ]]; then
  echo "Unexpected src/bd/ directory found — block design was removed in the pure-RTL revamp." >&2
  missing=1
fi

if [[ "$missing" -ne 0 ]]; then
  exit 1
fi

for shell_script in "$project_root"/scripts/*.sh; do
  bash -n "$shell_script"
done

if find "$project_root" -name '*.dcp' ! -path "$project_root/references/fixed_pnr.dcp" -print -quit | grep -q .; then
  echo "Unexpected .dcp checkpoint found in clean project tree." >&2
  echo "Only references/fixed_pnr.dcp is allowed; build checkpoints live under build/ (gitignored)." >&2
  exit 1
fi

if command -v vivado >/dev/null 2>&1; then
  vivado -version | sed -n '1p'
else
  echo "Vivado executable not found on PATH; source settings64.sh before creating or building the project."
fi

echo "Vivado project layout check passed: $project_root"
