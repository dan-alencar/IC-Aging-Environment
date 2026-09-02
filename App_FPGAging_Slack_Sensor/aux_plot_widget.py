from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Slot, Qt
from collections import deque
import pyqtgraph as pg


class AuxPlotWidget(QWidget):
    def __init__(self, parent=None, plot_window_size=100):
        super().__init__(parent)

        self.plot_window_size = plot_window_size
        self.time_data        = deque(maxlen=plot_window_size)
        self.dut_voltage_data = deque(maxlen=plot_window_size)
        self.voltage_data     = deque(maxlen=plot_window_size)
        self.current_data     = deque(maxlen=plot_window_size)

        self.plot_view = pg.PlotWidget()
        self.plot_view.setTitle("PSU, FPGA Voltage & Aging Slack", color='#cdd6f4')
        self.plot_view.setLabel('left', "Tensão (V) / Corrente (A)", color='#a6adc8')
        self.plot_view.setLabel('bottom', "Tempo", units="s", color='#a6adc8')

        self.legend = self.plot_view.addLegend(
            offset=(10, 10),
            labelTextColor='#cdd6f4',
        )
        self.plot_view.showGrid(x=True, y=True, alpha=0.2)

        self.vb_main = self.plot_view.getViewBox()
        self.vb_main.enableAutoRange(axis='y')
        self.vb_main.disableAutoRange(axis='x')

        self.dut_voltage_curve = self.plot_view.plot(
            pen=pg.mkPen('#a6e3a1', width=2, style=Qt.DashLine),
            name="VCCINT DUT (V)"
        )
        self.voltage_curve = self.plot_view.plot(
            pen=pg.mkPen('#89b4fa', width=2),
            name="Tensão PSU (V)"
        )
        self.current_curve = self.plot_view.plot(
            pen=pg.mkPen('#f38ba8', width=2, style=Qt.DotLine),
            name="Corrente PSU (A)"
        )

        # Slack displayed as a TextItem in the top-right corner
        self.slack_text = pg.TextItem(
            text="Slack: --",
            color='#cba6f7',
            anchor=(1.0, 0.0),
        )
        font = pg.QtGui.QFont('Monospace', 11)
        font.setBold(True)
        self.slack_text.setFont(font)
        self.plot_view.addItem(self.slack_text, ignoreBounds=True)

        self.vb_main.sigResized.connect(self._reposition_slack_text)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.plot_view)

    def _reposition_slack_text(self):
        vr = self.vb_main.viewRange()
        self.slack_text.setPos(vr[0][1], vr[1][1])

    @Slot(dict)
    def update_plot_data(self, data_row):
        time_sec = data_row.get('time_sec', 0.0)
        self.time_data.append(time_sec)
        self.dut_voltage_data.append(data_row.get('dut_volt', 0.0))
        self.voltage_data.append(data_row.get('psu_voltage', 0.0))
        self.current_data.append(data_row.get('psu_current', 0.0))

        # dut_slack is now per-channel (dut_slack_ch0..chN-1) -- show the
        # worst-case (minimum) channel here, same convention as the top-bar
        # label in main_window.py. See panel_multi (Multi-Sensor tab) for
        # the full per-channel breakdown.
        slacks = [v for k, v in data_row.items() if k.startswith('dut_slack_ch')]
        slack = min(slacks) if slacks else 0
        self.slack_text.setText(f"Slack (pior canal): {slack}")

        time_list = list(self.time_data)
        self.dut_voltage_curve.setData(time_list, list(self.dut_voltage_data))
        self.voltage_curve.setData(time_list, list(self.voltage_data))
        self.current_curve.setData(time_list, list(self.current_data))

        if time_list:
            self.vb_main.setXRange(time_list[0], time_list[-1], padding=0.01)
        self.vb_main.autoRange(axis='y')
        self._reposition_slack_text()

    @Slot()
    def clear_plot(self):
        self.time_data.clear()
        self.dut_voltage_data.clear()
        self.voltage_data.clear()
        self.current_data.clear()

        self.dut_voltage_curve.setData([], [])
        self.voltage_curve.setData([], [])
        self.current_curve.setData([], [])
        self.slack_text.setText("Slack: --")

        self.vb_main.autoRange()
