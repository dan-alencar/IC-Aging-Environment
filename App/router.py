# -*- coding: utf-8 -*-
"""
UART Router for CROC FPGA System

Handles bidirectional communication between:
- PC Application (this code)
- FPGA (CROC RISC-V softcore)
- STM32 MCU

Updated for text-based sensor output from CROC firmware:
  "F: 0x<alarm_f> | RF: 0x<alarm_rf>"
"""

from PySide6.QtCore import QObject, Signal, Slot, QMutex
from serial_config import SerialThread
from protocol import ProtocolParser
import config
import time
import re

# Headers de Roteamento (Envio)
HEADER_CROC = b'\x10'
HEADER_STM  = b'\x20'

class UARTRouter(QObject):
    # Signals for STM32 protocol frames
    stm_frame_received = Signal(object)
    
    # Signal for text log messages (displayed in GUI log)
    log_text_received = Signal(str)
    
    # Connection status updates
    connection_status = Signal(str)
    log_message = Signal(str)
    
    # Signal for parsed aging/sensor data (dict with dut_temp, dut_volt, alarm_f, alarm_rf)
    aging_data_received = Signal(dict) 

    # Raw data for debugging
    croc_raw_received = Signal(bytes) 

    def __init__(self):
        super().__init__()
        self.serial = None
        self.parser = ProtocolParser()
        self.is_connected = False
        self.last_target = None
        self.ROUTER_TIMEOUT_S = 0.06 
        self.route_lock = QMutex()
        
        # Buffer interno para remontar pacotes/linhas fragmentados
        self._rx_buffer = bytearray()
        
        # Regex para parsear a saída do firmware CROC
        # Formato: "F: 0x<hex> | RF: 0x<hex>"
        self._sensor_regex = re.compile(
            r'F:\s*0x([0-9A-Fa-f]+)\s*\|\s*RF:\s*0x([0-9A-Fa-f]+)',
            re.IGNORECASE
        )

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
        """Lógica central de envio atômico com gestão de dead-time."""
        self.route_lock.lock()
        try:
            # 1. Verifica se precisa de Dead Time (Troca de Rota)
            if self.last_target != target_header:
                time.sleep(self.ROUTER_TIMEOUT_S)
                self.last_target = target_header
            
            # 2. Envia Header + Payload
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
        """
        Processa dados recebidos da serial.
        
        O CROC envia dados em formato texto:
          "F: 0x12345678 | RF: 0xDEADBEEF\r\n"
        
        O STM32 envia respostas binárias do protocolo.
        """
        # Acumula no buffer
        self._rx_buffer.extend(data)
        
        # Emite raw para debug se necessário
        self.croc_raw_received.emit(bytes(data))
        
        # Processa linhas completas (terminadas em \n ou \r\n)
        self._process_buffer()

    def _process_buffer(self):
        """
        Processa o buffer procurando:
        1. Linhas de texto completas (terminadas em \n)
        2. Frames binários do protocolo STM32
        """
        while True:
            # Procura por newline no buffer
            newline_idx = -1
            for i, byte in enumerate(self._rx_buffer):
                if byte == 0x0A:  # '\n'
                    newline_idx = i
                    break
            
            if newline_idx >= 0:
                # Extrai a linha (sem o \n)
                line_bytes = bytes(self._rx_buffer[:newline_idx])
                # Remove a linha do buffer (incluindo \n)
                del self._rx_buffer[:newline_idx + 1]
                
                # Processa a linha
                self._process_line(line_bytes)
                continue
            
            # Se não encontrou newline, verifica se há frame binário STM32
            # Frames STM32 começam com 0x00-0x0F (ctrl byte com STM_SLAVE=0x00)
            # Mas na prática, respostas STM vêm como bytes soltos após o comando
            
            # Tenta processar com o parser de protocolo para pegar respostas STM
            if len(self._rx_buffer) > 0:
                # Verifica se primeiro byte pode ser início de frame STM32
                first_byte = self._rx_buffer[0]
                
                # STM32 response frame: [Ctrl][data...][CRC_L][CRC_H]
                # Ctrl byte para resposta: 0x00-0x0F (slave, no error/error, func)
                # Mas sem header de roteamento na resposta
                
                # Se não é printable e não é newline, pode ser binário
                if not (32 <= first_byte <= 126) and first_byte not in [0x0A, 0x0D]:
                    # Tenta parsear como protocolo STM32
                    events = self.parser.feed(bytes(self._rx_buffer))
                    if events:
                        # Consumiu dados, limpa buffer
                        self._rx_buffer.clear()
                        for evt in events:
                            self._handle_protocol_event(evt)
                        continue
            
            # Nada mais a processar por agora
            break
        
        # Limita tamanho do buffer para evitar crescimento infinito
        if len(self._rx_buffer) > 4096:
            # Descarta dados antigos se buffer muito grande
            self._rx_buffer = self._rx_buffer[-1024:]

    def _process_line(self, line_bytes: bytes):
        """
        Processa uma linha de texto completa recebida do CROC.
        """
        try:
            # Remove \r se presente
            line_str = line_bytes.decode('utf-8', errors='ignore').strip()
        except:
            return
        
        if not line_str:
            return
        
        # Tenta parsear como dados de sensor
        match = self._sensor_regex.search(line_str)
        if match:
            try:
                alarm_f = int(match.group(1), 16)
                alarm_rf = int(match.group(2), 16)
                
                # Conta bits ativos (alarmes disparados)
                alarm_f_count = bin(alarm_f).count('1')
                alarm_rf_count = bin(alarm_rf).count('1')
                
                # Emite dados parseados
                sensor_data = {
                    'alarm_f': alarm_f,
                    'alarm_rf': alarm_rf,
                    'alarm_f_count': alarm_f_count,
                    'alarm_rf_count': alarm_rf_count,
                    # Compatibilidade com interface antiga
                    'dut_temp': 0.0,      # XADC não implementado ainda
                    'dut_volt': 0.0,      # XADC não implementado ainda
                    'dut_slack': alarm_f_count + alarm_rf_count,  # Total de alarmes
                    'raw_alarm': 1 if (alarm_f or alarm_rf) else 0
                }
                self.aging_data_received.emit(sensor_data)
                
            except ValueError as e:
                # Erro de parsing, apenas loga a linha
                pass
        
        # Sempre emite a linha para o log (permite ver mensagens de debug do firmware)
        self.log_text_received.emit(f"[CROC] {line_str}")

    def _handle_protocol_event(self, evt):
        """
        Processa eventos do parser de protocolo STM32.
        """
        evt_type = evt[0]
        
        if evt_type in ('ok', 'error'):
            self.stm_frame_received.emit(evt)
        elif evt_type == 'line':
            # Texto do parser (fallback)
            raw_msg = evt[1]
            clean_msg = "".join(c for c in raw_msg if c.isprintable()).strip()
            if clean_msg:
                self.log_text_received.emit(f"[RX] {clean_msg}")

    @Slot(str)
    def _on_opened(self, port):
        self.is_connected = True
        self.connection_status.emit(f"FPGA Conectado: {port}")
        self.log_message.emit(f"Serial aberta: {port}")

    @Slot()
    def _on_closed(self):
        self.is_connected = False
        self.connection_status.emit("FPGA Desconectado")

    @Slot(str)
    def _on_error(self, msg):
        self.log_message.emit(f"Erro Serial: {msg}")