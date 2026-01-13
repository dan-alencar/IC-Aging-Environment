# -*- coding: utf-8 -*-
"""
Aging Event Logger

Records sensor alarm events with associated metadata for later analysis:
- Timestamp of alarm activation
- Which sensors triggered
- Current bitstream and its calibration (slack value)
- Environmental data (temperature, voltage)
- Calculated radiation dose based on experiment timeline

Output format is designed for easy import into analysis tools (CSV, pandas).
"""

import csv
import json
import os
from datetime import datetime
from dataclasses import dataclass, asdict, field
from typing import List, Optional, Dict, Any
from PySide6.QtCore import QObject, Signal


@dataclass
class AgingEvent:
    """A single aging/alarm event record."""
    
    # Timing
    timestamp: str                    # ISO format timestamp
    experiment_time_hours: float      # Hours since experiment start
    
    # Radiation (calculated from time)
    radiation_dose_krad: float        # Estimated accumulated dose
    
    # Sensor data
    alarm_f: int                      # ALARM_F register value (32-bit)
    alarm_rf: int                     # ALARM_RF register value (32-bit)
    triggered_sensors_f: List[int]    # List of bit indices that triggered
    triggered_sensors_rf: List[int]   # List of bit indices that triggered
    
    # Bitstream/Calibration
    bitstream_name: str               # Current bitstream filename
    phase_degrees: float              # Calibration phase shift
    slack_ns: float                   # Calibration slack value
    
    # Environmental
    fpga_temp_c: float = 0.0          # FPGA temperature
    vccint_v: float = 0.0             # VCCINT voltage
    vcore_v: float = 0.0              # DUT core voltage
    ambient_temp_c: float = 0.0       # Ambient/external temperature
    
    # Additional metadata
    notes: str = ""
    event_type: str = "alarm"         # "alarm", "bitstream_change", "manual"
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'AgingEvent':
        return cls(**data)
    
    def to_csv_row(self) -> List[Any]:
        """Convert to flat CSV row."""
        return [
            self.timestamp,
            self.experiment_time_hours,
            self.radiation_dose_krad,
            f"0x{self.alarm_f:08X}",
            f"0x{self.alarm_rf:08X}",
            len(self.triggered_sensors_f),
            len(self.triggered_sensors_rf),
            ','.join(map(str, self.triggered_sensors_f)),
            ','.join(map(str, self.triggered_sensors_rf)),
            self.bitstream_name,
            self.phase_degrees,
            self.slack_ns,
            self.fpga_temp_c,
            self.vccint_v,
            self.vcore_v,
            self.ambient_temp_c,
            self.event_type,
            self.notes
        ]
    
    @staticmethod
    def csv_header() -> List[str]:
        return [
            'timestamp',
            'experiment_time_hours',
            'radiation_dose_krad',
            'alarm_f_hex',
            'alarm_rf_hex',
            'triggered_count_f',
            'triggered_count_rf',
            'triggered_bits_f',
            'triggered_bits_rf',
            'bitstream_name',
            'phase_degrees',
            'slack_ns',
            'fpga_temp_c',
            'vccint_v',
            'vcore_v',
            'ambient_temp_c',
            'event_type',
            'notes'
        ]


class RadiationModel:
    """
    Model for calculating radiation dose based on experiment time.
    
    Assumes a linear relationship: dose = rate * time
    Can be configured for different radiation sources/facilities.
    """
    
    def __init__(self):
        self.dose_rate_krad_per_hour: float = 1.0  # krad/hour
        self.experiment_start: Optional[datetime] = None
        self.initial_dose_krad: float = 0.0
    
    def set_dose_rate(self, krad_per_hour: float):
        """Set the dose rate in krad/hour."""
        self.dose_rate_krad_per_hour = krad_per_hour
    
    def start_experiment(self, initial_dose: float = 0.0):
        """Mark the experiment start time."""
        self.experiment_start = datetime.now()
        self.initial_dose_krad = initial_dose
    
    def get_experiment_hours(self, timestamp: datetime = None) -> float:
        """Get hours elapsed since experiment start."""
        if self.experiment_start is None:
            return 0.0
        
        timestamp = timestamp or datetime.now()
        delta = timestamp - self.experiment_start
        return delta.total_seconds() / 3600.0
    
    def get_dose(self, timestamp: datetime = None) -> float:
        """Calculate accumulated dose at given time."""
        hours = self.get_experiment_hours(timestamp)
        return self.initial_dose_krad + (hours * self.dose_rate_krad_per_hour)
    
    def to_dict(self) -> dict:
        return {
            'dose_rate_krad_per_hour': self.dose_rate_krad_per_hour,
            'experiment_start': self.experiment_start.isoformat() if self.experiment_start else None,
            'initial_dose_krad': self.initial_dose_krad
        }
    
    def from_dict(self, data: dict):
        self.dose_rate_krad_per_hour = data.get('dose_rate_krad_per_hour', 1.0)
        start_str = data.get('experiment_start')
        if start_str:
            self.experiment_start = datetime.fromisoformat(start_str)
        self.initial_dose_krad = data.get('initial_dose_krad', 0.0)


class AgingLogger(QObject):
    """
    Main logging class for aging experiment data.
    
    Features:
    - Records alarm events with full context
    - Calculates radiation dose from experiment time
    - Exports to CSV and JSON formats
    - Tracks which sensors have triggered over the experiment
    """
    
    # Signals
    event_logged = Signal(object)  # AgingEvent
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.events: List[AgingEvent] = []
        self.radiation_model = RadiationModel()
        
        # Track sensors that have triggered
        self._triggered_history_f: set = set()
        self._triggered_history_rf: set = set()
        
        # Previous alarm state (for detecting new triggers)
        self._prev_alarm_f: int = 0
        self._prev_alarm_rf: int = 0
        
        # Current context (updated by main app)
        self._current_bitstream: str = ""
        self._current_phase: float = 0.0
        self._current_slack: float = 0.0
        self._current_fpga_temp: float = 0.0
        self._current_vccint: float = 0.0
        self._current_vcore: float = 0.0
        self._current_ambient_temp: float = 0.0
        
        # Auto-save settings
        self._log_file = "aging_log.json"
        self._csv_file = "aging_log.csv"
    
    def set_current_bitstream(self, name: str, phase_degrees: float, slack_ns: float):
        """Update current bitstream context."""
        self._current_bitstream = name
        self._current_phase = phase_degrees
        self._current_slack = slack_ns
    
    def set_environmental_data(self, fpga_temp: float = None, vccint: float = None,
                                vcore: float = None, ambient_temp: float = None):
        """Update environmental readings."""
        if fpga_temp is not None:
            self._current_fpga_temp = fpga_temp
        if vccint is not None:
            self._current_vccint = vccint
        if vcore is not None:
            self._current_vcore = vcore
        if ambient_temp is not None:
            self._current_ambient_temp = ambient_temp
    
    def check_and_log_alarms(self, alarm_f: int, alarm_rf: int) -> Optional[AgingEvent]:
        """
        Check for new alarm triggers and log if any detected.
        
        Compares current alarm state with previous state to detect
        newly triggered sensors.
        
        Returns:
            AgingEvent if new alarms detected, None otherwise
        """
        # Find newly triggered bits
        new_f = alarm_f & ~self._prev_alarm_f
        new_rf = alarm_rf & ~self._prev_alarm_rf
        
        # Update previous state
        self._prev_alarm_f = alarm_f
        self._prev_alarm_rf = alarm_rf
        
        # If any new triggers, log the event
        if new_f or new_rf:
            return self.log_event(alarm_f, alarm_rf, new_f, new_rf)
        
        return None
    
    def log_event(self, alarm_f: int, alarm_rf: int,
                  triggered_f: int = None, triggered_rf: int = None,
                  event_type: str = "alarm", notes: str = "") -> AgingEvent:
        """
        Log an aging event.
        
        Args:
            alarm_f: Current ALARM_F register value
            alarm_rf: Current ALARM_RF register value
            triggered_f: Bits that triggered (if None, uses all active bits)
            triggered_rf: Bits that triggered (if None, uses all active bits)
            event_type: Type of event ("alarm", "bitstream_change", "manual")
            notes: Optional notes
        
        Returns:
            The logged AgingEvent
        """
        now = datetime.now()
        
        # Determine which bits triggered
        if triggered_f is None:
            triggered_f = alarm_f
        if triggered_rf is None:
            triggered_rf = alarm_rf
        
        # Extract triggered bit indices
        triggered_sensors_f = [i for i in range(32) if triggered_f & (1 << i)]
        triggered_sensors_rf = [i for i in range(32) if triggered_rf & (1 << i)]
        
        # Update history
        self._triggered_history_f.update(triggered_sensors_f)
        self._triggered_history_rf.update(triggered_sensors_rf)
        
        # Create event
        event = AgingEvent(
            timestamp=now.isoformat(),
            experiment_time_hours=self.radiation_model.get_experiment_hours(now),
            radiation_dose_krad=self.radiation_model.get_dose(now),
            alarm_f=alarm_f,
            alarm_rf=alarm_rf,
            triggered_sensors_f=triggered_sensors_f,
            triggered_sensors_rf=triggered_sensors_rf,
            bitstream_name=self._current_bitstream,
            phase_degrees=self._current_phase,
            slack_ns=self._current_slack,
            fpga_temp_c=self._current_fpga_temp,
            vccint_v=self._current_vccint,
            vcore_v=self._current_vcore,
            ambient_temp_c=self._current_ambient_temp,
            event_type=event_type,
            notes=notes
        )
        
        self.events.append(event)
        self.event_logged.emit(event)
        
        return event
    
    def log_bitstream_change(self, old_bitstream: str, new_bitstream: str,
                              new_phase: float, new_slack: float) -> AgingEvent:
        """Log a bitstream change event."""
        self.set_current_bitstream(new_bitstream, new_phase, new_slack)
        
        return self.log_event(
            alarm_f=self._prev_alarm_f,
            alarm_rf=self._prev_alarm_rf,
            triggered_f=0,
            triggered_rf=0,
            event_type="bitstream_change",
            notes=f"Changed from {old_bitstream} to {new_bitstream}"
        )
    
    def get_triggered_history(self) -> Dict[str, set]:
        """Get all sensors that have triggered during experiment."""
        return {
            'alarm_f': self._triggered_history_f.copy(),
            'alarm_rf': self._triggered_history_rf.copy()
        }
    
    def get_events_for_analysis(self) -> List[Dict]:
        """Get events in a format suitable for analysis."""
        return [e.to_dict() for e in self.events]
    
    def get_slack_vs_dose_data(self) -> List[Dict]:
        """
        Get data for slack vs radiation dose plot.
        
        Returns list of dicts with:
        - dose_krad: Radiation dose at event
        - slack_ns: Slack value at event
        - sensors_triggered: Number of sensors that triggered
        """
        data = []
        for event in self.events:
            if event.event_type == "alarm":
                data.append({
                    'dose_krad': event.radiation_dose_krad,
                    'slack_ns': event.slack_ns,
                    'phase_degrees': event.phase_degrees,
                    'sensors_triggered': len(event.triggered_sensors_f) + len(event.triggered_sensors_rf),
                    'timestamp': event.timestamp
                })
        return data
    
    def save_json(self, filepath: str = None):
        """Save log to JSON file."""
        filepath = filepath or self._log_file
        
        data = {
            'radiation_model': self.radiation_model.to_dict(),
            'events': [e.to_dict() for e in self.events],
            'triggered_history': {
                'alarm_f': list(self._triggered_history_f),
                'alarm_rf': list(self._triggered_history_rf)
            }
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def save_csv(self, filepath: str = None):
        """Save log to CSV file."""
        filepath = filepath or self._csv_file
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(AgingEvent.csv_header())
            for event in self.events:
                writer.writerow(event.to_csv_row())
    
    def load_json(self, filepath: str = None) -> bool:
        """Load log from JSON file."""
        filepath = filepath or self._log_file
        
        if not os.path.exists(filepath):
            return False
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.radiation_model.from_dict(data.get('radiation_model', {}))
            
            self.events.clear()
            for event_data in data.get('events', []):
                self.events.append(AgingEvent.from_dict(event_data))
            
            history = data.get('triggered_history', {})
            self._triggered_history_f = set(history.get('alarm_f', []))
            self._triggered_history_rf = set(history.get('alarm_rf', []))
            
            return True
            
        except Exception as e:
            print(f"Error loading log: {e}")
            return False
    
    def clear(self):
        """Clear all logged events."""
        self.events.clear()
        self._triggered_history_f.clear()
        self._triggered_history_rf.clear()
        self._prev_alarm_f = 0
        self._prev_alarm_rf = 0
