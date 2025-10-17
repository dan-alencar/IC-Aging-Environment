import serial
import time
import csv
import os
import threading
import queue

# --- Configuração ---
SERIAL_PORT = 'COM25' # Altere para a porta serial correta
BAUD_RATE = 38400
OUTPUT_FILE = 'log_serial_tabela.csv'
INTERVALO_SEGUNDOS = 5 # Intervalo para o ENVIO (escrita periódica)
HEADER = ['Tempo Decorrido (s)', 'Dado Recebido']
# O comando a ser enviado para o dispositivo (Um único byte '1' para disparar a interrupção de leitura no STM32)
COMANDO_ENVIO = b'1' 
# --------------------

# Fila thread-safe para armazenar os dados lidos
dados_queue = queue.Queue()

def inicializar_csv():
    """Cria o arquivo CSV e escreve o cabeçalho, se o arquivo não existir."""
    if not os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(HEADER)
        print(f"Arquivo '{OUTPUT_FILE}' criado com sucesso.")

class SerialWriterThread(threading.Thread):
    """
    Thread responsável pelo envio periódico de comandos para a porta serial.
    """
    def __init__(self, serial_instance, interval, stop_event):
        super().__init__()
        self.ser = serial_instance
        self.interval = interval
        self.stop_event = stop_event
        print("Thread de Escrita Serial (Writer) inicializada para envio periódico.")

    def run(self):
        """Loop principal da thread: envia o comando a cada intervalo."""
        while not self.stop_event.is_set():
            try:
                # Envio do comando (Escrita contínua/periódica)
                # Este comando dispara a interrupção de leitura no STM32
                self.ser.write(COMANDO_ENVIO)
                
                # Aguarda o intervalo antes do próximo envio
                # Usamos wait para permitir interrupção limpa
                self.stop_event.wait(self.interval)

            except serial.SerialException as e:
                print(f"[ERRO WRITER THREAD] Falha de comunicação: {e}")
                self.stop_event.set() 
                break
            except Exception as e:
                print(f"[ERRO INESPERADO WRITER] {e}")
                self.stop_event.set()
                break

class SerialReaderThread(threading.Thread):
    """
    Thread responsável pela leitura constante da porta serial.
    A leitura é limitada apenas pelo timeout e pela velocidade da porta.
    """
    def __init__(self, serial_instance, data_queue, stop_event, start_time):
        super().__init__()
        self.ser = serial_instance
        self.data_queue = data_queue
        self.stop_event = stop_event
        self.start_time = start_time
        print("Thread de Leitura Serial (Reader) inicializada para leitura constante.")

    def run(self):
        """Loop principal da thread: lê a linha e enfileira o dado."""
        while not self.stop_event.is_set():
            try:
                # Tenta ler uma linha. O timeout (definido em ser.Serial) 
                # garante que a thread não bloqueie indefinidamente.
                line_bytes = self.ser.readline()
                
                if line_bytes:
                    # Cálculo do tempo é feito imediatamente após a leitura
                    tempo_decorrido = time.time() - self.start_time
                    
                    # Coloca o dado na fila para ser processado pela thread principal
                    self.data_queue.put((tempo_decorrido, line_bytes))
                
                # Pequena pausa para evitar 100% de uso da CPU se o timeout for 0
                time.sleep(0.01)

            except serial.SerialException as e:
                print(f"[ERRO READER THREAD] Falha de comunicação: {e}")
                self.stop_event.set()
                break
            except Exception as e:
                print(f"[ERRO INESPERADO READER] {e}")
                self.stop_event.set()
                break

def processar_e_logar_dados(tempo_decorrido, line_bytes):
    """Processa a linha lida, salva no CSV e imprime no console."""
    tempo_formatado = f"{tempo_decorrido:.2f}"
    
    if line_bytes:
        try:
            # Assume que o STM32 envia dados formatados (ex: "25.50\r\n")
            dado_recebido = line_bytes.decode('utf-8').strip()
            linha_para_salvar = [tempo_formatado, dado_recebido]

            with open(OUTPUT_FILE, mode='a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(linha_para_salvar)

            print(f"{tempo_formatado:<20} | {dado_recebido}")
        except UnicodeDecodeError:
            dado_recebido = f"ERRO DE DECODIFICAÇÃO: {line_bytes}"
            print(f"{tempo_formatado:<20} | {dado_recebido}")
            # Ainda salvamos, mas com a indicação de erro para rastreamento
            linha_para_salvar = [tempo_formatado, dado_recebido]
            with open(OUTPUT_FILE, mode='a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(linha_para_salvar)

    else:
        # Se line_bytes estiver vazio, a leitura por readline() deu timeout.
        # Isso é esperado se o STM32 não responder exatamente no momento do polling.
        pass


# --- Lógica Principal (Main Thread) ---

ser = None
writer_thread = None
reader_thread = None
stop_event = threading.Event()

try:
    inicializar_csv()
    
    # 1. Inicializa a porta serial
    # O timeout aqui é crucial para a Thread de Leitura: 
    # ela espera no máximo 1 segundo por linha antes de verificar o stop_event.
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) 
    print(f"Conectado à porta {SERIAL_PORT} (Baud Rate: {BAUD_RATE}).")
    
    # 2. Inicializa o tempo de início
    start_time = time.time()
    
    # Impressão do cabeçalho
    print(f"\n--- INÍCIO DA LEITURA E LOGGING ---\n")
    print(f"Intervalo de ENVIO (Escrita/Requisição): {INTERVALO_SEGUNDOS} segundos.")
    print(f"{HEADER[0]:<20} | {HEADER[1]}")
    print("-" * 40)
    
    # 3. Cria e inicia as Threads
    # Thread 1: Escrita Periódica (Envia '1' a cada 5s)
    writer_thread = SerialWriterThread(ser, INTERVALO_SEGUNDOS, stop_event)
    writer_thread.start()

    # Thread 2: Leitura Constante (Aguarda resposta do STM32)
    reader_thread = SerialReaderThread(ser, dados_queue, stop_event, start_time)
    reader_thread.start()
    
    # 4. Loop de Processamento na Thread Principal (Consome a Fila)
    while not stop_event.is_set():
        try:
            # Espera por dados na fila. Timeout garante que podemos verificar stop_event
            tempo_decorrido, line_bytes = dados_queue.get(timeout=0.1) 
            processar_e_logar_dados(tempo_decorrido, line_bytes)
            dados_queue.task_done()
        
        except queue.Empty:
            # Não há dados, verifica novamente a condição de parada
            continue
        
        except Exception as e:
            print(f"[ERRO MAIN THREAD] Falha no processamento de dados: {e}")
            stop_event.set()

except serial.SerialException as e:
    print(f"\nErro ao conectar na porta serial {SERIAL_PORT}: {e}")
    stop_event.set()
    
except KeyboardInterrupt:
    print("\nPrograma encerrado pelo usuário (Ctrl+C).")
    stop_event.set()
    
finally:
    # 5. Garante que as threads sejam interrompidas e a porta fechada
    print("\nIniciando procedimento de encerramento...")
    stop_event.set()
    
    if writer_thread and writer_thread.is_alive():
        writer_thread.join()
        print("Thread de Escrita parada.")
        
    if reader_thread and reader_thread.is_alive():
        reader_thread.join()
        print("Thread de Leitura parada.")

    if ser and ser.is_open:
        ser.close()
        print(f"Porta serial {SERIAL_PORT} fechada.")
        
    print("Fim do programa.")
