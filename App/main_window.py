"""
Janela Principal da HMI (PySide6)

Junta a UI (botões, gráfico) e os Workers (threads).
"""
import sys
import time
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QGroupBox, QFormLayout, QLineEdit, QTextEdit,
    QProgressBar, QLabel, QDoubleSpinBox
)
from PySide6.QtCore import QThread, Signal, Slot
import config
from workers import ArduinoWorker, PSUWorker, DUTWorker, TestSequencer
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

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Supervisor de Teste de Envelhecimento - TCC")
        self.setGeometry(100, 100, 1200, 800)
        
        # Dicionário para armazenar threads e workers
        self.threads = {}
        self.workers = {}
        
        self._create_widgets()
        self._create_layout()
        self._connect_signals()
        
        self._start_device_workers()
        self._start_test_sequencer()

    def _create_widgets(self):
        """Cria todos os widgets da UI."""
        
        # --- Grupo 1: Controle do Teste ---
        self.test_control_group = QGroupBox("Controle do Teste")
        self.test_name_input = QLineEdit("Teste_001")
        self.start_test_button = QPushButton("INICIAR TESTE")
        self.start_test_button.setStyleSheet("background-color: green; color: white; font-weight: bold;")
        self.stop_test_button = QPushButton("PARAR TESTE")
        self.stop_test_button.setStyleSheet("background-color: red; color: white; font-weight: bold;")
        self.stop_test_button.setEnabled(False)

        # --- Grupo 2: Parâmetros do Forno (PID) ---
        self.oven_control_group = QGroupBox("Parâmetros do Forno (Arduino)")
        self.oven_setpoint_input = QDoubleSpinBox()
        self.oven_setpoint_input.setRange(25.0, 200.0)
        self.oven_setpoint_input.setValue(100.0)
        self.oven_kp_input = QDoubleSpinBox()
        self.oven_kp_input.setDecimals(4); self.oven_kp_input.setValue(config.DEFAULT_KP)
        self.oven_ki_input = QDoubleSpinBox()
        self.oven_ki_input.setDecimals(4); self.oven_ki_input.setValue(config.DEFAULT_KI)
        self.oven_kd_input = QDoubleSpinBox()
        self.oven_kd_input.setDecimals(4); self.oven_kd_input.setValue(config.DEFAULT_KD)
        self.update_pid_button = QPushButton("Atualizar Ganhos PID")

        # --- Grupo 3: Parâmetros da Fonte (PSU) ---
        self.psu_control_group = QGroupBox("Parâmetros da Fonte (PSU)")
        self.psu_setpoint_input = QDoubleSpinBox()
        self.psu_setpoint_input.setRange(0.0, 5.0)
        self.psu_setpoint_input.setValue(1.1)
        self.psu_setpoint_input.setSingleStep(0.1)

        # --- Grupo 4: Gráfico ---
        self.plot_widget = PlotWidget()

        # --- Grupo 5: Log de Eventos ---
        self.log_group = QGroupBox("Log de Eventos")
        self.log_text_edit = QTextEdit()
        self.log_text_edit.setReadOnly(True)

    def _create_layout(self):
        """Organiza os widgets na janela."""
        
        # Layout Principal (Vertical)
        main_layout = QVBoxLayout()
        
        # Layout Superior (Controles - Horizontal)
        controls_layout = QHBoxLayout()
        
        # Coluna 1: Controle do Teste
        test_layout = QFormLayout()
        test_layout.addRow("Nome do Teste:", self.test_name_input)
        test_layout.addRow(self.start_test_button)
        test_layout.addRow(self.stop_test_button)
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
        
        # Adiciona controles ao layout principal
        main_layout.addLayout(controls_layout)
        
        # Adiciona o gráfico
        main_layout.addWidget(self.plot_widget, stretch=1) # stretch=1 faz o gráfico expandir
        
        # Adiciona a caixa de log
        log_layout = QVBoxLayout()
        log_layout.addWidget(self.log_text_edit)
        self.log_group.setLayout(log_layout)
        self.log_group.setFixedHeight(150) # Altura fixa para o log
        main_layout.addWidget(self.log_group)

        # Define o widget central
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def _start_worker(self, name, worker_class):
        """Função genérica para iniciar um worker em um QThread."""
        thread = QThread()
        worker = worker_class()
        
        self.threads[name] = thread
        self.workers[name] = worker
        
        worker.moveToThread(thread)
        
        # Conecta o sinal de log do worker à HMI
        worker.log_message.connect(self.log_message)
        
        thread.start()
        return worker

    def _start_device_workers(self):
        """Inicia os workers de hardware (Arduino, PSU, DUT)."""
        # Inicia Arduino Worker
        arduino_worker = self._start_worker("arduino", ArduinoWorker)
        self.start_arduino_signal.connect(arduino_worker.start)
        self.stop_arduino_signal.connect(arduino_worker.stop)
        self.start_arduino_signal.emit() # Conecta imediatamente
        
        # Inicia PSU Worker
        psu_worker = self._start_worker("psu", PSUWorker)
        self.start_psu_signal.connect(psu_worker.start)
        self.stop_psu_signal.connect(psu_worker.stop)
        self.start_psu_signal.emit() # Conecta imediatamente

        # Inicia DUT Worker
        dut_worker = self._start_worker("dut", DUTWorker)
        self.start_dut_signal.connect(dut_worker.start)
        self.stop_dut_signal.connect(dut_worker.stop)
        self.start_dut_signal.emit() # Conecta imediatamente

    def _start_test_sequencer(self):
        """Inicia o worker "mestre" que gerencia o teste."""
        
        # O Sequenciador precisa de referências aos outros workers
        sequencer_worker = self._start_worker("sequencer", 
            lambda: TestSequencer(
                self.workers["arduino"], 
                self.workers["psu"], 
                self.workers["dut"]
            )
        )
        
        # Conecta o sequenciador à HMI
        self.start_test_signal.connect(sequencer_worker.start_test)
        self.stop_test_signal.connect(sequencer_worker.stop_test)
        
        # Conecta o sequenciador ao gráfico
        sequencer_worker.plot_data_update.connect(self.plot_widget.update_plot_data)
        
        # Conecta o fim do teste de volta aos botões
        sequencer_worker.test_finished.connect(self.on_test_finished)


    def _connect_signals(self):
        """Conecta os botões da HMI aos seus slots."""
        self.start_test_button.clicked.connect(self.on_start_test)
        self.stop_test_button.clicked.connect(self.on_stop_test)
        
        # Conecta botões de atualização de parâmetros aos workers
        # (Ex: Atualizar PID em tempo real)
        # self.update_pid_button.clicked.connect(self.on_update_pid)
        # self.psu_setpoint_input.editingFinished.connect(self.on_update_psu_voltage)
        
    # --- Slots da HMI (Ações do Usuário) ---
    
    @Slot(str)
    def log_message(self, message):
        """Adiciona uma mensagem à caixa de log da HMI."""
        self.log_text_edit.append(f"[{time.strftime('%H:%M:%S')}] {message}")

    @Slot()
    def on_start_test(self):
        """Chamado pelo botão INICIAR TESTE."""
        self.log_message("Coletando configurações do teste...")
        
        # Coleta todas as configurações da HMI
        settings = {
            'test_name': self.test_name_input.text(),
            'oven_setpoint': self.oven_setpoint_input.value(),
            'psu_voltage': self.psu_setpoint_input.value(),
            'kp': self.oven_kp_input.value(),
            'ki': self.oven_ki_input.value(),
            'kd': self.oven_kd_input.value()
        }
        
        # Limpa o gráfico para o novo teste
        self.plot_widget.clear_plot()
        
        # Envia o sinal para o TestSequencer iniciar
        self.start_test_signal.emit(settings)
        
        # Atualiza a UI
        self.start_test_button.setEnabled(False)
        self.stop_test_button.setEnabled(True)
        self.test_control_group.setEnabled(False) # Trava os controles

    @Slot()
    def on_stop_test(self):
        """Chamado pelo botão PARAR TESTE."""
        self.stop_test_signal.emit()

    @Slot()
    def on_test_finished(self):
        """Slot chamado pelo Sequencer quando o teste é finalizado."""
        self.start_test_button.setEnabled(True)
        self.stop_test_button.setEnabled(False)
        self.test_control_group.setEnabled(True) # Destrava os controles
        
    def closeEvent(self, event):
        """Garante que todos os threads sejam fechados ao sair."""
        self.log_message("Fechando todos os threads e dispositivos...")
        
        # Emite sinais para parar todos os workers
        self.stop_test_signal.emit()
        self.stop_arduino_signal.emit()
        self.stop_psu_signal.emit()
        self.stop_dut_signal.emit()
        
        # Dá 1 segundo para os threads fecharem
        time.sleep(1) 
        
        for name, thread in self.threads.items():
            if thread.isRunning():
                thread.quit()
                thread.wait(1000) # Espera 1s
                
        event.accept()