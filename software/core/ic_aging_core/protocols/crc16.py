"""
CRC16-Modbus implementation for STM32 and microcontroller supervisory framing.
"""


def compute_crc16_modbus(data: bytes) -> int:
    """
    Compute CRC16-Modbus (polynomial 0xA001, initial value 0xFFFF).
    Returns 16-bit integer.
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


def verify_crc16_frame(frame: bytes) -> bool:
    """Verify that a frame ending in a 2-byte little-endian CRC16-Modbus is valid."""
    if len(frame) < 3:
        return False
    payload = frame[:-2]
    expected_crc = int.from_bytes(frame[-2:], byteorder="little")
    return compute_crc16_modbus(payload) == expected_crc
