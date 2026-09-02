"""
App_2Nexys — Data logger.

Extends App_Nexys/logger.py with dual-DUT columns:
  psu0_*, dut0_*, psu1_*, dut1_*, psu0_cmd_v, psu1_cmd_v.

The psu*_cmd_v columns record the PSU command voltage (what the app sent),
while psu*_voltage_v records the PSU's own measured readback.
"""
import os
import csv
from datetime import datetime
import config
from protocol import MULTI_NUM_CHANNELS


class DataLogger:
    def __init__(self, log_folder, test_name, num_channels=MULTI_NUM_CHANNELS):
        self.num_channels = num_channels
        self.filepath = self._create_log_file(log_folder, test_name)
        self.csv_writer = None
        self.file_handle = None
        self.start_time = datetime.now()
        self._write_header()

    def _create_log_file(self, folder, name):
        if not os.path.exists(folder):
            os.makedirs(folder)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = "".join(c if c.isalnum() or c in "._-" else "_" for c in name)
        return os.path.join(folder, f"{safe_name}_{timestamp}.csv")

    def _write_header(self):
        self.file_handle = open(
            self.filepath, "w", newline="", encoding="utf-8", buffering=1
        )
        w = self.file_handle.write
        w(f"# ==============================================\n")
        w(f"# App_2Nexys - Log de Teste de Envelhecimento (2 DUTs)\n")
        w(f"# ==============================================\n")
        w(f"# Data/Hora Início: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        w(f"# \n")
        w(f"# PARÂMETROS PID (FIXOS):\n")
        w(f"#   Kp = {config.PID_KP:.6f}\n")
        w(f"#   Ki = {config.PID_KI:.8f}\n")
        w(f"#   Kd = {config.PID_KD:.6f}\n")
        w(f"# \n")
        w(f"# MODELO FOPDT IDENTIFICADO:\n")
        w(f"#   G(s) = 1.56 * exp(-150.6s) / (1307.2s + 1)\n")
        w(f"#   K = 1.56 °C/%  θ = 150.6 s  τ = 1307.2 s\n")
        w(f"# \n")
        w(f"# CONTROLE VCCINT:\n")
        w(f"#   Kv (P-only) = {config.VOLTAGE_KP:.3f} V/V\n")
        w(f"#   Setpoint DUT0 = {config.VCCINT_SETPOINT_0_V:.3f} V\n")
        w(f"#   Setpoint DUT1 = {config.VCCINT_SETPOINT_1_V:.3f} V\n")
        w(f"# \n")
        w(f"# CONFIGURAÇÃO:\n")
        w(f"#   Taxa de Rampa: {config.DEFAULT_RAMP_RATE_C_PER_SEC} °C/s\n")
        w(f"#   Intervalo de Amostragem: {config.LOG_INTERVAL_MS} ms\n")
        w(f"# \n")
        w(f"# LIMITES DE SEGURANÇA:\n")
        w(f"#   Temp. Máx. Forno: {config.MAX_OVEN_TEMP_C} °C\n")
        w(f"#   Temp. Máx. DUT: {config.MAX_DUT_TEMP_C} °C\n")
        w(f"#   Corrente Máx. PSU: {config.MAX_PSU_CURRENT_A} A\n")
        w(f"# ==============================================\n")
        w(f"# \n")

        # dut0_slack/dut1_slack (and alarm) each get one column per channel
        # (dut0_slack_ch0..chN-1) -- there's no functional canary left to
        # report on this branch, and slack is now per-channel.
        header = [
            "time_sec",
            "oven_temp_c", "oven_setpoint_c", "oven_output_pct",
            "psu0_voltage_v", "psu0_current_a", "dut0_temp_c", "dut0_volt",
            "psu1_voltage_v", "psu1_current_a", "dut1_temp_c", "dut1_volt",
            "psu0_cmd_v", "psu1_cmd_v",
        ]
        for prefix in ("dut0", "dut1"):
            for i in range(self.num_channels):
                header.append(f"{prefix}_slack_ch{i}")
            for i in range(self.num_channels):
                header.append(f"{prefix}_alarm_ch{i}")

        self.csv_writer = csv.writer(self.file_handle)
        self.csv_writer.writerow(header)

    def write_data_row(self, d: dict):
        if not self.csv_writer:
            return
        try:
            row = [
                f"{d.get('time_sec', 0):.3f}",
                f"{d.get('oven_temp', 0):.2f}",
                f"{d.get('oven_setpoint', 0):.2f}",
                f"{d.get('oven_output', 0):.2f}",
                f"{d.get('psu0_voltage', 0):.3f}",
                f"{d.get('psu0_current', 0):.4f}",
                f"{d.get('dut0_temp', 0):.3f}",
                f"{d.get('dut0_volt', 0):.3f}",
                f"{d.get('psu1_voltage', 0):.3f}",
                f"{d.get('psu1_current', 0):.4f}",
                f"{d.get('dut1_temp', 0):.3f}",
                f"{d.get('dut1_volt', 0):.3f}",
                f"{d.get('psu0_cmd_v', 0):.3f}",
                f"{d.get('psu1_cmd_v', 0):.3f}",
            ]
            for prefix in ("dut0", "dut1"):
                for i in range(self.num_channels):
                    row.append(d.get(f"{prefix}_slack_ch{i}", 0))
                for i in range(self.num_channels):
                    row.append(d.get(f"{prefix}_alarm_ch{i}", 0))
            self.csv_writer.writerow(row)
        except Exception as e:
            print(f"CSV write error: {e}")

    def write_comment(self, comment):
        if self.file_handle:
            ts = datetime.now().strftime("%H:%M:%S")
            self.file_handle.write(f"# [{ts}] {comment}\n")

    def close(self):
        if self.file_handle:
            end_time = datetime.now()
            duration = (end_time - self.start_time).total_seconds()
            w = self.file_handle.write
            w(f"# \n")
            w(f"# ==============================================\n")
            w(f"# FIM DO LOG\n")
            w(f"# Data/Hora Fim: {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            w(f"# Duração Total: {duration:.1f} s ({duration/60:.1f} min)\n")
            w(f"# ==============================================\n")
            self.file_handle.close()
            print(f"Log finalizado: {self.filepath}")
