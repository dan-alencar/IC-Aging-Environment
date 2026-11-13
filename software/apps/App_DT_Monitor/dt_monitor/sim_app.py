"""The IC-Aging payload, simulated, for fbs sim (fbs SPEC §9.9).

AgingAppModel plugs into fpgaging_bsp.sim as the FPGA_APP node. It sends the same frames
as fbs_aging_top (AGING_WINDOW, AGING_CHAIN, AGING_RO, AGING_INFO) and answers the same
commands, with the slack from the colleague's model (fpgaging_bsp.sim.models.SlackModel):
nine stressed chains plus a reference chain like chain 0 that ages only while measured.
Ring oscillators slow down with die temperature (about -0.15 %/degC from 250 MHz).
"""
from __future__ import annotations

import math
from typing import List

from fpgaging_bsp import protocol as P
from fpgaging_bsp.codec import Frame
from fpgaging_bsp.sim.board import AppModel, SimBoard
from fpgaging_bsp.sim.models import SlackModel

from . import protocol_aging as A

KINDS = [A.ChainKind.INFERRED] + [A.ChainKind.CARRY8] * 4 + [A.ChainKind.LUT] * 4 + [A.ChainKind.REFERENCE]
SIZES = [256, 128, 256, 512, 1024, 8, 16, 24, 32, 256]
N, REF, N_RO = 10, 9, 2
MAX_STEPS = 504
RO_HZ = (250e6, 180e6)


class AgingAppModel(AppModel):
    name = "ic-aging-app"

    def __init__(self, index: int = 0):
        self.window_ms = 1000
        self.mode = A.SweepMode.CONTINUOUS
        self.periodic = 1
        self.ref_period_s = 60
        self.ref_windows = 3
        self.hist_base, self.hist_width = 300, 16
        self.window_id = 0
        self.t_win = 0.0
        self.t_ref = 0.0
        self.meas_left = 0
        self.measure = False
        self.partial = False
        self.info_due = True
        self.t_info = 0.0
        self.ref = SlackModel(s0=320.0 + 6.0 * index, chains=[("INFERRED", 256, 0.0, 3.570)])

    # ------------------------------------------------------------------ commands
    def on_frame(self, board: SimBoard, f: Frame) -> List:
        if f.is_reply:
            return []
        try:
            m = f.msg
        except ValueError:
            return [(f.src, P.Ack(ref_type=f.type, ref_seq=f.seq, status=P.AckStatus.BAD_LEN))]
        ack = lambda st=P.AckStatus.OK: [(f.src, P.Ack(ref_type=f.type, ref_seq=f.seq, status=int(st)))]  # noqa: E731
        if isinstance(m, P.Ping):
            return [(f.src, P.Pong(nonce=m.nonce, uptime_ms=board.now_ms & 0xFFFFFFFF))]
        if isinstance(m, P.GetInfo):
            return [(f.src, P.Info(proto_major=P.PROTO_MAJOR, proto_minor=P.PROTO_MINOR,
                                   fw_version=A.AGING_RTL_VERSION, clock_source=P.ClockSource.FPGA_BOARD,
                                   name=self.name))]
        if isinstance(m, A.AgingGetInfo):
            return [(f.src, self._info())]
        if isinstance(m, A.AgingSetMode):
            ok = (m.sweep_mode <= 2 and A.AGING_WINDOW_MS_MIN <= m.window_ms <= A.AGING_WINDOW_MS_MAX
                  and m.periodic <= 1 and not (m.ref_period_s and not m.ref_windows))
            if not ok:
                return ack(P.AckStatus.OUT_OF_RANGE)
            self.mode, self.window_ms, self.periodic = A.SweepMode(m.sweep_mode), m.window_ms, m.periodic
            self.ref_period_s, self.ref_windows = m.ref_period_s, m.ref_windows
            self.partial = True
            return ack()
        if isinstance(m, A.AgingSetHist):
            if m.bin_width == 0:
                return ack(P.AckStatus.OUT_OF_RANGE)
            self.hist_base, self.hist_width = m.base, m.bin_width
            self.partial = True
            return ack()
        return ack(P.AckStatus.UNKNOWN_TYPE)

    def _info(self) -> A.AgingInfo:
        return A.AgingInfo(rtl_version=A.AGING_RTL_VERSION, window_ms=self.window_ms, ps_step_fs=19841,
                           max_steps=MAX_STEPS, sweep_mode=self.mode, periodic=self.periodic,
                           ref_period_s=self.ref_period_s, ref_windows=self.ref_windows,
                           hist_base=self.hist_base, hist_bin_width=self.hist_width, n_chains=N,
                           chains=[A.AgingInfoChainsItem(kind=k, size=s, stressed=int(i != REF))
                                   for i, (k, s) in enumerate(zip(KINDS, SIZES))], n_ro=N_RO)

    # ------------------------------------------------------------------ windows
    def tick(self, board: SimBoard, dt_s: float) -> List:
        out = []
        self.t_info += dt_s
        if self.info_due or self.t_info >= 60.0:
            self.info_due, self.t_info = False, 0.0
            out.append((P.Node.HOST, self._info()))
        if not board.powered:
            return out
        if self.measure:
            self.ref.age(dt_s, True)
        self.t_win += dt_s
        self.t_ref += dt_s
        if self.t_win * 1000.0 + 1e-6 < self.window_ms:
            return out
        win_s, self.t_win = self.t_win, 0.0
        if self.mode != A.SweepMode.OFF and self.periodic:
            out += self._window(board, win_s)
        self.window_id += 1
        self.partial = False
        if self.meas_left:
            self.meas_left -= 1
            self.measure = True
        elif self.ref_period_s and self.ref_windows and self.t_ref >= self.ref_period_s:
            self.t_ref = 0.0
            self.meas_left = self.ref_windows - 1
            self.measure = True
        else:
            self.measure = False
        return out

    @staticmethod
    def _stat(w, n_max: int):
        return dict(sweeps=min(w.n, 0xFFFF), last=min(w.last, MAX_STEPS), min=min(w.min, MAX_STEPS),
                    max=min(w.max, MAX_STEPS), sum=w.sum & 0xFFFFFFFF, sumsq=w.sumsq)

    def _window(self, board: SimBoard, win_s: float) -> List:
        rng = board.rng
        die, v = board.die.temp_c, board.vccint_v + board.faults.sysmon_vccint_offset_mv / 1000.0
        sweeps = 1 if self.mode == A.SweepMode.SINGLE else max(1, int(rng.gauss(9000, 40) * win_s))
        ws = board.slack.window(rng, die, v, sweeps=sweeps)
        flags = 0
        if self.measure:
            flags |= A.AgingFlags.MEASURE_WINDOW
        if self.partial:
            flags |= A.AgingFlags.PARTIAL
        w0 = ws[0]
        if w0.n >= 2 and w0.min == w0.max:
            flags |= A.AgingFlags.STUCK
        # histogram of chain 0, from its mean and spread
        hist = [0] * 16
        mean = w0.sum / w0.n
        sd = max(0.3, math.sqrt(max(0.0, w0.sumsq / w0.n - mean * mean)))
        for k in range(16):
            lo = self.hist_base + k * self.hist_width if k else -1e9
            hi = self.hist_base + (k + 1) * self.hist_width if k < 15 else 1e9
            p = 0.5 * (math.erf((hi - mean) / (sd * math.sqrt(2))) - math.erf((lo - mean) / (sd * math.sqrt(2))))
            hist[k] = int(round(p * w0.n))
        hist[max(range(16), key=lambda k: hist[k])] += w0.n - sum(hist)
        out = [(P.Node.HOST, A.AgingWindow(
            t_ms=board.now_ms & 0xFFFFFFFF, window_id=self.window_id, hist=[A.AgingWindowHistItem(n=max(0, h)) for h in hist],
            lock_loss=0, sweep_mode=self.mode, flags=flags, **self._stat(w0, sweeps)))]
        for i, w in enumerate(ws):
            out.append((P.Node.HOST, A.AgingChain(window_id=self.window_id, chain=i, kind=KINDS[i], size=SIZES[i],
                                                  stressed=1, **self._stat(w, sweeps))))
        if self.measure:
            r = self.ref.window(rng, die, v, sweeps=sweeps)[0]
            out.append((P.Node.HOST, A.AgingChain(window_id=self.window_id, chain=REF, kind=KINDS[REF],
                                                  size=SIZES[REF], stressed=0, **self._stat(r, sweeps))))
            counts = [int(f0 * (1.0 - 0.0015 * (die - 25.0)) * win_s) for f0 in RO_HZ]
            out.append((P.Node.HOST, A.AgingRo(window_id=self.window_id, window_ms=int(round(win_s * 1000)),
                                               n_ro=N_RO, counts=[A.AgingRoCountsItem(count=c & 0xFFFFFFFF)
                                                                  for c in counts + [0, 0]])))
        return out
