"""
App_2Nexys — Auxiliary voltage/current plot widget.

One instance per DUT panel; receives data dict keys:
  psu_voltage, psu_current, dut_volt    (for DUT-0 panel: psu0_*, dut0_volt)
  OR
  psu_voltage, psu_current, dut_volt    (for DUT-1 panel: psu1_*, dut1_volt)

The parent (main_window.py) wraps update_plot_data to rename keys before
forwarding to each instance, keeping this widget reusable for either DUT.

Curves:
  psu_voltage  — blue solid     (PSU measured readback V)
  psu_cmd_v    — cyan dashed    (PSU command voltage V — what app sent)
  dut_volt     — green dashed   (VCCINT from FPGA XADC)
  psu_current  — red dotted     (PSU measured current A)
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Slot, Qt
from collections import deque
import pyqtgraph as pg


class AuxPlotWidget(QWidget):
    def __init__(self, title: str = "Tensão / Corrente", parent=None, plot_window_size=300):
        super().__init__(parent)

        self.plot_window_size = plot_window_size
        self.time_data = deque(maxlen=plot_window_size)
        self.psu_voltage_data = deque(maxlen=plot_window_size)
        self.psu_cmd_data = deque(maxlen=plot_window_size)
        self.dut_voltage_data = deque(maxlen=plot_window_size)
        self.current_data = deque(maxlen=plot_window_size)

        self.plot_view = pg.PlotWidget()
        self.plot_view.setTitle(title)
        self.plot_view.setLabel("left", "Tensão (V) / Corrente (A)")
        self.plot_view.setLabel("bottom", "Tempo", units="s")
        self.plot_view.showGrid(x=True, y=True, alpha=0.3)

        self.legend = self.plot_view.addLegend()
        self.vb = self.plot_view.getViewBox()
        self.vb.enableAutoRange(axis="y")
        self.vb.disableAutoRange(axis="x")

        self.psu_voltage_curve = self.plot_view.plot(
            pen=pg.mkPen("blue", width=2), name="PSU medido (V)"
        )
        self.psu_cmd_curve = self.plot_view.plot(
            pen=pg.mkPen((0, 200, 200), width=2, style=Qt.DashLine), name="PSU cmd (V)"
        )
        self.dut_voltage_curve = self.plot_view.plot(
            pen=pg.mkPen("green", width=2, style=Qt.DashLine), name="VCCINT (V)"
        )
        self.current_curve = self.plot_view.plot(
            pen=pg.mkPen("red", width=2, style=Qt.DotLine), name="Corrente (A)"
        )

        layout = QVBoxLayout()
        layout.addWidget(self.plot_view)
        self.setLayout(layout)

    @Slot(dict)
    def update_plot_data(self, data_row: dict):
        """data_row must have keys: time_sec, psu_voltage, psu_cmd_v, dut_volt, psu_current."""
        t = data_row.get("time_sec", 0)
        self.time_data.append(t)
        self.psu_voltage_data.append(data_row.get("psu_voltage", 0))
        self.psu_cmd_data.append(data_row.get("psu_cmd_v", 0))
        self.dut_voltage_data.append(data_row.get("dut_volt", 0))
        self.current_data.append(data_row.get("psu_current", 0))

        times = list(self.time_data)
        self.psu_voltage_curve.setData(times, list(self.psu_voltage_data))
        self.psu_cmd_curve.setData(times, list(self.psu_cmd_data))
        self.dut_voltage_curve.setData(times, list(self.dut_voltage_data))
        self.current_curve.setData(times, list(self.current_data))

        if times:
            self.vb.setXRange(times[0], times[-1], padding=0.01)
        self.vb.autoRange()

    @Slot()
    def clear_plot(self):
        self.time_data.clear()
        self.psu_voltage_data.clear()
        self.psu_cmd_data.clear()
        self.dut_voltage_data.clear()
        self.current_data.clear()
        for curve in (self.psu_voltage_curve, self.psu_cmd_curve,
                      self.dut_voltage_curve, self.current_curve):
            curve.setData([], [])
        self.vb.autoRange()
