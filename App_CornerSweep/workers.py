"""
Hardware workers for App_CornerSweep.

Three independent workers run in QThread via QObject + QTimer polling:
  ArduinoWorker  — oven PID control (optional)
  PSUWorker      — Agilent E3634A voltage/current control via RS-232 (required)
  DUTWorker      — FPGA 15-byte packet reader at 9600 baud

The CornerSweepSequencer (corner_sequencer.py) reads the latest data from each
worker via thread-safe getter methods.
"""
import threading
import time

import serial
from PySide6.QtCore import QObject, QTimer, Signal, Slot

import config


# ── Worker 1: Arduino (oven PID) ─────────────────────────────────────────────

class ArduinoWorker(QObject):
    log_message = Signal(str)
    data_ready  = Signal(float, float, float)   # temp, setpoint, output%

    def __init__(self):
        super().__init__()
        self.ser          = None
        self.is_running   = False
        self.is_ready     = False
        self._latest_data = (0.0, 0.0, 0.0)
        self._lock        = threading.Lock()

    @Slot()
    def start(self):
        if not config.ARDUINO_ENABLED or not config.ARDUINO_PORT:
            self.log_message.emit("Arduino desabilitado — controle de forno inativo.")
            return
        try:
            self.ser = serial.Serial(config.ARDUINO_PORT, config.ARDUINO_BAUD, timeout=2)
            self.log_message.emit("Arduino conectado. Aguardando boot (3 s)...")
            time.sleep(3.0)
            with self._lock:
                self.ser.reset_input_buffer()
                self.ser.reset_output_buffer()
                while self.ser.in_waiting:
                    self.ser.readline()
            self.log_message.emit(f"Arduino pronto em {config.ARDUINO_PORT}")
            self.is_running = True
            self.is_ready   = True
            self._timer = QTimer(self)
            self._timer.setInterval(config.LOG_INTERVAL_MS)
            self._timer.timeout.connect(self._poll)
            self._timer.start()
        except serial.SerialException as e:
            self.log_message.emit(f"ERRO (Arduino): {e}")
            self.is_ready = False

    @Slot()
    def stop(self):
        self.is_running = False
        if hasattr(self, '_timer'):
            self._timer.stop()
        with self._lock:
            if self.ser and self.ser.is_open:
                try:
                    self.ser.write(b"STOP_TEST\n")
                except Exception:
                    pass
                self.ser.close()
        self.log_message.emit("Arduino desconectado.")

    def _poll(self):
        if not self.is_running:
            return
        with self._lock:
            try:
                if self.ser and self.ser.is_open:
                    self.ser.write(b"GET_DATA\n")
                    line = self.ser.readline().decode('ascii', errors='ignore').strip()
                    if line.startswith("DATA,"):
                        parts = line.split(',')
                        temp_c, sp_c, out_pct = float(parts[1]), float(parts[2]), float(parts[3])
                        self._latest_data = (temp_c, sp_c, out_pct)
                        self.data_ready.emit(temp_c, sp_c, out_pct)
            except Exception as e:
                self.log_message.emit(f"Erro leitura Arduino: {e}")

    def get_latest_data(self):
        return self._latest_data

    def _send(self, cmd: str):
        try:
            with self._lock:
                if self.ser and self.ser.is_open:
                    self.ser.reset_input_buffer()
                    self.ser.write(f"{cmd}\n".encode('ascii'))
                    return self.ser.readline().decode('ascii', errors='ignore').strip()
        except Exception as e:
            self.log_message.emit(f"ERRO cmd '{cmd}': {e}")
        return None

    @Slot(float)
    def set_target_setpoint(self, temp: float):
        return self._send(f"SET_SP,{int(temp)}")

    def start_test_oven(self):
        return self._send("START_TEST")

    def stop_test_oven(self):
        return self._send("STOP_TEST")


# ── Worker 2: PSU — Agilent E3634A via RS-232 ────────────────────────────────

class PSUWorker(QObject):
    log_message = Signal(str)
    data_ready  = Signal(float, float)  # voltage_v, current_a

    def __init__(self):
        super().__init__()
        self.ser          = None
        self.is_running   = False
        self._latest_data = (0.0, 0.0)
        self._lock        = threading.Lock()

    def _query(self, cmd: str) -> str:
        with self._lock:
            self.ser.reset_input_buffer()
            self.ser.write(f"{cmd}\r\n".encode())
            return self.ser.readline().decode(errors='replace').strip()

    def _write(self, cmd: str):
        with self._lock:
            self.ser.write(f"{cmd}\r\n".encode())

    @Slot()
    def start(self):
        if not config.PSU_ENABLED or not config.PSU_PORT:
            self.log_message.emit("PSU desabilitada.")
            return
        try:
            self.ser = serial.Serial(
                config.PSU_PORT, config.PSU_BAUD,
                stopbits=serial.STOPBITS_TWO, timeout=3,
            )
            time.sleep(0.1)
            self.ser.reset_input_buffer()
            self._write("*CLS")
            time.sleep(0.1)
            idn = self._query("*IDN?")
            self.log_message.emit(f"PSU conectada: {idn}")
            self._write(f"CURR {config.MAX_PSU_CURRENT_A:.3f}")
            self._write("SYSTEM:BEEPER:STATE OFF")
            self.is_running = True
            self._timer = QTimer(self)
            self._timer.setInterval(config.LOG_INTERVAL_MS)
            self._timer.timeout.connect(self._poll)
            self._timer.start()
        except Exception as e:
            self.log_message.emit(f"ERRO PSU: {e}")

    @Slot()
    def stop(self):
        self.is_running = False
        if hasattr(self, '_timer'):
            self._timer.stop()
        try:
            if self.ser and self.ser.is_open:
                self._write("OUTP OFF")
                self.ser.close()
        except Exception:
            pass
        self.log_message.emit("PSU desconectada.")

    def _poll(self):
        if not self.is_running or not self.ser:
            return
        try:
            v = self._query("MEAS:VOLT?")
            time.sleep(0.05)
            c = self._query("MEAS:CURR?")
            if v and c:
                self._latest_data = (float(v), float(c))
                self.data_ready.emit(*self._latest_data)
        except ValueError:
            pass
        except Exception as e:
            self.log_message.emit(f"Erro leitura PSU: {e}")

    def get_latest_data(self):
        return self._latest_data

    @Slot(float)
    def set_voltage(self, voltage_v: float):
        if self.ser and self.ser.is_open:
            try:
                self._write(f"VOLT {voltage_v:.4f}")
            except Exception as e:
                self.log_message.emit(f"ERRO tensão PSU: {e}")

    @Slot()
    def turn_on(self):
        if self.ser and self.ser.is_open:
            try:
                self._write("OUTP ON")
                self.log_message.emit("PSU: saída LIGADA")
            except Exception as e:
                self.log_message.emit(f"ERRO ligar PSU: {e}")

    @Slot()
    def turn_off(self):
        if self.ser and self.ser.is_open:
            try:
                self._write("OUTP OFF")
                self.log_message.emit("PSU: saída DESLIGADA")
            except Exception as e:
                self.log_message.emit(f"ERRO desligar PSU: {e}")


# ── Worker 3: DUT — FPGA Nexys4 DDR (15-byte packet) ────────────────────────

class DUTWorker(QObject):
    """
    Polls the FPGA at LOG_INTERVAL_MS by sending 'T' (0x54) and reading the
    15-byte Little-Endian response:
      [TEMP×3][SLACK×2][VCCINT×3][FAIL×1][WRONG×2][CORRECT×2][ERR_CNT×2]

    Temperature and VCCINT are raw / 1000 to get °C and V respectively.
    DUT_BAUD must be 9600.
    """
    log_message = Signal(str)
    data_ready  = Signal(float, int, float)  # temp_c, slack, vccint_v

    _PACKET = 15

    def __init__(self):
        super().__init__()
        self.ser          = None
        self.is_running   = False
        self._latest_data = (0.0, 0, 0.0, 0, 0, 0, 0)
        self._timer = QTimer(self)
        self._timer.setInterval(config.LOG_INTERVAL_MS)
        self._timer.timeout.connect(self._poll)

    @Slot()
    def start(self):
        try:
            self.ser = serial.Serial(config.DUT_PORT, config.DUT_BAUD, timeout=2)
            self.log_message.emit(f"DUT conectado em {config.DUT_PORT} @ {config.DUT_BAUD}")
            self.is_running = True
            self._timer.start()
        except serial.SerialException as e:
            self.log_message.emit(f"ERRO DUT: {e}")

    @Slot()
    def stop(self):
        self.is_running = False
        self._timer.stop()
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.log_message.emit("DUT desconectado.")

    def _poll(self):
        if not self.is_running or not self.ser or not self.ser.is_open:
            return
        try:
            self.ser.reset_input_buffer()
            self.ser.write(b'\x54')  # 'T'
            data = self.ser.read(self._PACKET)

            if len(data) != self._PACKET:
                if not data:
                    print(f"DUT: timeout — baud {config.DUT_BAUD} correto?")
                return

            raw_temp  = int.from_bytes(data[0:3],   'little')
            raw_slack = int.from_bytes(data[3:5],   'little')
            raw_vcc   = int.from_bytes(data[5:8],   'little')
            raw_fail  = int(data[8])
            raw_wrong = int.from_bytes(data[9:11],  'little')
            raw_corr  = int.from_bytes(data[11:13], 'little')
            raw_err   = int.from_bytes(data[13:15], 'little')

            temp_c = raw_temp  / 1000.0
            vcc_v  = raw_vcc   / 1000.0
            slack  = int(raw_slack)

            # Discard zeroed boot packets
            if temp_c == 0 and slack == 0 and vcc_v == 0:
                return
            # Discard obviously invalid boot transients
            if temp_c > 200 or vcc_v > 2.5:
                return

            self._latest_data = (temp_c, slack, vcc_v, raw_fail, raw_wrong, raw_corr, raw_err)
            self.data_ready.emit(temp_c, slack, vcc_v)

        except Exception as e:
            self.log_message.emit(f"ERRO DUT: {e}")

    def get_latest_data(self):
        """Returns (temp_c, slack, vccint_v, fail, wrong, correct, error_count)."""
        return self._latest_data
