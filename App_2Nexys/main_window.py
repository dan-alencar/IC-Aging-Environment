"""
App_2Nexys — Main window.

Layout (side-by-side dual-DUT):
  ┌──────────────────────────────────────────────────────────────────────┐
  │  Oven controls (setpoint, PID info) | Test control (name, button)   │
  ├──────────────────────────────────────┬───────────────────────────────┤
  │ DUT-0 panel                          │ DUT-1 panel                   │
  │   PSU-0 initial voltage              │   PSU-1 initial voltage       │
  │   Slack-0 / Temp-0 / VCCINT-0        │   Slack-1 / Temp-1 / VCCINT-1│
  ├──────────────────────────────────────┴───────────────────────────────┤
  │ Shared temperature plot (Forno + DUT-0 + DUT-1)                      │
  ├──────────────────────────────────────┬───────────────────────────────┤
  │ Aux plot PSU-0 / VCCINT-0            │ Aux plot PSU-1 / VCCINT-1    │
  ├──────────────────────────────────────┴───────────────────────────────┤
  │ Log display (full width)                                              │
  └──────────────────────────────────────────────────────────────────────┘

Workers live in QThreads; signals cross thread boundaries safely.
The TestSequencer emits plot_data_update(dict) every LOG_INTERVAL_MS.
main_window.py remaps dict keys so each AuxPlotWidget gets generic names.
"""
import time
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QPushButton, QGroupBox, QFormLayout, QLineEdit, QTextEdit,
    QLabel, QDoubleSpinBox
)
from PySide6.QtGui import QFont
from PySide6.QtCore import QThread, Signal, Slot, Qt
import config
from workers import (
    ArduinoWorker, PSUWorker0, PSUWorker1,
    DUTWorker0, DUTWorker1, TestSequencer
)
from plot_widget import PlotWidget
from aux_plot_widget import AuxPlotWidget

_SLACK_STYLE_OK = """
QLabel {
    color: #00ff00; background-color: #1a1a1a;
    border: 2px solid #333333; border-radius: 6px; padding: 8px;
}"""
_SLACK_STYLE_WARN = """
QLabel {
    color: #ff4444; background-color: #1a1a1a;
    border: 2px solid #ff0000; border-radius: 6px; padding: 8px;
}"""


class MainWindow(QMainWindow):
    # Worker control signals
    start_arduino_signal = Signal()
    stop_arduino_signal = Signal()
    start_psu0_signal = Signal()
    stop_psu0_signal = Signal()
    start_psu1_signal = Signal()
    stop_psu1_signal = Signal()
    start_dut0_signal = Signal()
    stop_dut0_signal = Signal()
    start_dut1_signal = Signal()
    stop_dut1_signal = Signal()

    # Test lifecycle
    start_test_signal = Signal(dict)
    stop_test_signal = Signal()

    # Real-time oven setpoint (forwarded to ArduinoWorker)
    update_oven_setpoint_signal = Signal(float)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("App 2-Nexys — Supervisor de Envelhecimento (2 DUTs)")
        self.setGeometry(80, 80, 1600, 950)

        self.threads = {}
        self.workers = {}

        self._create_widgets()
        self._create_layout()
        self._apply_device_state()
        self._start_device_workers()
        self._start_test_sequencer()
        self._connect_ui_signals()

    # =========================================================================
    #   Widget creation
    # =========================================================================

    def _create_widgets(self):
        # --- Test control ---
        self.test_control_group = QGroupBox("Controle do Teste")
        self.test_name_input = QLineEdit("Teste_2DUT_001")
        self.toggle_test_button = QPushButton("INICIAR TESTE")
        self.toggle_test_button.setCheckable(True)
        self.toggle_test_button.setStyleSheet(
            "background-color: #28a745; color: white; font-weight: bold; "
            "padding: 10px; font-size: 14px;"
        )

        # --- Oven ---
        self.oven_group = QGroupBox("Forno (compartilhado)")
        self.oven_setpoint_input = QDoubleSpinBox()
        self.oven_setpoint_input.setRange(25.0, 150.0)
        self.oven_setpoint_input.setValue(100.0)
        self.oven_setpoint_input.setSuffix(" °C")
        self.pid_info_label = QLabel(
            f"<b>PID Forno (Fixo):</b><br>"
            f"Kp={config.PID_KP:.4f}  Ki={config.PID_KI:.6f}  Kd={config.PID_KD:.4f}"
        )
        self.pid_info_label.setStyleSheet(
            "background-color: #2d2d2d; padding: 6px; border-radius: 4px;"
        )
        self.dut_target_input = QDoubleSpinBox()
        self.dut_target_input.setRange(0.0, 140.0)
        self.dut_target_input.setValue(0.0)
        self.dut_target_input.setSuffix(" °C")
        self.dut_target_input.setToolTip(
            "Temperatura alvo dos DUTs (média de DUT-0 e DUT-1). "
            "0 = desabilitado — usa setpoint do forno diretamente. "
            "Ajuste de ±1°C/30 min até ±3°C do alvo."
        )

        # --- DUT-0 panel ---
        self.dut0_group = QGroupBox("DUT-0  (IT6502D)")
        self.psu0_voltage_input = QDoubleSpinBox()
        self.psu0_voltage_input.setRange(0.0, 1.5)
        self.psu0_voltage_input.setValue(config.VCCINT_SETPOINT_0_V)
        self.psu0_voltage_input.setSingleStep(0.05)
        self.psu0_voltage_input.setSuffix(" V")
        self.psu0_voltage_input.setToolTip(
            "Tensão inicial da PSU-0. O loop VCCINT ajusta automaticamente."
        )
        self.slack0_label = self._make_slack_label()
        self.dut0_info_label = QLabel("Temp: -- °C   VCCINT: -- V")

        # --- DUT-1 panel ---
        self.dut1_group = QGroupBox("DUT-1  (E3634A)")
        self.psu1_voltage_input = QDoubleSpinBox()
        self.psu1_voltage_input.setRange(0.0, 1.5)
        self.psu1_voltage_input.setValue(config.VCCINT_SETPOINT_1_V)
        self.psu1_voltage_input.setSingleStep(0.05)
        self.psu1_voltage_input.setSuffix(" V")
        self.psu1_voltage_input.setToolTip(
            "Tensão inicial da PSU-1. O loop VCCINT ajusta automaticamente."
        )
        self.slack1_label = self._make_slack_label()
        self.dut1_info_label = QLabel("Temp: -- °C   VCCINT: -- V")

        # --- Plots ---
        self.plot_widget = PlotWidget(plot_window_size=300)
        self.aux_plot0 = AuxPlotWidget(title="PSU-0 / VCCINT-0", plot_window_size=300)
        self.aux_plot1 = AuxPlotWidget(title="PSU-1 / VCCINT-1", plot_window_size=300)

        # --- Log ---
        self.log_group = QGroupBox("Log de Eventos")
        self.log_text_edit = QTextEdit()
        self.log_text_edit.setReadOnly(True)
        self.log_text_edit.setMaximumHeight(160)
        self.log_text_edit.setStyleSheet(
            "font-family: 'Consolas', 'Monaco', monospace; font-size: 10px;"
        )

    def _make_slack_label(self):
        lbl = QLabel("Slack: -- Inc.")
        f = QFont()
        f.setPointSize(14)
        f.setBold(True)
        lbl.setFont(f)
        lbl.setStyleSheet(_SLACK_STYLE_OK)
        return lbl

    # =========================================================================
    #   Layout
    # =========================================================================

    def _create_layout(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(6)

        # --- Top bar: oven + test control ---
        top_bar = QHBoxLayout()

        oven_form = QFormLayout()
        oven_form.addRow("Setpoint:", self.oven_setpoint_input)
        oven_form.addRow("Alvo DUT (0=off):", self.dut_target_input)
        oven_inner = QVBoxLayout()
        oven_inner.addLayout(oven_form)
        oven_inner.addWidget(self.pid_info_label)
        self.oven_group.setLayout(oven_inner)
        top_bar.addWidget(self.oven_group, stretch=1)

        test_form = QFormLayout()
        test_form.addRow("Nome:", self.test_name_input)
        test_form.addRow(self.toggle_test_button)
        test_form.addRow(QLabel(f"<small>Logs: {config.LOG_FOLDER}</small>"))
        self.test_control_group.setLayout(test_form)
        top_bar.addWidget(self.test_control_group, stretch=1)

        main_layout.addLayout(top_bar)

        # --- DUT panels (side-by-side) ---
        dut_row = QHBoxLayout()

        dut0_inner = QVBoxLayout()
        dut0_form = QFormLayout()
        dut0_form.addRow("Tensão inicial PSU-0:", self.psu0_voltage_input)
        dut0_inner.addLayout(dut0_form)
        dut0_inner.addWidget(QLabel("<b>Sensor de Degradação — DUT-0:</b>"))
        dut0_inner.addWidget(self.slack0_label)
        dut0_inner.addWidget(self.dut0_info_label)
        self.dut0_group.setLayout(dut0_inner)
        dut_row.addWidget(self.dut0_group, stretch=1)

        dut1_inner = QVBoxLayout()
        dut1_form = QFormLayout()
        dut1_form.addRow("Tensão inicial PSU-1:", self.psu1_voltage_input)
        dut1_inner.addLayout(dut1_form)
        dut1_inner.addWidget(QLabel("<b>Sensor de Degradação — DUT-1:</b>"))
        dut1_inner.addWidget(self.slack1_label)
        dut1_inner.addWidget(self.dut1_info_label)
        self.dut1_group.setLayout(dut1_inner)
        dut_row.addWidget(self.dut1_group, stretch=1)

        main_layout.addLayout(dut_row)

        # --- Shared temperature plot ---
        main_layout.addWidget(self.plot_widget, stretch=2)

        # --- Aux plots ---
        aux_row = QHBoxLayout()
        aux_row.addWidget(self.aux_plot0, stretch=1)
        aux_row.addWidget(self.aux_plot1, stretch=1)
        main_layout.addLayout(aux_row, stretch=1)

        # --- Log ---
        log_inner = QVBoxLayout()
        log_inner.addWidget(self.log_text_edit)
        self.log_group.setLayout(log_inner)
        main_layout.addWidget(self.log_group)

        central = QWidget()
        central.setLayout(main_layout)
        self.setCentralWidget(central)

    # =========================================================================
    #   Device state
    # =========================================================================

    def _apply_device_state(self):
        if not config.ARDUINO_ENABLED:
            self.oven_group.setEnabled(False)
            self.oven_group.setToolTip("Arduino não habilitado")
        if not config.PSU_0_ENABLED:
            self.psu0_voltage_input.setEnabled(False)
        if not config.PSU_1_ENABLED:
            self.psu1_voltage_input.setEnabled(False)

    # =========================================================================
    #   Worker lifecycle
    # =========================================================================

    def _start_worker(self, name, worker):
        thread = QThread()
        worker.moveToThread(thread)
        worker.log_message.connect(self.log_message)
        self.threads[name] = thread
        self.workers[name] = worker
        thread.start()
        return worker

    def _start_device_workers(self):
        arduino = self._start_worker("arduino", ArduinoWorker())
        self.start_arduino_signal.connect(arduino.start)
        self.stop_arduino_signal.connect(arduino.stop)
        self.update_oven_setpoint_signal.connect(arduino.set_target_setpoint)
        self.start_arduino_signal.emit()

        psu0 = self._start_worker("psu0", PSUWorker0())
        self.start_psu0_signal.connect(psu0.start)
        self.stop_psu0_signal.connect(psu0.stop)
        self.start_psu0_signal.emit()

        psu1 = self._start_worker("psu1", PSUWorker1())
        self.start_psu1_signal.connect(psu1.start)
        self.stop_psu1_signal.connect(psu1.stop)
        self.start_psu1_signal.emit()

        dut0 = self._start_worker("dut0", DUTWorker0())
        self.start_dut0_signal.connect(dut0.start)
        self.stop_dut0_signal.connect(dut0.stop)
        self.start_dut0_signal.emit()

        dut1 = self._start_worker("dut1", DUTWorker1())
        self.start_dut1_signal.connect(dut1.start)
        self.stop_dut1_signal.connect(dut1.stop)
        self.start_dut1_signal.emit()

    def _start_test_sequencer(self):
        seq = TestSequencer(
            self.workers["arduino"],
            self.workers["psu0"], self.workers["psu1"],
            self.workers["dut0"], self.workers["dut1"],
        )
        self._start_worker("sequencer", seq)
        self.start_test_signal.connect(seq.start_test)
        self.stop_test_signal.connect(seq.stop_test)

        seq.plot_data_update.connect(self.plot_widget.update_plot_data)
        seq.plot_data_update.connect(self._forward_to_aux0)
        seq.plot_data_update.connect(self._forward_to_aux1)
        seq.plot_data_update.connect(self._update_dut_displays)
        seq.test_finished.connect(self.on_test_finished)

    # =========================================================================
    #   Signal routing helpers
    # =========================================================================

    @Slot(dict)
    def _forward_to_aux0(self, d: dict):
        """Remap psu0_* keys to generic names expected by AuxPlotWidget."""
        self.aux_plot0.update_plot_data({
            "time_sec":   d.get("time_sec", 0),
            "psu_voltage": d.get("psu0_voltage", 0),
            "psu_cmd_v":  d.get("psu0_cmd_v", 0),
            "dut_volt":   d.get("dut0_volt", 0),
            "psu_current": d.get("psu0_current", 0),
        })

    @Slot(dict)
    def _forward_to_aux1(self, d: dict):
        """Remap psu1_* keys to generic names expected by AuxPlotWidget."""
        self.aux_plot1.update_plot_data({
            "time_sec":   d.get("time_sec", 0),
            "psu_voltage": d.get("psu1_voltage", 0),
            "psu_cmd_v":  d.get("psu1_cmd_v", 0),
            "dut_volt":   d.get("dut1_volt", 0),
            "psu_current": d.get("psu1_current", 0),
        })

    # =========================================================================
    #   UI signal connections
    # =========================================================================

    def _connect_ui_signals(self):
        self.toggle_test_button.clicked.connect(self.on_toggle_test)
        self.oven_setpoint_input.editingFinished.connect(self.on_update_oven_setpoint)

    # =========================================================================
    #   Slots
    # =========================================================================

    @Slot(str)
    def log_message(self, message: str):
        ts = time.strftime("%H:%M:%S")
        self.log_text_edit.append(f"[{ts}] {message}")

    @Slot(dict)
    def _update_dut_displays(self, d: dict):
        """Update slack labels and info text for both DUTs."""
        s0 = d.get("dut0_slack", 0)
        s1 = d.get("dut1_slack", 0)
        t0 = d.get("dut0_temp", 0.0)
        t1 = d.get("dut1_temp", 0.0)
        v0 = d.get("dut0_volt", 0.0)
        v1 = d.get("dut1_volt", 0.0)

        self.slack0_label.setText(f"Slack: {s0} Inc.")
        self.slack0_label.setStyleSheet(_SLACK_STYLE_WARN if 0 < s0 < 20 else _SLACK_STYLE_OK)
        self.dut0_info_label.setText(f"Temp: {t0:.1f} °C   VCCINT: {v0:.3f} V")

        self.slack1_label.setText(f"Slack: {s1} Inc.")
        self.slack1_label.setStyleSheet(_SLACK_STYLE_WARN if 0 < s1 < 20 else _SLACK_STYLE_OK)
        self.dut1_info_label.setText(f"Temp: {t1:.1f} °C   VCCINT: {v1:.3f} V")

    @Slot(bool)
    def on_toggle_test(self, checked: bool):
        if checked:
            self.log_message("Preparando teste (2 DUTs)...")
            settings = {
                "test_name":       self.test_name_input.text(),
                "oven_setpoint":   self.oven_setpoint_input.value(),
                "psu0_voltage":    self.psu0_voltage_input.value(),
                "psu1_voltage":    self.psu1_voltage_input.value(),
                "vccint_sp0":      config.VCCINT_SETPOINT_0_V,
                "vccint_sp1":      config.VCCINT_SETPOINT_1_V,
                "dut_target_temp": self.dut_target_input.value(),
            }
            self.plot_widget.clear_plot()
            self.aux_plot0.clear_plot()
            self.aux_plot1.clear_plot()
            self.start_test_signal.emit(settings)
            self.toggle_test_button.setText("PARAR TESTE")
            self.toggle_test_button.setStyleSheet(
                "background-color: #dc3545; color: white; font-weight: bold; "
                "padding: 10px; font-size: 14px;"
            )
            self.test_name_input.setEnabled(False)
        else:
            self.stop_test_signal.emit()
            self.on_test_finished()

    @Slot()
    def on_update_oven_setpoint(self):
        sp = self.oven_setpoint_input.value()
        self.log_message(f"Setpoint forno: {sp:.1f}°C")
        self.update_oven_setpoint_signal.emit(sp)

    @Slot()
    def on_test_finished(self):
        self.toggle_test_button.setText("INICIAR TESTE")
        self.toggle_test_button.setStyleSheet(
            "background-color: #28a745; color: white; font-weight: bold; "
            "padding: 10px; font-size: 14px;"
        )
        self.toggle_test_button.setChecked(False)
        self.test_name_input.setEnabled(True)

    def closeEvent(self, event):
        self.log_message("Encerrando aplicação...")
        self.stop_test_signal.emit()
        self.stop_arduino_signal.emit()
        self.stop_psu0_signal.emit()
        self.stop_psu1_signal.emit()
        self.stop_dut0_signal.emit()
        self.stop_dut1_signal.emit()
        for thread in self.threads.values():
            if thread.isRunning():
                thread.quit()
                thread.wait(1000)
        event.accept()
