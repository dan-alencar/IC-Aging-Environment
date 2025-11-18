import sys
import os
import glob
import platform
import serial.tools.list_ports
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QGridLayout, QComboBox, 
    QPushButton, QLabel, QMessageBox, QGroupBox, QSpinBox
)
import config

class SetupDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Configuração do Sistema - TCC")
        self.setGeometry(200, 200, 650, 400) # Janela um pouco mais larga
        self.setModal(True)
        
        self.available_ports = self._get_serial_ports()
        self._create_widgets()
        self._load_current_config()

    def _get_serial_ports(self):
        """Lista portas seriais (Serial + USBTMC) filtrando ttyS."""
        system_os = platform.system()
        port_list = []
        port_list.append(("", "Selecione uma porta..."))

        # 1. Listar Portas Seriais Comuns (Arduino, DUT)
        ports = serial.tools.list_ports.comports()
        
        # Mapa de by-id para Linux
        by_id_map = {}
        if system_os == "Linux":
            path = "/dev/serial/by-id/"
            if os.path.exists(path):
                for f in glob.glob(os.path.join(path, "*")):
                    try: by_id_map[os.path.realpath(f)] = f
                    except: pass

        for p in ports:
            device_path = p.device
            if "ttyS" in device_path: continue # Filtro de poluição

            if system_os == "Linux" and device_path in by_id_map:
                stable = by_id_map[device_path]
                display = f"{os.path.basename(stable)} ({p.description})"
                val = stable
            else:
                display = f"{device_path} - {p.description}"
                val = device_path
            port_list.append((val, display))

        # 2. Listar dispositivos USBTMC (Para a Fonte ITech) - APENAS LINUX
        if system_os == "Linux":
            usbtmc_devices = glob.glob("/dev/usbtmc*")
            for dev in usbtmc_devices:
                # USBTMC não tem "description" fácil sem abrir, usamos o nome genérico
                display = f"USBTMC Device ({dev})"
                val = dev
                port_list.append((val, display))
            
        return port_list

    def _create_widgets(self):
        layout = QVBoxLayout()
        
        title = QLabel("Configuração de Hardware")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        group = QGroupBox("Conexões e Velocidade")
        grid_layout = QGridLayout()
        
        # Cabeçalhos da Grid
        grid_layout.addWidget(QLabel("<b>Dispositivo</b>"), 0, 0)
        grid_layout.addWidget(QLabel("<b>Porta Serial</b>"), 0, 1)
        grid_layout.addWidget(QLabel("<b>Baud Rate</b>"), 0, 2)
        
        # --- Linha 1: Arduino ---
        grid_layout.addWidget(QLabel("Arduino (Forno):"), 1, 0)
        self.arduino_combo = self._create_port_combo()
        grid_layout.addWidget(self.arduino_combo, 1, 1)
        
        self.arduino_baud = self._create_baud_combo()
        grid_layout.addWidget(self.arduino_baud, 1, 2)

        # --- Linha 2: PSU ---
        grid_layout.addWidget(QLabel("Fonte (PSU):"), 2, 0)
        self.psu_combo = self._create_port_combo()
        grid_layout.addWidget(self.psu_combo, 2, 1)
        
        self.psu_baud = self._create_baud_combo()
        grid_layout.addWidget(self.psu_baud, 2, 2)

        # --- Linha 3: DUT ---
        grid_layout.addWidget(QLabel("DUT (FPGA):"), 3, 0)
        self.dut_combo = self._create_port_combo()
        grid_layout.addWidget(self.dut_combo, 3, 1)
        
        self.dut_baud = self._create_baud_combo()
        grid_layout.addWidget(self.dut_baud, 3, 2)
        
        # Ajusta colunas para ficar bonito
        grid_layout.setColumnStretch(1, 2) # Coluna da porta estica mais
        group.setLayout(grid_layout)
        layout.addWidget(group)
        
        # Botões
        self.save_button = QPushButton("Salvar e Iniciar")
        self.save_button.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; padding: 8px;")
        self.save_button.clicked.connect(self.on_save)
        
        self.cancel_button = QPushButton("Sair")
        self.cancel_button.clicked.connect(self.reject)
        
        layout.addWidget(self.save_button)
        layout.addWidget(self.cancel_button)
        self.setLayout(layout)

    def _create_port_combo(self):
        cb = QComboBox()
        for val, disp in self.available_ports:
            cb.addItem(disp, val)
        return cb

    def _create_baud_combo(self):
        """Cria uma combobox com baud rates comuns editável."""
        cb = QComboBox()
        cb.setEditable(True) # Permite digitar valor customizado
        rates = [9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600]
        for r in rates:
            cb.addItem(str(r))
        return cb

    def _load_current_config(self):
        # Carrega Portas
        self._set_combo_data(self.arduino_combo, config.ARDUINO_PORT)
        self._set_combo_data(self.psu_combo, config.PSU_PORT)
        self._set_combo_data(self.dut_combo, config.DUT_PORT)
        
        # Carrega Bauds
        self.arduino_baud.setCurrentText(str(config.ARDUINO_BAUD))
        self.psu_baud.setCurrentText(str(config.PSU_BAUD))
        self.dut_baud.setCurrentText(str(config.DUT_BAUD))

    def _set_combo_data(self, combo, value):
        idx = combo.findData(value)
        if idx >= 0: combo.setCurrentIndex(idx)

    def on_save(self):
        # Coleta Dados
        ap, pp, dp = self.arduino_combo.currentData(), self.psu_combo.currentData(), self.dut_combo.currentData()
        ab = self.arduino_baud.currentText()
        pb = self.psu_baud.currentText()
        db = self.dut_baud.currentText()

        if not ap or not pp or not dp:
             if QMessageBox.question(self, "Aviso", "Dispositivos não selecionados. Continuar?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.No:
                 return

        # Salva tudo (Portas + Bauds)
        if config.save_config(ap, pp, dp, ab, pb, db):
            self.accept()
        else:
            QMessageBox.critical(self, "Erro", "Falha ao salvar configurações.")