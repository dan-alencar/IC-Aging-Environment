# -*- coding: utf-8 -*-
"""
Sensor Visualization Widget

Provides a visual grid representation of 32-bit alarm registers,
showing which sensors are active (alarming) and which are inactive.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
    QLabel, QFrame, QGroupBox, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, Slot, QSize
from PySide6.QtGui import QColor, QPainter, QBrush, QPen, QFont


class SensorCell(QWidget):
    """
    A single sensor indicator cell.
    Shows green when inactive (0), red when active (1), gray when disabled.
    """
    
    def __init__(self, index: int, parent=None):
        super().__init__(parent)
        self.index = index
        self.active = False
        self.enabled = True  # NEW: disabled sensors show gray
        self.setMinimumSize(20, 20)
        self.setMaximumSize(30, 30)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setToolTip(f"Bit {index}")
    
    def setActive(self, active: bool):
        """Set the sensor state and trigger repaint."""
        if self.active != active:
            self.active = active
            self.update()
    
    def setEnabled(self, enabled: bool):
        """Set whether the sensor is enabled (gray if disabled)."""
        if self.enabled != enabled:
            self.enabled = enabled
            self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw border
        pen = QPen(QColor(80, 80, 80))
        pen.setWidth(1)
        painter.setPen(pen)
        
        # Fill based on state
        if not self.enabled:
            # Disabled: Gray
            brush = QBrush(QColor(60, 60, 60))  # Dark gray
        elif self.active:
            # Active/Alarm: Red
            brush = QBrush(QColor(220, 53, 69))  # Bootstrap danger red
        else:
            # Inactive/OK: Green
            brush = QBrush(QColor(40, 167, 69))  # Bootstrap success green
        
        painter.setBrush(brush)
        
        # Draw rounded rectangle
        margin = 2
        painter.drawRoundedRect(
            margin, margin, 
            self.width() - 2*margin, 
            self.height() - 2*margin,
            3, 3
        )
        
        painter.end()


class SensorRegisterWidget(QWidget):
    """
    Displays a 32-bit register as an 8x4 grid of sensor cells.
    Can be set to disabled (gray) state for placeholder registers.
    """
    
    def __init__(self, title: str, enabled: bool = True, parent=None):
        super().__init__(parent)
        self.title = title
        self.cells = []
        self._value = 0
        self._enabled = enabled
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Title with value display
        self.title_label = QLabel(f"{self.title}: 0x00000000")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-weight: bold; font-size: 11pt;")
        layout.addWidget(self.title_label)
        
        # Count display
        self.count_label = QLabel("Active: 0 / 32")
        self.count_label.setAlignment(Qt.AlignCenter)
        self.count_label.setStyleSheet("color: #888;")
        layout.addWidget(self.count_label)
        
        # Grid of sensor cells (8 columns x 4 rows = 32 bits)
        # Bit 31 (MSB) at top-left, Bit 0 (LSB) at bottom-right
        grid_widget = QWidget()
        grid = QGridLayout(grid_widget)
        grid.setSpacing(2)
        grid.setContentsMargins(5, 5, 5, 5)
        
        for i in range(32):
            row = i // 8
            col = 7 - (i % 8)  # Reverse column order so MSB is left
            bit_index = 31 - i  # Bit 31 first
            
            cell = SensorCell(bit_index)
            cell.setEnabled(self._enabled)
            self.cells.append(cell)
            grid.addWidget(cell, row, col)
        
        # Reverse cells list so index 0 = bit 0
        self.cells = list(reversed(self.cells))
        
        layout.addWidget(grid_widget)
        
        # Bit labels row
        bit_labels = QHBoxLayout()
        for i in [31, 24, 16, 8, 0]:
            lbl = QLabel(str(i))
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("color: #666; font-size: 8pt;")
            bit_labels.addWidget(lbl)
            if i > 0:
                bit_labels.addStretch()
        layout.addLayout(bit_labels)
        
        # Apply disabled styling if needed
        if not self._enabled:
            self._apply_disabled_style()
    
    def _apply_disabled_style(self):
        """Apply gray styling for disabled state."""
        self.title_label.setStyleSheet("font-weight: bold; font-size: 11pt; color: #666;")
        self.count_label.setText("Disabled")
        self.count_label.setStyleSheet("color: #555; font-style: italic;")
    
    def setRegisterEnabled(self, enabled: bool):
        """Enable or disable the register display."""
        self._enabled = enabled
        for cell in self.cells:
            cell.setEnabled(enabled)
        
        if not enabled:
            self._apply_disabled_style()
        else:
            self.title_label.setStyleSheet("font-weight: bold; font-size: 11pt;")
            self.setValue(self._value)  # Refresh display
    
    def setValue(self, value: int):
        """Update the register value and refresh display."""
        if not self._enabled:
            return
            
        self._value = value & 0xFFFFFFFF
        
        # Update each cell
        active_count = 0
        for i, cell in enumerate(self.cells):
            bit_active = bool(self._value & (1 << i))
            cell.setActive(bit_active)
            if bit_active:
                active_count += 1
        
        # Update labels
        self.title_label.setText(f"{self.title}: 0x{self._value:08X}")
        self.count_label.setText(f"Active: {active_count} / 32")
        
        # Color the count based on alarm level
        if active_count == 0:
            self.count_label.setStyleSheet("color: #28a745; font-weight: bold;")
        elif active_count < 8:
            self.count_label.setStyleSheet("color: #ffc107; font-weight: bold;")
        else:
            self.count_label.setStyleSheet("color: #dc3545; font-weight: bold;")
    
    def getValue(self) -> int:
        return self._value
    
    def isRegisterEnabled(self) -> bool:
        return self._enabled


class SensorVisualizationWidget(QWidget):
    """
    Main widget combining all sensor registers with summary statistics.
    Shows 4 sensor registers: 2 active (ALARM_F, ALARM_RF) and 2 disabled placeholders.
    """
    
    # Signal emitted when sensor data is updated
    data_updated = Signal(object, object)  # alarm_f, alarm_rf
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Main title
        title = QLabel("Aging Sensor Status")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 14pt; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Four register displays in 2x2 grid
        registers_grid = QGridLayout()
        registers_grid.setSpacing(10)
        
        # Row 1: Active sensors
        # AM Sensor (alarm_f)
        self.alarm_f_widget = SensorRegisterWidget("ALARM_F (AM Sensor)", enabled=True)
        registers_grid.addWidget(self.alarm_f_widget, 0, 0)
        
        # LF Sensor (alarm_rf)
        self.alarm_rf_widget = SensorRegisterWidget("ALARM_RF (LF Sensor)", enabled=True)
        registers_grid.addWidget(self.alarm_rf_widget, 0, 1)
        
        # Row 2: Placeholder sensors (disabled/gray)
        # Placeholder 1
        self.placeholder1_widget = SensorRegisterWidget("SENSOR_3 (Reserved)", enabled=False)
        registers_grid.addWidget(self.placeholder1_widget, 1, 0)
        
        # Placeholder 2
        self.placeholder2_widget = SensorRegisterWidget("SENSOR_4 (Reserved)", enabled=False)
        registers_grid.addWidget(self.placeholder2_widget, 1, 1)
        
        layout.addLayout(registers_grid)
        
        # Summary bar
        summary_layout = QHBoxLayout()
        
        self.total_label = QLabel("Total Active Alarms: 0 / 64")
        self.total_label.setAlignment(Qt.AlignCenter)
        self.total_label.setStyleSheet("""
            font-size: 12pt; 
            font-weight: bold; 
            padding: 10px;
            background-color: #1e1e1e;
            border-radius: 5px;
        """)
        summary_layout.addWidget(self.total_label)
        
        # Status indicator
        self.status_indicator = QLabel("● NOMINAL")
        self.status_indicator.setAlignment(Qt.AlignCenter)
        self.status_indicator.setStyleSheet("""
            font-size: 12pt;
            font-weight: bold;
            color: #28a745;
            padding: 10px;
            background-color: #1e1e1e;
            border-radius: 5px;
        """)
        summary_layout.addWidget(self.status_indicator)
        
        layout.addLayout(summary_layout)
    
    @Slot(object, object)
    def updateSensorData(self, alarm_f, alarm_rf):
        """Update both active sensor registers with new values."""
        self.alarm_f_widget.setValue(alarm_f)
        self.alarm_rf_widget.setValue(alarm_rf)
        
        # Calculate totals (only from active sensors)
        f_count = bin(alarm_f).count('1')
        rf_count = bin(alarm_rf).count('1')
        total = f_count + rf_count
        
        self.total_label.setText(f"Total Active Alarms: {total} / 64")
        
        # Update status indicator
        if total == 0:
            self.status_indicator.setText("● NOMINAL")
            self.status_indicator.setStyleSheet("""
                font-size: 12pt; font-weight: bold; color: #28a745;
                padding: 10px; background-color: #1e1e1e; border-radius: 5px;
            """)
        elif total < 16:
            self.status_indicator.setText("● WARNING")
            self.status_indicator.setStyleSheet("""
                font-size: 12pt; font-weight: bold; color: #ffc107;
                padding: 10px; background-color: #1e1e1e; border-radius: 5px;
            """)
        else:
            self.status_indicator.setText("● CRITICAL")
            self.status_indicator.setStyleSheet("""
                font-size: 12pt; font-weight: bold; color: #dc3545;
                padding: 10px; background-color: #1e1e1e; border-radius: 5px;
            """)
        
        # Emit signal
        self.data_updated.emit(alarm_f, alarm_rf)
    
    @Slot(dict)
    def updateFromDict(self, data: dict):
        """Update from a dictionary (compatibility with router signals)."""
        alarm_f = data.get('alarm_f', 0)
        alarm_rf = data.get('alarm_rf', 0)
        self.updateSensorData(alarm_f, alarm_rf)
    
    def enablePlaceholder(self, index: int, enabled: bool, title: str = None):
        """
        Enable/disable a placeholder register.
        
        Args:
            index: 1 or 2 (placeholder index)
            enabled: True to enable, False to disable (gray)
            title: Optional new title for the register
        """
        widget = self.placeholder1_widget if index == 1 else self.placeholder2_widget
        widget.setRegisterEnabled(enabled)
        if title:
            widget.title = title
            widget.title_label.setText(f"{title}: 0x00000000")
