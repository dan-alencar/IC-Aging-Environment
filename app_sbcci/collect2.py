import serial
import time
import csv
import signal
import sys
import threading
from datetime import datetime

# Configuração da porta serial
port = '/dev/ttyUSB1'  # Substitua pela porta correta
baud_rate = 9600       # Taxa de transmissão (ajuste conforme necessário)
bytes_to_read = 8      # Agora lemos 8 bytes por ciclo
timeout = 1            # Timeout para a leitura

# Intervalo de tempo compartilhado (em segundos)
INTERVALO_TEMPO = 10

# Lista para armazenar as tuplas de dados lidos
data_stack = []
running = True  # Controle para encerrar as threads

# Função para gerar um nome de arquivo único com base na data e hora
def generate_file_name(base_name="uart_data"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base_name}_{timestamp}.csv"

# Função para salvar os dados acumulados em um arquivo CSV
def save_to_file():
    file_name = generate_file_name()
    with open(file_name, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Data", "Hora", "Temperatura", "Incrementos", "Tensão"])  # Cabeçalhos
        writer.writerows(data_stack)
    print(f"\nDados salvos no arquivo {file_name}")

# Tratador de sinal para salvar os dados ao receber SIGINT (Ctrl+C)
def signal_handler(sig, frame):
    global running
    print("\nEncerrando o programa...")
    running = False  # Sinaliza para encerrar as threads
    save_to_file()
    sys.exit(0)

# Função para enviar "F" (0x46 em ASCII) a cada INTERVALO_TEMPO segundos
def send_f_command(ser):
    while running:
        ser.write(b'F')
        print("Enviado: 'F' (0x46)")
        time.sleep(INTERVALO_TEMPO)

# Função para coletar dados da UART a cada INTERVALO_TEMPO segundos
def read_uart_data(ser):
    while running:
        try:
            # Lê 8 bytes da UART
            data = ser.read(bytes_to_read)

            # Verifica se foram lidos os 8 bytes esperados
            if len(data) == bytes_to_read:
                # Obtém a data e hora do momento da coleta
                now = datetime.now()
                date_str = now.strftime("%d/%m/%Y")
                time_str = now.strftime("%H:%M:%S")

                # Converte os 3 primeiros bytes em um inteiro (LSB primeiro)
                integer1 = int.from_bytes(data[:3], byteorder='little')

                # Converte os 2 bytes seguintes em outro inteiro (LSB primeiro)
                integer2 = int.from_bytes(data[3:5], byteorder='little')

                # Converte os 3 últimos bytes em um terceiro inteiro (LSB primeiro)
                integer3 = int.from_bytes(data[5:], byteorder='little')

                # Ignora os dados se integer1, integer2 ou integer3 forem 0
                if integer1 == 0 or integer2 == 0 or integer3 == 0:
                    continue

                # Empilha a tupla (Data, Hora, integer1, integer2, integer3)
                data_stack.append((date_str, time_str, integer1, integer2, integer3))
                print(f"Dados recebidos: ({date_str}, {time_str}, {integer1}, {integer2}, {integer3})")
            else:
                print("Dados incompletos recebidos, ignorando...")
        except Exception as e:
            print(f"Erro durante a leitura: {e}")

        time.sleep(INTERVALO_TEMPO)  # Aguarda INTERVALO_TEMPO segundos antes de coletar novamente

# Configura o tratador de sinal
signal.signal(signal.SIGINT, signal_handler)

# Inicializa a conexão serial
with serial.Serial(port, baud_rate, timeout=timeout) as ser:
    print("Aguardando dados... Pressione Ctrl+C para encerrar.")

    # Inicia a thread para enviar "F" periodicamente
    sender_thread = threading.Thread(target=send_f_command, args=(ser,), daemon=True)
    sender_thread.start()

    # Inicia a thread para coletar dados periodicamente
    reader_thread = threading.Thread(target=read_uart_data, args=(ser,), daemon=True)
    reader_thread.start()

    # Mantém o programa rodando
    while True:
        time.sleep(1)
