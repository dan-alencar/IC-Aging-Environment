"""
Classe de Log de Dados (Estilo collect2.py)

Cria um arquivo CSV único por teste e escreve os dados nele.
"""
import os
import csv
from datetime import datetime

class DataLogger:
    def __init__(self, log_folder, test_name):
        self.filepath = self._create_log_file(log_folder, test_name)
        self.csv_writer = None
        self.file_handle = None
        self._write_header()

    def _create_log_file(self, folder, name):
        """Cria um nome de arquivo único com timestamp."""
        if not os.path.exists(folder):
            os.makedirs(folder)
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.csv"
        return os.path.join(folder, filename)

    def _write_header(self):
        """Escreve o cabeçalho no arquivo CSV."""
        self.file_handle = open(self.filepath, 'w', newline='', encoding='utf-8')
        self.csv_writer = csv.writer(self.file_handle)
        
        # Este cabeçalho define a estrutura do seu log
        header = [
            'timestamp',
            'oven_temp_c',
            'oven_setpoint_c',
            'oven_output_pct',
            'psu_voltage_v',
            'psu_current_a',
            'dut_temp_c',
            'dut_slack'
        ]
        self.csv_writer.writerow(header)

    def write_data_row(self, data_dict):
        """Escreve uma nova linha de dados no CSV."""
        if self.csv_writer:
            try:
                row = [
                    data_dict.get('timestamp'),
                    data_dict.get('oven_temp'),
                    data_dict.get('oven_setpoint'),
                    data_dict.get('oven_output'),
                    data_dict.get('psu_voltage'),
                    data_dict.get('psu_current'),
                    data_dict.get('dut_temp'),
                    data_dict.get('dut_slack')
                ]
                self.csv_writer.writerow(row)
            except Exception as e:
                print(f"Erro ao escrever no CSV: {e}")

    def close(self):
        """Fecha o arquivo CSV."""
        if self.file_handle:
            self.file_handle.close()
            self.file_handle = None
            print(f"Log salvo em: {self.filepath}")