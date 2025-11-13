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
#SERIAL_PORT = "/dev/serial/by-id/usb-Arduino_LLC_Arduino_NANO_33_IoT_91DB68C651544C3954202020FF0B0D09-if00"
SERIAL_PORT = "COM27"
BAUDRATE = 115200
CONTROL_PERIOD_SEC = 5.0
LOG_DATABASE = "aging_test_log.db" 
PLOT_WINDOW_SIZE = 100 

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
                print(f"ERRO de Banco de Dados: {e}") 

    def close(self):
        if self.db_conn:
            self.db_conn.close()

# =================================================================
#   CLASSE DE CONTROLE DO FORNO (Inalterada)
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
        
        self._latest_data_lock = threading.Lock()
        self._latest_data = {
            'timestamp': 0.0,
            'oven_temp_c': 0.0,
            'setpoint_c': 0.0,
            'pid_output_percent': 0.0
        }
        
        self.message_queue = queue.Queue() 

        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=2)
            self.message_queue.put(f"Conectado a {self.port}")
        except serial.SerialException as e:
            self.message_queue.put(f"ERRO: Não foi possível abrir a porta {self.port}. {e}")
            raise e

    def get_latest_data(self):
        with self._latest_data_lock:
            return self._latest_data.copy()

    def send_command(self, cmd):
        try:
            with self.serial_lock:
                self.ser.write(f"{cmd}\n".encode('ascii'))
                response = self.ser.readline().decode('ascii').strip()
                return response
        except serial.SerialException as e:
            self.message_queue.put(f"ERRO SERIAL: {e}. O Arduino foi desconectado?")
            self.test_running = False 
            return "ERROR"

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
        if not self.ser.is_open:
             self.message_queue.put(">>> Teste parado (porta serial já fechada).")
             self.test_running = False
             return
             
        self.test_running = False
        self.message_queue.put("HOST -> STOP_TEST")
        response = self.send_command("STOP_TEST")
        self.message_queue.put(f"ARDUINO -> {response}")
        if self.log_thread and self.log_thread.is_alive():
            self.log_thread.join(timeout=CONTROL_PERIOD_SEC + 1)
        self.message_queue.put(">>> Teste parado.")

    def _logging_loop(self):
        self.message_queue.put(f"Thread de log iniciada (intervalo: {CONTROL_PERIOD_SEC}s).")

        time.sleep(1.0) # Tratar o race condition na comunicação
        
        while self.test_running:
            start_time = time.time()
            try:
                response = self.send_command("GET_DATA")
                
                if response.startswith("DATA,"):
                    parts = response.split(',')
                    data = {
                        'timestamp': time.time(), 
                        'oven_temp_c': float(parts[1]),
                        'setpoint_c': float(parts[2]),
                        'pid_output_percent': float(parts[3]) # <--- JÁ ESTÁ SENDO LIDO
                    }
                    
                    with self._latest_data_lock:
                        self._latest_data = data
                    
                    self.db_logger.log_to_db(data)
                    
                elif response == "ERROR":
                    self.message_queue.put("Parando log devido a erro serial.")
                    break 
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
#   CLASSE DA IHM (Modificada com o Label de Saída do SSR)
# =================================================================
class App(tk.Tk):
    def __init__(self, controller, db_logger, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.controller = controller
        self.db_logger = db_logger 
        
        self.title("Controlador de Forno - TCC")
        self.geometry("800x600")
        
        self.start_time = None
        self.last_plotted_time = 0
        self.time_data = deque(maxlen=PLOT_WINDOW_SIZE)
        self.temp_data = deque(maxlen=PLOT_WINDOW_SIZE)
        self.setpoint_data = deque(maxlen=PLOT_WINDOW_SIZE)

        self._create_widgets()
        
        self.ani = animation.FuncAnimation(
            self.fig, 
            self._update_plot, 
            interval=1000, 
            blit=False,
            cache_frame_data=False 
        )
        
        self._poll_message_queue()
        
        # Inicia o loop que atualiza os labels (Saída SSR, etc)
        self._update_status_labels() 
        
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _create_widgets(self):
        # --- Frame de Controle (Botões) ---
        control_frame = tk.Frame(self)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        
        self.start_button = tk.Button(control_frame, text="INICIAR TESTE", command=self._ask_setpoint_and_start, bg="green", fg="white", font
=("Helvetica", 10, "bold"))
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = tk.Button(control_frame, text="PARAR TESTE", command=self._stop_test, bg="red", fg="white", font=("Helvetica", 10, "bold"), state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        # --- NOVO: Frame de Status (Saída SSR) ---
        status_frame = tk.Frame(self)
        status_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        
        # Label para a Saída do SSR
        self.ssr_output_label = tk.Label(status_frame, text="Saída SSR: 0.0 %", font=("Helvetica", 14, "bold"), fg="darkblue")
        self.ssr_output_label.pack(side=tk.LEFT)
        
        # Label para a Temperatura Atual (opcional, mas útil)
        self.temp_label = tk.Label(status_frame, text="Temp. Atual: -- °C", font=("Helvetica", 14), fg="black")
        self.temp_label.pack(side=tk.LEFT, padx=20)

        # --- Frame do Gráfico (Matplotlib) ---
        plot_frame = tk.Frame(self)
        plot_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.fig = Figure(figsize=(8, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        
        self.ax.set_xlabel("Tempo (segundos)")
        self.ax.set_ylabel("Temperatura (°C)")
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # --- Frame de Log (Terminal) ---
        log_frame = tk.Frame(self)
        log_frame.pack(side=tk.BOTTOM, fill=tk.X, expand=False)
        
        self.log_text = tk.Text(log_frame, height=6, state=tk.DISABLED, bg="black", fg="limegreen") # Altura reduzida
        self.log_text.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(log_frame, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)

    def _log_message(self, msg):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {msg}\n")
        self.log_text.see(tk.END) 
        self.log_text.config(state=tk.DISABLED)

    def _poll_message_queue(self):
        try:
            while True:
                msg = self.controller.message_queue.get_nowait()
                self._log_message(msg)
        except queue.Empty:
            pass 
        self.after(100, self._poll_message_queue)

    def _update_status_labels(self):
        """NOVO: Atualiza os labels de status (SSR e Temp)"""
        if self.controller.test_running:
            data = self.controller.get_latest_data()
            
            # Atualiza o Label da Saída do SSR
            ssr_pct = data['pid_output_percent']
            self.ssr_output_label.config(text=f"Saída SSR: {ssr_pct:.1f} %")
            
            # Muda a cor baseado na potência (100% = vermelho, 60% = azul)
            if ssr_pct > 99.0:
                self.ssr_output_label.config(fg="red")
            else:
                self.ssr_output_label.config(fg="darkblue")
                
            # Atualiza o Label de Temperatura Atual
            temp = data['oven_temp_c']
            self.temp_label.config(text=f"Temp. Atual: {temp:.2f} °C")
        
        # Re-agenda a atualização
        self.after(1000, self._update_status_labels) # Atualiza a cada 1 segundo

    def _update_plot(self, frame):
        """Função da animação que redesenha o gráfico."""
        if not self.controller.test_running:
            return 

        data = self.controller.get_latest_data()
        
        if data['timestamp'] > self.last_plotted_time:
            self.last_plotted_time = data['timestamp']
            
            if self.start_time is None:
                self.start_time = data['timestamp']
            
            self.time_data.append(data['timestamp'] - self.start_time)
            self.temp_data.append(data['oven_temp_c'])
            self.setpoint_data.append(data['setpoint_c'])

        self.ax.cla()
        
        self.ax.plot(self.time_data, self.temp_data, label="Temp. Forno (°C)", color="blue")
        self.ax.plot(self.time_data, self.setpoint_data, label="Setpoint (°C)", color="red", linestyle="--")
        
        self.ax.set_title("Evolução da Temperatura do Forno em Tempo Real")
        self.ax.set_ylabel("Temperatura (°C)")
        self.ax.set_xlabel("Tempo (segundos)")
        self.ax.legend()
        self.ax.grid(True)
        self.fig.tight_layout()

    def _ask_setpoint_and_start(self):
        temp = simpledialog.askfloat("Definir Setpoint", "Digite a temperatura alvo (ex: 125.0):",
                                     parent=self, minvalue=20.0, maxvalue=200.0)
        
        if temp is not None:
            self._log_message(f"Definindo temperatura alvo para {temp}°C...")
            threading.Thread(target=self.controller.set_target_setpoint, args=(temp,), daemon=True).start()
            time.sleep(0.5) 
            threading.Thread(target=self.controller.start_test, daemon=True).start()
            
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)

    def _stop_test(self):
        if messagebox.askyesno("Parar Teste", "Tem certeza que deseja parar o teste?"):
            self._log_message("Parando o teste...")
            threading.Thread(target=self.controller.stop_test, daemon=True).start()
            
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            
            # Reseta os labels de status
            self.ssr_output_label.config(text="Saída SSR: 0.0 %", fg="darkblue")
            self.temp_label.config(text="Temp. Atual: -- °C")
            
    def _on_close(self):
        self._log_message("Fechando aplicação... Por favor, aguarde.")
        
        def shutdown():
            self.controller.close()
            self.db_logger.close() 
            self.destroy() 
        
        threading.Thread(target=shutdown, daemon=True).start()

# =================================================================
#   FUNÇÃO PRINCIPAL (Inicia a IHM)
# =================================================================
if __name__ == "__main__":
    try:
        db_logger = DataLogger(LOG_DATABASE)
        oven = OvenController(port=SERIAL_PORT, baudrate=BAUDRATE, db_logger=db_logger)
        
        app = App(oven, db_logger=db_logger) 
        app.mainloop() 
        
    except serial.SerialException as e:
        print(f"ERRO FATAL: {e}")
        print("Verifique se o Arduino está conectado na porta correta.")
    except Exception as e:
        print(f"Uma exceção fatal ocorreu: {e}")