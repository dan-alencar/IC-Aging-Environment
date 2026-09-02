from PySide6.QtCore import QObject, Signal, Slot, QMutex
from serial_config import SerialThread
from protocol import (
    ProtocolParser, raw_to_temp, raw_to_vcc,
    MULTI_SYNC0, MULTI_SYNC1, MULTI_PKT_LEN, parse_multi_sensor_packet,
)
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

        # 2. Processamento de Pacotes de Aging Multi-Sensor (framed: sync +
        # length + checksum -- see multi_sensor_stream.sv / protocol.py).
        # Este branch (experimental-multi-sensor) não emite mais o pacote
        # legado de 9 bytes -- o RTL não instancia mais sensor_stream.
        while len(self._rx_buffer) > 0:
            if (len(self._rx_buffer) >= 2
                    and self._rx_buffer[0] == MULTI_SYNC0
                    and self._rx_buffer[1] == MULTI_SYNC1):
                if len(self._rx_buffer) < MULTI_PKT_LEN:
                    # Ainda não chegou o pacote inteiro, espera mais bytes
                    break

                pkt = bytes(self._rx_buffer[:MULTI_PKT_LEN])
                parsed = parse_multi_sensor_packet(pkt)

                if parsed is not None:
                    phys_data = {
                        'dut_temp':  round(raw_to_temp(parsed['temp_raw'] & 0xFFFF), 2),
                        'dut_volt':  round(raw_to_vcc(parsed['vccint_raw'] & 0xFFFF), 3),
                        'dut_slack': list(parsed['slack']),
                        'dut_alarm': list(parsed['alarm']),
                    }
                    self.aging_data_received.emit(phys_data)
                    del self._rx_buffer[:MULTI_PKT_LEN]
                    continue
                else:
                    # Checksum não bateu -- provavelmente 0xAA 0x55 "falso"
                    # dentro de outro fluxo de bytes. Descarta 1 byte e
                    # tenta ressincronizar (Sliding Window).
                    del self._rx_buffer[0]
                    continue

            # Se não validou, verifica se pode ser um cabeçalho STM (0x10 ou 0x20)
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
            # Limpa ANTES de fazer feed para não re-alimentar os mesmos bytes
            # na próxima chamada caso o parser não produza eventos
            self._rx_buffer.clear()

            events = self.parser.feed(chunk)

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