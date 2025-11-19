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
from PySide6.QtGui import QFont
from PySide6.QtCore import QThread, Signal, Slot, QObject
import config
from workers import ArduinoWorker, PSUWorker, DUTWorker, TestSequencer
# Assume que plot_widget.py contém a classe PlotWidget (pyqtgraph)
from plot_widget import PlotWidget 
# Importa o widget auxiliar de plotagem (agora só V e A)
from aux_plot_widget import AuxPlotWidget 

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
    update_kp_signal = Signal(float) 
    update_ki_signal = Signal(float)
    update_kd_signal = Signal(float)
    update_psu_voltage_signal = Signal(float) # Setpoint Voltagem
    update_oven_setpoint = Signal(float)

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
        self.oven_setpoint_input.setToolTip("Altere o valor e pressione ENTER para atualizar em tempo real.")
        
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
        
        # --- Grupo 3: Parâmetros da Fonte (PSU) + Novo Widget Slack ---
        self.psu_control_group = QGroupBox("Parâmetros da Fonte e DUT") # Nome ajustado
        self.psu_setpoint_input = QDoubleSpinBox()
        self.psu_setpoint_input.setRange(0.0, 5.0)
        self.psu_setpoint_input.setValue(1.0)
        self.psu_setpoint_input.setSingleStep(0.1)
        self.psu_setpoint_input.setToolTip("Altere o valor e pressione ENTER para atualizar em tempo real.")

        # NOVO WIDGET: Exibição do Slack
        self.slack_label = QLabel("Slack: 0 Inc.")

        # --- Configurações de Fonte ---
        # Vamos manter o tamanho grande para visibilidade (16),
        # mas podemos optar por um peso de fonte ligeiramente menor (se disponível)
        # ou manter o Bold se for essencial para o destaque.
        slack_font = self.slack_label.font()
        slack_font.setPointSize(14)  # Um pouco menor para sobriedade
        slack_font.setWeight(QFont.DemiBold) # Se for QFont no Qt
        # No PySide/PyQt, setBold(True) é equivalente a setWeight(QFont.Bold).
        # Vamos manter o setBold(True) para garantir o destaque de forma padrão.
        slack_font.setBold(True)
        self.slack_label.setFont(slack_font)

        # --- Configurações de Estilo (CSS) ---
        # Cores e Borda para Formalidade:
        # 1. 'lightgray' ou 'silver': Cor mais neutra que o branco puro.
        # 2. Borda sutil: Adiciona definição sem ser agressiva.
        # 3. Background/Padding: Mantemos um padding limpo.
        self.slack_label.setStyleSheet("""
            QLabel {
                color: #C0C0C0;          /* Cor prateada/cinza claro para sobriedade */
                background-color: #333333; /* Fundo cinza escuro ou preto (se estiver em um tema escuro) */
                border: 1px solid #555555; /* Borda sutil para delimitar o widget */
                border-radius: 4px;      /* Cantos levemente arredondados */
                padding: 5px 8px;        /* Ajuste de padding */
            }
        """)


        # --- Grupo 4: Gráfico ---
        self.plot_widget = PlotWidget() # Instancia o widget do gráfico principal
        self.aux_plot_widget = AuxPlotWidget() # Instancia o widget do gráfico auxiliar (V e A)

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
        test_layout.addRow(self.toggle_test_button) 
        
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

        # Coluna 3: Parâmetros da Fonte + Slack (usando QVBoxLayout para o grupo)
        psu_group_v_layout = QVBoxLayout()
        psu_layout = QFormLayout()
        psu_layout.addRow("Setpoint (V):", self.psu_setpoint_input)
        
        psu_group_v_layout.addLayout(psu_layout)
        psu_group_v_layout.addWidget(self.slack_label) # Adiciona o Slack abaixo do form
        psu_group_v_layout.addStretch(1) # Empurra o conteúdo para cima

        self.psu_control_group.setLayout(psu_group_v_layout)
        controls_layout.addWidget(self.psu_control_group)
        
        # Layout para os gráficos lado a lado
        plots_layout = QHBoxLayout()
        plots_layout.addWidget(self.plot_widget, stretch=1)
        plots_layout.addWidget(self.aux_plot_widget, stretch=1) 

        main_layout.addLayout(controls_layout)
        main_layout.addLayout(plots_layout, stretch=1) 
        
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
        self.update_kp_signal.connect(arduino_worker.update_kp) 
        self.update_ki_signal.connect(arduino_worker.update_ki)
        self.update_kd_signal.connect(arduino_worker.update_kd)
        self.update_oven_setpoint.connect(arduino_worker.set_target_setpoint)
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
        
        # Conecta o sinal de atualização de dados a AMBOS os gráficos
        sequencer_worker.plot_data_update.connect(self.plot_widget.update_plot_data)
        sequencer_worker.plot_data_update.connect(self.aux_plot_widget.update_plot_data)
        
        # NOVO: Conecta o sinal de atualização de dados ao novo slot de Slack
        sequencer_worker.plot_data_update.connect(self.update_slack_label) 
        
        sequencer_worker.test_finished.connect(self.on_test_finished)


    def _connect_signals(self):
        """Conecta os botões da HMI aos seus slots, incluindo os de controle em tempo real."""
        
        # Conecta o novo botão de toggle
        self.toggle_test_button.clicked.connect(self.on_toggle_test)
        
        # Conecta botões/inputs de atualização de parâmetros em tempo real
        self.update_pid_button.clicked.connect(self.on_update_pid)
        self.psu_setpoint_input.editingFinished.connect(self.on_update_psu_voltage)
        self.oven_setpoint_input.editingFinished.connect(self.on_update_oven_setpoint)
        
    # --- Slots da HMI (Ações do Usuário) ---
    
    @Slot(str)
    def log_message(self, message):
        """Adiciona uma mensagem à caixa de log da HMI."""
        self.log_text_edit.append(f"[{time.strftime('%H:%M:%S')}] {message}")

    @Slot(dict)
    def update_slack_label(self, data_row):
        """Atualiza a label de Slack em tempo real."""
        slack_value = data_row.get('dut_slack', 0)
        self.slack_label.setText(f"Slack: {slack_value} Inc.")
        if slack_value < 20:
             self.slack_label.setStyleSheet("""
            QLabel {
                color: red;          /* Cor prateada/cinza claro para sobriedade */
                background-color: #333333; /* Fundo cinza escuro ou preto (se estiver em um tema escuro) */
                border: 1px solid #555555; /* Borda sutil para delimitar o widget */
                border-radius: 4px;      /* Cantos levemente arredondados */
                padding: 5px 8px;        /* Ajuste de padding */
            }
        """)
        else:
             self.slack_label.setStyleSheet("""
            QLabel {
                color: #C0C0C0;          /* Cor prateada/cinza claro para sobriedade */
                background-color: #333333; /* Fundo cinza escuro ou preto (se estiver em um tema escuro) */
                border: 1px solid #555555; /* Borda sutil para delimitar o widget */
                border-radius: 4px;      /* Cantos levemente arredondados */
                padding: 5px 8px;        /* Ajuste de padding */
            }
            """)


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
            self.aux_plot_widget.clear_plot() 
            self.update_slack_label({'dut_slack': 0}) # Reseta a label
            self.start_test_signal.emit(settings)
            
            # Atualiza UI para o estado "Rodando"
            self.toggle_test_button.setText("PARAR TESTE")
            self.toggle_test_button.setStyleSheet("background-color: red; color: white; font-weight: bold;")
            self.oven_setpoint_input.setEnabled(True)
            self.test_name_input.setEnabled(False)
            self.psu_setpoint_input.setEnabled(True)
            self.oven_kp_input.setEnabled(False)
            self.oven_ki_input.setEnabled(False)
            self.oven_kd_input.setEnabled(False)
            self.update_pid_button.setEnabled(False)
            
        else:
            # Estado "Desligado" -> PARAR o teste
            self.stop_test_signal.emit()
            self.on_test_finished() 

    @Slot()
    def on_update_pid(self):
        """Chamado pelo botão 'Atualizar Ganhos PID'."""
        kp = self.oven_kp_input.value()
        ki = self.oven_ki_input.value()
        kd = self.oven_kd_input.value()
        
        self.log_message(f"Enviando novos ganhos PID em tempo real: Kp={kp}, Ki={ki}, Kd={kd}")
        
        self.update_kp_signal.emit(kp)
        time.sleep(0.05) 
        self.update_ki_signal.emit(ki)
        time.sleep(0.05)
        self.update_kd_signal.emit(kd)

    @Slot()
    def on_update_psu_voltage(self):
        """Chamado quando o campo do setpoint da PSU perde o foco (editingFinished)."""
        voltage = self.psu_setpoint_input.value()
        
        self.log_message(f"Enviando novo setpoint de tensão da PSU em tempo real: {voltage}V")
        self.update_psu_voltage_signal.emit(voltage)
    
    @Slot()
    def on_update_oven_setpoint(self):
        """Chamado quando o campo do setpoint da PSU perde o foco (editingFinished)."""
        setpoint = self.oven_setpoint_input.value()
        
        self.log_message(f"Enviando novo setpoint de temperatura do Forno em tempo real: {setpoint} graus Celsius")
        self.update_oven_setpoint.emit(setpoint)

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
        self.update_pid_button.setEnabled(True)
        self.oven_kp_input.setEnabled(True)
        self.oven_ki_input.setEnabled(True)
        self.oven_kd_input.setEnabled(True)
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