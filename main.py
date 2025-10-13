import tkinter as tk
import random

# Função para atualizar os dados do sensor
def atualizar_dados():
    # Simula a leitura de um novo valor do sensor
    valor_simulado = round(random.uniform(20.0, 30.0), 2)
    label_valor.config(text=f"Valor: {valor_simulado}°C")
    
    # Agenda a próxima atualização para daqui a 1000 milissegundos (1 segundo)
    # Altere este valor para a frequência de atualização desejada
    janela.after(1000, atualizar_dados)

# Cria a janela principal da aplicação
janela = tk.Tk()
janela.title("Monitoramento de Sensor")
janela.geometry("300x150")
janela.resizable(False, False) # Impede o redimensionamento da janela

# Frame principal para organizar os widgets
frame_principal = tk.Frame(janela, padx=20, pady=20)
frame_principal.pack(expand=True)

# Título da aplicação
label_titulo = tk.Label(frame_principal, text="Sensor de Temperatura", font=("Helvetica", 16, "bold"))
label_titulo.pack(pady=10)

# Label para exibir o valor do sensor
label_valor = tk.Label(frame_principal, text="Valor: -- °C", font=("Helvetica", 24), fg="blue")
label_valor.pack(pady=10)

# Inicia a função de atualização de dados após 100 milissegundos
janela.after(100, atualizar_dados)

# Inicia o loop principal da interface
janela.mainloop()