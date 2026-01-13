# -*- coding: utf-8 -*-
"""
Protocol Definitions for CROC System

STM32 communication protocol and utilities.
"""

# --------- STM32 Protocol Constants ---------
STM_MASTER  = 0x80
STM_SLAVE   = 0x00

NO_ERROR    = 0x00
ERR_TIMEOUT = 0x10
ERR_CRC     = 0x20
ERR_LEN     = 0x30
ERROR_MASK  = 0x70

FUNC_UNK = 0x00
FUNC_P   = 0x01  # Page
FUNC_M   = 0x02  # Message
FUNC_V   = 0x03  # Voltage

ERR_STR = {
    NO_ERROR:    "NONE",
    ERR_TIMEOUT: "TIMEOUT",
    ERR_CRC:     "CRC",
    ERR_LEN:     "LEN"
}

FUNC_STR = {
    FUNC_UNK: "UNK",
    FUNC_P:   "PAGE",
    FUNC_M:   "MSG",
    FUNC_V:   "VOLT",
}

CRC_ENDIAN = "little"
LEN_ENDIAN = "big"


def make_ctrl(origin: int, error: int, func: int) -> int:
    """Create control byte from components."""
    return (origin & 0x80) | (error & 0x70) | (func & 0x0F)


def decode_ctrl(byte_val: int) -> tuple:
    """Decode control byte into components."""
    origin = byte_val & 0x80
    error  = byte_val & 0x70
    func   = byte_val & 0x0F
    return origin, error, func


def compute_crc16_modbus(data: bytes) -> int:
    """Calculate Modbus CRC-16."""
    crc = 0xFFFF
    for b in data:
        crc ^= b
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc


class ProtocolParser:
    """
    Parser for STM32 protocol responses.
    
    Response format: [Ctrl][CRC_L][CRC_H] (3 bytes)
    """
    
    def __init__(self):
        self._rx_buf = bytearray()

    def feed(self, chunk: bytes) -> list:
        """
        Process incoming bytes and return parsed events.
        
        Returns:
            List of tuples: ('ok'/'error', data) or ('line', text)
        """
        events = []
        self._rx_buf.extend(chunk)

        while len(self._rx_buf) >= 3:
            ctrl = self._rx_buf[0]
            origin, error, func = decode_ctrl(ctrl)
            
            # Check for valid STM32 response
            if origin == STM_SLAVE and func in (FUNC_P, FUNC_M, FUNC_V):
                ctrl_byte = self._rx_buf[0]
                crc_l = self._rx_buf[1]
                crc_h = self._rx_buf[2]
                
                # Validate CRC
                recv_crc = crc_l | (crc_h << 8)
                calc_crc = compute_crc16_modbus(bytes([ctrl_byte]))
                
                if recv_crc == calc_crc:
                    del self._rx_buf[:3]
                    
                    meta = {
                        'func': FUNC_STR.get(func, 'UNK'),
                        'ctrl': ctrl_byte,
                    }
                    
                    if error == NO_ERROR:
                        events.append(('ok', meta))
                    else:
                        meta['err'] = ERR_STR.get(error, 'UNK')
                        events.append(('error', meta))
                    continue
                else:
                    # CRC mismatch - discard byte
                    del self._rx_buf[0]
                    continue
            else:
                # Not a valid protocol byte
                # Check for printable text
                if 32 <= self._rx_buf[0] <= 126 or self._rx_buf[0] in [0x0A, 0x0D]:
                    # Find newline
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
                        break
                else:
                    # Unknown byte, discard
                    del self._rx_buf[0]
                    continue
        
        return events

    def clear(self):
        """Clear internal buffer."""
        self._rx_buf.clear()


# --------- Command Builders ---------

HEADER_STM = 0x20


def build_page_command(page: int) -> tuple:
    """
    Build page change command.
    
    Returns:
        (payload_bytes, log_string, metadata)
    """
    page = max(1, min(6, page))
    ctrl = make_ctrl(STM_SLAVE, NO_ERROR, FUNC_P)
    attrs = str(page).encode("utf-8")
    
    payload = bytes([HEADER_STM, ctrl]) + attrs
    
    return payload, f"PAGE {page}", {"func": "P", "page": page}


def build_voltage_command(voltage: float) -> tuple:
    """
    Build voltage set command.
    
    Returns:
        (payload_bytes, log_string, metadata)
    """
    value_str = f"{voltage:.2f}"
    ctrl = make_ctrl(STM_SLAVE, NO_ERROR, FUNC_V)
    
    payload = bytes([HEADER_STM, ctrl]) + value_str.encode("utf-8")
    
    return payload, f"VOLT {value_str}V", {"func": "V", "voltage": voltage}


def build_message_command(msg: str) -> tuple:
    """
    Build message command.
    
    Returns:
        (payload_bytes, log_string, metadata)
    """
    msg_bytes = msg.encode("utf-8")
    if len(msg_bytes) > 0xFFFF:
        raise ValueError("Message exceeds maximum length (65535 bytes)")
    
    size_bin = len(msg_bytes).to_bytes(2, LEN_ENDIAN)
    ctrl = make_ctrl(STM_SLAVE, NO_ERROR, FUNC_M)
    
    payload = bytes([HEADER_STM, ctrl]) + size_bin + msg_bytes
    
    return payload, f"MSG \"{msg[:20]}...\"" if len(msg) > 20 else f"MSG \"{msg}\"", {"func": "M", "len": len(msg_bytes)}
