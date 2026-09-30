"""
Binary protocol decoders for FPGA DUT packets (Nexys4 DDR and Artix-7 targets).
"""
import struct
from typing import NamedTuple, Optional


class NexysPacket15(NamedTuple):
    """
    15-byte packet layout (triggered by byte 'T' / 0x54 at 9600 baud):
    [TEMP×3][SLACK×2][VCCINT×3][FAIL×1][WRONG×2][CORRECT×2][ERR_CNT×2]
    """
    temperature_c: float
    slack_sensor: int
    vccint_v: float
    failure: bool
    wrong: int
    correct: int
    error_count: int


def decode_15byte_packet(data: bytes) -> Optional[NexysPacket15]:
    """
    Parse a 15-byte payload into a structured NexysPacket15.
    Returns None if packet length != 15 or values exceed physical bounds.
    """
    if len(data) != 15:
        return None

    try:
        temp_raw = int.from_bytes(data[0:3], byteorder="little", signed=False)
        slack = int.from_bytes(data[3:5], byteorder="little", signed=False)
        vcc_raw = int.from_bytes(data[5:8], byteorder="little", signed=False)
        fail = bool(data[8])
        wrong = int.from_bytes(data[9:11], byteorder="little", signed=False)
        correct = int.from_bytes(data[11:13], byteorder="little", signed=False)
        err_cnt = int.from_bytes(data[13:15], byteorder="little", signed=False)

        temp_c = temp_raw / 1000.0
        vcc_v = vcc_raw / 1000.0

        # Sanity rejection filter (e.g. transient noise or unprogrammed FPGA)
        if temp_c > 200.0 or vcc_v > 2.5:
            return None

        return NexysPacket15(
            temperature_c=temp_c,
            slack_sensor=slack,
            vccint_v=vcc_v,
            failure=fail,
            wrong=wrong,
            correct=correct,
            error_count=err_cnt,
        )
    except Exception:
        return None
