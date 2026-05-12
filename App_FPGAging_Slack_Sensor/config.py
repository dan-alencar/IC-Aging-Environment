import json
import os
import platform

SETTINGS_FILE = "settings.json"

# --- Variáveis Globais ---
ARDUINO_PORT = ""       # Arduino Nano 33 IoT (PID Forno)
ESP32_PORT = ""         # ESP32 WROOM (Ponte para o Sistema)

# Baudrates (Alinhados com seus firmwares)
ARDUINO_BAUD = 115200   # PID_Controller.ino usa 115200
SYSTEM_BAUD = 115200    # esp32wroom_uart-reader.ino usa 125000

# --- Parâmetros de Teste ---
LOG_FOLDER = os.path.join(os.getcwd(), "test_logs") 
LOG_INTERVAL_MS = 500  
DEFAULT_KP = 2.78      # Atualizado conforme seu firmware
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
    global ARDUINO_PORT, ESP32_PORT, ARDUINO_BAUD, SYSTEM_BAUD
    defaults = get_default_ports()
    
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                data = json.load(f)
                ARDUINO_PORT = data.get("arduino_port", defaults["arduino"])
                ESP32_PORT = data.get("esp32_port", defaults["esp32"])
        except Exception as e:
            print(f"Erro config: {e}")
            _apply_defaults(defaults)
    else:
        _apply_defaults(defaults)

def _apply_defaults(defaults):
    global ARDUINO_PORT, ESP32_PORT
    ARDUINO_PORT = defaults["arduino"]
    ESP32_PORT = defaults["esp32"]

def save_config(ard_port, esp_port):
    global ARDUINO_PORT, ESP32_PORT
    data = {
        "arduino_port": ard_port,
        "esp32_port": esp_port
    }
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(data, f, indent=4)
        ARDUINO_PORT = ard_port
        ESP32_PORT = esp_port
        return True
    except Exception as e:
        print(f"Erro ao salvar: {e}")
        return False

load_config()