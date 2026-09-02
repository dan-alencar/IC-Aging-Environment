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
from protocol import MULTI_NUM_CHANNELS, MULTI_PKT_LEN, parse_multi_sensor_packet
import threading

_DUT_OUTER_TICK_INTERVAL = 1800   # ticks between oven-sp adjustments (~30 min at 1 s/tick)
_DUT_TEMP_TOLERANCE_C = 3.0       # ±3 °C dead-band around DUT target
_OVEN_SP_STEP_C = 1.0             # °C per adjustment step


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
            self.log_message.emit(f"Parâmetros PID fixos: {config.get_pid_info_string()}")
            
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
        return self.send_command(f"SET_SP,{int(temp)}")
        
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
    Comunicação com FPGA para leitura do array de sensores.

    Protocolo (experimental-multi-sensor): pacote autoframed de
    multi_sensor_stream.sv (sync 0xAA 0x55 + length + checksum) -- ver
    protocol.py. Substitui o pacote legado de 15 bytes: este branch não
    tem canário funcional para reportar (wrong/correct/error_count/fail
    não existem mais), e slack/alarm agora são um valor por canal.

    Sinais:
        log_message(str): Mensagem para o log
        data_ready(float, list, float, list): temp_c, slack (por canal),
            voltage, alarm (por canal)
    """
    log_message = Signal(str)
    data_ready = Signal(float, list, float, list)

    def __init__(self, num_channels=MULTI_NUM_CHANNELS):
        super().__init__()
        self.ser = None
        self.is_running = False
        self.num_channels = num_channels
        self._latest_data = (0.0, [0] * num_channels, 0.0, [False] * num_channels)

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
                timeout=2 # Timeout de 2s é crucial para o read(MULTI_PKT_LEN) funcionar
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
        """Aguarda e decodifica um pacote multi-sensor do FPGA."""
        if not self.is_running or not self.ser or not self.ser.is_open:
            return

        try:
            # Descarta bytes residuais de pacotes anteriores para manter o alinhamento.
            self.ser.reset_input_buffer()

            # 'T' (0x54) triggers the next phase sweep on the FPGA.
            # Falls back to the 1 Hz timer if this byte arrives during a sweep.
            self.ser.write(b'\x54')

            data = self.ser.read(MULTI_PKT_LEN)

            if len(data) == MULTI_PKT_LEN:
                parsed = parse_multi_sensor_packet(data, self.num_channels)
                if parsed is None:
                    print("DUT: pacote multi-sensor com sync/checksum inválido")
                    return

                temp_c  = parsed['temp_raw']   / 1000.0
                voltage = parsed['vccint_raw'] / 1000.0
                slack   = parsed['slack']
                alarm   = parsed['alarm']

                # Filtra leituras zeradas (comum na inicialização do FPGA)
                if temp_c == 0 and voltage == 0 and all(s == 0 for s in slack):
                    return

                self._latest_data = (temp_c, slack, voltage, alarm)
                self.data_ready.emit(temp_c, slack, voltage, alarm)

            else:
                if len(data) == 0:
                    print(f"DUT: Sem resposta (Timeout). Baud rate {config.DUT_BAUD} correto?")
                else:
                    print(f"DUT: Pacote incompleto ({len(data)}/{MULTI_PKT_LEN} bytes)")

        except Exception as e:
            self.log_message.emit(f"ERRO (DUT): {e}")
            self._latest_data = (0.0, [0] * self.num_channels, 0.0, [False] * self.num_channels)

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
    stats_update = Signal(list)  # list of per-channel {min,max,mean,alarm_count} dicts
    test_finished = Signal()
    sweep_step_changed = Signal(int, float, int, str)  # (step_idx_0based, target, total_steps, mode)

    def __init__(self, arduino_worker, psu_worker, dut_worker, num_channels=MULTI_NUM_CHANNELS):
        super().__init__()
        self.arduino = arduino_worker
        self.psu = psu_worker
        self.dut = dut_worker
        self.num_channels = num_channels

        self.logger = None
        self.is_running = False
        self.start_time = time.time()

        # Estatísticas em tempo real
        self.temp_samples = []
        self.error_samples = []
        self.output_samples = []

        # Estatísticas por canal (min/max/média/contagem de alarmes)
        self._chan_stats = None
        self._tick_count = 0

        # DUT temperature outer loop
        self._dut_target_temp = 0.0
        self._outer_tick = 0

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

    def _reset_channel_stats(self):
        self._chan_stats = [
            {'min': None, 'max': None, 'sum': 0.0, 'n': 0, 'alarm_count': 0}
            for _ in range(self.num_channels)
        ]
        self._tick_count = 0

    def _update_channel_stats(self, slack, alarm):
        for i in range(self.num_channels):
            s = self._chan_stats[i]
            v = slack[i] if i < len(slack) else 0
            s['min'] = v if s['min'] is None else min(s['min'], v)
            s['max'] = v if s['max'] is None else max(s['max'], v)
            s['sum'] += v
            s['n'] += 1
            if i < len(alarm) and alarm[i]:
                s['alarm_count'] += 1

    def get_channel_stats(self):
        """Returns a list of per-channel {min, max, mean, alarm_count} dicts,
        or None if no test has run yet."""
        if not self._chan_stats:
            return None
        out = []
        for s in self._chan_stats:
            mean = (s['sum'] / s['n']) if s['n'] else 0.0
            out.append({'min': s['min'] or 0, 'max': s['max'] or 0,
                        'mean': mean, 'alarm_count': s['alarm_count']})
        return out

    def _check_divergence(self, alarm):
        """Flags a channel whose alarm rate this test diverges noticeably
        from the group mean. Checked every 30 ticks to avoid log spam."""
        if self._tick_count == 0 or self._tick_count % 30 != 0:
            return
        rates = [s['alarm_count'] / s['n'] if s['n'] else 0.0 for s in self._chan_stats]
        if not rates:
            return
        mean_rate = sum(rates) / len(rates)
        for i, r in enumerate(rates):
            if abs(r - mean_rate) > 0.20:
                self.log_message.emit(
                    f"[Divergência] Canal {i}: taxa de alarme {r:.1%} "
                    f"(média do grupo {mean_rate:.1%})"
                )

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
            self._dut_target_temp = float(settings.get('dut_target_temp', 0.0))
            self._outer_tick = 0
            self._reset_channel_stats()
            self.logger = DataLogger(config.LOG_FOLDER, settings['test_name'])
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
            self.log_message.emit(f"PID: {config.get_pid_info_string()}")
            self.log_message.emit("=" * 50)
            
        except Exception as e:
            self.log_message.emit(f"ERRO CRÍTICO: {e}")
            self.is_running = False
            if self.logger:
                self.logger.close()
            self.test_finished.emit()

    def _log_system_config(self, settings):
        """Registra configuração do sistema no início do teste."""
        self.log_message.emit("-" * 50)
        self.log_message.emit("CONFIGURAÇÃO DO TESTE")
        self.log_message.emit("-" * 50)
        self.log_message.emit(f"Nome: {settings['test_name']}")
        self.log_message.emit(f"Setpoint Forno: {settings['oven_setpoint']}°C")
        self.log_message.emit(f"Tensão PSU: {settings['psu_voltage']}V")
        self.log_message.emit(f"Kp = {config.PID_KP:.4f}")
        self.log_message.emit(f"Ki = {config.PID_KI:.6f}")
        self.log_message.emit(f"Kd = {config.PID_KD:.4f}")
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
        self.log_message.emit(f"Output PID Médio: {output_mean:.1f}%")
        
        # Decomposição P/I estimada
        contrib_P = config.PID_KP * error_mean
        contrib_I = output_mean - contrib_P
        self.log_message.emit(f"Contribuição P estimada: {contrib_P:.2f}%")
        self.log_message.emit(f"Contribuição I estimada: {contrib_I:.2f}%")
        
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
            t_dut, s_dut, v_dut, a_dut = self.dut.get_latest_data()

            elapsed_time = time.time() - self.start_time

            # 2. Atualizar estatísticas
            self.temp_samples.append(t_oven)
            self.error_samples.append(sp_oven - t_oven)
            self.output_samples.append(out_oven)
            self._update_channel_stats(s_dut, a_dut)
            self._tick_count += 1
            self._check_divergence(a_dut)

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
                'dut_volt':       v_dut,
            }
            for i in range(self.num_channels):
                data_row[f'dut_slack_ch{i}'] = s_dut[i] if i < len(s_dut) else 0
                data_row[f'dut_alarm_ch{i}'] = int(a_dut[i]) if i < len(a_dut) else 0

            # 5. Log no arquivo principal
            if self.logger:
                self.logger.write_data_row(data_row)

            # 5b. Log no CSV paralelo do sweep (dados brutos). Usa o pior
            # canal (mínimo slack) como valor único representativo -- a
            # série completa por canal já está no CSV principal.
            worst_slack = min(s_dut) if s_dut else 0
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
                    worst_slack,
                ])

            # 6. Log periódico no terminal (a cada 30s)
            if int(elapsed_time) % 30 == 0 and int(elapsed_time) > 0:
                error = sp_oven - t_oven
                self._log_periodic_status(elapsed_time, t_oven, sp_oven, out_oven, error)

            # 7. Emitir para gráfico
            self.plot_data_update.emit(data_row)
            self.stats_update.emit(self.get_channel_stats())

            # 8. DUT temperature outer loop
            self._adjust_oven_outer_loop(t_dut, sp_oven)

            # 9. Verificar limites de segurança
            self._check_safety_limits(t_dut, c_psu, t_oven)

            # 10. Avançar passo do sweep (se ativo)
            if self._sweep_mode:
                self._do_sweep_tick(v_dut, t_oven, worst_slack, t_dut, v_psu, c_psu)

        except Exception as e:
            self.log_message.emit(f"ERRO no loop de log: {e}")
            self.stop_test()

    def _log_periodic_status(self, elapsed, temp, setpoint, output, error):
        """Log periódico de status."""
        contrib_P = config.PID_KP * error
        contrib_I = output - contrib_P
        
        print(f"[{elapsed:.0f}s] T={temp:.2f}°C | SP={setpoint:.1f}°C | "
              f"Erro={error:.2f}°C | Out={output:.1f}% | "
              f"P={contrib_P:.1f}% | I≈{contrib_I:.1f}%")

    def _adjust_oven_outer_loop(self, dut_temp: float, sp_oven: float):
        """Shift oven setpoint every ~30 min to bring DUT temp to target."""
        if self._dut_target_temp <= 0 or dut_temp <= 0:
            return
        self._outer_tick += 1
        if self._outer_tick < _DUT_OUTER_TICK_INTERVAL:
            return
        self._outer_tick = 0
        error = dut_temp - self._dut_target_temp
        if abs(error) <= _DUT_TEMP_TOLERANCE_C:
            return
        step = _OVEN_SP_STEP_C if error < 0 else -_OVEN_SP_STEP_C
        new_sp = max(0.0, min(config.MAX_OVEN_TEMP_C, sp_oven + step))
        if new_sp == sp_oven:
            return
        if config.ARDUINO_ENABLED and self.arduino.is_ready:
            self.arduino.set_target_setpoint(new_sp)
        self.log_message.emit(
            f"DUT outer loop: DUT={dut_temp:.1f}°C target={self._dut_target_temp:.0f}°C "
            f"→ oven_sp {sp_oven:.0f}→{new_sp:.0f}°C"
        )

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

    def _do_sweep_tick(self, v_dut, t_oven, s_dut, t_dut, v_psu, c_psu):
        """Verifica critério de estabilidade e avança passo quando atingido.
        s_dut aqui é o pior canal (mínimo slack) -- não há mais um canário
        funcional único (fail) neste branch."""
        if not self._sweep_steps or self._sweep_idx >= len(self._sweep_steps):
            return

        target = self._sweep_steps[self._sweep_idx]
        self._sweep_dwell_ticks += 1
        self._sweep_step_data.append((s_dut, t_dut, v_dut, t_oven, v_psu, c_psu))

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

