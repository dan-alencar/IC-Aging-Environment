#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" 
PCB Serial Controller
Dark-themed GUI to send/receive messages to a PCB over a USB STLink (virtual COM port).
Dependencies: PySide6, pyserial
CRC on TX: CRC-16/Modbus (poly 0xA001, init 0xFFFF, refin/refout yes by algorithm, xorout 0x0000)

Protocolo novo:
- Byte de controle: Direction (bit7) | Error (enums) | Function (enums)
- Atributos: iguais ao protocolo anterior (página ASCII, m+len+msg, v "x.xx")
- CRC-16/Modbus: 2 bytes binários (configurável endianness via CRC_ENDIAN)
"""

import os
import sys
import threading
import serial
import serial.tools.list_ports as list_ports

from PySide6.QtCore import Qt, QThread, Signal, Slot, QDateTime, QTimer
from PySide6.QtGui import QTextCursor, QFont, QIntValidator
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QGroupBox, QLabel, QPushButton, QPlainTextEdit, QLineEdit, QComboBox,
    QCheckBox, QMessageBox, QSizePolicy, QSplitter
)

# ---------------------- Enums / Constantes do protocolo ----------------------
# Direction
STM_MASTER  = 0x80
STM_SLAVE   = 0x00

# Cabeçalhos de Roteamento da FPGA
HEADER_CROC = b'\x10'  # Destino: Softcore RISC-V
HEADER_STM  = b'\x20'  # Destino: Microcontrolador STM32

# Errors (usar exatamente os valores dos seus enums em C)
NO_ERROR    = 0x00
ERR_TIMEOUT = 0x10
ERR_CRC     = 0x20
ERR_LEN     = 0x30
ERROR_MASK  = 0x70

# Functions
FUNC_UNK = 0x00
FUNC_P   = 0x01
FUNC_M   = 0x02
FUNC_V   = 0x03

# Texto para logs
ERR_STR = {
    NO_ERROR:    "NONE",
    ERR_TIMEOUT: "TIMEOUT",
    ERR_CRC:     "CRC",
    ERR_LEN:     "LEN"
}
FUNC_STR = {
    FUNC_UNK: "UNK",
    FUNC_P:   "P",
    FUNC_M:   "M",
    FUNC_V:   "V"
}

# Endianness dos 2 bytes de CRC no fio: "big" (CRC alto, depois baixo) ou "little" (LSB primeiro)
CRC_ENDIAN = "little"   # troque para "little" se o STM esperar LSB-first (estilo Modbus RTU)
LEN_ENDIAN = "big"

TIMEOUT = 10000
# ---------------------- Serial Thread ----------------------
class SerialThread(QThread):
    data = Signal(bytes)
    info = Signal(str)
    error = Signal(str)
    opened = Signal(str)
    closed = Signal()

    write_bytes = Signal(bytes)
    set_baud = Signal(int)
    set_rts = Signal(bool)
    set_dtr = Signal(bool)

    def __init__(self, port: str, baudrate: int, parity: str = 'N',
                 stopbits: int = 1, bytesize: int = 8,
                 rts: bool = True, dtr: bool = True):
        super().__init__()
        self._port = port
        self._baudrate = baudrate
        self._parity = parity
        self._stopbits = stopbits
        self._bytesize = bytesize
        self._want_rts = rts
        self._want_dtr = dtr

        self._ser: serial.Serial | None = None
        self._running = threading.Event()
        self._running.clear()

        self.write_bytes.connect(self._on_write, Qt.QueuedConnection)
        self.set_baud.connect(self._on_set_baud, Qt.QueuedConnection)
        self.set_rts.connect(self._on_set_rts, Qt.QueuedConnection)
        self.set_dtr.connect(self._on_set_dtr, Qt.QueuedConnection)

    def run(self):
        try:
            self._ser = serial.Serial(
                port=self._port,
                baudrate=self._baudrate,
                bytesize=self._translate_bytesize(self._bytesize),
                parity=self._translate_parity(self._parity),
                stopbits=self._translate_stopbits(self._stopbits),
                timeout=0.05,
                write_timeout=6.0,
                xonxoff=False,
                rtscts=False,
                dsrdtr=False
            )
            try:
                self._ser.setRTS(self._want_rts)
                self._ser.setDTR(self._want_dtr)
            except Exception:
                pass
            try:
                self._ser.reset_input_buffer()
                self._ser.reset_output_buffer()
            except Exception:
                pass
        except Exception as e:
            self.error.emit(f"Falha ao abrir {self._port}: {e}")
            return

        self._running.set()
        self.opened.emit(self._port)
        self.info.emit(f"Porta aberta: {self._port} @ {self._baudrate} bps")

        try:
            while self._running.is_set():
                try:
                    if self._ser and self._ser.in_waiting:
                        chunk = self._ser.read(self._ser.in_waiting)
                        if chunk:
                            self.data.emit(chunk)
                    else:
                        self.msleep(10)
                except Exception as re:
                    self.error.emit(f"Erro de leitura: {re}")
                    break
        finally:
            try:
                if self._ser and self._ser.is_open:
                    self._ser.close()
            except Exception:
                pass
            self.closed.emit()

    def stop(self):
        self._running.clear()

    @Slot(bytes)
    def _on_write(self, payload: bytes):
        try:
            if self._ser and self._ser.is_open:
                self._ser.write(payload)
                self._ser.flush()
            else:
                self.error.emit("Porta serial não está aberta.")
        except Exception as e:
            self.error.emit(f"Erro de escrita: {e}")

    @Slot(int)
    def _on_set_baud(self, baud: int):
        try:
            if self._ser and self._ser.is_open:
                self._ser.baudrate = baud
                self.info.emit(f"Baudrate trocado para {baud}")
        except Exception as e:
            self.error.emit(f"Falha ao trocar baudrate: {e}")

    @Slot(bool)
    def _on_set_rts(self, val: bool):
        try:
            if self._ser and self._ser.is_open:
                self._ser.setRTS(val)
                self.info.emit(f"RTS={'ON' if val else 'OFF'}")
        except Exception as e:
            self.error.emit(f"Falha ao setar RTS: {e}")

    @Slot(bool)
    def _on_set_dtr(self, val: bool):
        try:
            if self._ser and self._ser.is_open:
                self._ser.setDTR(val)
                self.info.emit(f"DTR={'ON' if val else 'OFF'}")
        except Exception as e:
            self.error.emit(f"Falha ao setar DTR: {e}")

    @staticmethod
    def _translate_parity(p: str):
        import serial as _s
        return {
            'N': _s.PARITY_NONE, 'E': _s.PARITY_EVEN, 'O': _s.PARITY_ODD,
            'M': _s.PARITY_MARK, 'S': _s.PARITY_SPACE
        }.get(p.upper(), _s.PARITY_NONE)

    @staticmethod
    def _translate_stopbits(s: int):
        import serial as _s
        return {1: _s.STOPBITS_ONE, 2: _s.STOPBITS_TWO}.get(int(s), _s.STOPBITS_ONE)

    @staticmethod
    def _translate_bytesize(b: int):
        import serial as _s
        return {5: _s.FIVEBITS, 6: _s.SIXBITS, 7: _s.SEVENBITS, 8: _s.EIGHTBITS}.get(int(b), _s.EIGHTBITS)


# ---------------------- Dark Theme ----------------------
def apply_dark_palette(app: QApplication):
    from PySide6.QtGui import QPalette, QColor
    dark = QPalette()
    dark.setColor(QPalette.Window, QColor(30, 31, 34))
    dark.setColor(QPalette.WindowText, QColor(220, 220, 220))
    dark.setColor(QPalette.Base, QColor(22, 23, 26))
    dark.setColor(QPalette.AlternateBase, QColor(35, 36, 39))
    dark.setColor(QPalette.Text, QColor(230, 230, 230))
    dark.setColor(QPalette.Button, QColor(45, 47, 50))
    dark.setColor(QPalette.ButtonText, QColor(230, 230, 230))
    dark.setColor(QPalette.Highlight, QColor(64, 128, 255))
    dark.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
    app.setPalette(dark)
    app.setStyle("Fusion")


# ---------------------- CRC helper ----------------------
def compute_crc16_modbus(data: bytes) -> int:
    """
    CRC-16/Modbus (poly 0xA001), init=0xFFFF, xorout=0x0000.
    Retorna inteiro 0..0xFFFF.
    """
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc & 0xFFFF

def _linux_is_good_serial(p) -> bool:
    """
    Aceita apenas portas USB/ACM reais no Linux.
    Critérios:
      - tem VID/PID (porta USB reconhecida), OU
      - device começa com /dev/ttyUSB ou /dev/ttyACM, OU
      - está em /dev/serial/by-id/
    E precisa ter permissão de R/W.
    """
    dev = (p.device or "")
    if not dev.startswith("/dev/"):
        return False

    # USB de verdade (VID/PID detectados pelo pyserial)
    if getattr(p, "vid", None) is not None or getattr(p, "pid", None) is not None:
        return os.access(dev, os.R_OK | os.W_OK)

    # Heurísticas adicionais
    if dev.startswith("/dev/ttyUSB") or dev.startswith("/dev/ttyACM") or dev.startswith("/dev/serial/by-id/"):
        return os.access(dev, os.R_OK | os.W_OK)

    # Filtra /dev/ttyS* e afins
    return False


def _linux_pretty_device(dev: str) -> str:
    """
    Se existir um symlink estável em /dev/serial/by-id para este device,
    retorna o caminho de /dev/serial/by-id/*; caso contrário, retorna o próprio dev.
    """
    by_id_dir = "/dev/serial/by-id"
    try:
        if os.path.isdir(by_id_dir):
            for name in os.listdir(by_id_dir):
                path = os.path.join(by_id_dir, name)
                try:
                    if os.path.islink(path):
                        target = os.path.realpath(path)
                        if os.path.realpath(dev) == target:
                            return path
                except Exception:
                    pass
    except Exception:
        pass
    return dev

# ---------------------- Main Window ----------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PCB Serial Controller")
        self.setMinimumSize(980, 600)
        self._serial_thread: SerialThread | None = None

        # Buffer de recepção textual (linhas)
        self._rx_buf = ""
        self._last_wire_sent = b""


        # ----- Estado do parser byte-a-byte -----
        self._sm_state = "IDLE"   # IDLE | WAIT_CRC1 | WAIT_CRC2 | SKIP_EOL
        self._sm_ctrl  = None     # byte de controle visto
        self._sm_crc1  = None
        self._sm_crc2  = None
        self._last_was_cr = False # ajuda a não duplicar linhas em CRLF

        # Estado para montar quadro de controle (erro/ok) atravessando múltiplos chunks
        self._pend_type = None         # "err" | "ok" | None
        self._pend_need = 0            # faltam N bytes de CRC (sempre 2)
        self._pend_acc  = bytearray()  # acumula [ctrl, crc1, crc2]

        # UI
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # Connection box
        self.conn_box = self._build_connection_group()
        layout.addWidget(self.conn_box)

        # Quick (mais estreito) + Manual (mais largo)
        mid = QHBoxLayout()
        mid.setSpacing(12)
        self.quick_box = self._build_quick_commands_group()
        self.manual_box = self._build_manual_send_group()
        mid.addWidget(self.quick_box, 1)  # quick menor
        mid.addWidget(self.manual_box, 2) # manual maior
        layout.addLayout(mid, 0)

        # Log area
        splitter = QSplitter(Qt.Horizontal)
        self.log_box = self._build_log_group()
        self.message_log_box = self._build_message_log_group()
        splitter.addWidget(self.log_box)
        splitter.addWidget(self.message_log_box)
        splitter.setChildrenCollapsible(False)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        splitter.setHandleWidth(8)
        layout.addWidget(splitter, 1) 

        # Status bar
        self.status = self.statusBar()
        self._update_status("Pronto.")

         # ---- Timer de resposta a comandos ----
        self._resp_timer = QTimer(self)
        self._resp_timer.setSingleShot(True)
        self._resp_timer.timeout.connect(self._on_response_timeout)
        self._awaiting_response = False
        self._resp_context = ""
        self._await_deadline_ms = 0  # momento (ms) limite para considerar ctrl-candidate

        self.refresh_ports(auto_select_stlink=True)

    # ---------- UI Builders ----------
    def _build_connection_group(self) -> QGroupBox:
        g = QGroupBox("Conexão")
        grid = QGridLayout(g)
        grid.setContentsMargins(10, 12, 10, 10)
        grid.setHorizontalSpacing(12)
        row = 0

        grid.addWidget(QLabel("Porta COM:"), row, 0)
        self.cmb_port = QComboBox()
        self.cmb_port.setMinimumWidth(380)
        grid.addWidget(self.cmb_port, row, 1)

        self.btn_refresh = QPushButton("Atualizar")
        self.btn_refresh.clicked.connect(self.refresh_ports)
        grid.addWidget(self.btn_refresh, row, 2)

        row += 1
        grid.addWidget(QLabel("Baud:"), row, 0)
        self.cmb_baud = QComboBox()
        self.cmb_baud.setEditable(True)
        for b in [9600, 19200, 38400, 57600, 115200, 125000, 230400, 460800, 921600]:
            self.cmb_baud.addItem(str(b))
        self.cmb_baud.setCurrentText("125000")
        grid.addWidget(self.cmb_baud, row, 1)

        self.btn_apply_baud = QPushButton("Aplicar baud")
        self.btn_apply_baud.clicked.connect(self.on_apply_baud)
        grid.addWidget(self.btn_apply_baud, row, 2)

        # --- Linha do formato + Conectar na MESMA linha ---
        row += 1
        grid.addWidget(QLabel("Formato:"), row, 0)
        self.cmb_format = QComboBox()
        self.cmb_format.addItems(["8N1", "8E1", "8O1", "7E1", "8N2"])
        grid.addWidget(self.cmb_format, row, 1)

        self.btn_connect = QPushButton("Conectar")
        self.btn_connect.setCheckable(True)
        self.btn_connect.clicked.connect(self.on_toggle_connect)
        grid.addWidget(self.btn_connect, row, 2)
        # ---------------------------------------------------

        # Linha RTS/DTR
        row += 1
        self.chk_rts = QCheckBox("RTS ON")
        self.chk_rts.setChecked(True)
        grid.addWidget(self.chk_rts, row, 0)

        self.chk_dtr = QCheckBox("DTR ON")
        self.chk_dtr.setChecked(True)
        grid.addWidget(self.chk_dtr, row, 1)

        return g

    def _make_expanding(self, line_edit: QLineEdit, min_width: int = 100):
        sp = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        line_edit.setSizePolicy(sp)
        line_edit.setMinimumWidth(min_width)

    def _build_quick_commands_group(self) -> QGroupBox:
        g = QGroupBox("Comandos Rápidos / Exibição")
        v = QVBoxLayout(g)
        v.setContentsMargins(10, 12, 10, 10)
        v.setSpacing(8)

        # ---------- Controle de página ----------
        page_row = QHBoxLayout()
        self.btn_page_prev = QPushButton("<")
        self.btn_page_prev.setFixedWidth(36)
        self.btn_page_prev.setToolTip("Página anterior")
        self.btn_page_prev.clicked.connect(self.on_click_page_prev)
        page_row.addWidget(self.btn_page_prev)

        self.txt_page = QLineEdit()
        self.txt_page.setAlignment(Qt.AlignCenter)
        self.txt_page.setPlaceholderText("1")
        self.txt_page.setText("1")
        self.txt_page.setValidator(QIntValidator(1, 6, self))
        self.txt_page.setToolTip("Número da página atual (edite e pressione Enter)")
        self.txt_page.editingFinished.connect(self.on_page_text_committed)
        self._make_expanding(self.txt_page, min_width=90)
        page_row.addWidget(self.txt_page, 1)

        self.btn_page_next = QPushButton(">")
        self.btn_page_next.setFixedWidth(36)
        self.btn_page_next.setToolTip("Próxima página")
        self.btn_page_next.clicked.connect(self.on_click_page_next)
        page_row.addWidget(self.btn_page_next)

        v.addLayout(page_row)
        # ---------------------------------------

        # ------- Setar Vcore -------
        vcore_row = QHBoxLayout()
        self.txt_vcore = QLineEdit()
        self.txt_vcore.setPlaceholderText("0.85")
        self.txt_vcore.setAlignment(Qt.AlignCenter)
        self.txt_vcore.setMaxLength(6)
        self._make_expanding(self.txt_vcore, min_width=140)
        vcore_row.addWidget(QLabel("Vcore (V):"))
        vcore_row.addWidget(self.txt_vcore, 1)

        self.btn_set_vcore = QPushButton("Set Vcore")
        self.btn_set_vcore.setFixedWidth(80)
        self.btn_set_vcore.clicked.connect(self.on_click_set_vcore)
        vcore_row.addWidget(self.btn_set_vcore)
        v.addLayout(vcore_row)

        # ------- Step com botões ao redor -------
        step_row = QHBoxLayout()
        self.btn_vcore_dec = QPushButton("−")
        self.btn_vcore_dec.setFixedWidth(36)
        self.btn_vcore_dec.setToolTip("Diminuir Vcore pelo step")
        self.btn_vcore_dec.clicked.connect(self.on_click_vcore_dec)
        step_row.addWidget(self.btn_vcore_dec)

        self.txt_vstep = QLineEdit("0.05")
        self.txt_vstep.setAlignment(Qt.AlignCenter)
        self._make_expanding(self.txt_vstep, min_width=140)
        step_row.addWidget(self.txt_vstep, 1)

        self.btn_vcore_inc = QPushButton("+")
        self.btn_vcore_inc.setFixedWidth(36)
        self.btn_vcore_inc.setToolTip("Aumentar Vcore pelo step")
        self.btn_vcore_inc.clicked.connect(self.on_click_vcore_inc)
        step_row.addWidget(self.btn_vcore_inc)

        v.addLayout(step_row)
        # ---------------------------------------------------------

        clear_row = QHBoxLayout()
        self.btn_clear_log = QPushButton("Limpar log")
        self.btn_clear_log.clicked.connect(self._clear_log)
        clear_row.addWidget(self.btn_clear_log)
        self.btn_clear_message_log = QPushButton("Limpar mensagens")
        self.btn_clear_message_log.clicked.connect(self._clear_message_log)
        clear_row.addWidget(self.btn_clear_message_log)
        v.addLayout(clear_row)

        # ---- HEX/TX details + RESET à direita ----
        opts_row = QHBoxLayout()
        self.chk_hex_view = QCheckBox("Exibir RX em HEX")
        self.chk_hex_view.setChecked(False)
        opts_row.addWidget(self.chk_hex_view)

        self.chk_tx_details = QCheckBox("Detalhes de TX")
        self.chk_tx_details.setChecked(False)
        opts_row.addWidget(self.chk_tx_details)

        opts_row.addStretch(1)  # empurra o Reset para a direita

        self.btn_reset = QPushButton("Reset")
        self.btn_reset.setFixedWidth(80)
        self.btn_reset.setToolTip("Enviar comando de reset (m 5 reset)")
        self.btn_reset.clicked.connect(self.on_click_reset)
        opts_row.addWidget(self.btn_reset)

        v.addLayout(opts_row)

        v.addStretch(1)
        return g

    def _build_manual_send_group(self) -> QGroupBox:
        g = QGroupBox("Enviar Mensagem Manual")
        grid = QGridLayout(g)
        grid.setContentsMargins(10, 12, 10, 10)
        grid.setHorizontalSpacing(8)
        row = 0

        # --- NOVA SEÇÃO: Seletor de Destino ---
        grid.addWidget(QLabel("Destino:"), row, 0)
        self.cmb_target = QComboBox()
        self.cmb_target.addItem("STM32 (Protocolo)", userData=HEADER_STM)
        self.cmb_target.addItem("CROC (Texto Puro)", userData=HEADER_CROC)
        grid.addWidget(self.cmb_target, row, 1, 1, 3)
        row += 1
        # --------------------------------------

        grid.addWidget(QLabel("Mensagem:"), row, 0)
        self.txt_message = QLineEdit()
        self.txt_message.setMaxLength(65535)
        self.txt_message.returnPressed.connect(self.on_click_send_manual)
        grid.addWidget(self.txt_message, row, 1, 1, 3)

        row += 1
        grid.addWidget(QLabel("Terminador:"), row, 0)
        self.cmb_eol = QComboBox()
        self.cmb_eol.addItems(["LF (\\n)", "CR (\\r)", "CRLF (\\r\\n)", "Nenhum"])
        self.cmb_eol.setCurrentIndex(3)  # mantenho o padrão atual; troque para 3 se quiser "Nenhum"
        grid.addWidget(self.cmb_eol, row, 1)

        self.btn_send = QPushButton("Enviar")
        self.btn_send.clicked.connect(self.on_click_send_manual)
        grid.addWidget(self.btn_send, row, 3)

        return g
        
    def _build_log_group(self) -> QGroupBox:
        g = QGroupBox("Log geral")
        v = QVBoxLayout(g)
        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)
        self.log.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.log.setPlaceholderText("Logs de comunicação aparecerão aqui...")
        self.log.setFont(QFont("Consolas", 10))
        v.addWidget(self.log)
        return g

    def _build_message_log_group(self) -> QGroupBox:
        g = QGroupBox("Mensagens recebidas")
        v = QVBoxLayout(g)
        self.m_log = QPlainTextEdit()
        self.m_log.setReadOnly(True)  # <- agora não é editável
        self.m_log.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.m_log.setPlaceholderText("Conteúdo das mensagens recebidas aparecerá aqui...")
        self.m_log.setFont(QFont("Consolas", 10))
        v.addWidget(self.m_log)
        return g
    # ---------- Aux ----------
    def _clear_log(self):
        if hasattr(self, "log") and self.log:
            self.log.clear()

    def _clear_message_log(self):
        if hasattr(self, "log") and self.m_log:
            self.m_log.clear()

    # ---------- Port Discovery ----------
    def refresh_ports(self, auto_select_stlink: bool = False):
        self.cmb_port.clear()

        ports = list_ports.comports()

        # --- FILTRO ESPECÍFICO PARA LINUX ---
        if sys.platform.startswith("linux"):
            ports = [p for p in ports if _linux_is_good_serial(p)]
        # Em outras plataformas, mantemos tudo (Windows/macOS)

        # Ordena por device para uma lista consistente
        ports = sorted(ports, key=lambda p: (p.device or ""))

        # Popular combo priorizando /dev/serial/by-id/* no Linux
        for p in ports:
            dev = p.device or ""
            pretty = _linux_pretty_device(dev) if sys.platform.startswith("linux") else dev
            desc = p.description or ""
            label = f"{pretty} — {desc}".strip(" —")
            self.cmb_port.addItem(label, userData=pretty)

        # Auto-select do STLink (por nome e depois por VID)
        if auto_select_stlink and self.cmb_port.count() > 0:
            chosen_index = -1
            # 1) por texto
            for i in range(self.cmb_port.count()):
                txt = (self.cmb_port.itemText(i) or "").lower()
                if any(k in txt for k in ("stlink", "st-link", "stmicro", "stmicroelectronics", "stm")):
                    chosen_index = i
                    break
            # 2) por VID ST (0x0483), se o objeto original ainda estiver disponível
            if chosen_index < 0:
                for i, portinfo in enumerate(ports):
                    try:
                        if getattr(portinfo, "vid", None) == 0x0483:
                            chosen_index = i
                            break
                    except Exception:
                        pass
            if chosen_index >= 0:
                self.cmb_port.setCurrentIndex(chosen_index)

        if self.cmb_port.count() == 0:
            self.cmb_port.addItem("Nenhuma porta encontrada", userData=None)



    # ---------- Connect / Disconnect ----------
    def parse_format(self, fmt: str):
        try:
            bits = int(fmt[0]); parity = fmt[1].upper(); stops = int(fmt[2])
            return bits, parity, stops
        except Exception:
            return 8, 'N', 1

    @Slot()
    def on_toggle_connect(self):
        if self._serial_thread and self._serial_thread.isRunning():
            self._update_status("Encerrando conexão...")
            self._serial_thread.stop()
            self._serial_thread.wait(1500)
            self._serial_thread = None
            self.btn_connect.setText("Conectar")
            self._update_status("Desconectado.")
            return

        port = self.cmb_port.currentData()
        if not port:
            QMessageBox.warning(self, "Porta inválida", "Selecione uma COM válida.")
            self.btn_connect.setChecked(False)
            return

        try:
            baud = int(self.cmb_baud.currentText().strip())
        except ValueError:
            QMessageBox.warning(self, "Baud inválido", "Informe um baudrate numérico (ex.: 115200).")
            self.btn_connect.setChecked(False)
            return

        bits, parity, stops = self.parse_format(self.cmb_format.currentText())

        th = SerialThread(
            port, baud, parity=parity, stopbits=stops, bytesize=bits,
            rts=self.chk_rts.isChecked(), dtr=self.chk_dtr.isChecked()
        )
        th.data.connect(self.on_serial_data)
        th.info.connect(self.on_serial_info)
        th.error.connect(self.on_serial_error)
        th.opened.connect(self.on_serial_opened)
        th.closed.connect(self.on_serial_closed)

        self._serial_thread = th
        th.start()

    @Slot()
    def on_apply_baud(self):
        if not (self._serial_thread and self._serial_thread.isRunning()):
            self.on_serial_error("Não conectado.")
            return
        try:
            baud = int(self.cmb_baud.currentText().strip())
        except ValueError:
            self.on_serial_error("Baud inválido.")
            return
        self._serial_thread.set_baud.emit(baud)

    # ---------- Helpers de envio ----------
    
    def _start_response_timer(self, context: str, ms: int = TIMEOUT):
        try:
            if self._resp_timer.isActive():
                self._resp_timer.stop()
        except Exception:
            pass
        self._resp_context = context
        self._awaiting_response = True
        # janela “armada”: só aceito cabeçalho no período do timeout
        self._await_deadline_ms = QDateTime.currentMSecsSinceEpoch() + ms
        self._resp_timer.start(ms)

    def _response_received(self):
        if self._resp_timer.isActive():
            self._resp_timer.stop()
        self._awaiting_response = False
        self._resp_context = ""
        self._await_deadline_ms = 0


    @Slot()
    def _on_response_timeout(self):
        """Disparado quando não chegou OK/ERRO no tempo esperado."""
        if not self._awaiting_response:
            return
        self._awaiting_response = False
        ctx = f" ({self._resp_context})" if self._resp_context else ""
        self._append_log(f"[{self._now()}] [ERRO] Sem resposta{ctx} após {TIMEOUT} ms.")
        self._resp_context = ""

        # --------- Helpers do parser byte-a-byte ---------
    def _reset_ctrl_sm(self):
        self._sm_state = "IDLE"
        self._sm_ctrl  = None
        self._sm_crc1  = None
        self._sm_crc2  = None

    def _is_ctrl_candidate(self, b: int) -> bool:
        if not self._awaiting_response:
            return False
        if QDateTime.currentMSecsSinceEpoch() > self._await_deadline_ms:
            return False
        return self._is_error_frame(b) or self._is_ok_frame(b)

    def _accept_ctrl_and_log(self):
        ctrl, c1, c2 = self._sm_ctrl, self._sm_crc1, self._sm_crc2
        if self._crc2_matches(ctrl, c1, c2):
            if self._is_error_frame(ctrl):
                self._log_error_ctrl(ctrl, c1, c2)
            else:
                self._log_ok_ctrl(ctrl, c1, c2)
            # Chegou resposta válida -> cancela timer
            self._response_received()
            self._sm_state = "SKIP_EOL"
        else:
            # CRC inválido: devolve os 3 bytes para o fluxo textual
            self._process_text_byte(ctrl)
            self._process_text_byte(c1)
            self._process_text_byte(c2)
            self._sm_state = "IDLE"
        self._sm_ctrl = self._sm_crc1 = self._sm_crc2 = None



    def _process_text_byte(self, b: int):
        if b == 0x0D:  # CR
            self._last_was_cr = True
            line = self._rx_buf
            self._rx_buf = ""
            if line != "":
                now = self._now()
                # Log geral (respeita opção HEX)
                if self.chk_hex_view.isChecked():
                    hexline = " ".join(f"{ord(c):02X}" for c in line)
                    self._append_log(f"[{now}] [<<] {hexline}")
                else:
                    self._append_log(f"[{now}] [<<] {line}")
                # Log de mensagens (sempre texto puro + hora)
                self._append_message_log(line)
            return

        if b == 0x0A:  # LF
            if self._last_was_cr:
                self._last_was_cr = False
                return
            line = self._rx_buf
            self._rx_buf = ""
            if line != "":
                now = self._now()
                if self.chk_hex_view.isChecked():
                    hexline = " ".join(f"{ord(c):02X}" for c in line)
                    self._append_log(f"[{now}] [<<] {hexline}")
                else:
                    self._append_log(f"[{now}] [<<] {line}")
                self._append_message_log(line)
            return

        # byte normal (acumula)
        self._last_was_cr = False
        try:
            ch = bytes([b]).decode("utf-8")
        except UnicodeDecodeError:
            ch = bytes([b]).decode("latin-1", errors="replace")
        self._rx_buf += ch  


    def selected_eol(self) -> bytes:
        idx = self.cmb_eol.currentIndex()
        if idx == 0:   # LF
            return b"\n"
        elif idx == 1: # CR
            return b"\r"
        elif idx == 2: # CRLF
            return b"\r\n"
        else:
            return b""

    def _crc_bytes(self, payload: bytes) -> bytes:
        crc = compute_crc16_modbus(payload)
        self._last_crc_hex = f"{crc:04X}"
        self._last_crc_bytes = crc.to_bytes(2, CRC_ENDIAN)  # ordem real no fio
        return self._last_crc_bytes

    def _send_frame(self, payload_without_crc: bytes, log_str: str, target: bytes = HEADER_STM):
            if not (self._serial_thread and self._serial_thread.isRunning()):
                self.on_serial_error("Não conectado.")
                return
            
            crc2 = self._crc_bytes(payload_without_crc)
            
            # ALTERAÇÃO: Enviar Header primeiro, esperar um pouco, enviar Payload
            # Isso dá tempo para a FPGA chavear o multiplexador interno
            
            self._serial_thread.write_bytes.emit(target)
            
            import time
            time.sleep(0.005) # Espera 5ms (suficiente para o Router reagir)
            
            wire_payload = payload_without_crc + crc2 + self.selected_eol()
            self._last_wire_sent = target + wire_payload # Apenas para registro interno
            
            dest_str = "STM" if target == HEADER_STM else "CROC"
            self._append_log(f"[{self._now()}] [>> {dest_str}] {log_str} {self._last_crc_hex}")
            
            self._serial_thread.write_bytes.emit(wire_payload)
            
            if target == HEADER_STM:
                self._start_response_timer(log_str, ms=TIMEOUT)



    # ---------- Construtores de comando (novo protocolo) ----------

    def _is_ok_frame(self, b: int) -> bool:
        direction, error, func = self._decode_ctrl(b)
        # ok com erro==0 e função entre 0..3 para reduzir falso-positivo em ASCII
        return (error == NO_ERROR) and (func in (FUNC_UNK, FUNC_P, FUNC_M, FUNC_V))


    def _log_ok_ctrl(self, ctrl: int, crc1: int | None = None, crc2: int | None = None):
        bits = f"{ctrl:08b}"
        now = self._now()
        # SEMPRE mostra uma linha curta de OK
        self._append_log(f"[{now}] [<<] OK   :{bits}")

        # Linha detalhada só se marcado
        if self.chk_tx_details.isChecked():
            direction, _, func = self._decode_ctrl(ctrl)
            dir_str = "MASTER" if direction == STM_MASTER else "SLAVE"
            fn_str  = FUNC_STR.get(func, f"0x{func:02X}")
            extra_crc = ""
            if crc1 is not None and crc2 is not None:
                extra_crc = f", crc=0x{crc1:02X} 0x{crc2:02X}"
            self._append_log(
                f"           └ detalhes: Ok={bits}, dir={dir_str}, func={fn_str}{extra_crc}"
            )

    @staticmethod
    def _make_ctrl(direction: int, error: int, func: int) -> int:
        return (direction & 0x80) | (error & ERROR_MASK) | (func & 0x03)

    def _send_page_command(self, page_val: int):
        page_val = max(1, min(6, page_val))
        self.txt_page.setText(str(page_val))
        ctrl = self._make_ctrl(STM_SLAVE, NO_ERROR, FUNC_P)
        attrs = str(page_val).encode("utf-8")
        payload = bytes([ctrl]) + attrs
        log_str = f"P {page_val}"
        self._send_frame(payload, log_str)
        if self.chk_tx_details.isChecked():
            c1, c2 = self._last_crc_bytes[0], self._last_crc_bytes[1]
            self._append_log(
                f"           └ detalhes: dir=SLAVE, err=NONE, func=P, attrs={page_val}, wire={ctrl:08b} + {page_val} + 0x{c1:02X} 0x{c2:02X}\n"
            )

    def _send_message_command(self, msg: str):
        msg_bytes = msg.encode("utf-8")

        # 2 bytes binários de tamanho (endianness configurável em LEN_ENDIAN)
        if len(msg_bytes) > 0xFFFF:
            QMessageBox.warning(self, "Mensagem muito grande",
                                "A mensagem excede 65535 bytes.")
            return
        size_bin = len(msg_bytes).to_bytes(2, LEN_ENDIAN)

        ctrl = self._make_ctrl(STM_SLAVE, NO_ERROR, FUNC_M)
        payload = bytes([ctrl]) + size_bin + msg_bytes

        # Log “humano”: mostra o tamanho numérico e os bytes do tamanho
        size_hex = " ".join(f"0x{x:02X}" for x in size_bin)
        log_str = f"M len={len(msg_bytes)} ({size_hex}) msg=\"{msg}\""

        self._send_frame(payload, log_str)

        if self.chk_tx_details.isChecked():
            c1, c2 = self._last_crc_bytes[0], self._last_crc_bytes[1]
            self._append_log(
                f"           └ detalhes: dir=SLAVE, err=NONE, func=M, "
                f"len={len(msg_bytes)} ({size_hex}), wire={ctrl:08b} + <len2> + <msg> + 0x{c1:02X} 0x{c2:02X}\n"
            )


    def _send_vcore(self, value: float):
        value_str = f"{value:.2f}"
        ctrl = self._make_ctrl(STM_SLAVE, NO_ERROR, FUNC_V)
        payload = bytes([ctrl]) + value_str.encode("utf-8")
        log_str = f"V {value_str}"
        self._send_frame(payload, log_str)
        if self.chk_tx_details.isChecked():
            c1, c2 = self._last_crc_bytes[0], self._last_crc_bytes[1]
            self._append_log(
                f"           └ detalhes: dir=SLAVE, err=NONE, func=V, attrs={value_str}, wire={ctrl:08b} + {value_str} + 0x{c1:02X} 0x{c2:02X}\n"
            )

    # ---------- Página: handlers ----------
    def _clamp_page(self, val: int) -> int:
        return max(1, min(6, val))

    def set_page_and_send(self, val: int):
        self._send_page_command(val)

    @Slot()
    def on_click_page_prev(self):
        try:
            val = int(self.txt_page.text())
        except ValueError:
            val = 1
        self._send_page_command(val - 1)

    @Slot()
    def on_click_page_next(self):
        try:
            val = int(self.txt_page.text())
        except ValueError:
            val = 1
        self._send_page_command(val + 1)

    @Slot()
    def on_page_text_committed(self):
        txt = self.txt_page.text().strip()
        if txt == "":
            return
        try:
            val = int(txt)
        except ValueError:
            QMessageBox.warning(self, "Página inválida", "Digite um número entre 1 e 6.")
            return
        self._send_page_command(val)

    # ---------- Serial: parsing de ERRO (novo) ----------
    def _decode_ctrl(self, b: int):
        direction = STM_MASTER if (b & 0x80) else STM_SLAVE
        error = b & ERROR_MASK      
        func = b & 0x03
        return direction, error, func


    def _is_error_frame(self, b: int) -> bool:
        direction, error, func = self._decode_ctrl(b)
        return (error in (ERR_TIMEOUT, ERR_CRC, ERR_LEN)) and (func in (FUNC_UNK, FUNC_P, FUNC_M, FUNC_V))


    def _crc2_matches(self, first_byte: int, crc_b1: int, crc_b2: int) -> bool:
        expected = compute_crc16_modbus(bytes([first_byte]))
        got_le = (crc_b1 & 0xFF) | ((crc_b2 & 0xFF) << 8)
        got_be = ((crc_b1 & 0xFF) << 8) | (crc_b2 & 0xFF)
        return expected == got_le or expected == got_be



    def _log_error_ctrl(self, ctrl: int, crc1: int | None = None, crc2: int | None = None):
        direction, error, func = self._decode_ctrl(ctrl)
        bits = f"{ctrl:08b}"
        now = self._now()
        self._append_log(f"[{now}] [<<] Erro :{bits}")
        if self.chk_tx_details.isChecked():
            dir_str = "MASTER" if direction == STM_MASTER else "SLAVE"
            err_str = ERR_STR.get(error, f"0x{error:02X}")
            fn_str  = FUNC_STR.get(func,  f"0x{func:02X}")
            extra_crc = ""
            if crc1 is not None and crc2 is not None:
                extra_crc = f", crc=0x{crc1:02X} 0x{crc2:02X}"
            self._append_log(
                f"           └ detalhes: Erro={bits}, dir={dir_str}, tipo={err_str}, func={fn_str}{extra_crc}"
            )


    # ---------- Serial Callbacks ----------
    @Slot(str)
    def on_serial_opened(self, port_str: str):
        self.btn_connect.setChecked(True)
        self.btn_connect.setText("Desconectar")
        self._append_log(f"[{self._now()}] [INFO] Conectado em {port_str}\n")

    @Slot()
    def on_serial_closed(self):
        self._response_received()
        if self._rx_buf:
            self._append_log(f"[{self._now()}] [<<] {self._rx_buf}")
            self._rx_buf = ""
        self.btn_connect.setChecked(False)
        self.btn_connect.setText("Conectar")
        self._append_log(f"[{self._now()}] [INFO] Conexão encerrada\n")

    @Slot(str)
    def on_serial_info(self, msg: str):
        self._update_status(msg)
        self._append_log(f"[{self._now()}] [INFO] {msg}\n")

    @Slot(str)
    def on_serial_error(self, msg: str):
        self._update_status(msg)
        self._append_log(f"[{self._now()}] [ERRO] {msg}\n")

    @Slot(bytes)
    def on_serial_data(self, data: bytes):
        """
        Parser byte-a-byte com máquina de estados:
        - Detecta quadros de controle: [ctrl][crc1][crc2] (apenas do byte 'ctrl')
        - Valida CRC do ctrl; se ok, loga Erro/OK (OK só aparece se 'Detalhes de TX' ligado)
        - Ignora CR/LF imediatamente após um quadro válido (não vira linha textual)
        - Todo o resto vai para o fluxo textual por linhas, sem inserir linhas vazias extras
        """
        for b in data:
            # Após quadro válido, ignorar CR/LF seguintes
            if self._sm_state == "SKIP_EOL":
                if b in (0x0D, 0x0A):
                    continue
                # Primeiro byte não-EOL: volta ao IDLE e processa como texto/controle
                self._sm_state = "IDLE"

            if self._sm_state == "IDLE":
                if self._is_ctrl_candidate(b):
                    self._sm_ctrl = b
                    self._sm_state = "WAIT_CRC1"
                else:
                    self._process_text_byte(b)
                continue

            if self._sm_state == "WAIT_CRC1":
                self._sm_crc1 = b
                self._sm_state = "WAIT_CRC2"
                continue

            if self._sm_state == "WAIT_CRC2":
                self._sm_crc2 = b
                self._accept_ctrl_and_log()
                # estado passa para SKIP_EOL (se CRC ok) ou IDLE (se CRC ruim)
                continue



    # ---------- Vcore helpers ----------
    def _parse_float(self, s: str, default: float | None) -> float | None:
        try:
            if s is None:
                return default
            s = str(s).strip().replace(",", ".")
            if s == "":
                return default
            return float(s)
        except Exception:
            return default

    def _parse_step(self) -> float:
        step = self._parse_float(self.txt_vstep.text(), 0.05)
        if step is None or step <= 0:
            step = 0.05
        return step

    # ---------- Sending (mensagem / vcore) ----------
    @Slot()
    def on_click_send_manual(self):
        msg = self.txt_message.text()
        if not msg:
            return
            
        target = self.cmb_target.currentData()

        if target == HEADER_STM:
            # Envia usando o protocolo do STM (M + Len + Msg + CRC)
            # O _send_message_command chama _send_frame, que agora adiciona o HEADER_STM por padrão
            # Precisamos garantir que ele use o target correto se alterarmos o padrão
            self._send_message_command(msg) 
        else:
            # Envio para o CROC (Raw Data)
            # Para o CROC, não usamos CRC nem encapsulamento do protocolo STM
            # Apenas: [HEADER_CROC] + [Texto] + [EOL]
            
            payload = msg.encode('utf-8')
            wire = HEADER_CROC + payload + self.selected_eol()
            
            if self._serial_thread and self._serial_thread.isRunning():
                self._serial_thread.write_bytes.emit(wire)
                self._append_log(f"[{self._now()}] [>> CROC] {msg}")
            else:
                self.on_serial_error("Não conectado.")

        self.txt_message.clear()

    @Slot()
    def on_click_set_vcore(self):
        if not (self._serial_thread and self._serial_thread.isRunning()):
            self.on_serial_error("Não conectado.")
            return

        val = self._parse_float(self.txt_vcore.text(), None)
        if val is None:
            QMessageBox.warning(self, "Valor inválido", "Digite uma tensão no formato x.xx (ex.: 1.00).")
            return

        val = round(val, 2)
        self.txt_vcore.setText(f"{val:.2f}")
        self._send_vcore(val)

    @Slot()
    def on_click_vcore_inc(self):
        if not (self._serial_thread and self._serial_thread.isRunning()):
            self.on_serial_error("Não conectado.")
            return
        step = self._parse_step()
        current = self._parse_float(self.txt_vcore.text(), 0.85)
        new_val = round(current + step, 2)
        self.txt_vcore.setText(f"{new_val:.2f}")
        self._send_vcore(new_val)

    @Slot()
    def on_click_vcore_dec(self):
        if not (self._serial_thread and self._serial_thread.isRunning()):
            self.on_serial_error("Não conectado.")
            return
        step = self._parse_step()
        current = self._parse_float(self.txt_vcore.text(), 0.85)
        new_val = round(current - step, 2)
        if new_val < 0:
            new_val = 0.00
        self.txt_vcore.setText(f"{new_val:.2f}")
        self._send_vcore(new_val)

    @Slot()
    def on_click_reset(self):
        if not (self._serial_thread and self._serial_thread.isRunning()):
            self.on_serial_error("Não conectado.")
            return
        resp = QMessageBox.question(self, "Confirmar Reset",
                                    "Enviar comando de RESET?", 
                                    QMessageBox.Yes | QMessageBox.No,
                                    QMessageBox.No)
        if resp != QMessageBox.Yes:
            return
        # Mantém a semântica: reset é uma mensagem "reset"
        self._send_message_command("reset")

    # ---------- Helpers ----------
    def _format_wire_human(self, wire: bytes) -> str:
        try:
            s = wire.decode("utf-8", errors="replace")
        except Exception:
            s = str(wire)
        return s.replace("\r", "\\r").replace("\n", "\\n")

    def _append_log(self, text: str, ensure_newline: bool = True):
        if ensure_newline and not text.endswith("\n"):
            text += "\n"

        edit = self.log
        sb = edit.verticalScrollBar()

        # Detecta se o usuário já estava no fim antes da inserção
        old_max = sb.maximum()
        old_val = sb.value()
        at_bottom = old_val >= old_max - 2

        # Evita repaints durante a inserção
        edit.setUpdatesEnabled(False)

        # Insere no fim usando um cursor do DOCUMENTO (não mexe no cursor do widget)
        doc = edit.document()
        cur = QTextCursor(doc)
        cur.movePosition(QTextCursor.End)
        cur.insertText(text)

        # Reativa repaints
        edit.setUpdatesEnabled(True)

        # Se o usuário estava no fim, acompanha o crescimento; senão mantém posição
        if at_bottom:
            sb.setValue(sb.maximum())
        else:
            # Mantém a rolagem onde estava (aproximadamente a mesma linha no topo)
            sb.setValue(old_val)

    def _append_message_log(self, text: str):
        # escreve "[hora] mensagem" na caixa da direita, com auto-scroll similar ao _append_log
        if text is None:
            return
        if not text.endswith("\n"):
            text = text + "\n"
        line = f"[{self._now()}] {text}"

        edit = self.m_log
        sb = edit.verticalScrollBar()
        old_max, old_val = sb.maximum(), sb.value()
        at_bottom = old_val >= old_max - 2

        edit.setUpdatesEnabled(False)
        doc = edit.document()
        cur = QTextCursor(doc)
        cur.movePosition(QTextCursor.End)
        cur.insertText(line)
        edit.setUpdatesEnabled(True)

        if at_bottom:
            sb.setValue(sb.maximum())
        else:
            sb.setValue(old_val)


    def _update_status(self, msg: str):
        self.status.showMessage(msg)

    @staticmethod
    def _now() -> str:
        return QDateTime.currentDateTime().toString("dd-MM-yyyy HH:mm:ss")


def main():
    app = QApplication(sys.argv)
    apply_dark_palette(app)

    win = MainWindow()
    win.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
