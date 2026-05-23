import json
import os

SETTINGS_FILE = "settings.json"

# Serial ports
DUT_PORT     = ""
DUT_BAUD     = 9600
ARDUINO_PORT = ""
ARDUINO_BAUD = 115200
PSU_PORT     = ""
PSU_BAUD     = 9600

ARDUINO_ENABLED = False
PSU_ENABLED     = False

# ── Corner sweep parameters ───────────────────────────────────────────────────
# Corners measured high-to-low so the device is stressed progressively.
CORNERS_V          = [1.1, 1.0, 0.9]  # V — characterisation voltages

SWEEP_STEP_V       = 0.01   # V per step in failure-point sweep
SWEEP_MIN_V        = 0.70   # V — safety floor (stop sweep here even if no error)

SAMPLES_PER_CORNER = 30     # ticks collected at each corner (30 s at 1 Hz)
SWEEP_SAMPLE_TICKS = 5      # ticks at each sweep voltage before stepping down

SETTLE_TICKS         = 5   # consecutive ticks within tolerance → declared stable
SETTLE_TIMEOUT_TICKS = 30  # give up waiting after this many ticks and proceed
VOLT_SETTLE_TOL_V    = 0.03 # ±30 mV VCCINT tolerance for "settled"

TEMP_STABLE_TICKS = 60     # consecutive ticks within tolerance → temp declared stable
TEMP_STABLE_TOL_C = 3.0   # ±3 °C dead-band around target DUT temperature

# ── PSU / safety limits ───────────────────────────────────────────────────────
PSU_MIN_V         = 0.60   # absolute PSU command floor (V)
PSU_MAX_V         = 1.50   # absolute PSU command ceiling (V)
MAX_PSU_CURRENT_A = 1.5    # safety cutoff (A)
MAX_OVEN_TEMP_C   = 130.0
MAX_DUT_TEMP_C    = 140.0

# ── Logging ──────────────────────────────────────────────────────────────────
LOG_FOLDER      = os.path.join(os.getcwd(), "test_logs")
LOG_INTERVAL_MS = 1000


def load_config():
    global DUT_PORT, DUT_BAUD, ARDUINO_PORT, ARDUINO_BAUD
    global PSU_PORT, PSU_BAUD, ARDUINO_ENABLED, PSU_ENABLED

    if not os.path.exists(SETTINGS_FILE):
        return
    try:
        with open(SETTINGS_FILE) as f:
            d = json.load(f)
        DUT_PORT        = d.get("dut_port", "")
        DUT_BAUD        = int(d.get("dut_baud", 9600))
        ARDUINO_PORT    = d.get("arduino_port", "")
        ARDUINO_BAUD    = int(d.get("arduino_baud", 115200))
        PSU_PORT        = d.get("psu_port", "")
        PSU_BAUD        = int(d.get("psu_baud", 9600))
        ARDUINO_ENABLED = bool(d.get("arduino_enabled", False))
        PSU_ENABLED     = bool(d.get("psu_enabled", False))
    except Exception as e:
        print(f"[config] load error: {e}")


def save_config(dut_p, dut_b, arduino_p, arduino_b, arduino_en, psu_p, psu_b, psu_en):
    global DUT_PORT, DUT_BAUD, ARDUINO_PORT, ARDUINO_BAUD
    global PSU_PORT, PSU_BAUD, ARDUINO_ENABLED, PSU_ENABLED

    data = {
        "dut_port":       dut_p,       "dut_baud":       int(dut_b),
        "arduino_port":   arduino_p,   "arduino_baud":   int(arduino_b),
        "arduino_enabled": arduino_en,
        "psu_port":       psu_p,       "psu_baud":       int(psu_b),
        "psu_enabled":    psu_en,
    }
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(data, f, indent=4)
        DUT_PORT = dut_p;   DUT_BAUD = int(dut_b)
        ARDUINO_PORT = arduino_p; ARDUINO_BAUD = int(arduino_b); ARDUINO_ENABLED = arduino_en
        PSU_PORT = psu_p;   PSU_BAUD = int(psu_b); PSU_ENABLED = psu_en
        return True
    except Exception as e:
        print(f"[config] save error: {e}")
        return False


load_config()
