#!/usr/bin/env python3
"""Generate the IC-Aging application bindings from protocol/messages.icaging.yaml.

Runs the fbs generator (external/fpgaging-board-support) and places its outputs:
    software/apps/App_DT_Monitor/dt_monitor/protocol_aging.py
    hardware/fpga/xilinx/ultrascale_plus/src/rtl/fbs_aging/fbs_aging_pkg.sv
    protocol/MESSAGES_aging.md
Usage: python3 protocol/generate.py [--check]
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FBS = ROOT / "external" / "fpgaging-board-support"
DEST = {
    "protocol_aging.py": ROOT / "software/apps/App_DT_Monitor/dt_monitor/protocol_aging.py",
    "fbs_aging_pkg.sv": ROOT / "hardware/fpga/xilinx/ultrascale_plus/src/rtl/fbs_aging/fbs_aging_pkg.sv",
    "MESSAGES_aging.md": ROOT / "protocol/MESSAGES_aging.md",
}


def main() -> int:
    check = "--check" in sys.argv[1:]
    with tempfile.TemporaryDirectory() as td:
        r = subprocess.run([sys.executable, str(FBS / "tools/gen_protocol.py"), "--app",
                            str(ROOT / "protocol/messages.icaging.yaml"), "--prefix", "aging", "--out", td],
                           capture_output=True, text=True)
        if r.returncode:
            sys.stderr.write(r.stderr)
            return r.returncode
        stale = 0
        for name, dst in DEST.items():
            new = (Path(td) / name).read_text()
            if dst.exists() and dst.read_text() == new:
                continue
            if check:
                print(f"stale: {dst.relative_to(ROOT)}", file=sys.stderr)
                stale += 1
            else:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(Path(td) / name, dst)
                print(f"wrote {dst.relative_to(ROOT)}")
    return 1 if stale else 0


if __name__ == "__main__":
    sys.exit(main())
