#!/usr/bin/env bash
# Write src/constraints/fbs_aging_fixed_pnr.xdc from a routed checkpoint of fbs_aging_top (V19).
#
#   scripts/extract_fbs_aging_pnr.sh [ROUTED.dcp]     default: build/fbs_aging_ref/fbs_aging_top_routed.dcp
#
# The usual sequence, when the aged logic (src/rtl/fbs_aging/aging_fabric.sv, the chain list, the
# clocks) changes and a new placement has to be frozen:
#   FBS_AGING_FREE_PNR=1 scripts/build_fbs_aging.sh build/fbs_aging_ref   # reference, free placement
#   scripts/extract_fbs_aging_pnr.sh                                       # freeze it
#   scripts/build_fbs_aging.sh                                             # fixed build
#   (the fixed build compares its chains.txt with src/constraints/fbs_aging_fixed_pnr_chains.txt
#    and fails if they differ)
# A new placement means new baselines: never re-extract in the middle of a campaign.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
vivado="${VIVADO_BIN:-vivado}"
dcp="$(realpath "${1:-$here/../build/fbs_aging_ref/fbs_aging_top_routed.dcp}")"
xdc="$here/../src/constraints/fbs_aging_fixed_pnr.xdc"
[ -f "$dcp" ] || { echo "no checkpoint: $dcp" >&2; exit 2; }
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
cat > "$tmp/extract.tcl" <<TCL
source {$here/fbs_aging_pnr.tcl}
open_checkpoint {$dcp}
fbs_aging_write_fixed_xdc {$xdc}
fbs_aging_report_chains {$tmp/chains.txt}
TCL
(cd "$tmp" && "$vivado" -mode batch -nojournal -log "$tmp/vivado.log" -source "$tmp/extract.tcl" >/dev/null) ||
  { tail -30 "$tmp/vivado.log" >&2; exit 1; }
cp "$tmp/chains.txt" "$here/../src/constraints/fbs_aging_fixed_pnr_chains.txt"   # what every fixed build must reproduce
echo "wrote $xdc ($(wc -c <"$xdc") bytes) from $dcp"
cat "$tmp/chains.txt"
