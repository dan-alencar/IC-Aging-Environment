"""The IC-Aging burn-in as an fbs-service experiment plugin (fbs SPEC §6.2, §9.3).

Registered as the entry point fbs.experiments = ic_aging.burnin. It adds the slack columns
to summary.csv (one set per board), keeps the data-quality counters, checks on every window
that the AGING_CHAIN record of chain 0 equals AGING_WINDOW, configures the payload at the
start of a run, and gives the simulator the aging payload model.

Summary columns per board (empty when there is no data, never 0):
  slack_mean, slack_std, slack_min, slack_max, sweeps, window_id, aging_flags,
  c<j>_slack_mean, c<j>_slack_std for chains 1-8, ref_slack_mean, ref_slack_std,
  ro<r>_hz, lock_loss, missing_windows, chain0_mismatch
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from fpgaging_bsp import protocol as P
from fpgaging_bsp.codec import Frame
from fpgaging_bsp.service.plugins import Experiment
from fpgaging_bsp.service.runplan import RunPlanSequencer

from . import protocol_aging as A
from .stats import window_stats

N_CHAINS, REF = 10, 9

COLUMNS = (["slack_mean", "slack_std", "slack_min", "slack_max", "sweeps", "window_id", "aging_flags"] +
           [f"c{j}_slack_{s}" for j in range(1, REF) for s in ("mean", "std")] +
           ["ref_slack_mean", "ref_slack_std", "ro0_hz", "ro1_hz", "lock_loss", "missing_windows",
            "chain0_mismatch"])

# payload settings for a run: continuous sweeps, 1 s windows, the reference chain and ring
# oscillators measured for 3 windows every minute, histogram of 16 x 8 steps from 300 (300-428)
RUN_MODE = dict(sweep_mode=A.SweepMode.CONTINUOUS, window_ms=1000, periodic=1, ref_period_s=60, ref_windows=3)
RUN_HIST = dict(base=300, bin_width=8)


@dataclass
class BoardQuality:
    windows: int = 0
    missing: int = 0
    mismatch: int = 0
    last_id: Optional[int] = None
    window: Optional[A.AgingWindow] = None
    chains_seen: Dict[int, set] = field(default_factory=dict)


class AgingSequencer(RunPlanSequencer):
    """The generic run plan, with the aging payload configured before the first step."""

    def run(self) -> None:
        for b in self.ctx.boards:
            try:
                self.ctx.request(b, P.Node.FPGA_APP, A.AgingSetHist(**RUN_HIST))
                self.ctx.request(b, P.Node.FPGA_APP, A.AgingSetMode(**RUN_MODE))
            except Exception as e:     # an old bitstream without the payload: record and go on
                self.ctx.log(f"{b}: aging payload not configured ({e})", "warning")
        super().run()


class AgingExperiment(Experiment):
    name = "ic_aging.burnin"
    columns = COLUMNS
    sequencer = AgingSequencer

    def __init__(self):
        self.q: Dict[str, BoardQuality] = {}

    def derive(self, board: str, f: Frame) -> Optional[Dict[str, Any]]:
        if f.src != P.Node.FPGA_APP:
            return None
        q = self.q.setdefault(board, BoardQuality())
        m = f.msg
        if isinstance(m, A.AgingWindow):
            if q.last_id is not None and m.window_id > q.last_id + 1:
                q.missing += m.window_id - q.last_id - 1
            q.last_id = m.window_id
            q.windows += 1
            q.window = m
            mean, std = window_stats(m.sweeps, m.sum, m.sumsq)
            return {"slack_mean": None if mean is None else round(mean, 4),
                    "slack_std": None if std is None else round(std, 4),
                    "slack_min": m.min if m.sweeps else None, "slack_max": m.max if m.sweeps else None,
                    "sweeps": m.sweeps, "window_id": m.window_id, "aging_flags": int(m.flags),
                    "lock_loss": m.lock_loss, "missing_windows": q.missing}
        if isinstance(m, A.AgingChain):
            mean, std = window_stats(m.sweeps, m.sum, m.sumsq)
            if m.chain == 0:
                w = q.window
                if w is None or w.window_id != m.window_id or \
                        (w.sweeps, w.last, w.min, w.max, w.sum, w.sumsq) != \
                        (m.sweeps, m.last, m.min, m.max, m.sum, m.sumsq):
                    q.mismatch += 1
                return {"chain0_mismatch": q.mismatch}
            key = "ref" if m.chain == REF else f"c{m.chain}"
            return {f"{key}_slack_mean": None if mean is None else round(mean, 4),
                    f"{key}_slack_std": None if std is None else round(std, 4)}
        if isinstance(m, A.AgingRo):
            ms = m.window_ms or 1
            return {f"ro{r}_hz": round(m.counts[r].count * 1000.0 / ms, 1) for r in range(min(m.n_ro, 2))}
        return None

    def app_model(self, index: int):
        from .sim_app import AgingAppModel
        return AgingAppModel(index)


def experiment() -> AgingExperiment:
    """Entry-point target (fbs.experiments: ic_aging.burnin)."""
    return AgingExperiment()
