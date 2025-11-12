import serial
import threading
import time
import sqlite3
import queue
import tkinter as tk
from tkinter import simpledialog, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
from collections import deque

# --- Configurações ---
SERIAL_PORT = "/dev/serial/by-id/usb-Arduino_LLC_Arduino_NANO_33_IoT_91DB68C651544C3954202020FF0B0D09-if00"
BAUDRATE = 115200
CONTROL_PERIOD_SEC = 5.0
LOG_DATABASE = "aging_test_log.db"
PLOT_WINDOW_SIZE = 100 # Quantos pontos mostrar no gráfico (janela de tempo)

# =================================================================
#   CLASSE DE LOG DE DADOS (Inalterada)
# =================================================================
class DataLogger:
    def __init__(self, db_file):
        self.db_conn = sqlite3.connect(db_file, check_same_thread=False)
        self.lock = threading.Lock()
        self._create_database_table()

    def _create_database_table(self):
        with self.lock:
            cursor = self.db_conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pid_log (
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    setpoint_c REAL,
                    oven_temp_c REAL,
                    pid_output_percent REAL
                )
            """)
            self.db_conn.commit()

    def log_to_db(self, data):
        with self.lock:
            try:
                cursor = self.db_conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO pid_log (setpoint_c, oven_temp_c, pid_output_percent)
                    VALUES (?, ?, ?)
                    """,
                    (data['setpoint_c'], data['oven_temp_c'], data['pid_output_percent'])
                )
                self.db_conn.commit()
            except sqlite3.Error as e:
                print(f"ERRO de Banco de Dados: {e}") # Eventualmente, enviar para a IHM

    def close(self):
        if self.db_conn:
            self.db_conn.close()

# =================================================================
#   CLASSE DE CONTROLE DO FORNO (Modificada para travas)
# =================================================================
class OvenController:
    def __init__(self, port, baudrate, db_logger):
        self.port = port
        self.baudrate = baudrate
        self.db_logger = db_logger
        self.ser = None
        self.log_thread = None
        self.test_running = False
        self.serial_lock = threading.Lock()
        
        # 'latest_data' é a ponte entre o thread de controle e a IHM
        self._latest_data_lock = threading.Lock()
        self._latest_data = {
            'timestamp': time.time(),
            'oven_temp_c': 0.0,
            'setpoint_c': 0.0,
            'pid_output_percent': 0.0
        }
        
        self.message_queue = queue.Queue() # Fila para logs na IHM

        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=2)
            self.message_queue.put(f"Conectado a {self.port}")
        except serial.SerialException as e:
            self.message_queue.put(f"ERRO: Não foi possível abrir a porta {self.port}. {e}")
            raise e

    def get_latest_data(self):
        """Método seguro para a IHM ler os dados mais recentes."""
        with self._latest_data_lock:
            return self._latest_data.copy()

    def send_command(self, cmd):
        with self.serial_lock:
            self.ser.write(f"{cmd}\n".encode('ascii'))
            response = self.ser.readline().decode('ascii').strip()
            return response

    def set_target_setpoint(self, temp):
        self.message_queue.put(f"HOST -> SET_SP,{temp}")
        response = self.send_command(f"SET_SP,{temp}")
        self.message_queue.put(f"ARDUINO -> {response}")

    def start_test(self):
        self.message_queue.put("HOST -> START_TEST")
        response = self.send_command("START_TEST")
        self.message_queue.put(f"ARDUINO -> {response}")
        
        if "OK" in response:
            self.test_running = True
            self.log_thread = threading.Thread(target=self._logging_loop, daemon=True)
            self.log_thread.start()
            self.message_queue.put(">>> Teste iniciado. Log de dados em background ativado.")
        else:
            self.message_queue.put("ERRO: Arduino não iniciou o teste.")

    def stop_test(self):
        self.test_running = False
        self.message_queue.put("HOST -> STOP_TEST")
        response = self.send_command("STOP_TEST")
        self.message_queue.put(f"ARDUINO -> {response}")
        if self.log_thread and self.log_thread.is_alive():
            self.log_thread.join(timeout=CONTROL_PERIOD_SEC + 1)
        self.message_queue.put(">>> Teste parado.")

    def _logging_loop(self):
        self.message_queue.put(f"Thread de log iniciada (intervalo: {CONTROL_PERIOD_SEC}s).")
        
        while self.test_running:
            start_time = time.time()
            try:
                response = self.send_command("GET_DATA")
                
                if response.startswith("DATA,"):
                    parts = response.split(',')
                    data = {
                        'timestamp': time.time(), # Usamos o tempo do PC para o eixo X
                        'oven_temp_c': float(parts[1]),
                        'setpoint_c': float(parts[2]),
                        'pid_output_percent': float(parts[3])
                    }
                    
                    # Atualiza a variável da IHM (thread-safe)
                    with self._latest_data_lock:
                        self._latest_data = data
                    
                    # Loga no banco de dados
                    self.db_logger.log_to_db(data)
                    
                else:
                    self.message_queue.put(f"Resposta inesperada: {response}")

            except Exception as e:
                self.message_queue.put(f"ERRO no loop de log: {e}")
                self.test_running = False

            elapsed = time.time() - start_time
            sleep_time = max(0, CONTROL_PERIOD_SEC - elapsed)
            time.sleep(sleep_time)
            
        self.message_queue.put("Thread de log finalizada.")

    def close(self):
        if self.test_running:
            self.stop_test()
        if self.ser and self.ser.is_open:
            self.ser.close()
            self.message_queue.put("Porta serial fechada.")

# =================================================================
#   CLASSE DA IHM (TKINTER + MATPLOTLIB)
# =================================================================
class App(tk.Tk):
    def __init__(self, controller, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.controller = controller
        
        self.title("Controlador de Forno - TCC")
        self.geometry("800x600")
        
        # Listas de dados para o gráfico (com tamanho máximo)
        self.time_data = deque(maxlen=PLOT_WINDOW_SIZE)
        self.temp_data = deque(maxlen=PLOT_WINDOW_SIZE)
        self.setpoint_data = deque(maxlen=PLOT_WINDOW_SIZE)

        self._create_widgets()
        
        # Inicia a animação do gráfico
        self.ani = animation.FuncAnimation(
            self.fig, 
            self._update_plot, 
            interval=1000, # Atualiza o gráfico a cada 1 segundo
            blit=False
        )
        
        # Inicia um loop para ler a fila de mensagens do controlador
        self._poll_message_queue()

        # Garante que o thread do controlador pare ao fechar a janela
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _create_widgets(self):
        # Frame de Controle (Botões)
        control_frame = tk.Frame(self)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        
        self.start_button = tk.Button(control_frame, text="INICIAR TESTE", command=self._ask_setpoint_and_start, bg="green", fg="white", font
=("Helvetica", 10, "bold"))
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = tk.Button(control_frame, text="PARAR TESTE", command=self._stop_test, bg="red", fg="white", font=("Helvetica", 10, "bold"), state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        # Frame do Gráfico (Matplotlib)
        plot_frame = tk.Frame(self)
        plot_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.fig = Figure(figsize=(8, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Frame de Log (Terminal)
        log_frame = tk.Frame(self)
        log_frame.pack(side=tk.BOTTOM, fill=tk.X, expand=False)
        
        self.log_text = tk.Text(log_frame, height=8, state=tk.DISABLED, bg="black", fg="limegreen")
        self.log_text.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(log_frame, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)

    def _log_message(self, msg):
        """Adiciona uma mensagem na caixa de log da IHM."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {msg}\n")
        self.log_text.see(tk.END) # Auto-scroll
        self.log_text.config(state=tk.DISABLED)

    def _poll_message_queue(self):
        """Verifica a fila de mensagens do controlador."""
        try:
            while True:
                msg = self.controller.message_queue.get_nowait()
                self._log_message(msg)
        except queue.Empty:
            pass # Fila vazia, normal
        
        # Re-agenda a verificação
        self.after(100, self._poll_message_queue)

    def _update_plot(self, frame):
        """Função chamada pela animação para redesenhar o gráfico."""
        if not self.controller.test_running:
            return # Não faz nada se o teste não começou

        # 1. Pega os dados mais recentes do thread do controlador
        data = self.controller.get_latest_data()
        
        # Evita plotar o mesmo dado duas vezes se a animação for mais rápida
        if data['timestamp'] != (self.time_data[-1] if self.time_data else 0):
            # 2. Adiciona dados aos 'deques' (listas de tamanho fixo)
            self.time_data.append(data['timestamp'])
            self.temp_data.append(data['oven_temp_c'])
            self.setpoint_data.append(data['setpoint_c'])

        # 3. Limpa o eixo para redesenhar (cla = Clear Axis)
        self.ax.cla()
        
        # 4. Plota os novos dados
        self.ax.plot(self.time_data, self.temp_data, label="Temp. Forno (°C)", color="blue")
        self.ax.plot(self.time_data, self.setpoint_data, label="Setpoint (°C)", color="red", linestyle="--")
        
        # 5. Formata o gráfico
        self.ax.set_title("Evolução da Temperatura do Forno em Tempo Real")
        self.ax.set_ylabel("Temperatura (°C)")
        
        # Formata o eixo X para mostrar o tempo relativo (em segundos)
        if self.time_data:
            start_time = self.time_data[0]
            x_ticks = [int(t - start_time) for t in self.time_data]
            self.ax.set_xticklabels(x_ticks)
            self.ax.set_xlabel("Tempo (segundos)")
            
        self.ax.legend()
        self.ax.grid(True)
        self.fig.tight_layout()

    def _ask_setpoint_and_start(self):
        """Chamado pelo botão INICIAR."""
        temp = simpledialog.askfloat("Definir Setpoint", "Digite a temperatura alvo (ex: 125.0):",
                                     parent=self, minvalue=20.0, maxvalue=200.0)
        
        if temp is not None:
            self._log_message(f"Definindo temperatura alvo para {temp}°C...")
            # Roda as chamadas de rede em um thread para não travar a IHM
            threading.Thread(target=self.controller.set_target_setpoint, args=(temp,), daemon=True).start()
            time.sleep(0.5) # Pequena pausa
            threading.Thread(target=self.controller.start_test, daemon=True).start()
            
            # Atualiza os botões
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)

    def _stop_test(self):
        """Chamado pelo botão PARAR."""
        if messagebox.askyesno("Parar Teste", "Tem certeza que deseja parar o teste?"):
            self._log_message("Parando o teste...")
            # Roda em um thread para não travar a IHM enquanto espera o 'join'
            threading.Thread(target=self.controller.stop_test, daemon=True).start()
            
            # Atualiza os botões
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            
    def _on_close(self):
        """Chamado ao fechar a janela da IHM."""
        self._log_message("Fechando aplicação... Por favor, aguarde.")
        
        # Roda o fechamento em um thread para a IHM não travar
        def shutdown():
            self.controller.close()
            self.db_logger.close()
            self.destroy() # Fecha a janela
        
        threading.Thread(target=shutdown, daemon=True).start()

# =================================================================
#   FUNÇÃO PRINCIPAL (Inicia a IHM)
# =================================================================
if __name__ == "__main__":
    try:
        db_logger = DataLogger(LOG_DATABASE)
        oven = OvenController(port=SERIAL_PORT, baudrate=BAUDRATE, db_logger=db_logger)
        
        app = App(oven)
        app.mainloop() # Inicia a IHM (loop principal do Tkinter)
        
    except serial.SerialException as e:
        print(f"ERRO FATAL: {e}")
        print("Verifique se o Arduino está conectado na porta correta.")
    except Exception as e:
        print(f"Uma exceção fatal ocorreu: {e}")