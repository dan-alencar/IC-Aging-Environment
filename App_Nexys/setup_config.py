import platform
import serial.tools.list_ports
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QComboBox,
    QPushButton, QLabel, QGroupBox, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import config

try:
    import pyvisa as visa
    _VISA_AVAILABLE = True
except ImportError:
    _VISA_AVAILABLE = False


class SetupDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Configuração do Sistema")
        self.setMinimumWidth(500)
        self.setModal(True)

        self.serial_ports = sorted([p.device for p in serial.tools.list_ports.comports()])
        self.visa_resources = self._list_visa_resources()

        self._build_ui()
        self._load_current_config()

    def _list_visa_resources(self):
        if not _VISA_AVAILABLE:
            return []
        try:
            rm = visa.ResourceManager('@py')
            resources = [r for r in rm.list_resources() if r.startswith("USB")]
            rm.close()
            return resources
        except Exception as e:
            print(f"AVISO: Falha ao listar VISA: {e}")
            return []

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(28, 24, 28, 22)

        lbl_title = QLabel("Configuração de Hardware")
        lbl_title.setAlignment(Qt.AlignCenter)
        f = QFont()
        f.setPointSize(13)
        f.setBold(True)
        lbl_title.setFont(f)
        layout.addWidget(lbl_title)

        lbl_sub = QLabel("Selecione as portas seriais do sistema")
        lbl_sub.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_sub)

        layout.addWidget(_separator())

        # DUT (required)
        grp_dut = QGroupBox("DUT — FPGA Nexys4DDR  (obrigatório)")
        grid_dut = QGridLayout()
        grid_dut.setColumnStretch(1, 1)
        grid_dut.addWidget(QLabel("Porta Serial:"), 0, 0)
        self.cmb_dut = _port_combo(self.serial_ports)
        grid_dut.addWidget(self.cmb_dut, 0, 1)
        grid_dut.addWidget(QLabel("Baud Rate:"), 1, 0)
        self.cmb_dut_baud = _baud_combo()
        grid_dut.addWidget(self.cmb_dut_baud, 1, 1)
        grp_dut.setLayout(grid_dut)
        layout.addWidget(grp_dut)

        # Arduino (optional)
        self.grp_ard = QGroupBox("Arduino — Controle de Forno  (opcional)")
        self.grp_ard.setCheckable(True)
        self.grp_ard.setChecked(config.ARDUINO_ENABLED)
        grid_ard = QGridLayout()
        grid_ard.setColumnStretch(1, 1)
        grid_ard.addWidget(QLabel("Porta Serial:"), 0, 0)
        self.cmb_ard = _port_combo(self.serial_ports)
        grid_ard.addWidget(self.cmb_ard, 0, 1)
        grid_ard.addWidget(QLabel("Baud Rate:"), 1, 0)
        self.cmb_ard_baud = _baud_combo()
        grid_ard.addWidget(self.cmb_ard_baud, 1, 1)
        self.grp_ard.setLayout(grid_ard)
        layout.addWidget(self.grp_ard)

        # PSU (optional)
        psu_ports = self.visa_resources + self.serial_ports
        self.grp_psu = QGroupBox("Fonte PSU  (opcional)")
        self.grp_psu.setCheckable(True)
        self.grp_psu.setChecked(config.PSU_ENABLED)
        grid_psu = QGridLayout()
        grid_psu.setColumnStretch(1, 1)
        grid_psu.addWidget(QLabel("Porta / VISA:"), 0, 0)
        self.cmb_psu = _port_combo(psu_ports)
        grid_psu.addWidget(self.cmb_psu, 0, 1)
        grid_psu.addWidget(QLabel("Baud Rate:"), 1, 0)
        self.cmb_psu_baud = _baud_combo()
        grid_psu.addWidget(self.cmb_psu_baud, 1, 1)
        self.grp_psu.setLayout(grid_psu)
        layout.addWidget(self.grp_psu)

        layout.addWidget(_separator())

        btn_row = QHBoxLayout()
        btn_cancel = QPushButton("Sair")
        btn_cancel.clicked.connect(self.reject)
        btn_start = QPushButton("Salvar e Iniciar →")
        btn_start.setDefault(True)
        btn_start.clicked.connect(self._save)
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_start)
        layout.addLayout(btn_row)

    def _load_current_config(self):
        _select(self.cmb_dut, config.DUT_PORT)
        self.cmb_dut_baud.setCurrentText(str(config.DUT_BAUD))

        _select(self.cmb_ard, config.ARDUINO_PORT)
        self.cmb_ard_baud.setCurrentText(str(config.ARDUINO_BAUD))

        _select(self.cmb_psu, config.PSU_PORT)
        self.cmb_psu_baud.setCurrentText(str(config.PSU_BAUD))

    def _save(self):
        ard_on = self.grp_ard.isChecked()
        psu_on = self.grp_psu.isChecked()

        config.save_config(
            dut_p=self.cmb_dut.currentText(),
            dut_b=self.cmb_dut_baud.currentText(),
            arduino_p=self.cmb_ard.currentText() if ard_on else "",
            arduino_b=self.cmb_ard_baud.currentText(),
            arduino_enabled=ard_on,
            psu_p=self.cmb_psu.currentText() if psu_on else "",
            psu_b=self.cmb_psu_baud.currentText(),
            psu_enabled=psu_on,
        )
        self.accept()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _port_combo(ports):
    cb = QComboBox()
    cb.setEditable(False)
    cb.addItems(ports if ports else ["(nenhuma porta detectada)"])
    return cb


def _baud_combo():
    cb = QComboBox()
    cb.setEditable(True)
    for r in [9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600]:
        cb.addItem(str(r))
    cb.setCurrentText("115200")
    return cb


def _select(combo, value):
    idx = combo.findText(value)
    if idx >= 0:
        combo.setCurrentIndex(idx)


def _separator():
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    return line
