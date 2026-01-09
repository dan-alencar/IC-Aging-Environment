"""
Widget de Gráfico em Tempo Real (pyqtgraph + PySide6)

Substitui a versão Matplotlib por pyqtgraph para alta performance,
mantendo a mesma lógica de slots e exibição de dados.

ATUALIZADO: Revertido para o tema padrão (escuro/cinza) do pyqtgraph,
removendo as fontes brancas e grandes para um visual coeso.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Slot, Qt
from PySide6.QtGui import QFont # Importa QFont para estilização
from collections import deque
import pyqtgraph as pg

class PlotWidget(QWidget):
    def __init__(self, parent=None, plot_window_size=100):
        super().__init__(parent)
        
        # --- Configuração dos Dados ---
        self.plot_window_size = plot_window_size
        
        self.time_data = deque(maxlen=plot_window_size)
        self.temp_oven_data = deque(maxlen=plot_window_size)
        self.temp_setpoint_data = deque(maxlen=plot_window_size)
        self.temp_dut_data = deque(maxlen=plot_window_size)
        self.output_pid_data = deque(maxlen=plot_window_size)

        # --- Configuração do Gráfico pyqtgraph ---
        # Removemos todos os estilos (fontes, cores) para usar o padrão do pyqtgraph
        self.plot_view = pg.PlotWidget() 
        
        # Configurar Título (padrão)
        self.plot_view.setTitle("Monitoramento Forno e DUT")

        # Configuração do Eixo Principal (Temperatura)
        self.plot_view.setLabel('left', "Temperatura", units="°C")
        self.plot_view.setLabel('bottom', "Tempo", units="s")
        
        # Obter eixos (sem estilização)
        self.ax_left = self.plot_view.getAxis('left')
        self.ax_bottom = self.plot_view.getAxis('bottom')

        self.legend = self.plot_view.addLegend()
        self.plot_view.showGrid(x=True, y=True, alpha=0.3)
        self.vb_temp = self.plot_view.getViewBox() # ViewBox principal
        
        # --- CONFIGURAÇÃO DE AUTO-RANGE ---
        self.vb_temp.enableAutoRange(axis='y')
        self.vb_temp.disableAutoRange(axis='x')
        # --- FIM DA CONFIGURAÇÃO ---

        # --- Criação das Linhas de Temperatura (Eixo Esquerdo) ---
        self.oven_curve = self.plot_view.plot(
            pen=pg.mkPen('blue', width=2), 
            name="Temp. Forno (°C)"
        )
        self.setpoint_curve = self.plot_view.plot(
            pen=pg.mkPen('red', width=2, style=Qt.DashLine), 
            name="Setpoint (°C)"
        )
        self.dut_curve = self.plot_view.plot(
            pen=pg.mkPen('orange', width=2, style=Qt.DotLine), 
            name="Temp. DUT (°C)"
        )

        # --- Configuração do Eixo Secundário (Saída PID - Eixo Direito) ---
        self.vb_output = pg.ViewBox()
        self.vb_output.setYRange(0, 100, padding=0.05) 

        self.output_curve = pg.PlotDataItem(
            pen=pg.mkPen('green', width=2, style=Qt.DashDotLine), 
            name="Saída SSR (%)"
        )
        self.vb_output.addItem(self.output_curve) 

        self.ax_output = pg.AxisItem('right')
        self.ax_output.setLabel('Saída PID', units='%') # Rótulo padrão
        self.ax_output.linkToView(self.vb_output) 
        self.legend.addItem(self.output_curve, name="Saída SSR (%)")
        
        self.plot_view.getPlotItem().layout.addItem(self.ax_output, 2, 3)
        self.plot_view.getPlotItem().scene().addItem(self.vb_output)
        
        self.vb_output.linkView(pg.ViewBox.XAxis, self.vb_temp)
        self.vb_temp.sigResized.connect(self._update_output_viewbox_geometry)

        # --- Layout do Widget ---
        layout = QVBoxLayout()
        layout.addWidget(self.plot_view)
        self.setLayout(layout)

    def _update_output_viewbox_geometry(self):
        """Garante que o ViewBox secundário (saída) se alinhe com o principal."""
        self.vb_output.setGeometry(self.vb_temp.sceneBoundingRect())

    @Slot(dict)
    def update_plot_data(self, data_row):
        """
        Slot para receber novos dados e atualizar o gráfico de forma eficiente.
        (Otimizado para pyqtgraph)
        """
        
        # 1. Adiciona dados aos deques
        time_sec = data_row.get('time_sec')
        
        self.time_data.append(time_sec)
        self.temp_oven_data.append(data_row.get('oven_temp'))
        print(data_row.get('oven_temp'))
        self.temp_setpoint_data.append(data_row.get('oven_setpoint'))
        self.temp_dut_data.append(data_row.get('dut_temp'))
        self.output_pid_data.append(data_row.get('oven_output')) 
        
        # 2. Atualiza as curvas com os novos dados
        time_list = list(self.time_data) # Converte para lista uma vez
        self.oven_curve.setData(time_list, list(self.temp_oven_data))
        self.setpoint_curve.setData(time_list, list(self.temp_setpoint_data))
        self.dut_curve.setData(time_list, list(self.temp_dut_data))
        self.output_curve.setData(time_list, list(self.output_pid_data))

        # --- ATUALIZAÇÃO DO EIXO X (Auto-Scroll) ---
        if time_list:
            self.vb_temp.setXRange(time_list[0], time_list[-1], padding=0.01)
        
        self.vb_temp.autoRange()

    @Slot()
    def clear_plot(self):
        """Limpa o gráfico para um novo teste."""
        
        # 1. Limpa os buffers de dados
        self.time_data.clear()
        self.temp_oven_data.clear()
        self.temp_setpoint_data.clear()
        self.temp_dut_data.clear()
        self.output_pid_data.clear()
        
        # 2. Limpa as curvas no gráfico
        self.oven_curve.setData([], [])
        self.setpoint_curve.setData([], [])
        self.dut_curve.setData([], [])
        self.output_curve.setData([], [])
        
        # 3. Reseta o zoom/pan
        self.vb_temp.autoRange()
        self.vb_output.autoRange()