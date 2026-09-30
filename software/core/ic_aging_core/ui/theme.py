"""
Centralized theme stylesheet and color palette (Catppuccin Mocha) for IC-Aging applications.
"""

PALETTE = {
    "base": "#1e1e2e",
    "mantle": "#181825",
    "crust": "#11111b",
    "surface0": "#313244",
    "surface1": "#45475a",
    "surface2": "#585b70",
    "text": "#cdd6f4",
    "subtext0": "#a6adc8",
    "subtext1": "#bac2de",
    "blue": "#89b4fa",
    "lavender": "#b4befe",
    "sapphire": "#74c7ec",
    "sky": "#89dceb",
    "teal": "#94e2d5",
    "green": "#a6e3a1",
    "yellow": "#f9e2af",
    "peach": "#fab387",
    "maroon": "#eba0ac",
    "red": "#f38ba8",
    "mauve": "#cba6f7",
}

DARK_STYLE = """
QMainWindow, QDialog, QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
    font-family: 'Segoe UI', 'Ubuntu', 'Helvetica Neue', sans-serif;
}
QGroupBox {
    border: 1px solid #45475a;
    border-radius: 8px;
    margin-top: 1.2em;
    padding-top: 0.8em;
    font-weight: bold;
    color: #89b4fa;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 4px;
}
QPushButton {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 6px 14px;
    color: #cdd6f4;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #45475a;
    border-color: #89b4fa;
}
QPushButton:pressed {
    background-color: #181825;
}
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background-color: #181825;
    border: 1px solid #45475a;
    border-radius: 4px;
    padding: 4px 8px;
    color: #cdd6f4;
}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
    border: 1px solid #89b4fa;
}
QTabBar::tab {
    background: #181825;
    color: #a6adc8;
    padding: 8px 16px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background: #313244;
    color: #cdd6f4;
    font-weight: bold;
    border-bottom: 2px solid #89b4fa;
}
QTabBar::tab:hover {
    background: #262738;
}
QPlainTextEdit {
    background-color: #11111b;
    border: 1px solid #313244;
    border-radius: 4px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 9pt;
    color: #a6adc8;
}
QStatusBar {
    background-color: #181825;
    color: #a6adc8;
    border-top: 1px solid #313244;
}
"""
