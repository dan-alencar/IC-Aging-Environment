# -*- coding: utf-8 -*-
"""
Telemetry Widget with Real-Time Graphs

Displays live telemetry data from:
- STM32: Vcore, Vin, Iout, External Temperature
- FPGA System Monitor: Internal Temperature, VCCINT

Uses pyqtgraph for high-performance real-time plotting.
"""

import time
from collections import deque
from dataclasses import dataclass, field
from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QGroupBox, QFrame, QSplitter, QSizePolicy,
    QComboBox, QSpinBox, QPushButton, QCheckBox
)
from PySide6.QtCore import Qt, Signal, Slot, QTimer
from PySide6.QtGui import QFont, QColor

# Try to import pyqtgraph, fallback to simple display if not available
try:
    import pyqtgraph as pg
    PYQTGRAPH_AVAILABLE = True
    
    # Configure pyqtgraph for dark theme
    pg.setConfigOptions(
        antialias=True,
        background='#1e1e1e',
        foreground='#d4d4d4'
    )
except ImportError:
    PYQTGRAPH_AVAILABLE = False
    print("Warning: pyqtgraph not installed. Graphs will be disabled.")


@dataclass
class TelemetryData:
    """Container for telemetry data point."""
    timestamp: float = 0.0
    
    # STM32 data
    vcore: float = 0.0          # Vcore to FPGA (V)
    vin: float = 0.0            # Input voltage (V)
    iout: float = 0.0           # Output current (A)
    ext_temp: float = 0.0       # External temperature (°C)
    mcu_temp: float = 0.0       # MCU temperature (°C)
    
    # FPGA System Monitor data
    fpga_temp: float = 0.0      # FPGA internal temperature (°C)
    vccint: float = 0.0         # VCCINT voltage (V)
    
    # Aging sensor data
    alarm_f: int = 0
    alarm_rf: int = 0


class TelemetryBuffer:
    """Circular buffer for telemetry history."""
    
    def __init__(self, max_points: int = 500):
        self.max_points = max_points
        self.timestamps = deque(maxlen=max_points)
        self.vcore = deque(maxlen=max_points)
        self.vin = deque(maxlen=max_points)
        self.iout = deque(maxlen=max_points)
        self.ext_temp = deque(maxlen=max_points)
        self.fpga_temp = deque(maxlen=max_points)
        self.vccint = deque(maxlen=max_points)
        self.alarm_count = deque(maxlen=max_points)
        self._start_time = time.time()
    
    def add(self, data: TelemetryData):
        """Add a data point to the buffer."""
        rel_time = time.time() - self._start_time
        self.timestamps.append(rel_time)
        self.vcore.append(data.vcore)
        self.vin.append(data.vin)
        self.iout.append(data.iout)
        self.ext_temp.append(data.ext_temp)
        self.fpga_temp.append(data.fpga_temp)
        self.vccint.append(data.vccint)
        
        # Count active alarm bits
        alarm_count = bin(data.alarm_f).count('1') + bin(data.alarm_rf).count('1')
        self.alarm_count.append(alarm_count)
    
    def clear(self):
        """Clear all data."""
        self.timestamps.clear()
        self.vcore.clear()
        self.vin.clear()
        self.iout.clear()
        self.ext_temp.clear()
        self.fpga_temp.clear()
        self.vccint.clear()
        self.alarm_count.clear()
        self._start_time = time.time()
    
    def get_arrays(self):
        """Return data as lists for plotting."""
        return {
            'time': list(self.timestamps),
            'vcore': list(self.vcore),
            'vin': list(self.vin),
            'iout': list(self.iout),
            'ext_temp': list(self.ext_temp),
            'fpga_temp': list(self.fpga_temp),
            'vccint': list(self.vccint),
            'alarm_count': list(self.alarm_count),
        }


class ValueDisplay(QFrame):
    """A styled display for a single telemetry value."""
    
    def __init__(self, label: str, unit: str = "", decimals: int = 3, parent=None):
        super().__init__(parent)
        self.unit = unit
        self.decimals = decimals
        self._value = 0.0
        
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: #252526;
                border: 1px solid #3f3f46;
                border-radius: 4px;
                padding: 5px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(2)
        
        # Label
        self.label = QLabel(label)
        self.label.setStyleSheet("color: #888; font-size: 9pt; border: none;")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)
        
        # Value
        self.value_label = QLabel("---")
        self.value_label.setStyleSheet("""
            color: #4fc3f7; 
            font-size: 14pt; 
            font-weight: bold;
            border: none;
        """)
        self.value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.value_label)
    
    def setValue(self, value: float):
        """Update the displayed value."""
        self._value = value
        fmt = f"{{:.{self.decimals}f}}"
        text = fmt.format(value)
        if self.unit:
            text += f" {self.unit}"
        self.value_label.setText(text)
    
    def setColor(self, color: str):
        """Set the value text color."""
        self.value_label.setStyleSheet(f"""
            color: {color}; 
            font-size: 14pt; 
            font-weight: bold;
            border: none;
        """)


class TelemetryWidget(QWidget):
    """
    Main telemetry display widget with real-time graphs.
    """
    
    # Signal emitted when new data is received
    data_updated = Signal(TelemetryData)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Data buffer
        self.buffer = TelemetryBuffer(max_points=500)
        self.latest_data = TelemetryData()
        
        # Plot references
        self.plots = {}
        self.curves = {}
        
        self._setup_ui()
        
        # Update timer for plots (60 FPS max)
        self.plot_timer = QTimer()
        self.plot_timer.timeout.connect(self._update_plots)
        self.plot_timer.start(100)  # 10 Hz update rate
    
    def _setup_ui(self):
        """Build the user interface."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Title
        title = QLabel("System Telemetry Monitor")
        title.setStyleSheet("font-size: 14pt; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # Current values display
        values_group = QGroupBox("Current Values")
        values_layout = QGridLayout(values_group)
        values_layout.setSpacing(10)
        
        # STM32 values (Row 0)
        stm_label = QLabel("STM32 (Power Supply)")
        stm_label.setStyleSheet("color: #ffc107; font-weight: bold;")
        values_layout.addWidget(stm_label, 0, 0, 1, 4)
        
        self.disp_vcore = ValueDisplay("Vcore", "V", 3)
        self.disp_vin = ValueDisplay("Vin", "V", 2)
        self.disp_iout = ValueDisplay("Iout", "A", 3)
        self.disp_ext_temp = ValueDisplay("Ext Temp", "°C", 1)
        
        values_layout.addWidget(self.disp_vcore, 1, 0)
        values_layout.addWidget(self.disp_vin, 1, 1)
        values_layout.addWidget(self.disp_iout, 1, 2)
        values_layout.addWidget(self.disp_ext_temp, 1, 3)
        
        # FPGA values (Row 2)
        fpga_label = QLabel("FPGA (System Monitor)")
        fpga_label.setStyleSheet("color: #4fc3f7; font-weight: bold;")
        values_layout.addWidget(fpga_label, 2, 0, 1, 4)
        
        self.disp_fpga_temp = ValueDisplay("FPGA Temp", "°C", 2)
        self.disp_vccint = ValueDisplay("VCCINT", "V", 3)
        self.disp_power = ValueDisplay("Power", "W", 3)
        self.disp_alarms = ValueDisplay("Active Alarms", "", 0)
        
        values_layout.addWidget(self.disp_fpga_temp, 3, 0)
        values_layout.addWidget(self.disp_vccint, 3, 1)
        values_layout.addWidget(self.disp_power, 3, 2)
        values_layout.addWidget(self.disp_alarms, 3, 3)
        
        main_layout.addWidget(values_group)
        
        # Graphs section
        if PYQTGRAPH_AVAILABLE:
            self._create_graphs(main_layout)
        else:
            no_graph_label = QLabel("Install pyqtgraph for real-time graphs:\npip install pyqtgraph")
            no_graph_label.setAlignment(Qt.AlignCenter)
            no_graph_label.setStyleSheet("color: #888; padding: 20px;")
            main_layout.addWidget(no_graph_label)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.chk_autoscale = QCheckBox("Auto-scale Y")
        self.chk_autoscale.setChecked(True)
        controls_layout.addWidget(self.chk_autoscale)
        
        controls_layout.addWidget(QLabel("History:"))
        self.spin_history = QSpinBox()
        self.spin_history.setRange(100, 2000)
        self.spin_history.setValue(500)
        self.spin_history.setSuffix(" pts")
        self.spin_history.valueChanged.connect(self._on_history_changed)
        controls_layout.addWidget(self.spin_history)
        
        controls_layout.addStretch()
        
        self.btn_clear = QPushButton("Clear History")
        self.btn_clear.clicked.connect(self._clear_history)
        controls_layout.addWidget(self.btn_clear)
        
        main_layout.addLayout(controls_layout)
    
    def _create_graphs(self, parent_layout):
        """Create the pyqtgraph plots."""
        # Create a graphics layout widget
        self.graph_widget = pg.GraphicsLayoutWidget()
        self.graph_widget.setMinimumHeight(300)
        
        # Color palette
        colors = {
            'vcore': '#4fc3f7',      # Light blue
            'vin': '#ffc107',        # Amber
            'iout': '#ff5722',       # Deep orange
            'ext_temp': '#4caf50',   # Green
            'fpga_temp': '#e91e63',  # Pink
            'vccint': '#9c27b0',     # Purple
            'alarm_count': '#f44336' # Red
        }
        
        # Row 1: Voltages
        p1 = self.graph_widget.addPlot(title="Voltages")
        p1.setLabel('left', 'Voltage', units='V')
        p1.setLabel('bottom', 'Time', units='s')
        p1.addLegend(offset=(-10, 10))
        p1.showGrid(x=True, y=True, alpha=0.3)
        
        self.curves['vcore'] = p1.plot(pen=pg.mkPen(colors['vcore'], width=2), name='Vcore')
        self.curves['vin'] = p1.plot(pen=pg.mkPen(colors['vin'], width=2), name='Vin')
        self.curves['vccint'] = p1.plot(pen=pg.mkPen(colors['vccint'], width=2), name='VCCINT')
        self.plots['voltages'] = p1
        
        # Row 2: Current and Power
        self.graph_widget.nextRow()
        
        p2 = self.graph_widget.addPlot(title="Current")
        p2.setLabel('left', 'Current', units='A')
        p2.setLabel('bottom', 'Time', units='s')
        p2.showGrid(x=True, y=True, alpha=0.3)
        
        self.curves['iout'] = p2.plot(pen=pg.mkPen(colors['iout'], width=2), name='Iout')
        self.plots['current'] = p2
        
        # Row 3: Temperatures
        self.graph_widget.nextRow()
        
        p3 = self.graph_widget.addPlot(title="Temperatures")
        p3.setLabel('left', 'Temperature', units='°C')
        p3.setLabel('bottom', 'Time', units='s')
        p3.addLegend(offset=(-10, 10))
        p3.showGrid(x=True, y=True, alpha=0.3)
        
        self.curves['ext_temp'] = p3.plot(pen=pg.mkPen(colors['ext_temp'], width=2), name='External')
        self.curves['fpga_temp'] = p3.plot(pen=pg.mkPen(colors['fpga_temp'], width=2), name='FPGA')
        self.plots['temperatures'] = p3
        
        # Link X axes
        p2.setXLink(p1)
        p3.setXLink(p1)
        
        parent_layout.addWidget(self.graph_widget, 1)
    
    @Slot(dict)
    def updateFromDict(self, data: dict):
        """Update telemetry from a dictionary (from router)."""
        td = TelemetryData(
            timestamp=time.time(),
            vcore=data.get('vcore', data.get('stm_vcore', 0.0)),
            vin=data.get('vin', data.get('stm_vin', 0.0)),
            iout=data.get('iout', data.get('stm_iout', 0.0)),
            ext_temp=data.get('ext_temp', data.get('stm_ext_temp', 0.0)),
            fpga_temp=data.get('fpga_temp', 0.0),
            vccint=data.get('vccint', 0.0),
            alarm_f=data.get('alarm_f', 0),
            alarm_rf=data.get('alarm_rf', 0)
        )
        self.updateTelemetry(td)
    
    @Slot(TelemetryData)
    def updateTelemetry(self, data: TelemetryData):
        """Update with new telemetry data."""
        self.latest_data = data
        self.buffer.add(data)
        
        # Update value displays
        self.disp_vcore.setValue(data.vcore)
        self.disp_vin.setValue(data.vin)
        self.disp_iout.setValue(data.iout)
        self.disp_ext_temp.setValue(data.ext_temp)
        self.disp_fpga_temp.setValue(data.fpga_temp)
        self.disp_vccint.setValue(data.vccint)
        
        # Calculate power (P = V * I)
        power = data.vcore * data.iout
        self.disp_power.setValue(power)
        
        # Alarm count
        alarm_count = bin(data.alarm_f).count('1') + bin(data.alarm_rf).count('1')
        self.disp_alarms.setValue(float(alarm_count))
        
        # Color code based on values
        self._update_colors(data, alarm_count)
        
        # Emit signal
        self.data_updated.emit(data)
    
    def _update_colors(self, data: TelemetryData, alarm_count: int):
        """Update display colors based on values."""
        # FPGA temperature warning
        if data.fpga_temp > 85:
            self.disp_fpga_temp.setColor('#f44336')  # Red
        elif data.fpga_temp > 70:
            self.disp_fpga_temp.setColor('#ffc107')  # Amber
        else:
            self.disp_fpga_temp.setColor('#4caf50')  # Green
        
        # VCCINT warning (should be ~1.0V for most FPGAs)
        if data.vccint < 0.9 or data.vccint > 1.1:
            self.disp_vccint.setColor('#ffc107')
        else:
            self.disp_vccint.setColor('#4fc3f7')
        
        # Alarm count
        if alarm_count > 16:
            self.disp_alarms.setColor('#f44336')  # Red
        elif alarm_count > 0:
            self.disp_alarms.setColor('#ffc107')  # Amber
        else:
            self.disp_alarms.setColor('#4caf50')  # Green
    
    def _update_plots(self):
        """Update plot curves with current data."""
        if not PYQTGRAPH_AVAILABLE:
            return
        
        data = self.buffer.get_arrays()
        t = data['time']
        
        if len(t) < 2:
            return
        
        # Update curves
        if 'vcore' in self.curves:
            self.curves['vcore'].setData(t, data['vcore'])
        if 'vin' in self.curves:
            self.curves['vin'].setData(t, data['vin'])
        if 'vccint' in self.curves:
            self.curves['vccint'].setData(t, data['vccint'])
        if 'iout' in self.curves:
            self.curves['iout'].setData(t, data['iout'])
        if 'ext_temp' in self.curves:
            self.curves['ext_temp'].setData(t, data['ext_temp'])
        if 'fpga_temp' in self.curves:
            self.curves['fpga_temp'].setData(t, data['fpga_temp'])
        
        # Auto-scale if enabled
        if self.chk_autoscale.isChecked():
            for plot in self.plots.values():
                plot.enableAutoRange()
    
    def _on_history_changed(self, value: int):
        """Handle history size change."""
        self.buffer = TelemetryBuffer(max_points=value)
    
    def _clear_history(self):
        """Clear all history data."""
        self.buffer.clear()
