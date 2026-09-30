"""
Agilent / Keysight E3634A Programmable DC Power Supply Driver (Serial RS-232 / VISA).
"""
import threading
from typing import Tuple


class AgilentE3634APSU:
    """Thread-safe controller for the Agilent E3634A power supply via RS-232 SCPI."""

    def __init__(self, port: str, baudrate: int = 9600, timeout_s: float = 2.0):
        self.port = port
        self.baudrate = baudrate
        self.timeout_s = timeout_s
        self.ser = None
        self._lock = threading.Lock()

    def connect(self) -> str:
        """Open serial connection and query *IDN?."""
        import serial

        with self._lock:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_TWO,
                timeout=self.timeout_s,
            )
            # Remote mode and clear status
            self.ser.write(b"SYST:REM\n")
            self.ser.write(b"*IDN?\n")
            idn = self.ser.readline().decode("ascii", errors="ignore").strip()
            return idn

    def set_voltage(self, voltage_v: float) -> None:
        """Set output voltage setpoint in Volts."""
        with self._lock:
            if self.ser and self.ser.is_open:
                self.ser.write(f"VOLT {voltage_v:.4f}\n".encode("ascii"))

    def measure(self) -> Tuple[float, float]:
        """Read measured voltage (V) and current (A)."""
        with self._lock:
            if not self.ser or not self.ser.is_open:
                return (0.0, 0.0)
            self.ser.write(b"MEAS:VOLT?\n")
            v_str = self.ser.readline().decode("ascii", errors="ignore").strip()
            self.ser.write(b"MEAS:CURR?\n")
            c_str = self.ser.readline().decode("ascii", errors="ignore").strip()
            return (float(v_str), float(c_str))

    def enable_output(self, enable: bool = True) -> None:
        """Turn output ON or OFF."""
        with self._lock:
            if self.ser and self.ser.is_open:
                self.ser.write(b"OUTP ON\n" if enable else b"OUTP OFF\n")

    def disconnect(self) -> None:
        """Turn output off and close serial port."""
        with self._lock:
            try:
                if self.ser and self.ser.is_open:
                    self.ser.write(b"OUTP OFF\n")
                    self.ser.write(b"SYST:LOC\n")
                    self.ser.close()
            except Exception:
                pass
            self.ser = None
