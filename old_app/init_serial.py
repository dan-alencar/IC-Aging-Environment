# init_serial.py
import serial
import serial.tools.list_ports
import time

baud_rate = 9600
timeout = 1


def find_matching_port(target_description=None, target_vid=None, target_pid=None):
    ports = serial.tools.list_ports.comports()
    for p in ports:
        if (target_description and target_description in p.description) or \
           (target_vid and p.vid == target_vid) or \
           (target_pid and p.pid == target_pid):
            return p.device
    return None


def initialize_serial(static_path='usb-Digilent_Digilent_USB_Device_210292A6E9A7-if01-port0', paridade="N"):
    try:
        return serial.Serial(static_path, baudrate=baud_rate, timeout=timeout, parity=paridade)
    except Exception as e:
        print(f"Erro ao abrir porta serial estática: {e}")
        return None


def attempt_reconnect(current_ser, static_path='usb-Digilent_Digilent_USB_Device_210292A6E9A7-if01-port0'):
    try:
        if current_ser and current_ser.is_open:
            current_ser.close()
    except:
        pass

    print("Tentando reconectar ao dispositivo serial...")

    while True:
        try:
            new_ser = serial.Serial(static_path, baudrate=baud_rate, timeout=timeout)
            print(f"Reconectado com sucesso em {static_path}")
            return new_ser
        except Exception as e:
            print(f"Erro ao abrir {static_path}: {e}")
        time.sleep(3)

