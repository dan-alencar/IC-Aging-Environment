import sys
import signal
from PySide6.QtWidgets import QApplication, QDialog
from PySide6.QtCore import QTimer
from setup_config import SetupDialog
from main_window import MainWindow

def main():
    # 1. Permite que o Ctrl+C (SIGINT) encerre o programa no terminal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # 2. Truque vital para aplicações Python+Qt:
    # O Qt bloqueia o interpretador Python. Este timer roda um "nada" a cada 500ms,
    # acordando o interpretador para verificar se você apertou Ctrl+C.
    timer = QTimer()
    timer.timeout.connect(lambda: None)
    timer.start(500)
    
    # 3. Executa o Dialog de Configuração
    # Nota: Se demorar para abrir, é culpa do 'list_ports' dentro do SetupDialog.
    if SetupDialog().exec() == QDialog.Accepted:
        # 4. Inicia Janela Principal
        win = MainWindow()
        win.show()
        
        # Executa o loop principal
        sys.exit(app.exec())
    else:
        sys.exit()

if __name__ == "__main__":
    main()