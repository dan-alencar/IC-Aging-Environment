"""
Widget de Gráfico Auxiliar (pyqtgraph + PySide6)
Exibe dados de Tensão e Corrente da Fonte.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Slot, Qt
from collections import deque
import pyqtgraph as pg

class AuxPlotWidget(QWidget):
    def __init__(self, parent=None, plot_window_size=100):
        super().__init__(parent)
        
        # --- Configuração dos Dados ---
        self.plot_window_size = plot_window_size
        
        self.time_data = deque(maxlen=plot_window_size)
        self.dut_voltage_data = deque(maxlen=plot_window_size)
        self.voltage_data = deque(maxlen=plot_window_size)
        self.current_data = deque(maxlen=plot_window_size)

        # --- Configuração do Gráfico pyqtgraph ---
        self.plot_view = pg.PlotWidget() 
        self.plot_view.setTitle("Tensão e Corrente da PSU e FPGA")

        # Configuração do Eixo Principal (Tensão e Corrente)
        self.plot_view.setLabel('left', "Tensão (V) / Corrente (A)")
        self.plot_view.setLabel('bottom', "Tempo", units="s")
        
        self.legend = self.plot_view.addLegend()
        self.plot_view.showGrid(x=True, y=True, alpha=0.3)
        self.vb_main = self.plot_view.getViewBox()
        
        # --- CONFIGURAÇÃO DE AUTO-RANGE ---
        self.vb_main.enableAutoRange(axis='y')
        self.vb_main.disableAutoRange(axis='x')
        # --- FIM DA CONFIGURAÇÃO ---

        # --- Criação das Linhas (Eixo Esquerdo: V / A) ---
        self.dut_voltage_curve = self.plot_view.plot(
            pen=pg.mkPen('green', width=2, style=Qt.DashLine), 
            name="Tensão DUT (V)"
        )
        self.voltage_curve = self.plot_view.plot(
            pen=pg.mkPen('blue', width=2), 
            name="Tensão PSU (V)"
        )
        self.current_curve = self.plot_view.plot(
            pen=pg.mkPen('red', width=2, style=Qt.DotLine), 
            name="Corrente PSU (A)"
        )
        
        # --- Layout do Widget ---
        layout = QVBoxLayout()
        layout.addWidget(self.plot_view)
        self.setLayout(layout)

    @Slot(dict)
    def update_plot_data(self, data_row):
        """
        Slot para receber novos dados e atualizar o gráfico de forma eficiente.
        """
        
        # 1. Adiciona dados aos deques
        time_sec = data_row.get('time_sec')
        
        self.time_data.append(time_sec)
        self.dut_voltage_data.append(data_row.get('dut_volt'))
        self.voltage_data.append(data_row.get('psu_voltage'))
        self.current_data.append(data_row.get('psu_current'))

        
        # 2. Atualiza as curvas com os novos dados
        time_list = list(self.time_data) 
        self.dut_voltage_curve.setData(time_list, list(self.dut_voltage_data))
        self.voltage_curve.setData(time_list, list(self.voltage_data))
        self.current_curve.setData(time_list, list(self.current_data))

        # --- ATUALIZAÇÃO DO EIXO X (Auto-Scroll) ---
        if time_list:
            self.vb_main.setXRange(time_list[0], time_list[-1], padding=0.01)
        
        self.vb_main.autoRange()

    @Slot()
    def clear_plot(self):
        """Limpa o gráfico para um novo teste."""
        
        # 1. Limpa os buffers de dados
        self.time_data.clear()
        self.dut_voltage_data.clear()
        self.voltage_data.clear()
        self.current_data.clear()
        
        # 2. Limpa as curvas no gráfico
        self.dut_voltage_curve.setData([], [])
        self.voltage_curve.setData([], [])
        self.current_curve.setData([], [])
        
        # 3. Reseta o zoom/pan
        self.vb_main.autoRange()