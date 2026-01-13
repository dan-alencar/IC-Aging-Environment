# -*- coding: utf-8 -*-
"""
Serial Communication Thread

Thread-safe serial port communication with Qt signals.
Cross-platform support for Windows and Linux.
"""

import threading
import serial
from serial.tools import list_ports
from PySide6.QtCore import QThread, Signal, Slot, Qt


def get_available_ports():
    """
    Get list of available serial ports.
    
    Returns:
        List of tuples: (port_name, description)
    """
    ports = []
    for port in list_ports.comports():
        ports.append((port.device, port.description))
    return ports


class SerialThread(QThread):
    """
    Thread for serial port communication.
    
    Signals:
        data_received(bytes): Data received from port
        port_opened(str): Port successfully opened
        port_closed(): Port closed
        error_occurred(str): Error message
        info_message(str): Informational message
    """
    
    data_received = Signal(bytes)
    port_opened = Signal(str)
    port_closed = Signal()
    error_occurred = Signal(str)
    info_message = Signal(str)

    def __init__(self, port: str, baudrate: int, 
                 parity: str = 'N', stopbits: int = 1, bytesize: int = 8,
                 rts: bool = True, dtr: bool = True, parent=None):
        super().__init__(parent)
        
        self._port = port
        self._baudrate = baudrate
        self._parity = parity
        self._stopbits = stopbits
        self._bytesize = bytesize
        self._want_rts = rts
        self._want_dtr = dtr

        self._serial: serial.Serial = None
        self._running = threading.Event()
        self._running.clear()
        
        self._write_lock = threading.Lock()
        self._write_queue = []

    def run(self):
        """Main thread loop - handles reading from serial port."""
        try:
            self._serial = serial.Serial(
                port=self._port,
                baudrate=self._baudrate,
                bytesize=self._translate_bytesize(self._bytesize),
                parity=self._translate_parity(self._parity),
                stopbits=self._translate_stopbits(self._stopbits),
                timeout=0.05,
                write_timeout=5,
                xonxoff=False,
                rtscts=False,
                dsrdtr=False
            )
            
            # Set control lines
            try:
                self._serial.setRTS(self._want_rts)
                self._serial.setDTR(self._want_dtr)
            except Exception:
                pass
            
            # Clear buffers
            try:
                self._serial.reset_input_buffer()
                self._serial.reset_output_buffer()
            except Exception:
                pass
                
        except Exception as e:
            self.error_occurred.emit(f"Failed to open {self._port}: {e}")
            return

        self._running.set()
        self.port_opened.emit(self._port)
        self.info_message.emit(f"Port opened: {self._port} @ {self._baudrate} bps")

        try:
            while self._running.is_set():
                # Process write queue
                with self._write_lock:
                    while self._write_queue:
                        data = self._write_queue.pop(0)
                        try:
                            if self._serial and self._serial.is_open:
                                self._serial.write(data)
                                self._serial.flush()
                        except Exception as e:
                            self.error_occurred.emit(f"Write error: {e}")
                
                # Read available data
                try:
                    if self._serial and self._serial.in_waiting:
                        chunk = self._serial.read(self._serial.in_waiting)
                        if chunk:
                            self.data_received.emit(chunk)
                    else:
                        self.msleep(10)
                except Exception as e:
                    self.error_occurred.emit(f"Read error: {e}")
                    break
                    
        finally:
            try:
                if self._serial and self._serial.is_open:
                    self._serial.close()
            except Exception:
                pass
            self.port_closed.emit()

    def stop(self):
        """Stop the serial thread."""
        self._running.clear()

    def write_data(self, data: bytes):
        """
        Queue data for writing to serial port.
        Thread-safe.
        """
        with self._write_lock:
            self._write_queue.append(data)

    def set_baudrate(self, baud: int):
        """Change the baud rate."""
        try:
            if self._serial and self._serial.is_open:
                self._serial.baudrate = baud
                self.info_message.emit(f"Baudrate changed to {baud}")
        except Exception as e:
            self.error_occurred.emit(f"Failed to change baudrate: {e}")

    def set_rts(self, value: bool):
        """Set RTS line state."""
        try:
            if self._serial and self._serial.is_open:
                self._serial.setRTS(value)
        except Exception as e:
            self.error_occurred.emit(f"Failed to set RTS: {e}")

    def set_dtr(self, value: bool):
        """Set DTR line state."""
        try:
            if self._serial and self._serial.is_open:
                self._serial.setDTR(value)
        except Exception as e:
            self.error_occurred.emit(f"Failed to set DTR: {e}")

    @staticmethod
    def _translate_parity(p: str):
        return {
            'N': serial.PARITY_NONE,
            'E': serial.PARITY_EVEN,
            'O': serial.PARITY_ODD,
            'M': serial.PARITY_MARK,
            'S': serial.PARITY_SPACE
        }.get(p.upper(), serial.PARITY_NONE)

    @staticmethod
    def _translate_stopbits(s: int):
        return {
            1: serial.STOPBITS_ONE,
            2: serial.STOPBITS_TWO
        }.get(int(s), serial.STOPBITS_ONE)

    @staticmethod
    def _translate_bytesize(b: int):
        return {
            5: serial.FIVEBITS,
            6: serial.SIXBITS,
            7: serial.SEVENBITS,
            8: serial.EIGHTBITS
        }.get(int(b), serial.EIGHTBITS)
