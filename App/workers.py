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
        self.is_ready = False # <--- NOVO: Flag de Prontidão

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
            self.is_ready = True # <--- AGORA ESTÁ PRONTO
            
            self.poll_timer = QTimer(self)
            self.poll_timer.setInterval(config.LOG_INTERVAL_MS)
            self.poll_timer.timeout.connect(self.poll_data)
            self.poll_timer.start()
            
        except serial.SerialException as e:
            self.log_message.emit(f"ERRO (Arduino): {e}")
            self.is_ready = False # Se falhar, a flag fica False

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
            """Leitura periódica protegida pelo Lock (AGORA BLOQUEANTE)."""
            if not self.is_running: return
            
            # O 'with' garante que esta leitura não conflita com o send_command
            with self.serial_lock: 
                try:
                    if self.ser and self.ser.is_open:
                        
                        # 1. ENVIA O COMANDO DE SOLICITAÇÃO DE DADOS (Trigger)
                        self.ser.write(b"GET_DATA\n") 
                        
                        # 2. LÊ A RESPOSTA
                        # O timeout de 2s da porta serial será usado se o Arduino não responder.
                        line = self.ser.readline().decode('ascii', errors='ignore').strip()
                            
                        # 3. PROCESSA A LINHA
                        if line.startswith("DATA,"):
                            # Debug temporário: ver o que o Arduino está mandando
                            #print(f"DEBUG ARDUINO RAW: {line}") 
                            try:
                                parts = line.split(',')
                                temp_c = float(parts[1])
                                setpoint_c = float(parts[2])
                                output_pct = float(parts[3])
                                
                                self._latest_data = (temp_c, setpoint_c, output_pct)
                                self.data_ready.emit(temp_c, setpoint_c, output_pct)
                            except Exception as e:
                                print(f"Erro de Parse Arduino: {e} na linha: {line}")
                                
                except Exception as e:
                    self.log_message.emit(f"Erro Leitura Arduino: {e}")

    def get_latest_data(self):
        return self._latest_data

    def send_command(self, cmd):
        """Envia comando de forma atômica (protegida)."""
        response = None
        
        try:
            # Tenta adquirir o Lock e executar a operação de I/O atômica
            with self.serial_lock:
                if self.ser and self.ser.is_open:
                    # 1. Limpa o buffer de entrada
                    self.ser.reset_input_buffer()
                    
                    # 2. Envia
                    self.ser.write(f"{cmd}\n".encode('ascii'))
                    
                    # 3. Lê a confirmação
                    response = self.ser.readline().decode('ascii', errors='ignore').strip()

        except Exception as e:
            # CRÍTICO: Qualquer exceção de I/O/Lock retorna None
            print(f"DEBUG CRASH: Comando '{cmd}' falhou. EXCEÇÃO: {type(e).__name__} - {e}")
            self.log_message.emit(f"ERRO fatal enviando '{cmd}'")
            return None 
        
        # Lógica de Checagem e Retorno AGORA ESTÁ FORA DO BLOCO de I/O do Lock
        # Se chegamos aqui, o I/O foi concluído sem exceções críticas.
        
        print(f"DEBUG RESPOSTA BRUTA: CMD='{cmd}' -> '{response}'")
        
        if response is None or "OK" not in response:
            self.log_message.emit(f"CMD '{cmd}' -> Resposta: '{response}' (FALHOU)")

        return response
            
    # --- Slots Públicos ---
    @Slot(float)
    def set_target_setpoint(self, temp):
        return self.send_command(f"SET_SP,{int(temp)}")

    @Slot(float, float, float)
    def update_pid_gains(self, kp, ki, kd):
        self.kp, self.ki, self.kd = kp, ki, kd
        return self.send_command(f"SET_GAINS,{kp:.2f},{ki:.5f},{kd:.2f}")
        
    @Slot()
    def start_test_oven(self):
        return self.send_command("START_TEST")

    @Slot()
    def stop_test_oven(self):
        return self.send_command("STOP_TEST")

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
            
            # --- CORREÇÃO CRÍTICA: Ativa o modo Remoto ITECH ---
            # Isso garante que a fonte obedeça aos comandos SCPI do PC.
            self.send_command("SYST:REMote")
            self.log_message.emit("Fonte PSU definida para modo remoto.")
            self.send_command("VOLT 1.0") # Seta a tensão para 0V
            self.send_command("OUTP 1")    # Desliga a saída
            
            self.poll_timer.start()
            
        except Exception as e:
            self.log_message.emit(f"ERRO (PSU): {e}")
            self.stop()

    @Slot()
    def stop(self):
        self.is_running = False
        self.poll_timer.stop()
        if self.ser and self.ser.is_open:
            # CORREÇÃO: Usar comandos SCPI corretos para desligar.
            self.send_command("VOLT 0.0") # Seta a tensão para 0V
            self.send_command("OUTP 0")    # Desliga a saída
            self.ser.close()
        self.log_message.emit("Fonte (PSU) desconectada.")
        
    def poll_data(self):
        if not self.is_running:
            return
            
        try:
            # CORREÇÃO: Usar comandos SCPI padrão MEASure
            v_str = self.send_command("MEAS:VOLT?") # SCPI: Measure Voltage [cite: uploaded file: ITECH_IT6500_Programming-Guide.pdf]
            c_str = self.send_command("MEAS:CURR?") # SCPI: Measure Current [cite: uploaded file: ITECH_IT6500_Programming-Guide.pdf]
            
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
                # Comandos SCPI ITECH geralmente usam \n ou \r\n como terminação
                self.ser.write(f"{cmd}\n".encode('ascii')) 
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
        # CORREÇÃO: Usar comando SCPI padrão VOLTage
        self.send_command(f"VOLT {volts:.3f}") # SCPI: Set Voltage
        
    @Slot()
    def turn_on(self):
        # CORREÇÃO: Usar comando SCPI padrão OUTPut
        self.send_command("OUTP 1") # 1 = ON
        
    @Slot()
    def turn_off(self):
        # CORREÇÃO: Usar comando SCPI padrão OUTPut
        self.send_command("OUTP 0") # 0 = OFF

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
                # Você pode precisar configurar o usbtmc.Instrument aqui
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
                # CORREÇÃO CRÍTICA: Não usar strip() para preservar o \n ou \r\n/código de terminação
                cmd_str = data_bytes.decode('ascii') 
                self.inst.write(cmd_str)
        except Exception as e:
            print(f"Erro de escrita USBTMC: {e}")

    def readline(self):
        try:
            if self.use_kernel_driver:
                return self.file.readline()
            else:
                # Adiciona \n para simular a leitura serial e garantir que a resposta seja completa
                return self.inst.read().encode('ascii') + b'\n'
        except Exception:
            return b""

    def flushInput(self):
        """
        Método dummy para compatibilidade com pyserial.
        """
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
        self.start_time = time.time()
        
        self.log_timer = QTimer(self)
        self.log_timer.setInterval(config.LOG_INTERVAL_MS)
        self.log_timer.timeout.connect(self.log_data_tick)

    @Slot(dict)
    def start_test(self, settings):
        """
        Inicia o teste. Espera o Arduino, envia comandos críticos 
        com validação de resposta 'OK'.
        """
        if self.is_running:
            self.log_message.emit("ERRO: Teste já em execução.")
            return
                
        try:
            # 1. Criar o Logger
            self.logger = DataLogger(config.LOG_FOLDER, settings['test_name'])
            self.log_message.emit(f"Novo log: {self.logger.filepath}")
            
            # --- ESPERA ROBUSTA: Garantir que o Worker terminou o sleep ---
            self.log_message.emit("Aguardando Arduino finalizar boot (máx 6s)...")
            
            timeout_s = 6
            start_wait = time.time()
            while not self.arduino.is_ready and (time.time() - start_wait < timeout_s):
                time.sleep(0.5) 

            if not self.arduino.is_ready:
                 raise Exception("Arduino não respondeu após o tempo de inicialização.")

            self.log_message.emit("Arduino está pronto. Enviando configurações...")
            
            # 2. Configurações críticas com validação
            
            # Ganhos PID (Comando sequencial: 3 comandos)
            # update_pid_gains agora envia 3 comandos e retorna OK se todos tiverem sucesso.
            #response_pid = self.arduino.update_pid_gains(settings['kp'], settings['ki'], settings['kd'])
            #if response_pid is None or "OK" not in response_pid:
            #    raise Exception(f"Falha ao configurar PID. Resposta: {response_pid}")
            #time.sleep(0.1)

            # Setpoint (SP) (Usa integer/float minimalista)
            response_sp = self.arduino.set_target_setpoint(settings['oven_setpoint'])
            
            if response_sp is None or "OK" not in response_sp:
                raise Exception(f"Falha ao configurar SP. Resposta: {response_sp}")
            time.sleep(0.1)
            
            # 3. Configuração de Tensão
            self.psu.set_voltage(settings['psu_voltage'])
            time.sleep(0.3)
            
            # 4. Ligar os dispositivos e iniciar o teste
            self.log_message.emit("Ligando saídas e ativando controle...")
            self.psu.turn_on()
            time.sleep(0.3)
            
            response_start = self.arduino.start_test_oven() 
            if response_start is None or "OK" not in response_start:
                 raise Exception(f"Falha ao iniciar teste. Resposta: {response_start}")

            time.sleep(0.5) 
            
            # 5. Iniciar o timer de log
            self.is_running = True
            self.start_time = time.time()
            self.log_timer.start()
            self.log_message.emit(">>> TESTE INICIADO <<<")
            
        except Exception as e:
            self.log_message.emit(f"ERRO CRÍTICO ao iniciar teste: {e}")
            
            # --- CORREÇÃO: Remova self.stop_test() para evitar loops ---
            # Em vez de self.stop_test, fazemos a limpeza mínima:
            
            self.is_running = False
            if self.logger:
                 self.logger.close()
            
            # self.stop_test() # <--- REMOVA ESTA LINHA
            
            self.log_message.emit(">>> TESTE PARADO <<<")
            self.test_finished.emit() # <--- Mantenha apenas o sinal de parada

    @Slot()
    def stop_test(self):
        """Para o teste e todos os dispositivos."""
        self.log_message.emit("Parando teste...")
        self.is_running = False
        self.log_timer.stop()
        
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

        Função chamada pelo QTimer (a cada LOG_INTERVAL_MS) para coletar dados
        e salvar no CSV.
        """
        if not self.is_running:
            return
            
        try:
            # 1. Coletar dados de todos os workers (simplificado)
            t_oven, sp_oven, out_oven = self.arduino.get_latest_data()
            v_psu, c_psu = self.psu.get_latest_data()
            t_dut, s_dut = self.dut.get_latest_data()
            
            # 2. Montar a linha de dados
            data_row = {
                'time_sec': time.time() - self.start_time, # <--- TEMPO RELATIVO
                'oven_temp': t_oven,
                'oven_setpoint': sp_oven,
                'oven_output': out_oven,
                'psu_voltage': v_psu,
                'psu_current': c_psu,
                'dut_temp': t_dut,
                'dut_slack': s_dut
            }
            
            # 3. Escrever no log
            if self.logger:
                self.logger.write_data_row(data_row)
                
            # 4. Emitir dados para o gráfico
            self.plot_data_update.emit(data_row) # <--- Emite o dicionário completo

            # 5. (Opcional) Lógica de Proteção
            if t_dut > 130.0 or c_psu > 1.5:
                self.log_message.emit("!!! ALERTA DE PROTEÇÃO: LIMITE EXCEDIDO !!!")
                self.log_message.emit(f"Temp DUT: {t_dut}°C, Corrente PSU: {c_psu}A. Parando o teste.")
                self.stop_test()

        except Exception as e:
            self.log_message.emit(f"ERRO CRÍTICO no loop de log: {e}")
            self.stop_test()