import sys
import time
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QGroupBox, QFormLayout, QLineEdit, QTextEdit,
    QLabel, QDoubleSpinBox, QComboBox, QGridLayout, QTabWidget, QSplitter,
    QCheckBox, QSpinBox, QFrame
)
from PySide6.QtCore import QThread, Signal, Slot, Qt, QTimer
import config

from router import UARTRouter
from workers import STMWorker, CROCWorker, ArduinoWorker, TestSequencer
from plot_widget import PlotWidget
from aux_plot_widget import AuxPlotWidget
from multi_channel_widget import MultiChannelPanel
from protocol import MULTI_NUM_CHANNELS

class MainWindow(QMainWindow):
    start_test_signal = Signal(dict)
    stop_test_signal = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("FPGAging — Sistema de Envelhecimento Acelerado")
        self.resize(1280, 860)

        self.router = UARTRouter()

        self.sweep_timer = QTimer()
        self.sweep_timer.timeout.connect(self._send_sweep_trigger)

        self._init_ui()
        self._apply_arduino_state()
        self._setup_status_bar()

        # Router signals
        self.router.connection_status.connect(self._on_connection_status)
        self.router.log_message.connect(self.log_message)
        self.router.log_text_received.connect(self.log_message)

        self.router.connect_serial()
        self._start_workers()
        self._start_sequencer()

    def _init_ui(self):
        self.tabs = QTabWidget()

        self.tab_monitor = QWidget()
        self._setup_monitor_tab()
        self.tabs.addTab(self.tab_monitor, "Monitoramento & Gráficos")

        self.panel_multi = MultiChannelPanel(MULTI_NUM_CHANNELS, plot_window_size=200)
        self.tabs.addTab(self.panel_multi, f"Multi-Sensor ({MULTI_NUM_CHANNELS} canais)")

        self.tab_config = QWidget()
        self._setup_config_tab()
        self.tabs.addTab(self.tab_config, "Engenharia & Configuração")

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tabs)

        # Log Global (Fixo na parte inferior)
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setMaximumHeight(110)
        self.log_box.setPlaceholderText("Logs do sistema...")
        self.log_box.setStyleSheet(
            "font-family: 'Monospace', 'Courier New'; font-size: 9pt;"
        )
        main_layout.addWidget(self.log_box)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def _setup_monitor_tab(self):
        layout = QVBoxLayout(self.tab_monitor)

        top_bar = QHBoxLayout()

        self.txt_test_name = QLineEdit("Teste_01")
        self.txt_test_name.setPlaceholderText("Nome do Teste")
        self.btn_test = QPushButton("INICIAR EXPERIMENTO")
        self.btn_test.setCheckable(True)
        self.btn_test.setMinimumHeight(40)
        self.btn_test.setStyleSheet("background-color: #2E7D32; color: white; font-weight: bold; font-size: 11pt;")
        self.btn_test.clicked.connect(self._toggle_test)

        self.sp_input = QDoubleSpinBox()
        self.sp_input.setRange(20, 150)
        self.sp_input.setValue(100)
        self.sp_input.setSuffix(" °C")
        self.sp_input.setPrefix("Forno: ")
        self.sp_input.setFixedWidth(120)

        self.vcore_monitor = QDoubleSpinBox()
        self.vcore_monitor.setRange(0, 1.2)
        self.vcore_monitor.setValue(0.85)
        self.vcore_monitor.setSuffix(" V")
        self.vcore_monitor.setPrefix("Vcore: ")
        self.vcore_monitor.setFixedWidth(120)

        self.lbl_slack = QLabel("Slack: ---")
        self.lbl_slack.setAlignment(Qt.AlignCenter)
        self.lbl_slack.setMinimumWidth(160)
        self.lbl_slack.setStyleSheet(
            "background-color: #313244; color: #cdd6f4; font-weight: bold;"
            " padding: 6px 12px; border-radius: 6px; font-size: 11pt;"
        )

        top_bar.addWidget(QLabel("Experimento:"))
        top_bar.addWidget(self.txt_test_name)
        top_bar.addWidget(self.sp_input)
        top_bar.addWidget(self.vcore_monitor)
        top_bar.addWidget(self.btn_test)
        top_bar.addSpacing(20)
        top_bar.addWidget(self.lbl_slack)

        layout.addLayout(top_bar)

        splitter = QSplitter(Qt.Vertical)

        self.plot1 = PlotWidget(plot_window_size=200)
        self.plot2 = AuxPlotWidget(plot_window_size=200)

        splitter.addWidget(self.plot1)
        splitter.addWidget(self.plot2)
        layout.addWidget(splitter)

    def _setup_config_tab(self):
        layout = QHBoxLayout(self.tab_config)

        # Coluna 1: Controle PID (Arduino)
        self.grp_pid = QGroupBox("Parâmetros PID (Forno)")
        grp_pid = self.grp_pid
        form_pid = QFormLayout()
        self.kp_input = QDoubleSpinBox(); self.kp_input.setValue(config.DEFAULT_KP)
        self.ki_input = QDoubleSpinBox(); self.ki_input.setValue(config.DEFAULT_KI); self.ki_input.setDecimals(5)
        self.kd_input = QDoubleSpinBox(); self.kd_input.setValue(config.DEFAULT_KD)
        self.btn_update_pid = QPushButton("Enviar PID para Arduino")
        self.btn_update_pid.clicked.connect(self._update_pid)

        form_pid.addRow("Proporcional (Kp):", self.kp_input)
        form_pid.addRow("Integral (Ki):", self.ki_input)
        form_pid.addRow("Derivativo (Kd):", self.kd_input)
        form_pid.addRow(self.btn_update_pid)
        grp_pid.setLayout(form_pid)

        # Coluna 2: Controle STM32 (Display/Vcore Manual)
        grp_stm = QGroupBox("Controle STM32 (Fonte/Display)")
        v_stm = QVBoxLayout()

        h_vcore = QHBoxLayout()
        self.vcore_manual_spin = QDoubleSpinBox(); self.vcore_manual_spin.setRange(0, 1.8); self.vcore_manual_spin.setValue(0.85)
        btn_set_vcore = QPushButton("Aplicar Tensão"); btn_set_vcore.clicked.connect(lambda: self.w_stm.set_voltage(self.vcore_manual_spin.value()))
        h_vcore.addWidget(QLabel("Vcore:")); h_vcore.addWidget(self.vcore_manual_spin); h_vcore.addWidget(btn_set_vcore)

        h_page = QHBoxLayout()
        self.page_combo = QComboBox(); self.page_combo.addItems([f"Página {i}" for i in range(1, 7)])
        btn_page = QPushButton("Mudar Página OLED"); btn_page.clicked.connect(lambda: self.w_stm.set_page(self.page_combo.currentIndex()+1))
        h_page.addWidget(self.page_combo); h_page.addWidget(btn_page)

        btn_ping = QPushButton("Ping STM32 (Debug)")
        btn_ping.setToolTip("Envia PING pelo caminho PC→ESP32→FPGA→STM32→FPGA→ESP32→PC\n"
                            "Uma resposta [STM RX] OK: func=M no log confirma o caminho completo.")
        btn_ping.clicked.connect(lambda: self.w_stm.send_ping())

        btn_reset = QPushButton("HARD RESET SYSTEM"); btn_reset.setStyleSheet("background-color: #800; color: white;")
        btn_reset.clicked.connect(lambda: self.w_stm.send_manual_message("reset"))

        v_stm.addLayout(h_vcore)
        v_stm.addLayout(h_page)
        v_stm.addStretch()
        v_stm.addWidget(btn_ping)
        v_stm.addWidget(btn_reset)
        grp_stm.setLayout(v_stm)

        # Coluna 3: Console Manual & Varredura
        grp_manual = QGroupBox("Terminal & Varredura FPGA")
        v_man = QVBoxLayout()

        self.txt_manual = QLineEdit()
        self.txt_manual.setPlaceholderText("Comando raw...")
        self.cmb_target = QComboBox(); self.cmb_target.addItems(["STM32 (Protocolo)", "CROC (Raw)"])
        self.btn_send_manual = QPushButton("Enviar Comando Texto")
        self.btn_send_manual.clicked.connect(self._manual_send)

        v_man.addWidget(QLabel("Destino:"))
        v_man.addWidget(self.cmb_target)
        v_man.addWidget(QLabel("Payload:"))
        v_man.addWidget(self.txt_manual)
        v_man.addWidget(self.btn_send_manual)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        v_man.addSpacing(10)
        v_man.addWidget(line)
        v_man.addSpacing(10)

        lbl_sweep = QLabel("<b>FPGA Sensor Sweep (0x0F)</b>")
        lbl_sweep.setAlignment(Qt.AlignCenter)
        v_man.addWidget(lbl_sweep)

        h_sweep = QHBoxLayout()

        self.chk_auto_sweep = QCheckBox("Ciclo Automático")
        self.chk_auto_sweep.setToolTip("Envia 0x0F repetidamente")
        self.chk_auto_sweep.toggled.connect(self._toggle_sweep_timer)

        self.spin_sweep_interval = QSpinBox()
        self.spin_sweep_interval.setRange(50, 5000)
        self.spin_sweep_interval.setValue(100)
        self.spin_sweep_interval.setSuffix(" ms")
        self.spin_sweep_interval.setToolTip("Período entre triggers")

        h_sweep.addWidget(self.chk_auto_sweep)
        h_sweep.addWidget(self.spin_sweep_interval)
        v_man.addLayout(h_sweep)

        self.btn_single_sweep = QPushButton("DISPARAR AGORA (Single)")
        self.btn_single_sweep.clicked.connect(self._send_sweep_trigger)
        self.btn_single_sweep.setStyleSheet("background-color: #0097A7; color: white; font-weight: bold;")
        self.btn_single_sweep.setToolTip("Envia um único byte 0x0F")
        v_man.addWidget(self.btn_single_sweep)

        v_man.addStretch()
        grp_manual.setLayout(v_man)

        layout.addWidget(grp_pid)
        layout.addWidget(grp_stm)
        layout.addWidget(grp_manual)

    # --- Inicialização ---

    def _apply_arduino_state(self):
        enabled = config.ARDUINO_ENABLED
        self.sp_input.setEnabled(enabled)
        self.grp_pid.setEnabled(enabled)
        if not enabled:
            self.sp_input.setToolTip("Arduino não habilitado — configure no Setup")
            self.grp_pid.setToolTip("Arduino não habilitado — configure no Setup")

    def _setup_status_bar(self):
        self.lbl_status_esp = QLabel("● ESP32: aguardando...")
        self.lbl_status_esp.setStyleSheet("color: #6c7086; padding: 0 8px;")
        if config.ARDUINO_ENABLED:
            self.lbl_status_ard = QLabel("● Arduino: aguardando...")
            self.lbl_status_ard.setStyleSheet("color: #6c7086; padding: 0 8px;")
            self.statusBar().addPermanentWidget(self.lbl_status_ard)
        self.statusBar().addPermanentWidget(self.lbl_status_esp)
        self.statusBar().showMessage("Iniciando sistema...")

    @Slot(str)
    def _on_connection_status(self, msg):
        self.log_message(msg)
        connected = "Conectado" in msg or "Aberta" in msg
        color = "#a6e3a1" if connected else "#f38ba8"
        self.lbl_status_esp.setText(f"● ESP32: {msg}")
        self.lbl_status_esp.setStyleSheet(f"color: {color}; padding: 0 8px;")
        self.statusBar().showMessage(msg, 5000)

    # --- Lógica de Negócio ---

    def _start_workers(self):
        # --- Arduino Worker ---
        self.w_ard = ArduinoWorker()
        self.t_ard = QThread()
        self.t_ard.setTerminationEnabled(True)
        self.w_ard.moveToThread(self.t_ard)
        self.w_ard.log_message.connect(self.log_message)
        self.t_ard.start()
        self.w_ard.start()

        # --- STM Worker ---
        self.w_stm = STMWorker(self.router)
        self.t_stm = QThread()
        self.t_stm.setTerminationEnabled(True)
        self.w_stm.moveToThread(self.t_stm)
        self.w_stm.log_message.connect(self.log_message)
        self.t_stm.start()
        self.w_stm.start()

        # --- CROC Worker ---
        self.w_croc = CROCWorker(self.router)
        self.t_croc = QThread()
        self.t_croc.setTerminationEnabled(True)
        self.w_croc.moveToThread(self.t_croc)
        self.w_croc.log_message.connect(self.log_message)
        self.t_croc.start()
        self.w_croc.start()

    def closeEvent(self, event):
        self.log_message("Encerrando sistema e parando threads...")

        if self.sweep_timer.isActive():
            self.sweep_timer.stop()

        if hasattr(self, 'seq'):
            self.stop_test_signal.emit()
            if hasattr(self, 't_seq') and self.t_seq.isRunning():
                self.t_seq.quit()
                self.t_seq.wait(100)

        if hasattr(self, 'router'):
            self.router.disconnect_serial()

        workers_threads = [
            (self.w_ard, self.t_ard),
            (self.w_stm, self.t_stm),
            (self.w_croc, self.t_croc)
        ]

        for worker, thread in workers_threads:
            if hasattr(worker, 'stop'): worker.stop()
            if thread.isRunning():
                thread.quit()
                if not thread.wait(100): thread.terminate()

        event.accept()
        super().closeEvent(event)

    def _start_sequencer(self):
        self.seq = TestSequencer(self.w_ard, self.w_stm, self.w_croc)
        self.t_seq = QThread()
        self.seq.moveToThread(self.t_seq)

        self.start_test_signal.connect(self.seq.start_test)
        self.stop_test_signal.connect(self.seq.stop_test)

        self.seq.plot_data_update.connect(self.plot1.update_plot_data)
        self.seq.plot_data_update.connect(self.plot2.update_plot_data)
        self.seq.plot_data_update.connect(self.update_slack_display)
        self.seq.plot_data_update.connect(self.panel_multi.update_plot_data)
        self.seq.stats_update.connect(self.panel_multi.update_stats)

        self.seq.test_finished.connect(self.on_finished)
        self.seq.log_message.connect(self.log_message)
        self.t_seq.start()

    @Slot(dict)
    def update_slack_display(self, d):
        # Worst-case (minimum) slack across all channels -- the single
        # number most worth flagging in the top bar.
        slacks = [d.get(f'dut_slack_ch{i}', 0) for i in range(MULTI_NUM_CHANNELS)]
        s = min(slacks) if slacks else 0
        self.lbl_slack.setText(f"Slack (pior canal): {s}")
        if s < 0:
            bg, fg = "#f38ba8", "#1e1e2e"   # violação
        elif s < 20:
            bg, fg = "#fab387", "#1e1e2e"   # alerta
        else:
            bg, fg = "#a6e3a1", "#1e1e2e"   # ok
        self.lbl_slack.setStyleSheet(
            f"background-color: {bg}; color: {fg}; font-weight: bold;"
            f" padding: 6px 12px; border-radius: 6px; font-size: 11pt;"
        )

    @Slot(bool)
    def _toggle_test(self, checked):
        if checked:
            cfg = {
                'test_name': self.txt_test_name.text(),
                'oven_setpoint': self.sp_input.value(),
                'psu_voltage': self.vcore_monitor.value(),
                'kp': self.kp_input.value(),
                'ki': self.ki_input.value(),
                'kd': self.kd_input.value()
            }
            self.plot1.clear_plot(); self.plot2.clear_plot(); self.panel_multi.clear_plot()
            self.start_test_signal.emit(cfg)
            self.btn_test.setText("PARAR EXPERIMENTO")
            self.btn_test.setStyleSheet("background-color: #C62828; color: white; font-weight: bold; font-size: 11pt;")
            self.vcore_monitor.setEnabled(False)
        else:
            self.stop_test_signal.emit()

    @Slot()
    def on_finished(self):
        self.btn_test.setChecked(False)
        self.btn_test.setText("INICIAR EXPERIMENTO")
        self.btn_test.setStyleSheet("background-color: #2E7D32; color: white; font-weight: bold; font-size: 11pt;")
        self.vcore_monitor.setEnabled(True)

    @Slot()
    def _manual_send(self):
        cmd = self.txt_manual.text()
        if "STM32" in self.cmb_target.currentText():
            self.w_stm.send_manual_message(cmd)
        else:
            self.w_croc.send_manual_command(cmd)

    @Slot()
    def _send_sweep_trigger(self):
        self.router._write_raw(b'\x0F\x0F')

    @Slot(bool)
    def _toggle_sweep_timer(self, checked):
        if checked:
            ms = self.spin_sweep_interval.value()
            self.sweep_timer.setInterval(ms)
            self.sweep_timer.start()
            self.btn_single_sweep.setEnabled(False)
            self.log_message(f"Varredura Automática Iniciada ({ms}ms)")
        else:
            self.sweep_timer.stop()
            self.btn_single_sweep.setEnabled(True)
            self.log_message("Varredura Automática Parada")

    @Slot()
    def _update_pid(self):
        self.w_ard.update_kp(self.kp_input.value())
        self.w_ard.update_ki(self.ki_input.value())
        self.w_ard.update_kd(self.kd_input.value())
        self.log_message("PID Atualizado Manualmente.")

    @Slot(str)
    def log_message(self, msg):
        self.log_box.append(f"[{time.strftime('%H:%M:%S')}] {msg}")
