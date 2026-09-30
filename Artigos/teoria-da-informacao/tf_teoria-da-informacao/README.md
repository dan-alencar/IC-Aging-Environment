# TF — Teoria da Informação (TIP7266, PPGETI/UFC, 2026.1)

Sensor de envelhecimento on-chip tratado como **canal de comunicação ruidoso**:
entropia, informação mútua, divergência KL/JS, capacidade e estimação (CRLB,
Bayes, Kalman) aplicadas aos logs de slack de uma FPGA Artix-7 em burn-in.

Entregável avaliado: **`latex/main_pt.pdf`**. Apresentação: `latex/seminar.pdf` (completa).
Versões da defesa de 22/08/2026: `latex/seminar_15min.pdf` (recorte de 10 slides apresentado) e
`latex/entregue_2026-08-22/trabalho_final.pdf` (artigo entregue, sem as seções KL/JS e ICA). As fontes
mantêm a versão completa, que serve de base para a extensão do artigo GSEM para o IEEE D&T.
Versão em inglês (`latex/main.pdf`) está desatualizada — ver `CLAUDE.md`.

## Reproduzir

Requisitos: `python3` (≥ 3.10) e TeX Live com `latexmk`
(`texlive-latex-extra texlive-lang-portuguese texlive-science latexmk`).

```bash
make            # cria .venv, roda a análise, gera figuras/valores e compila os PDFs
make analysis   # só o pipeline Python
make pdf        # só o LaTeX
make clean      # remove auxiliares do LaTeX e caches Python
```

Os números do texto **nunca** são digitados à mão: o pipeline em `analysis/`
gera `latex/generated/values.tex` (macros `\val…`) e `latex/figures/*.pdf`.
Para mudar um número, altere o script e rode `make` de novo.

## Estrutura

| Caminho | Conteúdo |
|---|---|
| `00_Work_Summary.md` … `06_*.md` | planejamento, metodologia e contribuição (comece pelo `00`) |
| `analysis/` | pipeline Python (`tier1_pipeline.py`, `kl_benches.py`, `ica_separation.py`, `kalman_rul.py`, `make_figures.py`) |
| `latex/` | artigo (`main_pt.tex`), slides (`seminar.tex`), seções, tabelas, figuras e valores gerados |
| `artigos/` | dados brutos (CSV) e artigos de referência do grupo |
| `material/` | material da disciplina |
| `review/` | requisitos do TF e rodadas de revisão |
| `App_Nexys/` | apenas dados e logs de aquisição (CSVs e capturas do teste de corners); o software em si é o `/App_Nexys` da raiz do repositório |

Dados: o dispositivo A (`artigos/Tentative_1_20260524_203756.csv`) alimenta
todas as métricas; o dispositivo B (`artigos/TCC vs SBCCI/`) é usado só na
comparação KL entre bancadas. Não misture os dois.
