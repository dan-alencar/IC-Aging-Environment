from PySide6.QtCore import QObject, Signal, Slot, QMutex
from serial_config import SerialThread
from protocol import ProtocolParser, AGING_PKT_LEN, raw_to_temp, raw_to_vcc
import config
import time

# Headers de Roteamento (Envio)
HEADER_CROC = b'\x10'
HEADER_STM  = b'\x20'
HEADER_AGING = b'\x1A'

class UARTRouter(QObject):
    # Sinais existentes...
    stm_frame_received = Signal(object)
    log_text_received = Signal(str)      
    connection_status = Signal(str)
    log_message = Signal(str)
    
    # NOVO SINAL: Envia dicionário com dados físicos (Temp, Vcc, Slack)
    aging_data_received = Signal(dict) 

    # (Sinal antigo croc_data_received pode ser depreciado ou mantido para debug)
    croc_raw_received = Signal(bytes) 

    def __init__(self):
        super().__init__()
        self.serial = None
        self.parser = ProtocolParser()
        self.is_connected = False
        self.last_target = None
        self.ROUTER_TIMEOUT_S = 0.06 
        self.route_lock = QMutex()
        
        # Buffer interno para remontar pacotes fragmentados
        self._rx_buffer = bytearray()

    def connect_serial(self):
        if self.serial and self.serial.isRunning():
            self.serial.stop()
            self.serial.wait()

        self.serial = SerialThread(
            config.ESP32_PORT,
            config.SYSTEM_BAUD,
            rts=True, dtr=True
        )
        
        self.serial.data.connect(self._on_data_received)
        self.serial.error.connect(self._on_error)
        self.serial.opened.connect(self._on_opened)
        self.serial.closed.connect(self._on_closed)
        
        self.serial.start()

    def disconnect_serial(self):
        if self.serial:
            self.serial.stop()
            self.serial.wait()
            self.serial = None

    def _write_raw(self, data: bytes):
        if self.serial and self.is_connected:
            self.serial.write_bytes.emit(data)

    def _send_guarded(self, target_header, payload_no_header):
        """Lógica central de envio atômico."""
        self.route_lock.lock()
        try:
            # 1. Verifica se precisa de Dead Time (Troca de Rota)
            if self.last_target != target_header:
                # O sleep aqui bloqueia a thread do Worker (não a GUI), o que é correto
                time.sleep(self.ROUTER_TIMEOUT_S)
                self.last_target = target_header
            
            # 2. Envia Header (Acorda o Roteador)
            packet = target_header + payload_no_header
            self._write_raw(packet)
            
        finally:
            self.route_lock.unlock()

    def send_to_stm(self, payload_no_header: bytes):
        """Envia para STM com Header 0x20 e gestão de gap."""
        self._send_guarded(HEADER_STM, payload_no_header)

    def send_to_croc(self, payload_no_header: bytes):
        """Envia para CROC com Header 0x10 e gestão de gap."""
        self._send_guarded(HEADER_CROC, payload_no_header)

    @Slot(bytes)
    def _on_data_received(self, data):
        # 1. Acumula no buffer
        self._rx_buffer.extend(data)
        
        # 2. Processamento de Pacotes de Aging (Prioridade Alta - Binário Fixo)
        while True:
            # Procura pelo cabeçalho 0x1A
            try:
                idx = self._rx_buffer.index(HEADER_AGING)
            except ValueError:
                break # Não achou cabeçalho
            
            # Verifica se tem o pacote completo (6 bytes)
            if len(self._rx_buffer) >= idx + AGING_PKT_LEN:
                # Extrai o pacote
                packet = self._rx_buffer[idx : idx + AGING_PKT_LEN]
                
                # Remove do buffer (incluindo lixo anterior ao header, se houver)
                del self._rx_buffer[:idx + AGING_PKT_LEN]
                
                # --- PARSE AGING DATA ---
                # [0:Header][1:TH][2:TL][3:VH][4:VL][5:Alarm]
                raw_temp = (packet[1] << 8) | packet[2]
                raw_vcc  = (packet[3] << 8) | packet[4]
                alarm    = packet[5]
                
                phys_data = {
                    'dut_temp':  round(raw_to_temp(raw_temp), 2),
                    'dut_volt':  round(raw_to_vcc(raw_vcc), 3),
                    'dut_slack': alarm, # 0 ou 1 (ou contador se evoluir)
                    'raw_alarm': alarm
                }
                
                self.aging_data_received.emit(phys_data)
            else:
                # Achou Header, mas pacote incompleto. Espera mais dados.
                break

        # 3. Processamento de Protocolo STM e Texto (O que sobrou no buffer)
        # O ProtocolParser consome e retorna eventos.
        # Importante: Precisamos alimentar o parser apenas com o que NÃO é Aging.
        # Como já removemos os pacotes Aging do self._rx_buffer, podemos passar o resto.
        
        # Para evitar travar o buffer se chegar lixo, processamos e limpamos.
        if self._rx_buffer:
            # Copia para bytes para o parser
            chunk = bytes(self._rx_buffer)
            events = self.parser.feed(chunk)
            
            # Limpa o buffer pois o parser mantém seu próprio estado interno para fragmentos
            # Se quisermos ser perfeitos, o parser deveria retornar quanto consumiu, 
            # mas o seu parser atual processa byte a byte. Vamos assumir que ele consome tudo.
            self._rx_buffer.clear() 

            for evt in events:
                evt_type = evt[0]
                
                if evt_type in ('ok', 'error'):
                    self.stm_frame_received.emit(evt)
                
                elif evt_type == 'line':
                    raw_msg = evt[1]
                    # Sanitização final (Remove caracteres estranhos)
                    clean_msg = "".join(c for c in raw_msg if c.isprintable()).strip()
                    if clean_msg:
                        self.log_text_received.emit(f"[RX] {clean_msg}")

    @Slot(str)
    def _on_opened(self, port):
        self.is_connected = True
        self.connection_status.emit(f"ESP32 Conectado: {port}")

    @Slot()
    def _on_closed(self):
        self.is_connected = False
        self.connection_status.emit("ESP32 Desconectado")

    @Slot(str)
    def _on_error(self, msg):
        self.log_message.emit(f"Erro Serial: {msg}")