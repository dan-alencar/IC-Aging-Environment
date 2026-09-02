"""
App_2Nexys — Hardware workers.

Workers (all run in QThread via QObject + QTimer polling):
  ArduinoWorker  — shared oven PID controller over serial (unchanged from App_Nexys)
  PSUWorker      — one SCPI PSU per DUT (IT6502D for DUT0, E3634A for DUT1)
  DUTWorker      — one Nexys4 DDR FPGA per slot; protocol: send 'F', read 15 binary bytes
  TestSequencer  — orchestrates all workers, runs VCCINT closed-loop, writes CSV

VCCINT loop (per DUT, runs every log tick):
  error = vccint_setpoint - measured_vccint_from_xadc
  psu_cmd += VOLTAGE_KP * error        # P-only trim
  psu_cmd  = clamp(psu_cmd, PSU_MIN_V, PSU_MAX_V)
  psu.set_voltage(psu_cmd)
"""
from PySide6.QtCore import QObject, Signal, Slot, QTimer
import serial
import time
import os
import subprocess
import tempfile
from datetime import datetime
import config
import pyvisa as visa
from logger import DataLogger
from protocol import MULTI_NUM_CHANNELS, MULTI_PKT_LEN, parse_multi_sensor_packet
import threading

_DUT_OUTER_TICK_INTERVAL = 1800   # ticks between oven-sp adjustments (~30 min at 1 s/tick)
_DUT_TEMP_TOLERANCE_C = 3.0       # ±3 °C dead-band around DUT target
_OVEN_SP_STEP_C = 1.0             # °C per adjustment step


# =============================================================================
#   ArduinoWorker — shared oven PID (identical to App_Nexys)
# =============================================================================
class ArduinoWorker(QObject):
    log_message = Signal(str)
    data_ready = Signal(float, float, float)  # temp, setpoint, output

    def __init__(self):
        super().__init__()
        self.ser = None
        self.is_running = False
        self.is_ready = False
        self._latest_data = (0.0, 0.0, 0.0)
        self.serial_lock = threading.Lock()

    @Slot()
    def start(self):
        if not config.ARDUINO_ENABLED or not config.ARDUINO_PORT:
            self.log_message.emit("Arduino desabilitado — controle de forno inativo.")
            return
        try:
            self.ser = serial.Serial(config.ARDUINO_PORT, config.ARDUINO_BAUD, timeout=2)
            self.log_message.emit("Arduino conectado. Aguardando boot (3s)...")
            time.sleep(3.0)
            with self.serial_lock:
                self.ser.reset_input_buffer()
                self.ser.reset_output_buffer()
                while self.ser.in_waiting:
                    self.ser.readline()
            self.is_running = True
            self.is_ready = True
            self.log_message.emit(f"Arduino pronto em {config.ARDUINO_PORT}")
            self.log_message.emit(f"Parâmetros PID fixos: {config.get_pid_info_string()}")
            self.poll_timer = QTimer(self)
            self.poll_timer.setInterval(config.LOG_INTERVAL_MS)
            self.poll_timer.timeout.connect(self.poll_data)
            self.poll_timer.start()
        except serial.SerialException as e:
            self.log_message.emit(f"ERRO (Arduino): {e}")
            self.is_ready = False

    @Slot()
    def stop(self):
        self.is_running = False
        if hasattr(self, "poll_timer"):
            self.poll_timer.stop()
        with self.serial_lock:
            if self.ser and self.ser.is_open:
                try:
                    self.ser.write(b"STOP_TEST\n")
                except Exception:
                    pass
                self.ser.close()
        self.log_message.emit("Arduino desconectado.")

    def poll_data(self):
        if not self.is_running:
            return
        with self.serial_lock:
            try:
                if self.ser and self.ser.is_open:
                    self.ser.write(b"GET_DATA\n")
                    line = self.ser.readline().decode("ascii", errors="ignore").strip()
                    if line.startswith("DATA,"):
                        parts = line.split(",")
                        t, sp, out = float(parts[1]), float(parts[2]), float(parts[3])
                        self._latest_data = (t, sp, out)
                        self.data_ready.emit(t, sp, out)
            except Exception as e:
                self.log_message.emit(f"Erro leitura Arduino: {e}")

    def get_latest_data(self):
        return self._latest_data

    def send_command(self, cmd):
        with self.serial_lock:
            try:
                if self.ser and self.ser.is_open:
                    self.ser.reset_input_buffer()
                    self.ser.write(f"{cmd}\n".encode("ascii"))
                    return self.ser.readline().decode("ascii", errors="ignore").strip()
            except Exception as e:
                self.log_message.emit(f"ERRO cmd '{cmd}': {e}")
        return None

    @Slot(float)
    def set_target_setpoint(self, temp):
        self.send_command(f"SET_SP,{int(temp)}")

    @Slot()
    def start_test_oven(self):
        self.send_command("START_TEST")

    @Slot()
    def stop_test_oven(self):
        self.send_command("STOP_TEST")


# =============================================================================
#   PSUWorker0 — IT6502D via USB-TMC VISA  (mirrors App_Nexys PSUWorker exactly)
# =============================================================================
class PSUWorker0(QObject):
    log_message = Signal(str)
    data_ready = Signal(float, float)  # voltage_v, current_a

    def __init__(self):
        super().__init__()
        self.rm = None
        self.inst = None
        self.is_running = False
        self._latest_data = (0.0, 0.0)
        self._lock = threading.Lock()

        self.poll_timer = QTimer(self)
        self.poll_timer.setInterval(config.LOG_INTERVAL_MS)
        self.poll_timer.timeout.connect(self.poll_data)

    @Slot()
    def start(self):
        if not config.PSU_0_ENABLED or not config.PSU_0_PORT:
            self.log_message.emit("PSU-0 desabilitada.")
            return
        try:
            self.rm = visa.ResourceManager("@py")
            self.inst = self.rm.open_resource(config.PSU_0_PORT)
            self.inst.timeout = 5000
            self.inst.read_termination = "\n"
            self.inst.write_termination = "\n"
            idn = self.inst.query("*IDN?").strip()
            self.log_message.emit(f"PSU-0 (IT6502D) conectada: {idn}")
            self.inst.write(f"CURR {config.MAX_PSU_CURRENT_A}")
            self.is_running = True
            self.poll_timer.start()
        except Exception as e:
            self.log_message.emit(f"ERRO (PSU-0): {e}")

    @Slot()
    def stop(self):
        self.is_running = False
        self.poll_timer.stop()
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
        self.log_message.emit("PSU-0 desconectada.")

    def poll_data(self):
        if not self.is_running or not self.inst:
            return
        try:
            with self._lock:
                if not self.inst:
                    return
                voltage = float(self.inst.query("MEAS:VOLT?").strip())
                current = float(self.inst.query("MEAS:CURR?").strip())
            self._latest_data = (voltage, current)
            self.data_ready.emit(voltage, current)
        except Exception as e:
            self.log_message.emit(f"Erro leitura PSU-0: {e}")
            self._try_reconnect()

    def _try_reconnect(self):
        """Close and reopen the VISA resource after a USB disruption (e.g. Vivado JTAG).
        Runs entirely in PSUWorker0's thread (called from poll_data timer callback)."""
        with self._lock:
            try:
                if self.inst: self.inst.close()
                if self.rm: self.rm.close()
            except Exception:
                pass
            self.inst = None
            self.rm = None
        time.sleep(2)    # wait for USB re-enumeration, outside the lock
        try:
            with self._lock:
                self.rm = visa.ResourceManager("@py")
                self.inst = self.rm.open_resource(config.PSU_0_PORT)
                self.inst.timeout = 5000
                self.inst.read_termination = "\n"
                self.inst.write_termination = "\n"
                _ = self.inst.query("*IDN?").strip()
            self.log_message.emit("PSU-0: reconectada.")
        except Exception as e:
            self.log_message.emit(f"PSU-0: falha na reconexão ({e}), tentará novamente.")
            with self._lock:
                self.inst = None

    def get_latest_data(self):
        return self._latest_data

    @Slot(float)
    def set_voltage(self, voltage_v: float):
        with self._lock:
            if not self.inst:
                return
            try:
                self.inst.write(f"VOLT {voltage_v:.4f}")
            except Exception as e:
                self.log_message.emit(f"ERRO tensão PSU-0: {e}")

    @Slot()
    def turn_on(self):
        with self._lock:
            if not self.inst:
                return
            try:
                self.inst.write("OUTP ON")
            except Exception as e:
                self.log_message.emit(f"ERRO ligar PSU-0: {e}")
                return
        self.log_message.emit("PSU-0: saída LIGADA")

    @Slot()
    def turn_off(self):
        with self._lock:
            if not self.inst:
                return
            try:
                self.inst.write("OUTP OFF")
            except Exception as e:
                self.log_message.emit(f"ERRO desligar PSU-0: {e}")
                return
        self.log_message.emit("PSU-0: saída DESLIGADA")

    @Slot(bool)
    def set_beeper(self, enabled: bool):
        with self._lock:
            if not self.inst:
                return
            try:
                self.inst.write(f"SYSTEM:BEEPER:STATE {'ON' if enabled else 'OFF'}")
                self.log_message.emit(f"PSU-0: buzzer {'LIGADO' if enabled else 'DESLIGADO'}")
            except Exception as e:
                self.log_message.emit(f"ERRO buzzer PSU-0: {e}")


class PSUWorker1(QObject):
    """Agilent E3634A — DUT 1, RS-232 via Prolific USB-Serial adapter (ttyUSB)."""
    log_message = Signal(str)
    data_ready = Signal(float, float)  # voltage_v, current_a

    def __init__(self):
        super().__init__()
        self._id = "PSU-1 (E3634A)"
        self.ser = None
        self.is_running = False
        self._latest_data = (0.0, 0.0)
        self._lock = threading.Lock()

    def _query(self, cmd: str) -> str:
        with self._lock:
            self.ser.reset_input_buffer()   # discard any stale/unsolicited bytes
            self.ser.write(f"{cmd}\r\n".encode())
            return self.ser.readline().decode(errors="replace").strip()

    def _write(self, cmd: str):
        with self._lock:
            self.ser.write(f"{cmd}\r\n".encode())

    @Slot()
    def start(self):
        if not config.PSU_1_ENABLED or not config.PSU_1_PORT:
            self.log_message.emit("PSU-1 desabilitada.")
            return
        try:
            self.ser = serial.Serial(
                config.PSU_1_PORT, config.PSU_1_BAUD,
                stopbits=serial.STOPBITS_TWO, timeout=3,
            )
            time.sleep(0.1)                   # let E3634A finish any pending TX
            self.ser.reset_input_buffer()     # discard stale bytes from previous session
            self._write("*CLS")              # clear error queue + STB/ESR
            time.sleep(0.1)                   # wait for *CLS to be processed
            idn = self._query("*IDN?")
            self.log_message.emit(f"{self._id} conectado: {idn}")
            self._write(f"CURR {config.MAX_PSU_CURRENT_A}")
            self._write("SYSTEM:BEEPER:STATE OFF")   # suppress error beeps automatically
            self.is_running = True
            self.poll_timer = QTimer(self)
            self.poll_timer.setInterval(config.LOG_INTERVAL_MS)
            self.poll_timer.timeout.connect(self.poll_data)
            self.poll_timer.start()
        except Exception as e:
            self.log_message.emit(f"ERRO ({self._id}): {e}")

    @Slot()
    def stop(self):
        self.is_running = False
        if hasattr(self, "poll_timer"):
            self.poll_timer.stop()
        try:
            if self.ser and self.ser.is_open:
                self._write("OUTP OFF")
                self.ser.close()
        except Exception:
            pass
        self.log_message.emit(f"{self._id} desconectado.")

    def poll_data(self):
        if not self.is_running or not self.ser:
            return
        try:
            v_str = self._query("MEAS:VOLT?")
            time.sleep(0.05)   # allow E3634A to flush TX before next query (avoids ERR -410)
            c_str = self._query("MEAS:CURR?")
            if not v_str or not c_str:
                return
            self._latest_data = (float(v_str), float(c_str))
            self.data_ready.emit(*self._latest_data)
        except ValueError:
            pass  # transient garbled response — skip tick silently
        except Exception as e:
            self.log_message.emit(f"Erro leitura {self._id}: {e}")

    def get_latest_data(self):
        return self._latest_data

    @Slot(float)
    def set_voltage(self, voltage_v: float):
        if self.ser and self.ser.is_open:
            try:
                self._write(f"VOLT {voltage_v:.4f}")
            except Exception as e:
                self.log_message.emit(f"ERRO tensão {self._id}: {e}")

    @Slot()
    def turn_on(self):
        if self.ser and self.ser.is_open:
            try:
                self._write("OUTP ON")
                self.log_message.emit(f"{self._id}: saída LIGADA")
            except Exception as e:
                self.log_message.emit(f"ERRO ligar {self._id}: {e}")

    @Slot()
    def turn_off(self):
        if self.ser and self.ser.is_open:
            try:
                self._write("OUTP OFF")
                self.log_message.emit(f"{self._id}: saída DESLIGADA")
            except Exception as e:
                self.log_message.emit(f"ERRO desligar {self._id}: {e}")

    @Slot(bool)
    def set_beeper(self, enabled: bool):
        if self.ser and self.ser.is_open:
            try:
                self._write(f"SYSTEM:BEEPER:STATE {'ON' if enabled else 'OFF'}")
                self.log_message.emit(f"{self._id}: buzzer {'LIGADO' if enabled else 'DESLIGADO'}")
            except Exception as e:
                self.log_message.emit(f"ERRO buzzer {self._id}: {e}")


# =============================================================================
#   DUTWorker — Nexys4 DDR FPGA
#
#   Protocol: send byte 'F', receive 15 binary bytes Little Endian:
#     [TL TH TH2  SL SH  VL VH VH2  AL  WL WH  CL CH  EL EH]
#     temp(3)  slack(2)  vccint(3)  fail(1)  wrong(2)  correct(2)  error_count(2)
#   Conversions:
#     temp_c      = raw_temp    / 1000.0
#     slack       = raw_slack   (integer phase-step count)
#     vccint      = raw_voltage / 1000.0
#     wrong       = raw adder canary result at first alarm (integer)
#     correct     = expected adder result at first alarm (integer)
#     error_count = running count of canary mismatches, saturates at 65535
# =============================================================================
class DUTWorker(QObject):
    """
    Protocolo (experimental-multi-sensor): pacote autoframed de
    multi_sensor_stream.sv (sync 0xAA 0x55 + length + checksum) -- ver
    protocol.py. Substitui o pacote legado de 15 bytes: este branch não
    tem canário funcional para reportar, e slack/alarm agora são um valor
    por canal.
    """
    log_message = Signal(str)
    data_ready = Signal(float, list, float, list)  # temp_c, slack (por canal), vccint_v, alarm (por canal)

    def __init__(self, dut_id: str, num_channels=MULTI_NUM_CHANNELS):
        """dut_id: 'DUT-0' or 'DUT-1' (for log messages)."""
        super().__init__()
        self._id = dut_id
        self.ser = None
        self.is_running = False
        self.num_channels = num_channels
        self._latest_data = (0.0, [0] * num_channels, 0.0, [False] * num_channels)
        self._boot_reject_count = 0

    def _get_port_baud(self):
        raise NotImplementedError

    @Slot()
    def start(self):
        raise NotImplementedError

    def _connect(self, port, baud):
        try:
            self.ser = serial.Serial(port, baud, timeout=2)
            self.log_message.emit(f"{self._id} conectado em {port} @ {baud}")
            self.is_running = True
            self.poll_timer = QTimer(self)
            self.poll_timer.setInterval(config.LOG_INTERVAL_MS)
            self.poll_timer.timeout.connect(self.poll_data)
            self.poll_timer.start()
        except serial.SerialException as e:
            self.log_message.emit(f"ERRO ({self._id}): {e}")

    @Slot()
    def stop(self):
        self.is_running = False
        if hasattr(self, "poll_timer"):
            self.poll_timer.stop()
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.log_message.emit(f"{self._id} desconectado.")

    def poll_data(self):
        if not self.is_running or not self.ser or not self.ser.is_open:
            return
        try:
            self.ser.reset_input_buffer()  # discard any buffered packets (FPGA 1 Hz timer accumulates them)
            self.ser.write(b"\x54")        # 'T': trigger a fresh phase sweep
            data = self.ser.read(MULTI_PKT_LEN)
            print(f"{self._id} raw ({len(data)}B): {data.hex(' ')}")
            if len(data) == MULTI_PKT_LEN:
                parsed = parse_multi_sensor_packet(data, self.num_channels)
                if parsed is None:
                    print(f"{self._id}: pacote multi-sensor com sync/checksum inválido")
                    return

                temp_c = parsed['temp_raw']   / 1000.0
                vccint = parsed['vccint_raw'] / 1000.0
                slack  = parsed['slack']
                alarm  = parsed['alarm']

                if temp_c == 0 and vccint == 0 and all(s == 0 for s in slack):
                    return
                if temp_c > 120.0 or vccint > 1.5:
                    self._boot_reject_count += 1
                    if self._boot_reject_count == 1:
                        print(f"{self._id}: aguardando FPGA inicializar (pacotes inválidos serão descartados)...")
                    self.ser.reset_input_buffer()
                    return
                if self._boot_reject_count > 0:
                    print(f"{self._id}: FPGA inicializado após {self._boot_reject_count} pacote(s) descartado(s).")
                    self._boot_reject_count = 0
                self._latest_data = (temp_c, slack, vccint, alarm)
                self.data_ready.emit(temp_c, slack, vccint, alarm)
            else:
                if len(data) == 0:
                    print(f"{self._id}: sem resposta (timeout).")
                else:
                    print(f"{self._id}: pacote incompleto ({len(data)}/{MULTI_PKT_LEN} bytes)")
        except Exception as e:
            self.log_message.emit(f"ERRO ({self._id}): {e}")
            self._latest_data = (0.0, [0] * self.num_channels, 0.0, [False] * self.num_channels)

    def get_latest_data(self):
        return self._latest_data

    def reset_data(self):
        """Clear stale data and flush serial buffer after FPGA reprogramming."""
        self._latest_data = (0.0, [0] * self.num_channels, 0.0, [False] * self.num_channels)
        self._boot_reject_count = 0
        if self.ser and self.ser.is_open:
            try:
                self.ser.reset_input_buffer()
            except Exception:
                pass


class DUTWorker0(DUTWorker):
    def __init__(self):
        super().__init__("DUT-0")

    @Slot()
    def start(self):
        self._connect(config.DUT_0_PORT, config.DUT_0_BAUD)


class DUTWorker1(DUTWorker):
    def __init__(self):
        super().__init__("DUT-1")

    @Slot()
    def start(self):
        self._connect(config.DUT_1_PORT, config.DUT_1_BAUD)


# =============================================================================
#   TestSequencer — orchestrates all workers, VCCINT loop, CSV logging
# =============================================================================
class TestSequencer(QObject):
    log_message = Signal(str)
    plot_data_update = Signal(dict)
    stats_update = Signal(list, list)  # per-channel stats for DUT-0, DUT-1
    test_finished = Signal()

    def __init__(self, arduino: ArduinoWorker,
                 psu0: PSUWorker0, psu1: PSUWorker1,
                 dut0: DUTWorker, dut1: DUTWorker,
                 num_channels=MULTI_NUM_CHANNELS):
        super().__init__()
        self.arduino = arduino
        self.psu0 = psu0
        self.psu1 = psu1
        self.dut0 = dut0
        self.dut1 = dut1
        self.num_channels = num_channels

        self.logger = None
        self.is_running = False
        self.start_time = time.time()
        self._settings = {}

        # Per-channel running stats (min/max/mean/alarm count), one set
        # per physical DUT -- reset at the start of each test.
        self._chan_stats0 = None
        self._chan_stats1 = None
        self._tick_count = 0

        # Tracked PSU command voltages for VCCINT loop
        self._psu0_cmd_v = 0.0
        self._psu1_cmd_v = 0.0

        # DUT temperature outer loop
        self._dut_target_temp = 0.0
        self._outer_tick = 0

        self.log_timer = QTimer(self)
        self.log_timer.setInterval(config.LOG_INTERVAL_MS)
        self.log_timer.timeout.connect(self.log_data_tick)

    def _reset_channel_stats(self):
        def _blank():
            return [{'min': None, 'max': None, 'sum': 0.0, 'n': 0, 'alarm_count': 0}
                    for _ in range(self.num_channels)]
        self._chan_stats0 = _blank()
        self._chan_stats1 = _blank()
        self._tick_count = 0

    @staticmethod
    def _update_stats(stats, slack, alarm, num_channels):
        for i in range(num_channels):
            s = stats[i]
            v = slack[i] if i < len(slack) else 0
            s['min'] = v if s['min'] is None else min(s['min'], v)
            s['max'] = v if s['max'] is None else max(s['max'], v)
            s['sum'] += v
            s['n'] += 1
            if i < len(alarm) and alarm[i]:
                s['alarm_count'] += 1

    @staticmethod
    def _summarize_stats(stats):
        out = []
        for s in stats:
            mean = (s['sum'] / s['n']) if s['n'] else 0.0
            out.append({'min': s['min'] or 0, 'max': s['max'] or 0,
                        'mean': mean, 'alarm_count': s['alarm_count']})
        return out

    def get_channel_stats(self):
        """Returns (stats_dut0, stats_dut1), each a list of per-channel
        {min, max, mean, alarm_count} dicts, or (None, None) if no test
        has run yet."""
        if not self._chan_stats0:
            return None, None
        return self._summarize_stats(self._chan_stats0), self._summarize_stats(self._chan_stats1)

    def _check_divergence(self, dut_label, stats, alarm):
        if self._tick_count == 0 or self._tick_count % 30 != 0:
            return
        rates = [s['alarm_count'] / s['n'] if s['n'] else 0.0 for s in stats]
        if not rates:
            return
        mean_rate = sum(rates) / len(rates)
        for i, r in enumerate(rates):
            if abs(r - mean_rate) > 0.20:
                self.log_message.emit(
                    f"[Divergência {dut_label}] Canal {i}: taxa de alarme {r:.1%} "
                    f"(média do grupo {mean_rate:.1%})"
                )

    def _program_both_duts(self) -> bool:
        """Program DUT-0 and DUT-1 in a single Vivado session (avoids hw_server re-enumeration race)."""
        if not os.path.isfile(config.BITSTREAM_PATH):
            self.log_message.emit(f"ERRO: Bitstream não encontrado: {config.BITSTREAM_PATH}")
            return False

        probes_line = (
            f"set_property PROBES.FILE {{{config.BITSTREAM_LTX}}} [current_hw_device]"
            if os.path.isfile(config.BITSTREAM_LTX) else ""
        )
        tcl = f"""\
open_hw_manager
connect_hw_server

set tgts0 [get_hw_targets *{config.DUT0_DIGILENT_SERIAL}*]
if {{[llength $tgts0] == 0}} {{
    error "DUT-0 não encontrado (serial {config.DUT0_DIGILENT_SERIAL})"
}}
open_hw_target [lindex $tgts0 0]
current_hw_device [lindex [get_hw_devices] 0]
refresh_hw_device -update_hw_probes false [current_hw_device]
set_property PROGRAM.FILE {{{config.BITSTREAM_PATH}}} [current_hw_device]
{probes_line}
program_hw_devices [current_hw_device]
close_hw_target

set tgts1 [get_hw_targets *{config.DUT1_DIGILENT_SERIAL}*]
if {{[llength $tgts1] == 0}} {{
    error "DUT-1 não encontrado (serial {config.DUT1_DIGILENT_SERIAL})"
}}
open_hw_target [lindex $tgts1 0]
current_hw_device [lindex [get_hw_devices] 0]
refresh_hw_device -update_hw_probes false [current_hw_device]
set_property PROGRAM.FILE {{{config.BITSTREAM_PATH}}} [current_hw_device]
{probes_line}
program_hw_devices [current_hw_device]
close_hw_target

disconnect_hw_server
close_hw_manager
exit
"""
        tcl_fd, tcl_path = tempfile.mkstemp(suffix=".tcl", prefix="prog_duts_")
        try:
            with os.fdopen(tcl_fd, "w") as f:
                f.write(tcl)
            result = subprocess.run(
                [config.VIVADO_BIN, "-mode", "batch", "-nojournal", "-nolog",
                 "-source", tcl_path],
                capture_output=True, text=True, timeout=300,
            )
            if result.returncode != 0:
                tail = (result.stdout + result.stderr)[-800:].strip()
                self.log_message.emit(f"ERRO ao programar DUTs:\n{tail}")
                return False
            self.log_message.emit("DUT-0 e DUT-1 programados com sucesso.")
            return True
        except subprocess.TimeoutExpired:
            self.log_message.emit("ERRO: Timeout ao programar DUTs (>300 s)")
            return False
        except Exception as e:
            self.log_message.emit(f"ERRO ao programar DUTs: {e}")
            return False
        finally:
            try:
                os.unlink(tcl_path)
            except OSError:
                pass

    @Slot(dict)
    def start_test(self, settings: dict):
        """
        settings keys:
          test_name, oven_setpoint, psu0_voltage, psu1_voltage,
          vccint_sp0, vccint_sp1
        """
        if self.is_running:
            self.log_message.emit("ERRO: Teste já em execução.")
            return
        try:
            self._settings = settings
            self._dut_target_temp = float(settings.get("dut_target_temp", 0.0))
            self._outer_tick = 0
            self._reset_channel_stats()
            self.logger = DataLogger(config.LOG_FOLDER, settings["test_name"])
            self.log_message.emit(f"Log criado: {self.logger.filepath}")

            # Oven (optional)
            if config.ARDUINO_ENABLED and self.arduino.is_ready:
                self.arduino.set_target_setpoint(settings["oven_setpoint"])
                time.sleep(0.1)
                self.arduino.start_test_oven()

            # PSU 0
            if config.PSU_0_ENABLED and self.psu0.is_running:
                self._psu0_cmd_v = float(settings["psu0_voltage"])
                self.psu0.set_voltage(self._psu0_cmd_v)
                time.sleep(0.2)
                self.psu0.turn_on()

            # PSU 1
            if config.PSU_1_ENABLED and self.psu1.is_running:
                self._psu1_cmd_v = float(settings["psu1_voltage"])
                self.psu1.set_voltage(self._psu1_cmd_v)
                time.sleep(0.2)
                self.psu1.turn_on()

            # Wait for rails to stabilise before touching FPGA SRAM
            self.log_message.emit(
                f"Aguardando {config.PSU_STABILISE_DELAY_S}s para estabilização das fontes..."
            )
            time.sleep(config.PSU_STABILISE_DELAY_S)

            # Both DUTs must be programmed on every power-on (SRAM only)
            self.log_message.emit("Programando DUT-0 e DUT-1 via Vivado...")
            if not self._program_both_duts():
                self.log_message.emit("ERRO CRÍTICO: Falha ao programar DUTs. Abortando.")
                if config.PSU_0_ENABLED:
                    self.psu0.turn_off()
                if config.PSU_1_ENABLED:
                    self.psu1.turn_off()
                if self.logger:
                    self.logger.close()
                    self.logger = None
                self.test_finished.emit()
                return

            # Flush any UART bytes the FPGAs may have emitted during reset/configuration.
            # The Vivado batch job itself takes 30-60 s, so the FPGAs are already running
            # by the time we reach here.  The boot-rejection logic in poll_data() handles
            # the brief transient before XADC values settle.
            self.dut0.reset_data()
            self.dut1.reset_data()

            self.is_running = True
            self.start_time = time.time()
            self.log_timer.start()

            self.log_message.emit("=" * 50)
            self.log_message.emit(">>> TESTE INICIADO (2 DUTs — ambos programados) <<<")
            self.log_message.emit(
                f"Setpoint forno: {settings['oven_setpoint']}°C | "
                f"PSU0: {settings['psu0_voltage']}V | PSU1: {settings['psu1_voltage']}V"
            )
            self.log_message.emit(f"VCCINT sp0={settings['vccint_sp0']}V  sp1={settings['vccint_sp1']}V")
            self.log_message.emit("=" * 50)

        except Exception as e:
            self.log_message.emit(f"ERRO CRÍTICO: {e}")
            self.is_running = False
            if self.logger:
                self.logger.close()
            self.test_finished.emit()

    @Slot()
    def stop_test(self):
        self.log_message.emit("Parando teste...")
        self.is_running = False
        self.log_timer.stop()

        if config.ARDUINO_ENABLED:
            self.arduino.stop_test_oven()
        if config.PSU_0_ENABLED:
            self.psu0.turn_off()
        if config.PSU_1_ENABLED:
            self.psu1.turn_off()

        if self.logger:
            self.logger.close()
            self.logger = None

        self.log_message.emit("=" * 50)
        self.log_message.emit(">>> TESTE FINALIZADO <<<")
        self.log_message.emit("=" * 50)
        self.test_finished.emit()

    def log_data_tick(self):
        if not self.is_running:
            return
        try:
            elapsed = time.time() - self.start_time

            t_oven, sp_oven, out_oven = self.arduino.get_latest_data()
            v0, c0 = self.psu0.get_latest_data()
            t0, s0, vcc0, a0 = self.dut0.get_latest_data()
            v1, c1 = self.psu1.get_latest_data()
            t1, s1, vcc1, a1 = self.dut1.get_latest_data()

            # --- VCCINT closed-loop (P-only) ---
            self._update_vccint_loop(vcc0, vcc1)

            # --- DUT temperature outer loop (slow oven setpoint trim) ---
            valid = [t for t in [t0, t1] if t > 0]
            avg_dut = sum(valid) / len(valid) if valid else 0.0
            self._adjust_oven_outer_loop(avg_dut, sp_oven)

            # --- Per-channel stats + divergence (per physical DUT) ---
            self._update_stats(self._chan_stats0, s0, a0, self.num_channels)
            self._update_stats(self._chan_stats1, s1, a1, self.num_channels)
            self._tick_count += 1
            self._check_divergence("DUT-0", self._chan_stats0, a0)
            self._check_divergence("DUT-1", self._chan_stats1, a1)

            row = {
                "time_sec": elapsed,
                "oven_temp": t_oven, "oven_setpoint": sp_oven, "oven_output": out_oven,
                "psu0_voltage": v0, "psu0_current": c0,
                "dut0_temp": t0, "dut0_volt": vcc0,
                "psu1_voltage": v1, "psu1_current": c1,
                "dut1_temp": t1, "dut1_volt": vcc1,
                "psu0_cmd_v": self._psu0_cmd_v,
                "psu1_cmd_v": self._psu1_cmd_v,
            }
            for i in range(self.num_channels):
                row[f"dut0_slack_ch{i}"] = s0[i] if i < len(s0) else 0
                row[f"dut0_alarm_ch{i}"] = int(a0[i]) if i < len(a0) else 0
                row[f"dut1_slack_ch{i}"] = s1[i] if i < len(s1) else 0
                row[f"dut1_alarm_ch{i}"] = int(a1[i]) if i < len(a1) else 0

            if self.logger:
                self.logger.write_data_row(row)

            self.plot_data_update.emit(row)
            stats0, stats1 = self.get_channel_stats()
            self.stats_update.emit(stats0, stats1)
            self._check_safety(t0, c0, t1, c1, t_oven)

        except Exception as e:
            self.log_message.emit(f"ERRO no loop de log: {e}")
            self.stop_test()

    def _update_vccint_loop(self, vcc0: float, vcc1: float):
        """Proportional trim of each PSU to bring VCCINT to its setpoint."""
        sp0 = self._settings.get("vccint_sp0", config.VCCINT_SETPOINT_0_V)
        sp1 = self._settings.get("vccint_sp1", config.VCCINT_SETPOINT_1_V)

        if config.PSU_0_ENABLED and self.psu0.is_running and vcc0 > 0:
            err0 = sp0 - vcc0
            self._psu0_cmd_v = max(
                config.PSU_MIN_V,
                min(config.PSU_MAX_V, self._psu0_cmd_v + config.VOLTAGE_KP * err0)
            )
            self.psu0.set_voltage(self._psu0_cmd_v)

        if config.PSU_1_ENABLED and self.psu1.is_running and vcc1 > 0:
            err1 = sp1 - vcc1
            self._psu1_cmd_v = max(
                config.PSU_MIN_V,
                min(config.PSU_MAX_V, self._psu1_cmd_v + config.VOLTAGE_KP * err1)
            )
            self.psu1.set_voltage(self._psu1_cmd_v)

    def _adjust_oven_outer_loop(self, avg_dut_temp: float, sp_oven: float):
        """Shift oven setpoint every ~30 min to bring average DUT temp to target.
        Runs every log tick; acts only when _outer_tick reaches the interval."""
        if self._dut_target_temp <= 0 or avg_dut_temp <= 0:
            return
        self._outer_tick += 1
        if self._outer_tick < _DUT_OUTER_TICK_INTERVAL:
            return
        self._outer_tick = 0
        error = avg_dut_temp - self._dut_target_temp
        if abs(error) <= _DUT_TEMP_TOLERANCE_C:
            return
        step = _OVEN_SP_STEP_C if error < 0 else -_OVEN_SP_STEP_C
        new_sp = max(0.0, min(config.MAX_OVEN_TEMP_C, sp_oven + step))
        if new_sp == sp_oven:
            return
        if config.ARDUINO_ENABLED and self.arduino.is_ready:
            self.arduino.set_target_setpoint(new_sp)
        self.log_message.emit(
            f"DUT outer loop: DUT_avg={avg_dut_temp:.1f}°C target={self._dut_target_temp:.0f}°C "
            f"→ oven_sp {sp_oven:.0f}→{new_sp:.0f}°C"
        )

    def _check_safety(self, t0, c0, t1, c1, t_oven):
        if t0 > config.MAX_DUT_TEMP_C:
            self.log_message.emit(f"!!! ALERTA: Temp DUT-0 ({t0:.1f}°C) > {config.MAX_DUT_TEMP_C}°C !!!")
            self.stop_test()
        if t1 > config.MAX_DUT_TEMP_C:
            self.log_message.emit(f"!!! ALERTA: Temp DUT-1 ({t1:.1f}°C) > {config.MAX_DUT_TEMP_C}°C !!!")
            self.stop_test()
        if config.PSU_0_ENABLED and c0 > config.MAX_PSU_CURRENT_A:
            self.log_message.emit(f"!!! ALERTA: Corrente PSU-0 ({c0:.3f}A) > {config.MAX_PSU_CURRENT_A}A !!!")
            self.stop_test()
        if config.PSU_1_ENABLED and c1 > config.MAX_PSU_CURRENT_A:
            self.log_message.emit(f"!!! ALERTA: Corrente PSU-1 ({c1:.3f}A) > {config.MAX_PSU_CURRENT_A}A !!!")
            self.stop_test()
        if config.ARDUINO_ENABLED and t_oven > config.MAX_OVEN_TEMP_C:
            self.log_message.emit(f"!!! ALERTA: Temp Forno ({t_oven:.1f}°C) > {config.MAX_OVEN_TEMP_C}°C !!!")
            self.stop_test()
