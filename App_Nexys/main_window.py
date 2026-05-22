"""
App_Nexys — Main window with tabbed layout.

Top bar (always visible):
  [Forno + PID info]  [PSU]  [Controle do Teste]

Tabs:
  Sensor      — slack, failure indicator, canary metrics, DUT readings
  Temperatura — temperature plot
  Tensão      — voltage/current aux plot
  Log         — event log
"""
import time
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QGroupBox, QFormLayout, QLineEdit, QTextEdit,
    QLabel, QDoubleSpinBox, QTabWidget
)
from PySide6.QtGui import QFont
from PySide6.QtCore import QThread, Signal, Slot

import config
from workers import ArduinoWorker, PSUWorker, DUTWorker, TestSequencer
from plot_widget import PlotWidget
from aux_plot_widget import AuxPlotWidget


_STYLE_GREEN = """
QLabel {
    color: #00ff00; background-color: #1a1a1a;
    border: 2px solid #333333; border-radius: 6px; padding: 10px;
}"""
_STYLE_RED = """
QLabel {
    color: #ff4444; background-color: #1a1a1a;
    border: 2px solid #ff0000; border-radius: 6px; padding: 10px;
}"""


class MainWindow(QMainWindow):
    start_arduino_signal = Signal()
    stop_arduino_signal = Signal()
    start_psu_signal = Signal()
    stop_psu_signal = Signal()
    start_dut_signal = Signal()
    stop_dut_signal = Signal()

    start_test_signal = Signal(dict)
    stop_test_signal = Signal()

    update_psu_voltage_signal = Signal(float)
    update_oven_setpoint_signal = Signal(float)
    psu_beeper_signal = Signal(bool)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("App Nexys — Supervisor de Envelhecimento")
        self.setGeometry(100, 100, 1400, 900)

        self.threads = {}
        self.workers = {}

        self._create_top_bar_widgets()
        self._create_tab_widgets()
        self._create_layout()
        self._apply_device_state()
        self._start_device_workers()
        self._start_test_sequencer()
        self._connect_signals()

    # =========================================================================
    #   Widget creation
    # =========================================================================

    def _create_top_bar_widgets(self):
        self.test_control_group = QGroupBox("Controle do Teste")
        self.test_name_input = QLineEdit("Teste_001")
        self.toggle_test_button = QPushButton("INICIAR TESTE")
        self.toggle_test_button.setCheckable(True)
        self.toggle_test_button.setStyleSheet(
            "background-color: #28a745; color: white; font-weight: bold; "
            "padding: 10px; font-size: 14px;"
        )

        self.oven_control_group = QGroupBox("Parâmetros do Forno")
        self.oven_setpoint_input = QDoubleSpinBox()
        self.oven_setpoint_input.setRange(25.0, 150.0)
        self.oven_setpoint_input.setValue(100.0)
        self.oven_setpoint_input.setSuffix(" °C")
        self.dut_target_input = QDoubleSpinBox()
        self.dut_target_input.setRange(0.0, 140.0)
        self.dut_target_input.setValue(0.0)
        self.dut_target_input.setSuffix(" °C")
        self.dut_target_input.setToolTip(
            "Temperatura alvo do DUT. 0 = desabilitado. Ajuste ±1°C/30 min até ±3°C do alvo."
        )
        self.pid_info_label = QLabel(
            f"<b>PID (Fixo):</b> Kp={config.PID_KP:.4f}  "
            f"Ki={config.PID_KI:.6f}  Kd={config.PID_KD:.4f}"
        )
        self.pid_info_label.setStyleSheet(
            "background-color: #2d2d2d; padding: 6px; border-radius: 4px;"
        )

        self.psu_control_group = QGroupBox("Fonte PSU (E3634A)")
        self.psu_setpoint_input = QDoubleSpinBox()
        self.psu_setpoint_input.setRange(0.0, 1.5)
        self.psu_setpoint_input.setValue(config.VCCINT_SETPOINT_V)
        self.psu_setpoint_input.setSingleStep(0.05)
        self.psu_setpoint_input.setDecimals(3)
        self.psu_setpoint_input.setSuffix(" V")
        self.psu_setpoint_input.setToolTip(
            "Alvo VCCINT. O loop P-only ajusta a saída da PSU a cada tick "
            f"com Kp={config.VOLTAGE_KP} V/V."
        )
        self.beeper_button = QPushButton("Silenciar Buzzer PSU")
        self.beeper_button.setCheckable(True)

    def _create_tab_widgets(self):
        # --- Sensor tab ---
        self.slack_label = QLabel("Slack: -- Inc.")
        f = QFont()
        f.setPointSize(22)
        f.setBold(True)
        self.slack_label.setFont(f)
        self.slack_label.setStyleSheet(_STYLE_GREEN)
        self.slack_label.setMinimumHeight(60)

        self.failure_label = QLabel("FALHA: ---")
        f2 = QFont()
        f2.setPointSize(18)
        f2.setBold(True)
        self.failure_label.setFont(f2)
        self.failure_label.setStyleSheet(_STYLE_GREEN)
        self.failure_label.setMinimumHeight(50)

        _info_style = (
            "QLabel { color: #dddddd; background-color: #222222; "
            "border: 1px solid #444; border-radius: 4px; padding: 8px; }"
        )
        self.dut_temp_label = QLabel("Temp DUT:  -- °C")
        self.dut_volt_label = QLabel("VCCINT:  -- V")
        for lbl in (self.dut_temp_label, self.dut_volt_label):
            f3 = QFont()
            f3.setPointSize(13)
            lbl.setFont(f3)
            lbl.setStyleSheet(_info_style)

        _canary_style = (
            "QLabel { color: #aaaaaa; background-color: #222222; "
            "border: 1px solid #444; border-radius: 4px; padding: 6px; }"
        )
        self.error_count_label = QLabel("Erros: --")
        self.wrong_label       = QLabel("Errado: --")
        self.correct_label     = QLabel("Correto: --")
        for lbl in (self.error_count_label, self.wrong_label, self.correct_label):
            lbl.setStyleSheet(_canary_style)

        # --- Other tabs ---
        self.plot_widget = PlotWidget(plot_window_size=300)
        self.aux_plot_widget = AuxPlotWidget(plot_window_size=300)
        self.log_text_edit = QTextEdit()
        self.log_text_edit.setReadOnly(True)
        self.log_text_edit.setStyleSheet(
            "font-family: 'Consolas', 'Monaco', monospace; font-size: 11px;"
        )

    # =========================================================================
    #   Layout
    # =========================================================================

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
        self.oven_control_group.setLayout(oven_inner)
        top_bar.addWidget(self.oven_control_group, stretch=2)

        psu_form = QFormLayout()
        psu_form.addRow("VCCINT Alvo:", self.psu_setpoint_input)
        psu_inner = QVBoxLayout()
        psu_inner.addLayout(psu_form)
        psu_inner.addWidget(self.beeper_button)
        psu_inner.addStretch()
        self.psu_control_group.setLayout(psu_inner)
        top_bar.addWidget(self.psu_control_group, stretch=1)

        test_form = QFormLayout()
        test_form.addRow("Nome:", self.test_name_input)
        test_form.addRow(self.toggle_test_button)
        test_form.addRow(QLabel(f"<small>Logs: {config.LOG_FOLDER}</small>"))
        self.test_control_group.setLayout(test_form)
        top_bar.addWidget(self.test_control_group, stretch=1)

        root.addLayout(top_bar)

        # Tab widget
        tabs = QTabWidget()

        # Tab 1: Sensor
        sensor_widget = QWidget()
        sensor_layout = QVBoxLayout(sensor_widget)
        sensor_layout.setSpacing(10)

        readings_row = QHBoxLayout()
        readings_row.addWidget(self.slack_label, stretch=2)
        readings_row.addWidget(self.failure_label, stretch=1)
        sensor_layout.addLayout(readings_row)

        dut_row = QHBoxLayout()
        dut_row.addWidget(self.dut_temp_label)
        dut_row.addWidget(self.dut_volt_label)
        sensor_layout.addLayout(dut_row)

        canary_group = QGroupBox("Canário de Envelhecimento (Adder Canary)")
        canary_row = QHBoxLayout()
        canary_row.addWidget(self.error_count_label)
        canary_row.addWidget(self.wrong_label)
        canary_row.addWidget(self.correct_label)
        canary_group.setLayout(canary_row)
        sensor_layout.addWidget(canary_group)
        sensor_layout.addStretch()

        tabs.addTab(sensor_widget, "Sensor")

        # Tab 2: Temperatura
        tabs.addTab(self.plot_widget, "Temperatura")

        # Tab 3: Tensão
        tabs.addTab(self.aux_plot_widget, "Tensão")

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
    #   Device state / workers
    # =========================================================================

    def _apply_device_state(self):
        if not config.ARDUINO_ENABLED:
            self.oven_control_group.setEnabled(False)
            self.oven_control_group.setToolTip("Arduino não habilitado — configure no Setup")
        if not config.PSU_ENABLED:
            self.psu_setpoint_input.setEnabled(False)
            self.beeper_button.setEnabled(False)

    def _start_worker(self, name, worker_class_or_instance):
        thread = QThread()
        if isinstance(worker_class_or_instance, type):
            worker = worker_class_or_instance()
        else:
            worker = worker_class_or_instance
        worker.moveToThread(thread)
        worker.log_message.connect(self.log_message)
        self.threads[name] = thread
        self.workers[name] = worker
        thread.start()
        return worker

    def _start_device_workers(self):
        arduino_worker = self._start_worker("arduino", ArduinoWorker)
        self.start_arduino_signal.connect(arduino_worker.start)
        self.stop_arduino_signal.connect(arduino_worker.stop)
        self.update_oven_setpoint_signal.connect(arduino_worker.set_target_setpoint)
        self.start_arduino_signal.emit()

        psu_worker = self._start_worker("psu", PSUWorker)
        self.start_psu_signal.connect(psu_worker.start)
        self.stop_psu_signal.connect(psu_worker.stop)
        self.update_psu_voltage_signal.connect(psu_worker.set_voltage)
        self.psu_beeper_signal.connect(psu_worker.set_beeper)
        self.start_psu_signal.emit()

        dut_worker = self._start_worker("dut", DUTWorker)
        self.start_dut_signal.connect(dut_worker.start)
        self.stop_dut_signal.connect(dut_worker.stop)
        self.start_dut_signal.emit()

    def _start_test_sequencer(self):
        sequencer_worker = TestSequencer(
            self.workers["arduino"],
            self.workers["psu"],
            self.workers["dut"]
        )
        self._start_worker("sequencer", sequencer_worker)
        self.start_test_signal.connect(sequencer_worker.start_test)
        self.stop_test_signal.connect(sequencer_worker.stop_test)
        sequencer_worker.plot_data_update.connect(self.plot_widget.update_plot_data)
        sequencer_worker.plot_data_update.connect(self.aux_plot_widget.update_plot_data)
        sequencer_worker.plot_data_update.connect(self._update_sensor_display)
        sequencer_worker.test_finished.connect(self.on_test_finished)

    def _connect_signals(self):
        self.toggle_test_button.clicked.connect(self.on_toggle_test)
        self.psu_setpoint_input.editingFinished.connect(self.on_update_psu_voltage)
        self.oven_setpoint_input.editingFinished.connect(self.on_update_oven_setpoint)
        self.beeper_button.clicked.connect(self._on_beeper_toggled)

    # =========================================================================
    #   Slots
    # =========================================================================

    @Slot(str)
    def log_message(self, message):
        ts = time.strftime('%H:%M:%S')
        self.log_text_edit.append(f"[{ts}] {message}")

    @Slot(dict)
    def _update_sensor_display(self, d: dict):
        slack       = d.get("dut_slack", 0)
        failure     = d.get("dut_fail", 0)
        temp        = d.get("dut_temp", 0.0)
        volt        = d.get("dut_volt", 0.0)
        error_count = d.get("dut_error_count", 0)
        wrong       = d.get("dut_wrong", 0)
        correct     = d.get("dut_correct", 0)

        self.slack_label.setText(f"Slack: {slack} Inc.")
        self.slack_label.setStyleSheet(_STYLE_RED if 0 < slack < 20 else _STYLE_GREEN)

        if failure:
            self.failure_label.setText("FALHA: SIM")
            self.failure_label.setStyleSheet(_STYLE_RED)
        else:
            self.failure_label.setText("FALHA: NÃO")
            self.failure_label.setStyleSheet(_STYLE_GREEN)

        self.dut_temp_label.setText(f"Temp DUT:  {temp:.1f} °C")
        self.dut_volt_label.setText(f"VCCINT:  {volt:.3f} V")
        self.error_count_label.setText(f"Erros: {error_count}")
        self.wrong_label.setText(f"Errado: {wrong}")
        self.correct_label.setText(f"Correto: {correct}")

    @Slot(bool)
    def on_toggle_test(self, checked):
        if checked:
            self.log_message("Preparando teste...")
            settings = {
                'test_name':       self.test_name_input.text(),
                'oven_setpoint':   self.oven_setpoint_input.value(),
                'psu_voltage':     self.psu_setpoint_input.value(),
                'dut_target_temp': self.dut_target_input.value(),
            }
            self.plot_widget.clear_plot()
            self.aux_plot_widget.clear_plot()
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
    def on_update_psu_voltage(self):
        voltage = self.psu_setpoint_input.value()
        config.VCCINT_SETPOINT_V = voltage
        self.log_message(f"VCCINT alvo atualizado: {voltage:.3f}V")
        self.update_psu_voltage_signal.emit(voltage)

    @Slot()
    def on_update_oven_setpoint(self):
        setpoint = self.oven_setpoint_input.value()
        self.log_message(f"Atualizando setpoint forno: {setpoint:.1f}°C")
        self.update_oven_setpoint_signal.emit(setpoint)

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
    def _on_beeper_toggled(self, checked: bool):
        self.psu_beeper_signal.emit(not checked)
        if checked:
            self.beeper_button.setText("Buzzer PSU: SILENCIADO")
            self.beeper_button.setStyleSheet("background-color: #856404; color: white;")
        else:
            self.beeper_button.setText("Silenciar Buzzer PSU")
            self.beeper_button.setStyleSheet("")

    def closeEvent(self, event):
        self.log_message("Encerrando aplicação...")
        self.stop_test_signal.emit()
        self.stop_arduino_signal.emit()
        self.stop_psu_signal.emit()
        self.stop_dut_signal.emit()
        for thread in self.threads.values():
            if thread.isRunning():
                thread.quit()
                thread.wait(1000)
        event.accept()
