# -*- coding: utf-8 -*-
"""
Configuration management for CROC Monitor

Handles cross-platform settings and paths for Windows/Linux.
"""

import json
import os
import platform
from pathlib import Path

SETTINGS_FILE = "settings.json"

# --- Global Variables ---
FPGA_PORT = ""          # USB-UART to FPGA
SYSTEM_BAUD = 115200    # UART baud rate (matches config.h)

# Vivado paths (will be auto-detected or configured)
VIVADO_PATH = ""
BITSTREAM_DIR = ""

# Logging
LOG_FOLDER = os.path.join(os.getcwd(), "logs")
LOG_INTERVAL_MS = 500

# --- Platform Detection ---
IS_WINDOWS = platform.system() == "Windows"
IS_LINUX = platform.system() == "Linux"


def get_default_ports():
    """Get default serial port based on OS."""
    if IS_WINDOWS:
        return {"fpga": "COM3"}
    elif IS_LINUX:
        return {"fpga": "/dev/ttyUSB0"}
    return {"fpga": ""}


def get_default_vivado_paths():
    """
    Get default Vivado installation paths based on OS.
    Returns tuple: (vivado_executable, default_bitstream_dir)
    """
    if IS_WINDOWS:
        # Common Windows Vivado installation paths
        possible_paths = [
            r"C:\Xilinx\Vivado\2024.2\bin\vivado.bat",
            r"C:\Xilinx\Vivado\2024.1\bin\vivado.bat",
            r"C:\Xilinx\Vivado\2023.2\bin\vivado.bat",
            r"C:\Xilinx\2025.1\Vivado\bin\vivado.bat",
            r"C:\Xilinx\Vivado_Lab\2024.2\bin\vivado_lab.bat",
        ]
        for p in possible_paths:
            if os.path.exists(p):
                return p, str(Path.home() / "Documents" / "FPGA_Bitstreams")
        return "", str(Path.home() / "Documents" / "FPGA_Bitstreams")
    
    elif IS_LINUX:
        # Common Linux Vivado installation paths
        possible_paths = [
            "/tools/Xilinx/Vivado/2024.2/bin/vivado",
            "/opt/Xilinx/Vivado/2024.2/bin/vivado",
            "/tools/Xilinx/Vivado/2024.1/bin/vivado",
            "/opt/Xilinx/Vivado/2024.1/bin/vivado",
            str(Path.home() / "Xilinx" / "Vivado" / "2024.2" / "bin" / "vivado"),
        ]
        for p in possible_paths:
            if os.path.exists(p):
                return p, str(Path.home() / "FPGA_Bitstreams")
        return "", str(Path.home() / "FPGA_Bitstreams")
    
    return "", ""


def find_vivado_executable():
    """
    Attempt to find Vivado executable in PATH or common locations.
    Returns the path if found, empty string otherwise.
    """
    import shutil
    import glob
    
    # Try PATH first
    exe_names = ["vivado", "vivado.bat", "vivado_lab", "vivado_lab.bat"]
    for name in exe_names:
        path = shutil.which(name)
        if path:
            return path
    
    # Try default paths
    default_path, _ = get_default_vivado_paths()
    if default_path and os.path.exists(default_path):
        return default_path
    
    # Windows: search common install locations
    if IS_WINDOWS:
        patterns = [
            r"C:\Xilinx\Vivado\*\bin\vivado.bat",
            r"C:\Xilinx\*\Vivado\bin\vivado.bat",
            r"C:\Xilinx\Vivado_Lab\*\bin\vivado_lab.bat",
        ]
        for pattern in patterns:
            matches = glob.glob(pattern)
            if matches:
                return matches[-1]  # Return newest version
    
    # Linux: search common install locations
    elif IS_LINUX:
        patterns = [
            "/tools/Xilinx/Vivado/*/bin/vivado",
            "/opt/Xilinx/Vivado/*/bin/vivado",
        ]
        for pattern in patterns:
            import glob
            matches = glob.glob(pattern)
            if matches:
                return sorted(matches)[-1]  # Return newest version
    
    return ""


def load_config():
    """Load configuration from settings file."""
    global FPGA_PORT, SYSTEM_BAUD, VIVADO_PATH, BITSTREAM_DIR
    
    defaults = get_default_ports()
    vivado_default, bitstream_default = get_default_vivado_paths()
    
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                data = json.load(f)
                FPGA_PORT = data.get("fpga_port", defaults["fpga"])
                SYSTEM_BAUD = data.get("baud_rate", 115200)
                VIVADO_PATH = data.get("vivado_path", vivado_default)
                BITSTREAM_DIR = data.get("bitstream_dir", bitstream_default)
        except Exception as e:
            print(f"Error loading config: {e}")
            _apply_defaults(defaults, vivado_default, bitstream_default)
    else:
        _apply_defaults(defaults, vivado_default, bitstream_default)
    
    # Try to auto-detect Vivado if not configured
    if not VIVADO_PATH or not os.path.exists(VIVADO_PATH):
        detected = find_vivado_executable()
        if detected:
            VIVADO_PATH = detected


def _apply_defaults(port_defaults, vivado_default, bitstream_default):
    """Apply default configuration values."""
    global FPGA_PORT, VIVADO_PATH, BITSTREAM_DIR
    FPGA_PORT = port_defaults["fpga"]
    VIVADO_PATH = vivado_default
    BITSTREAM_DIR = bitstream_default


def save_config(fpga_port=None, baud_rate=None, vivado_path=None, bitstream_dir=None):
    """Save configuration to settings file."""
    global FPGA_PORT, SYSTEM_BAUD, VIVADO_PATH, BITSTREAM_DIR
    
    # Update globals if provided
    if fpga_port is not None:
        FPGA_PORT = fpga_port
    if baud_rate is not None:
        SYSTEM_BAUD = baud_rate
    if vivado_path is not None:
        VIVADO_PATH = vivado_path
    if bitstream_dir is not None:
        BITSTREAM_DIR = bitstream_dir
    
    data = {
        "fpga_port": FPGA_PORT,
        "baud_rate": SYSTEM_BAUD,
        "vivado_path": VIVADO_PATH,
        "bitstream_dir": BITSTREAM_DIR,
    }
    
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False


# Load config on import
load_config()
