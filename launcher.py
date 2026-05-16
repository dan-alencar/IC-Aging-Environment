"""
Root launcher — presents a Qt dialog to choose between App_Nexys (1 DUT)
and App_2Nexys (2 DUTs). The selected app is spawned as a subprocess and
the launcher exits immediately so no config or workers are shared in memory.
"""
import sys
import os
import subprocess
import signal

from PySide6.QtWidgets import QApplication, QDialog, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt, QTimer

_REPO_ROOT = os.path.dirname(os.path.abspath(__file__))

_DARK_STYLE = """
QDialog, QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
}
QLabel#title {
    font-size: 18pt;
    font-weight: bold;
    color: #89b4fa;
    padding: 12px 0 4px 0;
}
QLabel#subtitle {
    font-size: 10pt;
    color: #6c7086;
    padding-bottom: 16px;
}
QPushButton {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 8px;
    padding: 18px 24px;
    color: #cdd6f4;
    font-size: 13pt;
    font-weight: bold;
    min-width: 280px;
}
QPushButton:hover  { background-color: #45475a; border-color: #89b4fa; }
QPushButton:pressed { background-color: #181825; }
QLabel#hint {
    font-size: 9pt;
    color: #585b70;
    padding-top: 14px;
}
"""


def _launch(script_rel_path: str) -> None:
    """Spawn the chosen app's run.sh and exit the launcher."""
    script_abs = os.path.join(_REPO_ROOT, script_rel_path)
    subprocess.Popen(["bash", script_abs], cwd=os.path.dirname(script_abs))
    sys.exit(0)


class LauncherDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IC Aging Environment")
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setAlignment(Qt.AlignHCenter)

        title = QLabel("IC Aging Environment")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)

        subtitle = QLabel("Select the experiment configuration to launch")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignCenter)

        btn_1dut = QPushButton("App Nexys  —  1 DUT")
        btn_1dut.setToolTip("Single Nexys4 DDR board (Artix-7)")
        btn_1dut.clicked.connect(lambda: _launch("App_Nexys/run.sh"))

        btn_2dut = QPushButton("App 2-Nexys  —  2 DUTs")
        btn_2dut.setToolTip("Two Nexys4 DDR boards with independent PSU voltage control")
        btn_2dut.clicked.connect(lambda: _launch("App_2Nexys/run.sh"))

        hint = QLabel("Each app manages its own virtual environment and hardware connections.")
        hint.setObjectName("hint")
        hint.setAlignment(Qt.AlignCenter)
        hint.setWordWrap(True)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(btn_1dut)
        layout.addWidget(btn_2dut)
        layout.addWidget(hint)

        self.adjustSize()


def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(_DARK_STYLE)

    timer = QTimer()
    timer.timeout.connect(lambda: None)
    timer.start(500)

    dlg = LauncherDialog()
    dlg.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
