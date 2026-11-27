"""
=============================================================================
TCC - Workers de Thread (VERSÃO FINAL)
=============================================================================
Cada classe roda em thread separada (QThread) para comunicação com hardware
sem travar a interface gráfica.

Workers:
  - ArduinoWorker: Controle do forno (PID, SSR, NTC)
  - PSUWorker: Controle da fonte de alimentação (IT6502D USB-TMC/PyVISA)
  - DUTWorker: Comunicação com FPGA (sensor de slack)
  - TestSequencer: Orquestrador do teste

Autor: [Seu Nome]
Data: Janeiro/2026
=============================================================================
"""
from PySide6.QtCore import QObject, Signal, Slot, QTimer
import serial
import time
import csv as csv_mod
from datetime import datetime
import config
from logger import DataLogger
import threading


# =============================================================================
#   DUT die-temperature outer loop (slow oven-setpoint trim)
# =============================================================================
# Decision rule, unchanged from the campaigns already logged (PID-214): every
# 30 min, if the die is more than 3 °C from its target, move the oven setpoint
# 1 °C toward it.
#
# Fixed 2026-11-27:
#   * The decision read one instantaneous die sample, so XADC noise or a
#     thermostat-cycle peak could trigger (or skip) a step. It now uses the mean
#     of the valid die samples over the whole interval.
#   * The 1 °C change went out as one SET_SP (the oven firmware ramps it at
#     1 °C/s), an air step the D&T 2027 analysis associates with jumps in the
#     corrected slack residual. It now goes out as a 0.1 °C / 150 s ramp
#     (1 °C in 25 min, close to the die's ~1300 s thermal time constant).
#   * The interval is counted from LOG_INTERVAL_MS instead of assuming 1 s ticks.
#   * A change is logged only when it was sent; a setpoint changed by hand in
#     the UI mid-ramp cancels the ramp instead of being overwritten.
#
# TODO(control): replace this dead-band stepper by a continuous cascade loop on
#   the die temperature (see the D&T 2027 analysis and the AU15P ideas note,
#   hardware/fpga/xilinx/ultrascale_plus/docs/ideas_au15p_burnin_2026-11-10.md §2.2):
#   1. Identify the outer plant first: step the oven setpoint at a fixed die
#      load and fit die-vs-setpoint as FOPDT (PID-214 gave 0.97-1.81 °C of die
#      per °C of air, die tau ~1300 s), then tune a PI by SIMC, as was done for
#      the oven PID. Do not guess the gains.
#   2. Outer PI on the low-passed die temperature (5-10 min, to keep XADC noise
#      and the bang-bang cycle out) -> oven setpoint, continuous and
#      rate-limited (<= ~0.1 °C/min), clamped to the oven range, with
#      anti-windup. The inner loop stays the Arduino oven PID.
#   3. No dead-band (or <= 0.5 °C): at 115 °C and Ea = 0.7 eV a 5 % AF tolerance
#      allows only 0.9 °C of mean die error (Eq. 3); the current +-3 °C
#      dead-band lets the mean sit ~3 °C off, an ~18 % AF shortfall.
#   4. Hold the integrator during the first-hour thermal soak, or start the
#      setpoint from a die-to-air offset model, so the soak does not wind it up.
#   5. Log the loop state (setpoint command, integral) in the CSV and name the
#      loop in the header, so the analysis can regress or mask it.
#   6. Validate against PID-214: Hadamard deviation of die temperature and of
#      the T,V-corrected residual (floor 0.25 cnt as run, 0.15 cnt with the
#      setpoint steps masked); the goal is a floor at or below the masked one.
#   Longer term: close the loop on the die itself (on-die heater driven from
#   SYSMON/XADC, response in seconds), with the oven as a slow bias.
_OUTER_INTERVAL_S = 1800.0      # decision interval (s)
_OUTER_DEADBAND_C = 3.0         # dead-band on the interval-mean die error (°C)
_OUTER_STEP_C = 1.0             # setpoint change per decision (°C)
_OUTER_RAMP_STEP_C = 0.1        # the change is sent in increments of this (°C)
_OUTER_RAMP_EVERY_S = 150.0     # ... one increment every this many seconds
_OUTER_SP_MIN_C = 20.0          # oven firmware SET_SP range (OVEN_SP_MIN_C)
_OUTER_SP_MATCH_TOL_C = 0.05    # readback vs last command; larger = changed by hand
_OUTER_MIN_VALID_FRACTION = 0.5 # skip a decision with fewer valid die samples


class DieTempOuterLoop:
    """Slow outer loop that trims the oven setpoint so the die mean reaches its target.

    Pure logic, no I/O: tick() is called once per log tick and returns the
    setpoint to send (or None) and a message to log (or None).
    """

    def __init__(self, tick_s: float, sp_max_c: float):
        self.interval_ticks = max(1, round(_OUTER_INTERVAL_S / tick_s))
        self.ramp_every_ticks = max(1, round(_OUTER_RAMP_EVERY_S / tick_s))
        self.sp_max_c = sp_max_c
        self.reset(0.0)

    def reset(self, target_c: float):
        self.target_c = float(target_c)
        self._tick = 0
        self._sum = 0.0
        self._n = 0
        self._ramp_goal = None
        self._ramp_cmd = None
        self._ramp_tick = 0

    @property
    def enabled(self) -> bool:
        return self.target_c > 0

    @property
    def ramping(self) -> bool:
        return self._ramp_goal is not None

    def tick(self, die_c: float, sp_readback: float, can_send: bool):
        if not self.enabled:
            return None, None
        if die_c > 0:
            self._sum += die_c
            self._n += 1
        self._tick += 1

        sp_out, msg = (self._ramp_step(sp_readback, can_send)
                       if self.ramping else (None, None))
        if self._tick < self.interval_ticks:
            return sp_out, msg

        # End of the interval: decide on its mean die temperature.
        n, mean = self._n, (self._sum / self._n if self._n else 0.0)
        self._tick, self._sum, self._n = 0, 0.0, 0
        if self.ramping:
            return sp_out, msg          # previous change still going out
        if n < _OUTER_MIN_VALID_FRACTION * self.interval_ticks:
            return None, (f"DUT outer loop: only {n}/{self.interval_ticks} valid die "
                          f"samples in the interval; no adjustment")
        error = mean - self.target_c
        if abs(error) <= _OUTER_DEADBAND_C:
            return None, None
        if not can_send or sp_readback <= 0:
            return None, (f"DUT outer loop: die mean {mean:.2f}°C, target "
                          f"{self.target_c:.1f}°C, but the oven is not available; "
                          f"no adjustment")
        base = round(sp_readback, 2)
        step = _OUTER_STEP_C if error < 0 else -_OUTER_STEP_C
        goal = round(max(_OUTER_SP_MIN_C, min(self.sp_max_c, base + step)), 2)
        if goal == base:
            return None, (f"DUT outer loop: die mean {mean:.2f}°C, target "
                          f"{self.target_c:.1f}°C, oven setpoint already at its "
                          f"limit ({base:.2f}°C)")
        self._ramp_goal, self._ramp_cmd = goal, base
        self._ramp_tick = self.ramp_every_ticks - 1   # first increment now
        sp_out, ramp_msg = self._ramp_step(sp_readback, can_send)
        msg = (f"DUT outer loop: die mean {mean:.2f}°C over {n} samples, target "
               f"{self.target_c:.1f}°C -> oven setpoint {base:.2f} -> {goal:.2f}°C, "
               f"ramp of {_OUTER_RAMP_STEP_C}°C every {_OUTER_RAMP_EVERY_S:.0f} s")
        if ramp_msg:
            msg += f" | {ramp_msg}"
        return sp_out, msg

    def _ramp_step(self, sp_readback: float, can_send: bool):
        self._ramp_tick += 1
        if self._ramp_tick < self.ramp_every_ticks:
            return None, None
        self._ramp_tick = 0
        if abs(sp_readback - self._ramp_cmd) > _OUTER_SP_MATCH_TOL_C:
            expected = self._ramp_cmd
            self._ramp_goal = self._ramp_cmd = None
            return None, (f"DUT outer loop: oven setpoint changed outside the loop "
                          f"({sp_readback:.2f}°C, expected {expected:.2f}°C); ramp cancelled")
        if not can_send:
            return None, None           # retry at the next increment
        delta = self._ramp_goal - self._ramp_cmd
        inc = max(-_OUTER_RAMP_STEP_C, min(_OUTER_RAMP_STEP_C, delta))
        self._ramp_cmd = round(self._ramp_cmd + inc, 2)
        if abs(self._ramp_goal - self._ramp_cmd) < 1e-6:
            self._ramp_cmd = self._ramp_goal
            self._ramp_goal = None
            return self._ramp_cmd, f"DUT outer loop: ramp done, oven setpoint {self._ramp_cmd:.2f}°C"
        return self._ramp_cmd, None


# =============================================================================
#   WORKER 1: Controlador do Forno (Arduino)
# =============================================================================
class ArduinoWorker(QObject):
    """
    Controla o Arduino (PID, SSR, NTC) com proteção de Thread (Lock).
    
    Sinais:
        log_message(str): Mensagem para o log da UI
        data_ready(float, float, float): temp, setpoint, output
    """
    log_message = Signal(str)
    data_ready = Signal(float, float, float) 

    def __init__(self):
        super().__init__()
        self.ser = None
        self.is_running = False
        self._latest_data = (0.0, 0.0, 0.0)
        self.serial_lock = threading.Lock()
        self.is_ready = False

    @Slot()
    def start(self):
        """Inicializa conexão com Arduino."""
        if not config.ARDUINO_ENABLED or not config.ARDUINO_PORT:
            self.log_message.emit("Arduino desabilitado — controle de forno inativo.")
            return
        try:
            self.ser = serial.Serial(
                config.ARDUINO_PORT,
                config.ARDUINO_BAUD,
                timeout=2
            )

            self.log_message.emit("Arduino conectado. Aguardando boot (3s)...")
            time.sleep(3.0)
            
            # Limpeza do buffer inicial
            with self.serial_lock:
                self.ser.reset_input_buffer()
                self.ser.reset_output_buffer()
                while self.ser.in_waiting:
                    self.ser.readline()

            self.log_message.emit(f"Arduino pronto em {config.ARDUINO_PORT}")
            self.log_message.emit(
                f"Config padrão (será confirmada via GET_CONFIG no teste): "
                f"{config.get_pid_info_string()}"
            )
            
            self.is_running = True
            self.is_ready = True
            
            self.poll_timer = QTimer(self)
            self.poll_timer.setInterval(config.LOG_INTERVAL_MS)
            self.poll_timer.timeout.connect(self.poll_data)
            self.poll_timer.start()
            
        except serial.SerialException as e:
            self.log_message.emit(f"ERRO (Arduino): {e}")
            self.is_ready = False

    @Slot()
    def stop(self):
        """Encerra conexão com Arduino."""
        self.is_running = False
        if hasattr(self, 'poll_timer'):
            self.poll_timer.stop()
        
        with self.serial_lock:
            if self.ser and self.ser.is_open:
                try:
                    self.ser.write(b"STOP_TEST\n") 
                except: 
                    pass
                self.ser.close()
        self.log_message.emit("Arduino desconectado.")

    def poll_data(self):
        """Leitura periódica de dados do Arduino."""
        if not self.is_running: 
            return
        
        with self.serial_lock: 
            try:
                if self.ser and self.ser.is_open:
                    self.ser.write(b"GET_DATA\n") 
                    line = self.ser.readline().decode('ascii', errors='ignore').strip()
                        
                    if line.startswith("DATA,"):
                        try:
                            parts = line.split(',')
                            temp_c = float(parts[1])
                            setpoint_c = float(parts[2])
                            output_pct = float(parts[3])
                            
                            self._latest_data = (temp_c, setpoint_c, output_pct)
                            self.data_ready.emit(temp_c, setpoint_c, output_pct)
                        except Exception as e:
                            print(f"Erro Parse Arduino: {e} - Linha: {line}")
                            
            except Exception as e:
                self.log_message.emit(f"Erro Leitura Arduino: {e}")

    def get_latest_data(self):
        """Retorna últimos dados lidos."""
        return self._latest_data

    def send_command(self, cmd):
        """Envia comando de forma thread-safe."""
        response = None
        
        try:
            with self.serial_lock:
                if self.ser and self.ser.is_open:
                    self.ser.reset_input_buffer()
                    self.ser.write(f"{cmd}\n".encode('ascii'))
                    response = self.ser.readline().decode('ascii', errors='ignore').strip()

        except Exception as e:
            print(f"Erro comando '{cmd}': {type(e).__name__} - {e}")
            self.log_message.emit(f"ERRO enviando '{cmd}'")
            return None 
        
        if response is None or "OK" not in response:
            self.log_message.emit(f"CMD '{cmd}' -> Resposta: '{response}' (FALHOU)")

        return response
            
    @Slot(float)
    def set_target_setpoint(self, temp):
        """Define setpoint de temperatura."""
        return self.send_command(f"SET_SP,{float(temp):.2f}")
        
    @Slot()
    def start_test_oven(self):
        """Inicia controle PID."""
        return self.send_command("START_TEST")

    @Slot()
    def stop_test_oven(self):
        """Para controle PID."""
        return self.send_command("STOP_TEST")
    
    def get_config(self):
        """Solicita configuração atual do Arduino."""
        return self.send_command("GET_CONFIG")

    def query_controller_config(self):
        """Consulta o firmware do forno (GET_CONFIG) e devolve o controlador
        identificado (ver config.parse_controller_config) ou None.

        Faz a leitura própria (sem send_command) porque a resposta é
        'CONFIG,...' e não 'OK', evitando o falso aviso de falha. O serial_lock
        garante exclusão mútua com o poll_data periódico.
        """
        if not config.ARDUINO_ENABLED or not self.is_ready:
            return None
        try:
            with self.serial_lock:
                if not (self.ser and self.ser.is_open):
                    return None
                self.ser.reset_input_buffer()
                self.ser.write(b"GET_CONFIG\n")
                raw = self.ser.readline().decode("ascii", errors="ignore").strip()
        except Exception as e:
            self.log_message.emit(f"ERRO consultando controlador do forno: {e}")
            return None
        return config.parse_controller_config(raw)


# =============================================================================
#   WORKER 2: Controlador da Fonte (PSU) - ITECH IT6502D via USB-TMC (PyVISA)
# =============================================================================
class PSUWorker(QObject):
    """ITECH IT6502D — USB-TMC via PyVISA (@py backend).
    config.PSU_PORT must be a USB VISA resource string, e.g.
    'USB0::0x1AB1::0x0E11::IT6502D300004::INSTR'.
    """
    log_message = Signal(str)
    data_ready = Signal(float, float)  # voltage_v, current_a

    def __init__(self):
        super().__init__()
        self.rm   = None
        self.inst = None
        self.is_running = False
        self._latest_data = (0.0, 0.0)
        self._lock = threading.Lock()

    @Slot()
    def start(self):
        if not config.PSU_ENABLED or not config.PSU_PORT:
            self.log_message.emit("PSU desabilitada — fonte de alimentação inativa.")
            return
        try:
            import pyvisa as visa
            self.rm   = visa.ResourceManager("@py")
            self.inst = self.rm.open_resource(config.PSU_PORT)
            self.inst.timeout           = 5000
            self.inst.read_termination  = "\n"
            self.inst.write_termination = "\n"
            idn = self.inst.query("*IDN?").strip()
            self.log_message.emit(f"PSU (IT6502D) conectada: {idn}")
            self.inst.write(f"CURR {config.MAX_PSU_CURRENT_A:.3f}")
            self.is_running = True
            self.poll_timer = QTimer(self)
            self.poll_timer.setInterval(config.LOG_INTERVAL_MS)
            self.poll_timer.timeout.connect(self.poll_data)
            self.poll_timer.start()
        except Exception as e:
            self.log_message.emit(f"ERRO (PSU): {e}")

    @Slot()
    def stop(self):
        self.is_running = False
        if hasattr(self, "poll_timer"):
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
            self.rm   = None
        self.log_message.emit("PSU (IT6502D) desconectada.")

    def poll_data(self):
        if not self.is_running or not self.inst:
            return
        try:
            with self._lock:
                if not self.inst:
                    return
                v = float(self.inst.query("MEAS:VOLT?").strip())
                c = float(self.inst.query("MEAS:CURR?").strip())
            self._latest_data = (v, c)
            self.data_ready.emit(v, c)
        except Exception as e:
            self.log_message.emit(f"Erro leitura PSU: {e}")

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
                self.log_message.emit(f"ERRO tensão PSU: {e}")

    @Slot()
    def turn_on(self):
        with self._lock:
            if not self.inst:
                return
            try:
                self.inst.write("OUTP ON")
            except Exception as e:
                self.log_message.emit(f"ERRO ligar PSU: {e}")
                return
        self.log_message.emit("PSU (IT6502D): saída LIGADA")

    @Slot()
    def turn_off(self):
        with self._lock:
            if not self.inst:
                return
            try:
                self.inst.write("OUTP OFF")
            except Exception as e:
                self.log_message.emit(f"ERRO desligar PSU: {e}")
                return
        self.log_message.emit("PSU (IT6502D): saída DESLIGADA")

    @Slot(bool)
    def set_beeper(self, enabled: bool):
        with self._lock:
            if not self.inst:
                return
            try:
                self.inst.write(f"SYSTEM:BEEPER:STATE {'ON' if enabled else 'OFF'}")
            except Exception as e:
                self.log_message.emit(f"ERRO buzzer PSU: {e}")


# =============================================================================
#   WORKER 3: Controlador do DUT (FPGA)
# =============================================================================
class DUTWorker(QObject):
    """
    Comunicação com FPGA para leitura do sensor de slack.

    Protocolo: 15 bytes binários (Little Endian), enviados autonomamente pelo FPGA.
    Formato: [TEMP×3][SLACK×2][VOLT×3][FAIL×1][WRONG×2][CORRECT×2][ERR_CNT×2]

    O byte 'F' enviado antes do read é legado — o FPGA não o decodifica; os
    pacotes são disparados pelo FSM interno quando o alarme é detectado.

    Sinais:
        log_message(str): Mensagem para o log
        data_ready(float, int, float): temp_c, slack, voltage
    """
    log_message = Signal(str)
    data_ready = Signal(float, int, float)

    def __init__(self):
        super().__init__()
        self.ser = None
        self.is_running = False
        self._latest_data = (0.0, 0, 0.0, 0, 0, 0, 0)  # temp, slack, voltage, fail, wrong, correct, error_count
        
        self.poll_timer = QTimer(self)
        self.poll_timer.setInterval(config.LOG_INTERVAL_MS) 
        self.poll_timer.timeout.connect(self.poll_data)

    @Slot()
    def start(self):
        try:
            # Abre a porta serial
            # IMPORTANTE: Verifique se config.DUT_BAUD está correto (ex: 115200)
            self.ser = serial.Serial(
                config.DUT_PORT, 
                config.DUT_BAUD, 
                timeout=2 # Timeout de 2s é crucial para o read(15) funcionar
            )
            self.log_message.emit(f"DUT (FPGA) conectado em {config.DUT_PORT} @ {config.DUT_BAUD}")
            
            self.is_running = True
            self.poll_timer.start()
        except serial.SerialException as e:
            self.log_message.emit(f"ERRO (DUT): Porta Serial inacessível: {e}")

    @Slot()
    def stop(self):
        self.is_running = False
        self.poll_timer.stop()
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.log_message.emit("DUT (FPGA) desconectado.")
        
    def poll_data(self):
        """Aguarda e decodifica um pacote de 15 bytes do FPGA."""
        if not self.is_running or not self.ser or not self.ser.is_open:
            return

        try:
            # Descarta bytes residuais de pacotes anteriores para manter o alinhamento.
            self.ser.reset_input_buffer()

            # 'T' (0x54) triggers the next phase sweep on the FPGA.
            # Falls back to the 1 Hz timer if this byte arrives during a sweep.
            self.ser.write(b'\x54')

            # Pacote de 15 bytes (Little Endian):
            # [TEMP×3][SLACK×2][VOLT×3][FAIL×1][WRONG×2][CORRECT×2][ERR_CNT×2]
            BYTES_TO_READ = 15
            data = self.ser.read(BYTES_TO_READ)

            if len(data) == BYTES_TO_READ:
                raw_temp    = int.from_bytes(data[0:3],   byteorder='little')
                raw_slack   = int.from_bytes(data[3:5],   byteorder='little')
                raw_voltage = int.from_bytes(data[5:8],   byteorder='little')
                raw_failure = int(data[8])               # 0 or 1 — failure_holder latch
                raw_wrong   = int.from_bytes(data[9:11],  byteorder='little')
                raw_correct = int.from_bytes(data[11:13], byteorder='little')
                raw_errcnt  = int.from_bytes(data[13:15], byteorder='little')

                temp_c  = float(raw_temp)    / 1000.0
                slack   = int(raw_slack)
                voltage = float(raw_voltage) / 1000.0

                # Filtra leituras zeradas (comum na inicialização do FPGA)
                if temp_c == 0 and slack == 0 and voltage == 0:
                    return

                self._latest_data = (temp_c, slack, voltage, raw_failure, raw_wrong, raw_correct, raw_errcnt)
                self.data_ready.emit(temp_c, slack, voltage)

            else:
                if len(data) == 0:
                    print(f"DUT: Sem resposta (Timeout). Baud rate {config.DUT_BAUD} correto?")
                else:
                    print(f"DUT: Pacote incompleto ({len(data)}/{BYTES_TO_READ} bytes)")

        except Exception as e:
            self.log_message.emit(f"ERRO (DUT): {e}")
            self._latest_data = (0.0, 0, 0.0, 0, 0, 0, 0)

    def get_latest_data(self):
        return self._latest_data

# =============================================================================
#   WORKER 4: Sequenciador de Teste (Orquestrador)
# =============================================================================
class TestSequencer(QObject):
    """
    Orquestra todos os workers e gerencia o log de dados.
    
    Responsabilidades:
      - Iniciar/parar teste coordenadamente
      - Coletar dados de todos os workers
      - Gravar log CSV sincronizado
      - Monitorar limites de segurança
      - Calcular e logar estatísticas em tempo real
    
    Sinais:
        log_message(str): Mensagem para o log
        plot_data_update(dict): Dados para atualização do gráfico
        test_finished(): Sinal de fim de teste
    """
    log_message = Signal(str)
    plot_data_update = Signal(dict)
    test_finished = Signal()
    sweep_step_changed = Signal(int, float, int, str)  # (step_idx_0based, target, total_steps, mode)
    controller_info_signal = Signal(object)            # oven controller dict resolved at test start

    def __init__(self, arduino_worker, psu_worker, dut_worker):
        super().__init__()
        self.arduino = arduino_worker
        self.psu = psu_worker
        self.dut = dut_worker

        self.logger = None
        self.is_running = False
        self.start_time = time.time()

        # Estatísticas em tempo real
        self.temp_samples = []
        self.error_samples = []
        self.output_samples = []

        # DUT temperature outer loop
        self._outer_loop = DieTempOuterLoop(config.LOG_INTERVAL_MS / 1000.0,
                                            config.MAX_OVEN_TEMP_C)

        # Oven controller identified from firmware (provenance)
        self._oven_controller = None

        # VCCINT closed-loop (IT6502D)
        self._psu_cmd_v = 0.0

        # Sweep automático
        self._sweep_mode = None          # None | 'voltage' | 'temperature'
        self._sweep_steps = []
        self._sweep_idx = 0
        self._sweep_required_stable = 60
        self._sweep_min_dwell = 60
        self._sweep_tolerance = 0.02
        self._sweep_stable_ticks = 0
        self._sweep_dwell_ticks = 0
        self._sweep_step_data = []       # (slack, dut_temp, dut_volt, oven_temp, psu_v, psu_i, fail) por tick
        self._sweep_csv_file   = None    # CSV paralelo do sweep (bruto)
        self._sweep_csv_writer = None

        self.log_timer = QTimer(self)
        self.log_timer.setInterval(config.LOG_INTERVAL_MS)
        self.log_timer.timeout.connect(self.log_data_tick)

    @Slot(dict)
    def start_test(self, settings):
        """
        Inicia o teste com as configurações especificadas.
        
        Args:
            settings: Dict com 'test_name', 'oven_setpoint', 'psu_voltage'
        """
        if self.is_running:
            self.log_message.emit("ERRO: Teste já em execução.")
            return
                
        try:
            # 1. Criar o Logger
            self._outer_loop.reset(float(settings.get('dut_target_temp', 0.0)))

            # Identifica o controlador real do forno ANTES de abrir o log, para
            # que o cabeçalho registre o regime correto (PID vs bang-bang são
            # firmwares distintos com o mesmo protocolo serial).
            self._oven_controller = self._resolve_oven_controller()
            self.controller_info_signal.emit(self._oven_controller)

            self.logger = DataLogger(config.LOG_FOLDER, settings['test_name'],
                                     controller_info=self._oven_controller)
            self.log_message.emit(f"Log criado: {self.logger.filepath}")
            
            # Log dos parâmetros do sistema
            self._log_system_config(settings)
            
            # 2. Configurar Arduino (se habilitado)
            if config.ARDUINO_ENABLED and self.arduino.is_ready:
                self.log_message.emit("Aguardando Arduino (máx 6s)...")
                timeout_s = 6
                start_wait = time.time()
                while not self.arduino.is_ready and (time.time() - start_wait < timeout_s):
                    time.sleep(0.5)

                if not self.arduino.is_ready:
                    self.log_message.emit("AVISO: Arduino não respondeu — continuando sem controle de forno.")
                else:
                    self.log_message.emit("Arduino pronto. Configurando...")
                    response_sp = self.arduino.set_target_setpoint(settings['oven_setpoint'])
                    time.sleep(0.1)
                    self.arduino.start_test_oven()

            # 3. Configurar PSU (se habilitada)
            if config.PSU_ENABLED and self.psu.is_running:
                self._psu_cmd_v = float(settings.get('psu_voltage', config.VCCINT_SETPOINT_V))
                config.VCCINT_SETPOINT_V = self._psu_cmd_v
                self.psu.set_voltage(self._psu_cmd_v)
                time.sleep(0.3)
                self.log_message.emit("Ligando saída PSU...")
                self.psu.turn_on()
                time.sleep(0.3)

            # 4. Configurar sweep (se habilitado)
            sweep_mode = settings.get('sweep_mode')
            if sweep_mode in ('voltage', 'temperature'):
                sweep_steps = settings.get('sweep_steps', [])
                if not sweep_steps:
                    self.log_message.emit("[Sweep] ERRO: lista de passos vazia.")
                elif sweep_mode == 'voltage' and (not config.PSU_ENABLED or not self.psu.is_running):
                    self.log_message.emit("[Sweep] ERRO: PSU necessária para sweep de tensão.")
                else:
                    self._sweep_mode = sweep_mode
                    self._sweep_steps = list(sweep_steps)
                    self._sweep_required_stable = int(settings.get('sweep_stable_s', 60))
                    self._sweep_min_dwell = int(settings.get('sweep_min_dwell', 60))
                    self._sweep_tolerance = float(settings.get('sweep_tolerance', 0.02))
                    self._sweep_idx = 0
                    self._sweep_stable_ticks = 0
                    self._sweep_dwell_ticks = 0
                    self._sweep_step_data = []
                    unit = 'V' if sweep_mode == 'voltage' else '°C'
                    self.log_message.emit(
                        f"[Sweep] Modo {sweep_mode} | {len(sweep_steps)} passos: "
                        f"{[f'{v}{unit}' for v in sweep_steps]}"
                    )
                    # Abre CSV paralelo do sweep (dados brutos)
                    sweep_path = self.logger.filepath.replace('.csv', '_sweep.csv')
                    self._sweep_csv_file = open(
                        sweep_path, 'w', newline='', encoding='utf-8', buffering=1
                    )
                    self._sweep_csv_writer = csv_mod.writer(self._sweep_csv_file)
                    self._sweep_csv_writer.writerow([
                        'time_sec', 'sweep_step', 'sweep_target',
                        'dut_volt_v', 'oven_temp_c', 'dut_temp_c', 'dut_slack',
                    ])
                    self.log_message.emit(f"[Sweep] CSV paralelo: {sweep_path}")
                    self._apply_sweep_step()

            time.sleep(0.5)

            # 6. Iniciar timer de log
            self.is_running = True
            self.start_time = time.time()
            
            # Limpa estatísticas
            self.temp_samples.clear()
            self.error_samples.clear()
            self.output_samples.clear()
            
            self.log_timer.start()
            self.log_message.emit("=" * 50)
            self.log_message.emit(">>> TESTE INICIADO <<<")
            self.log_message.emit(f"Setpoint: {settings['oven_setpoint']}°C | PSU: {settings['psu_voltage']}V")
            self.log_message.emit(f"Forno: {config.controller_summary(self._oven_controller)}")
            self.log_message.emit("=" * 50)
            
        except Exception as e:
            self.log_message.emit(f"ERRO CRÍTICO: {e}")
            self.is_running = False
            if self.logger:
                self.logger.close()
            self.test_finished.emit()

    def _resolve_oven_controller(self):
        """Consulta o firmware do forno (GET_CONFIG) para registrar o regime de
        forma honesta. Cai nas constantes PID configuradas — claramente
        marcadas — quando o Arduino está desabilitado ou não responde.
        """
        if not config.ARDUINO_ENABLED:
            return {"type": "UNKNOWN", "raw": None,
                    "source": "arduino-disabled", "params": {}}

        # Dá tempo para o boot do Arduino terminar, se necessário.
        t0 = time.time()
        while not self.arduino.is_ready and (time.time() - t0 < 6):
            time.sleep(0.5)

        info = self.arduino.query_controller_config()
        if info:
            self.log_message.emit("Controlador do forno: " + config.controller_summary(info))
            return info

        self.log_message.emit(
            "AVISO: firmware do forno não respondeu GET_CONFIG — "
            "registrando controlador como fallback de configuração."
        )
        return config.fallback_controller_info()

    def _log_system_config(self, settings):
        """Registra configuração do sistema no início do teste."""
        self.log_message.emit("-" * 50)
        self.log_message.emit("CONFIGURAÇÃO DO TESTE")
        self.log_message.emit("-" * 50)
        self.log_message.emit(f"Nome: {settings['test_name']}")
        self.log_message.emit(f"Setpoint Forno: {settings['oven_setpoint']}°C")
        self.log_message.emit(f"Tensão PSU: {settings['psu_voltage']}V")
        self.log_message.emit(f"Forno: {config.controller_summary(self._oven_controller)}")
        self.log_message.emit(f"Taxa Rampa: {config.DEFAULT_RAMP_RATE_C_PER_SEC}°C/s")
        self.log_message.emit(f"Intervalo Log: {config.LOG_INTERVAL_MS}ms")
        self.log_message.emit("-" * 50)

    @Slot()
    def stop_test(self):
        """Para o teste e todos os dispositivos."""
        self.log_message.emit("Parando teste...")
        self.is_running = False
        self.log_timer.stop()

        self._log_final_statistics()

        # Fecha CSV paralelo do sweep
        if self._sweep_csv_file:
            self._sweep_csv_file.close()
            self._sweep_csv_file   = None
            self._sweep_csv_writer = None
        self._sweep_mode = None

        if config.ARDUINO_ENABLED:
            self.arduino.stop_test_oven()
        if config.PSU_ENABLED:
            self.psu.turn_off()

        if self.logger:
            self.logger.close()
            self.logger = None

        self.log_message.emit("=" * 50)
        self.log_message.emit(">>> TESTE FINALIZADO <<<")
        self.log_message.emit("=" * 50)
        self.test_finished.emit()

    def _log_final_statistics(self):
        """Calcula e registra estatísticas finais do teste."""
        if len(self.temp_samples) < 10:
            return
            
        import statistics
        
        # Usa apenas últimas 60 amostras (1 minuto) para estatísticas de regime
        n_samples = min(60, len(self.temp_samples))
        temp_regime = self.temp_samples[-n_samples:]
        error_regime = self.error_samples[-n_samples:]
        output_regime = self.output_samples[-n_samples:]
        
        self.log_message.emit("-" * 50)
        self.log_message.emit("ESTATÍSTICAS FINAIS (último minuto)")
        self.log_message.emit("-" * 50)
        
        # Temperatura
        temp_mean = statistics.mean(temp_regime)
        temp_std = statistics.stdev(temp_regime) if len(temp_regime) > 1 else 0
        temp_min = min(temp_regime)
        temp_max = max(temp_regime)
        
        self.log_message.emit(f"Temperatura:")
        self.log_message.emit(f"  Média: {temp_mean:.2f}°C")
        self.log_message.emit(f"  Desvio Padrão: {temp_std:.3f}°C")
        self.log_message.emit(f"  Mín/Máx: {temp_min:.2f}°C / {temp_max:.2f}°C")
        self.log_message.emit(f"  Oscilação P-P: {temp_max - temp_min:.2f}°C")
        
        # Erro
        error_mean = statistics.mean(error_regime)
        self.log_message.emit(f"Erro Médio: {error_mean:.2f}°C")
        
        # Output
        output_mean = statistics.mean(output_regime)
        ctype = (self._oven_controller or {}).get("type")
        if ctype == "PID":
            self.log_message.emit(f"Output PID Médio: {output_mean:.1f}%")
            # Decomposição P/I estimada (apenas PID)
            contrib_P = config.PID_KP * error_mean
            contrib_I = output_mean - contrib_P
            self.log_message.emit(f"Contribuição P estimada: {contrib_P:.2f}%")
            self.log_message.emit(f"Contribuição I estimada: {contrib_I:.2f}%")
        else:
            self.log_message.emit(f"Duty médio do atuador: {output_mean:.1f}%")

        # Conformidade JEDEC
        if (temp_max - temp_min) <= 4.0:
            self.log_message.emit("✓ CONFORME JEDEC (±2°C)")
        else:
            self.log_message.emit("✗ NÃO CONFORME JEDEC")
        
        self.log_message.emit("-" * 50)

    def log_data_tick(self):
        """Callback do timer para coleta e registro de dados."""
        if not self.is_running:
            return
            
        try:
            # 1. Coletar dados
            t_oven, sp_oven, out_oven = self.arduino.get_latest_data()
            v_psu, c_psu = self.psu.get_latest_data()
            t_dut, s_dut, v_dut, fail_dut, wrong_dut, correct_dut, errcnt_dut = self.dut.get_latest_data()

            elapsed_time = time.time() - self.start_time

            # 2. Atualizar estatísticas
            self.temp_samples.append(t_oven)
            self.error_samples.append(sp_oven - t_oven)
            self.output_samples.append(out_oven)

            # 3. VCCINT closed-loop trim (E3634A)
            if config.PSU_ENABLED and self.psu.is_running and v_dut > 0:
                err = config.VCCINT_SETPOINT_V - v_dut
                self._psu_cmd_v = max(
                    config.PSU_MIN_V,
                    min(config.PSU_MAX_V, self._psu_cmd_v + config.VOLTAGE_KP * err)
                )
                self.psu.set_voltage(self._psu_cmd_v)

            # 4. Montar linha de dados
            data_row = {
                'time_sec':       elapsed_time,
                'oven_temp':      t_oven,
                'oven_setpoint':  sp_oven,
                'oven_output':    out_oven,
                'psu_cmd_v':      self._psu_cmd_v,
                'psu_voltage':    v_psu,
                'psu_current':    c_psu,
                'dut_temp':       t_dut,
                'dut_slack':      s_dut,
                'dut_volt':       v_dut,
                'dut_fail':       fail_dut,
                'dut_wrong':      wrong_dut,
                'dut_correct':    correct_dut,
                'dut_error_count': errcnt_dut,
            }

            # 5. Log no arquivo principal
            if self.logger:
                self.logger.write_data_row(data_row)

            # 5b. Log no CSV paralelo do sweep (dados brutos)
            if self._sweep_csv_writer and self._sweep_mode:
                target = (self._sweep_steps[self._sweep_idx]
                          if self._sweep_idx < len(self._sweep_steps) else float('nan'))
                self._sweep_csv_writer.writerow([
                    f"{elapsed_time:.3f}",
                    self._sweep_idx + 1,
                    target,
                    f"{v_dut:.4f}",
                    f"{t_oven:.2f}",
                    f"{t_dut:.3f}",
                    s_dut,
                ])

            # 6. Log periódico no terminal (a cada 30s)
            if int(elapsed_time) % 30 == 0 and int(elapsed_time) > 0:
                error = sp_oven - t_oven
                self._log_periodic_status(elapsed_time, t_oven, sp_oven, out_oven, error)

            # 7. Emitir para gráfico
            self.plot_data_update.emit(data_row)

            # 8. DUT temperature outer loop
            self._adjust_oven_outer_loop(t_dut, sp_oven)

            # 9. Verificar limites de segurança
            self._check_safety_limits(t_dut, c_psu, t_oven)

            # 10. Avançar passo do sweep (se ativo)
            if self._sweep_mode:
                self._do_sweep_tick(v_dut, t_oven, s_dut, t_dut, v_psu, c_psu, fail_dut)

        except Exception as e:
            self.log_message.emit(f"ERRO no loop de log: {e}")
            self.stop_test()

    def _log_periodic_status(self, elapsed, temp, setpoint, output, error):
        """Log periódico de status."""
        ctype = (self._oven_controller or {}).get("type")
        if ctype == "PID":
            contrib_P = config.PID_KP * error
            contrib_I = output - contrib_P
            print(f"[{elapsed:.0f}s] T={temp:.2f}°C | SP={setpoint:.1f}°C | "
                  f"Erro={error:.2f}°C | Out={output:.1f}% | "
                  f"P={contrib_P:.1f}% | I≈{contrib_I:.1f}%")
        else:
            # Bang-bang (e demais): a saída é estado do SSR (0/100%); a
            # decomposição P/I não se aplica.
            print(f"[{elapsed:.0f}s] T={temp:.2f}°C | SP={setpoint:.1f}°C | "
                  f"Erro={error:.2f}°C | SSR={output:.0f}%")

    def _adjust_oven_outer_loop(self, dut_temp: float, sp_oven: float):
        """Slow oven-setpoint trim toward the DUT die target (see DieTempOuterLoop)."""
        can_send = config.ARDUINO_ENABLED and self.arduino.is_ready
        new_sp, msg = self._outer_loop.tick(dut_temp, sp_oven, can_send)
        if new_sp is not None:
            resp = self.arduino.set_target_setpoint(new_sp)
            if not (resp or "").startswith("OK"):
                self.log_message.emit(
                    f"DUT outer loop: SET_SP,{new_sp:.2f} not acknowledged ({resp!r})")
        if msg:
            self.log_message.emit(msg)

    def _check_safety_limits(self, t_dut, c_psu, t_oven):
        """Verifica limites de segurança e para o teste se excedidos."""
        if t_dut > config.MAX_DUT_TEMP_C:
            self.log_message.emit(f"!!! ALERTA: Temp DUT ({t_dut:.1f}°C) > {config.MAX_DUT_TEMP_C}°C !!!")
            self.stop_test()

        if config.PSU_ENABLED and c_psu > config.MAX_PSU_CURRENT_A:
            self.log_message.emit(f"!!! ALERTA: Corrente PSU ({c_psu:.3f}A) > {config.MAX_PSU_CURRENT_A}A !!!")
            self.stop_test()

        if config.ARDUINO_ENABLED and t_oven > config.MAX_OVEN_TEMP_C:
            self.log_message.emit(f"!!! ALERTA: Temp Forno ({t_oven:.1f}°C) > {config.MAX_OVEN_TEMP_C}°C !!!")
            self.stop_test()

    # =========================================================================
    #   Sweep automático
    # =========================================================================

    def _apply_sweep_step(self):
        """Aplica o passo atual do sweep (muda tensão ou setpoint do forno)."""
        if not self._sweep_steps or self._sweep_idx >= len(self._sweep_steps):
            return
        target = self._sweep_steps[self._sweep_idx]
        total  = len(self._sweep_steps)

        if self._sweep_mode == 'voltage':
            self._psu_cmd_v = target
            config.VCCINT_SETPOINT_V = target
            self.psu.set_voltage(target)
            self.log_message.emit(
                f"[Sweep] Passo {self._sweep_idx + 1}/{total}: VCCINT → {target:.2f} V"
            )
        else:  # temperature
            if config.ARDUINO_ENABLED and self.arduino.is_ready:
                self.arduino.set_target_setpoint(target)
            self.log_message.emit(
                f"[Sweep] Passo {self._sweep_idx + 1}/{total}: Forno SP → {target:.0f} °C"
            )

        if self.logger:
            unit = 'V' if self._sweep_mode == 'voltage' else '°C'
            self.logger.write_comment(
                f"SWEEP PASSO {self._sweep_idx + 1}/{total}: target={target}{unit}"
            )

        self._sweep_step_data = []
        self._sweep_dwell_ticks = 0
        self._sweep_stable_ticks = 0
        self.sweep_step_changed.emit(self._sweep_idx, target, total, self._sweep_mode)

    def _do_sweep_tick(self, v_dut, t_oven, s_dut, t_dut, v_psu, c_psu, fail_dut):
        """Verifica critério de estabilidade e avança passo quando atingido."""
        if not self._sweep_steps or self._sweep_idx >= len(self._sweep_steps):
            return

        target = self._sweep_steps[self._sweep_idx]
        self._sweep_dwell_ticks += 1
        self._sweep_step_data.append((s_dut, t_dut, v_dut, t_oven, v_psu, c_psu, fail_dut))

        if self._sweep_dwell_ticks < self._sweep_min_dwell:
            return

        measured = v_dut if self._sweep_mode == 'voltage' else t_oven
        if abs(measured - target) < self._sweep_tolerance:
            self._sweep_stable_ticks += 1
        else:
            self._sweep_stable_ticks = 0

        if self._sweep_stable_ticks < self._sweep_required_stable:
            return

        # Critério atingido — avança para o próximo passo
        unit = 'V' if self._sweep_mode == 'voltage' else '°C'
        self.log_message.emit(
            f"[Sweep] Passo {self._sweep_idx + 1} concluído: "
            f"target={target}{unit}, dwell={len(self._sweep_step_data)}s"
        )
        self._sweep_idx += 1

        if self._sweep_idx >= len(self._sweep_steps):
            self.log_message.emit("=" * 50)
            self.log_message.emit(">>> SWEEP AUTOMÁTICO CONCLUÍDO <<<")
            self.log_message.emit("=" * 50)
            self.stop_test()
        else:
            self._apply_sweep_step()

