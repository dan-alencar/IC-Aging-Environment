"""
=============================================================================
TCC - Aplicação Supervisória de Teste de Envelhecimento (VERSÃO FINAL)
=============================================================================
Ponto de entrada principal da aplicação.

Fluxo:
  1. Abre janela de configuração de hardware (SetupDialog)
  2. Se configuração aceita, inicia janela principal (MainWindow)

Autor: [Seu Nome]
Data: Janeiro/2026
=============================================================================
"""
import sys
from PySide6.QtWidgets import QApplication, QDialog
from setup_config import SetupDialog 
from main_window import MainWindow
import config


def main():
    """Função principal da aplicação."""
    
    # Cria instância da aplicação Qt
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Informações de inicialização
    print("=" * 60)
    print("TCC - Sistema de Teste de Envelhecimento Acelerado")
    print("=" * 60)
    print(f"Parâmetros PID configurados:")
    print(f"  Kp = {config.PID_KP:.4f}")
    print(f"  Ki = {config.PID_KI:.6f}")
    print(f"  Kd = {config.PID_KD:.4f}")
    print("=" * 60)
    
    # 1. Abre janela de configuração de hardware
    setup = SetupDialog()
    
    if setup.exec() == QDialog.Accepted:
        # 2. Configuração aceita - inicia sistema principal
        print("\nConfiguração de hardware carregada:")
        print(f"  Arduino: {config.ARDUINO_PORT} @ {config.ARDUINO_BAUD} baud")
        print(f"  PSU:     {config.PSU_PORT}")
        print(f"  DUT:     {config.DUT_PORT} @ {config.DUT_BAUD} baud")
        print("\nIniciando interface principal...")
        print("-" * 60)
        
        window = MainWindow()
        window.show()
        
        # Inicia loop de eventos
        sys.exit(app.exec())
        
    else:
        # Usuário cancelou
        print("\nInicialização cancelada pelo usuário.")
        sys.exit(0)


if __name__ == "__main__":
    main()
