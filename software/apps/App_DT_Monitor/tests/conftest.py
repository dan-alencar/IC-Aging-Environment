"""Tests run against the fbs submodule's host library (not an installed copy)."""
import os
import sys
from pathlib import Path

APP = Path(__file__).resolve().parents[1]
ROOT = APP.parents[2]
sys.path.insert(0, str(ROOT / "external" / "fpgaging-board-support" / "host" / "python"))
sys.path.insert(0, str(APP))
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
