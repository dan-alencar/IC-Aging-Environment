# -*- coding: utf-8 -*-
from protocol import (
    make_ctrl, STM_SLAVE, NO_ERROR, FUNC_P, FUNC_M, FUNC_V, LEN_ENDIAN
)

# Header definido no uart_router.sv
HEADER_STM = 0x20 

def build_page_command(page_val: int) -> tuple[bytes, str, dict]:
    page_val = max(1, min(6, page_val))
    ctrl = make_ctrl(STM_SLAVE, NO_ERROR, FUNC_P)
    attrs = str(page_val).encode("utf-8")
    
    # ADICIONADO: HEADER_STM antes do pacote real
    payload = bytes([HEADER_STM, ctrl]) + attrs
    
    log_str = f"P {page_val}"
    meta = {"func":"P", "attrs": str(page_val), "ctrl": ctrl}
    return payload, log_str, meta

def build_message_command(msg: str) -> tuple[bytes, str, dict]:
    msg_bytes = msg.encode("utf-8")
    if len(msg_bytes) > 0xFFFF:
        raise ValueError("A mensagem excede 65535 bytes.")
    size_bin = len(msg_bytes).to_bytes(2, LEN_ENDIAN)

    ctrl = make_ctrl(STM_SLAVE, NO_ERROR, FUNC_M)
    
    # ADICIONADO: HEADER_STM
    payload = bytes([HEADER_STM, ctrl]) + size_bin + msg_bytes

    size_hex = " ".join(f"0x{x:02X}" for x in size_bin)
    log_str = f"M len={len(msg_bytes)} ({size_hex}) msg=\"{msg}\""
    meta = {"func":"M", "len": len(msg_bytes), "size_hex": size_hex, "ctrl": ctrl}
    return payload, log_str, meta

def build_vcore_command(value: float) -> tuple[bytes, str, dict]:
    value_str = f"{value:.2f}"
    ctrl = make_ctrl(STM_SLAVE, NO_ERROR, FUNC_V)
    
    # ADICIONADO: HEADER_STM
    payload = bytes([HEADER_STM, ctrl]) + value_str.encode("utf-8")
    
    log_str = f"V {value_str}"
    meta = {"func":"V", "attrs": value_str, "ctrl": ctrl}
    return payload, log_str, meta