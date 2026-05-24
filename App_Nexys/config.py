"""
=============================================================================
TCC - Arquivo de Configuração Central (VERSÃO FINAL)
=============================================================================
Gerencia configurações de hardware e parâmetros do sistema.
Persistência via settings.json.

Autor: [Seu Nome]
Data: Janeiro/2026
=============================================================================
"""
import json
import os
import platform

# =============================================================================
#   ARQUIVO DE PERSISTÊNCIA
# =============================================================================
SETTINGS_FILE = "settings.json"

# =============================================================================
#   CONFIGURAÇÕES DE PORTA SERIAL (Atualizadas pelo Setup)
# =============================================================================
ARDUINO_PORT = ""
PSU_PORT = ""
DUT_PORT = ""

ARDUINO_BAUD = 115200
DUT_BAUD     = 9600
# PSU uses USB-TMC/VISA — no baud rate

ARDUINO_ENABLED = False
PSU_ENABLED = False

# =============================================================================
#   PARÂMETROS DO SISTEMA DE TESTE
# =============================================================================
LOG_FOLDER = os.path.join(os.getcwd(), "test_logs") 
LOG_INTERVAL_MS = 1000  # Intervalo de amostragem (ms)

# =============================================================================
#   PARÂMETROS PID (FIXOS - CALCULADOS VIA SIMC)
# =============================================================================
# IMPORTANTE: Estes valores foram identificados experimentalmente via step test
# e validados em testes de longa duração. NÃO alterar sem nova identificação.
#
# Modelo FOPDT identificado:
#   G(s) = 1.56 * e^(-150.6s) / (1307.2s + 1)
#
# Parâmetros:
#   K (ganho)       = 1.56 °C/%
#   θ (tempo morto) = 150.6 s
#   τ (constante)   = 1307.2 s
#   θ/τ             = 0.115
#
# Método SIMC com τc = θ:
PID_KP = 2.78
PID_KI = 0.00106
PID_KD = 5.0

# Parâmetros de rampa
DEFAULT_RAMP_RATE_C_PER_SEC = 1.0 
DEFAULT_OVEN_SAMPLE_TIME_MS = 5000

# =============================================================================
#   VCCINT CLOSED-LOOP VOLTAGE CONTROL (IT6502D)
# =============================================================================
# TestSequencer trims PSU output each log tick: psu_cmd += VOLTAGE_KP * (setpoint - vccint).
# VOLTAGE_KP is conservative to avoid oscillation.
VCCINT_SETPOINT_V = 1.0   # Target VCCINT (V) — set from setup dialog
VOLTAGE_KP = 0.1           # Proportional gain (V/V)
PSU_MIN_V = 0.0
PSU_MAX_V = 1.5

# =============================================================================
#   LIMITES DE SEGURANÇA
# =============================================================================
MAX_OVEN_TEMP_C = 130.0      # Temperatura máxima do forno
MAX_DUT_TEMP_C = 160.0       # Temperatura máxima do DUT
MAX_PSU_CURRENT_A = 3.0      # Corrente máxima da fonte

# =============================================================================
#   FUNÇÕES DE CONFIGURAÇÃO
# =============================================================================

def get_default_ports():
    """Retorna portas padrão baseadas no Sistema Operacional."""
    system = platform.system()
    if system == "Windows":
        return {"arduino": "COM3", "psu": "", "dut": "COM5"}
    elif system == "Linux":
        return {"arduino": "/dev/ttyUSB0", "psu": "", "dut": "/dev/ttyACM0"}
    return {"arduino": "", "psu": "", "dut": ""}


def load_config():
    """Carrega as configurações (Portas e Bauds) do arquivo JSON."""
    global ARDUINO_PORT, PSU_PORT, DUT_PORT
    global ARDUINO_BAUD, DUT_BAUD
    global ARDUINO_ENABLED, PSU_ENABLED
    global VCCINT_SETPOINT_V

    defaults = get_default_ports()

    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                data = json.load(f)

                ARDUINO_PORT = data.get("arduino_port", defaults["arduino"])
                psu_p        = data.get("psu_port", "")
                # Reject legacy serial paths and ASRL VISA strings — IT6502D uses USB-TMC
                PSU_PORT     = psu_p if psu_p.startswith("USB") else ""
                DUT_PORT     = data.get("dut_port", defaults["dut"])

                ARDUINO_BAUD = int(data.get("arduino_baud", 115200))
                DUT_BAUD     = int(data.get("dut_baud", 9600))

                ARDUINO_ENABLED   = data.get("arduino_enabled", False)
                PSU_ENABLED       = data.get("psu_enabled", False)
                VCCINT_SETPOINT_V = float(data.get("vccint_setpoint", 1.0))

        except Exception as e:
            print(f"Erro ao ler config: {e}. Usando padrões.")
            _apply_defaults(defaults)
    else:
        _apply_defaults(defaults)


def _apply_defaults(defaults):
    """Aplica configurações padrão."""
    global ARDUINO_PORT, PSU_PORT, DUT_PORT
    global ARDUINO_BAUD, DUT_BAUD
    global ARDUINO_ENABLED, PSU_ENABLED
    global VCCINT_SETPOINT_V

    ARDUINO_PORT = defaults["arduino"]
    PSU_PORT     = ""
    DUT_PORT     = defaults["dut"]
    ARDUINO_BAUD = 115200
    DUT_BAUD     = 9600
    ARDUINO_ENABLED   = False
    PSU_ENABLED       = False
    VCCINT_SETPOINT_V = 1.0


def save_config(dut_p, dut_b,
                arduino_p="", arduino_b=115200, arduino_enabled=False,
                psu_p="", psu_enabled=False,
                vccint_setpoint=1.0):
    """Salva portas/recursos e flags de habilitação no arquivo JSON."""
    global ARDUINO_PORT, PSU_PORT, DUT_PORT
    global ARDUINO_BAUD, DUT_BAUD
    global ARDUINO_ENABLED, PSU_ENABLED
    global VCCINT_SETPOINT_V

    data = {
        "dut_port":        dut_p,
        "dut_baud":        dut_b,
        "arduino_port":    arduino_p,
        "arduino_baud":    arduino_b,
        "arduino_enabled": arduino_enabled,
        "psu_port":        psu_p,   # USB-TMC VISA resource string
        "psu_enabled":     psu_enabled,
        "vccint_setpoint": vccint_setpoint,
    }

    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(data, f, indent=4)

        DUT_PORT     = dut_p
        DUT_BAUD     = int(dut_b)
        ARDUINO_PORT = arduino_p
        ARDUINO_BAUD = int(arduino_b)
        ARDUINO_ENABLED   = arduino_enabled
        PSU_PORT          = psu_p
        PSU_ENABLED       = psu_enabled
        VCCINT_SETPOINT_V = float(vccint_setpoint)
        return True

    except Exception as e:
        print(f"Erro ao salvar configurações: {e}")
        return False


def get_pid_info_string():
    """Retorna string formatada com informações do PID para logs."""
    return f"PID[Kp={PID_KP:.4f}, Ki={PID_KI:.6f}, Kd={PID_KD:.4f}]"


def get_system_info():
    """Retorna dicionário com informações do sistema para log."""
    return {
        "pid_kp": PID_KP,
        "pid_ki": PID_KI,
        "pid_kd": PID_KD,
        "ramp_rate": DEFAULT_RAMP_RATE_C_PER_SEC,
        "sample_time_ms": DEFAULT_OVEN_SAMPLE_TIME_MS,
        "log_interval_ms": LOG_INTERVAL_MS,
        "max_oven_temp": MAX_OVEN_TEMP_C,
        "max_dut_temp": MAX_DUT_TEMP_C,
        "max_current": MAX_PSU_CURRENT_A
    }


# Carrega configuração ao importar o módulo
load_config()
