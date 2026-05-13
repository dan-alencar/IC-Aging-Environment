"""
=============================================================================
TCC - Workers de Thread (VERSÃO FINAL)
=============================================================================
Cada classe roda em thread separada (QThread) para comunicação com hardware
sem travar a interface gráfica.

Workers:
  - ArduinoWorker: Controle do forno (PID, SSR, NTC)
  - PSUWorker: Controle da fonte de alimentação (VISA/SCPI)
  - DUTWorker: Comunicação com FPGA (sensor de slack)
  - TestSequencer: Orquestrador do teste

Autor: [Seu Nome]
Data: Janeiro/2026
=============================================================================
"""
from PySide6.QtCore import QObject, Signal, Slot, QTimer
import serial
import time
from datetime import datetime
import config
import pyvisa as visa
from logger import DataLogger
import threading


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
#   WORKER 2: Controlador da Fonte (PSU) - PyVISA
# =============================================================================
class PSUWorker(QObject):
    """
    Controla a fonte de alimentação programável via PyVISA (SCPI).
    
    Sinais:
        log_message(str): Mensagem para o log
        data_ready(float, float): voltage_v, current_a
    """
    log_message = Signal(str)
    data_ready = Signal(float, float)
    
    def __init__(self):
        super().__init__()
        self.rm = None
        self.inst = None
        self.is_running = False
        self._latest_data = (0.0, 0.0)
        
        self.poll_timer = QTimer(self)
        self.poll_timer.setInterval(config.LOG_INTERVAL_MS)
        self.poll_timer.timeout.connect(self.poll_data)

    @Slot()
    def start(self):
        """Inicializa conexão com PSU via VISA."""
        try:
            self.rm = visa.ResourceManager('@py')
            self.inst = self.rm.open_resource(config.PSU_PORT)
            self.inst.timeout = 5000
            self.inst.read_termination = '\n'
            self.inst.write_termination = '\n'
            
            idn = self.inst.query("*IDN?").strip()
            self.log_message.emit(f"PSU conectada: {idn}")
            
            # Configura limites de segurança
            self.inst.write(f"CURR {config.MAX_PSU_CURRENT_A}")
            self.inst.write(f"VOLT {config.MAX_PSU_VOLTAGE_V}")
            
            self.is_running = True
            self.poll_timer.start()
            
        except Exception as e:
            self.log_message.emit(f"ERRO (PSU): {e}")

    @Slot()
    def stop(self):
        """Encerra conexão com PSU."""
        self.is_running = False
        self.poll_timer.stop()
        
        try:
            if self.inst:
                self.inst.write("OUTP OFF")
                self.inst.close()
            if self.rm:
                self.rm.close()
        except: 
            pass
        self.log_message.emit("PSU desconectada.")

    def poll_data(self):
        """Leitura periódica de tensão e corrente."""
        if not self.is_running or not self.inst:
            return
            
        try:
            voltage = float(self.inst.query("MEAS:VOLT?").strip())
            current = float(self.inst.query("MEAS:CURR?").strip())
            
            self._latest_data = (voltage, current)
            self.data_ready.emit(voltage, current)
            
        except Exception as e:
            self.log_message.emit(f"Erro Leitura PSU: {e}")

    def get_latest_data(self):
        return self._latest_data

    @Slot(float)
    def set_voltage(self, voltage):
        """Define tensão de saída."""
        if self.inst:
            try:
                self.inst.write(f"VOLT {voltage:.3f}")
                self.log_message.emit(f"PSU: Tensão definida para {voltage:.3f}V")
            except Exception as e:
                self.log_message.emit(f"Erro ao definir tensão: {e}")

    @Slot()
    def turn_on(self):
        """Liga saída da PSU."""
        if self.inst:
            try:
                self.inst.write("OUTP ON")
                self.log_message.emit("PSU: Saída LIGADA")
            except Exception as e:
                self.log_message.emit(f"Erro ao ligar PSU: {e}")

    @Slot()
    def turn_off(self):
        """Desliga saída da PSU."""
        if self.inst:
            try:
                self.inst.write("OUTP OFF")
                self.log_message.emit("PSU: Saída DESLIGADA")
            except Exception as e:
                self.log_message.emit(f"Erro ao desligar PSU: {e}")


# =============================================================================
#   WORKER 3: Controlador do DUT (FPGA)
# =============================================================================
class DUTWorker(QObject):
    """
    Comunicação com FPGA para leitura do sensor de slack.
    
    Protocolo: Comando 'F' + 9 bytes binários (Little Endian)
    Formato: [TEMP 3 bytes][SLACK 2 bytes][VOLT 3 bytes][FAIL 1 byte]
    
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
        self._latest_data = (0.0, 0, 0.0) # temp, slack, voltage
        
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
                timeout=2 # Timeout de 2s é crucial para o read(9) funcionar
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
        """Envia 'F' e espera bloqueando até receber 9 bytes."""
        if not self.is_running or not self.ser or not self.ser.is_open:
            return
            
        try:
            # 1. Limpa buffer antigo para garantir que lemos a resposta do comando ATUAL
            #self.ser.reset_input_buffer()
            
            # 2. Envia o comando 'F' (Trigger)
            self.ser.write(b'F')
            
            # 3. Lê exatos 9 bytes. 
            # REMOVIDO time.sleep(0.1): O read já espera os dados chegarem (devido ao timeout=2)
            BYTES_TO_READ = 9
            data = self.ser.read(BYTES_TO_READ)
            
            if len(data) == BYTES_TO_READ:
                # 4. Decodifica Binário (Little Endian)
                raw_temp = int.from_bytes(data[0:3], byteorder='little')
                raw_slack = int.from_bytes(data[3:5], byteorder='little')
                raw_voltage = int.from_bytes(data[5:8], byteorder='little')
                # raw_fail = data[8] # Byte de falha (não usado por enquanto)

                # Conversão para unidades físicas
                temp_c = float(raw_temp) / 1000.0
                slack = int(raw_slack)
                voltage = float(raw_voltage) / 1000.0

                # Filtra leituras zeradas (comum na inicialização do FPGA)
                if temp_c == 0 and slack == 0 and voltage == 0:
                    return

                self._latest_data = (temp_c, slack, voltage)
                self.data_ready.emit(temp_c, slack, voltage)
                
            else:
                # Se cair aqui, ocorreu TIMEOUT (FPGA não respondeu em 2s)
                # O print b'' e "Nope" que você via indicava que data estava vazio.
                # Não vamos spammar o log, apenas ignorar ou logar silenciosamente no terminal
                if len(data) == 0:
                    print(f"DUT: Sem resposta (Timeout). Baud rate {config.DUT_BAUD} correto?")
                else:
                    print(f"DUT: Pacote incompleto ({len(data)}/{BYTES_TO_READ} bytes)")
                
        except Exception as e:
            self.log_message.emit(f"ERRO (DUT): {e}")
            self._latest_data = (0.0, 0, 0.0)

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
            self.logger = DataLogger(config.LOG_FOLDER, settings['test_name'])
            self.log_message.emit(f"Log criado: {self.logger.filepath}")
            
            # Log dos parâmetros do sistema
            self._log_system_config(settings)
            
            # 2. Aguardar Arduino
            self.log_message.emit("Aguardando Arduino (máx 6s)...")
            
            timeout_s = 6
            start_wait = time.time()
            while not self.arduino.is_ready and (time.time() - start_wait < timeout_s):
                time.sleep(0.5) 

            if not self.arduino.is_ready:
                raise Exception("Arduino não respondeu após inicialização.")

            self.log_message.emit("Arduino pronto. Configurando...")
            
            # 3. Configurar Setpoint
            response_sp = self.arduino.set_target_setpoint(settings['oven_setpoint'])
            if response_sp is None or "OK" not in response_sp:
                raise Exception(f"Falha ao configurar SP. Resposta: {response_sp}")
            time.sleep(0.1)
            
            # 4. Configurar PSU
            self.psu.set_voltage(settings['psu_voltage'])
            time.sleep(0.3)
            
            # 5. Ligar dispositivos
            self.log_message.emit("Ligando saídas...")
            self.psu.turn_on()
            time.sleep(0.3)
            
            response_start = self.arduino.start_test_oven() 
            if response_start is None or "OK" not in response_start:
                raise Exception(f"Falha ao iniciar teste. Resposta: {response_start}")

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
        
        # Log estatísticas finais
        self._log_final_statistics()
        
        self.arduino.stop_test_oven()
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
            t_dut, s_dut, v_dut = self.dut.get_latest_data()
            
            elapsed_time = time.time() - self.start_time
            
            # 2. Atualizar estatísticas
            self.temp_samples.append(t_oven)
            self.error_samples.append(sp_oven - t_oven)
            self.output_samples.append(out_oven)
            
            # 3. Montar linha de dados
            data_row = {
                'time_sec': elapsed_time,
                'oven_temp': t_oven,
                'oven_setpoint': sp_oven,
                'oven_output': out_oven,
                'psu_voltage': v_psu,
                'psu_current': c_psu,
                'dut_temp': t_dut,
                'dut_slack': s_dut,
                'dut_volt': v_dut
            }
            
            # 4. Log no arquivo
            if self.logger:
                self.logger.write_data_row(data_row)
            
            # 5. Log periódico no terminal (a cada 30s)
            if int(elapsed_time) % 30 == 0 and int(elapsed_time) > 0:
                error = sp_oven - t_oven
                self._log_periodic_status(elapsed_time, t_oven, sp_oven, out_oven, error)
                
            # 6. Emitir para gráfico
            self.plot_data_update.emit(data_row)

            # 7. Verificar limites de segurança
            self._check_safety_limits(t_dut, c_psu, t_oven)

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

    def _check_safety_limits(self, t_dut, c_psu, t_oven):
        """Verifica limites de segurança e para o teste se excedidos."""
        if t_dut > config.MAX_DUT_TEMP_C:
            self.log_message.emit(f"!!! ALERTA: Temp DUT ({t_dut:.1f}°C) > {config.MAX_DUT_TEMP_C}°C !!!")
            self.stop_test()
            
        if c_psu > config.MAX_PSU_CURRENT_A:
            self.log_message.emit(f"!!! ALERTA: Corrente PSU ({c_psu:.3f}A) > {config.MAX_PSU_CURRENT_A}A !!!")
            self.stop_test()
            
        if t_oven > config.MAX_OVEN_TEMP_C:
            self.log_message.emit(f"!!! ALERTA: Temp Forno ({t_oven:.1f}°C) > {config.MAX_OVEN_TEMP_C}°C !!!")
            self.stop_test()