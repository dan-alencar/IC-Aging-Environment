import sqlite3
import pandas as pd
import os

# --- Configurações ---
DB_FILE = 'aging_test_log.db'
TABLE_NAME = 'pid_log'
OUTPUT_CSV = 'ultimo_teste_analise.csv'

# O seu log normal ocorre a cada 5 segundos.
# Definimos um "gap" (pausa entre testes) como qualquer
# pausa maior que 60 segundos.
GAP_THRESHOLD_SECONDS = 60 

def extract_last_test_run():
    print(f"Analisando '{DB_FILE}' para extrair o último teste...")
    
    # --- 1. Carregar Dados ---
    if not os.path.exists(DB_FILE):
        print(f"Erro: Arquivo '{DB_FILE}' não encontrado.")
        return

    try:
        conn = sqlite3.connect(DB_FILE)
        # Carrega o banco de dados, convertendo 'timestamp' para datetime
        df = pd.read_sql_query(
            f"SELECT * FROM {TABLE_NAME}", 
            conn, 
            parse_dates=['timestamp']
        )
        conn.close()
    except Exception as e:
        print(f"Erro ao ler o banco de dados: {e}")
        return

    if df.empty:
        print("O banco de dados está vazio.")
        return

    # --- 2. Encontrar o Último Teste ---
    # Garante que os dados estão em ordem cronológica
    df = df.sort_values(by='timestamp')

    # Calcula a diferença (em segundos) entre cada linha
    # .diff() calcula a diferença do atual para o anterior
    # .dt.total_seconds() converte o 'Timedelta' para segundos
    time_diffs = df['timestamp'].diff().dt.total_seconds()

    # Encontra os índices onde a diferença é MAIOR que o nosso limite
    # Estes são os "inícios" de novos testes (após uma pausa)
    gap_indices = df[time_diffs > GAP_THRESHOLD_SECONDS].index

    if gap_indices.empty:
        # Não há gaps, o arquivo SÓ TEM UM teste
        print("Nenhum gap de tempo detectado.")
        print("Assumindo que o arquivo contém apenas um único teste.")
        df_last_run = df
    else:
        # Pega o ÚLTIMO índice onde um gap ocorreu
        last_gap_index = gap_indices[-1]
        
        # O "último teste" são todos os dados A PARTIR desse índice
        # .loc[last_gap_index:] inclui a linha do gap
        df_last_run = df.loc[last_gap_index:]
        
        start_time = df_last_run['timestamp'].iloc[0]
        print(f"Último teste encontrado, iniciando em: {start_time}")

    # --- 3. Salvar o CSV ---
    try:
        df_last_run.to_csv(OUTPUT_CSV, index=False)
        print(f"\nSucesso!")
        print(f"O último teste (com {len(df_last_run)} linhas) foi salvo em:")
        print(f"==> {OUTPUT_CSV}")
    except Exception as e:
        print(f"Erro ao salvar o arquivo CSV: {e}")

if __name__ == "__main__":
    extract_last_test_run()