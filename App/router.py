from PySide6.QtCore import QObject, Signal, Slot, QMutex
from serial_config import SerialThread
from protocol import ProtocolParser
import config
import time

# Headers de Roteamento (Hardware FPGA)
HEADER_CROC = b'\x10'
HEADER_STM  = b'\x20'

class UARTRouter(QObject):
    """
    Roteador Central:
    - Gerencia o tráfego compartilhado.
    - [FIX]: Insere Dead Time de 60ms ao trocar de alvo.
    - [NEW]: Thread-safe com QMutex.
    """
    stm_frame_received = Signal(object)
    croc_data_received = Signal(bytes)
    log_text_received = Signal(str)      
    
    connection_status = Signal(str)
    log_message = Signal(str)

    def __init__(self):
        super().__init__()
        self.serial = None
        self.parser = ProtocolParser()
        self.is_connected = False
        
        # Controle de fluxo
        self.last_target = None
        self.ROUTER_TIMEOUT_S = 0.06 # 60ms (Hardware tem 50ms)
        
        # Mutex para garantir uso exclusivo do canal Serial durante a troca de rota
        self.route_lock = QMutex()

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
        # 1. Processa Protocolo e Texto Misto
        events = self.parser.feed(data)
        
        for evt in events:
            evt_type = evt[0]
            
            if evt_type in ('ok', 'error'):
                # Eventos de protocolo vão para o Worker do STM
                self.stm_frame_received.emit(evt)
            
            elif evt_type == 'line':
                raw_msg = evt[1]
                
                # --- SANITIZAÇÃO DE TEXTO ---
                # Remove qualquer byte não-imprimível que tenha escapado
                # Isso elimina símbolos estranhos como , ÿ, etc.
                clean_msg = "".join(c for c in raw_msg if c.isprintable())
                clean_msg = clean_msg.strip()
                
                # Só emite se sobrou algo legível (ex: "Tick", "Tock")
                if clean_msg:
                    self.log_text_received.emit(f"[RX] {clean_msg}")

        # 2. Dados brutos continuam indo para o gráfico do CROC (sem filtro)
        self.croc_data_received.emit(data)

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