# D&T 2027 — material do artigo SBCCI 2026

Tudo o que foi usado ou produzido no artigo do SBCCI 2026, reunido como base para a versão D&T 2027.

> D. Alencar, A. Barros, A. Pamplona, A. Grangeiro, L. Nogueira, J. Silveira, F. Vargas.
> *Quantifying the Effect of Burn-In Thermal Control on Delivered Acceleration Factor and
> On-Chip Slack-Sensor Fidelity in an FPGA Target.* 39º SBCCI, 2026 (aceito).
> BibTeX em `01_artigo/referencias.bib`.

**O experimento:** o mesmo Artix-7 (Nexys 4 DDR) e o mesmo sensor de slack em duas corridas de
23.08 h. A primeira usou o forno com o termostato original (bang-bang, abr/2025). A segunda usou o
mesmo forno controlado por PID (jan/2026).

**Origem dos arquivos:** pasta montada em 2026-10-26 a partir do working tree e do histórico git
(commits `bba71bc`, `09eaa46`, `2eb5238` e `a40bb7a`). A maior parte destes arquivos não existe mais
no `main`, porque foi apagada no commit `9644acd` (12/05/2026). A origem e o md5 de cada arquivo
estão em `PROVENIENCIA.tsv`.

## Estrutura

| Pasta | Conteúdo |
|---|---|
| `01_artigo/` | PDF submetido (2026-05-04), PDF camera-ready (2026-06-19) e `referencias.bib` |
| `02_dados/bangbang_2025-04-07/` | `SBCCI_TCC_COMP_ESTABILIZADO.csv` é a **corrida bang-bang do artigo** (07–08/04/2025, uma amostra a cada 2 s; temperatura em m°C e tensão em mV). `aging-plot-semana1.csv` é o log bruto da semana de burn-in do SBCCI 2025; o arquivo de 23.08 h corresponde às primeiras 41.500 linhas dele. |
| `02_dados/pid_2026-01-10/` | `TCC_SBCCI_COMP_ESTABILIZADO.csv` é a **corrida PID do artigo** (10–11/01/2026, 1 Hz). Em `calibracao_2026-01-10/` estão os testes curtos do mesmo dia usados para escolher o setpoint do forno e a tensão da fonte. |
| `03_identificacao_forno_FOPDT/` | Teste de degrau do forno (`step_test_data.csv`, nov/2025), firmware do degrau (Arduino), coletor `step_test_runner.py` e `fopdt_analyzer.py`, que dá K = 1.56 °C/%, θ = 150.6 s e τ = 1307.2 s. |
| `04_aquisicao/bangbang_2025_app_sbcci/` | Scripts que gravaram a corrida bang-bang (`collect.py` + `uart_reader.py`), com o laço de tensão citado no artigo (passo de 5 mV, banda de 10, ≥ 2 s). São um snapshot de nov/2025, porque a versão de abr/2025 não está no git. O bloco comentado no início dos dois arquivos corresponde ao formato daquela corrida (pacote de 8 bytes, CSV de 5 colunas). |
| `04_aquisicao/pid_2026-01_App_Nexys/` | App que gravou a corrida PID, com o código como estava em 10/01/2026. Roda com `./run.sh`. |
| `04_aquisicao/firmware_forno_PID/` | `PID_Controller.ino` usado na corrida PID (ArduPID, janela de SSR de 5 s, rampa de 1 °C/s). |
| `05_analise/` | `analise_sbcci_vs_pid.py` compara um dia de cada bancada e `analise_normalizada.py` compara a semana bang-bang com o PID; as figuras geradas estão em `figuras/`. Em `derivado_TF_teoria_da_informacao/` está `kl_benches.py`, a divergência KL/JS entre as bancadas feita no trabalho de Teoria da Informação. |
| `06_hardware_DUT_nexys4ddr/` | Projeto Vivado do DUT (`aging-study`) como foi commitado em 17/11/2025: block design, RTL do sensor, XDC, checkpoint roteado e `fixed_pnr.dcp`. Não há `.bit` no git. |
| `07_referencias_citadas/` | As 7 referências do artigo que existem no repositório. O prefixo é o número da referência no artigo. |
| `08_contexto/` | TCC final de Danilo Alencar (jan/2026, 70 p.), com a bancada PID completa, a identificação FOPDT e o SIMC; a proposta de TCC (jul/2025); o guia de onboarding do ambiente (mai/2026); e o rascunho JICS (jul/2026), que é a extensão do artigo do SBCCI 2025 para revista. |
| `09_apoio_nao_usado_no_artigo/` | Material do TCC sobre o forno que não entrou no artigo: PID vs ON-OFF a 100 °C (ar do forno), PID vs SIMC puro, logs brutos do App_Nexys de 8 a 11/01/2026 e a sintonia inicial do PID (nov/2025). |
| `10_DT_Monitor/` | **D&T Monitor**: app das runs novas com duas placas AU15P (Artix UltraScale+), com o mesmo sistema de bancada do SBCCI 2026, mas com os dados vindo pelo STM32/ST-Link. Abre pelo ícone na área de trabalho; os dados ficam em `10_DT_Monitor/test_logs/`. Detalhes no `README.md` da pasta. |
| `12_analises/` | `metricas_sbcci.py`: as métricas das Tabelas I–III (T e σ, σ(VDD), ⟨AF⟩, horas equivalentes, R², resíduo, inclinação tardia com Newey–West) calculadas do mesmo jeito para as corridas do artigo e para as runs do D&T Monitor. Reproduz os valores publicados, menos a inclinação tardia do bang-bang (ver o README da pasta). |

## Como os dados batem com o artigo

Valores recalculados a partir dos CSVs desta pasta:

| | Bang-bang | PID |
|---|---|---|
| Média / σ de T_DUT (corrida inteira) | 107.73 / 2.64 °C | 117.04 / 1.25 °C |
| Média / σ de VCCINT (corrida inteira) | 1.2988 V / 6.1 mV | 1.2967 V / 3.6 mV |
| R² do slack ~ T, V (t ≥ 1 h) | 92.11 % | 59.23 % |
| σ do resíduo (t ≥ 1 h) | 0.904 cnt | 0.726 cnt |

A Tabela II do artigo bate com a corrida inteira. A Tabela III bate com t ≥ 1 h.

## Pontos a verificar antes da versão D&T

1. **Setpoint do forno.** O artigo diz 80 °C nas duas corridas. O log PID mostra setpoint de
   83 °C (média medida de 83.02 °C) e fonte em 1.45 V nos terminais (VCCINT ≈ 1.297 V). Na corrida
   bang-bang, a temperatura do ar do forno não foi registrada.
2. **Janela das estatísticas.** O método diz que a primeira hora é excluída. A Tabela III segue
   isso, mas a Tabela II usa a corrida inteira. Com t ≥ 1 h, o PID tem σ(T) = 0.93 °C e
   σ(V) = 2.7 mV, e a razão de σ(V) bang-bang/PID passa de ~1.7× para ~2.2×. O ΔT = 9.37 °C da
   versão final (texto e Fig. 2) já é o de t ≥ 1 h, enquanto as médias da Tabela II dão 9.31 °C.
3. **Fator de aceleração.** A Tabela I (711 h / 1182 h) usa o AF da temperatura média. O texto
   define o AF médio ao longo da trajetória, e a Tabela II reporta esse valor (31.1 / 51.3), que
   daria 718 h / 1184 h.
4. **Ganhos do PID.** O artigo atribui Kp = 2.78, Ki = 1.06×10⁻³ e Kd = 5.0 ao SIMC. Mas o SIMC com
   τc = θ dá Kp = 2.78, Ki ≈ 2.3×10⁻³ e Kd = 0, exatamente os valores do cabeçalho de
   `09_apoio_nao_usado_no_artigo/forno_PID_vs_SIMC_100C/SIMC_PID_COMP_37.csv`. Os valores finais de Ki
   e Kd foram ajustados experimentalmente.
5. **Amostragem.** O artigo diz 1 Hz para tudo, mas a corrida bang-bang foi amostrada a cada 2 s.
6. **"Mesmo bitstream".** O coletor de 2025 lia pacotes de 8 bytes. O design de nov/2025, usado em
   jan/2026, envia 9 bytes (tem um byte de falha a mais). O sensor pode ser o mesmo, mas o bitstream
   provavelmente não é.
7. **Referência [10].** Os autores estão errados nas duas versões do PDF. O correto é Z. Li,
   Z. Huang, Q. Wang, J. Wang e N. Luo, *Sensors* 22(12):4439, 2022; a entrada corrigida está em
   `01_artigo/referencias.bib`. No texto, "Huang et al." deve virar "Li et al.".
8. **σ = 3.29 vs 0.40 °C.** Esse número, citado no `references.bib` do trabalho de Teoria da
   Informação, vem de `graficos.png`, um teste do TCC com o ar do forno a 100 °C. Ele não é do
   artigo.
9. **Cabeçalho dos logs ON-OFF.** Os CSVs bang-bang de jan/2026 trazem "PARÂMETROS PID" no
   cabeçalho por limitação do app na época. Isso foi corrigido depois, no commit `bff6174` em
   `origin/main`.

## Como rodar o aplicativo usado no artigo

O `run.sh` dessa época supõe que o `.venv` já existe. Na primeira vez, crie-o:

    cd 04_aquisicao/pid_2026-01_App_Nexys
    python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
    ./run.sh

É uma interface PySide6 que precisa do FPGA (com o bitstream de `06_`), do Arduino com
`PID_Controller.ino` e da fonte IT6502D. A corrida bang-bang de 2025 foi gravada com
`python3 collect.py` em `04_aquisicao/bangbang_2025_app_sbcci/`, que tem portas fixas em
`uart_reader.py`.

## Como rodar as análises

Dependências: `pandas`, `numpy`, `scipy` e `matplotlib`. O `requirements.txt` da pasta 03 serve
só para os scripts do degrau e não inclui `scipy`.

    cd 05_analise
    python3 analise_sbcci_vs_pid.py ../02_dados/pid_2026-01-10/TCC_SBCCI_COMP_ESTABILIZADO.csv \
                                    ../02_dados/bangbang_2025-04-07/SBCCI_TCC_COMP_ESTABILIZADO.csv
    python3 analise_normalizada.py  ../02_dados/pid_2026-01-10/TCC_SBCCI_COMP_ESTABILIZADO.csv \
                                    ../02_dados/bangbang_2025-04-07/aging-plot-semana1.csv

O `kl_benches.py` está como no projeto original e procura os CSVs em `../artigos/TCC vs SBCCI/`.
Para rodar aqui, ajuste os caminhos no topo do arquivo.

Os scripts das estatísticas finais do artigo (Newey–West, R² e AF) não estão no repositório. Eles foram reescritos em `12_analises/metricas_sbcci.py` (04/11/2026).

## O que ficou de fora

- `App_2Nexys`, criado em 16/05/2026, depois do artigo, e `App_FPGAging_Slack_Sensor`
  (UltraScale+). Nenhum dos dois foi usado no artigo.
- As análises do trabalho de Teoria da Informação sobre outro dispositivo (campanha de 214.6 h).
  Só a comparação KL/JS entre as bancadas usa estes dados.
- O rascunho JICS, que é a extensão do artigo do SBCCI 2025.
