#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CROC FPGA Sensor Monitor & Programming Tool

A unified application for:
- Real-time monitoring of aging sensor data (alarm_f, alarm_rf)
- Visual representation of active/inactive sensors
- FPGA bitstream programming via Vivado
- STM32 communication for voltage control

Cross-platform: Windows 11 & Linux
"""

import sys
import signal
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from PySide6.QtGui import QPalette, QColor

def apply_dark_palette(app: QApplication):
    """Apply a modern dark theme to the application."""
    palette = QPalette()
    
    # Base colors
    palette.setColor(QPalette.Window, QColor(45, 45, 48))
    palette.setColor(QPalette.WindowText, QColor(212, 212, 212))
    palette.setColor(QPalette.Base, QColor(30, 30, 30))
    palette.setColor(QPalette.AlternateBase, QColor(45, 45, 48))
    palette.setColor(QPalette.ToolTipBase, QColor(45, 45, 48))
    palette.setColor(QPalette.ToolTipText, QColor(212, 212, 212))
    palette.setColor(QPalette.Text, QColor(212, 212, 212))
    palette.setColor(QPalette.Button, QColor(45, 45, 48))
    palette.setColor(QPalette.ButtonText, QColor(212, 212, 212))
    palette.setColor(QPalette.BrightText, QColor(255, 255, 255))
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    
    # Disabled colors
    palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(127, 127, 127))
    palette.setColor(QPalette.Disabled, QPalette.Text, QColor(127, 127, 127))
    palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(127, 127, 127))
    
    app.setPalette(palette)
    
    # Additional stylesheet for finer control
    app.setStyleSheet("""
        QToolTip {
            color: #d4d4d4;
            background-color: #2d2d30;
            border: 1px solid #3f3f46;
            padding: 4px;
        }
        QGroupBox {
            font-weight: bold;
            border: 1px solid #3f3f46;
            border-radius: 4px;
            margin-top: 8px;
            padding-top: 8px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }
        QPushButton {
            background-color: #3f3f46;
            border: 1px solid #5a5a5a;
            border-radius: 4px;
            padding: 6px 12px;
            min-height: 20px;
        }
        QPushButton:hover {
            background-color: #4a4a52;
            border-color: #6a6a6a;
        }
        QPushButton:pressed {
            background-color: #2d2d30;
        }
        QPushButton:disabled {
            background-color: #2d2d30;
            color: #7f7f7f;
        }
        QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
            background-color: #1e1e1e;
            border: 1px solid #3f3f46;
            border-radius: 3px;
            padding: 4px;
        }
        QTextEdit {
            background-color: #1e1e1e;
            border: 1px solid #3f3f46;
            border-radius: 3px;
        }
        QScrollBar:vertical {
            background-color: #2d2d30;
            width: 12px;
            margin: 0;
        }
        QScrollBar::handle:vertical {
            background-color: #5a5a5a;
            min-height: 20px;
            border-radius: 4px;
            margin: 2px;
        }
        QScrollBar::handle:vertical:hover {
            background-color: #6a6a6a;
        }
        QTabWidget::pane {
            border: 1px solid #3f3f46;
            border-radius: 4px;
        }
        QTabBar::tab {
            background-color: #2d2d30;
            border: 1px solid #3f3f46;
            padding: 8px 16px;
            margin-right: 2px;
        }
        QTabBar::tab:selected {
            background-color: #3f3f46;
            border-bottom-color: #3f3f46;
        }
        QTabBar::tab:hover:!selected {
            background-color: #383838;
        }
    """)


def main():
    # Allow Ctrl+C to terminate
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    apply_dark_palette(app)
    
    # Timer trick for Python signal handling with Qt
    timer = QTimer()
    timer.timeout.connect(lambda: None)
    timer.start(500)
    
    # Import here to avoid circular imports
    from main_window import MainWindow
    
    win = MainWindow()
    win.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()