"""
App_2Nexys — Main window with tabbed layout.

Top bar (always visible):
  [Forno (setpoint, PID info, DUT target)]  [Controle do Teste]

Tabs:
  Sensor      — DUT-0 and DUT-1 side-by-side (slack, failure, canary, PSU inputs)
  Temperatura — shared temperature plot
  Tensão      — PSU-0 and PSU-1 voltage/current aux plots side-by-side
  Log         — event log

Workers live in QThreads; signals cross thread boundaries safely.
"""
import time
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QGroupBox, QFormLayout, QLineEdit, QTextEdit,
    QLabel, QDoubleSpinBox, QTabWidget, QFrame
)
from PySide6.QtGui import QFont
from PySide6.QtCore import QThread, Signal, Slot
import config
from workers import (
    ArduinoWorker, PSUWorker0, PSUWorker1,
    DUTWorker0, DUTWorker1, TestSequencer
)
from plot_widget import PlotWidget
from aux_plot_widget import AuxPlotWidget


_STYLE_GREEN = """
QLabel {
    color: #00ff00; background-color: #1a1a1a;
    border: 2px solid #333333; border-radius: 6px; padding: 8px;
}"""
_STYLE_RED = """
QLabel {
    color: #ff4444; background-color: #1a1a1a;
    border: 2px solid #ff0000; border-radius: 6px; padding: 8px;
}"""
_INFO_STYLE = (
    "QLabel { color: #dddddd; background-color: #222222; "
    "border: 1px solid #444; border-radius: 4px; padding: 6px; }"
)
_CANARY_STYLE = (
    "QLabel { color: #aaaaaa; background-color: #222222; "
    "border: 1px solid #444; border-radius: 4px; padding: 6px; }"
)


class MainWindow(QMainWindow):
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

    start_test_signal = Signal(dict)
    stop_test_signal = Signal()

    update_oven_setpoint_signal = Signal(float)
    psu0_beeper_signal = Signal(bool)
    psu1_beeper_signal = Signal(bool)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("App 2-Nexys — Supervisor de Envelhecimento (2 DUTs)")
        self.setGeometry(80, 80, 1600, 950)

        self.threads = {}
        self.workers = {}

        self._create_top_bar_widgets()
        self._create_tab_widgets()
        self._create_layout()
        self._apply_device_state()
        self._start_device_workers()
        self._start_test_sequencer()
        self._connect_ui_signals()

    # =========================================================================
    #   Widget creation
    # =========================================================================

    def _create_top_bar_widgets(self):
        self.oven_group = QGroupBox("Forno (compartilhado)")
        self.oven_setpoint_input = QDoubleSpinBox()
        self.oven_setpoint_input.setRange(25.0, 150.0)
        self.oven_setpoint_input.setValue(100.0)
        self.oven_setpoint_input.setSuffix(" °C")
        self.dut_target_input = QDoubleSpinBox()
        self.dut_target_input.setRange(0.0, 140.0)
        self.dut_target_input.setValue(0.0)
        self.dut_target_input.setSuffix(" °C")
        self.dut_target_input.setToolTip(
            "Temperatura alvo dos DUTs (média). 0 = desabilitado. "
            "Ajuste ±1°C/30 min até ±3°C do alvo."
        )
        self.pid_info_label = QLabel(
            f"<b>PID (Fixo):</b> Kp={config.PID_KP:.4f}  "
            f"Ki={config.PID_KI:.6f}  Kd={config.PID_KD:.4f}"
        )
        self.pid_info_label.setStyleSheet(
            "background-color: #2d2d2d; padding: 6px; border-radius: 4px;"
        )

        self.test_control_group = QGroupBox("Controle do Teste")
        self.test_name_input = QLineEdit("Teste_2DUT_001")
        self.toggle_test_button = QPushButton("INICIAR TESTE")
        self.toggle_test_button.setCheckable(True)
        self.toggle_test_button.setStyleSheet(
            "background-color: #28a745; color: white; font-weight: bold; "
            "padding: 10px; font-size: 14px;"
        )

    def _make_big_label(self, text: str, style: str) -> QLabel:
        lbl = QLabel(text)
        f = QFont()
        f.setPointSize(18)
        f.setBold(True)
        lbl.setFont(f)
        lbl.setStyleSheet(style)
        lbl.setMinimumHeight(50)
        return lbl

    def _create_tab_widgets(self):
        # DUT-0 sensor widgets
        self.slack0_label    = self._make_big_label("Slack: -- Inc.", _STYLE_GREEN)
        self.failure0_label  = self._make_big_label("FALHA: ---",     _STYLE_GREEN)
        self.dut0_temp_label = QLabel("Temp: -- °C")
        self.dut0_volt_label = QLabel("VCCINT: -- V")
        for lbl in (self.dut0_temp_label, self.dut0_volt_label):
            f = QFont(); f.setPointSize(12); lbl.setFont(f)
            lbl.setStyleSheet(_INFO_STYLE)
        self.err0_label     = QLabel("Erros: --")
        self.wrong0_label   = QLabel("Errado: --")
        self.correct0_label = QLabel("Correto: --")
        for lbl in (self.err0_label, self.wrong0_label, self.correct0_label):
            lbl.setStyleSheet(_CANARY_STYLE)

        self.psu0_voltage_input = QDoubleSpinBox()
        self.psu0_voltage_input.setRange(0.0, 1.5)
        self.psu0_voltage_input.setValue(config.VCCINT_SETPOINT_0_V)
        self.psu0_voltage_input.setSingleStep(0.05)
        self.psu0_voltage_input.setSuffix(" V")
        self.psu0_voltage_input.setToolTip(
            "Tensão inicial da PSU-0 (loop VCCINT ajusta automaticamente)"
        )
        self.beeper0_button = QPushButton("Silenciar Buzzer PSU-0")
        self.beeper0_button.setCheckable(True)

        # DUT-1 sensor widgets
        self.slack1_label    = self._make_big_label("Slack: -- Inc.", _STYLE_GREEN)
        self.failure1_label  = self._make_big_label("FALHA: ---",     _STYLE_GREEN)
        self.dut1_temp_label = QLabel("Temp: -- °C")
        self.dut1_volt_label = QLabel("VCCINT: -- V")
        for lbl in (self.dut1_temp_label, self.dut1_volt_label):
            f = QFont(); f.setPointSize(12); lbl.setFont(f)
            lbl.setStyleSheet(_INFO_STYLE)
        self.err1_label     = QLabel("Erros: --")
        self.wrong1_label   = QLabel("Errado: --")
        self.correct1_label = QLabel("Correto: --")
        for lbl in (self.err1_label, self.wrong1_label, self.correct1_label):
            lbl.setStyleSheet(_CANARY_STYLE)

        self.psu1_voltage_input = QDoubleSpinBox()
        self.psu1_voltage_input.setRange(0.0, 1.5)
        self.psu1_voltage_input.setValue(config.VCCINT_SETPOINT_1_V)
        self.psu1_voltage_input.setSingleStep(0.05)
        self.psu1_voltage_input.setSuffix(" V")
        self.psu1_voltage_input.setToolTip(
            "Tensão inicial da PSU-1 (loop VCCINT ajusta automaticamente)"
        )
        self.beeper1_button = QPushButton("Silenciar Buzzer PSU-1")
        self.beeper1_button.setCheckable(True)

        # Other tab widgets
        self.plot_widget = PlotWidget(plot_window_size=300)
        self.aux_plot0 = AuxPlotWidget(title="PSU-0 / VCCINT-0", plot_window_size=300)
        self.aux_plot1 = AuxPlotWidget(title="PSU-1 / VCCINT-1", plot_window_size=300)
        self.log_text_edit = QTextEdit()
        self.log_text_edit.setReadOnly(True)
        self.log_text_edit.setStyleSheet(
            "font-family: 'Consolas', 'Monaco', monospace; font-size: 10px;"
        )

    # =========================================================================
    #   Layout
    # =========================================================================

    def _build_dut_column(self, id_str,
                           slack_lbl, failure_lbl,
                           temp_lbl, volt_lbl,
                           err_lbl, wrong_lbl, correct_lbl,
                           psu_spin, beeper_btn) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(8)

        layout.addWidget(slack_lbl)
        layout.addWidget(failure_lbl)

        info_row = QHBoxLayout()
        info_row.addWidget(temp_lbl)
        info_row.addWidget(volt_lbl)
        layout.addLayout(info_row)

        canary_group = QGroupBox(f"Canário — {id_str}")
        canary_row = QHBoxLayout()
        canary_row.addWidget(err_lbl)
        canary_row.addWidget(wrong_lbl)
        canary_row.addWidget(correct_lbl)
        canary_group.setLayout(canary_row)
        layout.addWidget(canary_group)

        psu_group = QGroupBox(f"PSU — {id_str}")
        psu_form = QFormLayout()
        psu_form.addRow("Tensão inicial:", psu_spin)
        psu_inner = QVBoxLayout()
        psu_inner.addLayout(psu_form)
        psu_inner.addWidget(beeper_btn)
        psu_group.setLayout(psu_inner)
        layout.addWidget(psu_group)

        layout.addStretch()
        return widget

    def _create_layout(self):
        root = QVBoxLayout()
        root.setSpacing(6)

        # Top bar
        top_bar = QHBoxLayout()

        oven_form = QFormLayout()
        oven_form.addRow("Setpoint:", self.oven_setpoint_input)
        oven_form.addRow("Alvo DUT (0=off):", self.dut_target_input)
        oven_inner = QVBoxLayout()
        oven_inner.addLayout(oven_form)
        oven_inner.addWidget(self.pid_info_label)
        self.oven_group.setLayout(oven_inner)
        top_bar.addWidget(self.oven_group, stretch=2)

        test_form = QFormLayout()
        test_form.addRow("Nome:", self.test_name_input)
        test_form.addRow(self.toggle_test_button)
        test_form.addRow(QLabel(f"<small>Logs: {config.LOG_FOLDER}</small>"))
        self.test_control_group.setLayout(test_form)
        top_bar.addWidget(self.test_control_group, stretch=1)

        root.addLayout(top_bar)

        # Tab widget
        tabs = QTabWidget()

        # Tab 1: Sensor — two DUT columns side-by-side
        sensor_widget = QWidget()
        sensor_layout = QHBoxLayout(sensor_widget)
        sensor_layout.setSpacing(12)

        col0 = self._build_dut_column(
            "DUT-0",
            self.slack0_label, self.failure0_label,
            self.dut0_temp_label, self.dut0_volt_label,
            self.err0_label, self.wrong0_label, self.correct0_label,
            self.psu0_voltage_input, self.beeper0_button,
        )
        div = QFrame()
        div.setFrameShape(QFrame.VLine)
        div.setFrameShadow(QFrame.Sunken)
        col1 = self._build_dut_column(
            "DUT-1",
            self.slack1_label, self.failure1_label,
            self.dut1_temp_label, self.dut1_volt_label,
            self.err1_label, self.wrong1_label, self.correct1_label,
            self.psu1_voltage_input, self.beeper1_button,
        )
        sensor_layout.addWidget(col0)
        sensor_layout.addWidget(div)
        sensor_layout.addWidget(col1)

        tabs.addTab(sensor_widget, "Sensor")

        # Tab 2: Temperatura
        tabs.addTab(self.plot_widget, "Temperatura")

        # Tab 3: Tensão — aux plots side-by-side
        volt_widget = QWidget()
        volt_layout = QHBoxLayout(volt_widget)
        volt_layout.addWidget(self.aux_plot0)
        volt_layout.addWidget(self.aux_plot1)
        tabs.addTab(volt_widget, "Tensão")

        # Tab 4: Log
        log_widget = QWidget()
        log_layout = QVBoxLayout(log_widget)
        log_layout.addWidget(self.log_text_edit)
        tabs.addTab(log_widget, "Log")

        root.addWidget(tabs, stretch=1)

        central = QWidget()
        central.setLayout(root)
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
            self.beeper0_button.setEnabled(False)
        if not config.PSU_1_ENABLED:
            self.psu1_voltage_input.setEnabled(False)
            self.beeper1_button.setEnabled(False)

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
        self.psu0_beeper_signal.connect(psu0.set_beeper)
        self.start_psu0_signal.emit()

        psu1 = self._start_worker("psu1", PSUWorker1())
        self.start_psu1_signal.connect(psu1.start)
        self.stop_psu1_signal.connect(psu1.stop)
        self.psu1_beeper_signal.connect(psu1.set_beeper)
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
        seq.plot_data_update.connect(self._update_sensor_display)
        seq.test_finished.connect(self.on_test_finished)

    # =========================================================================
    #   Signal routing helpers
    # =========================================================================

    @Slot(dict)
    def _forward_to_aux0(self, d: dict):
        self.aux_plot0.update_plot_data({
            "time_sec":    d.get("time_sec", 0),
            "psu_voltage": d.get("psu0_voltage", 0),
            "psu_cmd_v":   d.get("psu0_cmd_v", 0),
            "dut_volt":    d.get("dut0_volt", 0),
            "psu_current": d.get("psu0_current", 0),
        })

    @Slot(dict)
    def _forward_to_aux1(self, d: dict):
        self.aux_plot1.update_plot_data({
            "time_sec":    d.get("time_sec", 0),
            "psu_voltage": d.get("psu1_voltage", 0),
            "psu_cmd_v":   d.get("psu1_cmd_v", 0),
            "dut_volt":    d.get("dut1_volt", 0),
            "psu_current": d.get("psu1_current", 0),
        })

    # =========================================================================
    #   UI signal connections
    # =========================================================================

    def _connect_ui_signals(self):
        self.toggle_test_button.clicked.connect(self.on_toggle_test)
        self.oven_setpoint_input.editingFinished.connect(self.on_update_oven_setpoint)
        self.beeper0_button.clicked.connect(self._on_beeper0_toggled)
        self.beeper1_button.clicked.connect(self._on_beeper1_toggled)

    # =========================================================================
    #   Slots
    # =========================================================================

    @Slot(str)
    def log_message(self, message: str):
        ts = time.strftime("%H:%M:%S")
        self.log_text_edit.append(f"[{ts}] {message}")

    @Slot(dict)
    def _update_sensor_display(self, d: dict):
        s0 = d.get("dut0_slack", 0)
        s1 = d.get("dut1_slack", 0)
        f0 = d.get("dut0_fail", 0)
        f1 = d.get("dut1_fail", 0)
        t0 = d.get("dut0_temp", 0.0)
        t1 = d.get("dut1_temp", 0.0)
        v0 = d.get("dut0_volt", 0.0)
        v1 = d.get("dut1_volt", 0.0)
        e0 = d.get("dut0_error_count", 0)
        e1 = d.get("dut1_error_count", 0)
        w0 = d.get("dut0_wrong", 0)
        w1 = d.get("dut1_wrong", 0)
        c0 = d.get("dut0_correct", 0)
        c1 = d.get("dut1_correct", 0)

        self.slack0_label.setText(f"Slack: {s0} Inc.")
        self.slack0_label.setStyleSheet(_STYLE_RED if 0 < s0 < 20 else _STYLE_GREEN)
        self.failure0_label.setText("FALHA: SIM" if f0 else "FALHA: NÃO")
        self.failure0_label.setStyleSheet(_STYLE_RED if f0 else _STYLE_GREEN)
        self.dut0_temp_label.setText(f"Temp: {t0:.1f} °C")
        self.dut0_volt_label.setText(f"VCCINT: {v0:.3f} V")
        self.err0_label.setText(f"Erros: {e0}")
        self.wrong0_label.setText(f"Errado: {w0}")
        self.correct0_label.setText(f"Correto: {c0}")

        self.slack1_label.setText(f"Slack: {s1} Inc.")
        self.slack1_label.setStyleSheet(_STYLE_RED if 0 < s1 < 20 else _STYLE_GREEN)
        self.failure1_label.setText("FALHA: SIM" if f1 else "FALHA: NÃO")
        self.failure1_label.setStyleSheet(_STYLE_RED if f1 else _STYLE_GREEN)
        self.dut1_temp_label.setText(f"Temp: {t1:.1f} °C")
        self.dut1_volt_label.setText(f"VCCINT: {v1:.3f} V")
        self.err1_label.setText(f"Erros: {e1}")
        self.wrong1_label.setText(f"Errado: {w1}")
        self.correct1_label.setText(f"Correto: {c1}")

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

    @Slot(bool)
    def _on_beeper0_toggled(self, checked: bool):
        self.psu0_beeper_signal.emit(not checked)
        if checked:
            self.beeper0_button.setText("Buzzer PSU-0: SILENCIADO")
            self.beeper0_button.setStyleSheet("background-color: #856404; color: white;")
        else:
            self.beeper0_button.setText("Silenciar Buzzer PSU-0")
            self.beeper0_button.setStyleSheet("")

    @Slot(bool)
    def _on_beeper1_toggled(self, checked: bool):
        self.psu1_beeper_signal.emit(not checked)
        if checked:
            self.beeper1_button.setText("Buzzer PSU-1: SILENCIADO")
            self.beeper1_button.setStyleSheet("background-color: #856404; color: white;")
        else:
            self.beeper1_button.setText("Silenciar Buzzer PSU-1")
            self.beeper1_button.setStyleSheet("")

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
