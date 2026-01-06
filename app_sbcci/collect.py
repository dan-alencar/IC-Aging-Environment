""" # main.py
from init_serial import initialize_serial, attempt_reconnect
from uart_reader import read_uart_data, send_f_command, FPGA_PATH, POWER_SUPPLY_PATH, save_data_to_csv
import signal
import threading
import time
import sys

running = True

def signal_handler(sig, frame):
    global running
    print("\nEncerrando o programa...")
    running = False
    time.sleep(1)
    save_data_to_csv()
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)

    fpga_ser = initialize_serial(static_path=FPGA_PATH)
    psu_ser = initialize_serial(static_path=POWER_SUPPLY_PATH)

    if not fpga_ser or not psu_ser:
        print("Erro ao inicializar uma ou mais portas seriais.")
        sys.exit(1)

    print("Dispositivos conectados. Iniciando comunicação...")

    sender_thread = threading.Thread(target=send_f_command, args=(fpga_ser,), daemon=True)
    sender_thread.start()

    reader_thread = threading.Thread(target=read_uart_data, args=(fpga_ser, psu_ser), daemon=True)
    reader_thread.start()

    while running:
        time.sleep(1)
 """
# main.py
from init_serial import initialize_serial, attempt_reconnect
from uart_reader import read_uart_data, send_f_command, FPGA_PATH, POWER_SUPPLY_PATH, save_data_to_csv
import signal
import threading
import time
import sys

running = True

def signal_handler(sig, frame):
    global running
    print("\nEncerrando o programa...")
    running = False
    time.sleep(1)
    save_data_to_csv()
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)

    fpga_ser = initialize_serial(static_path=FPGA_PATH, paridade="E")
    psu_ser = initialize_serial(static_path=POWER_SUPPLY_PATH)

    if not fpga_ser or not psu_ser:
        print("Erro ao inicializar uma ou mais portas seriais.")
        sys.exit(1)

    print("Dispositivos conectados. Iniciando comunicação...")

    sender_thread = threading.Thread(target=send_f_command, args=(fpga_ser,), daemon=True)
    sender_thread.start()

    reader_thread = threading.Thread(target=read_uart_data, args=(psu_ser,), daemon=True)
    reader_thread.start()

    while running:
        time.sleep(1)
