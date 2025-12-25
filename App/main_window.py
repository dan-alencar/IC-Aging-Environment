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

class MainWindow(QMainWindow):
    start_test_signal = Signal(dict)
    stop_test_signal = Signal()
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema Integrado de Envelhecimento (Burn-in)")
        self.resize(1200, 850)
        
        self.router = UARTRouter()
        
        # Timer dedicado para o Trigger Cíclico do FPGA (0x0F)
        self.sweep_timer = QTimer()
        self.sweep_timer.timeout.connect(self._send_sweep_trigger)
        
        self._init_ui()
        
        # Conexões do Router
        self.router.connection_status.connect(self.log_message)
        self.router.log_message.connect(self.log_message)
        self.router.log_text_received.connect(self.log_message)
        
        # Inicia Hardware
        self.router.connect_serial()
        self._start_workers()
        self._start_sequencer()

    def _init_ui(self):
        self.tabs = QTabWidget()
        
        # --- ABA 1: MONITORAMENTO (A "Outra IHM") ---
        self.tab_monitor = QWidget()
        self._setup_monitor_tab()
        self.tabs.addTab(self.tab_monitor, "Monitoramento & Gráficos")
        
        # --- ABA 2: ENGENHARIA (Controles Manuais) ---
        self.tab_config = QWidget()
        self._setup_config_tab()
        self.tabs.addTab(self.tab_config, "Engenharia & Configuração")
        
        # Layout Principal
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tabs)
        
        # Log Global (Fixo na parte inferior)
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setMaximumHeight(120)
        self.log_box.setPlaceholderText("Logs do sistema...")
        main_layout.addWidget(self.log_box)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def _setup_monitor_tab(self):
        """Recria a interface focada em Gráficos da IHM de Burn-in"""
        layout = QVBoxLayout(self.tab_monitor)
        
        # Barra de Controle Superior
        top_bar = QHBoxLayout()
        
        # Controle do Teste
        self.txt_test_name = QLineEdit("Teste_01")
        self.txt_test_name.setPlaceholderText("Nome do Teste")
        self.btn_test = QPushButton("INICIAR EXPERIMENTO")
        self.btn_test.setCheckable(True)
        self.btn_test.setMinimumHeight(40)
        self.btn_test.setStyleSheet("background-color: #2E7D32; color: white; font-weight: bold; font-size: 11pt;")
        self.btn_test.clicked.connect(self._toggle_test)
        
        # Setpoints Rápidos
        self.sp_input = QDoubleSpinBox()
        self.sp_input.setRange(20, 150); self.sp_input.setValue(100); self.sp_input.setSuffix(" °C")
        self.sp_input.setPrefix("Forno: ")
        
        self.vcore_monitor = QDoubleSpinBox()
        self.vcore_monitor.setRange(0, 1.2); self.vcore_monitor.setValue(1.0); self.vcore_monitor.setSuffix(" V")
        self.vcore_monitor.setPrefix("Vcore: ")
        
        # Status Slack (Destaque)
        self.lbl_slack = QLabel("Slack: ---")
        self.lbl_slack.setAlignment(Qt.AlignCenter)
        self.lbl_slack.setStyleSheet("background-color: #333; color: white; font-weight: bold; padding: 5px; border-radius: 4px;")
        
        top_bar.addWidget(QLabel("Experimento:"))
        top_bar.addWidget(self.txt_test_name)
        top_bar.addWidget(self.sp_input)
        top_bar.addWidget(self.vcore_monitor)
        top_bar.addWidget(self.btn_test)
        top_bar.addSpacing(20)
        top_bar.addWidget(self.lbl_slack)
        
        layout.addLayout(top_bar)
        
        # Área dos Gráficos (Splitter Vertical)
        splitter = QSplitter(Qt.Vertical)
        
        self.plot1 = PlotWidget(plot_window_size=200) # Gráfico Térmico
        self.plot2 = AuxPlotWidget(plot_window_size=200) # Gráfico Elétrico
        
        splitter.addWidget(self.plot1)
        splitter.addWidget(self.plot2)
        layout.addWidget(splitter)

    def _setup_config_tab(self):
        """Controles técnicos do Arduino, STM32 e Console Manual"""
        layout = QHBoxLayout(self.tab_config)
        
        # Coluna 1: Controle PID (Arduino)
        grp_pid = QGroupBox("Parâmetros PID (Forno)")
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
        self.vcore_manual_spin = QDoubleSpinBox(); self.vcore_manual_spin.setRange(0, 1.8); self.vcore_manual_spin.setValue(1.0)
        btn_set_vcore = QPushButton("Aplicar Tensão"); btn_set_vcore.clicked.connect(lambda: self.w_stm.set_voltage(self.vcore_manual_spin.value()))
        h_vcore.addWidget(QLabel("Vcore:")); h_vcore.addWidget(self.vcore_manual_spin); h_vcore.addWidget(btn_set_vcore)
        
        h_page = QHBoxLayout()
        self.page_combo = QComboBox(); self.page_combo.addItems([f"Página {i}" for i in range(1, 7)])
        btn_page = QPushButton("Mudar Página OLED"); btn_page.clicked.connect(lambda: self.w_stm.set_page(self.page_combo.currentIndex()+1))
        h_page.addWidget(self.page_combo); h_page.addWidget(btn_page)
        
        btn_reset = QPushButton("HARD RESET SYSTEM"); btn_reset.setStyleSheet("background-color: #800; color: white;")
        btn_reset.clicked.connect(lambda: self.w_stm.send_manual_message("reset"))
        
        v_stm.addLayout(h_vcore)
        v_stm.addLayout(h_page)
        v_stm.addStretch()
        v_stm.addWidget(btn_reset)
        grp_stm.setLayout(v_stm)
        
        # Coluna 3: Console Manual & Varredura
        grp_manual = QGroupBox("Terminal & Varredura FPGA")
        v_man = QVBoxLayout()
        
        # --- Parte Manual ---
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
        
        # --- Separador Visual ---
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        v_man.addSpacing(10)
        v_man.addWidget(line)
        v_man.addSpacing(10)
        
        # --- Nova Parte: Controle de Varredura (0x0F) ---
        lbl_sweep = QLabel("<b>FPGA Sensor Sweep (0x0F)</b>")
        lbl_sweep.setAlignment(Qt.AlignCenter)
        v_man.addWidget(lbl_sweep)
        
        h_sweep = QHBoxLayout()
        
        # Switch Cíclico
        self.chk_auto_sweep = QCheckBox("Ciclo Automático")
        self.chk_auto_sweep.setToolTip("Envia 0x0F repetidamente")
        self.chk_auto_sweep.toggled.connect(self._toggle_sweep_timer)
        
        # Intervalo
        self.spin_sweep_interval = QSpinBox()
        self.spin_sweep_interval.setRange(50, 5000)
        self.spin_sweep_interval.setValue(100) # Default 100ms
        self.spin_sweep_interval.setSuffix(" ms")
        self.spin_sweep_interval.setToolTip("Período entre triggers")
        
        h_sweep.addWidget(self.chk_auto_sweep)
        h_sweep.addWidget(self.spin_sweep_interval)
        v_man.addLayout(h_sweep)
        
        # Botão de Disparo Único
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

    # --- Lógica de Negócio ---

    def _start_workers(self):
        # --- Arduino Worker ---
        self.w_ard = ArduinoWorker()
        self.t_ard = QThread()
        self.t_ard.setTerminationEnabled(True) 
        self.w_ard.moveToThread(self.t_ard)
        self.w_ard.log_message.connect(self.log_message)
        self.t_ard.start()
        self.w_ard.start() # Inicia loop lógico

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
        """Evento disparado ao tentar fechar a janela."""
        self.log_message("Encerrando sistema e parando threads...")
        
        # Para Timer de Sweep
        if self.sweep_timer.isActive():
            self.sweep_timer.stop()
        
        # 1. Para o sequenciador (Logger e Updates automáticos)
        if hasattr(self, 'seq'):
            self.stop_test_signal.emit()
            if hasattr(self, 't_seq') and self.t_seq.isRunning():
                self.t_seq.quit()
                self.t_seq.wait(100) 

        # 2. Desconecta o Router
        if hasattr(self, 'router'):
            self.router.disconnect_serial()

        # 3. Encerra Workers
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
        
        # Conecta Plots e Slack
        self.seq.plot_data_update.connect(self.plot1.update_plot_data)
        self.seq.plot_data_update.connect(self.plot2.update_plot_data)
        self.seq.plot_data_update.connect(self.update_slack_display)
        
        self.seq.test_finished.connect(self.on_finished)
        self.seq.log_message.connect(self.log_message)
        self.t_seq.start()

    @Slot(dict)
    def update_slack_display(self, d):
        s = d.get('dut_slack', 0)
        self.lbl_slack.setText(f"Slack Crítico: {s}")
        # Lógica visual de alerta
        if s < 0: color = "#D32F2F" # Vermelho forte (violação)
        elif s < 20: color = "#F57C00" # Laranja (alerta)
        else: color = "#388E3C" # Verde (ok)
        self.lbl_slack.setStyleSheet(f"background-color: {color}; color: white; font-weight: bold; padding: 5px; border-radius: 4px;")

    @Slot(bool)
    def _toggle_test(self, checked):
        if checked:
            # Configuração do Experimento
            cfg = {
                'test_name': self.txt_test_name.text(),
                'oven_setpoint': self.sp_input.value(),
                'psu_voltage': self.vcore_monitor.value(), 
                'kp': self.kp_input.value(), 
                'ki': self.ki_input.value(), 
                'kd': self.kd_input.value()
            }
            self.plot1.clear_plot(); self.plot2.clear_plot()
            self.start_test_signal.emit(cfg)
            self.btn_test.setText("PARAR EXPERIMENTO")
            self.btn_test.setStyleSheet("background-color: #C62828; color: white; font-weight: bold; font-size: 11pt;")
            
            self.vcore_monitor.setEnabled(False)
            
            # Opcional: Ativar varredura automática ao iniciar teste?
            # self.chk_auto_sweep.setChecked(True)
        else:
            self.stop_test_signal.emit()

    @Slot()
    def on_finished(self):
        self.btn_test.setChecked(False)
        self.btn_test.setText("INICIAR EXPERIMENTO")
        self.btn_test.setStyleSheet("background-color: #2E7D32; color: white; font-weight: bold; font-size: 11pt;")
        self.vcore_monitor.setEnabled(True)
        # self.chk_auto_sweep.setChecked(False)

    @Slot()
    def _manual_send(self):
        cmd = self.txt_manual.text()
        if "STM32" in self.cmb_target.currentText():
            self.w_stm.send_manual_message(cmd)
        else:
            self.w_croc.send_manual_command(cmd)
    
    # --- NOVOS SLOTS PARA TRIGGER 0x0F ---
    
    @Slot()
    def _send_sweep_trigger(self):
        """Envia o byte 0x0F cru para o Router -> FPGA"""
        # Usa _write_raw para evitar headers adicionais, garantindo que o FPGA Sniffer pegue '0F' limpo.
        # Se usar send_to_croc, ele envia 10 0F. O Sniffer deve pegar 0F de qualquer jeito, 
        # mas enviar raw é mais garantido para gatilhos de baixo nível.
        self.router._write_raw(b'\x0F\x0F')

    @Slot(bool)
    def _toggle_sweep_timer(self, checked):
        if checked:
            ms = self.spin_sweep_interval.value()
            self.sweep_timer.setInterval(ms)
            self.sweep_timer.start()
            self.btn_single_sweep.setEnabled(False)
            # ERROR WAS HERE: self.log_message.emit(...)
            # FIX: Call directly
            self.log_message(f"Varredura Automática Iniciada ({ms}ms)") 
        else:
            self.sweep_timer.stop()
            self.btn_single_sweep.setEnabled(True)
            # FIX: Call directly
            self.log_message("Varredura Automática Parada")

    @Slot()
    def _update_pid(self):
        self.w_ard.update_kp(self.kp_input.value())
        self.w_ard.update_ki(self.ki_input.value())
        self.w_ard.update_kd(self.kd_input.value())
        # FIX: Call directly
        self.log_message("PID Atualizado Manualmente.")

    @Slot(str)
    def log_message(self, msg):
        self.log_box.append(f"[{time.strftime('%H:%M:%S')}] {msg}")