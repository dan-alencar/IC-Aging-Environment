# -*- coding: utf-8 -*-
"""
Bitstream Calibration Manager

Maps bitstream files to their calibration parameters:
- Phase degrees (left shift)
- Slack time in nanoseconds

Each bitstream represents a specific calibration point of the aging sensors.
"""

import json
import os
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Tuple
from PySide6.QtCore import QObject, Signal


@dataclass
class BitstreamCalibration:
    """Calibration data for a single bitstream."""
    name: str                    # Bitstream filename (without path)
    phase_degrees: float = 0.0   # Phase shift in degrees (left = positive)
    slack_ns: float = 0.0        # Corresponding slack in nanoseconds
    description: str = ""        # Optional description
    order: int = 0               # Order in the calibration sequence
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'BitstreamCalibration':
        return cls(**data)


class CalibrationManager(QObject):
    """
    Manages the mapping between bitstreams and their calibration values.
    
    The calibration determines:
    - How much phase shift (in degrees) the bitstream applies
    - What slack time (in ns) this corresponds to
    
    When an alarm triggers, we know the current calibration and can
    calculate the actual slack degradation.
    """
    
    # Emitted when calibration data changes
    calibration_changed = Signal()
    
    # Default clock period for slack calculations (ns)
    DEFAULT_CLOCK_PERIOD_NS = 50.0  # 20 MHz = 50ns period
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._calibrations: Dict[str, BitstreamCalibration] = {}
        self._clock_period_ns = self.DEFAULT_CLOCK_PERIOD_NS
        self._config_file = "bitstream_calibrations.json"
    
    @property
    def clock_period_ns(self) -> float:
        return self._clock_period_ns
    
    @clock_period_ns.setter
    def clock_period_ns(self, value: float):
        if value > 0:
            self._clock_period_ns = value
            self.calibration_changed.emit()
    
    def degrees_to_ns(self, degrees: float) -> float:
        """Convert phase degrees to nanoseconds based on clock period."""
        # 360 degrees = 1 clock period
        return (degrees / 360.0) * self._clock_period_ns
    
    def ns_to_degrees(self, ns: float) -> float:
        """Convert nanoseconds to phase degrees based on clock period."""
        return (ns / self._clock_period_ns) * 360.0
    
    def add_calibration(self, name: str, phase_degrees: float, 
                        description: str = "", order: int = -1) -> BitstreamCalibration:
        """
        Add or update calibration for a bitstream.
        
        Args:
            name: Bitstream filename
            phase_degrees: Phase shift in degrees (left = positive)
            description: Optional description
            order: Order in sequence (-1 = auto-assign)
        
        Returns:
            The created/updated calibration object
        """
        slack_ns = self.degrees_to_ns(phase_degrees)
        
        if order < 0:
            order = len(self._calibrations)
        
        cal = BitstreamCalibration(
            name=name,
            phase_degrees=phase_degrees,
            slack_ns=slack_ns,
            description=description,
            order=order
        )
        
        self._calibrations[name] = cal
        self.calibration_changed.emit()
        return cal
    
    def remove_calibration(self, name: str) -> bool:
        """Remove calibration for a bitstream."""
        if name in self._calibrations:
            del self._calibrations[name]
            self.calibration_changed.emit()
            return True
        return False
    
    def get_calibration(self, name: str) -> Optional[BitstreamCalibration]:
        """Get calibration for a specific bitstream."""
        return self._calibrations.get(name)
    
    def get_slack_for_bitstream(self, name: str) -> Optional[float]:
        """Get the slack (ns) for a bitstream, or None if not calibrated."""
        cal = self._calibrations.get(name)
        return cal.slack_ns if cal else None
    
    def get_all_calibrations(self) -> List[BitstreamCalibration]:
        """Get all calibrations sorted by order."""
        return sorted(self._calibrations.values(), key=lambda c: c.order)
    
    def get_ordered_bitstreams(self) -> List[str]:
        """Get bitstream names in calibration order."""
        return [c.name for c in self.get_all_calibrations()]
    
    def get_next_bitstream(self, current: str) -> Optional[str]:
        """
        Get the next bitstream in the calibration sequence.
        Used for auto-progression when alarms trigger.
        """
        ordered = self.get_ordered_bitstreams()
        if current in ordered:
            idx = ordered.index(current)
            if idx + 1 < len(ordered):
                return ordered[idx + 1]
        return None
    
    def import_from_directory(self, directory: str, 
                              start_degrees: float = 0.0,
                              step_degrees: float = 5.0) -> int:
        """
        Auto-import bitstreams from a directory with sequential calibration.
        
        Assumes bitstreams are named in order (alphabetically) and each
        represents a step increase in phase shift.
        
        Args:
            directory: Path to bitstream directory
            start_degrees: Starting phase shift
            step_degrees: Degrees increment per bitstream
        
        Returns:
            Number of bitstreams imported
        """
        if not os.path.isdir(directory):
            return 0
        
        bitstreams = sorted([
            f for f in os.listdir(directory)
            if f.endswith('.bit')
        ])
        
        for i, name in enumerate(bitstreams):
            phase = start_degrees + (i * step_degrees)
            self.add_calibration(
                name=name,
                phase_degrees=phase,
                description=f"Auto-imported: {phase:.1f}° phase shift",
                order=i
            )
        
        return len(bitstreams)
    
    def save(self, filepath: str = None):
        """Save calibrations to JSON file."""
        filepath = filepath or self._config_file
        
        data = {
            'clock_period_ns': self._clock_period_ns,
            'calibrations': [c.to_dict() for c in self._calibrations.values()]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def load(self, filepath: str = None) -> bool:
        """Load calibrations from JSON file."""
        filepath = filepath or self._config_file
        
        if not os.path.exists(filepath):
            return False
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self._clock_period_ns = data.get('clock_period_ns', self.DEFAULT_CLOCK_PERIOD_NS)
            self._calibrations.clear()
            
            for cal_data in data.get('calibrations', []):
                cal = BitstreamCalibration.from_dict(cal_data)
                self._calibrations[cal.name] = cal
            
            self.calibration_changed.emit()
            return True
            
        except Exception as e:
            print(f"Error loading calibrations: {e}")
            return False
    
    def clear(self):
        """Clear all calibrations."""
        self._calibrations.clear()
        self.calibration_changed.emit()
