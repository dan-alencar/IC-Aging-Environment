"""
Arquivo de Configuração Central (Multiplataforma)
Gerencia configurações de Portas e Baud Rates via settings.json.
"""
import json
import os
import platform

# --- Arquivo de Persistência ---
SETTINGS_FILE = "settings.json"

# --- Variáveis Globais (Atualizadas pelo Setup) ---
ARDUINO_PORT = ""
PSU_PORT = ""
DUT_PORT = ""

# Agora estas variáveis são dinâmicas, mas iniciam com um valor seguro
ARDUINO_BAUD = 115200
PSU_BAUD = 9600
DUT_BAUD = 9600

# --- Parâmetros de Teste ---
LOG_FOLDER = os.path.join(os.getcwd(), "test_logs") 
LOG_INTERVAL_MS = 1000
DEFAULT_KP = 1.39
DEFAULT_KI = 0.00106
DEFAULT_KD = 10.45
DEFAULT_RAMP_RATE_C_PER_SEC = 0.5 
DEFAULT_OVEN_SAMPLE_TIME_MS = 5000

def get_default_ports():
    """Retorna portas padrão baseadas no Sistema Operacional."""
    system = platform.system()
    if system == "Windows":
        return {"arduino": "COM3", "psu": "COM4", "dut": "COM5"}
    elif system == "Linux":
        return {"arduino": "/dev/ttyUSB0", "psu": "/dev/ttyUSB1", "dut": "/dev/ttyACM0"}
    return {"arduino": "", "psu": "", "dut": ""}

def load_config():
    """Carrega as configurações (Portas e Bauds) do JSON."""
    global ARDUINO_PORT, PSU_PORT, DUT_PORT
    global ARDUINO_BAUD, PSU_BAUD, DUT_BAUD
    
    defaults = get_default_ports()
    
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                data = json.load(f)
                
                # Carrega Portas
                ARDUINO_PORT = data.get("arduino_port", defaults["arduino"])
                PSU_PORT = data.get("psu_port", defaults["psu"])
                DUT_PORT = data.get("dut_port", defaults["dut"])
                
                # Carrega Bauds (com fallback para os valores padrão originais)
                ARDUINO_BAUD = int(data.get("arduino_baud", 115200))
                PSU_BAUD = int(data.get("psu_baud", 9600))
                DUT_BAUD = int(data.get("dut_baud", 9600))
                
        except Exception as e:
            print(f"Erro ao ler config: {e}. Usando padrões.")
            _apply_defaults(defaults)
    else:
        _apply_defaults(defaults)

def _apply_defaults(defaults):
    global ARDUINO_PORT, PSU_PORT, DUT_PORT
    global ARDUINO_BAUD, PSU_BAUD, DUT_BAUD
    ARDUINO_PORT = defaults["arduino"]
    PSU_PORT = defaults["psu"]
    DUT_PORT = defaults["dut"]
    ARDUINO_BAUD = 115200
    PSU_BAUD = 9600
    DUT_BAUD = 9600

def save_config(arduino_p, psu_p, dut_p, arduino_b, psu_b, dut_b):
    """Salva Portas e Bauds no arquivo JSON."""
    global ARDUINO_PORT, PSU_PORT, DUT_PORT
    global ARDUINO_BAUD, PSU_BAUD, DUT_BAUD
    
    data = {
        "arduino_port": arduino_p,
        "psu_port": psu_p,
        "dut_port": dut_p,
        "arduino_baud": arduino_b,
        "psu_baud": psu_b,
        "dut_baud": dut_b
    }
    
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(data, f, indent=4)
        
        # Atualiza memória
        ARDUINO_PORT = arduino_p
        PSU_PORT = psu_p
        DUT_PORT = dut_p
        ARDUINO_BAUD = int(arduino_b)
        PSU_BAUD = int(psu_b)
        DUT_BAUD = int(dut_b)
        return True
    except Exception as e:
        print(f"Erro ao salvar configurações: {e}")
        return False

load_config()