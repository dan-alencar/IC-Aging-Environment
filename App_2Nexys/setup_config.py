"""
App_2Nexys — Hardware setup dialog.

DUT-0, DUT-1, and PSU-1 serial ports are auto-detected from fixed USB device
IDs (see config.USB_ID_*) and displayed as read-only labels — no manual
port selection needed for those devices.
PSU-0 (IT6502D) still requires a VISA resource selection.
Arduino requires a ttyACM* port selection.
"""
import platform
import serial.tools.list_ports
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QComboBox,
    QPushButton, QLabel, QGroupBox, QFrame, QDoubleSpinBox
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
        self.setWindowTitle("Configuração do Sistema — App 2-Nexys")
        self.setMinimumWidth(560)
        self.setModal(True)

        # Separate serial ports from VISA resources
        all_ports = sorted([p.device for p in serial.tools.list_ports.comports()])
        self.usb_ports = [p for p in all_ports if "ttyUSB" in p or "COM" in p]
        self.acm_ports = [p for p in all_ports if "ttyACM" in p]
        self.visa_resources = self._list_visa_resources()

        self._build_ui()
        self._load_current_config()

    def _list_visa_resources(self):
        if not _VISA_AVAILABLE:
            return []
        try:
            rm = visa.ResourceManager("@py")
            resources = [r for r in rm.list_resources() if r.startswith("USB")]
            rm.close()
            return resources
        except Exception as e:
            print(f"AVISO: Falha ao listar VISA: {e}")
            return []

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(28, 24, 28, 22)

        title_lbl = QLabel("Configuração de Hardware — 2 DUTs")
        title_lbl.setAlignment(Qt.AlignCenter)
        f = QFont()
        f.setPointSize(13)
        f.setBold(True)
        title_lbl.setFont(f)
        layout.addWidget(title_lbl)

        note = QLabel(
            "Portas DUT e PSU-1 são detectadas automaticamente pelo ID USB. "
            "Conecte os dispositivos antes de abrir esta janela."
        )
        note.setWordWrap(True)
        note.setAlignment(Qt.AlignCenter)
        layout.addWidget(note)

        layout.addWidget(_separator())

        # --- DUT 0 (port auto-detected from USB ID) ---
        grp_dut0 = QGroupBox("DUT-0 — Nexys4 DDR  (obrigatório, porta fixa por ID)")
        grid0 = QGridLayout()
        grid0.setColumnStretch(1, 1)
        grid0.addWidget(QLabel("Porta detectada:"), 0, 0)
        self.lbl_dut0_port = QLabel(config.DUT_0_PORT or "(não encontrado)")
        self.lbl_dut0_port.setStyleSheet("color: #a6e3a1; font-family: monospace;")
        grid0.addWidget(self.lbl_dut0_port, 0, 1)
        grid0.addWidget(QLabel("Baud Rate:"), 1, 0)
        self.cmb_dut0_baud = _baud_combo(default="9600")
        grid0.addWidget(self.cmb_dut0_baud, 1, 1)
        grp_dut0.setLayout(grid0)
        layout.addWidget(grp_dut0)

        # --- DUT 1 (port auto-detected from USB ID) ---
        grp_dut1 = QGroupBox("DUT-1 — Nexys4 DDR  (obrigatório, porta fixa por ID)")
        grid1 = QGridLayout()
        grid1.setColumnStretch(1, 1)
        grid1.addWidget(QLabel("Porta detectada:"), 0, 0)
        self.lbl_dut1_port = QLabel(config.DUT_1_PORT or "(não encontrado)")
        self.lbl_dut1_port.setStyleSheet("color: #a6e3a1; font-family: monospace;")
        grid1.addWidget(self.lbl_dut1_port, 0, 1)
        grid1.addWidget(QLabel("Baud Rate:"), 1, 0)
        self.cmb_dut1_baud = _baud_combo(default="9600")
        grid1.addWidget(self.cmb_dut1_baud, 1, 1)
        grp_dut1.setLayout(grid1)
        layout.addWidget(grp_dut1)

        layout.addWidget(_separator())

        # --- PSU 0 (IT6502D) — USB-TMC VISA ---
        self.grp_psu0 = QGroupBox("PSU-0 — IT6502D  (opcional, USB VISA)")
        self.grp_psu0.setCheckable(True)
        self.grp_psu0.setChecked(config.PSU_0_ENABLED)
        grid_p0 = QGridLayout()
        grid_p0.setColumnStretch(1, 1)
        grid_p0.addWidget(QLabel("VISA Resource:"), 0, 0)
        self.cmb_psu0 = _port_combo(self.visa_resources)
        grid_p0.addWidget(self.cmb_psu0, 0, 1)
        grid_p0.addWidget(QLabel("VCCINT Setpoint (V):"), 1, 0)
        self.spn_vccint0 = _vccint_spinner()
        grid_p0.addWidget(self.spn_vccint0, 1, 1)
        self.grp_psu0.setLayout(grid_p0)
        layout.addWidget(self.grp_psu0)

        # --- PSU 1 (E3634A) — RS-232 via Prolific USB-Serial, port fixed by USB ID ---
        self.grp_psu1 = QGroupBox("PSU-1 — Agilent E3634A  (opcional, porta fixa por ID)")
        self.grp_psu1.setCheckable(True)
        self.grp_psu1.setChecked(config.PSU_1_ENABLED)
        grid_p1 = QGridLayout()
        grid_p1.setColumnStretch(1, 1)
        grid_p1.addWidget(QLabel("Porta detectada:"), 0, 0)
        self.lbl_psu1_port = QLabel(config.PSU_1_PORT or "(não encontrado)")
        self.lbl_psu1_port.setStyleSheet("color: #a6e3a1; font-family: monospace;")
        grid_p1.addWidget(self.lbl_psu1_port, 0, 1)
        grid_p1.addWidget(QLabel("Baud Rate:"), 1, 0)
        self.cmb_psu1_baud = _baud_combo(default="9600")
        grid_p1.addWidget(self.cmb_psu1_baud, 1, 1)
        grid_p1.addWidget(QLabel("VCCINT Setpoint (V):"), 2, 0)
        self.spn_vccint1 = _vccint_spinner()
        grid_p1.addWidget(self.spn_vccint1, 2, 1)
        self.grp_psu1.setLayout(grid_p1)
        layout.addWidget(self.grp_psu1)

        layout.addWidget(_separator())

        # --- Arduino (optional, shared oven) ---
        self.grp_ard = QGroupBox("Arduino — Controle de Forno  (opcional, compartilhado)")
        self.grp_ard.setCheckable(True)
        self.grp_ard.setChecked(config.ARDUINO_ENABLED)
        grid_a = QGridLayout()
        grid_a.setColumnStretch(1, 1)
        grid_a.addWidget(QLabel("Porta Serial:"), 0, 0)
        self.cmb_ard = _port_combo(self.acm_ports)
        grid_a.addWidget(self.cmb_ard, 0, 1)
        grid_a.addWidget(QLabel("Baud Rate:"), 1, 0)
        self.cmb_ard_baud = _baud_combo(default="115200")
        grid_a.addWidget(self.cmb_ard_baud, 1, 1)
        self.grp_ard.setLayout(grid_a)
        layout.addWidget(self.grp_ard)

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
        self.lbl_dut0_port.setText(config.DUT_0_PORT or "(não encontrado)")
        self.cmb_dut0_baud.setCurrentText(str(config.DUT_0_BAUD))
        self.lbl_dut1_port.setText(config.DUT_1_PORT or "(não encontrado)")
        self.cmb_dut1_baud.setCurrentText(str(config.DUT_1_BAUD))

        _select(self.cmb_psu0, config.PSU_0_PORT)
        self.spn_vccint0.setValue(config.VCCINT_SETPOINT_0_V)
        self.lbl_psu1_port.setText(config.PSU_1_PORT or "(não encontrado)")
        self.cmb_psu1_baud.setCurrentText(str(config.PSU_1_BAUD))
        self.spn_vccint1.setValue(config.VCCINT_SETPOINT_1_V)

        _select(self.cmb_ard, config.ARDUINO_PORT)
        self.cmb_ard_baud.setCurrentText(str(config.ARDUINO_BAUD))

    def _save(self):
        psu0_on = self.grp_psu0.isChecked()
        psu1_on = self.grp_psu1.isChecked()
        ard_on = self.grp_ard.isChecked()

        config.save_config(
            dut0_p=config.DUT_0_PORT,
            dut0_b=int(self.cmb_dut0_baud.currentText()),
            dut1_p=config.DUT_1_PORT,
            dut1_b=int(self.cmb_dut1_baud.currentText()),
            psu0_p=self.cmb_psu0.currentText() if psu0_on else "",
            psu0_b=9600,
            psu0_enabled=psu0_on,
            psu1_p=config.PSU_1_PORT if psu1_on else "",
            psu1_b=int(self.cmb_psu1_baud.currentText()),
            psu1_enabled=psu1_on,
            arduino_p=self.cmb_ard.currentText() if ard_on else "",
            arduino_b=int(self.cmb_ard_baud.currentText()),
            arduino_enabled=ard_on,
            vccint_sp0=self.spn_vccint0.value(),
            vccint_sp1=self.spn_vccint1.value(),
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


def _baud_combo(default="115200"):
    cb = QComboBox()
    cb.setEditable(True)
    for r in [9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600]:
        cb.addItem(str(r))
    cb.setCurrentText(default)
    return cb


def _vccint_spinner():
    sp = QDoubleSpinBox()
    sp.setRange(0.0, 1.5)
    sp.setSingleStep(0.05)
    sp.setDecimals(3)
    sp.setValue(1.0)
    sp.setSuffix(" V")
    return sp


def _select(combo, value):
    idx = combo.findText(value)
    if idx >= 0:
        combo.setCurrentIndex(idx)


def _separator():
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    return line
