"""
ITECH IT6502D Programmable DC Power Supply Driver (PyVISA via @py backend).
"""
import threading
from typing import Optional, Tuple


class IT6502DPSU:
    """Thread-safe controller for the ITECH IT6502D power supply via USB-TMC SCPI."""

    def __init__(self, resource_name: str, max_current_a: float = 1.5, timeout_ms: int = 5000):
        self.resource_name = resource_name
        self.max_current_a = max_current_a
        self.timeout_ms = timeout_ms
        self.rm = None
        self.inst = None
        self._lock = threading.Lock()

    def connect(self) -> str:
        """Connect to the instrument, verify *IDN?, set current limit, and return model string."""
        import pyvisa as visa

        with self._lock:
            self.rm = visa.ResourceManager("@py")
            self.inst = self.rm.open_resource(self.resource_name)
            self.inst.timeout = self.timeout_ms
            self.inst.read_termination = "\n"
            self.inst.write_termination = "\n"
            idn = self.inst.query("*IDN?").strip()
            self.inst.write(f"CURR {self.max_current_a:.3f}")
            return idn

    def set_voltage(self, voltage_v: float) -> None:
        """Set output voltage setpoint in Volts."""
        with self._lock:
            if self.inst:
                self.inst.write(f"VOLT {voltage_v:.4f}")

    def measure(self) -> Tuple[float, float]:
        """Read measured voltage (V) and current (A)."""
        with self._lock:
            if not self.inst:
                return (0.0, 0.0)
            v_str = self.inst.query("MEAS:VOLT?").strip()
            c_str = self.inst.query("MEAS:CURR?").strip()
            return (float(v_str), float(c_str))

    def enable_output(self, enable: bool = True) -> None:
        """Turn output ON or OFF."""
        with self._lock:
            if self.inst:
                self.inst.write("OUTP ON" if enable else "OUTP OFF")

    def disconnect(self) -> None:
        """Turn output off and release VISA resource."""
        with self._lock:
            try:
                if self.inst:
                    self.inst.write("OUTP OFF")
                    self.inst.close()
                if self.rm:
                    self.rm.close()
            except Exception:
                pass
            self.inst = None
            self.rm = None
