"""
Janela Principal da HMI (PySide6)

Junta a UI (botões, gráfico) e os Workers (threads).
Adiciona controle em tempo real para PID e PSU.
Alterado para usar um botão de toggle (Ligar/Desligar) para o teste.
"""
import sys
import time
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QGroupBox, QFormLayout, QLineEdit, QTextEdit,
    QProgressBar, QLabel, QDoubleSpinBox
)
from PySide6.QtCore import QThread, Signal, Slot, QObject
import config
from workers import ArduinoWorker, PSUWorker, DUTWorker, TestSequencer
# Assume que plot_widget.py contém a classe PlotWidget (pyqtgraph)
from plot_widget import PlotWidget 

class MainWindow(QMainWindow):
    # Sinais para iniciar/parar workers em outros threads
    start_arduino_signal = Signal()
    stop_arduino_signal = Signal()
    start_psu_signal = Signal()
    stop_psu_signal = Signal()
    start_dut_signal = Signal()
    stop_dut_signal = Signal()
    
    # Sinal para o sequenciador
    start_test_signal = Signal(dict)
    stop_test_signal = Signal()
    
    # SINAIS DE CONTROLE EM TEMPO REAL
    update_pid_signal = Signal(float, float, float) # Kp, Ki, Kd
    update_psu_voltage_signal = Signal(float) # Setpoint Voltagem

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Supervisor de Teste de Envelhecimento - TCC")
        self.setGeometry(100, 100, 1200, 800)
        
        self.threads = {}
        self.workers = {}
        
        self._create_widgets()
        self._create_layout()
        self._start_device_workers()
        self._start_test_sequencer()
        self._connect_signals()

    def _create_widgets(self):
        """Cria todos os widgets da UI."""
        
        # --- Grupo 1: Controle do Teste ---
        self.test_control_group = QGroupBox("Controle do Teste")
        self.test_name_input = QLineEdit("Teste_001")
        
        # Botão de Toggle (Ligar/Desligar)
        self.toggle_test_button = QPushButton("INICIAR TESTE")
        self.toggle_test_button.setCheckable(True) # Define como botão de toggle
        self.toggle_test_button.setStyleSheet("background-color: green; color: white; font-weight: bold;")

        # --- Grupo 2: Parâmetros do Forno (PID) ---
        self.oven_control_group = QGroupBox("Parâmetros do Forno (Arduino)")
        self.oven_setpoint_input = QDoubleSpinBox()
        self.oven_setpoint_input.setRange(25.0, 200.0)
        self.oven_setpoint_input.setValue(100.0)
        
        self.oven_kp_input = QDoubleSpinBox()
        self.oven_kp_input.setDecimals(4)
        self.oven_kp_input.setValue(config.DEFAULT_KP)
        
        self.oven_ki_input = QDoubleSpinBox()
        self.oven_ki_input.setDecimals(5) # Aumentando precisão para o novo Ki
        self.oven_ki_input.setValue(config.DEFAULT_KI)
        
        self.oven_kd_input = QDoubleSpinBox()
        self.oven_kd_input.setDecimals(4)
        self.oven_kd_input.setValue(config.DEFAULT_KD)
        
        self.update_pid_button = QPushButton("Atualizar Ganhos PID")
        # Remove o estilo amarelo, volta ao padrão "Fusion" (cinza/escuro)
        # self.update_pid_button.setStyleSheet("background-color: #f7a31b; color: black;")

        # --- Grupo 3: Parâmetros da Fonte (PSU) ---
        self.psu_control_group = QGroupBox("Parâmetros da Fonte (PSU)")
        self.psu_setpoint_input = QDoubleSpinBox()
        self.psu_setpoint_input.setRange(0.0, 5.0)
        self.psu_setpoint_input.setValue(1.1)
        self.psu_setpoint_input.setSingleStep(0.1)
        self.psu_setpoint_input.setToolTip("Altere o valor e pressione ENTER para atualizar em tempo real.")

        # --- Grupo 4: Gráfico ---
        self.plot_widget = PlotWidget() # Instancia o widget do gráfico (versão pyqtgraph)

        # --- Grupo 5: Log de Eventos ---
        self.log_group = QGroupBox("Log de Eventos")
        self.log_text_edit = QTextEdit()
        self.log_text_edit.setReadOnly(True)

    def _create_layout(self):
        """Organiza os widgets na janela."""
        
        main_layout = QVBoxLayout()
        controls_layout = QHBoxLayout()
        
        # Coluna 1: Controle do Teste
        test_layout = QFormLayout()
        test_layout.addRow("Nome do Teste:", self.test_name_input)
        test_layout.addRow(self.toggle_test_button) # Adiciona o novo botão de toggle
        
        self.log_folder_label = QLabel(f"Pasta de Log: {config.LOG_FOLDER}")
        test_layout.addRow(self.log_folder_label)
        
        self.test_control_group.setLayout(test_layout)
        controls_layout.addWidget(self.test_control_group)
        
        # Coluna 2: Parâmetros do Forno
        oven_layout = QFormLayout()
        oven_layout.addRow("Setpoint (°C):", self.oven_setpoint_input)
        oven_layout.addRow("Kp:", self.oven_kp_input)
        oven_layout.addRow("Ki:", self.oven_ki_input)
        oven_layout.addRow("Kd:", self.oven_kd_input)
        oven_layout.addRow(self.update_pid_button)
        self.oven_control_group.setLayout(oven_layout)
        controls_layout.addWidget(self.oven_control_group)

        # Coluna 3: Parâmetros da Fonte
        psu_layout = QFormLayout()
        psu_layout.addRow("Setpoint (V):", self.psu_setpoint_input)
        self.psu_control_group.setLayout(psu_layout)
        controls_layout.addWidget(self.psu_control_group)
        
        main_layout.addLayout(controls_layout)
        main_layout.addWidget(self.plot_widget, stretch=1)
        
        log_layout = QVBoxLayout()
        log_layout.addWidget(self.log_text_edit)
        self.log_group.setLayout(log_layout)
        self.log_group.setFixedHeight(150)
        main_layout.addWidget(self.log_group)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def _start_worker(self, name, worker_class):
        """Função genérica para iniciar um worker em um QThread."""
        thread = QThread()
        if isinstance(worker_class, QObject):
             worker = worker_class
        else:
             worker = worker_class()
        
        self.threads[name] = thread
        self.workers[name] = worker
        
        worker.moveToThread(thread)
        worker.log_message.connect(self.log_message)
        
        thread.start()
        return worker

    def _start_device_workers(self):
        """Inicia os workers de hardware (PySerial) e conecta seus sinais de controle."""
        
        # Inicia Arduino Worker
        arduino_worker = self._start_worker("arduino", ArduinoWorker)
        self.start_arduino_signal.connect(arduino_worker.start)
        self.stop_arduino_signal.connect(arduino_worker.stop)
        self.update_pid_signal.connect(arduino_worker.update_pid_gains) 
        self.start_arduino_signal.emit()
        
        # Inicia PSU Worker
        psu_worker = self._start_worker("psu", PSUWorker)
        self.start_psu_signal.connect(psu_worker.start)
        self.stop_psu_signal.connect(psu_worker.stop)
        self.update_psu_voltage_signal.connect(psu_worker.set_voltage)
        self.start_psu_signal.emit()

        # Inicia DUT Worker
        dut_worker = self._start_worker("dut", DUTWorker)
        self.start_dut_signal.connect(dut_worker.start)
        self.stop_dut_signal.connect(dut_worker.stop)
        self.start_dut_signal.emit()

    def _start_test_sequencer(self):
        """Inicia o worker "mestre" que gerencia o teste."""
        
        sequencer_worker = TestSequencer(
            self.workers["arduino"], 
            self.workers["psu"], 
            self.workers["dut"]
        )
        self._start_worker("sequencer", sequencer_worker)
        
        self.start_test_signal.connect(sequencer_worker.start_test)
        self.stop_test_signal.connect(sequencer_worker.stop_test)
        
        sequencer_worker.plot_data_update.connect(self.plot_widget.update_plot_data)
        sequencer_worker.test_finished.connect(self.on_test_finished)


    def _connect_signals(self):
        """Conecta os botões da HMI aos seus slots, incluindo os de controle em tempo real."""
        
        # Conecta o novo botão de toggle
        self.toggle_test_button.clicked.connect(self.on_toggle_test)
        
        # Conecta botões/inputs de atualização de parâmetros em tempo real
        self.update_pid_button.clicked.connect(self.on_update_pid)
        self.psu_setpoint_input.editingFinished.connect(self.on_update_psu_voltage)
        
    # --- Slots da HMI (Ações do Usuário) ---
    
    @Slot(str)
    def log_message(self, message):
        """Adiciona uma mensagem à caixa de log da HMI."""
        self.log_text_edit.append(f"[{time.strftime('%H:%M:%S')}] {message}")

    @Slot(bool)
    def on_toggle_test(self, checked):
        """Chamado pelo botão de toggle INICIAR/PARAR."""
        
        if checked:
            # Estado "Ligado" -> INICIAR o teste
            self.log_message("Coletando configurações do teste...")
            
            settings = {
                'test_name': self.test_name_input.text(),
                'oven_setpoint': self.oven_setpoint_input.value(),
                'psu_voltage': self.psu_setpoint_input.value(),
                'kp': self.oven_kp_input.value(),
                'ki': self.oven_ki_input.value(),
                'kd': self.oven_kd_input.value()
            }
            
            self.plot_widget.clear_plot()
            self.start_test_signal.emit(settings)
            
            # Atualiza UI para o estado "Rodando"
            self.toggle_test_button.setText("PARAR TESTE")
            self.toggle_test_button.setStyleSheet("background-color: red; color: white; font-weight: bold;")
            self.oven_setpoint_input.setEnabled(False)
            self.test_name_input.setEnabled(False)
            self.psu_setpoint_input.setEnabled(True) # Mantém ajustável
            
        else:
            # Estado "Desligado" -> PARAR o teste
            self.stop_test_signal.emit()
            
            # A UI será redefinida pelo slot on_test_finished
            # Mas podemos forçar aqui para garantir, caso o stop_test_signal falhe
            self.on_test_finished() 

    @Slot()
    def on_update_pid(self):
        """Chamado pelo botão 'Atualizar Ganhos PID'."""
        kp = self.oven_kp_input.value()
        ki = self.oven_ki_input.value()
        kd = self.oven_kd_input.value()
        
        self.log_message(f"Enviando novos ganhos PID em tempo real: Kp={kp}, Ki={ki}, Kd={kd}")
        self.update_pid_signal.emit(kp, ki, kd)

    @Slot()
    def on_update_psu_voltage(self):
        """Chamado quando o campo do setpoint da PSU perde o foco (editingFinished)."""
        voltage = self.psu_setpoint_input.value()
        
        self.log_message(f"Enviando novo setpoint de tensão da PSU em tempo real: {voltage}V")
        self.update_psu_voltage_signal.emit(voltage)

    @Slot()
    def on_test_finished(self):
        """Slot chamado pelo Sequencer quando o teste é finalizado ou parado."""
        
        # Reseta o botão de toggle para o estado "INICIAR"
        self.toggle_test_button.setText("INICIAR TESTE")
        self.toggle_test_button.setStyleSheet("background-color: green; color: white; font-weight: bold;")
        self.toggle_test_button.setChecked(False) # Força o estado "desligado"
        
        # Destrava os controles
        self.test_control_group.setEnabled(True)
        self.oven_setpoint_input.setEnabled(True)
        self.psu_setpoint_input.setEnabled(True)
        self.test_name_input.setEnabled(True)
        
    def closeEvent(self, event):
        """Garante que todos os threads sejam fechados ao sair."""
        self.log_message("Fechando todos os threads e dispositivos...")
        
        self.stop_test_signal.emit()
        self.stop_arduino_signal.emit()
        self.stop_psu_signal.emit()
        self.stop_dut_signal.emit()
        
        for name, thread in self.threads.items():
            if thread.isRunning():
                thread.quit()
                thread.wait(500)
                
        event.accept()