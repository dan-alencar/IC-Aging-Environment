"""
Widget de Gráfico em Tempo Real (Matplotlib + PySide6)
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from collections import deque
import time

class PlotWidget(QWidget):
    def __init__(self, parent=None, plot_window_size=100):
        super().__init__(parent)
        
        # --- Configuração dos Dados ---
        self.plot_window_size = plot_window_size
        self.start_time = None
        self.last_plotted_time = 0
        
        # Deques para os dados do gráfico (listas com tamanho máximo)
        self.time_data = deque(maxlen=plot_window_size)
        self.temp_oven_data = deque(maxlen=plot_window_size)
        self.temp_setpoint_data = deque(maxlen=plot_window_size)
        self.temp_dut_data = deque(maxlen=plot_window_size)

        # --- Configuração do Gráfico Matplotlib ---
        self.figure = Figure(figsize=(8, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        
        # Criação dos subplots (eixos)
        self.ax_temp = self.figure.add_subplot(111)
        self.ax_output = self.ax_temp.twinx() # Eixo Y secundário para a Saída
        
        self.figure.tight_layout()

        # --- Layout do Widget ---
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        
        self._configure_initial_plot()

    def _configure_initial_plot(self):
        """Configura a aparência inicial do gráfico."""
        self.ax_temp.set_title("Monitoramento em Tempo Real")
        self.ax_temp.set_xlabel("Tempo (segundos)")
        self.ax_temp.set_ylabel("Temperatura (°C)", color="blue")
        self.ax_output.set_ylabel("Saída PID (%)", color="green")
        self.ax_temp.grid(True)
        self.ax_temp.legend(loc='upper left')
        self.ax_output.legend(loc='upper right')

    def update_plot_data(self, data_row):
        """Slot para receber novos dados do TestSequencer."""
        
        # Pega os dados mais recentes
        data = data_row.copy()
        
        # Evita plotar o mesmo dado duas vezes
        if data['timestamp'] > self.last_plotted_time:
            self.last_plotted_time = data['timestamp']
            
            if self.start_time is None:
                self.start_time = data['timestamp']
            
            # Armazena o tempo RELATIVO
            time_sec = data['timestamp'] - self.start_time
            self.time_data.append(time_sec)
            
            # Adiciona dados de temperatura
            self.temp_oven_data.append(data.get('oven_temp', 0))
            self.temp_setpoint_data.append(data.get('oven_setpoint', 0))
            self.temp_dut_data.append(data.get('dut_temp', 0))
            
            # --- Redesenha o Gráfico ---
            self.ax_temp.cla()
            self.ax_output.cla()
            
            # Plota Temperaturas (Eixo Y Esquerdo)
            self.ax_temp.plot(self.time_data, self.temp_oven_data, label="Temp. Forno (°C)", color="blue")
            self.ax_temp.plot(self.time_data, self.temp_setpoint_data, label="Setpoint Forno (°C)", color="red", linestyle="--")
            self.ax_temp.plot(self.time_data, self.temp_dut_data, label="Temp. DUT (°C)", color="orange", linestyle=":")
            
            # Plota Saída PID (Eixo Y Direito)
            output_data = deque([d.get('oven_output', 0) for d in [data_row]], maxlen=self.plot_window_size) # Recria dados de saída
            self.ax_output.plot(self.time_data, data.get('oven_output_history', self.time_data), label="Saída SSR (%)", color="green", linestyle="-.", alpha=0.7) # Simulação, idealmente o 'data_row' teria o histórico
            self.ax_output.set_ylim(-5, 105) # Trava o eixo de 0-100%

            # Reconfigura legendas e eixos
            self._configure_initial_plot()
            
            # Desenha no canvas
            self.canvas.draw()
            
    def clear_plot(self):
        """Limpa o gráfico para um novo teste."""
        self.start_time = None
        self.last_plotted_time = 0
        self.time_data.clear()
        self.temp_oven_data.clear()
        self.temp_setpoint_data.clear()
        self.temp_dut_data.clear()
        
        self.ax_temp.cla()
        self.ax_output.cla()
        self._configure_initial_plot()
        self.canvas.draw()