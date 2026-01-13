# -*- coding: utf-8 -*-
"""
Aging Analysis Widget

Provides UI for:
- Configuring radiation model (dose rate, experiment start)
- Managing bitstream calibrations
- Viewing aging event log
- Plotting slack vs radiation dose
"""

import pyqtgraph as pg
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QGroupBox, QLabel, QPushButton, QDoubleSpinBox,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QSplitter, QTabWidget, QLineEdit, QSpinBox,
    QFileDialog, QMessageBox, QFrame, QComboBox,
    QTextEdit, QCheckBox
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QColor, QFont

from aging_logger import AgingLogger, AgingEvent
from bitstream_calibration import CalibrationManager, BitstreamCalibration


class RadiationConfigWidget(QGroupBox):
    """Widget for configuring radiation model parameters."""
    
    config_changed = Signal()
    experiment_started = Signal()
    
    def __init__(self, logger: AgingLogger, parent=None):
        super().__init__("Radiation Configuration", parent)
        self.logger = logger
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QGridLayout(self)
        
        # Dose rate
        layout.addWidget(QLabel("Dose Rate:"), 0, 0)
        self.spin_dose_rate = QDoubleSpinBox()
        self.spin_dose_rate.setRange(0.001, 1000.0)
        self.spin_dose_rate.setDecimals(3)
        self.spin_dose_rate.setValue(self.logger.radiation_model.dose_rate_krad_per_hour)
        self.spin_dose_rate.setSuffix(" krad/h")
        self.spin_dose_rate.valueChanged.connect(self._on_dose_rate_changed)
        layout.addWidget(self.spin_dose_rate, 0, 1)
        
        # Initial dose
        layout.addWidget(QLabel("Initial Dose:"), 1, 0)
        self.spin_initial_dose = QDoubleSpinBox()
        self.spin_initial_dose.setRange(0.0, 10000.0)
        self.spin_initial_dose.setDecimals(2)
        self.spin_initial_dose.setValue(self.logger.radiation_model.initial_dose_krad)
        self.spin_initial_dose.setSuffix(" krad")
        layout.addWidget(self.spin_initial_dose, 1, 1)
        
        # Experiment start button
        self.btn_start = QPushButton("▶ Start Experiment")
        self.btn_start.setStyleSheet("background-color: #28a745; color: white; font-weight: bold;")
        self.btn_start.clicked.connect(self._start_experiment)
        layout.addWidget(self.btn_start, 2, 0, 1, 2)
        
        # Status
        self.lbl_status = QLabel("Experiment not started")
        self.lbl_status.setStyleSheet("color: #888;")
        layout.addWidget(self.lbl_status, 3, 0, 1, 2)
        
        # Current values
        self.lbl_time = QLabel("Time: --:--:--")
        layout.addWidget(self.lbl_time, 4, 0)
        
        self.lbl_dose = QLabel("Dose: --- krad")
        layout.addWidget(self.lbl_dose, 4, 1)
    
    def _on_dose_rate_changed(self, value):
        self.logger.radiation_model.set_dose_rate(value)
        self.config_changed.emit()
    
    def _start_experiment(self):
        initial = self.spin_initial_dose.value()
        self.logger.radiation_model.start_experiment(initial)
        
        self.btn_start.setText("⏹ Reset Experiment")
        self.btn_start.setStyleSheet("background-color: #dc3545; color: white; font-weight: bold;")
        self.btn_start.clicked.disconnect()
        self.btn_start.clicked.connect(self._reset_experiment)
        
        self.lbl_status.setText(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.lbl_status.setStyleSheet("color: #28a745; font-weight: bold;")
        
        self.experiment_started.emit()
    
    def _reset_experiment(self):
        reply = QMessageBox.question(
            self, "Reset Experiment",
            "Are you sure you want to reset the experiment timer?\nThis will NOT clear logged events.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.logger.radiation_model.experiment_start = None
            
            self.btn_start.setText("▶ Start Experiment")
            self.btn_start.setStyleSheet("background-color: #28a745; color: white; font-weight: bold;")
            self.btn_start.clicked.disconnect()
            self.btn_start.clicked.connect(self._start_experiment)
            
            self.lbl_status.setText("Experiment not started")
            self.lbl_status.setStyleSheet("color: #888;")
    
    def update_display(self):
        """Update time and dose display."""
        if self.logger.radiation_model.experiment_start:
            hours = self.logger.radiation_model.get_experiment_hours()
            dose = self.logger.radiation_model.get_dose()
            
            h = int(hours)
            m = int((hours - h) * 60)
            s = int(((hours - h) * 60 - m) * 60)
            
            self.lbl_time.setText(f"Time: {h:02d}:{m:02d}:{s:02d}")
            self.lbl_dose.setText(f"Dose: {dose:.2f} krad")


class CalibrationTableWidget(QGroupBox):
    """Widget for managing bitstream calibrations."""
    
    calibration_selected = Signal(str, float, float)  # name, phase, slack
    
    def __init__(self, cal_manager: CalibrationManager, parent=None):
        super().__init__("Bitstream Calibrations", parent)
        self.cal_manager = cal_manager
        self._setup_ui()
        self._refresh_table()
        
        self.cal_manager.calibration_changed.connect(self._refresh_table)
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Clock period setting
        period_layout = QHBoxLayout()
        period_layout.addWidget(QLabel("Clock Period:"))
        self.spin_period = QDoubleSpinBox()
        self.spin_period.setRange(1.0, 1000.0)
        self.spin_period.setDecimals(2)
        self.spin_period.setValue(self.cal_manager.clock_period_ns)
        self.spin_period.setSuffix(" ns")
        self.spin_period.valueChanged.connect(self._on_period_changed)
        period_layout.addWidget(self.spin_period)
        period_layout.addStretch()
        layout.addLayout(period_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Bitstream", "Phase (°)", "Slack (ns)", "Order"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        layout.addWidget(self.table)
        
        # Add entry
        add_layout = QHBoxLayout()
        self.txt_name = QLineEdit()
        self.txt_name.setPlaceholderText("Bitstream name...")
        add_layout.addWidget(self.txt_name, 2)
        
        self.spin_phase = QDoubleSpinBox()
        self.spin_phase.setRange(-180.0, 360.0)
        self.spin_phase.setDecimals(2)
        self.spin_phase.setSuffix("°")
        add_layout.addWidget(self.spin_phase, 1)
        
        btn_add = QPushButton("+ Add")
        btn_add.clicked.connect(self._add_calibration)
        add_layout.addWidget(btn_add)
        
        btn_remove = QPushButton("- Remove")
        btn_remove.clicked.connect(self._remove_calibration)
        add_layout.addWidget(btn_remove)
        
        layout.addLayout(add_layout)
        
        # Import/Export buttons
        btn_layout = QHBoxLayout()
        
        btn_import = QPushButton("Import from Dir")
        btn_import.clicked.connect(self._import_from_dir)
        btn_layout.addWidget(btn_import)
        
        btn_save = QPushButton("Save")
        btn_save.clicked.connect(lambda: self.cal_manager.save())
        btn_layout.addWidget(btn_save)
        
        btn_load = QPushButton("Load")
        btn_load.clicked.connect(self._load_calibrations)
        btn_layout.addWidget(btn_load)
        
        layout.addLayout(btn_layout)
    
    def _on_period_changed(self, value):
        self.cal_manager.clock_period_ns = value
        self._refresh_table()
    
    def _refresh_table(self):
        self.table.setRowCount(0)
        
        for cal in self.cal_manager.get_all_calibrations():
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            self.table.setItem(row, 0, QTableWidgetItem(cal.name))
            self.table.setItem(row, 1, QTableWidgetItem(f"{cal.phase_degrees:.2f}"))
            self.table.setItem(row, 2, QTableWidgetItem(f"{cal.slack_ns:.3f}"))
            self.table.setItem(row, 3, QTableWidgetItem(str(cal.order)))
    
    def _on_selection_changed(self):
        selected = self.table.selectedItems()
        if selected:
            row = selected[0].row()
            name = self.table.item(row, 0).text()
            cal = self.cal_manager.get_calibration(name)
            if cal:
                self.calibration_selected.emit(cal.name, cal.phase_degrees, cal.slack_ns)
    
    def _add_calibration(self):
        name = self.txt_name.text().strip()
        phase = self.spin_phase.value()
        
        if name:
            self.cal_manager.add_calibration(name, phase)
            self.txt_name.clear()
    
    def _remove_calibration(self):
        selected = self.table.selectedItems()
        if selected:
            name = self.table.item(selected[0].row(), 0).text()
            self.cal_manager.remove_calibration(name)
    
    def _import_from_dir(self):
        path = QFileDialog.getExistingDirectory(self, "Select Bitstream Directory")
        if path:
            # Ask for step size
            step, ok = 5.0, True  # Could add dialog for this
            if ok:
                count = self.cal_manager.import_from_directory(path, step_degrees=step)
                QMessageBox.information(self, "Import Complete", 
                                       f"Imported {count} bitstreams with {step}° step")
    
    def _load_calibrations(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Load Calibrations", "", "JSON Files (*.json)"
        )
        if path:
            self.cal_manager.load(path)


class AgingEventLogWidget(QGroupBox):
    """Widget displaying the aging event log."""
    
    def __init__(self, logger: AgingLogger, parent=None):
        super().__init__("Event Log", parent)
        self.logger = logger
        self._setup_ui()
        
        self.logger.event_logged.connect(self._on_event_logged)
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Summary
        summary_layout = QHBoxLayout()
        self.lbl_event_count = QLabel("Events: 0")
        summary_layout.addWidget(self.lbl_event_count)
        
        self.lbl_sensors_triggered = QLabel("Sensors Triggered: F=0, RF=0")
        summary_layout.addWidget(self.lbl_sensors_triggered)
        
        summary_layout.addStretch()
        layout.addLayout(summary_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Time", "Dose (krad)", "Slack (ns)", 
            "F Triggers", "RF Triggers", "Bitstream", "Type"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.table)
        
        # Export buttons
        btn_layout = QHBoxLayout()
        
        btn_export_csv = QPushButton("Export CSV")
        btn_export_csv.clicked.connect(self._export_csv)
        btn_layout.addWidget(btn_export_csv)
        
        btn_export_json = QPushButton("Export JSON")
        btn_export_json.clicked.connect(self._export_json)
        btn_layout.addWidget(btn_export_json)
        
        btn_clear = QPushButton("Clear Log")
        btn_clear.clicked.connect(self._clear_log)
        btn_layout.addWidget(btn_clear)
        
        layout.addLayout(btn_layout)
    
    @Slot(object)
    def _on_event_logged(self, event: AgingEvent):
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        # Time (short format)
        time_str = event.timestamp.split('T')[1][:8] if 'T' in event.timestamp else event.timestamp[-8:]
        self.table.setItem(row, 0, QTableWidgetItem(time_str))
        
        # Dose
        self.table.setItem(row, 1, QTableWidgetItem(f"{event.radiation_dose_krad:.2f}"))
        
        # Slack
        self.table.setItem(row, 2, QTableWidgetItem(f"{event.slack_ns:.3f}"))
        
        # Triggers
        f_str = f"{len(event.triggered_sensors_f)}"
        rf_str = f"{len(event.triggered_sensors_rf)}"
        self.table.setItem(row, 3, QTableWidgetItem(f_str))
        self.table.setItem(row, 4, QTableWidgetItem(rf_str))
        
        # Bitstream
        self.table.setItem(row, 5, QTableWidgetItem(event.bitstream_name))
        
        # Type
        self.table.setItem(row, 6, QTableWidgetItem(event.event_type))
        
        # Color based on type
        if event.event_type == "alarm":
            for col in range(7):
                item = self.table.item(row, col)
                if item:
                    item.setBackground(QColor(50, 30, 30))
        
        # Update summary
        self._update_summary()
        
        # Scroll to bottom
        self.table.scrollToBottom()
    
    def _update_summary(self):
        self.lbl_event_count.setText(f"Events: {len(self.logger.events)}")
        
        history = self.logger.get_triggered_history()
        f_count = len(history['alarm_f'])
        rf_count = len(history['alarm_rf'])
        self.lbl_sensors_triggered.setText(f"Sensors Triggered: F={f_count}, RF={rf_count}")
    
    def _export_csv(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Export CSV", "aging_log.csv", "CSV Files (*.csv)"
        )
        if path:
            self.logger.save_csv(path)
    
    def _export_json(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Export JSON", "aging_log.json", "JSON Files (*.json)"
        )
        if path:
            self.logger.save_json(path)
    
    def _clear_log(self):
        reply = QMessageBox.question(
            self, "Clear Log",
            "Are you sure you want to clear all logged events?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.logger.clear()
            self.table.setRowCount(0)
            self._update_summary()


class AgingPlotWidget(QGroupBox):
    """Widget for plotting slack vs radiation dose."""
    
    def __init__(self, logger: AgingLogger, parent=None):
        super().__init__("Aging Analysis Plot", parent)
        self.logger = logger
        self._setup_ui()
        
        self.logger.event_logged.connect(self._update_plot)
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Plot widget
        pg.setConfigOptions(antialias=True)
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('#1e1e1e')
        self.plot_widget.setLabel('left', 'Slack', units='ns')
        self.plot_widget.setLabel('bottom', 'Radiation Dose', units='krad')
        self.plot_widget.setTitle('Slack Degradation vs Radiation Dose')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        
        # Data scatter
        self.scatter = pg.ScatterPlotItem(
            pen=pg.mkPen(None),
            brush=pg.mkBrush(79, 195, 247, 200),
            size=10
        )
        self.plot_widget.addItem(self.scatter)
        
        # Trend line
        self.trend_line = pg.PlotDataItem(
            pen=pg.mkPen('#ff5722', width=2, style=Qt.DashLine)
        )
        self.plot_widget.addItem(self.trend_line)
        
        layout.addWidget(self.plot_widget)
        
        # Controls
        ctrl_layout = QHBoxLayout()
        
        btn_refresh = QPushButton("🔄 Refresh")
        btn_refresh.clicked.connect(self._update_plot)
        ctrl_layout.addWidget(btn_refresh)
        
        self.chk_trend = QCheckBox("Show Trend Line")
        self.chk_trend.setChecked(True)
        self.chk_trend.stateChanged.connect(self._update_plot)
        ctrl_layout.addWidget(self.chk_trend)
        
        ctrl_layout.addStretch()
        layout.addLayout(ctrl_layout)
    
    @Slot()
    def _update_plot(self):
        data = self.logger.get_slack_vs_dose_data()
        
        if not data:
            self.scatter.setData([], [])
            self.trend_line.setData([], [])
            return
        
        doses = [d['dose_krad'] for d in data]
        slacks = [d['slack_ns'] for d in data]
        
        # Update scatter
        self.scatter.setData(doses, slacks)
        
        # Update trend line (simple linear fit)
        if self.chk_trend.isChecked() and len(doses) > 1:
            import numpy as np
            try:
                coeffs = np.polyfit(doses, slacks, 1)
                x_fit = np.linspace(min(doses), max(doses), 100)
                y_fit = np.polyval(coeffs, x_fit)
                self.trend_line.setData(x_fit, y_fit)
            except:
                self.trend_line.setData([], [])
        else:
            self.trend_line.setData([], [])


class AgingAnalysisWidget(QWidget):
    """Main widget combining all aging analysis components."""
    
    # Signal for auto-reprogram
    request_reprogram = Signal(str)  # bitstream name
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Create managers
        self.logger = AgingLogger()
        self.cal_manager = CalibrationManager()
        
        # Try to load saved data
        self.cal_manager.load()
        self.logger.load_json()
        
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        
        # Left side: Configuration
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Radiation config
        self.radiation_config = RadiationConfigWidget(self.logger)
        left_layout.addWidget(self.radiation_config)
        
        # Calibration table
        self.calibration_table = CalibrationTableWidget(self.cal_manager)
        left_layout.addWidget(self.calibration_table)
        
        # Auto-reprogram settings
        auto_group = QGroupBox("Auto-Reprogram on Alarm")
        auto_layout = QVBoxLayout(auto_group)
        
        self.chk_auto_reprogram = QCheckBox("Enable auto-reprogram when alarm triggers")
        auto_layout.addWidget(self.chk_auto_reprogram)
        
        self.lbl_next_bitstream = QLabel("Next bitstream: ---")
        self.lbl_next_bitstream.setStyleSheet("color: #888;")
        auto_layout.addWidget(self.lbl_next_bitstream)
        
        left_layout.addWidget(auto_group)
        
        # Right side: Log and Plot
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Event log
        self.event_log = AgingEventLogWidget(self.logger)
        right_layout.addWidget(self.event_log, 1)
        
        # Plot
        self.plot = AgingPlotWidget(self.logger)
        right_layout.addWidget(self.plot, 1)
        
        # Add to main layout
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 600])
        
        layout.addWidget(splitter)
    
    def set_current_bitstream(self, name: str):
        """Update current bitstream and associated calibration."""
        cal = self.cal_manager.get_calibration(name)
        if cal:
            self.logger.set_current_bitstream(name, cal.phase_degrees, cal.slack_ns)
        else:
            self.logger.set_current_bitstream(name, 0.0, 0.0)
        
        # Update next bitstream display
        next_bs = self.cal_manager.get_next_bitstream(name)
        if next_bs:
            self.lbl_next_bitstream.setText(f"Next bitstream: {next_bs}")
        else:
            self.lbl_next_bitstream.setText("Next bitstream: (end of sequence)")
    
    def set_environmental_data(self, **kwargs):
        """Update environmental readings."""
        self.logger.set_environmental_data(**kwargs)
    
    def check_alarms(self, alarm_f: int, alarm_rf: int) -> bool:
        """
        Check for alarm triggers and handle auto-reprogram.
        
        Returns True if new alarms were detected.
        """
        event = self.logger.check_and_log_alarms(alarm_f, alarm_rf)
        
        if event and self.chk_auto_reprogram.isChecked():
            # Get next bitstream
            next_bs = self.cal_manager.get_next_bitstream(self.logger._current_bitstream)
            if next_bs:
                self.request_reprogram.emit(next_bs)
        
        return event is not None
    
    def update_display(self):
        """Update time-dependent displays."""
        self.radiation_config.update_display()
    
    def save_all(self):
        """Save all configuration and log data."""
        self.cal_manager.save()
        self.logger.save_json()
        self.logger.save_csv()
