# Port MAX10 / DE10-Lite — Pesquisa de Sensor de Envelhecimento (Nova Linha)

*[Read in English](README.md)*

Este diretório é o espaço de trabalho para uma **linha de pesquisa nova e paralela**:
portar o sensor de envelhecimento por *slack* da implementação Artix-7/Artix
UltraScale+ deste repositório para um dispositivo **Intel MAX 10 (10M50DAF484C7G)**
em uma placa **DE10-Lite** (ou equivalente), usando **Intel Quartus Prime Lite** em
vez do Vivado.

Leia **[`docs/plano-port-max10.pdf`](docs/plano-port-max10.pdf)** (ou a fonte LaTeX,
`docs/plano-port-max10.tex`) primeiro — é o plano de projeto de fato: as trilhas de
estudo obrigatórias da Fase 0 (E1–E6), as seis frentes de implementação (F1–F6), o
cronograma de 16 semanas com portões de decisão, o registro de riscos e os critérios
de aceite de cada entregável. Tudo abaixo é andaime (*scaffolding*) para ajudar você a
começar a executar esse plano, não um resumo que substitui a leitura dele.

## Como isto se relaciona com o resto do repositório

**O restante deste repositório (tudo fora de `max10_port/`) é material de
referência para este branch, não uma base sobre a qual construir diretamente.** É a
implementação validada e publicada, em outro silício (Artix-7, planar 28 nm) e com
outra ferramenta (Vivado). Leia para entender *por que* a arquitetura tem a forma que
tem — a Seção 2 do documento de plano ("Diagnóstico técnico de portabilidade")
explica em detalhe o que se preserva e o que não se preserva. Não assuma que é
possível reaproveitar RTL, arquivos de restrição ou IP diretamente; o plano é
explícito sobre onde as plataformas divergem (granularidade do deslocamento de fase
de clock, telemetria PVT, memória de configuração, transporte).

Vale a pena ler antes de começar:
- **`../CLAUDE.md`** — mapa denso e preciso do código existente (em inglês).
- **`../docs/onboarding.tex`** — o manual de onboarding de 35 páginas (física do
  envelhecimento, RTL, software, protocolos) da implementação de referência (em
  inglês).
- **`../vivado/aging_study_nexys4ddr/`** — a implementação de referência específica
  que este port tem como alvo (conforme a Tabela 1 do próprio plano): sensor único,
  arquitetura de adder duplo (RCA), no branch `main`. Não os branches experimentais
  de multi-sensor ou cadeia de inversores.
- **`../vivado/aging_study_nexys4ddr/SENSOR_ARCHITECTURE.md`** — por que o sensor é
  construído da forma que é; o raciocínio aqui é exatamente o que a trilha E3 da Fase
  0 pede para ser re-derivado a partir do lado MAX 10.
- **`../App_Nexys/`** — a aplicação *host* de referência (protocolo, threads de
  trabalho, laço PID, registro em CSV) que a frente F4 (telemetria) precisará portar
  ou substituir.

## Estrutura

Seguindo a convenção sugerida pelo próprio documento de plano (Seção 6.2,
"Repositório e convenções"):

| Diretório | Propósito | Situação |
|---|---|---|
| `docs/` | Documentos próprios deste branch: o plano de projeto, e os artefatos das trilhas de estudo da Fase 0 e notas técnicas que a equipe produzir. | Documento de plano já presente |
| `hdl/` | Projeto Quartus Prime: RTL, restrições (`.sdc`, `.qsf`) e scripts de build. | Apenas andaime — veja `hdl/README.md` |
| `host/` | Software de aquisição do lado PC (protocolo, telemetria, registro, gráficos ao vivo). | Vazio — veja `host/README.md` |
| `analysis/` | Análise offline: decomposição de variância PVT, estimação de σ_resid, ajuste de modelo de degradação. | Vazio — veja `analysis/README.md` |
| `data/` | Dados brutos de campanha. Imutáveis após gravados — veja a exigência de proveniência de dados do plano (Seção 6.3). | Vazio — veja `data/README.md` |
| `minutes/` | Atas de reunião semanal (o plano exige que sejam versionadas, Seção 5.3). | Apenas modelo — veja `minutes/README.md` |

## Antes de escrever qualquer código

O plano é explícito, e vale repetir aqui: **a Fase 0 (quatro semanas, seis trilhas de
estudo em paralelo) é obrigatória e bloqueante.** Ninguém abre o Quartus antes de o
artefato escrito da própria trilha estar pronto e defendido. Se você está lendo este
arquivo porque quer começar pelo lado da FPGA, vá ler a Seção 3 de
`docs/plano-port-max10.pdf` primeiro.
