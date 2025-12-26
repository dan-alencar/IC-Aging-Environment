from PySide6.QtCore import QObject, Signal, Slot, QMutex
from serial_config import SerialThread
from protocol import ProtocolParser, AGING_PKT_LEN, raw_to_temp, raw_to_vcc
import config
import time

# Headers de Roteamento (Envio)
HEADER_CROC = b'\x10'
HEADER_STM  = b'\x20'

class UARTRouter(QObject):
    stm_frame_received = Signal(object)
    log_text_received = Signal(str)      
    connection_status = Signal(str)
    log_message = Signal(str)
    
    # SINAL: Envia dicionário com dados físicos (Temp, Vcc, Slack)
    aging_data_received = Signal(dict) 

    # (Sinal para debug raw se necessário)
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
        
        # 2. Processamento de Pacotes de Aging (Sliding Window)
        # O pacote tem 9 bytes. Estrutura: [TL, TH, 00, SL, SH, VL, VH, 00, AL]
        while len(self._rx_buffer) >= AGING_PKT_LEN:
            # Espia os primeiros 9 bytes
            pkt = self._rx_buffer[:AGING_PKT_LEN]
            
            # Validação: Bytes 2 e 7 devem ser 0x00 (Padding)
            padding_ok = (pkt[2] == 0x00 and pkt[7] == 0x00)
            
            if padding_ok:
                # Decodifica Little Endian (conforme debugger.py)
                raw_temp  = pkt[0] | (pkt[1] << 8)
                raw_slack = pkt[3] | (pkt[4] << 8)
                raw_vcc   = pkt[5] | (pkt[6] << 8)
                alarm     = pkt[8] & 0x01
                
                # Validação Extra: Valores razoáveis
                # Temp != 0xFFFF e Vcc != 0xFFFF (evita falsos positivos com tudo zero)
                valid_values = (raw_temp != 0xFFFF) and (raw_vcc != 0xFFFF)
                
                if valid_values:
                    # Pacote Válido! Processa e remove do buffer.
                    phys_data = {
                        'dut_temp':  round(raw_to_temp(raw_temp), 2),
                        'dut_volt':  round(raw_to_vcc(raw_vcc), 3),
                        'dut_slack': raw_slack,
                        'raw_alarm': alarm
                    }
                    self.aging_data_received.emit(phys_data)
                    
                    # Remove pacote processado
                    del self._rx_buffer[:AGING_PKT_LEN]
                    continue
            
            # Se não validou (padding errado ou valores inválidos),
            # verifica se pode ser um cabeçalho STM (0x10 ou 0x20)
            head = self._rx_buffer[0]
            if head in (0x10, 0x20) and len(self._rx_buffer) >= 4:
                # Parece começo de pacote STM, interrompe a busca por Aging
                # e deixa o ProtocolParser processar o que está no buffer.
                break
                
            # Se não é Aging nem STM, é lixo ou desalinhamento:
            # Descarta 1 byte e tenta de novo (Sliding Window)
            del self._rx_buffer[0]

        # 3. Processamento de Protocolo STM e Texto
        # Se sobrou algo no buffer (que não foi consumido como Aging), passamos para o Parser.
        if self._rx_buffer:
            chunk = bytes(self._rx_buffer)
            
            # O parser processa e retorna eventos identificados
            events = self.parser.feed(chunk)
            
            # Limpeza do Buffer:
            # Como o parser do STM é robusto, se ele encontrou eventos válidos, 
            # podemos assumir que os dados foram consumidos.
            # Para evitar crescimento infinito em caso de ruído, limpamos se eventos ocorreram.
            # (Numa implementação perfeita, o parser retornaria bytes consumidos)
            if events:
                self._rx_buffer.clear()

            for evt in events:
                evt_type = evt[0]
                
                if evt_type in ('ok', 'error'):
                    self.stm_frame_received.emit(evt)
                
                elif evt_type == 'line':
                    raw_msg = evt[1]
                    # Sanitização final
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