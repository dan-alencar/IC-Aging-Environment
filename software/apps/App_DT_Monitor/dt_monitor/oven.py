"""Driver for the oven controller firmware 2.0 (firmware/thermal_chamber/SAFETY.md), as an
fbs-service oven plugin (entry point fbs.ovens = ic_aging_oven).

The protocol is ASCII lines, every command answered: SET_SP,<c> -> OK,SP_SET | ERR,RANGE;
START_TEST -> OK,TEST_STARTED (+ INFO,PID_CONFIG,...) | ERR,FAULT | ERR,NO_READING;
STOP_TEST -> OK,TEST_STOPPED; GET_DATA -> DATA,t,sp,out,state,fault[,cutoff];
GET_CONFIG -> CONFIG,...; SET_HOST_TIMEOUT,<min> -> OK,HOSTTO; CLEAR_FAULT -> OK,FAULT_CLEARED |
ERR,ACTIVE. Unsolicited EVENT,FAULT,<name> lines can come at any time and are kept in
`events`. Firmware 1.x answers DATA with four fields and SET_SP/START with plain OK; both work.
"""
from __future__ import annotations

import threading
import time
from typing import Callable, List, Optional

from fpgaging_bsp.service.oven import OvenClient, OvenError, OvenReading, parse_data

BAUD = 115200


class AsciiOven(OvenClient):
    def __init__(self, port: str = "", baud: int = BAUD, timeout_s: float = 2.0, transport=None,
                 on_event: Optional[Callable[[str], None]] = None):
        if transport is None:
            import serial
            transport = serial.Serial(port, baud, timeout=0.05)
            time.sleep(2.0)            # the Arduino resets when the port opens
            transport.reset_input_buffer()
        self.t = transport
        self.timeout_s = timeout_s
        self.on_event = on_event
        self.events: List[str] = []
        self._lock = threading.Lock()
        self._buf = b""

    def _readline(self, deadline: float) -> Optional[str]:
        while time.monotonic() < deadline:
            i = self._buf.find(b"\n")
            if i >= 0:
                line, self._buf = self._buf[:i], self._buf[i + 1:]
                return line.decode("ascii", "replace").strip()
            self._buf += self.t.read(64)
        return None

    def command(self, cmd: str, expect: tuple) -> str:
        """Send one line and return the first reply that starts with one of `expect`."""
        with self._lock:
            self.t.write((cmd + "\n").encode("ascii"))
            deadline = time.monotonic() + self.timeout_s
            while True:
                line = self._readline(deadline)
                if line is None:
                    raise OvenError(f"{cmd}: no reply")
                if line.startswith("EVENT,"):
                    self.events.append(line)
                    if self.on_event:
                        self.on_event(line)
                    continue
                if line.startswith(expect):
                    return line
                if line.startswith("ERR"):
                    raise OvenError(f"{cmd}: {line}")
                # INFO,... and other chatter: keep waiting for the answer

    def get_data(self) -> OvenReading:
        return parse_data(self.command("GET_DATA", ("DATA,",)))

    def get_config(self) -> str:
        return self.command("GET_CONFIG", ("CONFIG,",))

    def set_setpoint(self, c: float) -> None:
        self.command(f"SET_SP,{c:.1f}", ("OK",))

    def start(self) -> None:
        self.command("START_TEST", ("OK",))

    def stop(self) -> None:
        self.command("STOP_TEST", ("OK",))

    def set_host_timeout(self, minutes: int) -> None:
        self.command(f"SET_HOST_TIMEOUT,{int(minutes)}", ("OK",))

    def clear_fault(self) -> None:
        self.command("CLEAR_FAULT", ("OK",))

    def close(self) -> None:
        try:
            self.t.close()
        except Exception:
            pass


def oven(port: str = "", baud: int = BAUD, **kw) -> AsciiOven:
    """Entry-point target (fbs.ovens: ic_aging_oven); the bench file gives port and baud."""
    return AsciiOven(port, baud, **kw)
