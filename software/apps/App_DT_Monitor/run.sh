#!/usr/bin/env bash
# App_DT_Monitor launcher. Uses ./.venv (created on first use with the fbs submodule and
# this package installed in editable mode).
#   ./run.sh                 window for the lab bench (starts the service if it is not running)
#   ./run.sh sim             service + window on the simulator
#   ./run.sh service         only the service for the lab bench
#   ./run.sh <dt-monitor command> [...]   corners, oven-test, check-board, gui
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
root="$(cd "$here/../../.." && pwd)"
venv="$here/.venv"
if [ ! -x "$venv/bin/python" ]; then
  python3 -m venv "$venv"
  "$venv/bin/pip" install -q -e "$root/external/fpgaging-board-support/host/python[qt]" -e "$here[dev]"
fi
py="$venv/bin/python"
sock_of() { echo "${XDG_RUNTIME_DIR:-/tmp/fbs-$(id -u)}/fbs/$1.sock"; }
start_service() {   # $1 bench name, $2 config
  if [ ! -S "$(sock_of "$1")" ]; then
    (cd "$here" && setsid "$py" -m dt_monitor service --config "$2" >"$here/service_$1.log" 2>&1 &)
    for _ in $(seq 50); do [ -S "$(sock_of "$1")" ] && break; sleep 0.2; done
  fi
}
case "${1:-}" in
  "")      start_service rv02a "$here/bench/rv02a_lab.yaml"; exec "$py" -m dt_monitor gui rv02a ;;
  sim)     start_service sim "$here/bench/sim.yaml"; exec "$py" -m dt_monitor gui sim ;;
  service) cd "$here" && exec "$py" -m dt_monitor service --config "$here/bench/rv02a_lab.yaml" ;;
  *)       exec "$py" -m dt_monitor "$@" ;;
esac
