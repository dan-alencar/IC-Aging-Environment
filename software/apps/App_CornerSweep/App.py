"""
App_CornerSweep — Entry point.

Flow:
  1. SetupDialog — configure DUT/PSU/Arduino ports
  2. MainWindow  — run the corner characterisation + failure sweep
"""
import sys

from PySide6.QtWidgets import QApplication, QDialog

import config
from main_window import MainWindow
from setup_config import SetupDialog


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    print("=" * 60)
    print("Corner Sweep — Caracterização de Falha por Tensão")
    print("=" * 60)
    print(f"Corners:        {config.CORNERS_V} V")
    print(f"Passo sweep:    {config.SWEEP_STEP_V} V")
    print(f"V mínimo:       {config.SWEEP_MIN_V} V")
    print(f"Amostras/corner:{config.SAMPLES_PER_CORNER}")
    print("=" * 60)

    dialog = SetupDialog()
    if dialog.exec() != QDialog.Accepted:
        print("Cancelado pelo usuário.")
        sys.exit(0)

    print(f"DUT:     {config.DUT_PORT} @ {config.DUT_BAUD}")
    print(f"PSU:     {config.PSU_PORT} @ {config.PSU_BAUD}")
    if config.ARDUINO_ENABLED:
        print(f"Arduino: {config.ARDUINO_PORT} @ {config.ARDUINO_BAUD}")
    else:
        print("Arduino: desabilitado")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
