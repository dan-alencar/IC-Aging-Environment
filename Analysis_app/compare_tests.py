#!/usr/bin/env python3
"""
=============================================================================
TCC - Análise Comparativa: PID vs Bang-Bang
=============================================================================
Script para análise estatística detalhada comparando o desempenho do
controlador PID desenvolvido com o controle termostático (bang-bang).

Métricas calculadas:
  - Erro médio e máximo
  - Desvio padrão (σ)
  - Oscilação pico-a-pico
  - Tempo de acomodação
  - Frequência de comutação
  - Conformidade JEDEC/MIL-STD
  - Eficiência energética estimada

Autor: [Seu Nome]
Data: Janeiro/2026
=============================================================================
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import sys
import os

# Configuração de plot
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = (14, 10)
plt.rcParams['font.size'] = 11
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 12


def load_csv_with_comments(filepath):
    """Carrega CSV ignorando linhas de comentário (#)."""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Encontra a linha do cabeçalho (primeira sem #)
    header_idx = 0
    for i, line in enumerate(lines):
        if not line.strip().startswith('#'):
            header_idx = i
            break
    
    # Carrega a partir do cabeçalho
    df = pd.read_csv(filepath, skiprows=header_idx)
    
    # Converte colunas numéricas (podem vir como string)
    numeric_cols = ['time_sec', 'oven_temp_c', 'oven_setpoint_c', 'oven_output_pct',
                    'psu_voltage_v', 'psu_current_a', 'dut_temp_c', 'dut_slack', 'dut_volt']
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Remove linhas com valores NaN nas colunas essenciais
    essential_cols = ['time_sec', 'oven_temp_c', 'oven_setpoint_c', 'oven_output_pct']
    existing_essential = [c for c in essential_cols if c in df.columns]
    if existing_essential:
        df = df.dropna(subset=existing_essential)
    
    return df


def calculate_steady_state_metrics(data, setpoint, steady_state_start_pct=0.7):
    """
    Calcula métricas de regime permanente.
    
    Args:
        data: DataFrame com os dados
        setpoint: Temperatura alvo
        steady_state_start_pct: Percentual do tempo total onde inicia regime permanente
    """
    # Define região de regime permanente
    total_samples = len(data)
    ss_start_idx = int(total_samples * steady_state_start_pct)
    ss_data = data.iloc[ss_start_idx:]
    
    temp = ss_data['oven_temp_c'].values
    output = ss_data['oven_output_pct'].values
    
    metrics = {
        'n_samples': len(temp),
        'duration_s': ss_data['time_sec'].iloc[-1] - ss_data['time_sec'].iloc[0],
        
        # Temperatura
        'temp_mean': np.mean(temp),
        'temp_std': np.std(temp),
        'temp_min': np.min(temp),
        'temp_max': np.max(temp),
        'temp_ptp': np.max(temp) - np.min(temp),  # Peak-to-peak
        'temp_median': np.median(temp),
        
        # Erro
        'error_mean': setpoint - np.mean(temp),
        'error_abs_mean': np.mean(np.abs(setpoint - temp)),
        'error_max': np.max(np.abs(setpoint - temp)),
        'error_rms': np.sqrt(np.mean((setpoint - temp)**2)),
        
        # Output/Duty Cycle
        'output_mean': np.mean(output),
        'output_std': np.std(output),
        
        # Conformidade
        'jedec_compliant': (np.max(temp) - np.min(temp)) <= 4.0,  # ±2°C
        'milstd_compliant': (np.max(temp) - np.min(temp)) <= 6.0,  # ±3°C
    }
    
    return metrics, ss_data


def calculate_switching_metrics(data):
    """Calcula métricas de comutação do atuador."""
    output = data['oven_output_pct'].values
    time = data['time_sec'].values
    
    # Detecta transições (mudanças significativas no output)
    # Para bang-bang: transições 0->100 ou 100->0
    # Para PID: considera mudança > 10% como transição
    diff = np.abs(np.diff(output))
    transitions = np.sum(diff > 10)
    
    duration = time[-1] - time[0]
    cycles = transitions / 2  # Cada ciclo tem 2 transições
    
    return {
        'transitions': transitions,
        'cycles': cycles,
        'cycles_per_minute': (cycles / duration) * 60 if duration > 0 else 0,
        'avg_cycle_period_s': duration / cycles if cycles > 0 else float('inf')
    }


def calculate_settling_time(data, setpoint, tolerance_pct=0.02):
    """
    Calcula tempo de acomodação (settling time).
    
    Args:
        tolerance_pct: Percentual de tolerância (2% = ±2% do setpoint)
    """
    temp = data['oven_temp_c'].values
    time = data['time_sec'].values
    
    tolerance = setpoint * tolerance_pct
    lower = setpoint - tolerance
    upper = setpoint + tolerance
    
    # Encontra último índice onde temperatura saiu da banda
    in_band = (temp >= lower) & (temp <= upper)
    
    if not np.any(in_band):
        return float('inf')
    
    # Procura de trás para frente o primeiro False
    for i in range(len(in_band) - 1, -1, -1):
        if not in_band[i]:
            if i + 1 < len(time):
                return time[i + 1]
            break
    
    # Se sempre esteve na banda desde o início
    first_in_band = np.argmax(in_band)
    return time[first_in_band]


def generate_comparison_report(pid_file, bangbang_file, setpoint, output_dir='./'):
    """
    Gera relatório comparativo completo.
    
    Args:
        pid_file: Caminho para CSV do teste PID
        bangbang_file: Caminho para CSV do teste Bang-Bang
        setpoint: Temperatura alvo (deve ser igual nos dois testes)
        output_dir: Diretório para salvar resultados
    """
    print("=" * 70)
    print("ANÁLISE COMPARATIVA: PID vs BANG-BANG")
    print("=" * 70)
    
    # Carrega dados
    print("\nCarregando dados...")
    pid_data = load_csv_with_comments(pid_file)
    bb_data = load_csv_with_comments(bangbang_file)
    
    print(f"  PID: {len(pid_data)} amostras, {pid_data['time_sec'].iloc[-1]:.0f}s")
    print(f"  Bang-Bang: {len(bb_data)} amostras, {bb_data['time_sec'].iloc[-1]:.0f}s")
    
    # Calcula métricas
    print("\nCalculando métricas de regime permanente...")
    pid_metrics, pid_ss = calculate_steady_state_metrics(pid_data, setpoint)
    bb_metrics, bb_ss = calculate_steady_state_metrics(bb_data, setpoint)
    
    print("Calculando métricas de comutação...")
    pid_switching = calculate_switching_metrics(pid_data)
    bb_switching = calculate_switching_metrics(bb_data)
    
    print("Calculando tempo de acomodação...")
    pid_settling = calculate_settling_time(pid_data, setpoint)
    bb_settling = calculate_settling_time(bb_data, setpoint)
    
    # =========================================================================
    # RELATÓRIO TEXTUAL
    # =========================================================================
    print("\n" + "=" * 70)
    print("RESULTADOS - REGIME PERMANENTE")
    print("=" * 70)
    
    print(f"\n{'Métrica':<35} {'PID':>15} {'Bang-Bang':>15} {'Melhoria':>12}")
    print("-" * 77)
    
    # Temperatura
    print(f"{'Temperatura média (°C)':<35} {pid_metrics['temp_mean']:>15.2f} {bb_metrics['temp_mean']:>15.2f}")
    print(f"{'Desvio padrão σ (°C)':<35} {pid_metrics['temp_std']:>15.3f} {bb_metrics['temp_std']:>15.3f} {bb_metrics['temp_std']/pid_metrics['temp_std']:>11.1f}x")
    print(f"{'Oscilação pico-a-pico (°C)':<35} {pid_metrics['temp_ptp']:>15.2f} {bb_metrics['temp_ptp']:>15.2f} {bb_metrics['temp_ptp']/pid_metrics['temp_ptp']:>11.1f}x")
    print(f"{'Temperatura mínima (°C)':<35} {pid_metrics['temp_min']:>15.2f} {bb_metrics['temp_min']:>15.2f}")
    print(f"{'Temperatura máxima (°C)':<35} {pid_metrics['temp_max']:>15.2f} {bb_metrics['temp_max']:>15.2f}")
    
    # Erro
    print(f"\n{'Erro médio (°C)':<35} {pid_metrics['error_mean']:>15.2f} {bb_metrics['error_mean']:>15.2f}")
    print(f"{'Erro absoluto médio (°C)':<35} {pid_metrics['error_abs_mean']:>15.2f} {bb_metrics['error_abs_mean']:>15.2f} {bb_metrics['error_abs_mean']/pid_metrics['error_abs_mean']:>11.1f}x")
    print(f"{'Erro máximo (°C)':<35} {pid_metrics['error_max']:>15.2f} {bb_metrics['error_max']:>15.2f} {bb_metrics['error_max']/pid_metrics['error_max']:>11.1f}x")
    print(f"{'Erro RMS (°C)':<35} {pid_metrics['error_rms']:>15.3f} {bb_metrics['error_rms']:>15.3f} {bb_metrics['error_rms']/pid_metrics['error_rms']:>11.1f}x")
    
    # Output
    print(f"\n{'Duty cycle médio (%)':<35} {pid_metrics['output_mean']:>15.1f} {bb_metrics['output_mean']:>15.1f}")
    print(f"{'Variação do output σ (%)':<35} {pid_metrics['output_std']:>15.1f} {bb_metrics['output_std']:>15.1f}")
    
    # Comutação
    print(f"\n{'Ciclos de comutação':<35} {pid_switching['cycles']:>15.0f} {bb_switching['cycles']:>15.0f}")
    print(f"{'Ciclos por minuto':<35} {pid_switching['cycles_per_minute']:>15.2f} {bb_switching['cycles_per_minute']:>15.2f}")
    
    # Conformidade
    print(f"\n{'Conforme JEDEC (±2°C)':<35} {'SIM' if pid_metrics['jedec_compliant'] else 'NÃO':>15} {'SIM' if bb_metrics['jedec_compliant'] else 'NÃO':>15}")
    print(f"{'Conforme MIL-STD-883 (±3°C)':<35} {'SIM' if pid_metrics['milstd_compliant'] else 'NÃO':>15} {'SIM' if bb_metrics['milstd_compliant'] else 'NÃO':>15}")
    
    print("\n" + "=" * 70)
    print("RESUMO DA MELHORIA")
    print("=" * 70)
    
    improvement_ptp = bb_metrics['temp_ptp'] / pid_metrics['temp_ptp']
    improvement_std = bb_metrics['temp_std'] / pid_metrics['temp_std']
    improvement_error = bb_metrics['error_abs_mean'] / pid_metrics['error_abs_mean']
    
    print(f"\n  • Redução da oscilação: {improvement_ptp:.1f}x ({bb_metrics['temp_ptp']:.1f}°C → {pid_metrics['temp_ptp']:.1f}°C)")
    print(f"  • Redução do desvio padrão: {improvement_std:.1f}x ({bb_metrics['temp_std']:.2f}°C → {pid_metrics['temp_std']:.2f}°C)")
    print(f"  • Redução do erro médio: {improvement_error:.1f}x ({bb_metrics['error_abs_mean']:.2f}°C → {pid_metrics['error_abs_mean']:.2f}°C)")
    
    if pid_metrics['jedec_compliant'] and not bb_metrics['jedec_compliant']:
        print(f"\n  ✓ Sistema PID ATENDE à norma JEDEC JESD22-A108")
        print(f"  ✗ Sistema Bang-Bang NÃO ATENDE à norma JEDEC")
    
    # =========================================================================
    # GRÁFICOS
    # =========================================================================
    print("\nGerando gráficos...")
    
    fig, axes = plt.subplots(3, 2, figsize=(16, 14))
    fig.suptitle(f'Análise Comparativa: PID vs Bang-Bang (Setpoint = {setpoint}°C)', 
                 fontsize=16, fontweight='bold')
    
    # 1. Temperatura ao longo do tempo
    ax1 = axes[0, 0]
    ax1.plot(pid_data['time_sec']/60, pid_data['oven_temp_c'], 'b-', label='PID', alpha=0.8)
    ax1.plot(bb_data['time_sec']/60, bb_data['oven_temp_c'], 'r-', label='Bang-Bang', alpha=0.8)
    ax1.axhline(y=setpoint, color='k', linestyle='--', label=f'Setpoint ({setpoint}°C)')
    ax1.axhline(y=setpoint+2, color='g', linestyle=':', alpha=0.5, label='JEDEC ±2°C')
    ax1.axhline(y=setpoint-2, color='g', linestyle=':', alpha=0.5)
    ax1.set_xlabel('Tempo (minutos)')
    ax1.set_ylabel('Temperatura (°C)')
    ax1.set_title('Evolução da Temperatura')
    ax1.legend(loc='lower right')
    ax1.grid(True, alpha=0.3)
    
    # 2. Zoom no regime permanente
    ax2 = axes[0, 1]
    ax2.plot(pid_ss['time_sec']/60, pid_ss['oven_temp_c'], 'b-', label='PID', alpha=0.8)
    ax2.plot(bb_ss['time_sec']/60, bb_ss['oven_temp_c'], 'r-', label='Bang-Bang', alpha=0.8)
    ax2.axhline(y=setpoint, color='k', linestyle='--')
    ax2.axhline(y=setpoint+2, color='g', linestyle=':', alpha=0.5)
    ax2.axhline(y=setpoint-2, color='g', linestyle=':', alpha=0.5)
    ax2.set_xlabel('Tempo (minutos)')
    ax2.set_ylabel('Temperatura (°C)')
    ax2.set_title('Regime Permanente (Zoom)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. Saída do controlador
    ax3 = axes[1, 0]
    ax3.plot(pid_data['time_sec']/60, pid_data['oven_output_pct'], 'b-', label='PID', alpha=0.8)
    ax3.plot(bb_data['time_sec']/60, bb_data['oven_output_pct'], 'r-', label='Bang-Bang', alpha=0.8)
    ax3.set_xlabel('Tempo (minutos)')
    ax3.set_ylabel('Saída (%)')
    ax3.set_title('Esforço de Controle')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    ax3.set_ylim(-5, 105)
    
    # 4. Histograma de temperatura
    ax4 = axes[1, 1]
    ax4.hist(pid_ss['oven_temp_c'], bins=30, alpha=0.7, label=f'PID (σ={pid_metrics["temp_std"]:.2f}°C)', color='blue', density=True)
    ax4.hist(bb_ss['oven_temp_c'], bins=30, alpha=0.7, label=f'Bang-Bang (σ={bb_metrics["temp_std"]:.2f}°C)', color='red', density=True)
    ax4.axvline(x=setpoint, color='k', linestyle='--', label='Setpoint')
    ax4.set_xlabel('Temperatura (°C)')
    ax4.set_ylabel('Densidade')
    ax4.set_title('Distribuição de Temperatura (Regime Permanente)')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    # 5. Erro ao longo do tempo
    ax5 = axes[2, 0]
    pid_error = setpoint - pid_data['oven_temp_c']
    bb_error = setpoint - bb_data['oven_temp_c']
    ax5.plot(pid_data['time_sec']/60, pid_error, 'b-', label='PID', alpha=0.8)
    ax5.plot(bb_data['time_sec']/60, bb_error, 'r-', label='Bang-Bang', alpha=0.8)
    ax5.axhline(y=0, color='k', linestyle='-', alpha=0.3)
    ax5.axhline(y=2, color='g', linestyle=':', alpha=0.5)
    ax5.axhline(y=-2, color='g', linestyle=':', alpha=0.5)
    ax5.set_xlabel('Tempo (minutos)')
    ax5.set_ylabel('Erro (°C)')
    ax5.set_title('Erro de Controle')
    ax5.legend()
    ax5.grid(True, alpha=0.3)
    
    # 6. Box plot comparativo
    ax6 = axes[2, 1]
    box_data = [pid_ss['oven_temp_c'].values, bb_ss['oven_temp_c'].values]
    bp = ax6.boxplot(box_data, labels=['PID', 'Bang-Bang'], patch_artist=True)
    bp['boxes'][0].set_facecolor('lightblue')
    bp['boxes'][1].set_facecolor('lightcoral')
    ax6.axhline(y=setpoint, color='k', linestyle='--', label='Setpoint')
    ax6.axhline(y=setpoint+2, color='g', linestyle=':', alpha=0.5)
    ax6.axhline(y=setpoint-2, color='g', linestyle=':', alpha=0.5)
    ax6.set_ylabel('Temperatura (°C)')
    ax6.set_title('Comparação Estatística')
    ax6.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    
    # Salva figura
    plot_path = os.path.join(output_dir, 'comparativo_pid_bangbang.png')
    plt.savefig(plot_path, dpi=150, bbox_inches='tight')
    print(f"  Gráfico salvo: {plot_path}")
    
    plt.show()
    
    # =========================================================================
    # TABELA LATEX
    # =========================================================================
    print("\n" + "=" * 70)
    print("TABELA LATEX PARA O TCC")
    print("=" * 70)
    
    latex_table = f"""
\\begin{{table}}[htbp]
    \\centering
    \\caption{{Comparativo de desempenho: Controle Termostático vs. PID}}
    \\label{{tab:comparativo-pid-bangbang}}
    \\begin{{tabular}}{{lccc}}
        \\toprule
        \\textbf{{Métrica}} & \\textbf{{Bang-Bang}} & \\textbf{{PID}} & \\textbf{{Melhoria}} \\\\
        \\midrule
        Temperatura média (°C) & {bb_metrics['temp_mean']:.2f} & {pid_metrics['temp_mean']:.2f} & --- \\\\
        Desvio padrão $\\sigma$ (°C) & {bb_metrics['temp_std']:.3f} & {pid_metrics['temp_std']:.3f} & {improvement_std:.1f}$\\times$ \\\\
        Oscilação pico-a-pico (°C) & {bb_metrics['temp_ptp']:.2f} & {pid_metrics['temp_ptp']:.2f} & {improvement_ptp:.1f}$\\times$ \\\\
        Erro absoluto médio (°C) & {bb_metrics['error_abs_mean']:.2f} & {pid_metrics['error_abs_mean']:.2f} & {improvement_error:.1f}$\\times$ \\\\
        Erro RMS (°C) & {bb_metrics['error_rms']:.3f} & {pid_metrics['error_rms']:.3f} & {bb_metrics['error_rms']/pid_metrics['error_rms']:.1f}$\\times$ \\\\
        \\midrule
        Conforme JEDEC ($\\pm$2°C) & {'Não' if not bb_metrics['jedec_compliant'] else 'Sim'} & {'Sim' if pid_metrics['jedec_compliant'] else 'Não'} & --- \\\\
        Conforme MIL-STD ($\\pm$3°C) & {'Não' if not bb_metrics['milstd_compliant'] else 'Sim'} & {'Sim' if pid_metrics['milstd_compliant'] else 'Não'} & --- \\\\
        \\bottomrule
    \\end{{tabular}}
\\end{{table}}
"""
    print(latex_table)
    
    return pid_metrics, bb_metrics


# =============================================================================
# MAIN
# =============================================================================
if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Uso: python analise_comparativa.py <arquivo_pid.csv> <arquivo_bangbang.csv> <setpoint>")
        print("\nExemplo:")
        print("  python analise_comparativa.py teste_pid_100c.csv teste_bangbang_100c.csv 100")
        sys.exit(1)
    
    pid_file = sys.argv[1]
    bb_file = sys.argv[2]
    setpoint = float(sys.argv[3])
    
    generate_comparison_report(pid_file, bb_file, setpoint)
