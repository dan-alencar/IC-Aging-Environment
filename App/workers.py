"""
Workers (Trabalhadores) de Thread

Cada classe aqui roda em seu próprio thread (QThread) para
conversar com um dispositivo de hardware sem travar a HMI.
"""
from PySide6.QtCore import QObject, Signal, Slot, QThread, QTimer
import serial
import time
from datetime import datetime
import config
import usbtmc
from logger import DataLogger # Importa a classe DataLogger
import threading

# =================================================================
#   WORKER 1: Controlador do Forno (Arduino) - BLINDADO
# =================================================================
class ArduinoWorker(QObject):
    """
    Controla o Arduino (PID, SSR, NTC) com proteção de Thread (Lock).
    Evita colisão entre o envio de comandos e a leitura automática.
    """
    log_message = Signal(str)
    data_ready = Signal(float, float, float) 

    def __init__(self):
        super().__init__()
        self.ser = None
        self.is_running = False
        self._latest_data = (0.0, 0.0, 0.0)
        self.kp = config.DEFAULT_KP
        self.ki = config.DEFAULT_KI
        self.kd = config.DEFAULT_KD
        
        # O 'Lock' é o semáforo que impede acesso simultâneo à porta serial
        self.serial_lock = threading.Lock()

    @Slot()
    def start(self):
        try:
            self.ser = serial.Serial(config.ARDUINO_PORT, config.ARDUINO_BAUD, timeout=2)
            
            self.log_message.emit("Arduino conectado. Aguardando boot e estabilização (3s)...")
            time.sleep(3.0) # Aumentei para 3s por segurança
            
            # Limpeza profunda do buffer inicial
            with self.serial_lock:
                self.ser.reset_input_buffer()
                self.ser.reset_output_buffer()
                # Lê e descarta qualquer linha quebrada que sobrou
                while self.ser.in_waiting:
                    self.ser.readline()

            self.log_message.emit(f"Arduino pronto e sincronizado em {config.ARDUINO_PORT}")
            self.is_running = True
            
            self.poll_timer = QTimer(self)
            self.poll_timer.setInterval(config.LOG_INTERVAL_MS)
            self.poll_timer.timeout.connect(self.poll_data)
            self.poll_timer.start()
            
        except serial.SerialException as e:
            self.log_message.emit(f"ERRO (Arduino): {e}")

    @Slot()
    def stop(self):
        self.is_running = False
        if hasattr(self, 'poll_timer'):
            self.poll_timer.stop()
        
        # Usa o Lock para fechar com segurança
        with self.serial_lock:
            if self.ser and self.ser.is_open:
                try:
                    # Tenta enviar STOP, mas sem esperar resposta para não travar
                    self.ser.write(b"STOP_TEST\n") 
                except: pass
                self.ser.close()
        self.log_message.emit("Arduino desconectado.")

    def poll_data(self):
        """Leitura periódica protegida pelo Lock."""
        if not self.is_running: return
        
        # Tenta adquirir o Lock. Se o 'send_command' estiver usando, ele espera.
        if self.serial_lock.acquire(blocking=False): 
            try:
                if self.ser and self.ser.is_open:
                    # Verifica se tem dados ANTES de tentar ler para evitar bloqueio
                    if self.ser.in_waiting > 0:
                        line = self.ser.readline().decode('ascii', errors='ignore').strip()
                        
                        # Trecho dentro de poll_data, logo após ler 'line':
                        if line.startswith("DATA,"):
                            # Debug temporário: ver o que o Arduino está mandando
                            # print(f"DEBUG ARDUINO RAW: {line}") 
                            try:
                                parts = line.split(',')
                                temp_c = float(parts[1])
                                setpoint_c = float(parts[2])
                                output_pct = float(parts[3])
                                
                                # Se output_pct for > 0, o relé deveria estar batendo
                                self._latest_data = (temp_c, setpoint_c, output_pct)
                                self.data_ready.emit(temp_c, setpoint_c, output_pct)
                            except Exception as e:
                                print(f"Erro de Parse Arduino: {e} na linha: {line}")
            except Exception as e:
                self.log_message.emit(f"Erro Leitura Arduino: {e}")
            finally:
                self.serial_lock.release()

    def get_latest_data(self):
        return self._latest_data

    def send_command(self, cmd):
        """Envia comando de forma atômica (protegida)."""
        # Aqui usamos blocking=True, pois enviar comando é prioridade
        with self.serial_lock:
            try:
                if self.ser and self.ser.is_open:
                    # 1. Limpa o buffer de entrada para não ler um "DATA" antigo
                    # achando que é a resposta do comando "OK"
                    self.ser.reset_input_buffer()
                    
                    # 2. Envia
                    self.ser.write(f"{cmd}\n".encode('ascii'))
                    
                    # 3. Lê a confirmação (esperamos um OK ou erro)
                    # O timeout do serial (2s) garante que não travamos aqui pra sempre
                    response = self.ser.readline().decode('ascii', errors='ignore').strip()
                    
                    if "OK" not in response:
                        # Se não for OK, logamos para debug
                        self.log_message.emit(f"CMD '{cmd}' -> Resposta: '{response}'")
                    return response
            except Exception as e:
                self.log_message.emit(f"ERRO enviando '{cmd}': {e}")
                return None

    # --- Slots Públicos ---
    @Slot(float)
    def set_target_setpoint(self, temp):
        self.send_command(f"SET_SP,{temp:.2f}")

    @Slot(float, float, float)
    def update_pid_gains(self, kp, ki, kd):
        self.kp, self.ki, self.kd = kp, ki, kd
        self.send_command(f"SET_PID,{kp:.4f},{ki:.6f},{kd:.4f}")
        
    @Slot()
    def start_test_oven(self):
        self.send_command("START_TEST")
        
    @Slot()
    def stop_test_oven(self):
        self.send_command("STOP_TEST")

# =================================================================
#   WORKER 2: Controlador da Fonte (PSU)
# =================================================================
class PSUWorker(QObject):
    """
    Controla a Fonte de Tensão (PSU) em um thread separado.
    """
    log_message = Signal(str)
    data_ready = Signal(float, float) # voltage_v, current_a
    
    def __init__(self):
        super().__init__()
        self.ser = None
        self.is_running = False
        self._latest_data = (0.0, 0.0) # voltage, current
        self.poll_timer = QTimer(self)
        self.poll_timer.setInterval(config.LOG_INTERVAL_MS) # Poll a cada 1s
        self.poll_timer.timeout.connect(self.poll_data)

    @Slot()
    def start(self):
        try:
            port_name = config.PSU_PORT
            
            if "usbtmc" in port_name.lower():
                self.log_message.emit(f"Conectando PSU via LIB USBTMC em {port_name}...")
                # Instancia o Wrapper da lib
                self.ser = USBTMCAdapter(port_name)
            else:
                self.log_message.emit(f"Conectando PSU via Serial em {port_name}...")
                self.ser = serial.Serial(port_name, config.PSU_BAUD, timeout=2)

            self.is_running = True
            self.poll_timer.start()
            
        except Exception as e:
            self.log_message.emit(f"ERRO (PSU): {e}")
            self.stop()

    @Slot()
    def stop(self):
        self.is_running = False
        self.poll_timer.stop()
        if self.ser and self.ser.is_open:
            self.send_command("VSET1:0.0") # Desliga a tensão por segurança
            self.send_command("OUT1:0")    # Desliga a saída
            self.ser.close()
        self.log_message.emit("Fonte (PSU) desconectada.")
        
    def poll_data(self):
        if not self.is_running:
            return
            
        try:
            v_str = self.send_command("VOUT1?") # Comando AT para "Ler Tensão"
            c_str = self.send_command("IOUT1?") # Comando AT para "Ler Corrente"
            
            # Tenta converter para float, assume 0.0 em caso de falha de leitura
            voltage = float(v_str) if v_str and self.is_float(v_str) else 0.0
            current = float(c_str) if c_str and self.is_float(c_str) else 0.0
            
            self._latest_data = (voltage, current)
            self.data_ready.emit(voltage, current)
        except Exception as e:
            self.log_message.emit(f"AVISO (PSU) ao ler dados: {e}. Retornando 0.0.")
            self._latest_data = (0.0, 0.0)

    def get_latest_data(self):
        return self._latest_data
        
    def is_float(self, element):
        try:
            float(element)
            return True
        except ValueError:
            return False

    def send_command(self, cmd):
        """Envia um comando para a PSU de forma segura."""
        try:
            if self.ser and self.ser.is_open:
                self.ser.flushInput() 
                self.ser.write(f"{cmd}\r\n".encode('ascii')) # Comandos AT usam \r\n
                response = self.ser.readline().decode('ascii').strip()
                return response
            return None
        except serial.SerialException as e:
            self.log_message.emit(f"ERRO (PSU): {e}")
            self.stop()
            return None
        except Exception as e:
             self.log_message.emit(f"ERRO (PSU): Falha de comunicação: {e}")
             return None

    # --- Slots Públicos ---
    @Slot(float)
    def set_voltage(self, volts):
        self.send_command(f"VSET1:{volts:.3f}")
        
    @Slot()
    def turn_on(self):
        self.send_command("OUT1:1") # 1 = ON
        
    @Slot()
    def turn_off(self):
        self.send_command("OUT1:0") # 0 = OFF

class USBTMCAdapter:
    """
    Adaptador Híbrido Corrigido:
    - Suporta verificação .is_open (Exigido pelo PSUWorker)
    - Suporta .flushInput() (Exigido pelo PSUWorker)
    """
    def __init__(self, port_address):
        self.use_kernel_driver = port_address.startswith("/dev/usbtmc")
        self.inst = None
        self.file = None
        self.port_address = port_address

        try:
            if self.use_kernel_driver:
                # Modo Arquivo (Linux Nativo)
                self.file = open(port_address, 'rb+', buffering=0)
            else:
                # Modo Lib (Windows / VISA)
                self.inst = usbtmc.Instrument(port_address)
                self.inst.timeout = 2
        except Exception as e:
            raise serial.SerialException(f"Erro ao iniciar USBTMC ({port_address}): {e}")

    @property
    def is_open(self):
        """Retorna True se a conexão estiver ativa."""
        if self.use_kernel_driver:
            return self.file is not None and not self.file.closed
        else:
            # Na lib, se o objeto existe, assumimos aberto
            return self.inst is not None

    def write(self, data_bytes):
        try:
            if self.use_kernel_driver:
                self.file.write(data_bytes)
                self.file.flush()
            else:
                cmd_str = data_bytes.decode('ascii').strip()
                self.inst.write(cmd_str)
        except Exception as e:
            print(f"Erro de escrita USBTMC: {e}")

    def readline(self):
        try:
            if self.use_kernel_driver:
                return self.file.readline()
            else:
                return self.inst.read().encode('ascii') + b'\n'
        except Exception:
            return b""

    def flushInput(self):
        """
        Método dummy para compatibilidade com pyserial.
        O PSUWorker chama isso antes de ler.
        """
        # USBTMC geralmente não precisa de flush manual no buffer de entrada
        # da mesma forma que UART, mas se necessário, poderia ser implementado aqui.
        pass

    def close(self):
        if self.use_kernel_driver and self.file:
            self.file.close()
        elif self.inst:
            self.inst.close()

# =================================================================
#   WORKER 3: Leitor do DUT (FPGA) - Modo Binário
# =================================================================
class DUTWorker(QObject):
    """
    Controla o DUT (FPGA) usando protocolo binário.
    Envia 'F', recebe 9 bytes brutos (Temp, Slack, Tensão, Status).
    """
    log_message = Signal(str)
    # Atualizei o sinal para passar mais dados se precisar no futuro, 
    # mas por enquanto mantive temp(float) e slack(int) para compatibilidade com o gráfico.
    data_ready = Signal(float, int) 
    
    def __init__(self):
        super().__init__()
        self.ser = None
        self.is_running = False
        self._latest_data = (0.0, 0) # temp, slack
        self.poll_timer = QTimer(self)
        self.poll_timer.setInterval(config.LOG_INTERVAL_MS) 
        self.poll_timer.timeout.connect(self.poll_data)

    @Slot()
    def start(self):
        try:
            # Abre a porta serial normalmente
            self.ser = serial.Serial(config.DUT_PORT, config.DUT_BAUD, timeout=2)
            self.log_message.emit(f"DUT (FPGA) conectado em {config.DUT_PORT}")
            self.is_running = True
            self.poll_timer.start()
        except serial.SerialException as e:
            self.log_message.emit(f"ERRO (DUT): Porta Serial não encontrada ou ocupada: {e}")

    @Slot()
    def stop(self):
        self.is_running = False
        self.poll_timer.stop()
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.log_message.emit("DUT (FPGA) desconectado.")
        
    def poll_data(self):
        """Envia 'F' e lê 9 bytes binários."""
        if not self.is_running or not self.ser or not self.ser.is_open:
            return
            
        try:
            # 1. Limpa buffer antigo para não ler dados velhos acumulados
            self.ser.reset_input_buffer()
            
            # 2. Envia o comando 'F' (Trigger)
            self.ser.write(b'F')
            
            # 3. Lê exatos 9 bytes (conforme seu código antigo)
            # Estrutura: 3 bytes (Temp) + 2 bytes (Slack) + 3 bytes (Volt) + 1 byte (Fail)
            BYTES_TO_READ = 9
            data = self.ser.read(BYTES_TO_READ)
            
            if len(data) == BYTES_TO_READ:
                # 4. Decodifica Binário (Little Endian)
                raw_temp = int.from_bytes(data[:3], byteorder='little')
                raw_slack = int.from_bytes(data[3:5], byteorder='little')
                # raw_voltage = int.from_bytes(data[5:8], byteorder='little') # Não usado no gráfico ainda
                # raw_failed = data[8] > 0                                    # Não usado no gráfico ainda

                # AVISO: Seu código antigo usava int puro para temp. 
                # Se a FPGA manda "2500" para representar 25.0°C, divida por 100.0 aqui.
                # Por enquanto, vou manter o valor bruto como float.
                temp_c = float(raw_temp) / 1000.0
                slack = int(raw_slack)

                # Validação simples (conforme seu código antigo: ignora zeros)
                if temp_c == 0 and slack == 0:
                    return

                self._latest_data = (temp_c, slack)
                self.data_ready.emit(temp_c, slack)
                
            else:
                # Timeout ou dados incompletos
                pass 
                
        except Exception as e:
            self.log_message.emit(f"ERRO (DUT): Falha de comunicação: {e}")
            self._latest_data = (0.0, 0)

    def get_latest_data(self):
        return self._latest_data
    
# =================================================================
#   WORKER 4: O Sequenciador de Teste (O Mestre)
# =================================================================
class TestSequencer(QObject):
    """
    Orquestra todos os workers e gerencia o log de dados principal.
    Este é o "cérebro" do teste.
    """
    log_message = Signal(str)
    plot_data_update = Signal(dict) # Envia a linha de dados completa para o gráfico
    test_finished = Signal()
    
    def __init__(self, arduino_worker, psu_worker, dut_worker):
        super().__init__()
        self.arduino = arduino_worker
        self.psu = psu_worker
        self.dut = dut_worker
        
        self.logger = None
        self.is_running = False
        self.start_time = 0.0 # Usado para calcular o tempo relativo
        
        # O QTimer é usado para orquestrar o log de dados a cada LOG_INTERVAL_MS
        self.log_timer = QTimer(self)
        self.log_timer.setInterval(config.LOG_INTERVAL_MS)
        self.log_timer.timeout.connect(self.log_data_tick)

    @Slot(dict)
    def start_test(self, settings):
        """
        Recebe as configurações da HMI e inicia o teste com atraso de segurança.
        """
        if self.is_running:
             self.log_message.emit("ERRO: Teste já em execução.")
             return
             
        try:
            # 1. Criar o Logger
            self.logger = DataLogger(config.LOG_FOLDER, settings['test_name'])
            self.log_message.emit(f"Novo log: {self.logger.filepath}")
            
            # --- CORREÇÃO AQUI: PAUSA DE ESTABILIZAÇÃO ---
            # Esperamos 2 segundos para garantir que Arduino e PSU já terminaram 
            # seus processos de boot/conexão (que levam ~3s no total).
            self.log_message.emit("Sincronizando dispositivos (Aguarde)...")
            time.sleep(2.0) 
            # ---------------------------------------------

            self.log_message.emit("Enviando parâmetros...")
            
            # Configuração de Setpoint e Ganhos PID (ArduinoWorker)
            # Agora o Arduino já deve estar pronto para ouvir
            self.arduino.set_target_setpoint(settings['oven_setpoint'])
            time.sleep(0.1) # Pequena pausa entre comandos seriais
            self.arduino.update_pid_gains(settings['kp'], settings['ki'], settings['kd'])
            time.sleep(0.1)

            # Configuração de Tensão (PSUWorker)
            self.psu.set_voltage(settings['psu_voltage'])
            time.sleep(0.5)
            
            # Ligar os dispositivos
            self.log_message.emit("Ligando saídas...")
            self.psu.turn_on()
            self.arduino.start_test_oven() # Envia o comando crucial "START_TEST"
            
            # 3. Iniciar o timer de log
            self.is_running = True
            self.start_time = time.time()
            self.log_timer.start()
            self.log_message.emit(">>> TESTE INICIADO <<<")
            
        except Exception as e:
            self.log_message.emit(f"ERRO CRÍTICO ao iniciar teste: {e}")
            self.stop_test()

    @Slot()
    def stop_test(self):
        """Para o teste e todos os dispositivos."""
        if not self.is_running:
            return
            
        self.log_message.emit("Parando teste...")
        self.is_running = False
        self.log_timer.stop()
        
        # Desligar dispositivos
        self.arduino.stop_test_oven()
        self.psu.turn_off()
        
        if self.logger:
            self.logger.close()
            self.logger = None
            
        self.log_message.emit(">>> TESTE PARADO <<<")
        self.test_finished.emit()

    def log_data_tick(self):
        """
        Local de Registro (Tick de Log)

        Função chamada pelo QTimer (a cada 1s) para coletar dados
        de todos os workers e salvar no CSV/gráfico.
        """
        if not self.is_running:
            return
            
        try:
            current_time = time.time()
            elapsed_time = current_time - self.start_time
            
            # 1. Coletar dados dos workers (usando os buffers _latest_data)
            t_oven, sp_oven, out_oven = self.arduino.get_latest_data()
            v_psu, c_psu = self.psu.get_latest_data()
            t_dut, s_dut = self.dut.get_latest_data()
            
            # 2. Montar a linha de dados
            data_row = {
                'timestamp': elapsed_time, # Tempo relativo para o gráfico/log
                'oven_temp': t_oven,
                'oven_setpoint': sp_oven,
                'oven_output': out_oven,
                'psu_voltage': v_psu,
                'psu_current': c_psu,
                'dut_temp': t_dut,
                'dut_slack': s_dut
            }
            
            # 3. Escrever no log e emitir para o gráfico
            if self.logger:
                self.logger.write_data_row(data_row)
                
            self.plot_data_update.emit(data_row)
            
            # 4. (Opcional) Lógica de Proteção
            if t_dut > 130.0 or c_psu > 1.5:
                self.log_message.emit("!!! ALERTA DE PROTEÇÃO: LIMITE EXCEDIDO !!!")
                self.log_message.emit(f"Temp DUT: {t_dut}°C, Corrente PSU: {c_psu}A. Parando o teste.")
                self.stop_test()

        except Exception as e:
            self.log_message.emit(f"ERRO CRÍTICO no loop de log: {e}")
            self.stop_test()