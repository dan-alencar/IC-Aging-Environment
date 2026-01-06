import sys
import serial.tools.list_ports
from PySide6.QtWidgets import QDialog, QVBoxLayout, QGridLayout, QComboBox, QPushButton, QLabel, QGroupBox
import config

class SetupDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Configuração de Hardware")
        self.setGeometry(200, 200, 400, 200)
        self.available_ports = sorted([p.device for p in serial.tools.list_ports.comports()])
        self._ui()

    def _ui(self):
        layout = QVBoxLayout()
        grid = QGridLayout()
        
        grid.addWidget(QLabel("Arduino (Forno):"), 0, 0)
        self.cmb_ard = QComboBox(); self.cmb_ard.addItems(self.available_ports)
        grid.addWidget(self.cmb_ard, 0, 1)

        grid.addWidget(QLabel("ESP32 (Ponte):"), 1, 0)
        self.cmb_esp = QComboBox(); self.cmb_esp.addItems(self.available_ports)
        grid.addWidget(self.cmb_esp, 1, 1)

        grp = QGroupBox("Portas COM"); grp.setLayout(grid)
        layout.addWidget(grp)
        
        btn = QPushButton("Iniciar"); btn.clicked.connect(self.save)
        layout.addWidget(btn)
        self.setLayout(layout)
        
        # Load Defaults
        idx = self.cmb_ard.findText(config.ARDUINO_PORT)
        if idx >= 0: self.cmb_ard.setCurrentIndex(idx)
        idx = self.cmb_esp.findText(config.ESP32_PORT)
        if idx >= 0: self.cmb_esp.setCurrentIndex(idx)

    def save(self):
        config.save_config(self.cmb_ard.currentText(), self.cmb_esp.currentText())
        self.accept()