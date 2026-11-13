"""App_DT_Monitor: statistics, experiment plugin, oven driver, scripts, service runs, GUI."""
import csv
import math
import queue
import time
from pathlib import Path

import pytest

from fpgaging_bsp import protocol as P
from fpgaging_bsp.codec import Frame
from fpgaging_bsp.service import BenchConfig, Service, ServiceClient
from fpgaging_bsp.service.oven import OvenError, SimOven
from fpgaging_bsp.sim import OvenAscii, OvenModel, Simulation, load_core

from dt_monitor import protocol_aging as A
from dt_monitor.experiment import COLUMNS, AgingExperiment
from dt_monitor.oven import AsciiOven
from dt_monitor.sim_app import AgingAppModel
from dt_monitor.stats import EquivalentHours, Trend, acceleration_factor, window_stats

needs_core = pytest.mark.skipif(load_core() is None, reason="firmware core library not available")
APP = Path(__file__).resolve().parents[1]
EXP = "dt_monitor.experiment:experiment"


def test_message_sizes():
    assert len(A.AgingWindow().pack()) == 64
    assert len(A.AgingChain().pack()) == 29
    assert len(A.AgingInfo().pack()) == 60
    assert A.AgingSetMode.TYPE == 0x50 and A.AgingGetInfo.REPLY == "AGING_INFO"


def test_stats():
    assert window_stats(0, 0, 0) == (None, None)
    m, s = window_stats(4, 4 * 400, 4 * 400 * 400 + 4)
    assert m == 400 and s == pytest.approx(1.0)
    assert acceleration_factor(55.0) == pytest.approx(1.0)
    assert acceleration_factor(115.0) == pytest.approx(math.exp(0.7 / 8.617333262e-5 * (1 / 328.15 - 1 / 388.15)))
    t = Trend(span_s=1e9)
    for h in range(10):
        t.add(h * 3600.0, 400.0 - 0.5 * h)
    b, se = t.slope_per_h()
    assert b == pytest.approx(-0.5) and se == pytest.approx(0.0, abs=1e-9)
    e = EquivalentHours()
    e.add(3600, 115.0, True)
    e.add(3600, 115.0, False)
    assert e.stress_h == 1.0 and e.af == pytest.approx(acceleration_factor(115.0))


def _frame(msg):
    return Frame(P.Node.FPGA_APP, P.Node.HOST, msg.TYPE, 0, msg.pack())


def test_experiment_derive_and_quality():
    x = AgingExperiment()
    w = A.AgingWindow(window_id=5, sweeps=4, last=400, min=399, max=401, sum=1600, sumsq=4 * 400 * 400 + 2)
    d = x.derive("A", _frame(w))
    assert d["slack_mean"] == 400 and d["sweeps"] == 4 and d["missing_windows"] == 0
    assert x.derive("A", _frame(A.AgingChain(window_id=5, chain=0, sweeps=4, last=400, min=399, max=401,
                                             sum=1600, sumsq=4 * 400 * 400 + 2)))["chain0_mismatch"] == 0
    assert x.derive("A", _frame(A.AgingChain(window_id=5, chain=0, sweeps=3)))["chain0_mismatch"] == 1
    d = x.derive("A", _frame(A.AgingChain(window_id=5, chain=9, sweeps=2, sum=800, sumsq=320000, stressed=0)))
    assert d == {"ref_slack_mean": 400.0, "ref_slack_std": 0.0}
    d = x.derive("A", _frame(A.AgingRo(window_id=5, window_ms=1000, n_ro=2,
                                       counts=[A.AgingRoCountsItem(count=c) for c in (250_000_000, 1, 0, 0)])))
    assert d["ro0_hz"] == 250e6
    d = x.derive("A", _frame(A.AgingWindow(window_id=8)))
    assert d["missing_windows"] == 2 and d["slack_mean"] is None
    assert set(d) <= set(COLUMNS)


class OvenLine:
    """A serial port in front of the simulated oven firmware."""

    def __init__(self, oven):
        self.oven, self.q = oven, queue.Queue()

    def write(self, data):
        for e in self.oven.take_events():          # events happened before this command
            self.q.put((e + "\n").encode())
        for line in self.oven.feed(data.decode()):
            self.q.put((line + "\n").encode())
        return len(data)

    def read(self, n):
        try:
            return self.q.get(timeout=0.01)
        except queue.Empty:
            return b""

    def close(self):
        pass


def test_ascii_oven_driver():
    o = OvenAscii(OvenModel())
    d = AsciiOven(transport=OvenLine(o), timeout_s=0.5)
    assert "FW=2.0.0" in d.get_config()
    d.set_setpoint(60)
    d.start()
    r = d.get_data()
    assert r.setpoint_c == 60 and r.state == "RUNNING" and r.fault == "NONE"
    with pytest.raises(OvenError, match="RANGE"):
        d.set_setpoint(300)
    o.m.ntc_open = True
    o.step(1.0)
    r = d.get_data()
    assert r.state == "FAULT" and d.events == ["EVENT,FAULT,SENSOR"]
    with pytest.raises(OvenError, match="ACTIVE"):
        d.clear_fault()
    d.stop()


def test_oven_test_script_interlocks(tmp_path):
    sim = Simulation(boards=1).start(speed=200)
    try:
        reason, samples = __import__("dt_monitor.oven_test", fromlist=["run"]).run(
            SimOven(sim), sp=40, minutes=30, out=tmp_path / "o.csv", clock=sim.clock.monotonic,
            sleep=sim.clock.sleep, log=lambda *_: None)
        # the simulated oven approaches its setpoint without overshoot
        assert reason in ("setpoint reached", "time up") and samples[-1][1] > 38
        assert sim.oven.state == "IDLE"                               # STOP_TEST always sent
        rows = list(csv.reader(line for line in open(tmp_path / "o.csv") if not line.startswith("#")))
        assert rows[0][-1] == "fopdt_temp_c" and len(rows) > 10
        sim.inject("ntc_open")
        from dt_monitor.oven_test import run
        reason, _ = run(SimOven(sim), sp=40, minutes=5, clock=sim.clock.monotonic, sleep=sim.clock.sleep,
                        log=lambda *_: None)
        assert "out of range" in reason or "fault" in reason.lower() or "NO_READING" in reason
    finally:
        sim.stop()


@needs_core
def test_check_board_on_the_simulator():
    from fpgaging_bsp.bench import Registry
    from fpgaging_bsp.link import Link
    from dt_monitor.check_board import check
    sim = Simulation(boards=1, app_factory=AgingAppModel).start(speed=1.0)
    try:
        time.sleep(1.2)
        with Link(sim.transport(0, "stlink")) as link:
            rep = check(link, "A", Registry.load(), seconds=4.0)
        assert rep.failed == 0, "\n".join(rep.lines)
        assert any("chain 0 equals" in x for x in rep.lines)
    finally:
        sim.stop()


class AgingBench:
    def __init__(self, tmp, speed=40.0, boards=1):
        self.tmp = tmp
        self.cfg = BenchConfig.from_dict({
            "bench": "dtm", "sessions_dir": str(tmp / "sessions"), "socket": str(tmp / "s.sock"),
            "experiment": EXP, "sim": {"boards": boards}, "oven": {"driver": "sim"},
            "notify": str(tmp / "none.yaml"), "boards": [{"name": "AB"[i], "via": "stlink"} for i in range(boards)]})
        self.sim = Simulation(boards=boards, app_factory=AgingAppModel).start(speed=speed)
        self.svc = Service(self.cfg, sim=self.sim).start()
        self.c = ServiceClient.connect(str(tmp / "s.sock"))

    def wait_idle(self, timeout=120):
        t0 = time.time()
        while time.time() - t0 < timeout:
            st = self.c.call("status")
            if st["run"]["state"] == "idle":
                return st
            time.sleep(0.2)
        raise AssertionError("run did not end")

    def close(self):
        self.c.close()
        self.svc.stop()
        self.sim.stop()


PLAN = (APP / "bench" / "burnin_115C_0v85.yaml").read_text() \
    .replace("settle_min: 2, measure_min: 3", "settle_min: 0.2, measure_min: 0.3") \
    .replace("duration_h: 37", "duration_h: 0.05").replace("until_die_below_c: 70", "minutes: 0.3")


@needs_core
def test_burnin_run_on_the_simulated_bench(tmp_path):
    b = AgingBench(tmp_path)
    try:
        b.c.call("lease")
        info = b.c.call("start_run", plan=PLAN, confirm_compat=True)
        st = b.wait_idle()
        assert st["run"]["reason"] == "finished"
        d = Path(info["session"])
        names = {p.name for p in d.iterdir()}
        assert {"A_AGING_WINDOW.csv", "A_AGING_CHAIN.csv", "A_AGING_INFO.csv", "summary.csv"} <= names
        with open(d / "summary.csv") as f:
            rows = list(csv.DictReader(line for line in f if not line.startswith("#")))
        stress = [r for r in rows if r["phase"].startswith("stress")]
        assert stress and all(r["A_slack_mean"] for r in stress[5:])
        assert all(r["A_c4_slack_mean"] for r in stress[5:])
        assert {r["A_chain0_mismatch"] for r in stress[5:]} == {"0"}
        assert any(r["A_ref_slack_mean"] for r in rows) and any(r["A_ro0_hz"] for r in rows)
        text = (d / "summary.csv").read_text()
        assert "# A_delta_slack:" in text
        # the payload was configured at the start of the run (AGING_SET_MODE acknowledged)
        assert "aging payload not configured" not in (d / "events.log").read_text()
    finally:
        b.close()


@needs_core
def test_corners_script_through_the_service(tmp_path):
    from dt_monitor.corners import run
    b = AgingBench(tmp_path, speed=60)
    try:
        d = run(str(tmp_path / "s.sock"), ["A"], [0.85, 0.90], settle_min=0.2, measure_min=0.3, poll_s=0.2)
        with open(d / "corners_summary.csv") as f:
            rows = list(csv.DictReader(f))
        assert [float(r["vccint_target_v"]) for r in rows] == [0.85, 0.90]
        assert all(r["c0_mean"] and r["c8_mean"] for r in rows)
        assert float(rows[1]["c0_mean"]) > float(rows[0]["c0_mean"])   # more voltage, more slack
    finally:
        b.close()


@needs_core
def test_gui_offscreen(tmp_path):
    pytest.importorskip("PySide6")
    from PySide6.QtWidgets import QApplication
    from dt_monitor.gui import AgingClient, MainWindow
    app = QApplication.instance() or QApplication([])
    b = AgingBench(tmp_path, speed=1.0)
    try:
        c = AgingClient(str(tmp_path / "s.sock"))
        assert c.connect_service()
        w = MainWindow("dtm", c)
        t0 = time.time()
        panel = w.panels["A"]
        while time.time() - t0 < 15 and (panel.windows < 2 or panel.table.item(4, 4) is None):
            app.processEvents()
            time.sleep(0.02)
        assert panel.windows >= 2 and "±" in panel.lbl["slack"].text()
        assert panel.table.item(4, 1).text() == "CARRY8"
        assert w.quality.item(0, 0) is None or w.quality.item(0, 0).text() == "A"
        assert "A" in w.p_slack.series
        w.close()
        c.close()
    finally:
        b.close()
