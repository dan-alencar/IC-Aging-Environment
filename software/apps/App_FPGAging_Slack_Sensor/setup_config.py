import serial.tools.list_ports
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QComboBox, QPushButton, QLabel, QGroupBox, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import config

_STYLE = """
QDialog {
    background-color: #1e1e2e;
    color: #cdd6f4;
}
QGroupBox {
    font-weight: bold;
    border: 1px solid #313244;
    border-radius: 8px;
    margin-top: 12px;
    padding: 14px 10px 10px 10px;
    background-color: #181825;
    color: #89b4fa;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
}
QGroupBox::indicator {
    width: 16px;
    height: 16px;
    border: 1.5px solid #585b70;
    border-radius: 3px;
    background-color: #313244;
    margin-right: 4px;
}
QGroupBox::indicator:checked {
    background-color: #89b4fa;
    border-color: #89b4fa;
}
QLabel { color: #a6adc8; }
QLabel#lbl_title { color: #cdd6f4; }
QLabel#lbl_sub   { color: #6c7086; }
QComboBox {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 4px;
    padding: 5px 10px;
    color: #cdd6f4;
    min-width: 180px;
}
QComboBox:focus { border-color: #89b4fa; }
QComboBox:disabled { color: #585b70; background-color: #181825; }
QComboBox::drop-down { border: none; width: 18px; }
QComboBox QAbstractItemView {
    background-color: #313244;
    color: #cdd6f4;
    selection-background-color: #45475a;
    border: 1px solid #45475a;
}
QPushButton {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 8px 20px;
    color: #cdd6f4;
    font-weight: bold;
}
QPushButton:hover { background-color: #45475a; }
QPushButton#btn_start {
    background-color: #89b4fa;
    color: #1e1e2e;
    border: none;
}
QPushButton#btn_start:hover { background-color: #b4befe; }
QFrame { color: #313244; }
"""


class SetupDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FPGAging — Configuração")
        self.setMinimumWidth(460)
        self.setModal(True)
        self.available_ports = sorted([p.device for p in serial.tools.list_ports.comports()])
        self._build_ui()
        self.setStyleSheet(_STYLE)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(28, 24, 28, 22)

        # Header
        lbl_title = QLabel("Configuração de Hardware")
        lbl_title.setObjectName("lbl_title")
        lbl_title.setAlignment(Qt.AlignCenter)
        f = QFont()
        f.setPointSize(13)
        f.setBold(True)
        lbl_title.setFont(f)
        layout.addWidget(lbl_title)

        lbl_sub = QLabel("Selecione as portas seriais do sistema")
        lbl_sub.setObjectName("lbl_sub")
        lbl_sub.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_sub)

        layout.addWidget(_separator())

        # ESP32 (required)
        grp_esp = QGroupBox("FPGA Bridge — ESP32  (obrigatório)")
        grid_esp = QGridLayout()
        grid_esp.setColumnStretch(1, 1)
        grid_esp.addWidget(QLabel("Porta Serial:"), 0, 0)
        self.cmb_esp = _port_combo(self.available_ports)
        grid_esp.addWidget(self.cmb_esp, 0, 1)
        grp_esp.setLayout(grid_esp)
        layout.addWidget(grp_esp)

        # Arduino (optional, toggled by QGroupBox checkbox)
        self.grp_ard = QGroupBox("Controle de Forno — Arduino  (opcional)")
        self.grp_ard.setCheckable(True)
        self.grp_ard.setChecked(config.ARDUINO_ENABLED)
        grid_ard = QGridLayout()
        grid_ard.setColumnStretch(1, 1)
        grid_ard.addWidget(QLabel("Porta Serial:"), 0, 0)
        self.cmb_ard = _port_combo(self.available_ports)
        grid_ard.addWidget(self.cmb_ard, 0, 1)
        self.grp_ard.setLayout(grid_ard)
        layout.addWidget(self.grp_ard)

        layout.addWidget(_separator())

        # Buttons
        btn_row = QHBoxLayout()
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setObjectName("btn_cancel")
        btn_cancel.clicked.connect(self.reject)
        btn_start = QPushButton("Iniciar Aplicação →")
        btn_start.setObjectName("btn_start")
        btn_start.setDefault(True)
        btn_start.clicked.connect(self._save)
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_start)
        layout.addLayout(btn_row)

        # Restore saved selections
        _select(self.cmb_esp, config.ESP32_PORT)
        _select(self.cmb_ard, config.ARDUINO_PORT)

    def _save(self):
        ard_on = self.grp_ard.isChecked()
        config.save_config(
            esp_port=self.cmb_esp.currentText(),
            ard_port=self.cmb_ard.currentText() if ard_on else "",
            ard_enabled=ard_on,
        )
        self.accept()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _port_combo(ports):
    cb = QComboBox()
    cb.addItems(ports if ports else ["(nenhuma porta detectada)"])
    return cb


def _select(combo, value):
    idx = combo.findText(value)
    if idx >= 0:
        combo.setCurrentIndex(idx)


def _separator():
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    return line
