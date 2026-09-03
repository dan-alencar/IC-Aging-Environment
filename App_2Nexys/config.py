"""
App_2Nexys — Central configuration module.

Differences from App_Nexys/config.py:
  - Two DUT ports (DUT_0, DUT_1) instead of one.
  - Two PSU ports (PSU_0 = IT6502D, PSU_1 = E3634A) instead of one.
  - VCCINT closed-loop parameters: setpoints per DUT and a shared P-gain.
  - Arduino (shared oven) is optional, same as App_Nexys.

Persisted to settings.json in this directory via load_config()/save_config().
"""
import json
import os
import platform
import shutil

_HERE = os.path.dirname(os.path.abspath(__file__))
SETTINGS_FILE = os.path.join(_HERE, "settings.json")

# =============================================================================
#   FIXED USB DEVICE IDs (from /dev/serial/by-id/)
#
#   DUT-0 and DUT-1 are Nexys4 DDR boards (Digilent FTDI, if01 = UART data).
#   PSU-1 is the Agilent E3634A via a Prolific USB-Serial adapter.
#   PSU-0 (IT6502D) uses USB-TMC VISA and is selected manually in the dialog.
# =============================================================================
_SERIAL_BY_ID = "/dev/serial/by-id"
USB_ID_DUT0 = "usb-Digilent_Digilent_USB_Device_210292A6E9A7-if01-port0"
USB_ID_DUT1 = "usb-Digilent_Digilent_USB_Device_210292745007-if01-port0"
USB_ID_PSU1 = "usb-Prolific_Technology_Inc._USB-Serial_Controller_BDDCb12CJ06-if00-port0"

# =============================================================================
#   DUT-0 SRAM PROGRAMMING (Vivado batch mode)
#
#   DUT-0's flash is broken — only SRAM works. The bitstream must be loaded
#   via JTAG every time the 1V0 rail is toggled. Programming happens
#   automatically at test start, after the PSU stabilisation delay.
# =============================================================================
_REPO_ROOT = os.path.dirname(_HERE)
DUT0_DIGILENT_SERIAL = "210292A6E9A7"   # Vivado hw_target wildcard match
DUT1_DIGILENT_SERIAL = "210292745007"
BITSTREAM_PATH = os.path.join(
    _REPO_ROOT, "vivado", "aging_study_nexys4ddr",
    "build", "aging_study_nexys4ddr", "aging_study_nexys4ddr.runs",
    "impl_1", "nexys4_aging_top.bit",
)
BITSTREAM_LTX = os.path.join(
    _REPO_ROOT, "vivado", "aging_study_nexys4ddr",
    "build", "aging_study_nexys4ddr", "aging_study_nexys4ddr.runs",
    "impl_1", "nexys4_aging_top.ltx",
)
# Resolution order: VIVADO_BIN env var override -> vivado found on PATH -> the
# historical hardcoded lab-machine path, kept only as a last-resort fallback
# so existing setups don't break. Update the fallback (or just set the env
# var) when running on a different machine.
VIVADO_BIN = (
    os.environ.get("VIVADO_BIN")
    or shutil.which("vivado")
    or "/home/andre/Xilinx/2025.1/Vivado/bin/vivado"
)
PSU_STABILISE_DELAY_S = 5   # seconds to wait after PSU turn-on before programming

# --- DUT serial ports (Nexys4 DDR — pick the higher ttyUSB* of each board pair) ---
DUT_0_PORT = ""
DUT_0_BAUD = 9600
DUT_1_PORT = ""
DUT_1_BAUD = 9600

# --- PSU ports ---
# PSU_0: IT6502D — USB-TMC, appears as VISA resource (USB0::...::INSTR)
# PSU_1: Agilent E3634A — RS-232 via Prolific USB-Serial adapter, appears as ttyUSB*
PSU_0_PORT = ""
PSU_0_BAUD = 9600
PSU_0_ENABLED = False
PSU_1_PORT = ""
PSU_1_BAUD = 9600
PSU_1_ENABLED = False

# --- Arduino (shared oven PID) ---
ARDUINO_PORT = ""
ARDUINO_BAUD = 115200
ARDUINO_ENABLED = False

# =============================================================================
#   PID OVEN PARAMETERS (identical to App_Nexys — SIMC-tuned, do not change)
# =============================================================================
# FOPDT model: G(s) = 1.56 * exp(-150.6s) / (1307.2s + 1)
PID_KP = 2.78
PID_KI = 0.00106
PID_KD = 5.0

DEFAULT_RAMP_RATE_C_PER_SEC = 1.0
DEFAULT_OVEN_SAMPLE_TIME_MS = 5000

# =============================================================================
#   VCCINT CLOSED-LOOP VOLTAGE CONTROL
# =============================================================================
# The FPGA XADC reports actual VCCINT via serial. The app trims each PSU's
# output voltage by VOLTAGE_KP * (setpoint - measured_vccint) each log tick.
# VOLTAGE_KP is intentionally conservative (0.1 V/V) to avoid oscillation.
VCCINT_SETPOINT_0_V = 1.0   # Target VCCINT for DUT 0 (V)
VCCINT_SETPOINT_1_V = 1.0   # Target VCCINT for DUT 1 (V)
VOLTAGE_KP = 0.1             # Proportional gain for VCCINT loop (V/V)
PSU_MIN_V = 0.0
PSU_MAX_V = 1.5

# =============================================================================
#   SAFETY LIMITS
# =============================================================================
MAX_OVEN_TEMP_C = 130.0
MAX_DUT_TEMP_C = 140.0
MAX_PSU_CURRENT_A = 1.5

# =============================================================================
#   LOGGING
# =============================================================================
LOG_FOLDER = os.path.join(_HERE, "test_logs")
LOG_INTERVAL_MS = 1000


# =============================================================================
#   HELPERS
# =============================================================================
def resolve_hw_ports():
    """Resolve DUT-0, DUT-1, PSU-1 ports from /dev/serial/by-id/ symlinks."""
    global DUT_0_PORT, DUT_1_PORT, PSU_1_PORT
    for attr, uid in [
        ("DUT_0_PORT", USB_ID_DUT0),
        ("DUT_1_PORT", USB_ID_DUT1),
        ("PSU_1_PORT", USB_ID_PSU1),
    ]:
        link = os.path.join(_SERIAL_BY_ID, uid)
        if os.path.exists(link):
            globals()[attr] = os.path.realpath(link)
        else:
            print(f"[config] USB device not found: {uid}")


def get_default_ports():
    system = platform.system()
    if system == "Windows":
        return {"dut0": "COM3", "dut1": "COM4", "arduino": "COM5",
                "psu0": "USB0::0x0000::0x0000::0::INSTR",
                "psu1": "USB0::0x0000::0x0000::1::INSTR"}
    return {"dut0": "/dev/ttyUSB1", "dut1": "/dev/ttyUSB3", "arduino": "/dev/ttyACM0",
            "psu0": "USB0::0x0000::0x0000::0::INSTR",
            "psu1": "/dev/ttyUSB0"}


def load_config():
    global DUT_0_PORT, DUT_0_BAUD, DUT_1_PORT, DUT_1_BAUD
    global PSU_0_PORT, PSU_0_BAUD, PSU_0_ENABLED
    global PSU_1_PORT, PSU_1_BAUD, PSU_1_ENABLED
    global ARDUINO_PORT, ARDUINO_BAUD, ARDUINO_ENABLED
    global VCCINT_SETPOINT_0_V, VCCINT_SETPOINT_1_V

    defaults = get_default_ports()

    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                d = json.load(f)
            DUT_0_PORT = d.get("dut0_port", defaults["dut0"])
            DUT_0_BAUD = int(d.get("dut0_baud", 9600))
            DUT_1_PORT = d.get("dut1_port", defaults["dut1"])
            DUT_1_BAUD = int(d.get("dut1_baud", 9600))
            PSU_0_PORT = d.get("psu0_port", defaults["psu0"])
            PSU_0_BAUD = int(d.get("psu0_baud", 9600))
            PSU_0_ENABLED = d.get("psu0_enabled", False)
            PSU_1_PORT = d.get("psu1_port", defaults["psu1"])
            PSU_1_BAUD = int(d.get("psu1_baud", 9600))
            PSU_1_ENABLED = d.get("psu1_enabled", False)
            ARDUINO_PORT = d.get("arduino_port", defaults["arduino"])
            ARDUINO_BAUD = int(d.get("arduino_baud", 115200))
            ARDUINO_ENABLED = d.get("arduino_enabled", False)
            VCCINT_SETPOINT_0_V = float(d.get("vccint_sp0", 1.0))
            VCCINT_SETPOINT_1_V = float(d.get("vccint_sp1", 1.0))
        except Exception as e:
            print(f"Config read error: {e}. Using defaults.")
            _apply_defaults(defaults)
    else:
        _apply_defaults(defaults)

    resolve_hw_ports()


def _apply_defaults(defaults):
    global DUT_0_PORT, DUT_0_BAUD, DUT_1_PORT, DUT_1_BAUD
    global PSU_0_PORT, PSU_0_BAUD, PSU_0_ENABLED
    global PSU_1_PORT, PSU_1_BAUD, PSU_1_ENABLED
    global ARDUINO_PORT, ARDUINO_BAUD, ARDUINO_ENABLED

    DUT_0_PORT = defaults["dut0"]
    DUT_0_BAUD = 9600
    DUT_1_PORT = defaults["dut1"]
    DUT_1_BAUD = 9600
    PSU_0_PORT = defaults["psu0"]
    PSU_0_BAUD = 9600
    PSU_0_ENABLED = False
    PSU_1_PORT = defaults["psu1"]
    PSU_1_BAUD = 9600
    PSU_1_ENABLED = False
    ARDUINO_PORT = defaults["arduino"]
    ARDUINO_BAUD = 115200
    ARDUINO_ENABLED = False


def save_config(dut0_p, dut0_b, dut1_p, dut1_b,
                psu0_p="", psu0_b=9600, psu0_enabled=False,
                psu1_p="", psu1_b=9600, psu1_enabled=False,
                arduino_p="", arduino_b=115200, arduino_enabled=False,
                vccint_sp0=1.0, vccint_sp1=1.0):
    global DUT_0_PORT, DUT_0_BAUD, DUT_1_PORT, DUT_1_BAUD
    global PSU_0_PORT, PSU_0_BAUD, PSU_0_ENABLED
    global PSU_1_PORT, PSU_1_BAUD, PSU_1_ENABLED
    global ARDUINO_PORT, ARDUINO_BAUD, ARDUINO_ENABLED
    global VCCINT_SETPOINT_0_V, VCCINT_SETPOINT_1_V

    data = {
        "dut0_port": dut0_p, "dut0_baud": dut0_b,
        "dut1_port": dut1_p, "dut1_baud": dut1_b,
        "psu0_port": psu0_p, "psu0_baud": psu0_b, "psu0_enabled": psu0_enabled,
        "psu1_port": psu1_p, "psu1_baud": psu1_b, "psu1_enabled": psu1_enabled,
        "arduino_port": arduino_p, "arduino_baud": arduino_b, "arduino_enabled": arduino_enabled,
        "vccint_sp0": vccint_sp0, "vccint_sp1": vccint_sp1,
    }
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(data, f, indent=4)
        DUT_0_PORT = dut0_p;  DUT_0_BAUD = int(dut0_b)
        DUT_1_PORT = dut1_p;  DUT_1_BAUD = int(dut1_b)
        PSU_0_PORT = psu0_p;  PSU_0_BAUD = int(psu0_b);  PSU_0_ENABLED = psu0_enabled
        PSU_1_PORT = psu1_p;  PSU_1_BAUD = int(psu1_b);  PSU_1_ENABLED = psu1_enabled
        ARDUINO_PORT = arduino_p; ARDUINO_BAUD = int(arduino_b); ARDUINO_ENABLED = arduino_enabled
        VCCINT_SETPOINT_0_V = float(vccint_sp0)
        VCCINT_SETPOINT_1_V = float(vccint_sp1)
        return True
    except Exception as e:
        print(f"Config save error: {e}")
        return False


def get_pid_info_string():
    return f"PID[Kp={PID_KP:.4f}, Ki={PID_KI:.6f}, Kd={PID_KD:.4f}]"


load_config()
