import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# --- Configurações ---
DATA_FILE = "step_test_data.csv"
STEP_MAGNITUDE_U = 50.0  # (em %) - O mesmo valor de STEP_DUTY_CYCLE

def analyze_fopdt():
    try:
        data = pd.read_csv(DATA_FILE)
    except FileNotFoundError:
        print(f"Erro: Arquivo {DATA_FILE} não encontrado.")
        print("Rode o script 'step_test_runner.py' primeiro.")
        return

    # --- 1. Preparar Dados ---
    time = data['Time_sec']
    temp = data['Temperature_C']
    
    # Detecta parâmetros iniciais
    T_inicial = temp[0]
    T_final = temp.iloc[-1] # Pega o último valor
    Delta_T_final = T_final - T_inicial
    
    print("--- Análise da Resposta ao Degrau ---")
    print(f"Temperatura Inicial (T_inicial): {T_inicial:.2f} °C")
    print(f"Temperatura Final (T_final): {T_final:.2f} °C")
    print(f"Variação Total (Delta_T_final): {Delta_T_final:.2f} °C")

    # --- 2. Calcular Parâmetros FOPDT ---
    
    # [cite_start]K (Ganho) [cite: 524]
    K = Delta_T_final / STEP_MAGNITUDE_U
    print(f"\n1. Ganho de Regime (K): {K:.4f} °C / %Potência")

    # [cite_start]L (Tempo Morto) [cite: 525]
    # Encontra o tempo (L) onde a temperatura *realmente* começa a subir.
    # (Vamos definir "começa a subir" como > 2% da variação total)
    try:
        L_index = np.where(temp > (T_inicial + 0.02 * Delta_T_final))[0][0]
        L = time[L_index]
    except IndexError:
        L = 0
        print("Aviso: Não foi possível detectar o tempo morto (L) automaticamente.")
    
    print(f"2. Tempo Morto (L ou theta): {L:.2f} segundos")

    # [cite_start]T (Constante de Tempo) [cite: 527-528]
    # É o tempo (APÓS L) para atingir 63.2% da mudança final.
    T_63pct = T_inicial + (0.632 * Delta_T_final)
    
    try:
        # Encontra o tempo absoluto onde T atinge T_63pct
        T_63_abs_index = np.where(temp >= T_63pct)[0][0]
        T_63_abs_time = time[T_63_abs_index]
        
        # A constante T (tau) é o tempo após o tempo morto (L)
        T = T_63_abs_time - L
    except IndexError:
        T = 0
        print("Aviso: A temperatura nunca atingiu 63.2% da estabilização.")
        print("      Verifique se o teste rodou por tempo suficiente.")

    print(f"3. Constante de Tempo (T ou tau): {T:.2f} segundos")
    
    print("\n--- Resultados Finais (Modelo FOPDT) ---")
    print(f"G(s) = K * e^(-Ls) / (Ts + 1)")
    print(f"K = {K:.4f}")
    print(f"L = {L:.2f}")
    print(f"T = {T:.2f}")

    # --- 3. Plotar Gráfico ---
    plt.figure(figsize=(12, 7))
    plt.plot(time, temp, 'b-', label='Temperatura do Forno (PV)')
    
    # Linhas de referência
    plt.axhline(y=T_inicial, color='k', linestyle='--', label=f'T_inicial ({T_inicial:.2f}°C)')
    plt.axhline(y=T_final, color='k', linestyle=':', label=f'T_final ({T_final:.2f}°C)')
    plt.axhline(y=T_63pct, color='r', linestyle='--', label=f'63.2% da subida ({T_63pct:.2f}°C)')
    
    # Linhas do modelo
    plt.axvline(x=L, color='g', linestyle='--', label=f'Tempo Morto (L = {L:.2f}s)')
    plt.axvline(x=(L + T), color='purple', linestyle='--', label=f'L + T (Tempo 63.2% = {L+T:.2f}s)')

    plt.title('Resposta ao Degrau do Forno (Identificação FOPDT)')
    plt.xlabel('Tempo (segundos)')
    plt.ylabel('Temperatura (°C)')
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    analyze_fopdt()