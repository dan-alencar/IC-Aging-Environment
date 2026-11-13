# 12_analises — métricas do SBCCI 2026 para a versão D&T

`metricas_sbcci.py` calcula as métricas das Tabelas I–III do SBCCI 2026 do mesmo jeito para as
duas corridas do artigo e para as runs novas do D&T Monitor (AU15P, arquitetura B). Só precisa
de numpy; o `.venv` do D&T Monitor serve.

    cd 12_analises
    ../10_DT_Monitor/.venv/bin/python metricas_sbcci.py --sbcci
    ../10_DT_Monitor/.venv/bin/python metricas_sbcci.py --dtm ../10_DT_Monitor/test_logs/<run>_dut0_frames.csv --slack last
    ../10_DT_Monitor/.venv/bin/python -m unittest test_metricas      # autoteste com dados sintéticos

`--slack last` usa o `slack_last` de cada janela, que equivale à varredura única por segundo
do SBCCI e é a comparação justa com o artigo. `--slack mean` usa a média das ~8000 varreduras
da janela. A diferença entre os dois mede o ganho da sobreamostragem, que é resultado novo.

## Validação contra o artigo (04/11/2026)

| | Bang-bang: script | Bang-bang: artigo | PID: script | PID: artigo |
|---|---|---|---|---|
| T_DUT média / σ (°C) | 107.73 / 2.64 | 107.73 / 2.64 | 117.04 / 1.25 | 117.04 / 1.25 |
| σ(VDD) (mV) | 6.1 | 6.1 | 3.6 | 3.6 |
| ⟨AF⟩ | 31.1 | 31.1 | 51.3 | 51.3 |
| Horas equivalentes, AF(⟨T⟩) | 710 | 711 | 1182 | 1182 |
| R² slack ~ T, V, t ≥ 1 h (%) | 92.11 | 92.1 | 59.23 | 59.2 |
| σ do resíduo (cnt) | 0.904 | 0.904 | 0.726 | 0.726 |
| Inclinação tardia (m-cnt/h) | −8.4 ± 4.9 | −6.5 | −5.35 ± 2.33 | −5.3 |

A inclinação tardia está definida como o coeficiente de t em slack ~ 1 + t + T + V, a partir de
12 h, com o erro padrão de Newey–West. O artigo não diz como ela foi calculada. Com essa
definição, o PID bate e o bang-bang não.

**A estimativa depende muito de onde a janela começa:**
- bang-bang: de −8.4 a −11.9 m-cnt/h para começos entre 10 e 14 h;
- PID: de −2.8 a −9.3 m-cnt/h.

Na versão D&T, vale fixar a janela antes de olhar os dados e mostrar essa sensibilidade (o
relatório do script já imprime). Com a sobreamostragem da run nova (`--slack mean`), o erro de
cada janela cai bastante, o que deve estreitar esses intervalos.
