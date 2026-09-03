# hdl/ — Projeto Quartus Prime (MAX10 / DE10-Lite)

*[Read in English](README.md)*

**Nada aqui é um projeto funcional ainda.** Isto é andaime (*scaffolding*): uma
estrutura de arquivos e um conjunto de scripts de build que espelham o padrão já
usado pelos projetos Vivado em `../../vivado/aging_study_nexys4ddr/` e
`../../vivado/sbcci_fpga_aging/` — o objetivo é que, assim que as frentes F1/F2
produzirem RTL e restrições reais, `scripts/create_project.sh` e
`scripts/build_bitstream.sh` funcionem do mesmo jeito que aqueles scripts Vivado:
reprodutível, a partir de arquivos de texto versionados, sem saída de build
commitada.

## Dispositivo alvo

- Peça: **10M50DAF484C7G** (Intel MAX 10, 50K elementos lógicos, encapsulamento FBGA
  484 pinos, *speed grade* 7).
- Placa: DE10-Lite (ou placa equivalente que carregue essa peça).
- Ferramenta: Intel Quartus Prime **Lite** Edition. **Fixe a versão exata** usada em
  todo o projeto e registre-a neste arquivo assim que escolhida — a Seção 6.1 do
  documento de plano explica o porquê (otimizações do *fitter* mudam entre versões e
  invalidam silenciosamente a reprodutibilidade de compilação, da qual o Gate A
  depende).

<!-- TODO quando decidido: registre a versão exata do Quartus Prime aqui, ex.: "23.1std.1". -->

## Estrutura esperada (preencher conforme F1/F2 avançam)

```
hdl/
├── src/
│   ├── rtl/            # Fontes RTL — espelhar a divisão de módulos de
│   │                    #  vivado/aging_study_nexys4ddr/src/rtl/: top/, aging_sensor/, uart/, display/
│   └── constraints/     # .sdc (exceções de temporização) e atribuições de pino/posição
├── scripts/
│   ├── check_layout.sh       # checagem de sanidade, não precisa do Quartus (já funciona)
│   ├── create_project.tcl    # cria o .qpf/.qsf a partir dos arquivos-fonte (modelo)
│   ├── create_project.sh     # wrapper fino em torno de create_project.tcl (já funciona)
│   └── build_bitstream.sh    # executa o fluxo completo de compilação (modelo)
├── build/                # saída do Quartus -- ignorada pelo git, nunca commitar
└── artifacts/            # .pof/.sof finais -- ignorados pelo git, nunca commitar
```

## Vocabulário Vivado → Quartus, do documento de plano (Seção 2.4)

| Vivado / Artix-7 | Quartus / MAX10 |
|---|---|
| `PSEN`, `PSINCDEC`, `PSDONE` | `phasestep`, `phaseupdown`, `phasecounterselect`, `phasedone` |
| `DONT_TOUCH`, `KEEP` | `preserve`, `noprune`, `keep`, `dont_merge` (atributos de RTL) |
| Restrições `LOC` / `BEL` | `set_location_assignment LC_X..Y..N..` no `.qsf` |
| Device View do Vivado | Chip Planner do Quartus |
| MMCM | PLL (`ALTPLL` com reconfiguração dinâmica de fase, ou Altera PLL + Altera PLL Reconfig) |
| XADC | Núcleo ADC SAR via IP Modular ADC Core (Platform Designer), modo diodo de sensor térmico |

A tabela do documento de plano (Seção 2.4, "Correspondência de recursos entre as
plataformas") é a versão de referência; esta é uma cópia rápida de consulta, não um
substituto.

## `scripts/create_project.tcl` — o que está lá e o que não está

O script Tcl neste diretório é um script real e mínimo de criação de projeto Quartus
Prime (`quartus_sh -t create_project.tcl`) para a peça `10M50DAF484C7G`, seguindo a
mesma convenção de sobrescrita por variável de ambiente usada pelos scripts
`create_project.tcl` do Vivado (`VIVADO_PROJECT_NAME`, `VIVADO_PART`, etc. lá;
`QUARTUS_PROJECT_NAME`, `QUARTUS_PART`, etc. aqui). Ele tem marcações `# TODO`
explícitas nos pontos em que precisa das listas de arquivos RTL/QSF/SDC que só
existirão quando F1/F2 as produzirem — não vai criar um projeto útil até que esses
TODOs sejam preenchidos, mas o andaime ao redor deles (criação do projeto, atribuição
de peça, definição do módulo de topo) é real.
