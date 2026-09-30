import serial.tools.list_ports
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QComboBox,
    QPushButton, QLabel, QGroupBox, QFrame, QDoubleSpinBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import config


class SetupDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Configuração do Sistema")
        self.setMinimumWidth(500)
        self.setModal(True)

        all_ports = sorted([p.device for p in serial.tools.list_ports.comports()])
        self.serial_ports = all_ports
        self.acm_ports = [p for p in all_ports if "ttyACM" in p]

        self._build_ui()
        self._load_current_config()

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
        self.cmb_dut_baud = _baud_combo(default="9600")
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
        self.cmb_ard = _port_combo(self.acm_ports)
        grid_ard.addWidget(self.cmb_ard, 0, 1)
        grid_ard.addWidget(QLabel("Baud Rate:"), 1, 0)
        self.cmb_ard_baud = _baud_combo(default="115200")
        grid_ard.addWidget(self.cmb_ard_baud, 1, 1)
        self.grp_ard.setLayout(grid_ard)
        layout.addWidget(self.grp_ard)

        # PSU (optional) — ITECH IT6502D via USB-TMC (PyVISA)
        self.grp_psu = QGroupBox("PSU — ITECH IT6502D  (opcional, USB-TMC/VISA)")
        self.grp_psu.setCheckable(True)
        self.grp_psu.setChecked(config.PSU_ENABLED)
        grid_psu = QGridLayout()
        grid_psu.setColumnStretch(1, 1)
        grid_psu.addWidget(QLabel("Recurso VISA:"), 0, 0)
        self.cmb_psu = _visa_combo(current=config.PSU_PORT)
        grid_psu.addWidget(self.cmb_psu, 0, 1)
        grid_psu.addWidget(QLabel("VCCINT Setpoint (V):"), 1, 0)
        self.spn_vccint = _vccint_spinner()
        grid_psu.addWidget(self.spn_vccint, 1, 1)
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
        self.spn_vccint.setValue(config.VCCINT_SETPOINT_V)

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
            psu_enabled=psu_on,
            vccint_setpoint=self.spn_vccint.value(),
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


def _visa_combo(current=""):
    """Combo box listing USB-TMC VISA resources (IT6502D connects as USB::...).
    Always editable so the user can paste a resource string manually."""
    try:
        import pyvisa as visa
        rm = visa.ResourceManager("@py")
        resources = [r for r in rm.list_resources() if r.startswith("USB")]
        rm.close()
    except Exception:
        resources = []

    cb = QComboBox()
    cb.setEditable(True)

    # If we have a saved valid USB resource, make sure it's in the list
    items = list(resources)
    if current and current.startswith("USB") and current not in items:
        items.insert(0, current)

    if items:
        cb.addItems(items)
    else:
        cb.addItem("(nenhum recurso USB-TMC detectado)")

    if current:
        _select(cb, current)

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
