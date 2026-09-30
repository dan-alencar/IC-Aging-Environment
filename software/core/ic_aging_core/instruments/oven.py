"""
Thermal Chamber (Oven) Controller Communication Driver (Arduino / ESP32).
"""
import threading
from typing import Optional, Tuple, Dict, Any


class OvenController:
    """Thread-safe serial interface to the Arduino/ESP oven temperature controller."""

    def __init__(self, port: str, baudrate: int = 115200, timeout_s: float = 1.0):
        self.port = port
        self.baudrate = baudrate
        self.timeout_s = timeout_s
        self.ser = None
        self._lock = threading.Lock()

    def connect(self) -> bool:
        """Open serial port."""
        import serial

        with self._lock:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout_s)
            return self.ser.is_open

    def poll_data(self) -> Optional[Tuple[float, float, float]]:
        """
        Request current readings via 'GET_DATA\\n'.
        Returns (temp_c, setpoint_c, duty_pct) or None if timeout/error.
        """
        with self._lock:
            if not self.ser or not self.ser.is_open:
                return None
            try:
                self.ser.write(b"GET_DATA\n")
                line = self.ser.readline().decode("ascii", errors="ignore").strip()
                if line.startswith("DATA,"):
                    parts = line.split(",")
                    return (float(parts[1]), float(parts[2]), float(parts[3]))
            except Exception:
                pass
            return None

    def query_config(self) -> Dict[str, Any]:
        """
        Send 'GET_CONFIG\\n' to identify controller firmware (PID vs bang-bang)
        and fetch active parameters.
        """
        with self._lock:
            if not self.ser or not self.ser.is_open:
                return {"type": "disconnected"}
            try:
                self.ser.reset_input_buffer()
                self.ser.write(b"GET_CONFIG\n")
                line = self.ser.readline().decode("ascii", errors="ignore").strip()
                if not line:
                    return {"type": "unknown", "raw": ""}
                
                info: Dict[str, Any] = {"raw": line}
                if "PID" in line:
                    info["type"] = "PID"
                elif "TERMOSTATO" in line or "BANG" in line.upper():
                    info["type"] = "BANG_BANG"
                else:
                    info["type"] = "CUSTOM"
                return info
            except Exception as e:
                return {"type": "error", "error": str(e)}

    def set_setpoint(self, temp_c: float) -> bool:
        """Set temperature setpoint."""
        return self._send_cmd(f"SET_SP,{temp_c:.1f}")

    def stop_test(self) -> bool:
        """Emergency stop / disable heating."""
        return self._send_cmd("STOP_TEST")

    def _send_cmd(self, cmd: str) -> bool:
        with self._lock:
            if not self.ser or not self.ser.is_open:
                return False
            try:
                self.ser.reset_input_buffer()
                self.ser.write(f"{cmd}\n".encode("ascii"))
                resp = self.ser.readline().decode("ascii", errors="ignore").strip()
                return "OK" in resp
            except Exception:
                return False

    def disconnect(self) -> None:
        """Send STOP_TEST and close connection."""
        with self._lock:
            try:
                if self.ser and self.ser.is_open:
                    self.ser.write(b"STOP_TEST\n")
                    self.ser.close()
            except Exception:
                pass
            self.ser = None
