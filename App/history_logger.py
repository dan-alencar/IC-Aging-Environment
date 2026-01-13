# -*- coding: utf-8 -*-
"""
History Logger

Records events for long-duration experiments (24h+ burn-in tests).
Logs programming events, alarms, and system status to a persistent file.
"""

import os
from datetime import datetime
from pathlib import Path


class HistoryLogger:
    """
    Persistent event logger for experiment tracking.
    
    Events are appended to a text file with timestamps.
    Useful for post-analysis of burn-in experiments.
    """
    
    def __init__(self, filename: str = None):
        """
        Initialize the logger.
        
        Args:
            filename: Log file path. Defaults to 'experiment_history.txt'
                     in the current directory.
        """
        if filename is None:
            filename = "experiment_history.txt"
        
        self.filename = filename
        self._ensure_directory()

    def _ensure_directory(self):
        """Create log directory if it doesn't exist."""
        log_dir = Path(self.filename).parent
        if log_dir and not log_dir.exists():
            log_dir.mkdir(parents=True, exist_ok=True)

    def log_event(self, event_type: str, details: str = "", 
                  bitstream: str = "", extra: dict = None):
        """
        Log an event to the history file.
        
        Args:
            event_type: Type of event (e.g., 'TRIGGER', 'PROGRAM', 'ALARM', 'INFO')
            details: Human-readable description
            bitstream: Current bitstream filename (optional)
            extra: Additional key-value data (optional)
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        
        # Build log line
        parts = [f"[{timestamp}]", f"[{event_type:8}]"]
        
        if bitstream:
            parts.append(f"[{bitstream}]")
        
        if details:
            parts.append(details)
        
        if extra:
            extra_str = " | ".join(f"{k}={v}" for k, v in extra.items())
            parts.append(f"({extra_str})")
        
        log_line = " ".join(parts)
        
        try:
            with open(self.filename, "a", encoding="utf-8") as f:
                f.write(log_line + "\n")
        except Exception as e:
            print(f"Failed to write to history log: {e}")

    def log_program_start(self, bitstream: str):
        """Log FPGA programming start."""
        self.log_event("PROG_START", "FPGA programming initiated", bitstream)

    def log_program_success(self, bitstream: str):
        """Log successful FPGA programming."""
        self.log_event("PROG_OK", "FPGA programming successful", bitstream)

    def log_program_fail(self, bitstream: str, error: str = ""):
        """Log failed FPGA programming."""
        self.log_event("PROG_FAIL", f"FPGA programming failed: {error}", bitstream)

    def log_alarm(self, alarm_f: int, alarm_rf: int, bitstream: str = ""):
        """Log sensor alarm detection."""
        f_count = bin(alarm_f).count('1')
        rf_count = bin(alarm_rf).count('1')
        details = f"F=0x{alarm_f:08X} ({f_count} active), RF=0x{alarm_rf:08X} ({rf_count} active)"
        self.log_event("ALARM", details, bitstream)

    def log_connection(self, port: str, connected: bool):
        """Log connection state change."""
        state = "connected" if connected else "disconnected"
        self.log_event("CONNECT", f"Serial {state}: {port}")

    def log_voltage_change(self, voltage: float):
        """Log voltage change command."""
        self.log_event("VOLTAGE", f"Vcore set to {voltage:.2f}V")

    def log_info(self, message: str):
        """Log general information."""
        self.log_event("INFO", message)

    def log_error(self, message: str):
        """Log error."""
        self.log_event("ERROR", message)

    def get_full_path(self) -> str:
        """Get absolute path to log file."""
        return os.path.abspath(self.filename)

    def get_recent_entries(self, count: int = 100) -> list:
        """
        Get the most recent log entries.
        
        Args:
            count: Number of entries to retrieve
            
        Returns:
            List of log lines (most recent last)
        """
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                lines = f.readlines()
            return lines[-count:] if len(lines) > count else lines
        except FileNotFoundError:
            return []
        except Exception as e:
            print(f"Failed to read history log: {e}")
            return []

    def clear(self):
        """Clear the log file (with backup)."""
        if os.path.exists(self.filename):
            # Create backup
            backup = f"{self.filename}.backup"
            try:
                os.rename(self.filename, backup)
                self.log_event("INFO", f"Log cleared (backup: {backup})")
            except Exception as e:
                print(f"Failed to backup log: {e}")
