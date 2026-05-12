from PySide6.QtCore import QObject, Signal, Slot, QTimer
import time
import serial
import threading
import config

# Imports da Nova IHM
from commands import build_vcore_command, build_page_command, build_message_command
from protocol import decode_ctrl, compute_crc16_modbus, CRC_ENDIAN, ERR_STR

# =================================================================
#   WORKER 1: Controlador do Forno (Arduino)
# =================================================================
class ArduinoWorker(QObject):
    log_message = Signal(str)
    data_ready = Signal(float, float, float) 

    def __init__(self):
        super().__init__()
        self.ser = None
        self.is_running = False
        self._latest_data = (0.0, 0.0, 0.0)
        self.serial_lock = threading.Lock()
        self.poll_timer = None 

    @Slot()
    def start(self):
        try:
            self.ser = serial.Serial(config.ARDUINO_PORT, config.ARDUINO_BAUD, timeout=2)
            self.log_message.emit("Arduino conectado. Aguardando boot...")
            time.sleep(2.0) 
            with self.serial_lock:
                self.ser.reset_input_buffer()
                self.ser.reset_output_buffer()
            
            self.is_running = True
            
            self.poll_timer = QTimer()
            self.poll_timer.setInterval(config.LOG_INTERVAL_MS)
            self.poll_timer.timeout.connect(self.poll_data)
            self.poll_timer.start()
            
        except Exception as e:
            self.log_message.emit(f"ERRO Arduino: {e}")

    @Slot()
    def stop(self):
        self.is_running = False
        if self.poll_timer:
            self.poll_timer.stop()
            self.poll_timer.deleteLater()
            self.poll_timer = None

        with self.serial_lock:
            if self.ser and self.ser.is_open:
                try: self.ser.write(b"STOP_TEST\n") 
                except: pass
                self.ser.close()
        self.log_message.emit("Arduino desconectado.")

    def poll_data(self):
        if not self.is_running: return
        with self.serial_lock: 
            try:
                if self.ser and self.ser.is_open:
                    self.ser.write(b"GET_DATA\n") 
                    line = self.ser.readline().decode('ascii', errors='ignore').strip()
                    if line.startswith("DATA,"):
                        parts = line.split(',')
                        if len(parts) >= 4:
                            t = float(parts[1])
                            sp = float(parts[2])
                            out = float(parts[3])
                            self._latest_data = (t, sp, out)
                            self.data_ready.emit(t, sp, out)
            except Exception as e:
                pass

    def get_latest_data(self): return self._latest_data

    def _send_cmd(self, cmd):
        with self.serial_lock:
            if self.ser and self.ser.is_open:
                self.ser.reset_input_buffer()
                self.ser.write(f"{cmd}\n".encode('ascii'))

    @Slot(float)
    def set_target_setpoint(self, val): self._send_cmd(f"SET_SP,{int(val)}")
    @Slot(float)
    def update_kp(self, val): self._send_cmd(f"SET_KP,{val:.2f}")
    @Slot(float)
    def update_ki(self, val): self._send_cmd(f"SET_KI,{val:.5f}")
    @Slot(float)
    def update_kd(self, val): self._send_cmd(f"SET_KD,{val:.2f}")
    @Slot()
    def start_test_oven(self): self._send_cmd("START_TEST")
    @Slot()
    def stop_test_oven(self): self._send_cmd("STOP_TEST")


# =================================================================
#   WORKER 2: STM32 (Fonte e Sistema)
# =================================================================
class STMWorker(QObject):
    log_message = Signal(str)
    data_ready = Signal(float, float) # Tensão, Corrente
    
    def __init__(self, router):
        super().__init__()
        self.router = router
        self.router.stm_frame_received.connect(self._on_frame_received)
        self.is_running = False
        self._curr_v = 0.0

    @Slot()
    def start(self): self.is_running = True
    @Slot()
    def stop(self): self.is_running = False

    def _send_with_crc(self, payload_from_commands, log_prefix):
        core_packet = payload_from_commands[1:] 
        crc = compute_crc16_modbus(core_packet)
        crc_bytes = crc.to_bytes(2, CRC_ENDIAN)
        final_payload = core_packet + crc_bytes
        
        hex_str = ' '.join(f'{b:02X}' for b in final_payload)
        self.log_message.emit(f"[STM TX] {log_prefix} [Hex: {hex_str}]")
        
        self.router.send_to_stm(final_payload)

    @Slot(float)
    def set_voltage(self, volts):
        if not self.is_running: return
        payload, log_str, _ = build_vcore_command(volts)
        self._send_with_crc(payload, log_str)
        self._curr_v = volts
        self.data_ready.emit(volts, 0.0) 

    @Slot(int)
    def set_page(self, page):
        if not self.is_running: return
        payload, log_str, _ = build_page_command(page)
        self._send_with_crc(payload, log_str)

    @Slot(str)
    def send_manual_message(self, msg):
        try:
            payload, log_str, _ = build_message_command(msg)
            self._send_with_crc(payload, log_str)
        except Exception as e:
            self.log_message.emit(f"Erro msg: {e}")
            
    @Slot()
    def turn_off(self): self.set_voltage(0.0)

    @Slot(object)
    def _on_frame_received(self, event):
        status, ctrl, c1, c2 = event
        if status == 'error':
            _, err_code, _ = decode_ctrl(ctrl)
            err_name = ERR_STR.get(err_code, f"0x{err_code:02X}")
            self.log_message.emit(f"[STM RX] Erro: {err_name}")

    def get_latest_data(self): return (self._curr_v, 0.0)


# =================================================================
#   WORKER 3: CROC (FPGA DUT) - POLLING ATIVADO
# =================================================================
class CROCWorker(QObject):
    log_message = Signal(str)
    
    def __init__(self, router):
        super().__init__()
        self.router = router
        self.is_running = False
        
        # Variáveis de Estado da FPGA
        self._temp = 0.0
        self._slack = 0
        self._volt = 0.0
        
    @Slot()
    def start(self):
        self.is_running = True
        # Conecta ao novo sinal do Router
        self.router.aging_data_received.connect(self._on_aging_data)
        self.log_message.emit("CROC Worker iniciado (Monitoramento FPGA).")

    @Slot()
    def stop(self):
        self.is_running = False
        try:
            self.router.aging_data_received.disconnect(self._on_aging_data)
        except:
            pass

    @Slot(dict)
    def _on_aging_data(self, data):
        """Recebe dados processados do Router (0x1A Packet)."""
        if not self.is_running: return
        
        self._temp  = data.get('dut_temp', 0.0)
        self._volt  = data.get('dut_volt', 0.0)
        self._slack = data.get('dut_slack', 0)
        
        # Opcional: Logar alarmes críticos
        if self._slack > 0:
             # Evita spam de log, logar só mudanças de estado se quiser
             pass 

    def get_latest_data(self):
        """Retorna (Temp, Slack, Vcc_Internal) para o Logger/Gráfico"""
        return self._temp, self._slack, self._volt

    def send_manual_command(self, cmd: str):
        # Envia texto puro + Enter para o terminal do CROC
        payload = (cmd + "\n").encode('utf-8')
        self.router.send_to_croc(payload)

# =================================================================
#   SEQUENCIADOR
# =================================================================
from logger import DataLogger 

class TestSequencer(QObject):
    log_message = Signal(str)
    plot_data_update = Signal(dict)
    test_finished = Signal()
    
    def __init__(self, arduino, stm, croc):
        super().__init__()
        self.arduino = arduino
        self.stm = stm
        self.croc = croc
        self.logger = None
        self.running = False
        self.t0 = 0
        self.log_timer = None

    @Slot(dict)
    def start_test(self, settings):
        if self.running: return
        try:
            self.logger = DataLogger(config.LOG_FOLDER, settings['test_name'])
            
            self.arduino.update_kp(settings['kp'])
            time.sleep(0.1)
            self.arduino.update_ki(settings['ki'])
            time.sleep(0.1)
            self.arduino.update_kd(settings['kd'])
            time.sleep(0.1)
            self.arduino.set_target_setpoint(settings['oven_setpoint'])
            
            self.stm.set_voltage(settings['psu_voltage'])
            time.sleep(0.5)
            
            self.arduino.start_test_oven()
            
            self.running = True
            self.t0 = time.time()
            
            self.log_timer = QTimer()
            self.log_timer.setInterval(config.LOG_INTERVAL_MS)
            self.log_timer.timeout.connect(self.log_data_tick)
            self.log_timer.start()
            
            self.log_message.emit(">>> TESTE INICIADO <<<")
            
        except Exception as e:
            self.log_message.emit(f"ERRO CRÍTICO START: {e}")
            self.stop_test()

    @Slot()
    def stop_test(self):
        self.running = False
        if self.log_timer:
            self.log_timer.stop()
            self.log_timer.deleteLater()
            self.log_timer = None
            
        self.arduino.stop_test_oven()
        self.stm.turn_off()
        if self.logger: self.logger.close()
        self.log_message.emit(">>> TESTE PARADO <<<")
        self.test_finished.emit()

    def log_data_tick(self):
        if not self.running: return
        try:
            # Pega dados dos workers
            t_oven, sp, out = self.arduino.get_latest_data()
            v_stm, _ = self.stm.get_latest_data()
            
            # AGORA O CROC RETORNA DADOS REAIS!
            t_dut, s_dut, v_dut = self.croc.get_latest_data() 
            
            row = {
                'time_sec': time.time() - self.t0,
                'oven_temp': t_oven, 'oven_setpoint': sp, 'oven_output': out,
                'psu_voltage': v_stm, 'psu_current': 0.0,
                'dut_temp': t_dut,    # Temperatura interna da FPGA
                'dut_slack': s_dut,   # Alarme de Timing
                'dut_volt': v_dut     # VCCINT da FPGA
            }
            
            # Salva no CSV
            if self.logger: self.logger.write_data_row(row)
            
            # Emite para a GUI atualizar gráficos
            self.plot_data_update.emit(row)
            
        except Exception as e:
            print(f"Erro no log tick: {e}")