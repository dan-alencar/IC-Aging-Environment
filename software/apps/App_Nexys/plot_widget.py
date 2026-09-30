from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Slot, Qt
from collections import deque
import pyqtgraph as pg

pg.setConfigOptions(antialias=True, background='#1e1e2e', foreground='#cdd6f4')

_C_OVEN   = '#89b4fa'   # blue   — oven temp
_C_SP     = '#f38ba8'   # pink   — setpoint (dashed)
_C_DUT    = '#fab387'   # orange — DUT temp (dotted)
_C_OUTPUT = '#a6e3a1'   # green  — SSR output % (right axis)


class PlotWidget(QWidget):
    def __init__(self, parent=None, plot_window_size=100):
        super().__init__(parent)
        self.plot_window_size = plot_window_size

        self.time_data          = deque(maxlen=plot_window_size)
        self.temp_oven_data     = deque(maxlen=plot_window_size)
        self.temp_setpoint_data = deque(maxlen=plot_window_size)
        self.temp_dut_data      = deque(maxlen=plot_window_size)
        self.output_pid_data    = deque(maxlen=plot_window_size)

        self.plot_view = pg.PlotWidget()
        self.plot_view.setTitle("Temperatura — Forno e DUT", color='#cdd6f4', size='11pt')
        self.plot_view.setLabel('left',   "Temperatura (°C)", color='#cdd6f4')
        self.plot_view.setLabel('bottom', "Tempo (s)",         color='#cdd6f4')
        self.plot_view.showGrid(x=True, y=True, alpha=0.15)

        self.legend = self.plot_view.addLegend(
            offset=(10, 10),
            labelTextColor='#cdd6f4',
        )
        self.vb_temp = self.plot_view.getViewBox()
        self.vb_temp.enableAutoRange(axis='y')
        self.vb_temp.disableAutoRange(axis='x')

        self.oven_curve = self.plot_view.plot(
            pen=pg.mkPen(_C_OVEN, width=2),
            name="Forno (°C)"
        )
        self.setpoint_curve = self.plot_view.plot(
            pen=pg.mkPen(_C_SP, width=2, style=Qt.DashLine),
            name="Setpoint (°C)"
        )
        self.dut_curve = self.plot_view.plot(
            pen=pg.mkPen(_C_DUT, width=2, style=Qt.DotLine),
            name="DUT (°C)"
        )

        # Right axis — SSR output %
        self.vb_output = pg.ViewBox()
        self.vb_output.setYRange(0, 100, padding=0.05)

        self.output_curve = pg.PlotDataItem(
            pen=pg.mkPen(_C_OUTPUT, width=1.5, style=Qt.DashDotLine),
            name="SSR Output (%)"
        )
        self.vb_output.addItem(self.output_curve)

        self.ax_output = pg.AxisItem('right')
        self.ax_output.setLabel('SSR Output (%)', color='#cdd6f4')
        self.ax_output.linkToView(self.vb_output)
        self.legend.addItem(self.output_curve, name="SSR Output (%)")

        self.plot_view.getPlotItem().layout.addItem(self.ax_output, 2, 3)
        self.plot_view.getPlotItem().scene().addItem(self.vb_output)
        self.vb_output.linkView(pg.ViewBox.XAxis, self.vb_temp)
        self.vb_temp.sigResized.connect(self._sync_output_viewbox)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.plot_view)
        self.setLayout(layout)

    def _sync_output_viewbox(self):
        self.vb_output.setGeometry(self.vb_temp.sceneBoundingRect())

    @Slot(dict)
    def update_plot_data(self, data_row):
        self.time_data.append(data_row.get('time_sec', 0.0))
        self.temp_oven_data.append(data_row.get('oven_temp', 0.0))
        self.temp_setpoint_data.append(data_row.get('oven_setpoint', 0.0))
        self.temp_dut_data.append(data_row.get('dut_temp', 0.0))
        self.output_pid_data.append(data_row.get('oven_output', 0.0))

        time_list = list(self.time_data)
        self.oven_curve.setData(time_list, list(self.temp_oven_data))
        self.setpoint_curve.setData(time_list, list(self.temp_setpoint_data))
        self.dut_curve.setData(time_list, list(self.temp_dut_data))
        self.output_curve.setData(time_list, list(self.output_pid_data))

        if len(time_list) > 1:
            self.vb_temp.setXRange(time_list[0], time_list[-1], padding=0.02)

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
