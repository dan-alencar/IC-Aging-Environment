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
from logger import DataLogger

# =================================================================
#   WORKER 1: Controlador do Forno (Arduino)
# =================================================================
class ArduinoWorker(QObject):
    """
    Controla o Arduino (PID, SSR, NTC) em um thread separado.
    """
    # Sinais emitidos pelo worker
    log_message = Signal(str)
    data_ready = Signal(float, float, float) # temp_c, setpoint_c, output_pct

    def __init__(self):
        super().__init__()
        self.ser = None
        self.is_running = False
        self._latest_data = (0.0, 0.0, 0.0) # temp, setpoint, output

    @Slot()
    def start(self):
        """Inicia a conexão serial e o loop de polling."""
        try:
            self.ser = serial.Serial(config.ARDUINO_PORT, config.ARDUINO_BAUD, timeout=2)
            self.log_message.emit(f"Arduino conectado em {config.ARDUINO_PORT}")
            self.is_running = True
            
            # Inicia um QTimer para polling (melhor que time.sleep em QThread)
            self.poll_timer = QTimer(self)
            self.poll_timer.setInterval(config.LOG_INTERVAL_MS) # Poll a cada 1s
            self.poll_timer.timeout.connect(self.poll_data)
            self.poll_timer.start()
            
        except serial.SerialException as e:
            self.log_message.emit(f"ERRO (Arduino): {e}")

    @Slot()
    def stop(self):
        """Para o worker e fecha a serial."""
        self.is_running = False
        if hasattr(self, 'poll_timer'):
            self.poll_timer.stop()
        if self.ser and self.ser.is_open:
            self.send_command("STOP_TEST") # Garante que o Arduino pare
            self.ser.close()
        self.log_message.emit("Arduino desconectado.")

    def poll_data(self):
        """Função chamada pelo QTimer para pedir dados."""
        if not self.is_running:
            return
            
        response = self.send_command("GET_DATA")
        if response and response.startswith("DATA,"):
            # "DATA,TempAtual,TempRampa,SaidaPID"
            try:
                parts = response.split(',')
                temp_c = float(parts[1])
                setpoint_c = float(parts[2])
                output_pct = float(parts[3])
                
                self._latest_data = (temp_c, setpoint_c, output_pct)
                self.data_ready.emit(temp_c, setpoint_c, output_pct)
            except (ValueError, IndexError):
                self.log_message.emit(f"ERRO (Arduino): Resposta mal formatada: {response}")

    def get_latest_data(self):
        """Método não-bloqueante para o TestSequencer pegar os dados."""
        return self._latest_data

    def send_command(self, cmd):
        """Envia um comando para o Arduino de forma segura."""
        try:
            if self.ser and self.ser.is_open:
                self.ser.write(f"{cmd}\n".encode('ascii'))
                response = self.ser.readline().decode('ascii').strip()
                if "OK" not in response and "DATA" not in response:
                    self.log_message.emit(f"ARDUINO -> {response}")
                return response
            else:
                self.log_message.emit("ERRO (Arduino): Porta serial não está aberta.")
                return None
        except serial.SerialException as e:
            self.log_message.emit(f"ERRO (Arduino): {e}")
            self.stop()
            return None
    
    # --- Slots Públicos (Comandos da HMI) ---
    @Slot(float)
    def set_target_setpoint(self, temp):
        self.send_command(f"SET_SP,{temp}")
        
    @Slot()
    def start_test_oven(self):
        self.send_command("START_TEST")
        
    @Slot()
    def stop_test_oven(self):
        self.send_command("STOP_TEST")

# =================================================================
#   WORKER 2: Controlador da Fonte (PSU)
# =================================================================
class PSUWorker(QObject):
    """
    Controla a Fonte de Tensão (PSU) em um thread separado.
    Baseado em fonte_serial.py e comandos AT.
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
            self.ser = serial.Serial(config.PSU_PORT, config.PSU_BAUD, timeout=2)
            self.log_message.emit(f"Fonte (PSU) conectada em {config.PSU_PORT}")
            self.is_running = True
            self.poll_timer.start()
        except serial.SerialException as e:
            self.log_message.emit(f"ERRO (PSU): {e}")

    @Slot()
    def stop(self):
        self.is_running = False
        self.poll_timer.stop()
        if self.ser and self.ser.is_open:
            self.send_command("VSET1:0.0") # Desliga a tensão por segurança
            self.send_command("OUT1:0")   # Desliga a saída
            self.ser.close()
        self.log_message.emit("Fonte (PSU) desconectada.")
        
    def poll_data(self):
        if not self.is_running:
            return
            
        try:
            v_str = self.send_command("VOUT1?") # Comando AT para "Ler Tensão"
            c_str = self.send_command("IOUT1?") # Comando AT para "Ler Corrente"
            
            voltage = float(v_str) if v_str else 0.0
            current = float(c_str) if c_str else 0.0
            
            self._latest_data = (voltage, current)
            self.data_ready.emit(voltage, current)
        except Exception as e:
            self.log_message.emit(f"ERRO (PSU) ao ler dados: {e}")
            self._latest_data = (0.0, 0.0)

    def get_latest_data(self):
        return self._latest_data

    def send_command(self, cmd):
        # Implementação de envio de comando AT (similar ao Arduino)
        try:
            if self.ser and self.ser.is_open:
                self.ser.write(f"{cmd}\r\n".encode('ascii')) # Comandos AT usam \r\n
                response = self.ser.readline().decode('ascii').strip()
                return response
            return None
        except serial.SerialException as e:
            self.log_message.emit(f"ERRO (PSU): {e}")
            self.stop()
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

# =================================================================
#   WORKER 3: Leitor do DUT (FPGA)
# =================================================================
class DUTWorker(QObject):
    """
    Controla o DUT (FPGA) em um thread separado.
    Baseado em uart_reader.py.
    """
    log_message = Signal(str)
    data_ready = Signal(float, int) # internal_temp_c, slack
    
    def __init__(self):
        super().__init__()
        self.ser = None
        self.is_running = False
        self._latest_data = (0.0, 0) # temp, slack
        self.poll_timer = QTimer(self)
        self.poll_timer.setInterval(config.LOG_INTERVAL_MS) # Poll a cada 1s
        self.poll_timer.timeout.connect(self.poll_data)

    @Slot()
    def start(self):
        try:
            self.ser = serial.Serial(config.DUT_PORT, config.DUT_BAUD, timeout=2)
            self.log_message.emit(f"DUT (FPGA) conectado em {config.DUT_PORT}")
            self.is_running = True
            self.poll_timer.start()
        except serial.SerialException as e:
            self.log_message.emit(f"ERRO (DUT): {e}")

    @Slot()
    def stop(self):
        self.is_running = False
        self.poll_timer.stop()
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.log_message.emit("DUT (FPGA) desconectado.")
        
    def poll_data(self):
        if not self.is_running:
            return
            
        try:
            # Assume que o FPGA envia dados quando recebe um 'GET'
            self.ser.write(b"GET_DATA\n") 
            response = self.ser.readline().decode('ascii').strip()
            
            # Ex: "DUT_DATA,45.2,1234" (temp, slack)
            if response.startswith("DUT_DATA,"):
                parts = response.split(',')
                temp = float(parts[1])
                slack = int(parts[2])
                self._latest_data = (temp, slack)
                self.data_ready.emit(temp, slack)
            else:
                self.log_message.emit(f"ERRO (DUT): Resposta mal formatada: {response}")
                
        except Exception as e:
            self.log_message.emit(f"ERRO (DUT) ao ler dados: {e}")
            self._latest_data = (0.0, 0)

    def get_latest_data(self):
        return self._latest_data

# =================================================================
#   WORKER 4: O Sequenciador de Teste (O Mestre)
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
        
        self.log_timer = QTimer(self)
        self.log_timer.setInterval(config.LOG_INTERVAL_MS)
        self.log_timer.timeout.connect(self.log_data_tick)

    @Slot(dict)
    def start_test(self, settings):
        """
        Recebe as configurações da HMI e inicia o teste.
        settings = {
            'test_name': str,
            'oven_setpoint': float,
            'psu_voltage': float,
            'kp': float, 'ki': float, 'kd': float
        }
        """
        try:
            # 1. Criar o Logger (arquivo CSV único)
            self.logger = DataLogger(config.LOG_FOLDER, settings['test_name'])
            self.log_message.emit(f"Novo log de teste criado: {self.logger.filepath}")
            
            # 2. Configurar dispositivos
            self.log_message.emit("Configurando dispositivos...")
            self.arduino.set_target_setpoint(settings['oven_setpoint'])
            self.psu.set_voltage(settings['psu_voltage'])
            # (Adicionar envio de ganhos PID para o Arduino se necessário)

            # 3. Ligar os dispositivos
            self.psu.turn_on()
            self.arduino.start_test_oven()
            
            # 4. Iniciar o timer de log
            self.is_running = True
            self.log_timer.start()
            self.log_message.emit(">>> TESTE INICIADO <<<")
            
        except Exception as e:
            self.log_message.emit(f"ERRO ao iniciar teste: {e}")

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

Função chamada pelo QTimer (a cada 1s) para coletar dados
de todos os workers e salvar no CSV.
"""
        if not self.is_running:
            return
            
        try:
            # 1. Coletar dados de todos os workers
            t_oven, sp_oven, out_oven = self.arduino.get_latest_data()
            v_psu, c_psu = self.psu.get_latest_data()
            t_dut, s_dut = self.dut.get_latest_data()
            
            # 2. Montar a linha de dados
            data_row = {
                'timestamp': time.time(),
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
            self.plot_data_update.emit(data_row)
            
            # 5. (Opcional) Lógica de Proteção
            #    [cite: 2595-2598]
            if t_dut > 130.0 or c_psu > 1.5: # Exemplo de limites
                self.log_message.emit("!!! ALERTA DE PROTEÇÃO !!!")
                self.log_message.emit(f"Temp DUT: {t_dut}°C, Corrente PSU: {c_psu}A")
                self.stop_test()

        except Exception as e:
            self.log_message.emit(f"ERRO no loop de log: {e}")
            self.stop_test()