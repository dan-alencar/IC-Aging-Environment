from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Slot, Qt
from collections import deque
import pyqtgraph as pg

class PlotWidget(QWidget):
    def __init__(self, parent=None, plot_window_size=100):
        super().__init__(parent)

        self.plot_window_size = plot_window_size

        self.time_data = deque(maxlen=plot_window_size)
        self.temp_oven_data = deque(maxlen=plot_window_size)
        self.temp_setpoint_data = deque(maxlen=plot_window_size)
        self.temp_dut_data = deque(maxlen=plot_window_size)
        self.output_pid_data = deque(maxlen=plot_window_size)

        self.plot_view = pg.PlotWidget()
        self.plot_view.setTitle("Monitoramento Forno e DUT", color='#cdd6f4')
        self.plot_view.setLabel('left', "Temperatura", units="°C", color='#a6adc8')
        self.plot_view.setLabel('bottom', "Tempo", units="s", color='#a6adc8')

        self.ax_left   = self.plot_view.getAxis('left')
        self.ax_bottom = self.plot_view.getAxis('bottom')

        self.legend = self.plot_view.addLegend(
            offset=(10, 10),
            labelTextColor='#cdd6f4',
        )
        self.plot_view.showGrid(x=True, y=True, alpha=0.2)
        self.vb_temp = self.plot_view.getViewBox()

        self.vb_temp.enableAutoRange(axis='y')
        self.vb_temp.disableAutoRange(axis='x')

        # Linhas de temperatura (eixo esquerdo)
        self.oven_curve = self.plot_view.plot(
            pen=pg.mkPen('#89b4fa', width=2),
            name="Temp. Forno (°C)"
        )
        self.setpoint_curve = self.plot_view.plot(
            pen=pg.mkPen('#f38ba8', width=2, style=Qt.DashLine),
            name="Setpoint (°C)"
        )
        self.dut_curve = self.plot_view.plot(
            pen=pg.mkPen('#fab387', width=2, style=Qt.DotLine),
            name="Temp. DUT (°C)"
        )

        # Eixo secundário: Saída PID (eixo direito)
        self.vb_output = pg.ViewBox()
        self.vb_output.setYRange(0, 100, padding=0.05)

        self.output_curve = pg.PlotDataItem(
            pen=pg.mkPen('#a6e3a1', width=2, style=Qt.DashDotLine),
            name="Saída SSR (%)"
        )
        self.vb_output.addItem(self.output_curve)

        self.ax_output = pg.AxisItem('right')
        self.ax_output.setLabel('Saída PID', units='%')
        self.ax_output.linkToView(self.vb_output)
        self.legend.addItem(self.output_curve, name="Saída SSR (%)")

        self.plot_view.getPlotItem().layout.addItem(self.ax_output, 2, 3)
        self.plot_view.getPlotItem().scene().addItem(self.vb_output)

        self.vb_output.linkView(pg.ViewBox.XAxis, self.vb_temp)
        self.vb_temp.sigResized.connect(self._update_output_viewbox_geometry)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.plot_view)

    def _update_output_viewbox_geometry(self):
        self.vb_output.setGeometry(self.vb_temp.sceneBoundingRect())

    @Slot(dict)
    def update_plot_data(self, data_row):
        time_sec = data_row.get('time_sec')

        self.time_data.append(time_sec)
        self.temp_oven_data.append(data_row.get('oven_temp'))
        self.temp_setpoint_data.append(data_row.get('oven_setpoint'))
        self.temp_dut_data.append(data_row.get('dut_temp'))
        self.output_pid_data.append(data_row.get('oven_output'))

        time_list = list(self.time_data)
        self.oven_curve.setData(time_list, list(self.temp_oven_data))
        self.setpoint_curve.setData(time_list, list(self.temp_setpoint_data))
        self.dut_curve.setData(time_list, list(self.temp_dut_data))
        self.output_curve.setData(time_list, list(self.output_pid_data))

        if time_list:
            self.vb_temp.setXRange(time_list[0], time_list[-1], padding=0.01)

        self.vb_temp.autoRange(axis='y')

    @Slot()
    def clear_plot(self):
        self.time_data.clear()
        self.temp_oven_data.clear()
        self.temp_setpoint_data.clear()
        self.temp_dut_data.clear()
        self.output_pid_data.clear()

        self.oven_curve.setData([], [])
        self.setpoint_curve.setData([], [])
        self.dut_curve.setData([], [])
        self.output_curve.setData([], [])

        self.vb_temp.autoRange()
        self.vb_output.autoRange()
