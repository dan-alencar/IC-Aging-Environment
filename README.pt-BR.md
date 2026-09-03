# IC Aging Environment

*[Read in English](README.md)*

Um ambiente *hardware-in-the-loop* para experimentos de envelhecimento acelerado
(*burn-in*) de FPGAs. O sistema controla a temperatura do forno por PID, programa e
monitora um sensor de *slack* (margem temporal) embarcado que acompanha a degradação
de temporização, e registra tudo para análise posterior. Desenvolvido no
**LESC — Laboratório de Engenharia de Sistemas de Computação, UFC** (Universidade
Federal do Ceará).

Se você é novo aqui, este arquivo é o mapa. Para se aprofundar, veja:
- **[`docs/onboarding.tex`](docs/onboarding.tex)** (ou o PDF compilado
  [`docs/IC_Aging_Environment.pdf`](docs/IC_Aging_Environment.pdf)) — o manual
  completo de 35 páginas (em inglês): física do envelhecimento, RTL, arquitetura de
  software, protocolos, preparação de estação de trabalho do zero, execução de
  experimento e análise de dados.
- **[`ARCHITECTURE.md`](ARCHITECTURE.md)** — intenção de projeto por trás de cada
  subsistema (em inglês).
- **[`PROTOCOL.md`](PROTOCOL.md)** — todo protocolo serial, byte a byte (em inglês).
- **[`CLAUDE.md`](CLAUDE.md)** — referência de trabalho para assistentes de IA
  (Claude Code); também é um mapa denso e preciso do código para humanos com pressa
  (em inglês).

> **Nota de idioma:** os documentos técnicos aprofundados acima permanecem em inglês
> — é o idioma em que já estão escritos, revisados e usados no dia a dia do
> laboratório. Este README e a documentação de orientação do port para MAX 10 são
> bilíngues; o restante é referência técnica em inglês mesmo.

## Branches — qual arquitetura de sensor está onde

Este repositório hospeda mais de uma variante do sensor de envelhecimento. Escolha o
branch de acordo com o que você está fazendo:

| Branch | Arquitetura | Situação |
|---|---|---|
| `main` | **Sensor único, adder duplo (RCA).** Um caminho crítico de somador *ripple-carry*, amostrado pelo sensor de metaestabilidade `modern_sensible`, com um segundo somador idêntico (`adder_canary`) como canário de erro funcional. É a arquitetura validada e publicada (SBCCI 2025/2026). | Referência / produção |
| `inverter-chain-sensor` | Mesma arquitetura de sensor único, mas o caminho crítico é uma cadeia de inversores parametrizável (`not_series`) em vez de um somador — apenas temporização, sem canário funcional. | Experimental |
| `experimental-multi-sensor` | Quatro instâncias independentes de `rca_sensor_channel` compartilhando um único controlador de varredura de fase, reportando todos os canais a cada ciclo. Protocolo novo, interface multi-canal nova. | Experimental, ainda sem validação em hardware |
| `max10-de10lite-port` | Uma **linha de pesquisa separada**: portar este sensor para um dispositivo Intel MAX 10 (placa DE10-Lite) com Quartus Prime. Tudo em `max10_port/`; o restante deste repositório fica ali como material de referência. Veja `max10_port/README.pt-BR.md` naquele branch. | Nova equipe, escopo exploratório |

A menos que você esteja trabalhando especificamente em uma das variantes
experimentais ou no port para MAX 10, o branch que você quer é o `main`.

## O que há neste repositório

| Caminho | O que é |
|---|---|
| `vivado/aging_study_nexys4ddr/` | Projeto Vivado para a placa **Nexys4 DDR (Artix-7, xc7a100t)** — o alvo de hardware principal e mais bem documentado. RTL puro, sem *block design*. |
| `vivado/sbcci_fpga_aging/` | Projeto Vivado para o alvo **SBCCI / Artix UltraScale+ (xcau15p)** — placa customizada, roteia UART tanto para a FPGA do sensor quanto para um STM32. |
| `App_Nexys/` | Aplicação desktop (PySide6) para um único DUT Nexys4 DDR: PID do forno, controle de fonte, gráficos ao vivo, registro em CSV. A aplicação de referência — leia esta primeiro. |
| `App_2Nexys/` | Igual à `App_Nexys`, duplicada para dois DUTs Nexys4 DDR independentes, com controle de tensão de fonte independente por DUT. |
| `App_FPGAging_Slack_Sensor/` | Aplicação desktop para o alvo SBCCI/UltraScale+; roteia tráfego serial entre a FPGA e uma ponte STM32. Deve ser executada isoladamente (família de hardware diferente). |
| `App_CornerSweep/` | Ferramenta de caracterização de bancada (não é uma aplicação de *burn-in*): varre VCCINT por *corners* fixos e, em cada um, dá passos finos de tensão até localizar a fronteira de falha. |
| `STM_FW_Aging/` | Firmware do STM32L4R9 (projeto STM32CubeIDE) para o microcontrolador supervisório do alvo SBCCI — controle do PMIC, display OLED. |
| `Arduino-ESP/` | Sketches Arduino/ESP32: controlador PID do forno, roteador UART (caminho SBCCI), ferramenta de teste de degrau FOPDT, sniffer de UART. `legacy/` guarda versões superadas. |
| `Artigos/` | Artigos: publicações e rascunhos do grupo (`Artigos_GSEM/`), materiais do TCC (`Artigos_TCC/`), e referências de revisão bibliográfica organizadas por tema (`Artigos_refs_SBCCI_2025/`). |
| `docs/` | O manual de onboarding (fonte LaTeX + PDF compilado). |
| `run.sh` / `launcher.py` | Lançador raiz — um diálogo para escolher qual aplicação Nexys4 executar. |

## Início rápido

```bash
./run.sh
```

Isso mostra um diálogo para escolher entre `App_Nexys` (1 DUT), `App_2Nexys` (2 DUTs)
e `App_CornerSweep` (caracterização de tensão). Cada aplicação gerencia seu próprio
ambiente virtual Python (criado automaticamente na primeira execução) e suas próprias
conexões de hardware — nada é compartilhado entre elas. `App_FPGAging_Slack_Sensor`
tem hardware diferente e é executada isoladamente:

```bash
cd App_FPGAging_Slack_Sensor && ./run.sh
```

Para a primeira preparação da estação de trabalho (instalar o Vivado, regras udev
para dispositivos seriais/JTAG, identificar qual `ttyUSB*` é qual), veja o Capítulo 8
de `docs/onboarding.tex` — é a parte mais importante de ler antes de mexer no
hardware.

## Compilando um bitstream de FPGA

```bash
cd vivado/aging_study_nexys4ddr    # ou vivado/sbcci_fpga_aging
scripts/check_layout.sh            # checagem de sanidade, não precisa do Vivado
scripts/create_project.sh          # gera build/*.xpr a partir do RTL/XDC versionado
scripts/build_bitstream.sh --jobs 8
```

A saída gerada (`build/`, `artifacts/`) nunca é versionada — tudo o que é necessário
para reproduzir um bitstream está no controle de versão como fonte (RTL, XDC, XCI).

## Sem suite de testes automatizada

Toda validação é feita contra hardware real — forno, DUT, fonte. Não há CI. Na
dúvida, leia a seção "No automated test suite" do `CLAUDE.md` antes de supor que
algo deveria ter testes unitários.

## Contribuindo

Ainda não há um processo formal de contribuição — este é o código de um laboratório
de pesquisa. Se você é novo na equipe: leia `docs/onboarding.tex` de ponta a ponta
antes da sua primeira sessão com hardware, e confirme com quem orienta sua trilha
antes de alterar `fixed_pnr_constraints.xdc`, invariantes documentados em
`SENSOR_ARCHITECTURE.md`, ou qualquer coisa que já esteja executando uma campanha de
vários dias.
