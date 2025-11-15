""" # uart_reader.py
from init_serial import attempt_reconnect
from datetime import datetime
import time
import csv
import os

INTERVALO_TEMPO = 2
bytes_to_read = 8
running = True
data_stack = []

# Caminhos fixos para os dispositivos
FPGA_PATH = '/dev/serial/by-id/usb-Digilent_Digilent_USB_Device_210292A6E9A7-if01-port0'
POWER_SUPPLY_PATH = '/dev/serial/by-id/usb-Prolific_Technology_Inc._USB-Serial_Controller-if00-port0'

# Parâmetros de controle de tensão
TARGET_VOLTAGE = 1300
VOLTAGE_STEP = 0.005
VOLTAGE_TOLERANCE = 10
ADJUST_INTERVAL = 2
last_adjust_time = 0

def send_command(psu_ser, command, expect_response=False):
    try:
        if not psu_ser.is_open:
            psu_ser.open()
        psu_ser.reset_input_buffer()
        psu_ser.write(f"{command}\n".encode())
        time.sleep(0.1)
        if expect_response:
            raw_response = psu_ser.readline()
            try:
                return raw_response.decode('utf-8').strip()
            except UnicodeDecodeError:
                print(f"Erro de decodificação (PSU). Dados brutos: {raw_response}")
                return None
    except Exception as e:
        print(f"Erro no comando serial (PSU): {e}")
        return None

def send_f_command(fpga_ser):
    global running
    while running:
        try:
            fpga_ser.write(b'F')
            print("Enviado: 'F' (0x46)")
        except Exception as e:
            print(f"Erro ao enviar: {e}")
            fpga_ser = attempt_reconnect(fpga_ser, static_path=FPGA_PATH)
        time.sleep(INTERVALO_TEMPO)

def read_uart_data(fpga_ser, psu_ser):
    global running, data_stack, last_adjust_time
    while running:
        try:
            data = fpga_ser.read(bytes_to_read)

            if len(data) == bytes_to_read:
                now = datetime.now()
                date_str = now.strftime("%d/%m/%Y")
                time_str = now.strftime("%H:%M:%S")

                fpga_temp = int.from_bytes(data[:3], byteorder='little')
                fpga_slack = int.from_bytes(data[3:5], byteorder='little')
                fpga_voltage = int.from_bytes(data[5:], byteorder='little')

                if fpga_temp == 0 or fpga_slack == 0 or fpga_voltage == 0:
                    time.sleep(INTERVALO_TEMPO)
                    continue

                if fpga_temp > 135000:
                    voltage_str = send_command(psu_ser, 'MEAS:VOLT?', expect_response=True)
                    if voltage_str:
                        try:
                            voltage = float(voltage_str)
                            new_voltage = 1.2
                            send_command(psu_ser, f'VOLT {new_voltage:.3f}')
                            last_adjust_time = time.time()
                            print(f"Tensão ajustada para {new_voltage:.3f} V (temp alta)")
                            time.sleep(INTERVALO_TEMPO)
                            continue
                        except Exception as e:
                            print(f"Erro ao ajustar tensão: {e}")

                if (time.time() - last_adjust_time) > ADJUST_INTERVAL:
                    voltage_str = send_command(psu_ser, 'MEAS:VOLT?', expect_response=True)
                    if voltage_str:
                        try:
                            voltage = float(voltage_str)
                            error = fpga_voltage - TARGET_VOLTAGE
                            if abs(error) > VOLTAGE_TOLERANCE:
                                adjustment = VOLTAGE_STEP if error > 0 else -VOLTAGE_STEP
                                new_voltage = voltage - adjustment
                                send_command(psu_ser, f'VOLT {new_voltage:.3f}')
                                last_adjust_time = time.time()
                                print(f"Tensão ajustada para {new_voltage:.3f} V (erro = {error})")
                        except Exception as e:
                            print(f"Erro ao ajustar tensão: {e}")

                data_stack.append((date_str, time_str, fpga_temp, fpga_slack, fpga_voltage))
                print(f"Dados recebidos: ({date_str}, {time_str}, {fpga_temp}, {fpga_slack}, {fpga_voltage})")
            else:
                print("Dados incompletos recebidos, ignorando...")
        except Exception as e:
            print(f"Erro na leitura da FPGA: {e}")
            fpga_ser = attempt_reconnect(fpga_ser, static_path=FPGA_PATH)

        time.sleep(INTERVALO_TEMPO)

def save_data_to_csv():
    if not data_stack:
        print("Nenhum dado para salvar.")
        return

    now = datetime.now()
    filename = now.strftime("dados_uart_%Y%m%d_%H%M%S.csv")
    filepath = os.path.join(os.getcwd(), filename)

    with open(filepath, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Data", "Hora", "Temperatura", "Slack", "Tensão"])
        writer.writerows(data_stack)

    print(f"\nDados salvos no arquivo {filepath}")

 """
# uart_reader.py
from init_serial import attempt_reconnect
from datetime import datetime
import time
import csv
import os
import threading

INTERVALO_TEMPO = 2
bytes_to_read = 9
running = True
data_stack = []

# Caminhos fixos para os dispositivos
FPGA_PATH = '/dev/serial/by-id/usb-Digilent_Digilent_USB_Device_210292A6E9A7-if01-port0'
POWER_SUPPLY_PATH = '/dev/serial/by-id/usb-Prolific_Technology_Inc._USB-Serial_Controller-if00-port0'

# Parâmetros de controle de tensão
TARGET_VOLTAGE = 1300
VOLTAGE_STEP = 0.005
VOLTAGE_TOLERANCE = 10
ADJUST_INTERVAL = 2
last_adjust_time = 0

lock = threading.Lock()
fpga_temp = 0
fpga_slack = 0
fpga_voltage = 0
fpga_failed = False

def send_command(psu_ser, command, expect_response=False):
    try:
        if not psu_ser.is_open:
            psu_ser.open()
        psu_ser.reset_input_buffer()
        psu_ser.write(f"{command}\n".encode())
        time.sleep(0.1)
        if expect_response:
            raw_response = psu_ser.readline()
            try:
                return raw_response.decode('utf-8').strip()
            except UnicodeDecodeError:
                print(f"Erro de decodificação (PSU). Dados brutos: {raw_response}")
                return None
    except Exception as e:
        print(f"Erro no comando serial (PSU): {e}")
        return None

def send_f_command(fpga_ser): # Na verdade manda um F e lê a serial
    global running
    while running:
        try:
            fpga_ser.write(b'F')
            print("Enviado: 'F' (0x46)")
            time.sleep(INTERVALO_TEMPO)
            data = fpga_ser.read(bytes_to_read)
            if len(data) == bytes_to_read:
                now = datetime.now()
                date_str = now.strftime("%d/%m/%Y")
                time_str = now.strftime("%H:%M:%S")

                with lock:
                    fpga_temp = int.from_bytes(data[:3], byteorder='little')
                    fpga_slack = int.from_bytes(data[3:5], byteorder='little')
                    fpga_voltage = int.from_bytes(data[5:8], byteorder='little')
                    fpga_failed = data[8] > 0
                    if fpga_temp == 0 or fpga_slack == 0 or fpga_voltage == 0:
                        continue
                    data_stack.append((date_str, time_str, fpga_temp, fpga_slack, fpga_voltage, fpga_failed))
                    print(f"Dados recebidos: ({date_str}, {time_str}, {fpga_temp}, {fpga_slack}, {fpga_voltage}, {fpga_failed})")
            else:
                print("Dados incompletos recebidos, ignorando...")
        except Exception as e:
            print(f"Erro na comunicação com FPGA: {e}")
            fpga_ser = attempt_reconnect(fpga_ser, static_path=FPGA_PATH)

def read_uart_data(psu_ser): #Na verdade, lê e setta os dados da fonte
    global running, data_stack, last_adjust_time
    while running:
        with lock:
            if fpga_temp >= 135000:
                voltage_str = send_command(psu_ser, 'MEAS:VOLT?', expect_response=True)
                if voltage_str:
                    try:
                        voltage = float(voltage_str)
                        new_voltage = 1.2
                        send_command(psu_ser, f'VOLT {new_voltage:.3f}')
                        last_adjust_time = time.time()
                        print(f"Tensão ajustada para {new_voltage:.3f} V (temp alta)")

                        continue
                    except Exception as e:
                        print(f"Erro ao ajustar tensão: {e}")
            else:
                voltage_str = send_command(psu_ser, 'MEAS:VOLT?', expect_response=True)
                if voltage_str:
                    try:
                        voltage = float(voltage_str)
                        error = fpga_voltage - TARGET_VOLTAGE
                        if abs(error) > VOLTAGE_TOLERANCE:
                            adjustment = VOLTAGE_STEP if error > 0 else -VOLTAGE_STEP
                            new_voltage = voltage - adjustment
                            send_command(psu_ser, f'VOLT {new_voltage:.3f}')
                            last_adjust_time = time.time()
                            print(f"Tensão ajustada para {new_voltage:.3f} V (erro = {error})")
                    except Exception as e:
                        print(f"Erro ao ajustar tensão: {e}")
        time.sleep(ADJUST_INTERVAL)

def save_data_to_csv():
    if not data_stack:
        print("Nenhum dado para salvar.")
        return

    now = datetime.now()
    filename = now.strftime("dados_uart_%Y%m%d_%H%M%S.csv")
    filepath = os.path.join(os.getcwd(), filename)

    with open(filepath, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Data", "Hora", "Temperatura", "Slack", "Tensão", "Falha"])
        writer.writerows(data_stack)

    print(f"\nDados salvos no arquivo {filepath}")
