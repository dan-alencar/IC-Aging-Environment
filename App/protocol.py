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

# UPDATED: Packet length is now 8 bytes for UltraScale+ System
# [Header 1A] + [Temp 2B] + [Vcc 2B] + [Slack 2B] + [Alarm 1B]
AGING_PKT_LEN = 8  

# --------- Fatores de Conversão Xilinx UltraScale+ (SYSMONE4) ---------
def raw_to_temp(raw_val):
    # Transfer Function: Temp(C) = (ADC * 501.3743 / 65536) - 273.67
    return (raw_val * 501.3743 / 65536.0) - 273.67

def raw_to_vcc(raw_val):
    # Transfer Function: VCC(V) = (ADC / 65536) * 3.0V
    return (raw_val / 65536.0) * 3.0

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
# CLASSE: ProtocolParser
# -------------------------------------------------------------------------
class ProtocolParser:
    def __init__(self):
        self._rx_buf = bytes()
        self._last_was_cr = False

    def feed(self, chunk: bytes) -> list:
        """
        Recebe bytes crus e retorna uma lista de eventos:
          ('line', "texto") -> Logs do STM32
          ('aging', {dict}) -> Dados do Sensor FPGA
          ('ok', meta), ('error', meta) -> Respostas de Comandos
        """
        events = []
        # Concatena ao buffer existente
        self._rx_buf += chunk

        while len(self._rx_buf) > 0:
            byte = self._rx_buf[0]

            # ------------------------------------------------------------------
            # 1. PACOTE DE AGING (FPGA) - Header 0x1A
            # ------------------------------------------------------------------
            if byte == 0x1A:
                if len(self._rx_buf) >= AGING_PKT_LEN:
                    # Extrai o pacote completo
                    pkt = self._rx_buf[:AGING_PKT_LEN]
                    self._rx_buf = self._rx_buf[AGING_PKT_LEN:] # Remove do buffer
                    
                    # Unpack: [1A][TH][TL][VH][VL][SH][SL][AL]
                    raw_temp  = (pkt[1] << 8) | pkt[2]
                    raw_vcc   = (pkt[3] << 8) | pkt[4]
                    raw_slack = (pkt[5] << 8) | pkt[6] # Slack / Phase Count
                    raw_alarm = pkt[7]

                    data = {
                        'dut_temp':  raw_to_temp(raw_temp),
                        'dut_volt':  raw_to_vcc(raw_vcc),
                        'dut_slack': raw_slack, # Passa o Slack direto (Inteiro)
                        'alarm':     bool(raw_alarm)
                    }
                    events.append(('aging', data))
                    continue
                else:
                    # Pacote incompleto, aguarda mais bytes
                    break
            
            # ------------------------------------------------------------------
            # 2. PACOTES DO STM32 (Headers 0x10, 0x20 ou Texto)
            # ------------------------------------------------------------------
            # Se não for 0x1A, assumimos lógica legado ou texto
            # A lógica abaixo tenta detectar texto vs binário STM
            
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
            # (Mantendo a lógica original do seu arquivo para compatibilidade)
            head = self._rx_buf[0]
            ctrl = self._rx_buf[1]
            origin, error, func = decode_ctrl(ctrl)

            # Verifica se parece um pacote STM válido
            is_protocol_noise = False
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
                # Não é Header 0x1A, nem 0x10, nem 0x20. É Lixo ou Texto solto.
                # Consome 1 byte para tentar resincronizar ou processa como texto
                self._process_text_byte(byte, events)
                self._rx_buf = self._rx_buf[1:]
                continue
                
        return events

    def _process_text_byte(self, b: int, events: list):
        # Auxiliar para remontar linhas de texto caractere por caractere
        # se o buffer estiver desalinhado
        if b == 0x0D: return # Ignora CR solto se tratado no loop principal
        if b == 0x0A: return 
        # (Implementação simplificada: O loop principal já trata chunks de linhas.
        #  Aqui só descartamos bytes não processados para limpar o buffer)
        pass