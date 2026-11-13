#!/usr/bin/env bash
# Every check of the fbs-based parts of this repository (no hardware needed):
#   bindings current, RTL lint and simulation, App_DT_Monitor tests, analysis self-test.
# Uses the Python of $PY, or the fbs submodule's .venv, or App_DT_Monitor/.venv, or python3; Verilator >= 5.036 and
# cocotb >= 2.0 for the RTL (skipped if missing).
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
fbs="$root/external/fpgaging-board-support"
app_venv="$root/software/apps/App_DT_Monitor/.venv/bin/python"
py="${PY:-$( [ -x "$fbs/.venv/bin/python" ] && echo "$fbs/.venv/bin/python" || { [ -x "$app_venv" ] && echo "$app_venv"; } || echo python3 )}"
top="$root/hardware/fpga/xilinx/ultrascale_plus"
export QT_QPA_PLATFORM=offscreen
[ -d "$HOME/eda/oss-cad-suite/bin" ] && export PATH="$HOME/eda/oss-cad-suite/bin:$PATH"

echo "== generated bindings"
"$py" "$root/protocol/generate.py" --check
if command -v verilator >/dev/null; then
  echo "== RTL lint (Verilator -Wall)"
  plat=$(grep -v '^//' "$fbs/fpga/rtl/files.f" | sed "s#^#$fbs/fpga/#")
  aging=$(grep -v '^//' "$top/src/rtl/fbs_aging/files.f" | sed "s#^#$top/#")
  verilator --lint-only -Wall "$fbs/fpga/verilator.vlt" $plat "$fbs/fpga/sim/fbs_sysmon_model.sv" $aging \
    --top-module fbs_aging_top
fi
echo "== RTL simulation, App_DT_Monitor, analysis"
"$py" -m pytest -q "$top/sim/test_rtl.py" "$root/software/apps/App_DT_Monitor/tests" "$root/analysis/dt2027"
