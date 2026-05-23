"""
Hardware configuration dialog shown at app startup.

DUT (required): Nexys4 DDR FPGA — ttyUSB higher port @ 9600
Arduino (optional): oven PID controller — ttyACM
PSU (required): Agilent E3634A — RS-232/ttyUSB @ 9600
"""
import serial.tools.list_ports
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QComboBox, QDialog, QDoubleSpinBox, QFormLayout, QFrame,
    QGridLayout, QGroupBox, QHBoxLayout, QLabel, QPushButton, QVBoxLayout,
)

import config


class SetupDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Configuração de Hardware — Corner Sweep")
        self.setMinimumWidth(520)
        self.setModal(True)

        all_ports = sorted(p.device for p in serial.tools.list_ports.comports())
        self._usb  = [p for p in all_ports if "ttyUSB" in p or "COM" in p]
        self._acm  = [p for p in all_ports if "ttyACM" in p]
        self._all  = all_ports

        self._build_ui()
        self._load()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(28, 24, 28, 22)

        title = QLabel("Configuração de Hardware")
        title.setAlignment(Qt.AlignCenter)
        f = QFont(); f.setPointSize(13); f.setBold(True)
        title.setFont(f)
        layout.addWidget(title)

        sub = QLabel("Corner Sweep — Caracterização de Falha por Tensão")
        sub.setAlignment(Qt.AlignCenter)
        layout.addWidget(sub)

        layout.addWidget(_sep())

        # DUT (required)
        grp_dut = QGroupBox("DUT — FPGA Nexys4 DDR  (obrigatório)")
        g = QGridLayout(); g.setColumnStretch(1, 1)
        g.addWidget(QLabel("Porta Serial:"), 0, 0)
        self.cmb_dut = _cb(self._all)
        g.addWidget(self.cmb_dut, 0, 1)
        g.addWidget(QLabel("Baud Rate:"), 1, 0)
        self.cmb_dut_baud = _baud("9600")
        g.addWidget(self.cmb_dut_baud, 1, 1)
        note = QLabel("Usar a porta ttyUSB de número MAIOR em cada Nexys4.")
        note.setStyleSheet("font-size: 10px; color: #6c7086;")
        g.addWidget(note, 2, 0, 1, 2)
        grp_dut.setLayout(g)
        layout.addWidget(grp_dut)

        # PSU (required for corner sweep)
        grp_psu = QGroupBox("PSU — Agilent E3634A  (obrigatório, RS-232)")
        g2 = QGridLayout(); g2.setColumnStretch(1, 1)
        g2.addWidget(QLabel("Porta Serial:"), 0, 0)
        self.cmb_psu = _cb(self._usb)
        g2.addWidget(self.cmb_psu, 0, 1)
        g2.addWidget(QLabel("Baud Rate:"), 1, 0)
        self.cmb_psu_baud = _baud("9600")
        g2.addWidget(self.cmb_psu_baud, 1, 1)
        grp_psu.setLayout(g2)
        layout.addWidget(grp_psu)

        # Arduino (optional)
        self.grp_ard = QGroupBox("Arduino — Controle de Forno  (opcional)")
        self.grp_ard.setCheckable(True)
        self.grp_ard.setChecked(config.ARDUINO_ENABLED)
        g3 = QGridLayout(); g3.setColumnStretch(1, 1)
        g3.addWidget(QLabel("Porta Serial:"), 0, 0)
        self.cmb_ard = _cb(self._acm)
        g3.addWidget(self.cmb_ard, 0, 1)
        g3.addWidget(QLabel("Baud Rate:"), 1, 0)
        self.cmb_ard_baud = _baud("115200")
        g3.addWidget(self.cmb_ard_baud, 1, 1)
        self.grp_ard.setLayout(g3)
        layout.addWidget(self.grp_ard)

        layout.addWidget(_sep())

        # Sweep parameters summary (read-only info)
        info = QLabel(
            f"Corners: {config.CORNERS_V} V  |  "
            f"Passo sweep: {config.SWEEP_STEP_V} V  |  "
            f"V mínimo: {config.SWEEP_MIN_V} V  |  "
            f"Amostras/corner: {config.SAMPLES_PER_CORNER}"
        )
        info.setAlignment(Qt.AlignCenter)
        info.setStyleSheet("font-size: 10px; color: #6c7086;")
        layout.addWidget(info)

        layout.addWidget(_sep())

        btn_row = QHBoxLayout()
        btn_cancel = QPushButton("Sair")
        btn_cancel.clicked.connect(self.reject)
        btn_ok = QPushButton("Salvar e Iniciar →")
        btn_ok.setDefault(True)
        btn_ok.clicked.connect(self._save)
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_ok)
        layout.addLayout(btn_row)

    def _load(self):
        _sel(self.cmb_dut,  config.DUT_PORT)
        self.cmb_dut_baud.setCurrentText(str(config.DUT_BAUD))
        _sel(self.cmb_psu,  config.PSU_PORT)
        self.cmb_psu_baud.setCurrentText(str(config.PSU_BAUD))
        _sel(self.cmb_ard,  config.ARDUINO_PORT)
        self.cmb_ard_baud.setCurrentText(str(config.ARDUINO_BAUD))

    def _save(self):
        ard_on = self.grp_ard.isChecked()
        config.save_config(
            dut_p=self.cmb_dut.currentText(),
            dut_b=self.cmb_dut_baud.currentText(),
            arduino_p=self.cmb_ard.currentText() if ard_on else "",
            arduino_b=self.cmb_ard_baud.currentText(),
            arduino_en=ard_on,
            psu_p=self.cmb_psu.currentText(),
            psu_b=self.cmb_psu_baud.currentText(),
            psu_en=True,  # PSU is always required for this app
        )
        self.accept()


def _cb(ports):
    cb = QComboBox()
    cb.setEditable(False)
    cb.addItems(ports if ports else ["(nenhuma porta detectada)"])
    return cb


def _baud(default="115200"):
    cb = QComboBox()
    cb.setEditable(True)
    for r in [9600, 19200, 38400, 57600, 115200]:
        cb.addItem(str(r))
    cb.setCurrentText(default)
    return cb


def _sel(combo, value):
    idx = combo.findText(value)
    if idx >= 0:
        combo.setCurrentIndex(idx)


def _sep():
    f = QFrame()
    f.setFrameShape(QFrame.HLine)
    return f
