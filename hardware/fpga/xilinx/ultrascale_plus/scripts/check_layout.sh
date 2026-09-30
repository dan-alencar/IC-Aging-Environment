#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_root="$(cd "$script_dir/.." && pwd)"

required_files=(
  "README.md"
  "docs/SOURCE_MANIFEST.md"
  "scripts/create_project.sh"
  "scripts/create_project.tcl"
  "scripts/build_bitstream.sh"
  "scripts/build_bitstream.tcl"
  "scripts/clean.sh"
  "scripts/check_layout.sh"
  "src/constraints/fpga_aging_constraints.xdc"
  "src/ip/clk_wiz_0/clk_wiz_0.xci"
  "src/ip/vio_0/vio_0.xci"
  "src/ip/xadc_wiz_0/xadc_wiz_0.xci"
  "src/rtl/aging_sensor/controller_controller.v"
  "src/rtl/aging_sensor/modern_sensible.v"
  "src/rtl/aging_sensor/nand_series.v"
  "src/rtl/monitor/sysmon_monitor.sv"
  "src/rtl/top/fpga_unified_top.sv"
  "src/rtl/uart/sensor_stream.v"
  "src/rtl/uart/uart_arbiter.sv"
  "src/rtl/uart/uart_router.sv"
  "src/rtl/uart/uart_tx.v"
)

missing=0
for path in "${required_files[@]}"; do
  if [[ ! -f "$project_root/$path" ]]; then
    echo "Missing required file: $path" >&2
    missing=1
  fi
done

if [[ "$missing" -ne 0 ]]; then
  exit 1
fi

for shell_script in "$project_root"/scripts/*.sh; do
  bash -n "$shell_script"
done

if command -v vivado >/dev/null 2>&1; then
  vivado -version | sed -n '1p'
else
  echo "Vivado executable not found on PATH; source settings64.sh before creating or building the project."
fi

echo "Vivado project layout check passed: $project_root"
