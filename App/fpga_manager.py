# -*- coding: utf-8 -*-
"""
FPGA Programming Manager

Handles FPGA bitstream programming via Vivado in batch mode.
Cross-platform support for Windows and Linux.
"""

import os
import shutil
import glob
from pathlib import Path
from PySide6.QtCore import QObject, QProcess, Signal, Slot

import config


class FPGAManager(QObject):
    """
    Manages FPGA programming operations using Vivado.
    
    Signals:
        started(str): Emitted when programming starts (bitstream name)
        output(str): Emitted for each line of Vivado output
        finished(bool, str): Emitted when programming completes (success, message)
        progress(int): Emitted with progress percentage (0-100)
    """
    
    started = Signal(str)
    output = Signal(str)
    finished = Signal(bool, str)
    progress = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.process = None
        self.is_programming = False
        self._current_bitstream = ""
        
        # Get TCL script path (same directory as this module)
        self._tcl_script = str(Path(__file__).parent / "program_fpga.tcl")
        self._tcl_reset = str(Path(__file__).parent / "reset_fpga.tcl") # NOVO

    def _find_vivado(self) -> str:
        """
        Find the Vivado executable.
        Priority:
        1. Configured path in settings
        2. Auto-detected path
        3. PATH lookup
        """
        # Try configured path first
        if config.VIVADO_PATH and os.path.exists(config.VIVADO_PATH):
            return config.VIVADO_PATH
        
        # Try auto-detection
        detected = config.find_vivado_executable()
        if detected:
            return detected
        
        # Try PATH lookup
        exe_names = ["vivado", "vivado.bat", "vivado_lab", "vivado_lab.bat"]
        if config.IS_WINDOWS:
            exe_names = ["vivado.bat", "vivado_lab.bat", "vivado.exe", "vivado_lab.exe"]
        
        for name in exe_names:
            path = shutil.which(name)
            if path:
                return path
        
        return ""

    def get_vivado_path(self) -> str:
        """Return the current Vivado executable path."""
        return self._find_vivado()

    def is_vivado_available(self) -> bool:
        """Check if Vivado is available for programming."""
        return bool(self._find_vivado())

    def program(self, file_path: str, mode: str = "sram"):
        """
        Start programming the FPGA.
        
        Args:
            file_path: Path to the .bit or .bin file
            mode: "sram" (default) or "flash"
        """
        if self.is_programming:
            self.output.emit("⚠ Another programming operation is in progress.")
            return
        
        # Validate file
        if not os.path.exists(file_path):
            self.output.emit(f"✗ File not found: {file_path}")
            self.finished.emit(False, "File not found")
            return
            
        # Check extensions warning
        if mode == "flash" and not file_path.lower().endswith('.bin'):
            self.output.emit("⚠ Warning: Flash programming usually requires a .bin file.")
        
        # Find Vivado and Script (Copy existing logic here...)
        vivado_exe = self._find_vivado()
        if not vivado_exe:
            msg = (
                "✗ Vivado executable not found.\n"
                "Please configure the Vivado path in Settings or ensure it's in your PATH.\n"
                f"Searched: {config.VIVADO_PATH}"
            )
            self.output.emit(msg)
            self.finished.emit(False, "Vivado not found")
            return
        
        # Validate TCL script
        if not os.path.exists(self._tcl_script):
            self.output.emit(f"✗ TCL script not found: {self._tcl_script}")
            self.finished.emit(False, "TCL script not found")
            return
        
        # Setup process
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self._handle_stdout)
        self.process.readyReadStandardError.connect(self._handle_stderr)
        self.process.finished.connect(self._handle_finished)
        self.process.errorOccurred.connect(self._handle_error)
        
        # Build command arguments
        file_abspath = os.path.abspath(file_path)
        tcl_abspath = os.path.abspath(self._tcl_script)
        
        # Base arguments
        args = ["-mode", "batch", "-source", tcl_abspath, "-tclargs", file_abspath]
        
        # Add flash flag if needed
        if mode == "flash":
            args.append("-flash")
        
        # UI Updates
        self._current_bitstream = os.path.basename(file_path)
        self.is_programming = True
        
        mode_str = "FLASH (Persistent)" if mode == "flash" else "SRAM (Volatile)"
        
        self.output.emit("=" * 60)
        self.output.emit(f"▶ Starting FPGA Programming [{mode_str}]")
        self.output.emit(f"  File: {self._current_bitstream}")
        self.output.emit("=" * 60)
        
        self.started.emit(self._current_bitstream)
        self.progress.emit(5)
        
        # Start
        self.process.start(vivado_exe, args)

    def reset(self, ltx_path: str = None):
        """
        Trigger FPGA Reset via VIO.
        Args:
            ltx_path: Full path to the .ltx debug probes file.
        """
        if self.is_programming:
            self.output.emit("⚠ Another operation is in progress.")
            return

        vivado_exe = self._find_vivado()
        if not vivado_exe:
            self.output.emit("✗ Vivado executable not found.")
            return

        if not os.path.exists(self._tcl_reset):
            self.output.emit(f"✗ Reset script not found: {self._tcl_reset}")
            return

        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self._handle_stdout)
        self.process.readyReadStandardError.connect(self._handle_stderr)
        self.process.finished.connect(self._handle_finished)
        self.process.errorOccurred.connect(self._handle_error)

        # Pass the LTX file to the TCL script
        args = ["-mode", "batch", "-source", self._tcl_reset]
        
        if ltx_path:
            # Check if file exists before passing
            if os.path.exists(ltx_path):
                args.extend(["-tclargs", ltx_path])
            else:
                self.output.emit(f"⚠ Warning: LTX file not found at {ltx_path}")
                # We try running anyway, maybe user relies on luck (but likely fails)

        self.is_programming = True
        
        self.output.emit("=" * 60)
        self.output.emit("▶ STARTING FPGA RESET (VIO)...")
        if ltx_path:
             self.output.emit(f"  Probes: {os.path.basename(ltx_path)}")
        self.output.emit("=" * 60)
        self.started.emit("Reset Sequence")
        self.progress.emit(10)

        self.process.start(vivado_exe, args)

    def cancel(self):
        """Attempt to cancel the current programming operation."""
        if self.process and self.process.state() != QProcess.NotRunning:
            self.output.emit("⚠ Cancelling programming operation...")
            self.process.kill()

    def _handle_stdout(self):
        """Handle standard output from Vivado."""
        try:
            raw = self.process.readAllStandardOutput().data()
            lines = raw.decode(errors="replace").strip().split('\n')
            for line in lines:
                line = line.strip()
                if line:
                    self.output.emit(f"  {line}")
                    
                    # Parse progress from Vivado output
                    if "open_hw_manager" in line.lower():
                        self.progress.emit(20)
                    elif "connect_hw_server" in line.lower():
                        self.progress.emit(30)
                    elif "open_hw_target" in line.lower():
                        self.progress.emit(50)
                    elif "program_hw_devices" in line.lower():
                        self.progress.emit(70)
                    elif "close_hw" in line.lower():
                        self.progress.emit(90)
                    elif "sucesso" in line.lower() or "success" in line.lower():
                        self.progress.emit(100)
        except Exception as e:
            self.output.emit(f"[Read Error] {e}")

    def _handle_stderr(self):
        """Handle standard error from Vivado."""
        try:
            raw = self.process.readAllStandardError().data()
            lines = raw.decode(errors="replace").strip().split('\n')
            for line in lines:
                line = line.strip()
                if line:
                    # Filter out some common non-error messages
                    if "INFO:" in line:
                        self.output.emit(f"  ℹ {line}")
                    elif "WARNING:" in line:
                        self.output.emit(f"  ⚠ {line}")
                    elif "ERROR:" in line:
                        self.output.emit(f"  ✗ {line}")
                    else:
                        self.output.emit(f"  {line}")
        except Exception as e:
            self.output.emit(f"[Read Error] {e}")

    def _handle_finished(self, exit_code, exit_status=None):
        """Handle process completion."""
        self.is_programming = False
        
        success = (exit_code == 0)
        
        self.output.emit("=" * 60)
        if success:
            msg = f"✓ Programming completed successfully!"
            self.output.emit(msg)
            self.progress.emit(100)
        else:
            msg = f"✗ Programming failed (exit code: {exit_code})"
            self.output.emit(msg)
            self.progress.emit(0)
        self.output.emit("=" * 60)
        
        self.finished.emit(success, msg)

    def _handle_error(self, error):
        """Handle process errors."""
        self.is_programming = False
        
        error_msgs = {
            QProcess.FailedToStart: "Failed to start Vivado process",
            QProcess.Crashed: "Vivado process crashed",
            QProcess.Timedout: "Vivado process timed out",
            QProcess.WriteError: "Write error to Vivado process",
            QProcess.ReadError: "Read error from Vivado process",
            QProcess.UnknownError: "Unknown error occurred",
        }
        
        msg = error_msgs.get(error, f"Process error: {error}")
        self.output.emit(f"✗ {msg}")
        self.finished.emit(False, msg)


class BitstreamManager:
    """
    Manages a sequence of bitstream files for automated testing.
    """
    
    def __init__(self):
        self.files = []
        self.index = 0
        self._directory = ""

    def load_directory(self, path: str) -> int:
        """
        Load all .bit files from a directory.
        
        Returns:
            Number of bitstream files found
        """
        self._directory = path
        self.files = sorted(list(Path(path).glob("*.bit")))
        self.index = 0
        return len(self.files)

    def get_directory(self) -> str:
        """Get the current bitstream directory."""
        return self._directory

    def current(self) -> str:
        """Get the current bitstream file path."""
        if self.files and 0 <= self.index < len(self.files):
            return str(self.files[self.index])
        return ""

    def current_name(self) -> str:
        """Get the current bitstream filename (without path)."""
        if self.files and 0 <= self.index < len(self.files):
            return self.files[self.index].name
        return ""

    def count(self) -> int:
        """Get the total number of bitstreams."""
        return len(self.files)

    def get_index(self) -> int:
        """Get the current index."""
        return self.index

    def set_index(self, idx: int) -> bool:
        """Set the current index."""
        if 0 <= idx < len(self.files):
            self.index = idx
            return True
        return False

    def advance(self) -> bool:
        """Move to the next bitstream (wraps around)."""
        if not self.files:
            return False
        self.index = (self.index + 1) % len(self.files)
        return True

    def back(self) -> bool:
        """Move to the previous bitstream (wraps around)."""
        if not self.files:
            return False
        self.index = (self.index - 1) % len(self.files)
        return True

    def get_all_names(self) -> list:
        """Get list of all bitstream filenames."""
        return [f.name for f in self.files]
