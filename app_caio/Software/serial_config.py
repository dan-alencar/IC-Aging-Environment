# -*- coding: utf-8 -*-
import threading
import serial
from PySide6.QtCore import Qt, QThread, Signal, Slot

class SerialThread(QThread):
    data = Signal(bytes)
    info = Signal(str)
    error = Signal(str)
    opened = Signal(str)
    closed = Signal()

    write_bytes = Signal(bytes)
    set_baud = Signal(int)
    set_rts = Signal(bool)
    set_dtr = Signal(bool)

    def __init__(self, port: str, baudrate: int, parity: str = 'N',
                 stopbits: int = 1, bytesize: int = 8,
                 rts: bool = True, dtr: bool = True):
        super().__init__()
        self._port = port
        self._baudrate = baudrate
        self._parity = parity
        self._stopbits = stopbits
        self._bytesize = bytesize
        self._want_rts = rts
        self._want_dtr = dtr

        self._ser: serial.Serial | None = None
        self._running = threading.Event()
        self._running.clear()

        self.write_bytes.connect(self._on_write, Qt.QueuedConnection)
        self.set_baud.connect(self._on_set_baud, Qt.QueuedConnection)
        self.set_rts.connect(self._on_set_rts, Qt.QueuedConnection)
        self.set_dtr.connect(self._on_set_dtr, Qt.QueuedConnection)

    def run(self):
        try:
            self._ser = serial.Serial(
                port=self._port,
                baudrate=self._baudrate,
                bytesize=self._translate_bytesize(self._bytesize),
                parity=self._translate_parity(self._parity),
                stopbits=self._translate_stopbits(self._stopbits),
                timeout=0.05,
                write_timeout=6,
                xonxoff=False,
                rtscts=False,
                dsrdtr=False
            )
            try:
                self._ser.setRTS(self._want_rts)
                self._ser.setDTR(self._want_dtr)
            except Exception:
                pass
            try:
                self._ser.reset_input_buffer()
                self._ser.reset_output_buffer()
            except Exception:
                pass
        except Exception as e:
            self.error.emit(f"Falha ao abrir {self._port}: {e}")
            return

        self._running.set()
        self.opened.emit(self._port)
        self.info.emit(f"Porta aberta: {self._port} @ {self._baudrate} bps")

        try:
            while self._running.is_set():
                try:
                    if self._ser and self._ser.in_waiting:
                        chunk = self._ser.read(self._ser.in_waiting)
                        if chunk:
                            self.data.emit(chunk)
                    else:
                        self.msleep(10)
                except Exception as re:
                    self.error.emit(f"Erro de leitura: {re}")
                    break
        finally:
            try:
                if self._ser and self._ser.is_open:
                    self._ser.close()
            except Exception:
                pass
            self.closed.emit()

    def stop(self):
        self._running.clear()

    @Slot(bytes)
    def _on_write(self, payload: bytes):
        try:
            if self._ser and self._ser.is_open:
                self._ser.write(payload)
                self._ser.flush()
            else:
                self.error.emit("Porta serial não está aberta.")
        except Exception as e:
            self.error.emit(f"Erro de escrita: {e}")

    @Slot(int)
    def _on_set_baud(self, baud: int):
        try:
            if self._ser and self._ser.is_open:
                self._ser.baudrate = baud
                self.info.emit(f"Baudrate trocado para {baud}")
        except Exception as e:
            self.error.emit(f"Falha ao trocar baudrate: {e}")

    @Slot(bool)
    def _on_set_rts(self, val: bool):
        try:
            if self._ser and self._ser.is_open:
                self._ser.setRTS(val)
                self.info.emit(f"RTS={'ON' if val else 'OFF'}")
        except Exception as e:
            self.error.emit(f"Falha ao setar RTS: {e}")

    @Slot(bool)
    def _on_set_dtr(self, val: bool):
        try:
            if self._ser and self._ser.is_open:
                self._ser.setDTR(val)
                self.info.emit(f"DTR={'ON' if val else 'OFF'}")
        except Exception as e:
            self.error.emit(f"Falha ao setar DTR: {e}")

    @staticmethod
    def _translate_parity(p: str):
        import serial as _s
        return {
            'N': _s.PARITY_NONE, 'E': _s.PARITY_EVEN, 'O': _s.PARITY_ODD,
            'M': _s.PARITY_MARK, 'S': _s.PARITY_SPACE
        }.get(p.upper(), _s.PARITY_NONE)

    @staticmethod
    def _translate_stopbits(s: int):
        import serial as _s
        return {1: _s.STOPBITS_ONE, 2: _s.STOPBITS_TWO}.get(int(s), _s.STOPBITS_ONE)

    @staticmethod
    def _translate_bytesize(b: int):
        import serial as _s
        return {5: _s.FIVEBITS, 6: _s.SIXBITS, 7: _s.SEVENBITS, 8: _s.EIGHTBITS}.get(int(b), _s.EIGHTBITS)
