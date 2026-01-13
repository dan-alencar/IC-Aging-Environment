# -*- coding: utf-8 -*-
"""
UART Router for CROC FPGA System

Handles bidirectional communication between:
- PC Application (this code)
- FPGA (CROC RISC-V softcore)
- STM32 MCU

Parses text-based sensor output from CROC firmware:
  "F: 0x<alarm_f> | RF: 0x<alarm_rf>"
  
Parses telemetry from STM32:
  "$TEL,Vc,X.XXX,Vi,X.XXX,Io,X.XXX,Et,XX.X,Mt,XX.X*CS"
  
Parses system telemetry from FPGA:
  "$SYS,FT,XX.XX,VI,X.XXX,AF,XXXXXXXX,AR,XXXXXXXX*CS"
"""

from PySide6.QtCore import QObject, Signal, Slot, QMutex
from serial_thread import SerialThread
from protocol import ProtocolParser
import config
import time
import re


# Routing headers (for sending)
HEADER_CROC = b'\x10'
HEADER_STM  = b'\x20'


class UARTRouter(QObject):
    """
    Central UART routing and parsing manager.
    
    Signals:
        stm_frame_received(object): STM32 protocol frame received
        log_text_received(str): Text message for display in log
        connection_status(str): Connection state changed
        log_message(str): General log message
        aging_data_received(dict): Parsed sensor data
        telemetry_received(dict): Parsed telemetry data (STM32 + FPGA)
        raw_data_received(bytes): Raw bytes for debugging
    """
    
    # STM32 protocol events
    stm_frame_received = Signal(object)
    
    # Text logging
    log_text_received = Signal(str)
    connection_status = Signal(str)
    log_message = Signal(str)
    
    # Sensor data (parsed)
    aging_data_received = Signal(dict)
    
    # Telemetry data (STM32 + FPGA System Monitor)
    telemetry_received = Signal(dict)
    
    # Raw data for debugging
    raw_data_received = Signal(bytes)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.serial = None
        self.parser = ProtocolParser()
        self.is_connected = False
        self.last_target = None
        self.ROUTER_TIMEOUT_S = 0.06
        self.route_lock = QMutex()
        
        # RX buffer for reassembling fragmented data
        self._rx_buffer = bytearray()
        
        # Latest telemetry values (accumulated from multiple sources)
        self._telemetry = {
            'vcore': 0.0,
            'vin': 0.0,
            'iout': 0.0,
            'ext_temp': 0.0,
            'mcu_temp': 0.0,
            'fpga_temp': 0.0,
            'vccint': 0.0,
            'alarm_f': 0,
            'alarm_rf': 0,
        }
        
        # Regex patterns for CROC output
        # Pattern 1: "F: 0x<hex> | RF: 0x<hex>"
        self._sensor_regex = re.compile(
            r'F:\s*0x([0-9A-Fa-f]+)\s*\|\s*RF:\s*0x([0-9A-Fa-f]+)',
            re.IGNORECASE
        )
        
        # Pattern 2: Extended format with more sensors
        self._sensor_regex_ext = re.compile(
            r'F:\s*0x([0-9A-Fa-f]+).*?RF:\s*0x([0-9A-Fa-f]+).*?'
            r'OBI_DMX:\s*0x([0-9A-Fa-f]+).*?UART:\s*0x([0-9A-Fa-f]+)',
            re.IGNORECASE
        )
        
        # Pattern 3: STM32 telemetry "$TEL,Vc,X.XXX,Vi,X.XXX,Io,X.XXX,Et,XX.X,Mt,XX.X*CS"
        self._stm_telemetry_regex = re.compile(
            r'\$TEL,Vc,([0-9.]+),Vi,([0-9.]+),Io,([0-9.]+),Et,([0-9.]+),Mt,([0-9.]+)\*([0-9A-Fa-f]{2})',
            re.IGNORECASE
        )
        
        # Pattern 4: FPGA system telemetry "$SYS,FT,XX.XX,VI,X.XXX,AF,XXXXXXXX,AR,XXXXXXXX*CS"
        self._sys_telemetry_regex = re.compile(
            r'\$SYS,FT,([0-9.]+),VI,([0-9.]+),AF,([0-9A-Fa-f]+),AR,([0-9A-Fa-f]+)\*([0-9A-Fa-f]{2})',
            re.IGNORECASE
        )

    def connect_serial(self, port: str = None, baud: int = None):
        """
        Connect to the FPGA serial port.
        
        Args:
            port: Serial port (defaults to config.FPGA_PORT)
            baud: Baud rate (defaults to config.SYSTEM_BAUD)
        """
        if port is None:
            port = config.FPGA_PORT
        if baud is None:
            baud = config.SYSTEM_BAUD
        
        # Disconnect existing connection
        if self.serial and self.serial.isRunning():
            self.serial.stop()
            self.serial.wait()

        self.serial = SerialThread(port, baud, rts=True, dtr=True)
        
        # Connect signals
        self.serial.data_received.connect(self._on_data_received)
        self.serial.error_occurred.connect(self._on_error)
        self.serial.port_opened.connect(self._on_opened)
        self.serial.port_closed.connect(self._on_closed)
        
        self.serial.start()

    def disconnect_serial(self):
        """Disconnect from the serial port."""
        if self.serial:
            self.serial.stop()
            self.serial.wait()
            self.serial = None
            self.is_connected = False

    def is_serial_connected(self) -> bool:
        """Check if serial port is connected."""
        return self.is_connected and self.serial is not None

    def _write_raw(self, data: bytes):
        """Write raw bytes to serial port."""
        if self.serial and self.is_connected:
            self.serial.write_data(data)

    def _send_guarded(self, target_header: bytes, payload: bytes):
        """Send data with routing header and dead-time management."""
        self.route_lock.lock()
        try:
            # Dead time on route change
            if self.last_target != target_header:
                time.sleep(self.ROUTER_TIMEOUT_S)
                self.last_target = target_header
            
            # Send header + payload
            packet = target_header + payload
            self._write_raw(packet)
        finally:
            self.route_lock.unlock()

    def send_to_stm(self, payload: bytes):
        """Send data to STM32 with header 0x20."""
        self._send_guarded(HEADER_STM, payload)

    def send_to_croc(self, payload: bytes):
        """Send data to CROC with header 0x10."""
        self._send_guarded(HEADER_CROC, payload)

    def send_text_to_croc(self, text: str):
        """Send text command to CROC (adds newline)."""
        payload = (text + "\n").encode('utf-8')
        self.send_to_croc(payload)

    @Slot(bytes)
    def _on_data_received(self, data: bytes):
        """Process received serial data."""
        # Emit raw data for debugging
        self.raw_data_received.emit(data)
        
        # Accumulate in buffer
        self._rx_buffer.extend(data)
        
        # Process complete lines
        self._process_buffer()

    def _process_buffer(self):
        """Process the RX buffer, extracting complete lines."""
        while True:
            # Find newline
            newline_idx = -1
            for i, byte in enumerate(self._rx_buffer):
                if byte == 0x0A:  # '\n'
                    newline_idx = i
                    break
            
            if newline_idx >= 0:
                # Extract line (without \n)
                line_bytes = bytes(self._rx_buffer[:newline_idx])
                del self._rx_buffer[:newline_idx + 1]
                
                # Process the line
                self._process_line(line_bytes)
                continue
            
            # No complete line, check for binary protocol data
            if len(self._rx_buffer) > 0:
                first_byte = self._rx_buffer[0]
                
                # Non-printable byte might be STM32 response
                if not (32 <= first_byte <= 126) and first_byte not in [0x0A, 0x0D]:
                    events = self.parser.feed(bytes(self._rx_buffer))
                    if events:
                        self._rx_buffer.clear()
                        for evt in events:
                            self._handle_protocol_event(evt)
                        continue
            
            # Nothing more to process
            break
        
        # Prevent buffer overflow
        if len(self._rx_buffer) > 4096:
            self._rx_buffer = self._rx_buffer[-1024:]

    def _process_line(self, line_bytes: bytes):
        """Process a complete text line from CROC/STM32."""
        try:
            line_str = line_bytes.decode('utf-8', errors='ignore').strip()
        except:
            return
        
        if not line_str:
            return
        
        # Check for STM32 telemetry format: $TEL,...*CS
        stm_match = self._stm_telemetry_regex.search(line_str)
        if stm_match:
            try:
                vcore = float(stm_match.group(1))
                vin = float(stm_match.group(2))
                iout = float(stm_match.group(3))
                ext_temp = float(stm_match.group(4))
                mcu_temp = float(stm_match.group(5))
                # checksum = stm_match.group(6)  # Could verify
                
                # Update telemetry
                self._telemetry.update({
                    'vcore': vcore,
                    'vin': vin,
                    'iout': iout,
                    'ext_temp': ext_temp,
                    'mcu_temp': mcu_temp,
                })
                
                # Emit combined telemetry
                self.telemetry_received.emit(self._telemetry.copy())
                
                # Log
                self.log_text_received.emit(
                    f"[STM32] Vc={vcore:.3f}V Vi={vin:.2f}V Io={iout:.3f}A T={ext_temp:.1f}°C"
                )
                return
            except ValueError:
                pass
        
        # Check for FPGA system telemetry format: $SYS,...*CS
        sys_match = self._sys_telemetry_regex.search(line_str)
        if sys_match:
            try:
                fpga_temp = float(sys_match.group(1))
                vccint = float(sys_match.group(2))
                alarm_f = int(sys_match.group(3), 16)
                alarm_rf = int(sys_match.group(4), 16)
                # checksum = sys_match.group(5)
                
                # Update telemetry
                self._telemetry.update({
                    'fpga_temp': fpga_temp,
                    'vccint': vccint,
                    'alarm_f': alarm_f,
                    'alarm_rf': alarm_rf,
                })
                
                # Emit combined telemetry
                self.telemetry_received.emit(self._telemetry.copy())
                
                # Also emit as aging data for sensor widget
                sensor_data = {
                    'alarm_f': alarm_f,
                    'alarm_rf': alarm_rf,
                    'alarm_f_count': bin(alarm_f).count('1'),
                    'alarm_rf_count': bin(alarm_rf).count('1'),
                    'dut_temp': fpga_temp,
                    'dut_volt': vccint,
                    'dut_slack': bin(alarm_f).count('1') + bin(alarm_rf).count('1'),
                }
                self.aging_data_received.emit(sensor_data)
                
                # Log
                f_count = bin(alarm_f).count('1')
                rf_count = bin(alarm_rf).count('1')
                self.log_text_received.emit(
                    f"[FPGA] T={fpga_temp:.2f}°C VCCINT={vccint:.3f}V Alarms={f_count+rf_count}"
                )
                return
            except ValueError:
                pass
        
        # Try extended sensor pattern first
        match = self._sensor_regex_ext.search(line_str)
        if match:
            try:
                alarm_f = int(match.group(1), 16)
                alarm_rf = int(match.group(2), 16)
                obi_dmx = int(match.group(3), 16)
                uart_alarm = int(match.group(4), 16)
                
                sensor_data = {
                    'alarm_f': alarm_f,
                    'alarm_rf': alarm_rf,
                    'obi_dmx': obi_dmx,
                    'uart_alarm': uart_alarm,
                    'alarm_f_count': bin(alarm_f).count('1'),
                    'alarm_rf_count': bin(alarm_rf).count('1'),
                    'dut_temp': 0.0,
                    'dut_volt': 0.0,
                    'dut_slack': bin(alarm_f).count('1') + bin(alarm_rf).count('1'),
                }
                
                # Update telemetry alarms
                self._telemetry['alarm_f'] = alarm_f
                self._telemetry['alarm_rf'] = alarm_rf
                
                self.aging_data_received.emit(sensor_data)
            except ValueError:
                pass
        else:
            # Try basic two-register pattern
            match = self._sensor_regex.search(line_str)
            if match:
                try:
                    alarm_f = int(match.group(1), 16)
                    alarm_rf = int(match.group(2), 16)
                    
                    sensor_data = {
                        'alarm_f': alarm_f,
                        'alarm_rf': alarm_rf,
                        'alarm_f_count': bin(alarm_f).count('1'),
                        'alarm_rf_count': bin(alarm_rf).count('1'),
                        'dut_temp': 0.0,
                        'dut_volt': 0.0,
                        'dut_slack': bin(alarm_f).count('1') + bin(alarm_rf).count('1'),
                    }
                    
                    # Update telemetry alarms
                    self._telemetry['alarm_f'] = alarm_f
                    self._telemetry['alarm_rf'] = alarm_rf
                    
                    self.aging_data_received.emit(sensor_data)
                except ValueError:
                    pass
        
        # Always emit line to log (unless it was a telemetry packet)
        if not line_str.startswith('$'):
            self.log_text_received.emit(f"[CROC] {line_str}")

    def _handle_protocol_event(self, evt):
        """Handle parsed protocol events."""
        evt_type = evt[0]
        
        if evt_type in ('ok', 'error'):
            self.stm_frame_received.emit(evt)
        elif evt_type == 'line':
            raw_msg = evt[1]
            clean_msg = "".join(c for c in raw_msg if c.isprintable()).strip()
            if clean_msg:
                self.log_text_received.emit(f"[RX] {clean_msg}")

    @Slot(str)
    def _on_opened(self, port: str):
        self.is_connected = True
        self.connection_status.emit(f"Connected: {port}")
        self.log_message.emit(f"Serial port opened: {port}")

    @Slot()
    def _on_closed(self):
        self.is_connected = False
        self.connection_status.emit("Disconnected")
        self.log_message.emit("Serial port closed")

    @Slot(str)
    def _on_error(self, msg: str):
        self.log_message.emit(f"Serial error: {msg}")
