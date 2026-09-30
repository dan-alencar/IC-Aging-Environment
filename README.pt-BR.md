# IC Aging Environment

*[Read in English](README.md)*

Um ambiente central de pesquisa para experimentos de envelhecimento acelerado (*burn-in*), caracterização e confiabilidade de circuitos integrados (CI) e FPGAs. Desenvolvido no **LESC — Laboratório de Engenharia de Sistemas de Computação, UFC** (Universidade Federal do Ceará).

---

## Links Rápidos de Documentação

Se você é novo no laboratório, comece por aqui:
- **[`docs/onboarding/onboarding.tex`](docs/onboarding/onboarding.tex)** (ou o compilado **[`docs/IC_Aging_Environment.pdf`](docs/IC_Aging_Environment.pdf)**) — Manual completo de 35 páginas cobrindo física do envelhecimento, RTL do sensor, arquitetura do software, protocolos seriais, configuração da bancada, execução de testes e análise de dados.
- **[`CONTRIBUTING.md`](CONTRIBUTING.md)** — Diretrizes para novos pesquisadores sobre padrões de código, higiene de dados e fluxo de trabalho.
- **[`ARCHITECTURE.md`](ARCHITECTURE.md)** — Decisões de projeto e invariantes arquiteturais.
- **[`PROTOCOL.md`](PROTOCOL.md)** — Protocolos de comunicação serial e formato dos pacotes.
- **[`CLAUDE.md`](CLAUDE.md)** — Guia rápido para assistentes de IA e referência rápida para desenvolvedores.

---

## Estrutura do Repositório

O repositório é organizado em domínios modulares e bem definidos:

```text
.
├── hardware/                    # Projetos digitais e RTL
│   ├── fpga/
│   │   ├── xilinx/              # Projetos Vivado
│   │   │   ├── nexys4_ddr/      # Digilent Nexys4 DDR (Artix-7 xc7a100t)
│   │   │   └── ultrascale_plus/ # UltraScale+ customizado (xcau15p) - SBCCI
│   │   └── intel/               # Projetos Quartus Prime
│   │       └── de10_lite/       # Terasic DE10-Lite (MAX10 10M50DA)
│   ├── common/                  # Módulos RTL compartilhados (sensores, filtros, UART)
│   └── asic/                    # Designs para PDKs ASIC (SkyWater 130nm, GF180, etc.)
│
├── firmware/                    # Firmware para microcontroladores
│   ├── thermal_chamber/         # Controladores de temperatura da estufa (PID e bang-bang)
│   ├── uart_router/             # Roteador de pacotes ESP32 (ponte CROC / STM32)
│   └── supervisory/             # Firmware supervisório STM32L4 (PMIC e display OLED)
│
├── software/                    # Aplicações desktop para host e instrumentação
│   ├── core/                    # Pacote Python compartilhado (ic_aging_core)
│   ├── apps/
│   │   ├── App_Nexys/           # App para 1 DUT (Nexys4 DDR)
│   │   ├── App_2Nexys/          # App para 2 DUTs simultâneos no mesmo forno
│   │   ├── App_CornerSweep/     # Ferramenta para varredura de limites de tensão
│   │   └── App_FPGAging_Slack_Sensor/ # App para UltraScale+ CROC e ponte STM32
│   └── launcher.py              # Launcher unificado em Qt
│
├── analysis/                    # Pós-processamento, modelagem e estatística
│   ├── notebooks/               # Jupyter notebooks interativos
│   ├── scripts/                 # Scripts para cálculo de aceleração de Arrhenius e degradação
│   ├── figures/                 # Gráficos gerados para publicações
│   └── teoria_da_informacao/    # Métricas de teoria da informação sobre dados de envelhecimento
│
├── data/                        # Dados experimentais e padrões
│   ├── README.md                # Padrões de cabeçalho e regras de nomenclatura
│   ├── sample_logs/             # Logs pequenos (<1MB) versionados no Git para testes
│   └── campaigns/               # CSVs de campanhas longas locais (ignorados pelo Git)
│
├── publications/                # Produção acadêmica do grupo
│   ├── papers/                  # Artigos de conferências e periódicos (SBCCI, JICS, IEEE)
│   ├── theses/                  # Trabalhos de Conclusão de Curso (TCC) e dissertações
│   ├── coursework/              # Relatórios e materiais de disciplinas
│   └── literature/              # Banco BibTeX (references.bib) e referências
│
└── docs/                        # Manuais de onboarding, protocolos e especificações
```

*(Nota: Atalhos como `vivado/`, `Arduino-ESP/`, `STM_FW_Aging/` e `Artigos/` na raiz são links simbólicos para manter total compatibilidade com scripts legados).*

---

## Início Rápido

### 1. Executando as Aplicações
Para abrir o launcher gráfico unificado a partir da raiz:
```bash
./run.sh
```

### 2. Compilando Bitstreams FPGA

Para **Nexys4 DDR (Artix-7)**:
```bash
cd hardware/fpga/xilinx/nexys4_ddr
scripts/check_layout.sh
scripts/create_project.sh
scripts/build_bitstream.sh --jobs 8
```

Para **UltraScale+ (SBCCI)**:
```bash
cd hardware/fpga/xilinx/ultrascale_plus
scripts/check_layout.sh
scripts/create_project.sh
scripts/build_bitstream.sh --jobs 8
```

---

## Política de Dados Experimentais

Para evitar sobrecarga no repositório Git, **arquivos CSV brutos de campanhas (>1 MB) nunca devem ser commitados**.
- Logs de experimentos locais são salvos em `test_logs/` ou `data/campaigns/` (preservados localmente no disco, ignorados pelo Git).
- Dados de campanhas publicados devem ser arquivados no **Zenodo** (gerando DOI) ou no storage do laboratório.
- Amostras pequenas para validação gráfica estão em `data/sample_logs/`.
