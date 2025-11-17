"""
Arquivo Principal - Ponto de Entrada da Aplicação

Este é o único arquivo que você precisa executar.
Ele inicia a interface gráfica (HMI) principal.
"""
import sys
from PySide6.QtWidgets import QApplication
from main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Define um estilo (opcional, mas deixa mais bonito)
    app.setStyle("Fusion") 
    
    # Cria e exibe a janela principal
    window = MainWindow()
    window.show()
    
    # Inicia o loop de eventos da aplicação
    sys.exit(app.exec())