# -*- coding: utf-8 -*-
import os
import sys
import serial.tools.list_ports as list_ports

from PySide6.QtCore import Qt, Slot, QDateTime, QTimer
from PySide6.QtGui import QTextCursor, QFont, QIntValidator, QPalette, QColor
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QLabel, QPushButton, QPlainTextEdit, QLineEdit, QComboBox, QCheckBox,
    QMessageBox, QSizePolicy, QApplication, QSplitter
)

from serial_config import SerialThread
from protocol import (
    compute_crc16_modbus, CRC_ENDIAN, ERR_STR, FUNC_STR, STM_MASTER,
    decode_ctrl, is_error_frame, is_ok_frame, now_str, make_ctrl,
    FUNC_UNK, FUNC_P, FUNC_M, FUNC_V, NO_ERROR, ERR_TIMEOUT, ERR_CRC, ERR_LEN
)
from commands import (
    build_page_command, build_message_command, build_vcore_command
)

TIMEOUT = 10000

# ---------------------- Theming dentro da UI ----------------------
def apply_dark_palette(app: QApplication):
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

# ---------------------- Helpers de Portas (Linux) ----------------------

def _linux_is_good_serial(p) -> bool:
    dev = (p.device or "")
    if not dev.startswith("/dev/"):
        return False
    if getattr(p, "vid", None) is not None or getattr(p, "pid", None) is not None:
        return os.access(dev, os.R_OK | os.W_OK)
    if dev.startswith("/dev/ttyUSB") or dev.startswith("/dev/ttyACM") or dev.startswith("/dev/serial/by-id/"):
        return os.access(dev, os.R_OK | os.W_OK)
    return False

def _linux_pretty_device(dev: str) -> str:
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

# ---------------------- Janela Principal ----------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PCB Serial Controller")
        self.setMinimumSize(980, 600)
        self._serial_thread: SerialThread | None = None

        # Estado interno
        self._last_wire_sent = b""
        self._last_crc_hex = "0000"
        self._last_crc_bytes = b""
        
        # Buffer de recepção textual
        self._rx_buf = ""
        self._last_was_cr = False

        # Estado do parser byte-a-byte
        self._sm_state = "IDLE"  # IDLE | WAIT_CRC1 | WAIT_CRC2 | SKIP_EOL
        self._sm_ctrl = None
        self._sm_crc1 = None
        self._sm_crc2 = None

        # UI
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        self.conn_box = self._build_connection_group()
        layout.addWidget(self.conn_box)

        mid = QHBoxLayout()
        mid.setSpacing(12)
        self.quick_box = self._build_quick_commands_group()
        self.manual_box = self._build_manual_send_group()
        mid.addWidget(self.quick_box, 1)
        mid.addWidget(self.manual_box, 2)
        layout.addLayout(mid, 0)

        # Área de Log
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

        self.status = self.statusBar()
        self._update_status("Pronto.")

        # Timer de resposta a comandos
        self._resp_timer = QTimer(self)
        self._resp_timer.setSingleShot(True)
        self._resp_timer.timeout.connect(self._on_response_timeout)
        self._awaiting_response = False
        self._resp_context = ""
        self._await_deadline_ms = 0
        
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

        row += 1
        grid.addWidget(QLabel("Formato:"), row, 0)
        self.cmb_format = QComboBox()
        self.cmb_format.addItems(["8N1", "8E1", "8O1", "7E1", "8N2"])
        grid.addWidget(self.cmb_format, row, 1)

        self.btn_connect = QPushButton("Conectar")
        self.btn_connect.setCheckable(True)
        self.btn_connect.clicked.connect(self.on_toggle_connect)
        grid.addWidget(self.btn_connect, row, 2)

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
        
        # Botões de Limpar
        clear_row = QHBoxLayout()
        self.btn_clear_log = QPushButton("Limpar log")
        self.btn_clear_log.clicked.connect(self._clear_log)
        clear_row.addWidget(self.btn_clear_log)
        self.btn_clear_message_log = QPushButton("Limpar mensagens")
        self.btn_clear_message_log.clicked.connect(self._clear_message_log)
        clear_row.addWidget(self.btn_clear_message_log)
        v.addLayout(clear_row)

        opts_row = QHBoxLayout()
        self.chk_hex_view = QCheckBox("Exibir RX em HEX")
        self.chk_hex_view.setChecked(False)
        opts_row.addWidget(self.chk_hex_view)

        self.chk_tx_details = QCheckBox("Detalhes de TX")
        self.chk_tx_details.setChecked(False)
        opts_row.addWidget(self.chk_tx_details)
        opts_row.addStretch(1)

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

        grid.addWidget(QLabel("Mensagem:"), row, 0)
        self.txt_message = QLineEdit()
        self.txt_message.setMaxLength(65535)
        self.txt_message.returnPressed.connect(self.on_click_send_manual)
        grid.addWidget(self.txt_message, row, 1, 1, 3)

        row += 1
        grid.addWidget(QLabel("Terminador:"), row, 0)
        self.cmb_eol = QComboBox()
        self.cmb_eol.addItems(["LF (\\n)", "CR (\\r)", "CRLF (\\r\\n)", "Nenhum"])
        self.cmb_eol.setCurrentIndex(3)
        grid.addWidget(self.cmb_eol, row, 1)

        self.btn_send = QPushButton("Enviar")
        self.btn_send.clicked.connect(self.on_click_send_manual)
        grid.addWidget(self.btn_send, row, 3)

        return g
    
    # --- Grupos de Log ---
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
        self.m_log.setReadOnly(True)
        self.m_log.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.m_log.setPlaceholderText("Conteúdo das mensagens recebidas aparecerá aqui...")
        self.m_log.setFont(QFont("Consolas", 10))
        v.addWidget(self.m_log)
        return g

    # ---------- Aux (Log Helpers) ----------
    def _clear_log(self):
        if hasattr(self, "log") and self.log:
            self.log.clear()
            
    def _clear_message_log(self):
        if hasattr(self, "m_log") and self.m_log:
            self.m_log.clear()

    # ---------- Port Discovery ----------
    def refresh_ports(self, auto_select_stlink: bool = False):
        self.cmb_port.clear()
        ports = list_ports.comports()

        if sys.platform.startswith("linux"):
            ports = [p for p in ports if _linux_is_good_serial(p)]
        
        ports = sorted(ports, key=lambda p: (p.device or ""))

        for p in ports:
            dev = p.device or ""
            pretty = _linux_pretty_device(dev) if sys.platform.startswith("linux") else dev
            desc = p.description or ""
            label = f"{pretty} — {desc}".strip(" —")
            self.cmb_port.addItem(label, userData=pretty)

        if auto_select_stlink and self.cmb_port.count() > 0:
            chosen_index = -1
            # 1) por texto
            for i in range(self.cmb_port.count()):
                txt = (self.cmb_port.itemText(i) or "").lower()
                if any(k in txt for k in ("stlink", "st-link", "stmicro", "stmicroelectronics", "stm")):
                    chosen_index = i
                    break
            # 2) por VID
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

    # ---------- EOL ----------
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

    # ---------- Envio / CRC ----------
    def _crc_bytes(self, payload: bytes) -> bytes:
        crc = compute_crc16_modbus(payload)
        self._last_crc_hex = f"{crc:04X}"
        self._last_crc_bytes = crc.to_bytes(2, CRC_ENDIAN)
        return self._last_crc_bytes

    def _send_frame(self, payload_without_crc: bytes, log_str: str):
        if not (self._serial_thread and self._serial_thread.isRunning()):
            self.on_serial_error("Não conectado.")
            return
        crc2 = self._crc_bytes(payload_without_crc)
        wire = payload_without_crc + crc2 + self.selected_eol()
        self._last_wire_sent = wire
        self._append_log(f"[{now_str()}] [>>] {log_str} {self._last_crc_hex}")
        self._serial_thread.write_bytes.emit(wire)
        
        # Timer de Resposta
        self._start_response_timer(log_str, ms=TIMEOUT)
        
    # ---------- Timer de Resposta ----------
    def _start_response_timer(self, context: str, ms: int = TIMEOUT):
        try:
            if self._resp_timer.isActive():
                self._resp_timer.stop()
        except Exception:
            pass
        self._resp_context = context
        self._awaiting_response = True
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
        if not self._awaiting_response:
            return
        self._awaiting_response = False
        ctx = f" ({self._resp_context})" if self._resp_context else ""
        self._append_log(f"[{now_str()}] [ERRO] Sem resposta{ctx} após {TIMEOUT} ms.")
        self._resp_context = ""
        
    def _is_ctrl_candidate(self, b: int) -> bool:
        if not self._awaiting_response:
            return False
        if QDateTime.currentMSecsSinceEpoch() > self._await_deadline_ms:
            # Resposta chegou, mas o timer já estourou
            return False
            
        return is_error_frame(b) or is_ok_frame(b)

    # ---------- Logging ----------
    def _append_log(self, text: str, ensure_newline: bool = True):
        # (Este é o log geral)
        if ensure_newline and not text.endswith("\n"):
            text += "\n"

        edit = self.log
        if not edit: return
        sb = edit.verticalScrollBar()
        
        old_max = sb.maximum()
        old_val = sb.value()
        at_bottom = old_val >= old_max - 2

        edit.setUpdatesEnabled(False)
        doc = edit.document()
        cur = QTextCursor(doc)
        cur.movePosition(QTextCursor.End)
        cur.insertText(text)
        edit.setUpdatesEnabled(True)

        if at_bottom:
            sb.setValue(sb.maximum())
        else:
            sb.setValue(old_val)
            
    def _append_message_log(self, text: str):
        # (Este é o log de mensagens recebidas)
        if text is None:
            return
        if not text.endswith("\n"):
            text = text + "\n"
        line = f"[{now_str()}] {text}"

        edit = self.m_log
        if not edit: return
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

    def _log_ok_ctrl(self, ctrl: int, crc1: int | None = None, crc2: int | None = None):
        bits = f"{ctrl:08b}"
        self._append_log(f"[{now_str()}] [<<] OK   :{bits}")
        if self.chk_tx_details.isChecked():
            direction, _, func = decode_ctrl(ctrl)
            dir_str = "MASTER" if direction == STM_MASTER else "SLAVE"
            fn_str  = FUNC_STR.get(func, f"0x{func:02X}")
            extra_crc = f", crc=0x{crc1:02X} 0x{crc2:02X}" if (crc1 is not None and crc2 is not None) else ""
            self._append_log(f"           └ detalhes: Ok={bits}, dir={dir_str}, func={fn_str}{extra_crc}")

    def _log_error_ctrl(self, ctrl: int, crc1: int | None = None, crc2: int | None = None):
        direction, error, func = decode_ctrl(ctrl)
        bits = f"{ctrl:08b}"
        self._append_log(f"[{now_str()}] [<<] Erro :{bits}")
        if self.chk_tx_details.isChecked():
            dir_str = "MASTER" if direction == STM_MASTER else "SLAVE"
            err_str = ERR_STR.get(error, f"0x{error:02X}")
            fn_str  = FUNC_STR.get(func,  f"0x{func:02X}")
            extra_crc = f", crc=0x{crc1:02X} 0x{crc2:02X}" if (crc1 is not None and crc2 is not None) else ""
            self._append_log(f"           └ detalhes: Erro={bits}, dir={dir_str}, tipo={err_str}, func={fn_str}{extra_crc}")

    # ---------- Métodos do Parser ----------
    def _reset_ctrl_sm(self):
        self._sm_state = "IDLE"
        self._sm_ctrl  = None
        self._sm_crc1  = None
        self._sm_crc2  = None

    def _crc2_matches(self, first_byte: int, crc_b1: int, crc_b2: int) -> bool:
        expected = compute_crc16_modbus(bytes([first_byte]))
        if CRC_ENDIAN == "little":
            got = (crc_b1 & 0xFF) | ((crc_b2 & 0xFF) << 8)
        else:
            got = ((crc_b1 & 0xFF) << 8) | (crc_b2 & 0xFF)
        return expected == got

    def _accept_ctrl_and_log(self):
        ctrl, c1, c2 = self._sm_ctrl, self._sm_crc1, self._sm_crc2
        if self._crc2_matches(ctrl, c1, c2):
            if is_error_frame(ctrl):
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
                now = now_str()
                if self.chk_hex_view.isChecked():
                    hexline = " ".join(f"{ord(c):02X}" for c in line)
                    self._append_log(f"[{now}] [<<] {hexline}")
                else:
                    self._append_log(f"[{now}] [<<] {line}")
                # Envia para a caixa de mensagens separada
                self._append_message_log(line)
            return

        if b == 0x0A:  # LF
            if self._last_was_cr:
                self._last_was_cr = False
                return
            line = self._rx_buf
            self._rx_buf = ""
            if line != "":
                now = now_str()
                if self.chk_hex_view.isChecked():
                    hexline = " ".join(f"{ord(c):02X}" for c in line)
                    self._append_log(f"[{now}] [<<] {hexline}")
                else:
                    self._append_log(f"[{now}] [<<] {line}")
                self._append_message_log(line)
            return

        self._last_was_cr = False
        try:
            ch = bytes([b]).decode("utf-8")
        except UnicodeDecodeError:
            ch = bytes([b]).decode("latin-1", errors="replace")
        self._rx_buf += ch

    # ---------- Serial Callbacks ----------
    @Slot(str)
    def on_serial_opened(self, port_str: str):
        self.btn_connect.setChecked(True)
        self.btn_connect.setText("Desconectar")
        self._append_log(f"[{now_str()}] [INFO] Conectado em {port_str}\n")

    @Slot()
    def on_serial_closed(self):
        self._response_received()
        if self._rx_buf:
            self._append_log(f"[{now_str()}] [<<] {self._rx_buf}")
            self._rx_buf = ""
        self.btn_connect.setChecked(False)
        self.btn_connect.setText("Conectar")
        self._append_log(f"[{now_str()}] [INFO] Conexão encerrada\n")

    @Slot(str)
    def on_serial_info(self, msg: str):
        self._update_status(msg)
        self._append_log(f"[{now_str()}] [INFO] {msg}\n")

    @Slot(str)
    def on_serial_error(self, msg: str):
        self._update_status(msg)
        self._append_log(f"[{now_str()}] [ERRO] {msg}\n")

    @Slot(bytes)
    def on_serial_data(self, data: bytes):
        for b in data:
            if self._sm_state == "SKIP_EOL":
                if b in (0x0D, 0x0A):
                    continue
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
                continue

    # ---------- Quick actions / send ----------
    def _send_page_command(self, page_val: int):
        page_val = max(1, min(6, page_val))
        self.txt_page.setText(str(page_val))
        payload, log_str, meta = build_page_command(page_val)
        self._send_frame(payload, log_str)

        if self.chk_tx_details.isChecked():
            c1, c2 = self._last_crc_bytes[0], self._last_crc_bytes[1]
            ctrl = meta["ctrl"]
            self._append_log(
                f"           └ detalhes: dir=SLAVE, err=NONE, func=P, "
                f"attrs={page_val}, wire={ctrl:08b} + {page_val} + 0x{c1:02X} 0x{c2:02X}\n"
            )

    def _send_message_command(self, msg: str):
        try:
            payload, log_str, meta = build_message_command(msg)
        except ValueError as e:
            QMessageBox.warning(self, "Mensagem muito grande", str(e))
            return
        self._send_frame(payload, log_str)
        if self.chk_tx_details.isChecked():
            c1, c2 = self._last_crc_bytes[0], self._last_crc_bytes[1]
            ctrl = meta["ctrl"]
            self._append_log(
                f"           └ detalhes: dir=SLAVE, err=NONE, func=M, "
                f"len={meta['len']} ({meta['size_hex']}), wire={ctrl:08b} + <len2> + <msg> + 0x{c1:02X} 0x{c2:02X}\n"
            )

    def _send_vcore(self, value: float):
        payload, log_str, meta = build_vcore_command(value)
        self._send_frame(payload, log_str)
        if self.chk_tx_details.isChecked():
            c1, c2 = self._last_crc_bytes[0], self._last_crc_bytes[1]
            ctrl = meta["ctrl"]
            self._append_log(
                f"           └ detalhes: dir=SLAVE, err=NONE, func=V, attrs={meta['attrs']}, wire={ctrl:08b} + {meta['attrs']} + 0x{c1:02X} 0x{c2:02X}\n"
            )

    # ---------- Página: handlers ----------
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
        self._send_message_command(msg)
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
        self._send_message_command("reset")

    # ---------- Helpers ----------
    def _update_status(self, msg: str):
        self.status.showMessage(msg)