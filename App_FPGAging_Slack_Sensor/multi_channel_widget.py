"""
Multi-channel monitoring widgets for the experimental-multi-sensor branch.

Reuses the deque + pyqtgraph.PlotWidget pattern already established by
plot_widget.py / aux_plot_widget.py, stacked one-per-channel in a
QSplitter (the same layout pattern main_window.py already uses for the
existing two plot widgets), plus a live per-channel stats table.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QSplitter, QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Slot, Qt
from collections import deque
import pyqtgraph as pg

_CHANNEL_COLORS = ['#89b4fa', '#f38ba8', '#a6e3a1', '#fab387',
                   '#cba6f7', '#94e2d5', '#f9e2af', '#eba0ac']


class ChannelSlackPlot(QWidget):
    """One channel's slack-over-time plot, with alarm events marked."""

    def __init__(self, channel_idx, parent=None, plot_window_size=200):
        super().__init__(parent)
        self.channel_idx = channel_idx
        self.time_data = deque(maxlen=plot_window_size)
        self.slack_data = deque(maxlen=plot_window_size)
        self.alarm_time = deque(maxlen=plot_window_size)
        self.alarm_slack = deque(maxlen=plot_window_size)

        color = _CHANNEL_COLORS[channel_idx % len(_CHANNEL_COLORS)]

        self.plot_view = pg.PlotWidget()
        self.plot_view.setTitle(f"Canal {channel_idx}", color='#cdd6f4')
        self.plot_view.setLabel('left', "Slack", color='#a6adc8')
        self.plot_view.showGrid(x=True, y=True, alpha=0.2)

        self.vb = self.plot_view.getViewBox()
        self.vb.enableAutoRange(axis='y')
        self.vb.disableAutoRange(axis='x')

        self.slack_curve = self.plot_view.plot(pen=pg.mkPen(color, width=2))
        self.alarm_scatter = pg.ScatterPlotItem(
            pen=None, brush=pg.mkBrush('#f38ba8'), size=8
        )
        self.plot_view.addItem(self.alarm_scatter)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.plot_view)

    def append(self, time_sec, slack, alarm):
        self.time_data.append(time_sec)
        self.slack_data.append(slack)
        if alarm:
            self.alarm_time.append(time_sec)
            self.alarm_slack.append(slack)

        time_list = list(self.time_data)
        self.slack_curve.setData(time_list, list(self.slack_data))
        self.alarm_scatter.setData(list(self.alarm_time), list(self.alarm_slack))

        if time_list:
            self.vb.setXRange(time_list[0], time_list[-1], padding=0.01)
        self.vb.autoRange(axis='y')

    def clear(self):
        self.time_data.clear()
        self.slack_data.clear()
        self.alarm_time.clear()
        self.alarm_slack.clear()
        self.slack_curve.setData([], [])
        self.alarm_scatter.setData([], [])
        self.vb.autoRange()


class MultiChannelPanel(QWidget):
    """Stacked per-channel plots + a live per-channel stats table.

    update_plot_data(dict) reads dut_slack_chN/dut_alarm_chN from the same
    row dict TestSequencer.plot_data_update already broadcasts to every
    other plot widget (aux_plot_widget/plot_widget), following that same
    "broadcast one dict, each widget filters its own keys" pattern.
    update_stats(list) is fed separately by TestSequencer.stats_update.
    """

    def __init__(self, num_channels, parent=None, plot_window_size=200):
        super().__init__(parent)
        self.num_channels = num_channels

        splitter = QSplitter(Qt.Vertical)
        self.channel_plots = []
        for i in range(num_channels):
            p = ChannelSlackPlot(i, plot_window_size=plot_window_size)
            self.channel_plots.append(p)
            splitter.addWidget(p)

        self.stats_table = QTableWidget(num_channels, 4)
        self.stats_table.setHorizontalHeaderLabels(["Min", "Max", "Média", "Alarmes"])
        self.stats_table.setVerticalHeaderLabels([f"Canal {i}" for i in range(num_channels)])
        self.stats_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.stats_table.setMaximumHeight(36 + 28 * num_channels)
        self.stats_table.setStyleSheet(
            "QTableWidget { background-color: #1e1e2e; color: #cdd6f4; "
            "gridline-color: #313244; }"
            "QHeaderView::section { background-color: #313244; color: #cdd6f4; }"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(splitter, stretch=4)
        layout.addWidget(self.stats_table, stretch=1)

    @Slot(dict)
    def update_plot_data(self, data_row):
        time_sec = data_row.get('time_sec', 0.0)
        for i, p in enumerate(self.channel_plots):
            slack = data_row.get(f'dut_slack_ch{i}', 0)
            alarm = bool(data_row.get(f'dut_alarm_ch{i}', 0))
            p.append(time_sec, slack, alarm)

    @Slot(list)
    def update_stats(self, stats_list):
        if not stats_list:
            return
        for i, s in enumerate(stats_list):
            if i >= self.num_channels:
                break
            self.stats_table.setItem(i, 0, QTableWidgetItem(str(s['min'])))
            self.stats_table.setItem(i, 1, QTableWidgetItem(str(s['max'])))
            self.stats_table.setItem(i, 2, QTableWidgetItem(f"{s['mean']:.1f}"))
            self.stats_table.setItem(i, 3, QTableWidgetItem(str(s['alarm_count'])))

    @Slot()
    def clear_plot(self):
        for p in self.channel_plots:
            p.clear()
        self.stats_table.clearContents()
