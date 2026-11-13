"""pytest entry for the fbs_aging_top simulation (cocotb + Verilator).

    make -C hardware/fpga/xilinx/ultrascale_plus sim
Needs Verilator >= 5.036 and cocotb >= 2.0 (the fbs submodule's .venv has both).
"""
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

import pytest

runner = pytest.importorskip("cocotb_tools.runner")

HERE = Path(__file__).resolve().parent
TOP = HERE.parent                                   # hardware/fpga/xilinx/ultrascale_plus
ROOT = TOP.parents[3]
FBS = ROOT / "external" / "fpgaging-board-support" / "fpga"
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))


def files(base: Path, flist: Path):
    return [base / ln.strip() for ln in flist.read_text().splitlines() if ln.strip() and not ln.startswith("//")]


PARAMS = {"CLK_FREQ_HZ": 4_000_000, "BAUD": 250_000, "REF_UNIT_MS": 50, "WINDOW_MS": 100,
          "INFO_PERIOD_MS": 60_000, "SYSMON_AVG_LOG2": 4}


def test_fbs_aging_top():
    if shutil.which(os.environ.get("VERILATOR", "verilator")) is None:
        pytest.skip("verilator not on PATH")
    srcs = files(FBS, FBS / "rtl" / "files.f") + [FBS / "sim" / "fbs_sysmon_model.sv"] + \
        files(TOP, TOP / "src" / "rtl" / "fbs_aging" / "files.f")
    r = runner.get_runner("verilator")
    build = HERE / "build"
    r.build(sources=srcs, hdl_toplevel="fbs_aging_top", parameters=PARAMS, build_dir=build,
            build_args=[str(FBS / "verilator.vlt"), "-Wno-fatal", "--timescale", "1ns/1ps"],
            waves=bool(os.environ.get("WAVES")), always=True)
    xml = r.test(hdl_toplevel="fbs_aging_top", test_module="test_fbs_aging", build_dir=build, test_dir=build,
                 waves=bool(os.environ.get("WAVES")), testcase=os.environ.get("TESTCASE"))
    n, failed = runner.get_results(xml)
    assert n > 0 and failed == 0, f"{failed} of {n} cocotb tests failed, see {xml}"
