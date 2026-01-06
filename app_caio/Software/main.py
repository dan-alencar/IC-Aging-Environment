#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from PySide6.QtWidgets import QApplication
from ui import MainWindow, apply_dark_palette

def main():
    app = QApplication(sys.argv)
    apply_dark_palette(app)

    win = MainWindow()
    win.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
