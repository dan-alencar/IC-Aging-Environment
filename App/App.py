"""
Arquivo Principal - Ponto de Entrada da Aplicação
"""
import sys
from PySide6.QtWidgets import QApplication, QDialog
from setup_config import SetupDialog 
from main_window import MainWindow 

if __name__ == "__main__":
    # Cria a instância da aplicação Qt
    app = QApplication(sys.argv)
    app.setStyle("Fusion") 
    
    # 1. Abre primeiro a Janela de Configuração (Modal)
    setup = SetupDialog()
    
    # setup.exec() bloqueia a execução aqui até o usuário fechar a janela
    if setup.exec() == QDialog.Accepted:
        # 2. Se o usuário clicou em "Salvar e Iniciar", abrimos a Main
        print("Configuração carregada. Iniciando sistema...")
        
        window = MainWindow()
        window.show()
        
        # Inicia o loop de eventos
        sys.exit(app.exec())
    else:
        # Se o usuário fechou ou cancelou, encerramos tudo
        print("Inicialização cancelada pelo usuário.")
        sys.exit()