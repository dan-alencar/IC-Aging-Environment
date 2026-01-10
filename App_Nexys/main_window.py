"""
=============================================================================
TCC - Janela Principal da HMI (VERSÃO FINAL)
=============================================================================
Interface gráfica principal para supervisão do teste de envelhecimento.

Características:
  - Controle centralizado de início/parada de teste
  - Visualização em tempo real (temperatura, tensão, corrente, slack)
  - Log de eventos
  - Parâmetros PID fixos (não alteráveis em tempo de execução)

Autor: [Seu Nome]
Data: Janeiro/2026
=============================================================================
"""
import sys
import time
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QGroupBox, QFormLayout, QLineEdit, QTextEdit,
    QLabel, QDoubleSpinBox
)
from PySide6.QtGui import QFont
from PySide6.QtCore import QThread, Signal, Slot

import config
from workers import ArduinoWorker, PSUWorker, DUTWorker, TestSequencer
from plot_widget import PlotWidget 
from aux_plot_widget import AuxPlotWidget 


class MainWindow(QMainWindow):
    """Janela principal da aplicação supervisória."""
    
    # Sinais para controle de workers
    start_arduino_signal = Signal()
    stop_arduino_signal = Signal()
    start_psu_signal = Signal()
    stop_psu_signal = Signal()
    start_dut_signal = Signal()
    stop_dut_signal = Signal()
    
    # Sinais para o sequenciador
    start_test_signal = Signal(dict)
    stop_test_signal = Signal()
    
    # Sinais de controle em tempo real (apenas setpoints, não PID)
    update_psu_voltage_signal = Signal(float)
    update_oven_setpoint_signal = Signal(float)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("TCC - Supervisor de Teste de Envelhecimento")
        self.setGeometry(100, 100, 1400, 900)
        
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
        
        self.toggle_test_button = QPushButton("INICIAR TESTE")
        self.toggle_test_button.setCheckable(True)
        self.toggle_test_button.setStyleSheet(
            "background-color: #28a745; color: white; font-weight: bold; "
            "padding: 10px; font-size: 14px;"
        )

        # --- Grupo 2: Parâmetros do Forno ---
        self.oven_control_group = QGroupBox("Parâmetros do Forno")
        
        self.oven_setpoint_input = QDoubleSpinBox()
        self.oven_setpoint_input.setRange(25.0, 150.0)
        self.oven_setpoint_input.setValue(100.0)
        self.oven_setpoint_input.setSuffix(" °C")
        self.oven_setpoint_input.setToolTip("Setpoint de temperatura do forno")
        
        # Labels de parâmetros PID (somente leitura)
        self.pid_info_label = QLabel()
        self.pid_info_label.setText(
            f"<b>Parâmetros PID (Fixos):</b><br>"
            f"Kp = {config.PID_KP:.4f}<br>"
            f"Ki = {config.PID_KI:.6f}<br>"
            f"Kd = {config.PID_KD:.4f}"
        )
        self.pid_info_label.setStyleSheet(
            "background-color: #2d2d2d; padding: 8px; border-radius: 4px;"
        )
        
        # --- Grupo 3: Parâmetros da Fonte e DUT ---
        self.psu_control_group = QGroupBox("Fonte PSU e DUT")
        
        self.psu_setpoint_input = QDoubleSpinBox()
        self.psu_setpoint_input.setRange(0.0, 1.2)
        self.psu_setpoint_input.setValue(1.0)
        self.psu_setpoint_input.setSingleStep(0.01)
        self.psu_setpoint_input.setSuffix(" V")
        self.psu_setpoint_input.setToolTip("Tensão de saída da fonte")

        # Widget de Slack
        self.slack_label = QLabel("Slack: -- Inc.")
        slack_font = self.slack_label.font()
        slack_font.setPointSize(16)
        slack_font.setBold(True)
        self.slack_label.setFont(slack_font)
        self.slack_label.setStyleSheet("""
            QLabel {
                color: #00ff00;
                background-color: #1a1a1a;
                border: 2px solid #333333;
                border-radius: 6px;
                padding: 10px;
            }
        """)

        # --- Grupo 4: Gráficos ---
        self.plot_widget = PlotWidget(plot_window_size=300)
        self.aux_plot_widget = AuxPlotWidget(plot_window_size=300)

        # --- Grupo 5: Log de Eventos ---
        self.log_group = QGroupBox("Log de Eventos")
        self.log_text_edit = QTextEdit()
        self.log_text_edit.setReadOnly(True)
        self.log_text_edit.setStyleSheet(
            "font-family: 'Consolas', 'Monaco', monospace; font-size: 11px;"
        )

    def _create_layout(self):
        """Organiza os widgets na janela."""
        
        main_layout = QVBoxLayout()
        controls_layout = QHBoxLayout()
        
        # Coluna 1: Controle do Teste
        test_layout = QFormLayout()
        test_layout.addRow("Nome do Teste:", self.test_name_input)
        test_layout.addRow(self.toggle_test_button)
        
        self.log_folder_label = QLabel(f"<small>Logs: {config.LOG_FOLDER}</small>")
        test_layout.addRow(self.log_folder_label)
        
        self.test_control_group.setLayout(test_layout)
        controls_layout.addWidget(self.test_control_group)
        
        # Coluna 2: Parâmetros do Forno
        oven_layout = QVBoxLayout()
        oven_form = QFormLayout()
        oven_form.addRow("Setpoint:", self.oven_setpoint_input)
        oven_layout.addLayout(oven_form)
        oven_layout.addWidget(self.pid_info_label)
        oven_layout.addStretch()
        
        self.oven_control_group.setLayout(oven_layout)
        controls_layout.addWidget(self.oven_control_group)

        # Coluna 3: PSU e DUT
        psu_layout = QVBoxLayout()
        psu_form = QFormLayout()
        psu_form.addRow("Tensão PSU:", self.psu_setpoint_input)
        psu_layout.addLayout(psu_form)
        psu_layout.addWidget(QLabel("<b>Sensor de Degradação:</b>"))
        psu_layout.addWidget(self.slack_label)
        psu_layout.addStretch()

        self.psu_control_group.setLayout(psu_layout)
        controls_layout.addWidget(self.psu_control_group)
        
        # Layout dos gráficos
        plots_layout = QHBoxLayout()
        plots_layout.addWidget(self.plot_widget, stretch=1)
        plots_layout.addWidget(self.aux_plot_widget, stretch=1)

        main_layout.addLayout(controls_layout)
        main_layout.addLayout(plots_layout, stretch=1)
        
        # Log
        log_layout = QVBoxLayout()
        log_layout.addWidget(self.log_text_edit)
        self.log_group.setLayout(log_layout)
        main_layout.addWidget(self.log_group)

        # Widget central
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def _start_worker(self, name, worker_class_or_instance):
        """Inicia um worker em sua própria thread."""
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
        """Inicia workers de hardware."""
        
        # Arduino Worker
        arduino_worker = self._start_worker("arduino", ArduinoWorker)
        self.start_arduino_signal.connect(arduino_worker.start)
        self.stop_arduino_signal.connect(arduino_worker.stop)
        self.update_oven_setpoint_signal.connect(arduino_worker.set_target_setpoint)
        self.start_arduino_signal.emit()
        
        # PSU Worker
        psu_worker = self._start_worker("psu", PSUWorker)
        self.start_psu_signal.connect(psu_worker.start)
        self.stop_psu_signal.connect(psu_worker.stop)
        self.update_psu_voltage_signal.connect(psu_worker.set_voltage)
        self.start_psu_signal.emit()

        # DUT Worker
        dut_worker = self._start_worker("dut", DUTWorker)
        self.start_dut_signal.connect(dut_worker.start)
        self.stop_dut_signal.connect(dut_worker.stop)
        self.start_dut_signal.emit()

    def _start_test_sequencer(self):
        """Inicia o worker orquestrador do teste."""
        
        sequencer_worker = TestSequencer(
            self.workers["arduino"], 
            self.workers["psu"], 
            self.workers["dut"]
        )
        self._start_worker("sequencer", sequencer_worker)
        
        self.start_test_signal.connect(sequencer_worker.start_test)
        self.stop_test_signal.connect(sequencer_worker.stop_test)
        
        # Conecta sinais de dados aos gráficos
        sequencer_worker.plot_data_update.connect(self.plot_widget.update_plot_data)
        sequencer_worker.plot_data_update.connect(self.aux_plot_widget.update_plot_data)
        sequencer_worker.plot_data_update.connect(self.update_slack_label)
        
        sequencer_worker.test_finished.connect(self.on_test_finished)

    def _connect_signals(self):
        """Conecta sinais da UI aos slots."""
        self.toggle_test_button.clicked.connect(self.on_toggle_test)
        self.psu_setpoint_input.editingFinished.connect(self.on_update_psu_voltage)
        self.oven_setpoint_input.editingFinished.connect(self.on_update_oven_setpoint)

    # =========================================================================
    #   SLOTS
    # =========================================================================
    
    @Slot(str)
    def log_message(self, message):
        """Adiciona mensagem ao log."""
        timestamp = time.strftime('%H:%M:%S')
        self.log_text_edit.append(f"[{timestamp}] {message}")

    @Slot(dict)
    def update_slack_label(self, data_row):
        """Atualiza display do slack."""
        slack_value = data_row.get('dut_slack', 0)
        self.slack_label.setText(f"Slack: {slack_value} Inc.")
        
        # Alerta visual se slack baixo
        if slack_value < 20 and slack_value > 0:
            self.slack_label.setStyleSheet("""
                QLabel {
                    color: #ff4444;
                    background-color: #1a1a1a;
                    border: 2px solid #ff0000;
                    border-radius: 6px;
                    padding: 10px;
                }
            """)
        else:
            self.slack_label.setStyleSheet("""
                QLabel {
                    color: #00ff00;
                    background-color: #1a1a1a;
                    border: 2px solid #333333;
                    border-radius: 6px;
                    padding: 10px;
                }
            """)

    @Slot(bool)
    def on_toggle_test(self, checked):
        """Handler do botão de toggle."""
        
        if checked:
            # INICIAR teste
            self.log_message("Preparando teste...")
            
            settings = {
                'test_name': self.test_name_input.text(),
                'oven_setpoint': self.oven_setpoint_input.value(),
                'psu_voltage': self.psu_setpoint_input.value()
            }
            
            # Limpa gráficos
            self.plot_widget.clear_plot()
            self.aux_plot_widget.clear_plot()
            self.update_slack_label({'dut_slack': 0})
            
            self.start_test_signal.emit(settings)
            
            # Atualiza UI
            self.toggle_test_button.setText("PARAR TESTE")
            self.toggle_test_button.setStyleSheet(
                "background-color: #dc3545; color: white; font-weight: bold; "
                "padding: 10px; font-size: 14px;"
            )
            self.test_name_input.setEnabled(False)
            
        else:
            # PARAR teste
            self.stop_test_signal.emit()
            self.on_test_finished()

    @Slot()
    def on_update_psu_voltage(self):
        """Atualiza tensão da PSU em tempo real."""
        voltage = self.psu_setpoint_input.value()
        self.log_message(f"Atualizando tensão PSU: {voltage:.3f}V")
        self.update_psu_voltage_signal.emit(voltage)
    
    @Slot()
    def on_update_oven_setpoint(self):
        """Atualiza setpoint do forno em tempo real."""
        setpoint = self.oven_setpoint_input.value()
        self.log_message(f"Atualizando setpoint forno: {setpoint:.1f}°C")
        self.update_oven_setpoint_signal.emit(setpoint)

    @Slot()
    def on_test_finished(self):
        """Handler de fim de teste."""
        
        self.toggle_test_button.setText("INICIAR TESTE")
        self.toggle_test_button.setStyleSheet(
            "background-color: #28a745; color: white; font-weight: bold; "
            "padding: 10px; font-size: 14px;"
        )
        self.toggle_test_button.setChecked(False)
        self.test_name_input.setEnabled(True)
        
    def closeEvent(self, event):
        """Encerra todos os threads ao fechar."""
        self.log_message("Encerrando aplicação...")
        
        self.stop_test_signal.emit()
        self.stop_arduino_signal.emit()
        self.stop_psu_signal.emit()
        self.stop_dut_signal.emit()
        
        for name, thread in self.threads.items():
            if thread.isRunning():
                thread.quit()
                thread.wait(1000)
                
        event.accept()
