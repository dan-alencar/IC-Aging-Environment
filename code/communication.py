import serial
import time
import csv
import os

# --- Configuracao ---
SERIAL_PORT = 'COM25'
BAUD_RATE = 38400
OUTPUT_FILE = 'log_serial_tabela.csv'
INTERVALO_SEGUNDOS = 5
HEADER = ['Tempo Decorrido (s)', 'Dado Recebido']
# --------------------

def inicializar_csv():
    if not os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(HEADER)
        print(f"Arquivo '{OUTPUT_FILE}' criado com sucesso.")

ser = None

try:
    inicializar_csv()
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)
    print(f"Conectado à porta {SERIAL_PORT}. Lendo dados a cada {INTERVALO_SEGUNDOS} segundos...")
    
    # MODIFICADO: Impressão do cabeçalho simplificado
    print(f"{HEADER[0]:<20} | {HEADER[1]}")
    print("-" * 40)

    # Marcamos o tempo exato em que o script começou para iniciar a contagem em 0
    start_time = time.time()

    while True:
        ser.write(b'1')
        line_bytes = ser.readline()
        
        # Calculamos o tempo decorrido desde o início
        tempo_decorrido = time.time() - start_time
        tempo_formatado = f"{tempo_decorrido:.2f}"

        if line_bytes:
            dado_recebido = line_bytes.decode('utf-8').strip()

            linha_para_salvar = [tempo_formatado, dado_recebido]

            with open(OUTPUT_FILE, mode='a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(linha_para_salvar)

            # MODIFICADO: Imprimimos a linha simplificada no terminal
            print(f"{tempo_formatado:<20} | {dado_recebido}")
        else:
            # MODIFICADO: Saída simplificada para quando não há dados
            print(f"{tempo_formatado:<20} | Nenhum dado recebido.")
            
        time.sleep(INTERVALO_SEGUNDOS)

except serial.SerialException as e:
    print(f"Erro ao conectar na porta serial: {e}")
except KeyboardInterrupt:
    print("\nPrograma encerrado pelo usuário.")
except Exception as e:
    print(f"Ocorreu um erro inesperado: {e}")
finally:
    if ser and ser.is_open:
        ser.close()
        print(f"Porta serial {SERIAL_PORT} fechada.")