from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Slot, Qt
from collections import deque
import pyqtgraph as pg

pg.setConfigOptions(antialias=True, background='#1e1e2e', foreground='#cdd6f4')

_C_DUT_V = '#a6e3a1'   # green  — DUT VCCINT measured
_C_CMD_V = '#cba6f7'   # purple — PSU command voltage (dotted)
_C_PSU_V = '#89b4fa'   # blue   — PSU measured voltage
_C_CURR  = '#f38ba8'   # pink   — PSU current (dashed)


class AuxPlotWidget(QWidget):
    def __init__(self, parent=None, plot_window_size=100):
        super().__init__(parent)
        self.plot_window_size = plot_window_size

        self.time_data        = deque(maxlen=plot_window_size)
        self.dut_voltage_data = deque(maxlen=plot_window_size)
        self.cmd_voltage_data = deque(maxlen=plot_window_size)
        self.voltage_data     = deque(maxlen=plot_window_size)
        self.current_data     = deque(maxlen=plot_window_size)

        self.plot_view = pg.PlotWidget()
        self.plot_view.setTitle("Tensão e Corrente — PSU e FPGA", color='#cdd6f4', size='11pt')
        self.plot_view.setLabel('left',   "Tensão (V) / Corrente (A)", color='#cdd6f4')
        self.plot_view.setLabel('bottom', "Tempo (s)",                  color='#cdd6f4')
        self.plot_view.showGrid(x=True, y=True, alpha=0.15)

        self.legend = self.plot_view.addLegend(
            offset=(10, 10),
            labelTextColor='#cdd6f4',
        )
        self.vb_main = self.plot_view.getViewBox()
        self.vb_main.enableAutoRange(axis='y')
        self.vb_main.disableAutoRange(axis='x')

        self.dut_voltage_curve = self.plot_view.plot(
            pen=pg.mkPen(_C_DUT_V, width=2, style=Qt.DashLine),
            name="VCCINT DUT (V)"
        )
        self.cmd_voltage_curve = self.plot_view.plot(
            pen=pg.mkPen(_C_CMD_V, width=1.5, style=Qt.DotLine),
            name="PSU Cmd (V)"
        )
        self.voltage_curve = self.plot_view.plot(
            pen=pg.mkPen(_C_PSU_V, width=2),
            name="PSU Medida (V)"
        )
        self.current_curve = self.plot_view.plot(
            pen=pg.mkPen(_C_CURR, width=2, style=Qt.DashLine),
            name="Corrente (A)"
        )

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.plot_view)
        self.setLayout(layout)

    @Slot(dict)
    def update_plot_data(self, data_row):
        self.time_data.append(data_row.get('time_sec', 0.0))
        self.dut_voltage_data.append(data_row.get('dut_volt', 0.0))
        self.cmd_voltage_data.append(data_row.get('psu_cmd_v', 0.0))
        self.voltage_data.append(data_row.get('psu_voltage', 0.0))
        self.current_data.append(data_row.get('psu_current', 0.0))

        time_list = list(self.time_data)
        self.dut_voltage_curve.setData(time_list, list(self.dut_voltage_data))
        self.cmd_voltage_curve.setData(time_list, list(self.cmd_voltage_data))
        self.voltage_curve.setData(time_list, list(self.voltage_data))
        self.current_curve.setData(time_list, list(self.current_data))

        if len(time_list) > 1:
            self.vb_main.setXRange(time_list[0], time_list[-1], padding=0.02)

    @Slot()
    def clear_plot(self):
        self.time_data.clear()
        self.dut_voltage_data.clear()
        self.cmd_voltage_data.clear()
        self.voltage_data.clear()
        self.current_data.clear()

        self.dut_voltage_curve.setData([], [])
        self.cmd_voltage_curve.setData([], [])
        self.voltage_curve.setData([], [])
        self.current_curve.setData([], [])

        self.vb_main.autoRange()
