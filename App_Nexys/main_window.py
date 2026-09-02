"""
App_Nexys — Main window with tabbed layout.

Top bar (always visible):
  [Forno + PID info]  [PSU]  [Controle do Teste]

Tabs:
  Sensor      — slack, failure indicator, DUT + oven + PSU live readouts, canary metrics
  Temperatura — temperature plot
  Tensão      — voltage/current aux plot
  Log         — event log
"""
import time
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QGroupBox, QFormLayout, QLineEdit, QTextEdit,
    QLabel, QDoubleSpinBox, QTabWidget, QStatusBar, QSplitter,
    QDialog, QRadioButton, QDialogButtonBox,
)
from PySide6.QtGui import QFont
from PySide6.QtCore import QThread, Signal, Slot, Qt

import config
from workers import ArduinoWorker, PSUWorker, DUTWorker, TestSequencer
from plot_widget import PlotWidget
from aux_plot_widget import AuxPlotWidget
from multi_channel_widget import MultiChannelPanel
from protocol import MULTI_NUM_CHANNELS


# ---------------------------------------------------------------------------
# Colour palette (Catppuccin Mocha)
# ---------------------------------------------------------------------------
_BG       = '#1e1e2e'
_SURFACE  = '#313244'
_OVERLAY  = '#45475a'
_MUTED    = '#6c7086'
_TEXT     = '#cdd6f4'
_SUBTEXT  = '#a6adc8'
_GREEN    = '#a6e3a1'
_RED      = '#f38ba8'
_YELLOW   = '#f9e2af'
_BLUE     = '#89b4fa'
_PURPLE   = '#cba6f7'
_ORANGE   = '#fab387'
_TEAL     = '#89dceb'

_DARK_STYLE = f"""
QMainWindow, QDialog {{
    background-color: {_BG};
}}
QWidget {{
    background-color: {_BG};
    color: {_TEXT};
    font-size: 12px;
}}
QGroupBox {{
    color: {_PURPLE};
    border: 1px solid {_OVERLAY};
    border-radius: 6px;
    margin-top: 10px;
    padding-top: 6px;
    font-weight: bold;
    font-size: 12px;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 6px;
    left: 10px;
}}
QGroupBox:disabled {{
    color: {_MUTED};
    border-color: {_SURFACE};
}}
QTabWidget::pane {{
    border: 1px solid {_OVERLAY};
    border-radius: 4px;
    background-color: {_BG};
    top: -1px;
}}
QTabBar::tab {{
    background-color: {_SURFACE};
    color: {_SUBTEXT};
    border: 1px solid {_OVERLAY};
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    padding: 6px 20px;
    min-width: 80px;
}}
QTabBar::tab:selected {{
    background-color: {_OVERLAY};
    color: {_TEXT};
    font-weight: bold;
}}
QTabBar::tab:hover:!selected {{
    background-color: #3a3a52;
}}
QLineEdit, QDoubleSpinBox, QComboBox, QSpinBox {{
    background-color: {_SURFACE};
    color: {_TEXT};
    border: 1px solid {_OVERLAY};
    border-radius: 4px;
    padding: 3px 6px;
    selection-background-color: {_OVERLAY};
}}
QLineEdit:focus, QDoubleSpinBox:focus {{
    border: 1px solid {_PURPLE};
}}
QLineEdit:disabled, QDoubleSpinBox:disabled {{
    color: {_MUTED};
    background-color: #262637;
}}
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
    background-color: {_OVERLAY};
    border: none;
    width: 16px;
    border-radius: 2px;
}}
QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {{
    background-color: #585b70;
}}
QTextEdit {{
    background-color: #181825;
    color: {_GREEN};
    border: 1px solid {_OVERLAY};
    border-radius: 4px;
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
    font-size: 11px;
}}
QPushButton {{
    background-color: {_OVERLAY};
    color: {_TEXT};
    border: none;
    border-radius: 4px;
    padding: 6px 14px;
    font-size: 12px;
}}
QPushButton:hover {{
    background-color: #585b70;
}}
QPushButton:pressed {{
    background-color: {_SURFACE};
}}
QPushButton:disabled {{
    color: {_MUTED};
    background-color: {_SURFACE};
}}
QStatusBar {{
    background-color: #181825;
    border-top: 1px solid {_OVERLAY};
}}
QStatusBar QLabel {{
    background-color: transparent;
    color: {_MUTED};
    padding: 0 8px;
    font-size: 11px;
}}
"""

# Sensor tab status labels
_STYLE_OK = f"""
QLabel {{
    color: {_GREEN}; background-color: #1a2e1a;
    border: 2px solid #40a060; border-radius: 8px; padding: 12px;
}}"""
_STYLE_WARN = f"""
QLabel {{
    color: {_RED}; background-color: #2e1a1a;
    border: 2px solid #c04060; border-radius: 8px; padding: 12px;
}}"""
_INFO_STYLE = (
    f"QLabel {{ color: {_TEAL}; background-color: #1e2535; "
    f"border: 1px solid {_OVERLAY}; border-radius: 6px; padding: 10px; }}"
)
_CANARY_STYLE = (
    f"QLabel {{ color: {_PURPLE}; background-color: #251e35; "
    f"border: 1px solid {_OVERLAY}; border-radius: 6px; padding: 8px; }}"
)
_PSU_STYLE = (
    f"QLabel {{ color: {_YELLOW}; background-color: #2e2a1e; "
    f"border: 1px solid {_OVERLAY}; border-radius: 6px; padding: 10px; }}"
)


class SweepConfigDialog(QDialog):
    """Diálogo de configuração para sweep automático de tensão ou temperatura."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sweep Automático")
        self.setModal(True)
        self.setMinimumWidth(420)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # --- Modo ---
        mode_group = QGroupBox("Modo de Sweep")
        mode_layout = QVBoxLayout()
        self.radio_voltage = QRadioButton("Tensão Variável  (temperatura fixa)")
        self.radio_temp = QRadioButton(
            "Temperatura Variável  (tensão fixa)  →  40 °C … 130 °C"
        )
        self.radio_voltage.setChecked(True)
        mode_layout.addWidget(self.radio_voltage)
        mode_layout.addWidget(self.radio_temp)
        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)

        # --- Parâmetros sweep de tensão ---
        self.volt_group = QGroupBox("Parâmetros — Sweep de Tensão")
        vf = QFormLayout()
        vf.setSpacing(6)
        self.volt_start = QDoubleSpinBox()
        self.volt_start.setRange(0.0, 1.4)
        self.volt_start.setDecimals(3)
        self.volt_start.setSingleStep(0.05)
        self.volt_start.setValue(0.8)
        self.volt_start.setSuffix(" V")
        self.volt_step = QDoubleSpinBox()
        self.volt_step.setRange(0.01, 0.5)
        self.volt_step.setDecimals(3)
        self.volt_step.setSingleStep(0.01)
        self.volt_step.setValue(0.05)
        self.volt_step.setSuffix(" V")
        self.volt_end = QDoubleSpinBox()
        self.volt_end.setRange(0.1, 1.5)
        self.volt_end.setDecimals(3)
        self.volt_end.setSingleStep(0.05)
        self.volt_end.setValue(1.3)
        self.volt_end.setSuffix(" V")
        self.volt_oven_sp = QDoubleSpinBox()
        self.volt_oven_sp.setRange(25.0, 130.0)
        self.volt_oven_sp.setValue(100.0)
        self.volt_oven_sp.setSuffix(" °C")
        self.volt_stable_s = QDoubleSpinBox()
        self.volt_stable_s.setRange(10.0, 600.0)
        self.volt_stable_s.setValue(60.0)
        self.volt_stable_s.setSuffix(" s")
        self.volt_min_dwell = QDoubleSpinBox()
        self.volt_min_dwell.setRange(10.0, 600.0)
        self.volt_min_dwell.setValue(60.0)
        self.volt_min_dwell.setSuffix(" s")
        self.volt_tolerance = QDoubleSpinBox()
        self.volt_tolerance.setRange(0.001, 0.2)
        self.volt_tolerance.setDecimals(3)
        self.volt_tolerance.setSingleStep(0.005)
        self.volt_tolerance.setValue(0.02)
        self.volt_tolerance.setSuffix(" V")
        vf.addRow("Tensão inicial:", self.volt_start)
        vf.addRow("Passo:", self.volt_step)
        vf.addRow("Tensão final:", self.volt_end)
        vf.addRow("Setpoint forno:", self.volt_oven_sp)
        vf.addRow("Tempo estável mínimo:", self.volt_stable_s)
        vf.addRow("Dwell mínimo por passo:", self.volt_min_dwell)
        vf.addRow("Tolerância VCCINT:", self.volt_tolerance)
        self.volt_group.setLayout(vf)
        layout.addWidget(self.volt_group)

        # --- Parâmetros sweep de temperatura ---
        self.temp_group = QGroupBox("Parâmetros — Sweep de Temperatura")
        tf = QFormLayout()
        tf.setSpacing(6)
        self.temp_start = QDoubleSpinBox()
        self.temp_start.setRange(25.0, 129.0)
        self.temp_start.setValue(40.0)
        self.temp_start.setSuffix(" °C")
        self.temp_step = QDoubleSpinBox()
        self.temp_step.setRange(1.0, 50.0)
        self.temp_step.setValue(20.0)
        self.temp_step.setSuffix(" °C")
        self.temp_end = QDoubleSpinBox()
        self.temp_end.setRange(26.0, 130.0)
        self.temp_end.setValue(130.0)
        self.temp_end.setSuffix(" °C")
        self.temp_volt_sp = QDoubleSpinBox()
        self.temp_volt_sp.setRange(0.0, 1.5)
        self.temp_volt_sp.setValue(1.0)
        self.temp_volt_sp.setDecimals(3)
        self.temp_volt_sp.setSuffix(" V")
        self.temp_stable_s = QDoubleSpinBox()
        self.temp_stable_s.setRange(30.0, 1200.0)
        self.temp_stable_s.setValue(120.0)
        self.temp_stable_s.setSuffix(" s")
        self.temp_min_dwell = QDoubleSpinBox()
        self.temp_min_dwell.setRange(30.0, 1200.0)
        self.temp_min_dwell.setValue(120.0)
        self.temp_min_dwell.setSuffix(" s")
        self.temp_tolerance = QDoubleSpinBox()
        self.temp_tolerance.setRange(0.5, 10.0)
        self.temp_tolerance.setValue(2.0)
        self.temp_tolerance.setSuffix(" °C")
        tf.addRow("Temp. inicial:", self.temp_start)
        tf.addRow("Passo:", self.temp_step)
        tf.addRow("Temp. final:", self.temp_end)
        tf.addRow("VCCINT fixo:", self.temp_volt_sp)
        tf.addRow("Tempo estável mínimo:", self.temp_stable_s)
        tf.addRow("Dwell mínimo por passo:", self.temp_min_dwell)
        tf.addRow("Tolerância forno:", self.temp_tolerance)
        self.temp_group.setLayout(tf)
        layout.addWidget(self.temp_group)
        self.temp_group.hide()

        # --- Nome do teste ---
        nf = QFormLayout()
        self.test_name_edit = QLineEdit("Sweep_001")
        nf.addRow("Nome do teste:", self.test_name_edit)
        layout.addLayout(nf)

        # --- Botões ---
        self.ok_btn = QPushButton("INICIAR SWEEP")
        self.ok_btn.setStyleSheet(
            f"background-color: #1a2e4a; color: {_BLUE}; font-weight: bold; "
            "padding: 8px; border: 1px solid #3a6a9a; border-radius: 4px;"
        )
        cancel_btn = QPushButton("Cancelar")
        btn_row = QHBoxLayout()
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(self.ok_btn)
        layout.addLayout(btn_row)

        self.radio_voltage.toggled.connect(self._on_mode_changed)
        self.ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)

    def _on_mode_changed(self, voltage_selected: bool):
        self.volt_group.setVisible(voltage_selected)
        self.temp_group.setVisible(not voltage_selected)

    def get_settings(self) -> dict:
        """Retorna dict de configuração para TestSequencer.start_test()."""
        if self.radio_voltage.isChecked():
            start = self.volt_start.value()
            step  = self.volt_step.value()
            end   = self.volt_end.value()
            steps, v = [], start
            while v <= end + 1e-9:
                steps.append(round(v, 3))
                v += step
            if steps and steps[-1] < end - 1e-9:
                steps.append(round(end, 3))
            return {
                'test_name':       self.test_name_edit.text() or "Sweep_001",
                'oven_setpoint':   self.volt_oven_sp.value(),
                'psu_voltage':     steps[0] if steps else start,
                'dut_target_temp': 0.0,
                'sweep_mode':      'voltage',
                'sweep_steps':     steps,
                'sweep_stable_s':  int(self.volt_stable_s.value()),
                'sweep_min_dwell': int(self.volt_min_dwell.value()),
                'sweep_tolerance': self.volt_tolerance.value(),
            }
        else:
            start = self.temp_start.value()
            step  = self.temp_step.value()
            end   = self.temp_end.value()
            steps, t = [], start
            while t <= end + 0.001:
                steps.append(round(t, 1))
                t += step
            if steps and steps[-1] < end - 0.001:
                steps.append(round(end, 1))
            return {
                'test_name':       self.test_name_edit.text() or "Sweep_001",
                'oven_setpoint':   steps[0] if steps else start,
                'psu_voltage':     self.temp_volt_sp.value(),
                'dut_target_temp': 0.0,
                'sweep_mode':      'temperature',
                'sweep_steps':     steps,
                'sweep_stable_s':  int(self.temp_stable_s.value()),
                'sweep_min_dwell': int(self.temp_min_dwell.value()),
                'sweep_tolerance': self.temp_tolerance.value(),
            }


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
        self.setStyleSheet(_DARK_STYLE)

        self.threads = {}
        self.workers = {}

        self._create_top_bar_widgets()
        self._create_tab_widgets()
        self._create_layout()
        self._setup_status_bar()
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
            f"background-color: #1e4d2b; color: {_GREEN}; font-weight: bold; "
            "padding: 10px; font-size: 14px; border: 1px solid #40a060; border-radius: 4px;"
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
            f"<b>PID (Fixo):</b> Kp={config.PID_KP:.4f} &nbsp;"
            f"Ki={config.PID_KI:.6f} &nbsp;Kd={config.PID_KD:.4f}"
        )
        self.pid_info_label.setStyleSheet(
            f"color: {_SUBTEXT}; background-color: {_SURFACE}; "
            "padding: 5px 8px; border-radius: 4px; font-size: 11px;"
        )

        self.psu_control_group = QGroupBox("Fonte PSU (IT6502D)")
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

        # Sweep automático
        self.sweep_button = QPushButton("SWEEP AUTO")
        self.sweep_button.setStyleSheet(
            f"background-color: #1a2e4a; color: {_BLUE}; font-weight: bold; "
            "padding: 8px; font-size: 12px; border: 1px solid #3a6a9a; border-radius: 4px;"
        )
        self._sweep_progress_label = QLabel("")
        self._sweep_progress_label.setStyleSheet(
            f"color: {_BLUE}; background-color: #121e30; "
            f"border: 1px solid #3a6a9a; border-radius: 4px; padding: 4px 6px; font-size: 11px;"
        )
        self._sweep_progress_label.hide()

    def _create_tab_widgets(self):
        # --- Sensor tab ---
        self.slack_label = QLabel("Slack: -- Inc.")
        f = QFont()
        f.setPointSize(22)
        f.setBold(True)
        self.slack_label.setFont(f)
        self.slack_label.setStyleSheet(_STYLE_OK)
        self.slack_label.setMinimumHeight(60)
        self.slack_label.setAlignment(Qt.AlignCenter)

        self.failure_label = QLabel("FALHA: ---")
        f2 = QFont()
        f2.setPointSize(18)
        f2.setBold(True)
        self.failure_label.setFont(f2)
        self.failure_label.setStyleSheet(_STYLE_OK)
        self.failure_label.setMinimumHeight(50)
        self.failure_label.setAlignment(Qt.AlignCenter)

        # DUT + oven info row
        self.dut_temp_label  = QLabel("Temp DUT:  -- °C")
        self.dut_volt_label  = QLabel("VCCINT:  -- V")
        self.oven_temp_label = QLabel("Forno:  -- °C")
        _font_med = QFont()
        _font_med.setPointSize(13)
        for lbl in (self.dut_temp_label, self.dut_volt_label, self.oven_temp_label):
            lbl.setFont(_font_med)
            lbl.setStyleSheet(_INFO_STYLE)
            lbl.setAlignment(Qt.AlignCenter)

        # PSU live readout row
        self.psu_cmd_label  = QLabel("PSU Cmd:  -- V")
        self.psu_meas_label = QLabel("PSU Med:  -- V")
        self.psu_curr_label = QLabel("Corrente:  -- A")
        _font_sm = QFont()
        _font_sm.setPointSize(12)
        for lbl in (self.psu_cmd_label, self.psu_meas_label, self.psu_curr_label):
            lbl.setFont(_font_sm)
            lbl.setStyleSheet(_PSU_STYLE)
            lbl.setAlignment(Qt.AlignCenter)

        # Per-channel slack summary (replaces the removed adder-canary
        # metrics -- this branch's rca_sensor_channel has no single
        # wrong/correct/error_count concept across N independent channels)
        self.channel_labels = []
        for i in range(MULTI_NUM_CHANNELS):
            lbl = QLabel(f"Canal {i}: --")
            lbl.setStyleSheet(_CANARY_STYLE)
            lbl.setAlignment(Qt.AlignCenter)
            self.channel_labels.append(lbl)

        # --- Other tabs ---
        self.plot_widget = PlotWidget(plot_window_size=300)
        self.aux_plot_widget = AuxPlotWidget(plot_window_size=300)
        self.panel_multi = MultiChannelPanel(MULTI_NUM_CHANNELS, plot_window_size=300)
        self.log_text_edit = QTextEdit()
        self.log_text_edit.setReadOnly(True)

    # =========================================================================
    #   Layout
    # =========================================================================

    def _create_layout(self):
        root = QVBoxLayout()
        root.setSpacing(6)
        root.setContentsMargins(8, 8, 8, 4)

        # ---- Top bar ----
        top_bar = QHBoxLayout()
        top_bar.setSpacing(8)

        oven_form = QFormLayout()
        oven_form.setSpacing(6)
        oven_form.addRow("Setpoint Forno:", self.oven_setpoint_input)
        oven_form.addRow("Alvo DUT (0=off):", self.dut_target_input)
        oven_inner = QVBoxLayout()
        oven_inner.addLayout(oven_form)
        oven_inner.addWidget(self.pid_info_label)
        self.oven_control_group.setLayout(oven_inner)
        top_bar.addWidget(self.oven_control_group, stretch=2)

        psu_form = QFormLayout()
        psu_form.setSpacing(6)
        psu_form.addRow("VCCINT Alvo:", self.psu_setpoint_input)
        psu_inner = QVBoxLayout()
        psu_inner.addLayout(psu_form)
        psu_inner.addWidget(self.beeper_button)
        psu_inner.addStretch()
        self.psu_control_group.setLayout(psu_inner)
        top_bar.addWidget(self.psu_control_group, stretch=1)

        test_form = QFormLayout()
        test_form.setSpacing(6)
        test_form.addRow("Nome:", self.test_name_input)
        test_form.addRow(self.toggle_test_button)
        test_form.addRow(self.sweep_button)
        test_form.addRow(self._sweep_progress_label)
        test_form.addRow(QLabel(f"<small style='color:{_MUTED}'>Logs: {config.LOG_FOLDER}</small>"))
        self.test_control_group.setLayout(test_form)
        top_bar.addWidget(self.test_control_group, stretch=1)

        root.addLayout(top_bar)

        # ---- Tab widget ----
        tabs = QTabWidget()

        # Tab 1: Sensor
        sensor_widget = QWidget()
        sensor_layout = QVBoxLayout(sensor_widget)
        sensor_layout.setSpacing(8)
        sensor_layout.setContentsMargins(8, 8, 8, 8)

        # Row 1: slack + failure
        row1 = QHBoxLayout()
        row1.setSpacing(8)
        row1.addWidget(self.slack_label, stretch=2)
        row1.addWidget(self.failure_label, stretch=1)
        sensor_layout.addLayout(row1)

        # Row 2: DUT temp / VCCINT / oven temp
        row2 = QHBoxLayout()
        row2.setSpacing(8)
        row2.addWidget(self.dut_temp_label)
        row2.addWidget(self.dut_volt_label)
        row2.addWidget(self.oven_temp_label)
        sensor_layout.addLayout(row2)

        # Row 3: PSU cmd / measured / current
        row3 = QHBoxLayout()
        row3.setSpacing(8)
        row3.addWidget(self.psu_cmd_label)
        row3.addWidget(self.psu_meas_label)
        row3.addWidget(self.psu_curr_label)
        sensor_layout.addLayout(row3)

        # Row 4: per-channel slack summary
        channels_group = QGroupBox(f"Canais ({MULTI_NUM_CHANNELS})")
        channels_row = QHBoxLayout()
        channels_row.setSpacing(8)
        for lbl in self.channel_labels:
            channels_row.addWidget(lbl)
        channels_group.setLayout(channels_row)
        sensor_layout.addWidget(channels_group)
        sensor_layout.addStretch()

        tabs.addTab(sensor_widget,        "Sensor")
        tabs.addTab(self.plot_widget,     "Temperatura")
        tabs.addTab(self.aux_plot_widget, "Tensão")
        tabs.addTab(self.panel_multi,     f"Multi-Sensor ({MULTI_NUM_CHANNELS} canais)")

        # Log panel — always visible in bottom half, resizable
        log_group = QGroupBox("Log de Eventos")
        log_inner = QVBoxLayout()
        log_inner.setContentsMargins(4, 4, 4, 4)
        log_inner.addWidget(self.log_text_edit)
        log_group.setLayout(log_inner)

        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(tabs)
        splitter.addWidget(log_group)
        splitter.setStretchFactor(0, 7)
        splitter.setStretchFactor(1, 3)
        splitter.setChildrenCollapsible(False)

        root.addWidget(splitter, stretch=1)

        central = QWidget()
        central.setLayout(root)
        self.setCentralWidget(central)

    # =========================================================================
    #   Status bar
    # =========================================================================

    def _setup_status_bar(self):
        sb = QStatusBar()
        self.setStatusBar(sb)
        self._sb_arduino = QLabel()
        self._sb_psu     = QLabel()
        self._sb_dut     = QLabel()
        self._sb_test    = QLabel("Aguardando início do teste")
        sb.addWidget(self._sb_test, 1)
        sb.addPermanentWidget(self._sb_dut)
        sb.addPermanentWidget(self._sb_psu)
        sb.addPermanentWidget(self._sb_arduino)
        self._refresh_status_bar()

    def _refresh_status_bar(self, test_running: bool = False):
        def _pill(label, ok):
            dot   = "●" if ok else "○"
            color = _GREEN if ok else _MUTED
            return f'<span style="color:{color}; font-size:11px;">{dot} {label}</span>'

        self._sb_dut.setText(_pill("DUT", True))
        self._sb_psu.setText(_pill("PSU", config.PSU_ENABLED))
        self._sb_arduino.setText(_pill("Arduino", config.ARDUINO_ENABLED))
        if test_running:
            self._sb_test.setText(
                f'<span style="color:{_GREEN}; font-weight:bold;">▶ Teste em execução</span>'
            )
        else:
            self._sb_test.setText(
                f'<span style="color:{_MUTED};">■ Aguardando início do teste</span>'
            )

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
        sequencer_worker.plot_data_update.connect(self.panel_multi.update_plot_data)
        sequencer_worker.stats_update.connect(self.panel_multi.update_stats)
        sequencer_worker.test_finished.connect(self.on_test_finished)
        sequencer_worker.sweep_step_changed.connect(self._on_sweep_step_changed)  # type: ignore[arg-type]

    def _connect_signals(self):
        self.toggle_test_button.clicked.connect(self.on_toggle_test)
        self.psu_setpoint_input.editingFinished.connect(self.on_update_psu_voltage)
        self.oven_setpoint_input.editingFinished.connect(self.on_update_oven_setpoint)
        self.beeper_button.clicked.connect(self._on_beeper_toggled)
        self.sweep_button.clicked.connect(self.on_start_sweep)

    # =========================================================================
    #   Slots
    # =========================================================================

    @Slot(str)
    def log_message(self, message):
        ts = time.strftime('%H:%M:%S')
        self.log_text_edit.append(f"[{ts}] {message}")

    @Slot(dict)
    def _update_sensor_display(self, d: dict):
        slacks    = [d.get(f"dut_slack_ch{i}", 0) for i in range(MULTI_NUM_CHANNELS)]
        alarms    = [bool(d.get(f"dut_alarm_ch{i}", 0)) for i in range(MULTI_NUM_CHANNELS)]
        slack     = min(slacks) if slacks else 0   # worst-case channel
        any_alarm = any(alarms)
        temp      = d.get("dut_temp", 0.0)
        volt      = d.get("dut_volt", 0.0)
        oven_temp = d.get("oven_temp", 0.0)
        psu_cmd   = d.get("psu_cmd_v", 0.0)
        psu_meas  = d.get("psu_voltage", 0.0)
        psu_curr  = d.get("psu_current", 0.0)

        self.slack_label.setText(f"Slack (pior canal): {slack} Inc.")
        self.slack_label.setStyleSheet(_STYLE_WARN if 0 < slack < 20 else _STYLE_OK)

        if any_alarm:
            self.failure_label.setText("ALARME: SIM")
            self.failure_label.setStyleSheet(_STYLE_WARN)
        else:
            self.failure_label.setText("ALARME: NÃO")
            self.failure_label.setStyleSheet(_STYLE_OK)

        self.dut_temp_label.setText(f"Temp DUT:  {temp:.1f} °C")
        self.dut_volt_label.setText(f"VCCINT:  {volt:.3f} V")
        self.oven_temp_label.setText(f"Forno:  {oven_temp:.1f} °C")

        self.psu_cmd_label.setText(f"PSU Cmd:  {psu_cmd:.3f} V")
        self.psu_meas_label.setText(f"PSU Med:  {psu_meas:.3f} V")
        self.psu_curr_label.setText(f"Corrente:  {psu_curr:.3f} A")

        for i, lbl in enumerate(self.channel_labels):
            marker = " ⚠" if alarms[i] else ""
            lbl.setText(f"Canal {i}: {slacks[i]}{marker}")
            lbl.setStyleSheet(_STYLE_WARN if alarms[i] else _CANARY_STYLE)

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
            self.panel_multi.clear_plot()
            self.start_test_signal.emit(settings)
            self.toggle_test_button.setText("PARAR TESTE")
            self.toggle_test_button.setStyleSheet(
                f"background-color: #4d1e2b; color: {_RED}; font-weight: bold; "
                "padding: 10px; font-size: 14px; border: 1px solid #c04060; border-radius: 4px;"
            )
            self.test_name_input.setEnabled(False)
            self.sweep_button.setEnabled(False)
            self._refresh_status_bar(test_running=True)
        else:
            self.stop_test_signal.emit()
            self.on_test_finished()

    @Slot()
    def on_start_sweep(self):
        """Abre diálogo de configuração e inicia sweep automático."""
        dialog = SweepConfigDialog(self)
        if dialog.exec() != QDialog.Accepted:
            return
        settings = dialog.get_settings()
        self.plot_widget.clear_plot()
        self.aux_plot_widget.clear_plot()
        self.panel_multi.clear_plot()
        self.start_test_signal.emit(settings)
        self.toggle_test_button.setChecked(True)
        self.toggle_test_button.setText("PARAR SWEEP")
        self.toggle_test_button.setStyleSheet(
            f"background-color: #4d1e2b; color: {_RED}; font-weight: bold; "
            "padding: 10px; font-size: 14px; border: 1px solid #c04060; border-radius: 4px;"
        )
        self.test_name_input.setEnabled(False)
        self.sweep_button.setEnabled(False)
        self._sweep_progress_label.setText("Sweep: aguardando passo 1…")
        self._sweep_progress_label.show()
        self._refresh_status_bar(test_running=True)

    @Slot(int, float, int, str)
    def _on_sweep_step_changed(self, idx: int, target: float, total: int, mode: str):
        """Atualiza indicador de progresso do sweep."""
        unit = "V" if mode == 'voltage' else "°C"
        text = f"Sweep [{idx + 1}/{total}]: {target}{unit}"
        self._sweep_progress_label.setText(text)
        self._sb_test.setText(
            f'<span style="color:{_BLUE}; font-weight:bold;">◈ {text}</span>'
        )

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
            f"background-color: #1e4d2b; color: {_GREEN}; font-weight: bold; "
            "padding: 10px; font-size: 14px; border: 1px solid #40a060; border-radius: 4px;"
        )
        self.toggle_test_button.setChecked(False)
        self.test_name_input.setEnabled(True)
        self.sweep_button.setEnabled(True)
        self._sweep_progress_label.hide()
        self._sweep_progress_label.setText("")
        self._refresh_status_bar(test_running=False)

    @Slot(bool)
    def _on_beeper_toggled(self, checked: bool):
        self.psu_beeper_signal.emit(not checked)
        if checked:
            self.beeper_button.setText("Buzzer: SILENCIADO")
            self.beeper_button.setStyleSheet(
                f"background-color: #3a2e10; color: {_YELLOW}; "
                "border: 1px solid #856404;"
            )
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
