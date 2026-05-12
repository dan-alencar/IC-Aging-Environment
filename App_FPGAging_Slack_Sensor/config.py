import json
import os
import platform

_HERE = os.path.dirname(os.path.abspath(__file__))
SETTINGS_FILE = os.path.join(_HERE, "settings.json")

# --- Portas Seriais ---
ARDUINO_PORT = ""
ESP32_PORT = ""
ARDUINO_ENABLED = False

# --- Baudrates ---
ARDUINO_BAUD = 115200
SYSTEM_BAUD = 115200

# --- Parâmetros de Teste ---
LOG_FOLDER = os.path.join(_HERE, "test_logs")
LOG_INTERVAL_MS = 500
DEFAULT_KP = 2.78
DEFAULT_KI = 0.00106
DEFAULT_KD = 5.0


def get_default_ports():
    system = platform.system()
    if system == "Windows":
        return {"arduino": "COM3", "esp32": "COM4"}
    elif system == "Linux":
        return {"arduino": "/dev/ttyUSB0", "esp32": "/dev/ttyUSB1"}
    return {"arduino": "", "esp32": ""}


def load_config():
    global ARDUINO_PORT, ESP32_PORT, ARDUINO_ENABLED
    defaults = get_default_ports()
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                data = json.load(f)
                ESP32_PORT = data.get("esp32_port", defaults["esp32"])
                ARDUINO_PORT = data.get("arduino_port", defaults["arduino"])
                ARDUINO_ENABLED = data.get("arduino_enabled", False)
        except Exception as e:
            print(f"Erro config: {e}")
            _apply_defaults(defaults)
    else:
        _apply_defaults(defaults)


def _apply_defaults(defaults):
    global ARDUINO_PORT, ESP32_PORT, ARDUINO_ENABLED
    ARDUINO_PORT = defaults["arduino"]
    ESP32_PORT = defaults["esp32"]
    ARDUINO_ENABLED = False


def save_config(esp_port, ard_port="", ard_enabled=False):
    global ARDUINO_PORT, ESP32_PORT, ARDUINO_ENABLED
    data = {
        "esp32_port": esp_port,
        "arduino_port": ard_port,
        "arduino_enabled": ard_enabled,
    }
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(data, f, indent=4)
        ESP32_PORT = esp_port
        ARDUINO_PORT = ard_port
        ARDUINO_ENABLED = ard_enabled
        return True
    except Exception as e:
        print(f"Erro ao salvar: {e}")
        return False


load_config()
