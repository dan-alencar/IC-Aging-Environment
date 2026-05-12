import sys
import signal
import pyqtgraph as pg
from PySide6.QtWidgets import QApplication, QDialog
from PySide6.QtCore import QTimer
from setup_config import SetupDialog
from main_window import MainWindow

# pyqtgraph dark theme (must be set before any PlotWidget is created)
pg.setConfigOption('background', '#1e1e2e')
pg.setConfigOption('foreground', '#cdd6f4')
pg.setConfigOptions(antialias=True)

_DARK_STYLE = """
QMainWindow, QDialog, QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
}
QTabWidget::pane {
    border: 1px solid #313244;
    border-radius: 4px;
    background-color: #1e1e2e;
}
QTabBar::tab {
    background-color: #181825;
    color: #6c7086;
    padding: 8px 18px;
    border-bottom: 2px solid transparent;
    font-weight: 500;
}
QTabBar::tab:selected {
    color: #89b4fa;
    border-bottom: 2px solid #89b4fa;
    background-color: #1e1e2e;
}
QTabBar::tab:hover:!selected {
    color: #cdd6f4;
    background-color: #1e1e2e;
}
QGroupBox {
    font-weight: bold;
    border: 1px solid #313244;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 14px;
    background-color: #181825;
    color: #89b4fa;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
}
QGroupBox::indicator {
    width: 16px;
    height: 16px;
    border: 1.5px solid #585b70;
    border-radius: 3px;
    background-color: #313244;
    margin-right: 4px;
}
QGroupBox::indicator:checked {
    background-color: #89b4fa;
    border-color: #89b4fa;
}
QLineEdit, QTextEdit {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 4px;
    padding: 5px 8px;
    color: #cdd6f4;
    selection-background-color: #45475a;
}
QLineEdit:focus, QTextEdit:focus { border-color: #89b4fa; }
QSpinBox, QDoubleSpinBox {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 4px;
    padding: 4px 6px;
    color: #cdd6f4;
}
QSpinBox:focus, QDoubleSpinBox:focus { border-color: #89b4fa; }
QSpinBox::up-button, QDoubleSpinBox::up-button,
QSpinBox::down-button, QDoubleSpinBox::down-button {
    background-color: #45475a;
    border: none;
    border-radius: 2px;
}
QSpinBox:disabled, QDoubleSpinBox:disabled {
    background-color: #181825;
    color: #585b70;
    border-color: #313244;
}
QComboBox {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 4px;
    padding: 4px 8px;
    color: #cdd6f4;
}
QComboBox:focus { border-color: #89b4fa; }
QComboBox::drop-down { border: none; width: 20px; }
QComboBox QAbstractItemView {
    background-color: #313244;
    color: #cdd6f4;
    selection-background-color: #45475a;
    border: 1px solid #45475a;
}
QPushButton {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 6px 14px;
    color: #cdd6f4;
    font-weight: bold;
}
QPushButton:hover  { background-color: #45475a; }
QPushButton:pressed { background-color: #181825; }
QPushButton:disabled {
    background-color: #181825;
    color: #585b70;
    border-color: #313244;
}
QCheckBox { color: #cdd6f4; spacing: 6px; }
QCheckBox::indicator {
    width: 16px; height: 16px;
    border: 1.5px solid #585b70;
    border-radius: 3px;
    background-color: #313244;
}
QCheckBox::indicator:checked {
    background-color: #89b4fa;
    border-color: #89b4fa;
}
QScrollBar:vertical {
    background: #1e1e2e;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #45475a;
    border-radius: 4px;
    min-height: 20px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal {
    background: #1e1e2e;
    height: 8px;
}
QScrollBar::handle:horizontal {
    background: #45475a;
    border-radius: 4px;
    min-width: 20px;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
QSplitter::handle { background: #313244; }
QSplitter::handle:horizontal { width: 2px; }
QSplitter::handle:vertical   { height: 2px; }
QFrame[frameShape="4"],
QFrame[frameShape="5"] { color: #313244; }
QStatusBar {
    background-color: #181825;
    color: #6c7086;
    border-top: 1px solid #313244;
    font-size: 10pt;
}
QStatusBar::item { border: none; }
"""


def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(_DARK_STYLE)

    # Keep the Python event loop alive so Ctrl+C works
    timer = QTimer()
    timer.timeout.connect(lambda: None)
    timer.start(500)

    if SetupDialog().exec() == QDialog.Accepted:
        win = MainWindow()
        win.show()
        sys.exit(app.exec())
    else:
        sys.exit()


if __name__ == "__main__":
    main()
