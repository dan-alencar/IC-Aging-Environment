"""
App_2Nexys — Temperature plot widget.

Extends App_Nexys/plot_widget.py with a second DUT curve (DUT-1, purple dotted).
Data dict keys: oven_temp, oven_setpoint, oven_output, dut0_temp, dut1_temp.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Slot, Qt
from collections import deque
import pyqtgraph as pg


class PlotWidget(QWidget):
    def __init__(self, parent=None, plot_window_size=300):
        super().__init__(parent)

        self.plot_window_size = plot_window_size

        self.time_data = deque(maxlen=plot_window_size)
        self.temp_oven_data = deque(maxlen=plot_window_size)
        self.temp_setpoint_data = deque(maxlen=plot_window_size)
        self.temp_dut0_data = deque(maxlen=plot_window_size)
        self.temp_dut1_data = deque(maxlen=plot_window_size)
        self.output_pid_data = deque(maxlen=plot_window_size)

        self.plot_view = pg.PlotWidget()
        self.plot_view.setTitle("Temperatura — Forno e DUTs")
        self.plot_view.setLabel("left", "Temperatura", units="°C")
        self.plot_view.setLabel("bottom", "Tempo", units="s")
        self.plot_view.showGrid(x=True, y=True, alpha=0.3)

        self.legend = self.plot_view.addLegend()
        self.vb_temp = self.plot_view.getViewBox()
        self.vb_temp.enableAutoRange(axis="y")
        self.vb_temp.disableAutoRange(axis="x")

        self.oven_curve = self.plot_view.plot(
            pen=pg.mkPen("blue", width=2), name="Forno (°C)"
        )
        self.setpoint_curve = self.plot_view.plot(
            pen=pg.mkPen("red", width=2, style=Qt.DashLine), name="Setpoint (°C)"
        )
        self.dut0_curve = self.plot_view.plot(
            pen=pg.mkPen("orange", width=2, style=Qt.DotLine), name="DUT-0 (°C)"
        )
        self.dut1_curve = self.plot_view.plot(
            pen=pg.mkPen((160, 32, 240), width=2, style=Qt.DotLine), name="DUT-1 (°C)"
        )

        # Secondary axis: PID output %
        self.vb_output = pg.ViewBox()
        self.vb_output.setYRange(0, 100, padding=0.05)
        self.output_curve = pg.PlotDataItem(
            pen=pg.mkPen("green", width=2, style=Qt.DashDotLine), name="Saída SSR (%)"
        )
        self.vb_output.addItem(self.output_curve)
        self.ax_output = pg.AxisItem("right")
        self.ax_output.setLabel("Saída PID", units="%")
        self.ax_output.linkToView(self.vb_output)
        self.legend.addItem(self.output_curve, name="Saída SSR (%)")
        self.plot_view.getPlotItem().layout.addItem(self.ax_output, 2, 3)
        self.plot_view.getPlotItem().scene().addItem(self.vb_output)
        self.vb_output.linkView(pg.ViewBox.XAxis, self.vb_temp)
        self.vb_temp.sigResized.connect(
            lambda: self.vb_output.setGeometry(self.vb_temp.sceneBoundingRect())
        )

        layout = QVBoxLayout()
        layout.addWidget(self.plot_view)
        self.setLayout(layout)

    @Slot(dict)
    def update_plot_data(self, data_row: dict):
        t = data_row.get("time_sec", 0)
        self.time_data.append(t)
        self.temp_oven_data.append(data_row.get("oven_temp", 0))
        self.temp_setpoint_data.append(data_row.get("oven_setpoint", 0))
        self.temp_dut0_data.append(data_row.get("dut0_temp", 0))
        self.temp_dut1_data.append(data_row.get("dut1_temp", 0))
        self.output_pid_data.append(data_row.get("oven_output", 0))

        times = list(self.time_data)
        self.oven_curve.setData(times, list(self.temp_oven_data))
        self.setpoint_curve.setData(times, list(self.temp_setpoint_data))
        self.dut0_curve.setData(times, list(self.temp_dut0_data))
        self.dut1_curve.setData(times, list(self.temp_dut1_data))
        self.output_curve.setData(times, list(self.output_pid_data))

        if times:
            self.vb_temp.setXRange(times[0], times[-1], padding=0.01)
        self.vb_temp.autoRange()

    @Slot()
    def clear_plot(self):
        self.time_data.clear()
        self.temp_oven_data.clear()
        self.temp_setpoint_data.clear()
        self.temp_dut0_data.clear()
        self.temp_dut1_data.clear()
        self.output_pid_data.clear()
        for curve in (self.oven_curve, self.setpoint_curve,
                      self.dut0_curve, self.dut1_curve, self.output_curve):
            curve.setData([], [])
        self.vb_temp.autoRange()
        self.vb_output.autoRange()
