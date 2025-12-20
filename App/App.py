import sys
from PySide6.QtWidgets import QApplication, QDialog
from setup_config import SetupDialog
from main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # 1. Configuração de Portas
    if SetupDialog().exec() == QDialog.Accepted:
        # 2. Janela Principal
        win = MainWindow()
        win.show()
        sys.exit(app.exec())
    else:
        sys.exit()