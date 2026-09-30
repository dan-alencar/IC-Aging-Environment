"""
App_CornerSweep — Main window.

Layout
──────
Top bar (fixed):  [Forno + DUT temp targets]  [Teste (name + start)]
Content (QSplitter vertical):
  ├─ Top (QSplitter horizontal):
  │   ├─ Left  (30 %): Live status panel
  │   └─ Right (70 %): Corner results table  +  Sweep status panel
  └─ Bottom (30 %): Event log
Status bar: device connection indicators
"""
import time

from PySide6.QtCore import QThread, Signal, Slot, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDoubleSpinBox, QFormLayout, QGroupBox, QHBoxLayout, QLabel,
    QLineEdit, QMainWindow, QPushButton, QSizePolicy, QSplitter,
    QStatusBar, QTextEdit, QVBoxLayout, QWidget, QGridLayout,
)

import config
from corner_sequencer import CornerResult, CornerSweepSequencer, Phase
from workers import ArduinoWorker, DUTWorker, PSUWorker

# ── Catppuccin Mocha palette ─────────────────────────────────────────────────
_BG      = '#1e1e2e'
_SURFACE = '#313244'
_OVERLAY = '#45475a'
_MUTED   = '#6c7086'
_TEXT    = '#cdd6f4'
_SUBTEXT = '#a6adc8'
_GREEN   = '#a6e3a1'
_RED     = '#f38ba8'
_YELLOW  = '#f9e2af'
_BLUE    = '#89b4fa'
_PURPLE  = '#cba6f7'
_ORANGE  = '#fab387'
_TEAL    = '#89dceb'

_DARK_STYLE = f"""
QMainWindow, QDialog {{ background-color: {_BG}; }}
QWidget     {{ background-color: {_BG}; color: {_TEXT}; font-size: 12px; }}
QGroupBox   {{
    color: {_PURPLE}; border: 1px solid {_OVERLAY}; border-radius: 6px;
    margin-top: 10px; padding-top: 6px; font-weight: bold;
}}
QGroupBox::title {{
    subcontrol-origin: margin; subcontrol-position: top left;
    padding: 0 6px; left: 10px;
}}
QGroupBox:disabled {{ color: {_MUTED}; border-color: {_SURFACE}; }}
QLineEdit, QDoubleSpinBox {{
    background-color: {_SURFACE}; color: {_TEXT};
    border: 1px solid {_OVERLAY}; border-radius: 4px; padding: 3px 6px;
}}
QLineEdit:focus, QDoubleSpinBox:focus {{ border: 1px solid {_PURPLE}; }}
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
    background-color: {_OVERLAY}; border: none; width: 16px; border-radius: 2px;
}}
QPushButton {{
    background-color: {_OVERLAY}; color: {_TEXT}; border: none;
    border-radius: 4px; padding: 6px 14px; font-size: 12px;
}}
QPushButton:hover   {{ background-color: #585b70; }}
QPushButton:pressed {{ background-color: {_SURFACE}; }}
QPushButton:disabled {{ color: {_MUTED}; background-color: {_SURFACE}; }}
QTextEdit {{
    background-color: #181825; color: {_GREEN};
    border: 1px solid {_OVERLAY}; border-radius: 4px;
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace; font-size: 11px;
}}
QStatusBar {{ background-color: #181825; border-top: 1px solid {_OVERLAY}; }}
QStatusBar QLabel {{
    background-color: transparent; color: {_MUTED}; padding: 0 8px; font-size: 11px;
}}
"""

_STYLE_INFO = (
    f"QLabel {{ color: {_TEAL}; background-color: #1e2535; "
    f"border: 1px solid {_OVERLAY}; border-radius: 6px; padding: 8px; }}"
)
_STYLE_OK = (
    f"QLabel {{ color: {_GREEN}; background-color: #1a2e1a; "
    f"border: 2px solid #40a060; border-radius: 8px; padding: 10px; }}"
)
_STYLE_ERR = (
    f"QLabel {{ color: {_RED}; background-color: #2e1a1a; "
    f"border: 2px solid #c04060; border-radius: 8px; padding: 10px; }}"
)
_STYLE_WARN = (
    f"QLabel {{ color: {_YELLOW}; background-color: #2e2a1e; "
    f"border: 1px solid #856404; border-radius: 6px; padding: 8px; }}"
)
_STYLE_PENDING = (
    f"QLabel {{ color: {_MUTED}; background-color: {_SURFACE}; "
    f"border: 1px solid {_OVERLAY}; border-radius: 6px; padding: 8px; }}"
)

_N_CORNERS = len(config.CORNERS_V)

# Column indices in the corner results grid
_COL_VCMD, _COL_VCCINT, _COL_SLACK, _COL_MINMAX, _COL_FAIL, _COL_ERROS, _COL_STATUS = range(7)
_COL_HEADERS = ["V cmd", "VCCINT", "Slack médio", "Min / Max", "Fail", "Erros", "Status"]


class MainWindow(QMainWindow):
    start_test_signal = Signal(dict)
    stop_test_signal  = Signal()

    start_arduino_signal = Signal()
    stop_arduino_signal  = Signal()
    start_psu_signal     = Signal()
    stop_psu_signal      = Signal()
    start_dut_signal     = Signal()
    stop_dut_signal      = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Corner Sweep — Caracterização de Falha por Tensão")
        self.setGeometry(100, 100, 1300, 820)
        self.setStyleSheet(_DARK_STYLE)

        self.threads = {}
        self.workers = {}

        self._build_top_bar()
        self._build_status_panel()
        self._build_corners_panel()
        self._build_sweep_panel()
        self._build_log_panel()
        self._assemble_layout()
        self._setup_status_bar()
        self._start_workers()
        self._start_sequencer()
        self._connect_signals()

    # ── Widget construction ───────────────────────────────────────────────────

    def _build_top_bar(self):
        self.grp_oven = QGroupBox("Controle de Temperatura")
        self.spn_oven_sp = QDoubleSpinBox()
        self.spn_oven_sp.setRange(25.0, 150.0)
        self.spn_oven_sp.setValue(100.0)
        self.spn_oven_sp.setSuffix(" °C")
        self.spn_oven_sp.setToolTip("Setpoint de temperatura do forno (enviado ao Arduino PID)")

        self.spn_dut_target = QDoubleSpinBox()
        self.spn_dut_target.setRange(25.0, 140.0)
        self.spn_dut_target.setValue(85.0)
        self.spn_dut_target.setSuffix(" °C")
        self.spn_dut_target.setToolTip(
            f"Temperatura alvo do DUT. O teste só inicia quando o DUT atingir "
            f"este valor ±{config.TEMP_STABLE_TOL_C}°C por {config.TEMP_STABLE_TICKS} s."
        )

        self.grp_test = QGroupBox("Controle do Teste")
        self.test_name_input = QLineEdit("Sweep_001")
        self.btn_toggle = QPushButton("INICIAR TESTE")
        self.btn_toggle.setCheckable(True)
        self.btn_toggle.setStyleSheet(
            f"background-color: #1e4d2b; color: {_GREEN}; font-weight: bold; "
            "padding: 10px; font-size: 14px; border: 1px solid #40a060; border-radius: 4px;"
        )

        self.lbl_phase = QLabel("Fase: —")
        self.lbl_phase.setStyleSheet(
            f"color: {_SUBTEXT}; background-color: {_SURFACE}; "
            "padding: 5px 8px; border-radius: 4px; font-size: 11px;"
        )

    def _build_status_panel(self):
        """Left live-status panel."""
        def _big_lbl(text):
            lbl = QLabel(text)
            lbl.setFont(QFont("", 14, QFont.Bold))
            lbl.setStyleSheet(_STYLE_INFO)
            lbl.setAlignment(Qt.AlignCenter)
            return lbl

        def _med_lbl(text):
            lbl = QLabel(text)
            lbl.setStyleSheet(_STYLE_WARN)
            lbl.setAlignment(Qt.AlignCenter)
            return lbl

        self.lbl_dut_temp  = _big_lbl("DUT: — °C")
        self.lbl_vccint    = _big_lbl("VCCINT: — V")
        self.lbl_oven_temp = _med_lbl("Forno: — °C")
        self.lbl_psu_cmd   = _med_lbl("PSU cmd: — V")
        self.lbl_psu_meas  = _med_lbl("PSU med: — V")
        self.lbl_psu_curr  = _med_lbl("Corrente: — A")

        self.lbl_stability = QLabel("Estabilidade: —")
        self.lbl_stability.setStyleSheet(
            f"color: {_SUBTEXT}; background-color: {_SURFACE}; "
            "padding: 4px 8px; border-radius: 4px; font-size: 11px;"
        )

    def _build_corners_panel(self):
        """Corner results grid — header + 3 data rows."""
        self._corner_cells: list[dict] = []

        self._corner_grid = QGridLayout()
        self._corner_grid.setSpacing(4)

        # Header row
        for col, hdr in enumerate(_COL_HEADERS):
            lbl = QLabel(hdr)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet(
                f"color: {_PURPLE}; background-color: {_SURFACE}; "
                "font-weight: bold; padding: 4px; border-radius: 4px;"
            )
            self._corner_grid.addWidget(lbl, 0, col)

        # Data rows (one per corner voltage)
        for i, v in enumerate(config.CORNERS_V):
            row = i + 1
            cells = {}

            def _cell(text="—", style=_STYLE_PENDING):
                lbl = QLabel(text)
                lbl.setAlignment(Qt.AlignCenter)
                lbl.setStyleSheet(style)
                return lbl

            cells['vcmd']   = _cell(f"{v:.3f} V")
            cells['vccint'] = _cell()
            cells['slack']  = _cell()
            cells['minmax'] = _cell()
            cells['fail']   = _cell()
            cells['erros']  = _cell()
            cells['status'] = _cell("Aguardando")

            for col, key in enumerate(
                ['vcmd', 'vccint', 'slack', 'minmax', 'fail', 'erros', 'status']
            ):
                self._corner_grid.addWidget(cells[key], row, col)

            self._corner_cells.append(cells)

    def _build_sweep_panel(self):
        """Sweep status indicators."""
        self.lbl_sweep_v     = QLabel("Tensão sweep: —")
        self.lbl_sweep_vcc   = QLabel("VCCINT: —")
        self.lbl_sweep_slack = QLabel("Slack: —")
        self.lbl_sweep_status = QLabel("—")

        self.lbl_sweep_status.setFont(QFont("", 16, QFont.Bold))
        self.lbl_sweep_status.setAlignment(Qt.AlignCenter)
        self.lbl_sweep_status.setMinimumHeight(50)
        self.lbl_sweep_status.setStyleSheet(_STYLE_PENDING)

        for lbl in (self.lbl_sweep_v, self.lbl_sweep_vcc, self.lbl_sweep_slack):
            lbl.setStyleSheet(_STYLE_INFO)
            lbl.setAlignment(Qt.AlignCenter)

        self.lbl_failure_result = QLabel("")
        self.lbl_failure_result.setAlignment(Qt.AlignCenter)
        self.lbl_failure_result.setStyleSheet(
            f"color: {_YELLOW}; background-color: {_SURFACE}; "
            "padding: 8px; border-radius: 6px; font-weight: bold; font-size: 13px;"
        )
        self.lbl_failure_result.setVisible(False)

    def _build_log_panel(self):
        self.log_edit = QTextEdit()
        self.log_edit.setReadOnly(True)

    # ── Layout assembly ───────────────────────────────────────────────────────

    def _assemble_layout(self):
        root = QVBoxLayout()
        root.setSpacing(6)
        root.setContentsMargins(8, 8, 8, 4)

        # ── Top bar ──
        top_bar = QHBoxLayout()
        top_bar.setSpacing(8)

        oven_form = QFormLayout()
        oven_form.setSpacing(6)
        oven_form.addRow("Setpoint Forno:", self.spn_oven_sp)
        oven_form.addRow("Alvo DUT:", self.spn_dut_target)
        self.grp_oven.setLayout(oven_form)
        top_bar.addWidget(self.grp_oven, stretch=2)

        test_form = QFormLayout()
        test_form.setSpacing(6)
        test_form.addRow("Nome:", self.test_name_input)
        test_form.addRow(self.btn_toggle)
        test_form.addRow(self.lbl_phase)
        self.grp_test.setLayout(test_form)
        top_bar.addWidget(self.grp_test, stretch=2)

        root.addLayout(top_bar)

        # ── Content splitter ──
        main_splitter = QSplitter(Qt.Vertical)

        # ── Top: left status + right results ──
        top_widget = QWidget()
        top_hbox   = QHBoxLayout(top_widget)
        top_hbox.setSpacing(8)
        top_hbox.setContentsMargins(0, 0, 0, 0)

        # Left: live status
        grp_status = QGroupBox("Status em Tempo Real")
        status_v = QVBoxLayout()
        status_v.setSpacing(6)
        status_v.addWidget(self.lbl_dut_temp)
        status_v.addWidget(self.lbl_vccint)
        status_v.addWidget(self.lbl_oven_temp)
        status_v.addWidget(self.lbl_psu_cmd)
        status_v.addWidget(self.lbl_psu_meas)
        status_v.addWidget(self.lbl_psu_curr)
        status_v.addStretch()
        status_v.addWidget(self.lbl_stability)
        grp_status.setLayout(status_v)
        top_hbox.addWidget(grp_status, stretch=3)

        # Right: corner table + sweep panel
        right_widget = QWidget()
        right_v = QVBoxLayout(right_widget)
        right_v.setSpacing(8)
        right_v.setContentsMargins(0, 0, 0, 0)

        grp_corners = QGroupBox("Resultados por Corner")
        corners_inner = QVBoxLayout()
        corners_inner.setContentsMargins(6, 6, 6, 6)
        corners_inner.addLayout(self._corner_grid)
        grp_corners.setLayout(corners_inner)
        right_v.addWidget(grp_corners, stretch=3)

        grp_sweep = QGroupBox("Varredura Descendente de Tensão")
        sweep_v = QVBoxLayout()
        sweep_v.setSpacing(6)
        sweep_metrics = QHBoxLayout()
        sweep_metrics.addWidget(self.lbl_sweep_v)
        sweep_metrics.addWidget(self.lbl_sweep_vcc)
        sweep_metrics.addWidget(self.lbl_sweep_slack)
        sweep_v.addLayout(sweep_metrics)
        sweep_v.addWidget(self.lbl_sweep_status)
        sweep_v.addWidget(self.lbl_failure_result)
        grp_sweep.setLayout(sweep_v)
        right_v.addWidget(grp_sweep, stretch=2)

        top_hbox.addWidget(right_widget, stretch=7)
        main_splitter.addWidget(top_widget)

        # Bottom: log
        grp_log = QGroupBox("Log de Eventos")
        log_inner = QVBoxLayout()
        log_inner.setContentsMargins(4, 4, 4, 4)
        log_inner.addWidget(self.log_edit)
        grp_log.setLayout(log_inner)
        main_splitter.addWidget(grp_log)

        main_splitter.setStretchFactor(0, 7)
        main_splitter.setStretchFactor(1, 3)
        main_splitter.setChildrenCollapsible(False)
        root.addWidget(main_splitter, stretch=1)

        central = QWidget()
        central.setLayout(root)
        self.setCentralWidget(central)

    def _setup_status_bar(self):
        sb = QStatusBar()
        self.setStatusBar(sb)
        self._sb_test    = QLabel("Aguardando início")
        self._sb_dut     = QLabel()
        self._sb_psu     = QLabel()
        self._sb_arduino = QLabel()
        sb.addWidget(self._sb_test, 1)
        sb.addPermanentWidget(self._sb_dut)
        sb.addPermanentWidget(self._sb_psu)
        sb.addPermanentWidget(self._sb_arduino)
        self._refresh_status_bar()

    def _refresh_status_bar(self, running: bool = False):
        def pill(label, ok):
            dot   = "●" if ok else "○"
            color = _GREEN if ok else _MUTED
            return f'<span style="color:{color}; font-size:11px;">{dot} {label}</span>'

        self._sb_dut.setText(pill("DUT", True))
        self._sb_psu.setText(pill("PSU", config.PSU_ENABLED))
        self._sb_arduino.setText(pill("Arduino", config.ARDUINO_ENABLED))
        if running:
            self._sb_test.setText(
                f'<span style="color:{_GREEN}; font-weight:bold;">▶ Teste em execução</span>'
            )
        else:
            self._sb_test.setText(
                f'<span style="color:{_MUTED};">■ Aguardando início</span>'
            )

    # ── Worker & sequencer setup ──────────────────────────────────────────────

    def _start_worker(self, name, worker):
        thread = QThread()
        worker.moveToThread(thread)
        worker.log_message.connect(self._log)
        self.threads[name] = thread
        self.workers[name] = worker
        thread.start()
        return worker

    def _start_workers(self):
        ard = self._start_worker("arduino", ArduinoWorker())
        self.start_arduino_signal.connect(ard.start)
        self.stop_arduino_signal.connect(ard.stop)
        self.start_arduino_signal.emit()

        psu = self._start_worker("psu", PSUWorker())
        self.start_psu_signal.connect(psu.start)
        self.stop_psu_signal.connect(psu.stop)
        self.start_psu_signal.emit()

        dut = self._start_worker("dut", DUTWorker())
        self.start_dut_signal.connect(dut.start)
        self.stop_dut_signal.connect(dut.stop)
        self.start_dut_signal.emit()

    def _start_sequencer(self):
        seq = CornerSweepSequencer(
            self.workers["arduino"],
            self.workers["psu"],
            self.workers["dut"],
        )
        self._start_worker("sequencer", seq)

        self.start_test_signal.connect(seq.start_test)
        self.stop_test_signal.connect(seq.stop_test)
        seq.log_message.connect(self._log)
        seq.phase_changed.connect(self._on_phase_changed)
        seq.status_update.connect(self._on_status_update)
        seq.corner_done.connect(self._on_corner_done)
        seq.sweep_tick.connect(self._on_sweep_tick)
        seq.test_finished.connect(self._on_test_finished)

    def _connect_signals(self):
        self.btn_toggle.clicked.connect(self._on_toggle_test)

    # ── Slots ─────────────────────────────────────────────────────────────────

    @Slot(str)
    def _log(self, msg: str):
        ts = time.strftime('%H:%M:%S')
        self.log_edit.append(f"[{ts}] {msg}")

    @Slot(bool)
    def _on_toggle_test(self, checked: bool):
        if checked:
            settings = {
                'test_name':      self.test_name_input.text(),
                'oven_setpoint':  self.spn_oven_sp.value(),
                'target_dut_temp': self.spn_dut_target.value(),
            }
            # Reset corner cells
            for cells in self._corner_cells:
                for key in ('vccint', 'slack', 'minmax', 'fail', 'erros'):
                    cells[key].setText("—")
                    cells[key].setStyleSheet(_STYLE_PENDING)
                cells['status'].setText("Aguardando")
                cells['status'].setStyleSheet(_STYLE_PENDING)
            # Reset sweep panel
            self.lbl_sweep_v.setText("Tensão sweep: —")
            self.lbl_sweep_vcc.setText("VCCINT: —")
            self.lbl_sweep_slack.setText("Slack: —")
            self.lbl_sweep_status.setText("—")
            self.lbl_sweep_status.setStyleSheet(_STYLE_PENDING)
            self.lbl_failure_result.setVisible(False)

            self.btn_toggle.setText("PARAR TESTE")
            self.btn_toggle.setStyleSheet(
                f"background-color: #4d1e2b; color: {_RED}; font-weight: bold; "
                "padding: 10px; font-size: 14px; border: 1px solid #c04060; border-radius: 4px;"
            )
            self.test_name_input.setEnabled(False)
            self._refresh_status_bar(running=True)
            self.start_test_signal.emit(settings)
        else:
            self.stop_test_signal.emit()

    @Slot(str)
    def _on_phase_changed(self, phase_str: str):
        self.lbl_phase.setText(f"Fase: {phase_str}")

    @Slot(dict)
    def _on_status_update(self, d: dict):
        t_dut    = d.get('dut_temp_c',  0.0)
        v_dut    = d.get('dut_volt_v',  0.0)
        t_oven   = d.get('oven_temp_c', 0.0)
        v_psu    = d.get('psu_volt_v',  0.0)
        c_psu    = d.get('psu_curr_a',  0.0)
        target   = self.spn_dut_target.value()
        elapsed  = d.get('elapsed_s', '0.0')

        self.lbl_dut_temp.setText(f"DUT: {t_dut:.1f} °C")
        self.lbl_vccint.setText(f"VCCINT: {v_dut:.3f} V")
        self.lbl_oven_temp.setText(f"Forno: {t_oven:.1f} °C")
        self.lbl_psu_cmd.setText(f"PSU cmd: — V")
        self.lbl_psu_meas.setText(f"PSU med: {v_psu:.3f} V")
        self.lbl_psu_curr.setText(f"Corrente: {c_psu:.3f} A")
        self.lbl_stability.setText(
            f"DUT Δ={t_dut - target:+.1f}°C  |  {elapsed} s"
        )

    @Slot(int, object)
    def _on_corner_done(self, idx: int, result: CornerResult):
        if idx >= len(self._corner_cells):
            return
        cells = self._corner_cells[idx]
        has_err = result.fail_any or result.wrong_total > 0 or result.errcnt_total > 0

        cells['vccint'].setText(f"{result.vccint_mean:.3f} V")
        cells['slack'].setText(f"{result.slack_mean:.1f}")
        cells['minmax'].setText(f"{result.slack_min} / {result.slack_max}")
        cells['fail'].setText("SIM" if result.fail_any else "NÃO")
        cells['erros'].setText(
            f"W={result.wrong_total} E={result.errcnt_total}"
            if (result.wrong_total or result.errcnt_total)
            else "0"
        )

        if has_err:
            style = _STYLE_ERR
            cells['status'].setText("FALHA")
        else:
            style = _STYLE_OK
            cells['status'].setText("OK")

        for key in ('vccint', 'slack', 'minmax', 'fail', 'erros', 'status'):
            cells[key].setStyleSheet(style)

    @Slot(float, int, bool)
    def _on_sweep_tick(self, v_cmd: float, slack: int, error: bool):
        self.lbl_sweep_v.setText(f"Tensão sweep: {v_cmd:.3f} V")
        self.lbl_sweep_slack.setText(f"Slack: {slack} cnt")

        # Update VCCINT from latest status (sequencer emits status_update first)
        # Use the stored value in the label
        if error:
            self.lbl_sweep_status.setText("ERRO DETECTADO")
            self.lbl_sweep_status.setStyleSheet(_STYLE_ERR)
        else:
            self.lbl_sweep_status.setText("OK")
            self.lbl_sweep_status.setStyleSheet(_STYLE_OK)

    @Slot(bool, str)
    def _on_test_finished(self, had_failure: bool, msg: str):
        self.btn_toggle.setText("INICIAR TESTE")
        self.btn_toggle.setStyleSheet(
            f"background-color: #1e4d2b; color: {_GREEN}; font-weight: bold; "
            "padding: 10px; font-size: 14px; border: 1px solid #40a060; border-radius: 4px;"
        )
        self.btn_toggle.setChecked(False)
        self.test_name_input.setEnabled(True)
        self._refresh_status_bar(running=False)

        self.lbl_failure_result.setText(msg)
        self.lbl_failure_result.setVisible(True)
        if had_failure:
            self.lbl_failure_result.setStyleSheet(
                f"color: {_RED}; background-color: #2e1a1a; "
                "padding: 8px; border-radius: 6px; font-weight: bold; font-size: 13px; "
                "border: 2px solid #c04060;"
            )
        else:
            self.lbl_failure_result.setStyleSheet(
                f"color: {_GREEN}; background-color: #1a2e1a; "
                "padding: 8px; border-radius: 6px; font-weight: bold; font-size: 13px; "
                "border: 2px solid #40a060;"
            )

    def closeEvent(self, event):
        self._log("Encerrando aplicação...")
        self.stop_test_signal.emit()
        self.stop_arduino_signal.emit()
        self.stop_psu_signal.emit()
        self.stop_dut_signal.emit()
        for thread in self.threads.values():
            if thread.isRunning():
                thread.quit()
                thread.wait(1000)
        event.accept()
