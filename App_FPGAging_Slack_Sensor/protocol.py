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

# UPDATED: Packet is now 9 bytes: [TL, TH, 00, SL, SH, VL, VH, 00, AL]
AGING_PKT_LEN = 9

# --------- Fatores de Conversão Xilinx UltraScale+ (Matches debugger.py) ---------
def raw_to_temp(raw_16bit):
    """
    Converts XADC raw 16-bit value to Celsius.
    Logic: ((ADC[15:4] * 503.975) / 4096) - 273.15
    """
    # Shift right by 4 (discard lower 4 bits)
    adc_12bit = (raw_16bit >> 4) & 0xFFF
    return (adc_12bit * 503.975 / 4096.0) - 273.15

def raw_to_vcc(raw_16bit):
    """
    Converts XADC raw 16-bit value to Voltage.
    Logic: (ADC[15:4] * 3.0) / 4096
    """
    adc_12bit = (raw_16bit >> 4) & 0xFFF
    return (adc_12bit * 3.0) / 4096.0

# -------------------------------------------------------------------------
# Funções Auxiliares de Protocolo (STM32)
# -------------------------------------------------------------------------
def make_ctrl(origin, error, func):
    return (origin & 0x80) | (error & 0x70) | (func & 0x0F)

def decode_ctrl(byte_val):
    origin = byte_val & 0x80
    error  = byte_val & 0x70
    func   = byte_val & 0x0F
    return origin, error, func

def compute_crc16_modbus(data: bytes) -> int:
    crc = 0xFFFF
    for b in data:
        crc ^= b
        for _ in range(8):
            if (crc & 0x0001):
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return crc

# -------------------------------------------------------------------------
# Multi-sensor packet (experimental-multi-sensor branch only)
#
# Matches multi_sensor_stream.sv -- see that file's header comment for the
# exact byte layout. This is a separate, self-framed protocol (sync bytes +
# length + checksum) used only on this branch; it does not touch the
# single-channel 9-byte format above.
# -------------------------------------------------------------------------
MULTI_SYNC0 = 0xAA
MULTI_SYNC1 = 0x55
MULTI_NUM_CHANNELS = 4
MULTI_PKT_LEN = 10 + 2 * MULTI_NUM_CHANNELS  # sync(2)+len(1)+temp(3)+vcc(3)+slack(2N)+alarm(1)+cksum(1)


def parse_multi_sensor_packet(pkt: bytes, num_channels: int = MULTI_NUM_CHANNELS):
    """
    Decodes one multi_sensor_stream.sv frame. `pkt` must be exactly
    MULTI_PKT_LEN bytes, starting at the sync bytes (framing/sync-byte
    search is the router's job, not this function's).

    Returns a dict with 'temp_raw' (24-bit), 'vccint_raw' (24-bit),
    'slack' (list[int], one per channel), 'alarm' (list[bool], one per
    channel) -- or None if the sync bytes or checksum don't match.
    """
    expected_len = 10 + 2 * num_channels
    if len(pkt) != expected_len:
        return None
    if pkt[0] != MULTI_SYNC0 or pkt[1] != MULTI_SYNC1:
        return None

    len_field    = pkt[2]
    temp_bytes   = pkt[3:6]
    vccint_bytes = pkt[6:9]
    slack_bytes  = pkt[9:9 + 2 * num_channels]
    alarm_byte   = pkt[9 + 2 * num_channels]
    checksum     = pkt[10 + 2 * num_channels]

    calc = len_field
    for b in temp_bytes:
        calc ^= b
    for b in vccint_bytes:
        calc ^= b
    for b in slack_bytes:
        calc ^= b
    calc ^= alarm_byte
    calc &= 0xFF

    if calc != checksum:
        return None

    return {
        'temp_raw':   int.from_bytes(temp_bytes, 'little'),
        'vccint_raw': int.from_bytes(vccint_bytes, 'little'),
        'slack':      [int.from_bytes(slack_bytes[2 * i:2 * i + 2], 'little')
                        for i in range(num_channels)],
        'alarm':      [bool((alarm_byte >> i) & 1) for i in range(num_channels)],
    }


# -------------------------------------------------------------------------
# CLASSE: ProtocolParser
# -------------------------------------------------------------------------
class ProtocolParser:
    def __init__(self):
        self._rx_buf = bytes()

    def feed(self, chunk: bytes) -> list:
        """
        Recebe bytes e retorna eventos do STM32 ou Texto.
        (A detecção de Aging Packet agora é feita no Router via Sliding Window)
        Eventos:
          ('line', "texto") -> Logs
          ('ok', meta), ('error', meta) -> Respostas de Comandos
        """
        events = []
        # Concatena ao buffer existente
        self._rx_buf += chunk

        while len(self._rx_buf) > 0:
            byte = self._rx_buf[0]

            # ------------------------------------------------------------------
            # DETECÇÃO STM32 (Headers 0x10, 0x20 ou Texto)
            # ------------------------------------------------------------------
            
            # Verifica tamanho mínimo para header binário (min 4 bytes: Head+Ctrl+LenH+LenL)
            if len(self._rx_buf) < 4:
                # Se for caractere imprimível, pode ser texto, tentamos processar linha
                if (32 <= byte <= 126) or byte in [10, 13]:
                    # Processamento simples de linha
                    idx = -1
                    if 10 in self._rx_buf: idx = self._rx_buf.find(10)
                    elif 13 in self._rx_buf: idx = self._rx_buf.find(13)
                    
                    if idx != -1:
                        line_bytes = self._rx_buf[:idx+1]
                        self._rx_buf = self._rx_buf[idx+1:]
                        line_str = line_bytes.decode('utf-8', errors='ignore').strip()
                        if line_str:
                            events.append(('line', line_str))
                        continue
                # Se não tem tamanho e não formou linha, espera.
                break

            # Se chegamos aqui, temos > 4 bytes. Tenta decodificar binário STM32.
            head = self._rx_buf[0]
            ctrl = self._rx_buf[1]
            origin, error, func = decode_ctrl(ctrl)

            if (head == 0x20 or head == 0x10): 
                # Lê tamanho
                payload_len = int.from_bytes(self._rx_buf[2:4], LEN_ENDIAN)
                total_len = 4 + payload_len + 2 # Header(4) + Payload + CRC(2)

                if len(self._rx_buf) >= total_len:
                    # Pacote completo!
                    packet = self._rx_buf[:total_len]
                    self._rx_buf = self._rx_buf[total_len:]

                    # Valida CRC
                    msg_crc = packet[:-2]
                    recv_crc = int.from_bytes(packet[-2:], CRC_ENDIAN)
                    calc_crc = compute_crc16_modbus(msg_crc)

                    meta = {"func": FUNC_STR.get(func, "UNK"), "origin": origin}

                    if calc_crc == recv_crc:
                        if error == NO_ERROR:
                            events.append(('ok', meta))
                        else:
                            meta["err"] = ERR_STR.get(error, "UNK")
                            events.append(('error', meta))
                    else:
                        meta["err"] = "CRC_FAIL"
                        events.append(('error', meta))
                    continue
                else:
                    # Pacote STM incompleto, espera
                    break
            else:
                # Não é Header STM. Pode ser texto solto ou lixo.
                # Consome 1 byte e continua
                self._rx_buf = self._rx_buf[1:]
                continue
                
        return events