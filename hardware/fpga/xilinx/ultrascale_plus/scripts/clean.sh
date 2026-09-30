#!/usr/bin/env bash
set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

rm -rf "$project_root/build"
rm -rf "$project_root/artifacts"
rm -f "$project_root"/*.jou "$project_root"/*.log "$project_root"/*.str
rm -rf "$project_root/.Xil"

echo "Removed generated Vivado build output from $project_root"
