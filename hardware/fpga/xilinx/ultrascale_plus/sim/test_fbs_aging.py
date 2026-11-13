"""cocotb tests of fbs_aging_top: the fbs platform plus the IC-Aging payload, driven through J9.

The fabric model alarms chain i once the phase has moved back sim_slack[i] steps (+-1 at
random; a sweep keeps the earliest alarm, so means sit up to one step below the slack) and the ring oscillators count sim_ro_rate[r]/256 edges per clock. The top runs at
4 MHz with the UART at 250 kBd and ref_period_s in units of 50 ms, so windows of 100 ms hold a
few hundred sweeps and the tests stay short.
"""
from __future__ import annotations

import sys
from pathlib import Path

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT / "external" / "fpgaging-board-support" / "fpga" / "sim"))
sys.path.insert(0, str(ROOT / "software" / "apps" / "App_DT_Monitor"))

from fbs_tb import P, UartRx, UartTx, encode  # noqa: E402
from dt_monitor import protocol_aging as A  # noqa: E402  (registers the AGING_* messages)

CLK_HZ = 4_000_000
BAUD = 250_000
MS = CLK_HZ // 1000
N = P.Node
SLACK = [40, 60, 55, 38, 20, 50, 38, 30, 21, 42]   # chain 9 is the reference


def pack16(vals):
    v = 0
    for i, x in enumerate(vals):
        v |= (x & 0xFFFF) << (16 * i)
    return v


class Bench:
    def __init__(self, dut):
        self.dut = dut
        self.clk = dut.sys_clk_p
        self.pc = UartRx(dut.fpga_uart_tx, BAUD, "pc")
        self.stm = UartRx(dut.mcu_usart1_rx, BAUD, "stm")
        self.tx = UartTx(dut.fpga_uart_rx, BAUD)
        self.seq = 0

    async def cmd(self, msg, dst=N.FPGA_APP, reply_type=None, timeout_ms=40):
        self.seq = (self.seq + 1) & 0xFF
        seq = self.seq
        await self.tx.send(encode(0, int(dst), msg.TYPE, seq, msg.pack()))
        want = reply_type or P.Ack.TYPE

        def match(f):
            if f.type != want or not f.is_reply or f.src != dst:
                return False
            return want != P.Ack.TYPE or (f.msg.ref_type == msg.TYPE and f.msg.ref_seq == seq)
        return (await self.pc.wait_for(match, self.clk, timeout_ms * MS)).msg

    def of(self, cls, after=0):
        return [f.msg for f in self.pc.frames[after:] if f.type == cls.TYPE and f.src == N.FPGA_APP]

    async def windows(self, n, after=None, timeout_ms=2000):
        start = len(self.pc.frames) if after is None else after
        for _ in range(timeout_ms // 10):
            if len(self.of(A.AgingWindow, start)) >= n:
                await ClockCycles(self.clk, 40 * MS)      # its AGING_CHAIN/RO frames follow
                return start
            await ClockCycles(self.clk, 10 * MS)
        raise AssertionError(f"fewer than {n} AGING_WINDOW frames")


async def start(dut, slack=SLACK, ro=(300, 200)):
    cocotb.start_soon(Clock(dut.sys_clk_p, 250, unit="ns").start())
    dut.sys_clk_n.value = 0
    dut.fpga_uart_rx.value = 1
    dut.mcu_usart1_tx.value = 1
    dut.fpga_button.value = 0
    dut.i2c_ac13_i.value = 1
    dut.i2c_ac14_i.value = 1
    dut.sim_slack_i.value = pack16(slack)
    dut.sim_ro_rate_i.value = pack16(ro)
    b = Bench(dut)
    await ClockCycles(b.clk, 5 * MS)
    return b


def stats(m):
    mean = m.sum / m.sweeps
    var = m.sumsq / m.sweeps - mean * mean
    return mean, var


@cocotb.test()
async def info_and_commands(dut):
    b = await start(dut)
    info = (await b.pc.wait_for(lambda f: f.type == A.AgingInfo.TYPE, b.clk, 20 * MS)).msg
    assert info.n_chains == 10 and info.ps_step_fs == 19841 and info.max_steps == 504
    assert info.rtl_version == A.AGING_RTL_VERSION and info.n_ro == 2
    assert [c.kind for c in info.chains] == [A.ChainKind.INFERRED] + [A.ChainKind.CARRY8] * 4 + \
        [A.ChainKind.LUT] * 4 + [A.ChainKind.REFERENCE]
    assert [c.size for c in info.chains] == [256, 128, 256, 512, 1024, 8, 16, 24, 32, 256]
    assert [c.stressed for c in info.chains] == [1] * 9 + [0]
    pong = await b.cmd(P.Ping(nonce=0xCAFEF00D), reply_type=P.Pong.TYPE)
    assert pong.nonce == 0xCAFEF00D
    i = await b.cmd(P.GetInfo(), reply_type=P.Info.TYPE)
    assert i.name == "ic-aging-app" and i.fw_version == A.AGING_RTL_VERSION
    plat = await b.cmd(P.GetInfo(), dst=N.FPGA_PLATFORM, reply_type=P.Info.TYPE)
    assert plat.device_id.hex().upper() == "40020000016069492D020185"
    assert (await b.cmd(A.AgingGetInfo(), reply_type=A.AgingInfo.TYPE)).n_chains == 10
    # wrong length, unknown type, bad values
    b.seq += 1
    await b.tx.send(encode(0, int(N.FPGA_APP), A.AgingSetHist.TYPE, b.seq, b"\x01"))
    f = await b.pc.wait_for(lambda f: f.type == P.Ack.TYPE and f.msg.ref_seq == b.seq, b.clk, 40 * MS)
    assert f.msg.status == P.AckStatus.BAD_LEN
    b.seq += 1
    await b.tx.send(encode(0, int(N.FPGA_APP), 0x5F, b.seq, b""))
    f = await b.pc.wait_for(lambda f: f.type == P.Ack.TYPE and f.msg.ref_seq == b.seq, b.clk, 40 * MS)
    assert f.msg.status == P.AckStatus.UNKNOWN_TYPE
    a = await b.cmd(A.AgingSetMode(sweep_mode=1, window_ms=50, periodic=1, ref_period_s=0, ref_windows=0))
    assert a.status == P.AckStatus.OUT_OF_RANGE
    a = await b.cmd(A.AgingSetHist(base=10, bin_width=0))
    assert a.status == P.AckStatus.OUT_OF_RANGE
    # replies to replies are never sent
    n = len(b.pc.frames)
    await b.tx.send(encode(0, int(N.FPGA_APP), P.Ping.TYPE, 99, P.Ping(nonce=1).pack(), is_reply=True))
    await ClockCycles(b.clk, 20 * MS)
    assert not [f for f in b.pc.frames[n:] if f.type == P.Pong.TYPE]


@cocotb.test()
async def windows_chains_histogram(dut):
    b = await start(dut)
    a = await b.cmd(A.AgingSetHist(base=36, bin_width=2))
    assert a.status == P.AckStatus.OK
    a = await b.cmd(A.AgingSetMode(sweep_mode=1, window_ms=100, periodic=1, ref_period_s=0, ref_windows=0))
    assert a.status == P.AckStatus.OK
    s = await b.windows(3)
    ws = b.of(A.AgingWindow, s)
    for w in ws[1:3]:                                    # whole windows after the mode change
        assert w.sweeps > 100, w.sweeps
        mean, var = stats(w)
        assert SLACK[0] - 1 < mean <= SLACK[0] and var < 1.0, (mean, var)
        assert SLACK[0] - 1 <= w.min <= w.max <= SLACK[0] + 1
        assert sum(h.n for h in w.hist) == w.sweeps
        # bins of width 2 from 36: 39 -> bin 1, 40/41 -> bin 2
        assert sum(h.n for h in w.hist[1:3]) == w.sweeps
        assert w.sweep_mode == A.SweepMode.CONTINUOUS
        assert not (w.flags & (A.AgingFlags.NO_ALARM | A.AgingFlags.PS_TIMEOUT | A.AgingFlags.MEASURE_WINDOW))
        chains = [c for c in b.of(A.AgingChain, s) if c.window_id == w.window_id]
        assert [c.chain for c in chains] == list(range(9))  # no reference outside measurement windows
        c0 = chains[0]
        assert (c0.sweeps, c0.last, c0.min, c0.max, c0.sum, c0.sumsq) == \
               (w.sweeps, w.last, w.min, w.max, w.sum, w.sumsq)  # chain 0 equals AGING_WINDOW
        for c in chains:
            assert SLACK[c.chain] - 1 < c.sum / c.sweeps <= SLACK[c.chain], (c.chain, c.sum / c.sweeps)
            assert c.stressed == 1
    assert ws[1].window_id == ws[0].window_id + 1
    assert ws[0].flags & A.AgingFlags.PARTIAL


@cocotb.test()
async def reference_chain_and_ring_oscillators(dut):
    b = await start(dut, ro=(512, 128))
    # 'seconds' are 50 ms here: every 2 units (100 ms) measure 1 window of 50 ms... use 100 ms windows
    a = await b.cmd(A.AgingSetMode(sweep_mode=1, window_ms=100, periodic=1, ref_period_s=4, ref_windows=1))
    assert a.status == P.AckStatus.OK
    s = await b.windows(6, timeout_ms=3000)
    ws = b.of(A.AgingWindow, s)
    meas = [w for w in ws if w.flags & A.AgingFlags.MEASURE_WINDOW]
    plain = [w for w in ws if not w.flags & A.AgingFlags.MEASURE_WINDOW]
    assert meas and plain
    for w in meas:
        chains = {c.chain: c for c in b.of(A.AgingChain, s) if c.window_id == w.window_id}
        assert 9 in chains and chains[9].stressed == 0 and chains[9].kind == A.ChainKind.REFERENCE
        assert SLACK[9] - 1 < chains[9].sum / chains[9].sweeps <= SLACK[9]
        ros = [r for r in b.of(A.AgingRo, s) if r.window_id == w.window_id]
        assert len(ros) == 1 and ros[0].n_ro == 2
        cyc = ros[0].window_ms * MS
        assert abs(ros[0].counts[0].count - 2 * cyc) <= 2 * MS + 4, (ros[0].counts[0].count, cyc)
        assert abs(ros[0].counts[1].count - cyc // 2) <= MS + 4
    for w in plain:
        assert not [c for c in b.of(A.AgingChain, s) if c.window_id == w.window_id and c.chain == 9]
        assert not [r for r in b.of(A.AgingRo, s) if r.window_id == w.window_id]


@cocotb.test()
async def single_mode_aging_and_no_alarm(dut):
    b = await start(dut)
    a = await b.cmd(A.AgingSetMode(sweep_mode=2, window_ms=100, periodic=1, ref_period_s=0, ref_windows=0))
    assert a.status == P.AckStatus.OK
    s = await b.windows(3)
    w = [x for x in b.of(A.AgingWindow, s) if not x.flags & A.AgingFlags.PARTIAL][-1]
    assert w.sweeps == 1 and w.sweep_mode == A.SweepMode.SINGLE
    # aging: the slack shrinks, the sensor follows
    await b.cmd(A.AgingSetMode(sweep_mode=1, window_ms=100, periodic=1, ref_period_s=0, ref_windows=0))
    dut.sim_slack_i.value = pack16([35] + SLACK[1:])
    s = await b.windows(2)
    w = b.of(A.AgingWindow, s)[1]
    assert 34 < stats(w)[0] <= 35
    # a chain that never alarms: max_steps and NO_ALARM
    dut.sim_slack_i.value = pack16([600] + SLACK[1:])
    s = await b.windows(2, timeout_ms=3000)
    w = b.of(A.AgingWindow, s)[1]
    assert w.flags & A.AgingFlags.NO_ALARM and w.max == 504 and w.sweeps >= 1
    # the other chains are unaffected
    c3 = [c for c in b.of(A.AgingChain, s) if c.window_id == w.window_id and c.chain == 3][0]
    assert SLACK[3] - 1 < c3.sum / c3.sweeps <= SLACK[3]
    assert b.pc.framing_errors == 0
