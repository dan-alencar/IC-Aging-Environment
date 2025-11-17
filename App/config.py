"""
Arquivo de Configuração Central

Edite os valores aqui para ajustar os parâmetros do sistema
sem precisar alterar o código da HMI ou dos workers.
"""

# --- Configurações das Portas Seriais (Linux) ---
# Use 'dmesg | grep tty' ou 'ls /dev/serial/by-id/' para encontrar
ARDUINO_PORT = "/dev/serial/by-id/usb-Arduino_LLC_Arduino_NANO_33_IoT_40C381DB51544C3954202020FF082015-if00"
PSU_PORT = "/dev/serial/by-id/usb-Prolific_Technology_Inc._USB-Serial_Controller-if00-port0"
DUT_PORT = "/dev/serial/by-id/usb-Digilent_Digilent_USB_Device_210292A6E9A7-if01-port0"

# --- Configurações das Portas Seriais (Windows) ---
# ARDUINO_PORT = "COM3"
# PSU_PORT = "COM4"
# DUT_PORT = "COM5"

# --- Configurações de Comunicação ---
ARDUINO_BAUD = 115200
PSU_BAUD = 9600
DUT_BAUD = 9600

# --- Parâmetros de Teste ---
LOG_FOLDER = "test_logs" # Pasta para salvar os CSVs
LOG_INTERVAL_MS = 1000   # Intervalo de log (1 segundo)

# --- Ganhos PID Padrão (Sintonizados) ---
# O operador poderá mudar isso na HMI
DEFAULT_KP = 2.78 #testar com 1.39
DEFAULT_KI = 0.00106  # Ki correto para ArduPID (Kp / Tau_I)
DEFAULT_KD = 5.0  #testar com 4.0

# --- Outros Parâmetros do PID ---
DEFAULT_RAMP_RATE_C_PER_SEC = 0.5 # °C por segundo
DEFAULT_OVEN_SAMPLE_TIME_MS = 5000 # 5 segundos