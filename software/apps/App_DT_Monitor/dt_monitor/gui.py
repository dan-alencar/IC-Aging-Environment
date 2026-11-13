"""App_DT_Monitor main window: a client of fbs-service (fbs SPEC §6.2, §9.2).

Per board: the fbs board widgets (STM32 state and power, SYSMON, rails, link health,
identity) and the aging panel (every chain's window statistics, the reference chain, ring
oscillators, live slack mean/std/trend, Arrhenius acceleration and equivalent hours).
Plus plots, a data-quality table, the oven, run control (start a run plan, stop, notes) and
the service log. The window never touches a serial port.
"""
from __future__ import annotations

import sys
import time
from typing import Dict, List, Optional

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (QApplication, QDoubleSpinBox, QFileDialog, QFormLayout, QGridLayout, QGroupBox,
                               QHBoxLayout, QInputDialog, QLabel, QMainWindow, QMessageBox, QPushButton,
                               QSplitter, QTableWidget, QTableWidgetItem, QTabWidget, QVBoxLayout, QWidget)

from fpgaging_bsp.qt import theme
from fpgaging_bsp.qt.client import LinkClient
from fpgaging_bsp.qt.plots import TimePlot
from fpgaging_bsp.qt.widgets import (IdentityWidget, LinkHealthWidget, LogPanel, RailsWidget, StateWidget,
                                     SysmonWidget)
from fpgaging_bsp.units import sysmon_temp_c, sysmon_volt

from . import protocol_aging as A
from .stats import EquivalentHours, Trend, acceleration_factor, window_stats

KIND = {int(k): k.name for k in A.ChainKind}


class AgingClient(LinkClient):
    """LinkClient with the IC-Aging message signals."""
    aging_window = Signal(str, dict, dict)
    aging_chain = Signal(str, dict, dict)
    aging_ro = Signal(str, dict, dict)
    aging_info = Signal(str, dict, dict)


class AgingPanel(QGroupBox):
    """Chains, reference, ring oscillators and live statistics of one board."""

    COLS = ["chain", "kind", "size", "sweeps", "mean", "std", "min", "max", "window"]

    def __init__(self, client: "AgingClient", board: str, parent=None):
        super().__init__(f"Aging sensor - board {board}", parent)
        self.client, self.board = client, board
        v = QVBoxLayout(self)
        self.table = QTableWidget(10, len(self.COLS))
        self.table.setHorizontalHeaderLabels(self.COLS)
        self.table.verticalHeader().hide()
        v.addWidget(self.table)
        g = QGridLayout()
        self.lbl: Dict[str, QLabel] = {}
        keys = ["slack", "trend", "flags", "ro", "die", "AF", "stress h", "equivalent h"]
        for i, k in enumerate(keys):
            n = QLabel(k)
            n.setStyleSheet(f"color: {theme.SUBTEXT};")
            val = QLabel("-")
            g.addWidget(n, i // 2, 2 * (i % 2))
            g.addWidget(val, i // 2, 2 * (i % 2) + 1)
            self.lbl[k] = val
        v.addLayout(g)
        form = QFormLayout()
        self.t_use = QDoubleSpinBox()
        self.t_use.setRange(-40, 150)
        self.t_use.setValue(55.0)
        self.t_use.setSuffix(" °C")
        self.ea = QDoubleSpinBox()
        self.ea.setRange(0.1, 2.0)
        self.ea.setDecimals(2)
        self.ea.setSingleStep(0.05)
        self.ea.setValue(0.7)
        self.ea.setSuffix(" eV")
        form.addRow("T use", self.t_use)
        form.addRow("Ea", self.ea)
        v.addLayout(form)
        self.trend = Trend(span_s=3600.0)
        self.eq = EquivalentHours()
        self.die_c: Optional[float] = None
        self.powered = False
        self.last_win_t: Optional[float] = None
        self.windows = 0
        self.last_window: Optional[Dict] = None
        client.aging_window.connect(self.on_window)
        client.aging_chain.connect(self.on_chain)
        client.aging_ro.connect(self.on_ro)
        client.sysmon.connect(self.on_sysmon)
        client.pwr_telem.connect(lambda b, m, ev: b == self.board and setattr(
            self, "powered", bool(m["flags"] & 1)))
        self.t_use.valueChanged.connect(self._params)
        self.ea.valueChanged.connect(self._params)

    def _params(self) -> None:
        self.eq.t_use_c, self.eq.ea_ev = self.t_use.value(), self.ea.value()

    def _set(self, row: int, vals) -> None:
        for c, x in enumerate(vals):
            self.table.setItem(row, c, QTableWidgetItem("" if x is None else str(x)))

    def on_window(self, board, m, ev) -> None:
        if board != self.board:
            return
        t = ev["t"]
        mean, std = window_stats(m["sweeps"], m["sum"], m["sumsq"])
        self.trend.add(t, mean)
        if self.last_win_t is not None:
            self.eq.add(t - self.last_win_t, self.die_c, self.powered)
        self.last_win_t = t
        self.windows += 1
        self.last_window = m
        self.lbl["slack"].setText("-" if mean is None else f"{mean:.2f} ± {std:.2f} ({m['min']}-{m['max']})")
        b, se = self.trend.slope_per_h()
        self.lbl["trend"].setText("-" if b is None else f"{b:+.3f} ± {se:.3f} steps/h (last hour)")
        fl = [f.name for f in A.AgingFlags if f.value and m["flags"] & f.value]
        bad = {"NO_ALARM", "PS_TIMEOUT", "LOCK_LOST", "STUCK"} & set(fl)
        self.lbl["flags"].setText(" ".join(fl) or "none")
        self.lbl["flags"].setStyleSheet(f"color: {theme.ORANGE};" if bad else "")
        if self.die_c is not None:
            self.lbl["AF"].setText(f"{acceleration_factor(self.die_c, self.eq.t_use_c, self.eq.ea_ev):.1f}")
        self.lbl["stress h"].setText(f"{self.eq.stress_h:.3f}")
        self.lbl["equivalent h"].setText(f"{self.eq.eq_h:.2f}")

    def on_chain(self, board, m, ev) -> None:
        if board != self.board or not 0 <= m["chain"] < 10:
            return
        mean, std = window_stats(m["sweeps"], m["sum"], m["sumsq"])
        self._set(m["chain"], [m["chain"], KIND.get(m["kind"], m["kind"]) + ("" if m["stressed"] else " (ref)"),
                               m["size"], m["sweeps"], None if mean is None else f"{mean:.2f}",
                               None if std is None else f"{std:.2f}", m["min"], m["max"], m["window_id"]])

    def on_ro(self, board, m, ev) -> None:
        if board == self.board:
            ms = m["window_ms"] or 1
            self.lbl["ro"].setText("  ".join(f"{c['count'] / ms / 1000:.2f} MHz" for c in m["counts"][:m["n_ro"]]))

    def on_sysmon(self, board, m, ev) -> None:
        if board == self.board:
            self.die_c = sysmon_temp_c(m["temp_avg"] if m.get("n_avg") else m["temp"])
            self.lbl["die"].setText(f"{self.die_c:.1f} °C")


class QualityTable(QTableWidget):
    COLS = ["board", "windows", "missing", "chain 0 mismatch", "host CRC err", "seq lost", "last window"]

    def __init__(self, client: LinkClient, boards: List[str], panels: Dict[str, AgingPanel], parent=None):
        super().__init__(len(boards), len(self.COLS), parent)
        self.client, self.boards, self.panels = client, boards, panels
        self.setHorizontalHeaderLabels(self.COLS)
        self.verticalHeader().hide()
        self.missing = {b: 0 for b in boards}
        self.mismatch = {b: 0 for b in boards}
        self.last_id: Dict[str, int] = {}
        self.win0: Dict[str, Dict] = {}
        client.aging_window.connect(self.on_window)
        client.aging_chain.connect(self.on_chain)
        t = QTimer(self)
        t.timeout.connect(self.refresh)
        t.start(2000)

    def on_window(self, board, m, ev) -> None:
        if board in self.last_id and m["window_id"] > self.last_id[board] + 1:
            self.missing[board] += m["window_id"] - self.last_id[board] - 1
        self.last_id[board] = m["window_id"]
        self.win0[board] = m

    def on_chain(self, board, m, ev) -> None:
        w = self.win0.get(board)
        if m["chain"] == 0 and w is not None and any(w[k] != m[k] for k in ("sweeps", "min", "max", "sum", "sumsq")):
            self.mismatch[board] += 1

    def refresh(self) -> None:
        def done(st, err):
            if err or not st:
                return
            for i, b in enumerate(self.boards):
                link = next((x["link"] for x in st["boards"] if x["name"] == b), {})
                p = self.panels.get(b)
                age = f"{time.time() - p.last_win_t:.1f} s ago" if p and p.last_win_t else "-"
                vals = [b, p.windows if p else 0, self.missing[b], self.mismatch[b],
                        link.get("decoder", {}).get("crc_err", ""), link.get("seq_lost", ""), age]
                for c, x in enumerate(vals):
                    it = QTableWidgetItem(str(x))
                    if c in (2, 3) and x:
                        it.setForeground(Qt.GlobalColor.red)
                    self.setItem(i, c, it)
        if self.client.connected:
            self.client.call_async("status", done)


class MainWindow(QMainWindow):
    def __init__(self, bench: str, client: Optional[AgingClient] = None):
        super().__init__()
        self.setWindowTitle(f"D&T Monitor - {bench}")
        self.setStyleSheet(theme.STYLE)
        self.client = client or AgingClient(bench, self)
        if not self.client.connected:
            self.client.connect_service()
        boards = [b["name"] for b in self.client.hello.get("boards", [])]
        self.boards = boards
        # top bar
        top = QWidget()
        bar = QHBoxLayout(top)
        self.conn = QLabel("disconnected")
        self.lease_lbl = QLabel("")
        self.run_lbl = QLabel("run: idle")
        self.oven_lbl = QLabel("oven: -")
        self.b_lease = QPushButton("Take control")
        self.b_run = QPushButton("Start run plan…")
        self.b_stop = QPushButton("Stop run")
        self.b_stop.setObjectName("danger")
        self.b_note = QPushButton("Note…")
        for w in (self.conn, self.lease_lbl, self.b_lease, self.run_lbl, self.b_run, self.b_stop, self.b_note,
                  self.oven_lbl):
            bar.addWidget(w)
        bar.addStretch(1)
        self.b_lease.clicked.connect(lambda: self.client.call_async("lease", self._err))
        self.b_run.clicked.connect(self.start_run)
        self.b_stop.clicked.connect(self.stop_run)
        self.b_note.clicked.connect(self.note)
        # tabs
        self.tabs = QTabWidget()
        self.panels: Dict[str, AgingPanel] = {}
        for b in boards:
            page = QWidget()
            g = QGridLayout(page)
            left = QWidget()
            lv = QVBoxLayout(left)
            for w in (StateWidget(self.client, b), SysmonWidget(self.client, b), LinkHealthWidget(self.client, b)):
                lv.addWidget(w)
            right = QWidget()
            rv = QVBoxLayout(right)
            self.panels[b] = AgingPanel(self.client, b)
            rv.addWidget(self.panels[b])
            rv.addWidget(IdentityWidget(self.client, b))
            rv.addWidget(RailsWidget(self.client, b))
            g.addWidget(left, 0, 0)
            g.addWidget(right, 0, 1)
            self.tabs.addTab(page, f"Board {b}")
        self.p_slack = TimePlot("Slack (chain 0, window mean)", "steps")
        self.p_temp = TimePlot("Temperatures", "°C")
        self.p_volt = TimePlot("VCCINT", "V")
        plots = QWidget()
        pl = QVBoxLayout(plots)
        for p in (self.p_slack, self.p_temp, self.p_volt):
            pl.addWidget(p.widget)
        self.tabs.addTab(plots, "Plots")
        self.quality = QualityTable(self.client, boards, self.panels)
        self.tabs.addTab(self.quality, "Data quality")
        self.logp = LogPanel(self.client)
        split = QSplitter(Qt.Vertical)
        split.addWidget(self.tabs)
        split.addWidget(self.logp)
        split.setStretchFactor(0, 4)
        central = QWidget()
        v = QVBoxLayout(central)
        v.addWidget(top)
        v.addWidget(split)
        self.setCentralWidget(central)
        # signals
        c = self.client
        c.connection.connect(self.on_conn)
        c.lease.connect(self.on_lease)
        c.run.connect(self.on_run)
        c.oven.connect(self.on_oven)
        c.aging_window.connect(self.on_window)
        c.sysmon.connect(self.on_sysmon)
        c.pwr_telem.connect(self.on_pwr)
        self._redraw = QTimer(self)
        self._redraw.timeout.connect(lambda: [p.redraw() for p in (self.p_slack, self.p_temp, self.p_volt)])
        self._redraw.start(1000)
        self.on_conn(c.connected)
        self.on_lease(c.lease_holder)
        self.on_run(c.hello.get("run", {}))

    # -------------------------------------------------------------- slots
    def _err(self, r, err) -> None:
        if err:
            QMessageBox.warning(self, "Service", err)

    def on_conn(self, ok: bool) -> None:
        self.conn.setText("connected" if ok else "service not reachable (retrying)")
        self.conn.setStyleSheet(theme.badge(theme.GREEN if ok else theme.RED))

    def on_lease(self, holder) -> None:
        mine = self.client.has_lease
        self.lease_lbl.setText("you have control" if mine else ("read-only" if holder is None else
                                                                f"control: client {holder}"))
        for b in (self.b_run, self.b_stop, self.b_note):
            b.setEnabled(mine)
        self.b_lease.setEnabled(not mine)

    def on_run(self, r: Dict) -> None:
        p = r.get("progress") or {}
        txt = f"run: {r.get('state', 'idle')}"
        if r.get("plan"):
            txt += f" {r['plan']}"
        if p.get("stress_s"):
            txt += f" - stress {p['stress_s'] / 3600:.2f} h, {p.get('eq_h', 0):.2f} eq h"
        if r.get("reason") and r.get("state") == "idle":
            txt += f" ({r['reason']})"
        self.run_lbl.setText(txt)

    def on_oven(self, ev: Dict) -> None:
        t = ev.get("temp_c")
        self.oven_lbl.setText(f"oven: {t:.1f} °C → {ev.get('setpoint_c') or 0:.1f}, {ev.get('output_pct') or 0:.0f} %"
                              f" {ev.get('state', '')} {'' if ev.get('fault') in ('', 'NONE') else ev.get('fault')}"
                              if t is not None else "oven: no reading")
        if t is not None:
            self.p_temp.append("oven", ev["t"], t)

    def on_window(self, board, m, ev) -> None:
        mean, _ = window_stats(m["sweeps"], m["sum"], m["sumsq"])
        self.p_slack.append(board, ev["t"], mean)

    def on_sysmon(self, board, m, ev) -> None:
        self.p_temp.append(f"{board} die", ev["t"], sysmon_temp_c(m["temp_avg"] if m.get("n_avg") else m["temp"]))
        self.p_volt.append(f"{board} SYSMON", ev["t"], sysmon_volt(m["vccint_avg"] if m.get("n_avg") else m["vccint"]))

    def on_pwr(self, board, m, ev) -> None:
        if m.get("n_samples"):
            self.p_volt.append(f"{board} module", ev["t"], m["vccint_mean_mv"] / 1000)

    def start_run(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Run plan", "", "Run plans (*.yaml *.yml)")
        if path:
            self.start_plan(open(path).read())

    def start_plan(self, text: str, confirm: Optional[bool] = None) -> None:
        def done(r, err):
            if not err:
                return
            if "untested combination" in err or "acknowledged" in err:
                if confirm is None and QMessageBox.question(self, "Start run", f"{err}\n\nStart anyway?") == \
                        QMessageBox.StandardButton.Yes:
                    self.start_plan(text, confirm=True)
                return
            QMessageBox.warning(self, "Start run", err)
        self.client.call_async("start_run", done, plan=text, confirm_compat=bool(confirm), ack_identity=bool(confirm))

    def stop_run(self) -> None:
        if QMessageBox.question(self, "Stop run", "Stop the run? Boards go to 850 mV and the oven stops.") == \
                QMessageBox.StandardButton.Yes:
            self.client.call_async("stop_run", self._err, reason="stopped by the operator")

    def note(self) -> None:
        text, ok = QInputDialog.getText(self, "Note", "Text for the session log:")
        if ok and text:
            self.client.call_async("note", self._err, text=text)


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    bench = argv[0] if argv else "rv02a"
    app = QApplication.instance() or QApplication(sys.argv[:1])
    w = MainWindow(bench)
    w.resize(1500, 950)
    w.show()
    return app.exec()
