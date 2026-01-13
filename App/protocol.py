# -*- coding: utf-8 -*-
"""
Protocol definitions and parser for CROC FPGA System

Handles:
- STM32 binary protocol frames
- Text output from CROC firmware

Updated for text-based sensor output format.
"""

from PySide6.QtCore import QDateTime

# --------- Constantes / Enums do protocolo STM32 ---------
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

# --------- Conversão XADC (para uso futuro) ---------
def raw_to_temp(raw_16bit):
    """
    Converts XADC raw 16-bit value to Celsius.
    Logic: ((ADC[15:4] * 503.975) / 4096) - 273.15
    """
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
    """Calcula CRC-16 Modbus"""
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
    """
    Parser para respostas do protocolo STM32.
    
    Formato de resposta STM32:
      [Ctrl][CRC_L][CRC_H]  (resposta simples, 3 bytes)
    
    Onde Ctrl contém:
      - Bits 7: Direction (0x00 = Slave response)
      - Bits 6-4: Error code
      - Bits 3-0: Function code
    """
    
    def __init__(self):
        self._rx_buf = bytearray()

    def feed(self, chunk: bytes) -> list:
        """
        Recebe bytes e retorna eventos identificados.
        
        Eventos possíveis:
          ('ok', (status, ctrl, crc_l, crc_h)) -> Resposta OK
          ('error', (status, ctrl, crc_l, crc_h)) -> Resposta com erro
          ('line', "texto") -> Linha de texto
        """
        events = []
        self._rx_buf.extend(chunk)

        while len(self._rx_buf) >= 3:
            # Tenta parsear como resposta STM32 (3 bytes: Ctrl + CRC)
            ctrl = self._rx_buf[0]
            origin, error, func = decode_ctrl(ctrl)
            
            # Verifica se parece uma resposta válida do STM32
            # Origin deve ser 0x00 (STM_SLAVE) para resposta
            # Func deve ser válido (0x01, 0x02, 0x03)
            if origin == STM_SLAVE and func in (FUNC_P, FUNC_M, FUNC_V):
                # Resposta STM32: [Ctrl][CRC_L][CRC_H]
                if len(self._rx_buf) >= 3:
                    ctrl_byte = self._rx_buf[0]
                    crc_l = self._rx_buf[1]
                    crc_h = self._rx_buf[2]
                    
                    # Valida CRC
                    recv_crc = crc_l | (crc_h << 8)
                    calc_crc = compute_crc16_modbus(bytes([ctrl_byte]))
                    
                    if recv_crc == calc_crc:
                        # CRC válido
                        del self._rx_buf[:3]
                        
                        if error == NO_ERROR:
                            events.append(('ok', (ctrl_byte, ctrl_byte, crc_l, crc_h)))
                        else:
                            events.append(('error', (ctrl_byte, ctrl_byte, crc_l, crc_h)))
                        continue
                    else:
                        # CRC inválido - pode não ser frame STM32
                        # Descarta primeiro byte e tenta novamente
                        del self._rx_buf[0]
                        continue
                else:
                    # Precisa de mais bytes
                    break
            else:
                # Não parece resposta STM32, pode ser texto
                # Procura por caracteres printáveis
                if 32 <= self._rx_buf[0] <= 126 or self._rx_buf[0] in [0x0A, 0x0D]:
                    # Tenta encontrar fim de linha
                    newline_idx = -1
                    for i, b in enumerate(self._rx_buf):
                        if b == 0x0A:
                            newline_idx = i
                            break
                    
                    if newline_idx >= 0:
                        line_bytes = bytes(self._rx_buf[:newline_idx])
                        del self._rx_buf[:newline_idx + 1]
                        try:
                            line_str = line_bytes.decode('utf-8', errors='ignore').strip()
                            if line_str:
                                events.append(('line', line_str))
                        except:
                            pass
                        continue
                    else:
                        # Sem newline ainda, espera mais dados
                        break
                else:
                    # Byte não reconhecido, descarta
                    del self._rx_buf[0]
                    continue
        
        return events

    def clear(self):
        """Limpa o buffer interno"""
        self._rx_buf.clear()