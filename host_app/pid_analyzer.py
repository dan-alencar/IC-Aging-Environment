import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# --- Configurações de Análise ---
DB_FILE = 'aging_test_log.db' # O arquivo de log que você forneceu
TABLE_NAME = 'pid_log'
SETPOINT_TARGET = 100.0  # O setpoint alvo de 100°C
SETTLING_BAND_PERCENT = 0.02  # Banda de 2% (para 100°C, fica de 98°C a 102°C)
STEADY_STATE_PERCENT = 0.25 # Usar os últimos 25% dos dados para análise

# --- Nomes dos arquivos de saída ---
PLOT_TEMP_FILE = 'plot_temperatura_vs_tempo.png'
PLOT_OUTPUT_FILE = 'plot_saida_pid_vs_tempo.png'

def analyze_pid_performance(db_file):
    """
    Lê um banco de dados SQLite de um log de PID e realiza uma
    análise de performance comportamental e estatística.
    """
    print(f"Iniciando análise do arquivo: {db_file}\n")
    
    # --- 1. Carregar Dados ---
    try:
        conn = sqlite3.connect(db_file)
        df = pd.read_sql_query(f"SELECT * FROM {TABLE_NAME}", conn)
        conn.close()
    except Exception as e:
        print(f"Erro ao ler o banco de dados: {e}")
        return

    if df.empty:
        print("O banco de dados está vazio.")
        return

    # --- 2. Preparar Dados ---
    # Converter timestamp para datetime e calcular tempo decorrido em segundos
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values(by='timestamp')
    start_time = df['timestamp'].iloc[0]
    df['time_sec'] = (df['timestamp'] - start_time).dt.total_seconds()
    
    # Isolar os dados onde o setpoint atingiu o alvo
    # (ou onde a rampa parou e o setpoint ficou constante)
    df_at_target = df[df['setpoint_c'] == df['setpoint_c'].iloc[-1]]
    
    if df_at_target.empty:
        print(f"Não foram encontrados dados no setpoint alvo.")
        return

    # Define o setpoint alvo com base no último valor
    SETPOINT_TARGET = df_at_target['setpoint_c'].iloc[0]

    # --- 3. Calcular Métricas Estatísticas ---
    print("--- Análise Estatística de Performance ---")
    
    # Overshoot
    T_max = df_at_target['oven_temp_c'].max()
    overshoot_value = T_max - SETPOINT_TARGET
    overshoot_percent = (overshoot_value / SETPOINT_TARGET) * 100.0 if SETPOINT_TARGET != 0 else 0
    print(f"Setpoint Alvo: {SETPOINT_TARGET:.2f}°C")
    print(f"Temperatura de Pico (T_max): {T_max:.2f}°C")
    print(f"Overshoot (Ultrapassagem): {overshoot_value:.2f}°C ({overshoot_percent:.2f}%)")

    # Tempo de Pico
    try:
        peak_time_sec = df_at_target[df_at_target['oven_temp_c'] == T_max]['time_sec'].iloc[0]
        print(f"Tempo de Pico: {peak_time_sec:.2f} segundos")
    except IndexError:
        peak_time_sec = 0
        print("Não foi possível determinar o tempo de pico.")

    # Settling Time (Tempo de Acomodação)
    settling_band_min = SETPOINT_TARGET * (1.0 - SETTLING_BAND_PERCENT)
    settling_band_max = SETPOINT_TARGET * (1.0 + SETTLING_BAND_PERCENT)
    
    try:
        # Encontra o primeiro momento em que o sistema entra na banda
        first_entry_index = df_at_target[(df_at_target['oven_temp_c'] >= settling_band_min) & 
                                         (df_at_target['oven_temp_c'] <= settling_band_max)].index[0]
        
        # Agora, verifica se ele *saiu* da banda depois disso
        df_after_entry = df_at_target.loc[first_entry_index:]
        out_of_band_indices = df_after_entry[(df_after_entry['oven_temp_c'] < settling_band_min) | 
                                             (df_after_entry['oven_temp_c'] > settling_band_max)].index
        
        if not out_of_band_indices.empty:
            last_out_of_band_index = out_of_band_indices[-1]
            # Encontra o índice no DataFrame original
            original_index = df.index[df.index == last_out_of_band_index].tolist()[0]
            if original_index + 1 < len(df):
                settling_time_sec = df.loc[original_index + 1]['time_sec']
                print(f"Tempo de Acomodação (para ±2%): {settling_time_sec:.2f} segundos (tempo para estabilizar após a última perturbação)")
            else:
                 print("Tempo de Acomodação: O sistema saiu da banda e não retornou.")
                 settling_time_sec = None
        else:
            settling_time_sec = df_at_target.loc[first_entry_index]['time_sec']
            print(f"Tempo de Acomodação (para ±2%): {settling_time_sec:.2f} segundos (nunca saiu da banda após a primeira entrada)")
            
    except IndexError:
        print("Tempo de Acomodação: O sistema nunca entrou na banda de ±2%.")
        settling_time_sec = None

    # Análise de Estado Estacionário (Steady-State)
    ss_start_time = df['time_sec'].max() * (1.0 - STEADY_STATE_PERCENT)
    df_ss = df[df['time_sec'] >= ss_start_time]
    
    if not df_ss.empty:
        ss_temp_mean = df_ss['oven_temp_c'].mean()
        ss_error = SETPOINT_TARGET - ss_temp_mean
        ss_oscillation = df_ss['oven_temp_c'].max() - df_ss['oven_temp_c'].min()
        
        print(f"\n--- Análise de Estado Estacionário (Últimos {STEADY_STATE_PERCENT*100}%) ---")
        print(f"Temperatura Média (T_ss): {ss_temp_mean:.2f}°C")
        print(f"Erro Estacionário (Droop): {ss_error:.2f}°C")
        print(f"Oscilação Estacionária (Pico a Vale): {ss_oscillation:.2f}°C")
    
    # --- 4. Análise Comportamental (O Bug do Windup) ---
    print("\n--- Análise Comportamental ---")
    pid_output = df['pid_output_percent']
    if (pid_output > 99.0).any():
        print("Sintoma de Windup: Saída do PID atingiu 100%.")
        
    # Encontra o momento do overshoot
    if overshoot_value > 0 and peak_time_sec > 0:
        df_overshoot = df_at_target[df_at_target['time_sec'] >= peak_time_sec]
        
        # Encontra o primeiro ponto *depois* do pico onde o PID foi para < 1%
        try:
            recovery_point = df_overshoot[df_overshoot['pid_output_percent'] < 1.0].iloc[0]
            recovery_time = recovery_point['time_sec'] - peak_time_sec
            print(f"Tempo de Recuperação do Windup (Output < 1%): {recovery_time:.2f} segundos após o pico.")
        except IndexError:
            print("Bug de Windup Confirmado: A saída do PID nunca foi a 0% após o pico de overshoot.")

    # --- 5. Gerar Gráficos ---
    print("\nGerando gráficos...")
    
    # Gráfico 1: Temperatura vs Tempo
    plt.figure(figsize=(15, 7))
    plt.plot(df['time_sec'], df['oven_temp_c'], label='Temp. Forno (°C)', color='blue')
    plt.plot(df['time_sec'], df['setpoint_c'], label='Setpoint Rampa (°C)', color='red', linestyle='--')
    
    # Adiciona bandas de setpoint
    if settling_time_sec is not None:
        plt.axhline(settling_band_min, color='gray', linestyle=':', label=f'Banda de ±2% ({settling_band_min:.1f}°C)')
        plt.axhline(settling_band_max, color='gray', linestyle=':', label=f'Banda de ±2% ({settling_band_max:.1f}°C)')
    
    plt.axhline(SETPOINT_TARGET, color='black', linestyle='-', label=f'Setpoint Alvo ({SETPOINT_TARGET}°C)')
    if peak_time_sec > 0:
        plt.axvline(peak_time_sec, color='orange', linestyle=':', label=f'Pico ({T_max:.2f}°C)')
    
    plt.title('Análise de Performance: Temperatura vs. Tempo', fontsize=16)
    plt.xlabel('Tempo (segundos)', fontsize=12)
    plt.ylabel('Temperatura (°C)', fontsize=12)
    plt.legend()
    plt.grid(True)
    plt.savefig(PLOT_TEMP_FILE)
    print(f"Gráfico de temperatura salvo em: {PLOT_TEMP_FILE}")

    # Gráfico 2: Saída do PID vs Tempo
    plt.figure(figsize=(15, 5))
    plt.plot(df['time_sec'], df['pid_output_percent'], label='Saída SSR (%)', color='green')
    plt.title('Análise de Performance: Esforço de Controle (Saída PID) vs. Tempo', fontsize=16)
    plt.xlabel('Tempo (segundos)', fontsize=12)
    plt.ylabel('Saída PID (%)', fontsize=12)
    plt.ylim(-5, 105) # Limites de 0-100% com margem
    plt.legend()
    plt.grid(True)
    plt.savefig(PLOT_OUTPUT_FILE)
    print(f"Gráfico de saída do PID salvo em: {PLOT_OUTPUT_FILE}")

# --- Executa a análise ---
if __name__ == "__main__":
    if os.path.exists(DB_FILE):
        analyze_pid_performance(DB_FILE)
    else:
        print(f"Erro: Arquivo '{DB_FILE}' não encontrado.")
        print("Certifique-se de que o banco de dados está na mesma pasta que este script.")