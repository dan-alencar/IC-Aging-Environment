import serial
import time
import csv
import threading

# --- Configurações ---
SERIAL_PORT = "/dev/serial/by-id/usb-Arduino_LLC_Arduino_NANO_33_IoT_40C381DB51544C3954202020FF082015-if00"  # Mude para a sua porta
BAUDRATE = 115200
STEP_DUTY_CYCLE = 50.0  # O degrau de potência (em %) que você aplicará
SAMPLE_INTERVAL = 5     # (segundos) - Com que frequência salvar os dados. 5s é bom.
OUTPUT_FILE = "step_test_data.csv"

# Flag para parar a thread de log
g_run_logging = True

def send_stm_command(ser_handle, cmd):
    """Envia um comando e espera por uma resposta 'OK' ou de dados."""
    print(f"HOST -> STM: {cmd}")
    ser_handle.write(f"{cmd}\n".encode('ascii'))
    
    # Aguarda uma resposta simples. Para GET_DATA, a resposta é tratada no loop.
    if "GET_DATA" not in cmd:
        response = ser_handle.readline().decode('ascii').strip()
        print(f"STM -> HOST: {response}")
        return response
    return None

def logging_thread_func(controller_handle, csv_writer):
    """
    Thread que roda em background, pedindo dados ao STM32
    e salvando no CSV.
    """
    start_time = time.time()
    
    while g_run_logging:
        try:
            # 1. Pede dados
            controller_handle.write(b"GET_DATA\n")
            
            # 2. Lê e processa a resposta
            # Ex: "DATA,25.1,25.0,26.0,0.01,0.0"
            data_line = controller_handle.readline().decode('ascii').strip()
            
            if data_line.startswith("DATA,"):
                parts = data_line.split(',')
                current_time = time.time() - start_time
                oven_temp = float(parts[1])
                
                # 3. Salva no CSV
                csv_writer.writerow([current_time, oven_temp])
                print(f"LOG: Time={current_time:.2f}s, Temp={oven_temp:.2f}°C")
                
            elif "ALERT" in data_line:
                print(f"!!! ALERTA DO STM32: {data_line} !!!")
                
        except Exception as e:
            print(f"Erro na thread de log: {e}")

        # Aguarda o próximo intervalo de amostragem
        time.sleep(SAMPLE_INTERVAL)

# --- Função Principal ---
def run_step_test():
    global g_run_logging
    
    # Abre o arquivo CSV para escrita
    with open(OUTPUT_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Time_sec", "Temperature_C"]) # Escreve o cabeçalho

        try:
            # Conecta ao STM32
            ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=2)
            time.sleep(2) # Espera o STM32 reiniciar
            print(f"Conectado a {SERIAL_PORT}")

            # 1. Parar qualquer teste anterior (garante estado inicial)
            send_stm_command(ser, "STOP_TEST")

            # 2. Inicia a thread de log
            print("Iniciando thread de log...")
            log_thread = threading.Thread(target=logging_thread_func, args=(ser, writer))
            log_thread.start()

            # 3. Aplica o Degrau de Potência
            print("\n!!! TESTE DE DEGRAU INICIADO !!!")
            print(f"Aplicando {STEP_DUTY_CYCLE}% de potência constante.")
            # Assume que você criou o comando 'SET_DUTY' no STM32
            send_stm_command(ser, f"SET_DUTY,{STEP_DUTY_CYCLE}")

            # 4. Aguarda o usuário
            print("\nO teste está rodando e salvando dados em step_test_data.csv")
            print("Observe a temperatura no console.")
            print("Pressione [ENTER] APENAS QUANDO A TEMPERATURA ESTABILIZAR POR COMPLETO.")
            input()

        except serial.SerialException as e:
            print(f"Erro: Não foi possível abrir a porta {SERIAL_PORT}. {e}")
            return
        except KeyboardInterrupt:
            print("\nInterrupção manual...")
        
        finally:
            # 5. Para o teste
            print("Parando o teste e fechando...")
            g_run_logging = False # Sinaliza para a thread parar
            if 'log_thread' in locals() and log_thread.is_alive():
                log_thread.join()
                
            if 'ser' in locals() and ser.is_open:
                send_stm_command(ser, "STOP_TEST")
                ser.close()
            
            print(f"Dados salvos em {OUTPUT_FILE}")

if __name__ == "__main__":
    run_step_test()