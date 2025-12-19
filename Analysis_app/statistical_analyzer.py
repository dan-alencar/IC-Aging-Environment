import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error
import os

# --- Configurações ---
CSV_FILE = 'ultimo_teste_analise.csv'
STEADY_STATE_PERCENT = 0.25 # Usar os últimos 25% dos dados para a análise

def analyze_steady_state_performance(csv_file):
    """
    Lê o CSV de um teste isolado e calcula as métricas estatísticas
    do período de regime estacionário.
    """
    print(f"Iniciando análise estatística de: {csv_file}\n")

    # --- 1. Carregar Dados ---
    if not os.path.exists(csv_file):
        print(f"Erro: Arquivo '{csv_file}' não encontrado.")
        return
        
    try:
        df = pd.read_csv(csv_file)
    except Exception as e:
        print(f"Erro ao ler o arquivo CSV: {e}")
        return

    if df.empty:
        print("O arquivo CSV está vazio.")
        return

    # --- 2. Isolar o Período de Regime Estacionário ---
    # Encontra o ponto de início dos últimos 25% do teste
    ss_start_index = int(len(df) * (1.0 - STEADY_STATE_PERCENT))
    
    df_ss = df.iloc[ss_start_index:].copy()
    
    if df_ss.empty:
        print("Não há dados suficientes para analisar o regime estacionário.")
        return
        
    print(f"Analisando o Regime Estacionário (últimos 25%, {len(df_ss)} amostras)...")

    # Define as variáveis para a análise
    y_true = df_ss['setpoint_c'] # O alvo (ex: 100.0)
    y_pred = df_ss['oven_temp_c'] # O valor real

    # --- 3. Calcular Métricas Estatísticas ---
    
    # Métrica 1: Erro de Regime Estacionário (Droop)
    # Mede a PRECISÃO (Accuracy)
    errors = y_true - y_pred
    ss_error_mean = errors.mean()

    # Métrica 2: Desvio Padrão
    # Mede a ESTABILIDADE (Oscilação em torno DA PRÓPRIA MÉDIA)
    ss_std_dev = y_pred.std()

    # Métrica 3: MAE (Mean Absolute Error)
    # Mede o erro médio em °C (fácil de interpretar)
    ss_mae = mean_absolute_error(y_true, y_pred)

    # Métrica 4: RMSE (Root Mean Squared Error)
    # Mede o ERRO GERAL, penalizando erros grandes (Overshoot, Oscilação)
    ss_mse = mean_squared_error(y_true, y_pred)
    ss_rmse = np.sqrt(ss_mse)


    # --- 4. Exibir Relatório ---
    print("\n--- Relatório de Performance Estatística ---")
    print("\n[Métricas de Precisão (Erro vs Setpoint)]")
    print(f"  Erro de Regime Estacionário (Droop): {ss_error_mean:+.4f} °C")
    print(f"     (Interpretação: Um valor negativo, como -0.2, significa que o forno ficou, em média, 0.2°C ACIMA do setpoint)")
    print(f"  Erro Médio Absoluto (MAE):          {ss_mae:.4f} °C")
    print(f"     (Interpretação: Em média, a temperatura esteve a {ss_mae:.4f}°C de distância do setpoint)")
    print(f"  RMSE (Erro Padrão da Indústria):    {ss_rmse:.4f} °C")
    print(f"     (Interpretação: Esta é a 'distância' geral do erro. A sua meta  é < 0.2)")

    print("\n[Métricas de Estabilidade (Oscilação)]")
    print(f"  Desvio Padrão da Temperatura:       {ss_std_dev:+.4f} °C")
    print(f"     (Interpretação: Mede o quanto a temperatura 'vibrou' em torno da sua própria média)")


# --- Executa a análise ---
if __name__ == "__main__":
    analyze_steady_state_performance(CSV_FILE)