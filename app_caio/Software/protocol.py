# -*- coding: utf-8 -*-
from PySide6.QtCore import QDateTime

# --------- Constantes / Enums do protocolo ---------
STM_MASTER  = 0x80
STM_SLAVE   = 0x00

NO_ERROR    = 0x00
ERR_TIMEOUT = 0x10
ERR_CRC     = 0x20
ERR_LEN     = 0x30
ERROR_MASK  = 0x70

FUNC_UNK = 0x00
FUNC_P   = 0x01
FUNC_M   = 0x02
FUNC_V   = 0x03

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
    FUNC_V:   "V",
}

CRC_ENDIAN = "little"  # ordem dos 2 bytes de CRC no fio
LEN_ENDIAN = "big"     # ordem dos 2 bytes do campo de tamanho

# --------- CRC16/Modbus ---------
def compute_crc16_modbus(data: bytes) -> int:
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc & 0xFFFF

# --------- Helpers de protocolo ---------
def make_ctrl(direction: int, error: int, func: int) -> int:
    return (direction & 0x80) | (error & ERROR_MASK) | (func & 0x03)

def decode_ctrl(b: int):
    direction = STM_MASTER if (b & 0x80) else STM_SLAVE
    error = b & ERROR_MASK
    func = b & 0x03
    return direction, error, func

def is_ok_frame(b: int) -> bool:
    _, error, func = decode_ctrl(b)
    return (error == NO_ERROR) and (func in (FUNC_UNK, FUNC_P, FUNC_M, FUNC_V))

def is_error_frame(b: int) -> bool:
    _, error, func = decode_ctrl(b)
    return (error != NO_ERROR) and (func in (FUNC_UNK, FUNC_P, FUNC_M, FUNC_V))

def crc2_matches(first_byte: int, crc_b1: int, crc_b2: int) -> bool:
    expected = compute_crc16_modbus(bytes([first_byte]))
    if CRC_ENDIAN == "little":
        got = (crc_b1 & 0xFF) | ((crc_b2 & 0xFF) << 8)
    else:
        got = ((crc_b1 & 0xFF) << 8) | (crc_b2 & 0xFF)
    return expected == got

def now_str() -> str:
    return QDateTime.currentDateTime().toString("dd-MM-yyyy HH:mm:ss")

# --------- Parser byte-a-byte (gera eventos) ---------
class ProtocolParser:
    """
    Converte bytes recebidos em eventos:
    - ('ok', ctrl, crc1, crc2)
    - ('error', ctrl, crc1, crc2)
    - ('line', text_line)
    Mantém semântica original: ignora CR/LF logo após um quadro válido.
    """
    def __init__(self):
        self._sm_state = "IDLE"      # IDLE, WAIT_CRC1, WAIT_CRC2 e SKIP_EOL
        self._sm_ctrl  = None
        self._sm_crc1  = None
        self._sm_crc2  = None
        self._last_was_cr = False
        self._rx_buf = ""

    def feed(self, data: bytes):
        events = []
        for b in data:
            # Após quadro válido, ignorar CR/LF seguintes
            if self._sm_state == "SKIP_EOL":
                if b in (0x0D, 0x0A):
                    continue
                self._sm_state = "IDLE"

            if self._sm_state == "IDLE":
                if is_error_frame(b) or is_ok_frame(b):
                    self._sm_ctrl = b
                    self._sm_state = "WAIT_CRC1"
                else:
                    self._process_text_byte(b, events)
                continue

            if self._sm_state == "WAIT_CRC1":
                self._sm_crc1 = b
                self._sm_state = "WAIT_CRC2"
                continue

            if self._sm_state == "WAIT_CRC2":
                self._sm_crc2 = b
                ctrl, c1, c2 = self._sm_ctrl, self._sm_crc1, self._sm_crc2
                if crc2_matches(ctrl, c1, c2):
                    if is_error_frame(ctrl):
                        events.append(('error', ctrl, c1, c2))
                    else:
                        events.append(('ok', ctrl, c1, c2))
                    self._sm_state = "SKIP_EOL"
                else:
                    # CRC inválido: devolve os 3 bytes para o fluxo textual
                    for x in (ctrl, c1, c2):
                        self._process_text_byte(x, events)
                    self._sm_state = "IDLE"
                self._sm_ctrl = self._sm_crc1 = self._sm_crc2 = None
                continue
        return events

    def _process_text_byte(self, b: int, events: list):
        if b == 0x0D:  # CR
            self._last_was_cr = True
            line = self._rx_buf
            self._rx_buf = ""
            if line != "":
                events.append(('line', line))
            return
        if b == 0x0A:  # LF
            if self._last_was_cr:
                self._last_was_cr = False
                return
            line = self._rx_buf
            self._rx_buf = ""
            if line != "":
                events.append(('line', line))
            return

        self._last_was_cr = False
        try:
            ch = bytes([b]).decode("utf-8")
        except UnicodeDecodeError:
            ch = bytes([b]).decode("latin-1", errors="replace")
        self._rx_buf += ch
