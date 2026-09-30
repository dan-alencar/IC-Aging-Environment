"""
=============================================================================
TCC - Sistema de Log de Dados (VERSÃO FINAL)
=============================================================================
Gerencia a criação e escrita de arquivos CSV para registro de testes.

Características:
  - Arquivo único por teste com timestamp
  - Cabeçalho com metadados do sistema
  - Escrita com buffer mínimo (flush imediato)
  - Formato compatível com análise posterior

Autor: [Seu Nome]
Data: Janeiro/2026
=============================================================================
"""
import os
import csv
from datetime import datetime
import config


class DataLogger:
    """
    Gerenciador de log de dados para testes de envelhecimento.
    
    Cria um arquivo CSV único por teste contendo:
      - Cabeçalho com metadados e configuração do sistema
      - Dados sincronizados de todos os sensores
    """
    
    def __init__(self, log_folder, test_name, controller_info=None):
        """
        Inicializa o logger.

        Args:
            log_folder: Pasta para salvar os logs
            test_name: Nome base do teste
            controller_info: dict do controlador do forno identificado via
                firmware (ver config.parse_controller_config). Quando None,
                o cabeçalho cai no bloco PID configurado.
        """
        self.controller_info = controller_info
        self.filepath = self._create_log_file(log_folder, test_name)
        self.csv_writer = None
        self.file_handle = None
        self.start_time = datetime.now()
        self._write_header()

    def _create_log_file(self, folder, name):
        """Cria nome de arquivo único com timestamp."""
        if not os.path.exists(folder):
            os.makedirs(folder)
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Sanitiza nome do teste
        safe_name = "".join(c if c.isalnum() or c in "._-" else "_" for c in name)
        
        filename = f"{safe_name}_{timestamp}.csv"
        return os.path.join(folder, filename)

    def _write_header(self):
        """Escreve cabeçalho com metadados e colunas no arquivo CSV."""
        self.file_handle = open(
            self.filepath, 'w', 
            newline='', 
            encoding='utf-8', 
            buffering=1  # Line buffering para flush imediato
        )
        
        # Escreve metadados como comentários
        self.file_handle.write(f"# ==============================================\n")
        self.file_handle.write(f"# TCC - Log de Teste de Envelhecimento\n")
        self.file_handle.write(f"# ==============================================\n")
        self.file_handle.write(f"# Data/Hora Início: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        self.file_handle.write(f"# \n")
        self._write_controller_block()
        self.file_handle.write(f"# \n")
        self.file_handle.write(f"# CONFIGURAÇÃO:\n")
        self.file_handle.write(f"#   Taxa de Rampa: {config.DEFAULT_RAMP_RATE_C_PER_SEC} °C/s\n")
        self.file_handle.write(f"#   Intervalo de Amostragem: {config.LOG_INTERVAL_MS} ms\n")
        if (self.controller_info or {}).get("type", "PID") == "PID":
            self.file_handle.write(f"#   Janela PWM (SSR): {config.DEFAULT_OVEN_SAMPLE_TIME_MS} ms\n")
        self.file_handle.write(f"# \n")
        self.file_handle.write(f"# LIMITES DE SEGURANÇA:\n")
        self.file_handle.write(f"#   Temp. Máx. Forno: {config.MAX_OVEN_TEMP_C} °C\n")
        self.file_handle.write(f"#   Temp. Máx. DUT: {config.MAX_DUT_TEMP_C} °C\n")
        self.file_handle.write(f"#   Corrente Máx. PSU: {config.MAX_PSU_CURRENT_A} A\n")
        self.file_handle.write(f"# ==============================================\n")
        self.file_handle.write(f"# \n")
        
        # Cria writer CSV
        self.csv_writer = csv.writer(self.file_handle)
        
        # Cabeçalho das colunas
        header = [
            'time_sec',           # Tempo desde início (s)
            'oven_temp_c',        # Temperatura do forno (°C)
            'oven_setpoint_c',    # Setpoint atual (°C)
            'oven_output_pct',    # Saída do controlador (% / duty; bang-bang = 0/100)
            'psu_voltage_v',      # Tensão da fonte (V)
            'psu_current_a',      # Corrente da fonte (A)
            'dut_temp_c',         # Temperatura do DUT (°C)
            'dut_slack',          # Valor do slack (incrementos)
            'dut_volt'            # Tensão do DUT (V)
        ]
        self.csv_writer.writerow(header)

    def _write_controller_block(self):
        """Escreve no cabeçalho o controlador do forno realmente em uso.

        PID e bang-bang são firmwares distintos com o mesmo protocolo serial;
        registrar o tipo correto (consultado via GET_CONFIG) é essencial para
        que a análise documente o regime sem ambiguidade.
        """
        info   = self.controller_info or {}
        ctype  = info.get("type", "PID")
        params = info.get("params", {})
        source = info.get("source", "config-fallback")
        raw    = info.get("raw")

        if ctype == "BANGBANG":
            self.file_handle.write("# CONTROLADOR DO FORNO: BANG-BANG (termostático)\n")
            self.file_handle.write(f"#   Histerese liga  (T < SP - x): -{params.get('HYST_LOW', '?')} °C\n")
            self.file_handle.write(f"#   Histerese desliga (T > SP + x): +{params.get('HYST_HIGH', '?')} °C\n")
            self.file_handle.write(f"#   Intervalo de amostragem do controle: {params.get('SAMPLE_MS', '?')} ms\n")
        elif ctype == "PID":
            self.file_handle.write("# CONTROLADOR DO FORNO: PID (FIXO)\n")
            self.file_handle.write(f"#   Kp = {params.get('KP', f'{config.PID_KP:.6f}')}\n")
            self.file_handle.write(f"#   Ki = {params.get('KI', f'{config.PID_KI:.8f}')}\n")
            self.file_handle.write(f"#   Kd = {params.get('KD', f'{config.PID_KD:.6f}')}\n")
            self.file_handle.write("#   MODELO FOPDT: G(s) = 1.56 exp(-150.6s)/(1307.2s + 1)\n")
        else:
            self.file_handle.write(f"# CONTROLADOR DO FORNO: {ctype}\n")

        self.file_handle.write(f"#   Identificação: {source}\n")
        if raw:
            self.file_handle.write(f"#   GET_CONFIG: {raw}\n")

    def write_data_row(self, data_dict):
        """
        Escreve uma linha de dados no CSV.
        
        Args:
            data_dict: Dicionário com as chaves correspondentes às colunas
        """
        if self.csv_writer:
            try:
                row = [
                    f"{data_dict.get('time_sec', 0):.3f}",
                    f"{data_dict.get('oven_temp', 0):.2f}",
                    f"{data_dict.get('oven_setpoint', 0):.2f}",
                    f"{data_dict.get('oven_output', 0):.2f}",
                    f"{data_dict.get('psu_voltage', 0):.3f}",
                    f"{data_dict.get('psu_current', 0):.4f}",
                    f"{data_dict.get('dut_temp', 0):.3f}",
                    data_dict.get('dut_slack', 0),
                    f"{data_dict.get('dut_volt', 0):.3f}"
                ]
                self.csv_writer.writerow(row)
            except Exception as e:
                print(f"Erro ao escrever no CSV: {e}")

    def write_comment(self, comment):
        """
        Adiciona um comentário ao arquivo de log.
        
        Args:
            comment: Texto do comentário
        """
        if self.file_handle:
            timestamp = datetime.now().strftime('%H:%M:%S')
            self.file_handle.write(f"# [{timestamp}] {comment}\n")

    def close(self):
        """Finaliza e fecha o arquivo CSV."""
        if self.file_handle:
            # Escreve rodapé
            end_time = datetime.now()
            duration = (end_time - self.start_time).total_seconds()
            
            self.file_handle.write(f"# \n")
            self.file_handle.write(f"# ==============================================\n")
            self.file_handle.write(f"# FIM DO LOG\n")
            self.file_handle.write(f"# Data/Hora Fim: {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            self.file_handle.write(f"# Duração Total: {duration:.1f} segundos ({duration/60:.1f} minutos)\n")
            self.file_handle.write(f"# ==============================================\n")
            
            self.file_handle.close()
            print(f"Log finalizado: {self.filepath}")
            print(f"Duração do teste: {duration/60:.1f} minutos")
