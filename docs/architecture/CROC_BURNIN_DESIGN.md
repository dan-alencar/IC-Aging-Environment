# Burn-in do CROC com sensores de auto-tuning: design do aparato

**Rascunho 1, 2026-11-27.** Decisões tomadas com o usuário em 2026-11-27, em duas rodadas
(inclusão de cada melhoria; depois implementação). Nada aqui foi implementado ainda: este
documento é a especificação que os pacotes de trabalho (§6) seguem.

Objetivo: medir o envelhecimento do **processador** (CROC + CVE2, não o RCROC) em tempo real,
antes, durante e depois de um burn-in na RV02A, com os sensores de auto-tuning dentro do SoC e
o aparato corrigido pelos achados de três artigos do grupo:

| Sigla | Artigo | Achado usado aqui |
|---|---|---|
| [ST] | Nogueira et al., SBCCI 2025, *Auto-tuning aging sensor…* | sensor junto ao caminho; skew de 200–300 ps entre FF1 e FF2; desligar o sensor ocioso; failure catcher valida slack → 0 |
| [TC] | Alencar et al., SBCCI 2026, *Quantifying the effect of burn-in thermal control…* | o AF entregue segue a média do die (1,65× entre bancadas); a correção por T/V deixa um resíduo de 0,73–0,90 cnt a 1 Hz |
| [DT] | Alencar et al., D&T 2027, *Averaging time defines when…* | o piso de horas (0,040–0,25 cnt) define a duração da corrida, 4,5–7,6× o previsto por ruído branco; os degraus do laço externo coincidem com saltos no resíduo (piso 0,25 → 0,15 cnt mascarando-os); corrente e tensão da fonte são *bad controls* |

Os dados de 0,25 e 0,15 cnt são da PID-214 em [DT]; a duração 91–149 h também.

---

## 1. Decisões

| # | Item | Decisão |
|---|---|---|
| P1 | RTL base | **CROC98** (TVLSI---Slack-Scanner, Lucas) com peças do **croc-cve2-aging** (Alisson): cadeias de referência, MMCM único com as três armadilhas de silício já resolvidas e extrator de PnR fixo |
| P2 | Repositório | Payload do CROC no **repositório do colega** (TVLSI---Slack-Scanner), sobre o fbs; no IC-Aging, a bancada, o host, a análise e uma versão parcial adaptada (revisto em 2026-11-27, §6 e §13) |
| P3 | Clock | **Um perfil durante o burn-in**; os outros dois perfis só nos checkpoints antes/depois, trocados por JTAG |
| P4 | Cadência | **Uma varredura por minuto**, instrumento desligado entre varreduras |
| B1 | Controle térmico | **PI em cascata** na temperatura do die, no host; o PID do Arduino continua como laço interno |
| B2 | Aquecedor no die | **Laço rápido** de Tj pelo aquecedor, com o forno como bias |
| B3 | Checkpoints | Antes/depois completos; **diário na temperatura de estresse**, só com a tensão baixada para o nominal por poucos minutos |
| B4 | Eventos | **Mensagem de evento no protocolo fbs**, emitida por FPGA, STM32 e host |
| S1 | Referência | **Cadeias casadas por grupo, com polaridade alternada** |
| S2 | Termômetro local | **Um RO por grupo** e um junto das referências, ligados só na medida |
| S3 | Cadeia nula | **Uma por região de clock** que contém taps |
| S4 | Gating | **BUFGCE nos clocks de prova** (dpsclk e catcher) |
| A1 | Agregação | **Cada varredura inteira** vai ao host; as janelas são feitas no host |
| A2 | Hadamard ao vivo | **Indicativo, por grupo**: mostra HDEV e T_min; o operador decide |
| A3 | Relatório | **Relatório automático** com a Tabela 2 de [DT] e **regra rígida** de regressores |

### 1.1 O que é um perfil de clock (P3)

No CROC98 um perfil é o mesmo checkpoint roteado (mesmo placement, rotas e firmware) com só o
divisor do MMCM (frequência do CROC) e a fase do catcher trocados. Na AUBoard (-2-e) os perfis
são 35,294 / 48 / 60 MHz, com margem de setup do CROC de 41,43 / 20,36 / 0,47 % do período
(`TVLSI---Slack-Scanner/projeto/README.md`; `fpga/phase2/ARQUITETURA.md` §4).

Os perfis servem para:

- **calibrar o instrumento:** um ΔT no período deve deslocar a borda medida em ΔT, nos mesmos
  caminhos físicos;
- **chegar perto da falha funcional:** no perfil limite;
- **fazer o burn-in:** no perfil de ~20 %.

Na RV02A (-1-i) os três perfis **têm de ser derivados de novo** pelo mesmo critério (o maior
clock que atende ao alvo e fecha setup/hold do projeto inteiro). Os valores da -2-e não valem
(`croc-cve2-aging/00_CONTEXTO_DO_PROJETO.md` §4.1).

---

## 2. Arquitetura

```
PC (fbs-service + App_DT_Monitor, plugin ic_aging.croc_burnin)
 │  J9 / ST-LINK, 125 kbaud, frames fbs
 ▼
RV02A ── FPGA xcau15p-ffvb676-1-i ─────────────────────────────────────────────┐
 │  fbs_platform: router, SYSMON (Tj, VCCINT), t_ms, link counters, EVENT        │
 │     │ app stream (FPGA_APP)          │ RAW0 = console do CROC                  │
 │  fbs_croc_aging (payload)                                                    │
 │     ├─ CROC + CVE2 (firmware de carga fixa, hash no manifesto)               │
 │     ├─ scanner CROC98: 98 taps (IF 32, RF 32, OBI 15, UART 19)               │
 │     ├─ kit por grupo (IF, RF, OBI, UART): cadeia de referência + RO          │
 │     ├─ cadeias nulas: uma por região de clock com taps                       │
 │     ├─ aquecedor: banco distribuído, PWM lento, PI em malha sobre Tj         │
 │     └─ MMCME4_ADV único: soc_clk (perfil) | dpsclk (fine PS) ─BUFGCE─►        │
 │                          clk_catcher ─BUFGCE─►                               │
 └─ STM32 (autoridade de segurança, VCCINT via MYMGM1R) ──── Arduino + forno (PID)
```

- O CROC continua dono do console (RAW0, sem mudar o firmware). O scanner fala direto com o
  `fbs_platform` como `FPGA_APP`. Isso resolve dois problemas do CROC98:
  - o top de campanha não liga o STM32 à UART externa (`projeto/README.md`, item 4);
  - a coleta dependia de sessão JTAG (B6 do croc-cve2-aging).
- **MMCM único** para soc_clk, dpsclk e catcher. Com dois MMCMs, cada relock sorteia a origem
  de fase entre 5 estados e o ruído fica ~1000× maior que a erosão procurada
  (`00_CONTEXTO` §4.3). As três armadilhas de §4.4 entram como requisito do RTL:
  - `MMCM_CLKOUTn_USE_FINE_PS` em cada saída que se move;
  - reset do MMCM gerado no domínio do clock de entrada;
  - armar os holders só depois do lock.
- O `fbs_platform` roda a 100 MHz do oscilador da placa. O cruzamento com o scanner segue o
  CROC98, que já tem a UART de instrumentação em clock independente de 100 MHz
  (`ARQUITETURA.md` §3).

---

## 3. Lado do sensor (RTL)

### S1. Cadeias de referência casadas, polaridade alternada

- Uma cadeia sintética por grupo (IF, RF, OBI, UART), com atraso roteado próximo ao da
  mediana dos taps qualificados do grupo (alvo ±10 %, conferido no STA pós-roteamento).
  Fica colada ao cluster do grupo e usa o mesmo tipo de sensor (FF1/FF2/XOR/catcher/holder),
  como mais um canal do scanner (ids 98–101).
- **Estado fora da medida:** entrada parada num nível. A polaridade se inverte a cada
  `ref_flip_s` (padrão 3600 s), para o BTI DC não se acumular só de um lado. Cada inversão é
  um `EVENT`.
- **Medida:** a cadeia só alterna durante a varredura que a mede. Medir a cada
  `ref_period_scans` varreduras (padrão 10, ou seja ~10 min) mantém a atividade abaixo de ~1 %,
  como o `ref_period_s` do `fbs_aging`.
- **Limite:** no forno nada fica sem estresse. A referência separa o efeito da **atividade**
  (HCI, BTI AC) e cancela T, V, gradiente e clock. Não separa o BTI DC da temperatura. O
  relatório deve dizer isso.
- **Origem:** as cadeias ref18/51/190 do croc-cve2-aging (o coeficiente térmico escala com o
  comprimento: ref190 9,5–10,8 ps/°C, commit `e6aff51`), dimensionadas para cada grupo.

### S2. Ring oscillators locais

- Cinco ROs: um colado a cada cluster e um junto das referências. Cada um tem enable, contador
  de 32 bits e janela fixa (padrão 10 ms, em clocks de 100 MHz da plataforma).
- **Ligados só na janela de medida**, no início de cada varredura, para não envelhecerem nem
  aquecerem o die. Ainda assim envelhecem (~0,02 % do tempo): a calibração contra o SYSMON se
  repete antes e depois (B3).
- **Calibração:** forno uniforme, aquecedor desligado, CPU em carga fixa, três patamares de
  temperatura no checkpoint inicial. Ajuste linear contagem → °C por RO, com resíduo
  publicado.

### S3. Cadeias nulas

- Um sensor sobre caminho quase vazio (FF de lançamento → um LUT → FF1/FF2) em cada região de
  clock que contém taps. Ele mede só o skew dpsclk/soc_clk e o drift do MMCM e da
  distribuição de clock até aquela região.
- A lista de regiões sai do placement: um script pós-roteamento gera os LOCs e o build falha
  se faltar nula em alguma região com taps.

### S4. Gating dos clocks de prova

- `BUFGCE` em dpsclk e em clk_catcher. Fora da varredura, FF2, catcher e holders param. O FF1
  fica no soc_clk, porque amostra o tap e faz parte da carga do caminho.
- Sequência de cada varredura:
  1. habilitar os BUFGCE;
  2. esperar `settle_cycles`;
  3. armar os holders, só depois disso (mesma lógica da armadilha 3 de §2);
  4. varrer;
  5. voltar a fase à origem por PS reverso, conferida pela contagem de passos;
  6. desabilitar os BUFGCE.
- **[VERIFY G1]** O estado de fine phase shift do MMCM se mantém com o BUFGCE desligado (o
  MMCM continua rodando; só a árvore a jusante para). Confirmar em simulação com o modelo
  MMCME4_ADV e em silício: a borda da cadeia nula deve repetir entre varreduras com e sem
  gating no meio.
- **Duty do instrumento:** com X = 100k ciclos por fase, uma varredura leva ~5,4 / 2,9 / 1,9 s a
  35,3 / 48 / 60 MHz. É uma extrapolação linear das medidas com X = 4M ciclos por fase
  (216,0 / 116,7 / 74,8 s, `evidencias/phase2/bancada_20261116/LEIA-ME.md`). A 1 varredura por
  minuto, isso dá ~3–9 %.

### Correções do CROC98 que entram no port

Os itens 1–3 estão em `TVLSI---Slack-Scanner/projeto/README.md` e no relatório de
16/11 (§8); o item 4 está em `projeto/README.md`, §1 do relatório e `ARQUITETURA.md` §3.

1. `STATUS` empacota `error_code` em `[5:3]`, mas o firmware lê `[6:4]`: uma perda de lock
   pode sair como erro zero. Corrigir dos dois lados, com teste.
2. O contador de progresso de 16 bits é ambíguo com firmware rápido: passa a 32 bits.
3. As janelas do holder e do traço diferem (arm em WARM, contagem em MEASURE): uniformizar
   ou documentar, com regressão.
4. O firmware de carga do burn-in fica fixo (o compacto melhorou a repetibilidade, mas mudou
   a borda observada em alguns caminhos) e o seu hash vai para o manifesto.

### PnR fixo

Usar a abordagem V19 do `fbs_aging`: LOC/BEL **e** rotas das células de medida **e** rotas dos
clocks de medida. Só as células deixava 6 ps de drift de skew. O build falha se a lista de
sensores divergir da lista congelada. O extrator do Alisson (B5: redução de 5×, "não basta")
é ponto de partida, não o resultado.

---

## 4. Bancada

### B1. PI em cascata sobre a temperatura do die

- **Onde:** no host, no sequenciador de run plan do fbs (`fpgaging_bsp/service/runplan.py`),
  que hoje já faz o laço externo de die para o App_DT_Monitor. Entra como
  `stress.outer_loop.mode: pi`, configurado pelo plan do IC-Aging. O modo atual (`step`) fica
  para reproduzir as campanhas antigas. Hoje esse laço já usa a média do intervalo, mas ainda
  muda 1 °C de uma vez: é o mesmo problema corrigido nos apps Nexys em 2026-11-27.
- **Antes de sintonizar:** ensaio de degrau do setpoint do forno com o die em carga fixa
  (`dt_monitor/oven_test.py` como base), ajuste FOPDT die × setpoint e sintonia SIMC, como no
  PID do forno. Referência para o chute inicial: na PID-214, 0,97–1,81 °C de die por °C de ar
  ([DT]); a constante do die é de ~1300 s (`ideas_au15p_burnin_2026-11-10.md` §2.2).
- **Lei de controle:**
  - entrada: Tj do SYSMON filtrada (5–10 min);
  - saída: setpoint contínuo com taxa ≤ 0,1 °C/min, limitado à faixa do forno, com
    anti-windup;
  - sem banda morta;
  - integrador congelado na primeira hora (soak).
- **Com o aquecedor (B2):** o PI do forno deixa de seguir a Tj e passa a manter o **duty médio
  do aquecedor** no meio da faixa (padrão 50 %). Quem segura a Tj é o aquecedor; o forno dá o
  bias que mantém o aquecedor com autoridade nos dois sentidos.
- **Critério de aceite:** a média de Tj fica a ≤ 0,9 °C do alvo (orçamento de 5 % no AF a
  115 °C e 0,7 eV, Eq. 3 de [TC]/[DT]). O desvio de Hadamard de Tj não pode mostrar degraus.

### B2. Aquecedor no die

- Banco de LUT/FF alternando, **modulado pelo número de células ativas** (enable em código
  termômetro, constante no tempo), e não por PWM no tempo. *Correção do rascunho:* um PWM de
  1 Hz modularia o VCCINT e a Tj **dentro** de uma varredura (2–5 s), e cada fase seria medida
  com o aquecedor num estado diferente, o que distorce a borda. O duty só muda **entre**
  varreduras; durante a varredura ele fica congelado. Fica **distribuído** pelo die, longe dos
  clusters de taps, para não criar gradiente nos sensores; o modo gradiente está fora deste
  design.
- **PI do aquecedor no payload**, em ponto fixo, a 10 Hz sobre a Tj do SYSMON. O alvo e os
  limites de duty vêm do host. Se o host ficar mudo por `heater_host_timeout_s` (padrão 10 s), o
  duty desce a zero em rampa.
- **Segurança:** o STM32 continua sendo a autoridade. Se ele cortar o VCCINT, o aquecedor
  morre junto. O payload também limita o duty por um teto que o host só pode baixar.
- **Orçamento de corrente: corte de 3,0 A (decisão de 2026-11-27).** O DS931 não especifica
  corrente máxima de operação: manda usar o XPE ou o `report_power`. O módulo MYMGM1R admite
  16 A (`IOUT_TRIP_CAP_MA`), então o limite de 3 A é uma escolha de proteção da placa.
  - O `report_power` do `au15p_multi_B` dá 1,111 A a 0,85 V e Tj = 115 °C. É uma estimativa,
    não uma medida.
  - **[VERIFY H1]** Rodar o `report_power` do payload CROC completo, sem o aquecedor, no ponto
    de estresse (§9). A fuga cresce com V e T, e o folgado para o aquecedor é 3 A menos esse
    valor. Confirmar na bancada pelo `READ_IOUT`.
- **[VERIFY H2]** A latência da Tj: o `fbs_aging` usa `SYSMON_AVG_LOG2 = 10`. Conferir se a
  média do SYSMON deixa banda para um PI a 10 Hz.

### B3. Checkpoints

| Quando | O que | Duração |
|---|---|---|
| Antes | (1) calibração dos ROs: 3 patamares, forno uniforme, aquecedor desligado; (2) corners T × V nos 3 perfis, trocados por JTAG; (3) **linha de base** no perfil de burn-in, em condição de estresse com tensão nominal, longa o bastante para medir o piso (HDEV de 1–4 h, regra de [DT]) | horas a dias |
| Diário | mesma Tj; VCCINT cai para o nominal; varreduras por `cp_daily_min` (padrão 5 min); volta ao estresse. O aquecedor compensa a queda de autoaquecimento, e a Tj fica constante | minutos |
| Depois | (1) **recuperação**: varreduras de 1/min mantidas por `post_recovery_h` depois de tirar o estresse; (2) corners e perfis como antes; (3) recalibração dos ROs | horas |

Cada checkpoint é um `EVENT` com início e fim. O relatório separa as varreduras de checkpoint
das de estresse e registra a recuperação acumulada (soma das janelas a V nominal).

### B4. Mensagem de evento

- Nova mensagem de plataforma no fbs, `EVENT` (`t_ms`, `source`, `code`, `value`). Os códigos
  iniciais são:
  - `SETPOINT`, `REPROGRAM`, `PROFILE`, `MMCM_RELOCK`, `LOCK_LOSS`;
  - `PHASE_HOME_FAIL`, `REF_FLIP`, `CHECKPOINT_BEGIN`, `CHECKPOINT_END`;
  - `HEATER_LIMIT`, `RECONNECT`, `OPERATOR_NOTE`.
- O FPGA marca sozinho lock, relock, falha de origem de fase e inversão de referência. O STM32
  já tem `SAFETY_EVENT` e `RAIL_FAULT`, que entram no mesmo fluxo. O host grava os seus no
  mesmo log, com o `t_ms` estimado pelo `TIME_SYNC`.
- É uma mudança de SPEC no **fpgaging-board-support**: revisão do SPEC, `messages.yaml`,
  bindings, testes, e atualização do ARCHITECTURE.pdf (capítulo, status, iteração, `\docrev`).

---

## 5. Aquisição e análise

### A1. Uma varredura inteira por mensagem

Proposta de mensagens para `protocol/messages.croc.yaml`, cujo dono é o repositório do colega
(contrato, §13), com cópia fixada no IC-Aging. Os números são distintos dos do `fbs_aging`
(0x40–0x43, 0x50–0x51), para os dois payloads conviverem no mesmo host:

| Tipo | Nome | Conteúdo |
|---|---|---|
| 0x44 | `CROC_SCAN` | `scan_id u32`, `t_start_ms`, `t_end_ms`, `profile u8`, `x_cycles u32`, `n_phases u16`, `ps_step_fs u32`, `fw_hash u32`, `cpu_progress u32`, `selftest_fail u16`, `lock_loss u16`, `kind u8` (estresse ou checkpoint), `flags` |
| 0x45 | `CROC_SENSORS` | `scan_id`, `first_id u8`, `n u8`, e por sensor: `edge u16`, `act_total u32` (satura), `act_min u16`, `dt_first_ms u16`, `tj_first u16`, `vcc_first u16`, `flags u8` (sem alarme, sem atividade, saturado, limitado pelo catcher). São ~17 B por sensor, 12 sensores por frame |
| 0x46 | `CROC_RO` | `scan_id`, `gate_ms u16`, contagens dos 5 ROs |
| 0x47 | `CROC_HEATER` | `t_ms`, `duty u8`, `target_c`, `tj_c`, `limit_flags` (1 Hz) |
| 0x48 | `CROC_INFO` | versão do RTL, mapa de canais (grupo, tipo: tap/ref/nula, região de clock), perfil, `ref_flip_s`, `ref_period_scans` |
| 0x52–0x55 | comandos | `CROC_SET_SCAN` (X, cadência), `CROC_START_SCAN`, `CROC_SET_HEATER` (alvo, teto, timeout), `CROC_SET_REF` (período de inversão e de medida) |

- **Tráfego:** ~110 canais (98 taps, 4 referências, as nulas) × 17 B, mais o cabeçalho, dá
  ~2 kB por varredura, ou seja ~0,03 kB/s a 1/min. Em rajada, 2 kB ocupam o link de 125 kbaud
  por ~0,16 s (10 bits por byte), uma vez por minuto.
- O host agrega as janelas (min, max, média, histograma) na escala que quiser. Nada se perde
  no FPGA.

### A2. Resíduo, diferencial e HDEV ao vivo

- **Resíduo por sensor:** borda − f(Tj_first, VCCINT_first, RO do grupo), por mínimos quadrados
  num trecho de calibração (linha de base ou janela deslizante; fica registrado qual).
- **Diferencial:** tap − referência do grupo − nula da região. É a grandeza principal; o
  resíduo só por T/V é mostrado ao lado, para comparação.
- **No App_DT_Monitor**, por grupo (mediana dos sensores qualificados de IF, RF, OBI e UART;
  o sensor isolado sob demanda):
  - HDEV do resíduo e do diferencial;
  - piso na faixa de 1–4 h;
  - drift β;
  - T_min ≈ 2·3√2·piso/|β|, a regra de [DT];
  - aviso quando o drift fica resolvido a 3σ.

  Quem decide parar é o operador. O `dt_monitor/stats.py` é o ponto de partida.
- **Qualificação:** canal sem atividade, limitado pelo catcher ou com `act_total` saturado não
  entra na mediana (regras de C6 do croc-cve2-aging e da qualificação do CROC98). No relatório
  de 16/11, só 75 dos 98 canais foram qualificados.

### A3. Relatório e regra de regressores

- `analysis/croc_burnin/report.py` gera, no fim da corrida e por demanda, Markdown e PDF com os
  5 itens da Tabela 2 de [DT]:
  1. trajetória de Tj e V (média, desvio, erro contra o alvo);
  2. ⟨AF⟩ com a faixa de Ea e a configuração;
  3. Allan/Hadamard de Tj, do resíduo e do diferencial;
  4. drift com o conjunto de regressores;
  5. tempo de detecção com o método.

  Inclui também a recuperação acumulada nos checkpoints e os eventos. Reaproveita o
  `analysis/dt2027/sbcci_metrics.py`.
- **Regra rígida:** a estimativa oficial só aceita {Tj do SYSMON, VCCINT do SYSMON, RO local}.
  Corrente e tensão da fonte e o ar do forno só aparecem numa tabela de sensibilidade (como a
  Fig. 3b de [DT]). O módulo de análise recusa qualquer outro regressor na estimativa principal.

---

## 6. Pacotes de trabalho

**Divisão (decisão de 2026-11-27, revista):** o payload do CROC (CROC98 + instrumentação) é
migrado para a RV02A **pelo colega, no repositório dele** (TVLSI---Slack-Scanner), que passa a
consumir o fbs como submódulo, como o IC-Aging, podendo reaproveitar peças do `fbs_aging`. O
IC-Aging fica com a bancada, o host, a análise e a integração dos experimentos, e pode ter uma
**versão parcial adaptada** do payload para testar essa integração (WP1p). O fbs fica com a
plataforma, o protocolo comum, o STM32 e o sequenciador (fase **P10** do fbs). A §13 tem o
contrato entre os repositórios.

| WP | O quê | Repositório | Depende de | Aceite |
|---|---|---|---|---|
| 0 | Fase 0 na RV02A: MMCM único com 3 saídas e fine PS só no dpsclk; BUFGCE nas duas saídas de prova; `report_clock_interaction` soc_clk → dpsclk "Clean/Timed" | TVLSI (colega) | — | as três perguntas de `00_CONTEXTO` §6 respondidas; G1 em simulação |
| 1 | CROC98 sobre o `fbs_platform` (`fbs_croc_aging_top`); console em RAW0; correções 1–3; `slm_regs` (SLM1) no lugar do monitor OBI legado; alarme de margem (SLM4); carga dirigida para os taps não qualificados (metodologia do CROC §4) | TVLSI (colega) | 0 | elabora; cocotb: scan completo em simulação reduzida; ≥ 90/98 taps qualificados |
| 1p | Versão parcial adaptada no IC-Aging: poucos taps, um kit, as mensagens do contrato. É só para testar a integração com host, análise e bancada enquanto o WP1 avança | IC-Aging, `src/rtl/fbs_croc_aging/` | 2 | o plugin do WP5 roda contra ela no simulador do fbs e numa placa |
| 2 | Mensagens `CROC_*` do contrato (§13) | TVLSI (dono do arquivo), espelhado no IC-Aging | — | `generate.py --check` nos dois lados |
| 3 | Kits de instrumentação: referências com polaridade alternada, ROs, nulas por região, gating; PnR fixo à moda V19; controlador de DRP do MMCM (perfil e SLM3). Os blocos genéricos ficam em `src/rtl/aging_instruments/` no IC-Aging, usados pelo `fbs_aging` e oferecidos ao colega | IC-Aging (blocos) + TVLSI (integração) | 1 (ou 1p) | build reproduzível; WNS ≥ 0 no funcional; censo de sensores igual à lista |
| 4 | Aquecedor + PI no payload + heartbeat do host; bloco genérico em `aging_instruments/` | IC-Aging (bloco) + TVLSI (integração) | 3, **orçamento de corrente H1 medido** | sim: degrau de alvo, timeout do host; bancada: Tj segura ±0,5 °C a 1 Hz |
| 5 | Host: plugin `ic_aging.croc_burnin` (`derive` por varredura, janelas, eventos) e run plans com pré, estresse, checkpoints e pós; ensaio de degrau para identificar a planta do PI | IC-Aging, `software/apps/App_DT_Monitor/` | 2, P10 | simulador do fbs com modelo do payload; pytest |
| 6 | Análise: resíduo, diferencial, HDEV ao vivo, relatório, regra de regressores, **verificação do oscilador por software (M8)** e **estimador de espaço de estados (M1a)**, validado em dados simulados com drift conhecido | IC-Aging, `analysis/croc_burnin/`, `dt_monitor/stats.py` | 5 | relatório gerado num log simulado; a regra recusa corrente da fonte; M1a recupera o drift simulado dentro do intervalo |
| 7 | Bancada: perfis derivados na -1-i, calibração dos ROs, linha de base, burn-in piloto | laboratório | 3–6, P10 | piso medido; checkpoint diário sem degrau visível na HDEV |
| 8 | Firmware do CROC: controlador de AVS, ações de proteção, modos de ocioso (SLM2, SLM6) | TVLSI (colega) | 1, P10 | sim e bancada pela metodologia `ic_aging_avs.md` |
| 9 | Modos de estresse do `fbs_aging` (`alternate` / `static0` / `static1` / `measure-only`), para o experimento `ic_aging.burnin` | IC-Aging, `src/rtl/fbs_aging/` | — | cocotb por modo; `AGING_SET_MODE` com o campo novo |

**No fbs (fase P10):** revisão 3 do SPEC com:
- `EVENT`;
- `AVS_CONFIG` e `VCCINT_REQUEST` (SLM2), com o firmware do STM32;
- os limites em conflito (§9.3): `DIE_TEMP_CAP_CC`, `VCCINT_SENSE_TOL_MV`, os exemplos com
  `die_c: 130`, e `VCCINT_HARD_MIN_MV` diante do VDRINT de 0,68 V;
- no `runplan.py`: `outer_loop.mode: pi`, o papel `control` para placas, o registro da
  metodologia na sessão e os passos `vmin_search` / `fmax_search` (SLM5).

**Caminho crítico:** TVLSI 0 → 1 → 3, junto com P10, e depois a bancada (WP7). O IC-Aging não
espera o colega: o WP1p, o WP5, o WP6 e o WP9 andam em paralelo.

## 7. Pendências abertas

- **H1 e H2** (aquecedor) e **G1** (gating), acima.
- **Perfis na -1-i:** a margem e a frequência de cada perfil só existem depois do build na
  RV02A.
- **Ponto de estresse:** fixado em §9 (Tj lida de 110 °C, VCCINT lido de 0,95 V). Isso resolve
  a contradição do croc-cve2-aging entre Tj = 125 °C (`seguranca.tcl`) e 100 °C
  (`COMO_RODAR`). O perfil de burn-in ainda tem de ser escolhido junto com esse ponto: no
  build do Alisson, a 125 °C a margem de E1 fica negativa (−158 ps, commit `e6aff51`). A CPU
  não pode falhar no meio do estresse por temperatura em vez de por envelhecimento.
- **Os 23 canais não qualificados** do CROC98 e a dependência de workload (relatório de 16/11,
  §9): o firmware de carga do burn-in precisa estar fixado antes da linha de base.
- **BTI DC nas referências:** a polaridade alternada só equilibra o estresse; não o elimina
  (S1).
- **Uma placa só:** a replicação fica fora deste rascunho, como em [DT].

---

## 8. Overhead esperado das adições

**Base de comparação:** o CROC98 portado para o fbs sem as adições.

**Fontes dos números medidos:**

- `bitstreams/au15p_multi_B_utilization.rpt`: o dispositivo tem 77 760 LUTs, 155 520 FFs,
  84 BUFGCE e 3 MMCMs.
- `bitstreams/au15p_multi_B_power_Tj115.rpt`: VCCINT de 1,111 A a 0,85 V, sendo 1,045 A
  estáticos e 0,066 A dinâmicos.
- `croc-cve2-aging/experimentos/cve2_vs_ibex/RESULTADO_2026-08-11.md`: o topo CROC+CVE2 usa
  6 061 LUTs e 2 919 FFs.

As demais linhas da tabela são **estimativas**, a confirmar no primeiro build (WP1/WP3).

| Recurso | Adição | Estimativa | Observação |
|---|---|---|---|
| Área | 4 referências + ~4–8 nulas | ~10 canais a mais no scanner, ~+10 % do scanner | o custo por canal vem dos contadores (atividade, mínimo, instante e Tj/V no 1º alarme), estimados em ~150 FF por canal |
| Área | 5 ROs | ~350 LUT, ~200 FF (<0,5 %) | RO de poucos LUTs + contador de 32 bits |
| Área | gating, inversão de polaridade, mensagens | desprezível | no UltraScale+ o BUFG já é um BUFGCE; usa-se o pino CE |
| Área | **aquecedor** | **dimensionado pela potência**, provavelmente a maior adição (ordem de 10 % ou mais da fábrica) | o tamanho sai do `report_power` para o orçamento H1, não de uma meta de área |
| Potência | instrumento (sensores, ROs) | desprezível perante 1,27 W estáticos | clocks de prova ativos ~3–9 % do tempo, ROs ~0,02 % |
| Potência | aquecedor | com o corte de 3,0 A e ~1,1–1,6 A de base (a fuga sobe com V; confirmar no H1): ~1,4–1,9 A, ou ~1,3–1,8 W a 0,95 V | dá mais autoridade que o corte de 2 A, mas o limite passa a ser a Tj (§9), não a corrente |
| Timing do CROC | todas | ~0 | as adições não tocam os caminhos do CROC; o carregamento dos taps já existe no CROC98 |
| CPU | todas | 0 | o scanner é externo ao core e o firmware de carga não muda |
| Link | varreduras + aquecedor + eventos | ~0,3 % do link em média | ~2 kB por minuto, e rajada de ~0,16 s |
| Disco | log | ~3 MB/dia binário, ~10–15 MB/dia em texto | uma corrida de 150 h passa de 50 MB: vai para Zenodo ou NAS, pela regra do repo |
| Ruído | diferencial tap − ref − nula | até √3 ≈ 1,7× o ruído branco em escala curta | só compensa onde o piso é de modo comum, em horas. A referência medida a cada ~10 min limita o diferencial a τ ≳ 10–20 min |
| Tempo de bancada | checkpoints | pré ~1,5–2 dias, pós ~1–1,5 dia, diário 5 min (0,35 % do estresse) | o pré é dominado pela linha de base (≥ 5 janelas de 4 h para a HDEV de 1–4 h) e pelos patamares do forno (τ ≈ 1307 s, atraso 150 s; `croc-cve2-aging/PLANO_VALIDACAO_PRE_BURNIN.md`) |

---

## 9. Limites de operação pelo DS931, com margem

Fonte: AMD DS931 *Artix UltraScale+ FPGA Data Sheet*, **revisão 1.9 (2026-05-19)**, lida em
2026-11-27 nas páginas
[Absolute Maximum Ratings](https://docs.amd.com/r/en-US/ds931-artix-ultrascale-plus/Absolute-Maximum-Ratings),
[Recommended Operating Conditions](https://docs.amd.com/r/en-US/ds931-artix-ultrascale-plus/Recommended-Operating-Conditions),
[System Monitor Specifications](https://docs.amd.com/r/en-US/ds931-artix-ultrascale-plus/System-Monitor-Specifications)
e [Quiescent Supply Current](https://docs.amd.com/r/en-US/ds931-artix-ultrascale-plus/Quiescent-Supply-Current).

### 9.1 O que o fabricante especifica

| Grandeza | Recomendado (-1-i) | Máximo absoluto | Observação |
|---|---|---|---|
| VCCINT | 0,825 / 0,850 / **0,876 V** | **1,000 V** | |
| VCCINT_IO | 0,825 / 0,850 / 0,876 V | **1,000 V** | na RV02A estão na mesma rede que o VCCINT, e "the lower absolute voltage specification always applies" (nota 4) |
| VCCBRAM | 0,825 / 0,850 / 0,876 V | **1,000 V** | idem |
| Tj | −40 a **100 °C** (grau I) | **125 °C** | nota 1: exposição prolongada aos máximos absolutos "might affect device reliability" |
| Erro do sensor de Tj do SYSMON, referência interna | ±3,5 °C de −55 a 110 °C; **±5 °C de 110 a 125 °C** | — | a RV02A usa a referência interna (`formula_id` 1, SPEC §4) |
| Erro do sensor de VCCINT do SYSMON, ref. interna, 0,72–1,2 V | ±1,0 % até 100 °C; **±2,0 %** de −55 a 125 °C | — | com a autocalibração ligada (nota 4) |
| Corrente de VCCINT | sem máximo especificado | — | o DS931 manda usar XPE/`report_power`. O ICCINTQ típico do XCAU15P é de 372–424 mA (85 °C, dispositivo em branco) |

O burn-in é, por definição, **sobre-estresse em relação ao recomendado**: Tj acima de 100 °C e
VCCINT acima de 0,876 V. "Cabe na especificação" quer dizer aqui: abaixo dos máximos
absolutos, com margem para o erro das medidas e para as excursões do controle.

### 9.2 Ponto de estresse e cortes

**Temperatura.** O valor real pode estar até 5 °C acima do lido (erro do SYSMON acima de
110 °C). Com mais 3 °C de margem (o mesmo ajuste que a nota 13 do DS931 usa no exemplo), o
**corte em leitura** fica em 125 − 5 − 3 = **117 °C**. Somando ~±1 °C de controle e o tempo de
reação do corte, o **alvo em leitura** fica em **110 °C**.

| | Leitura do SYSMON | Pior caso real |
|---|---|---|
| Alvo de burn-in | 110 °C | 115 °C |
| Corte (STM32 `die_temp_max` por `SET_LIMITS`, e plan `limits.die_c`) | 117 °C | 122 °C |

**Tensão.** A trim fecha sobre o VCCINT do SYSMON, que pode ler até 2 % abaixo do real. Com
~10 mV de ripple e transientes (o aquecedor muda a carga) e 20 mV de margem:
setpoint ≤ (1,000 − 0,020 − 0,010)/1,02 ≈ **0,95 V em leitura**.

| | Leitura | Pior caso real |
|---|---|---|
| Setpoint de estresse | 0,950 V | ~0,97 V, mais o ripple |
| Teto de setpoint (`vccint_soft_max_mv`) | 0,950 V | — |
| Disparo por sobretensão no SYSMON | ≤ 0,975 V (ver o conflito C3) | ≤ ~0,995 V |

**Corrente.** Corte em **3,0 A** (`iout_trip_ma = 3000`), abaixo do teto do módulo (16 A). A
3 A e 0,95 V entram ~2,85 W em VCCINT. Quem limita a autoridade do aquecedor é a Tj; o corte de
corrente protege a placa contra latch-up e runaway térmico da fuga.

**Custo em aceleração.** Passar de 115 °C para 110 °C reduz o AF a 0,7 eV por um fator de 1,31.
O próprio erro do SYSMON (±5 °C) já dá ±32 % de incerteza no AF absoluto a 110 °C. O relatório
(A3) deve publicar o ⟨AF⟩ com essa faixa, além da faixa de Ea.

### 9.3 Conflitos com a configuração atual da bancada

| # | Onde | Hoje | Problema | Proposta |
|---|---|---|---|---|
| C1 | fbs SPEC §8.9, `DIE_TEMP_CAP_CC` | 140 °C | acima do máximo absoluto de 125 °C; o texto diz que "115 °C deixa 25 °C de margem", mas a margem real até o máximo absoluto é de 10 °C menos o erro do sensor | baixar o teto de compilação para ≤ 120 °C (mudança no SPEC do fbs, decisão do usuário). Até lá, usar `SET_LIMITS` com 117 °C em toda corrida |
| C2 | `bench/burnin_115C_0v85.yaml` (e o exemplo do SPEC) | `limits.die_c: 130` | acima de 125 °C | 117 °C no plan do CROC |
| C3 | fbs `VCCINT_SENSE_TOL_MV` | 50 mV | a 0,95 V de setpoint, o disparo por SYSMON só ocorre em leitura de 1,000 V, até ~1,02 V real, acima do máximo absoluto | reduzir para 25 mV (mudança de firmware no fbs), ou manter 50 mV e limitar o setpoint a 0,925 V |
| C4 | fbs `VCCINT_HARD_CAP_MV` / arm | 1300 mV com arm | permite passar do máximo absoluto de 1,000 V; é decisão anterior, para sobre-estresse deliberado | para esta campanha, `vccint_soft_max_mv = 950` em toda corrida; o teto de compilação fica como está |
| C5 | fbs SPEC V1 | aberto | — | **fechado pelo DS931 1.9:** VCCINT, VCCINT_IO e VCCBRAM têm o mesmo máximo de 1,000 V, então `VCCINT_SAFE_MAX_MV = 1000` está correto |
| C6 | croc-cve2-aging, campanha | ponto de ensaio declarado de 1,200 V | 20 % acima do máximo absoluto | não usar no burn-in do CROC; registrar a decisão lá |

O DS931 só cobre a FPGA. A placa dentro do forno tem outros limites (STM32, módulo MYMGM1R,
conectores), e o forno continua mais frio que o die. Isso fica para o HIL checklist do fbs.

---

## 10. Metodologia e decisões de 2026-11-27 (terceira rodada)

A metodologia de cada experimento fica no repositório do fbs, em `docs/methodology/`:

- `README.md`: regras comuns M1–M10;
- `ic_aging_croc_burnin.md`: este experimento;
- `ic_aging_burnin.md`: as cadeias do `fbs_aging`.

Ela é escrita e congelada antes da corrida. Este documento diz *como o aparato é construído*;
a metodologia diz *como o experimento é conduzido e julgado*.

Entram por decisão do usuário, implementadas ou anotadas na metodologia:

| Item | Onde fica |
|---|---|
| Plano de análise pré-registrado, com o arquivo de metodologia gravado na sessão | M1; `runplan.py` |
| Placa de controle fora do estresse (papel `control` no run plan) | M2; hoje não há placa disponível (B e C bloqueadas, V12) |
| Replicação em ≥ 3 placas estressadas | M3; hoje só a A |
| Modos de estresse por placa (`active` / `halted` no CROC) | M4; clock enable do CROC fora das varreduras |
| Ea medido com duas temperaturas (100 e 110 °C em leitura) | M5 |
| UPS, alarmes, retomada, relógio do host com NTP | M6 |
| Verificação do oscilador da placa **só por software**: inclinação de `t_board_ms` contra `t_host_s` | M8; regressor da tabela de sensibilidade |
| Carga dirigida para os 23 taps não qualificados (aceite: ≥ 90/98) | metodologia do CROC, §4 |
| **Troca de perfil por reconfiguração do MMCM em execução** (DRP + restauração da fase fina, conferida nas cadeias nulas), no lugar do JTAG | P3 passa a ter essa opção depois de validada em WP0/WP1; até lá, JTAG só antes/depois |

**Fora por decisão do usuário** (não mexer na parte física da placa nem do setup de burn-in):
cabeça térmica no lugar do forno, clock de referência externo e referência externa ou ADC de
precisão para o SYSMON.

---

## 11. Ganchos de SLM e AVS na arquitetura (2026-11-27)

O objetivo é que o mesmo bitstream do burn-in já sirva aos experimentos de SLM e AVS
(metodologia `docs/methodology/ic_aging_avs.md` no fbs). Os ganchos abaixo entram no
`fbs_croc_aging` e no fbs. As **políticas** (quando baixar a tensão, quando reduzir a frequência)
ficam no firmware do CROC e no host, não no hardware.

### SLM1. O CPU lê os próprios sensores

- Periférico OBI `slm_regs` no `user_domain` do CROC, **só leitura para o CPU**, com:
  - por canal: última borda válida (`u16`), flags de qualificação e `scan_id`;
  - Tj e VCCINT no primeiro alarme;
  - por grupo (IF, RF, OBI, UART): a **margem mínima** sobre os taps qualificados, ou seja
    borda − limiar do grupo;
  - status `SCAN_DONE`, com interrupção.
- O CPU pode **pedir** uma varredura (`SCAN_REQ`). O scanner continua com um dono só: a agenda
  do host tem prioridade, e o pedido do CPU entra na fila.
- **Timing:** a auditoria do CROC98 achou o caminho limitante do projeto no monitor OBI legado
  (`i_user/u_sensors/obi_rdata_o_reg`, `ARQUITETURA.md` §4). O `slm_regs` registra o dado de
  leitura (um ciclo a mais de latência) e substitui esse monitor, em vez de somar a ele.
- **Conferência:** em cada varredura, o host compara o que leu pelo fbs com o que o CPU leu
  pelo OBI (o firmware ecoa um resumo no console RAW0). Uma divergência é um evento.

### SLM2. Caminho de AVS limitado: o payload pede, o STM32 decide

- Proposta de mensagens novas no fbs (é mudança de SPEC):
  - `AVS_CONFIG` (host → STM32): habilita por corrida e fixa `min_mv`, `max_mv`, `step_mv`,
    `min_interval_ms` e `max_slew_mv_s`;
  - `VCCINT_REQUEST` (`FPGA_APP` → STM32): `mv` e `reason`.
- O STM32 aplica só com o AVS habilitado, dentro de [`min_mv`, teto em vigor] e respeitando
  passo e intervalo. Cada mudança aplicada vira `EVENT` com a origem. Com o AVS desabilitado, o
  pedido é recusado e contado. **O STM32 continua sendo a autoridade de segurança**: o pedido
  nunca passa de `vccint_soft_max_mv` (M9).
- O **controlador** de AVS roda no firmware do CROC: lê o SLM1 e escreve num registrador de
  pedido do `slm_regs`, que o payload converte em `VCCINT_REQUEST`. O laço fica todo na placa,
  sem o PC, que é a narrativa de SLM ("o processador gerencia a própria margem").

### SLM3. Ação de frequência

- O controlador de DRP do MMCM, o mesmo da troca de perfil em execução (P3), fica acessível ao
  host e ao CPU (`slm_regs`, registrador `PROFILE_REQ`).
- Sequência de cada troca:
  1. pausar o scanner;
  2. reconfigurar os divisores;
  3. esperar o relock;
  4. restaurar a fase fina;
  5. conferir as cadeias nulas;
  6. emitir `EVENT PROFILE`.
- **[VERIFY F1]** O CROC tem de sobreviver à troca sem reset, porque o soc_clk para durante o
  relock. Caso contrário, a troca exige reset do CPU, e isso entra na metodologia.

### SLM4. Alarme de margem em hardware

- Comparador no payload: se a margem mínima de algum grupo cair abaixo do limiar programado
  pelo host, ele gera ao mesmo tempo uma interrupção no CPU e um `EVENT` no fbs. É o ponto onde
  as ações de proteção (metodologia, E5) se ligam.
- O limiar vem da calibração de Vmin (SLM5). O hardware só sinaliza; a ação é política de
  firmware.

### SLM5. Busca de Vmin e Fmax como passos do run plan

- Passos novos no sequenciador do fbs, `vmin_search` e `fmax_search`:
  - `vmin_search` desce a VCCINT em passos de `step_mv`;
  - `fmax_search` sobe o perfil por SLM3.

  Em cada ponto, são feitas N varreduras e o autoteste do CPU. O passo para na **primeira falha
  funcional**: autoteste falho, progresso do CPU parado, ou erros de CRC no link da plataforma
  (porque a VCCINT também alimenta a lógica do fbs). Em seguida restaura o ponto anterior, faz
  reset do CPU e registra tudo.
- **Piso de segurança:** o DS931 rev. 1.9 (DC Characteristics) dá **VDRINT = 0,68 V (mín.)**:
  abaixo disso, "configuration data might be lost", o bitstream se perde e o watchdog do fbs
  teria de reprogramar. O `VCCINT_HARD_MIN_MV` do SPEC (700 mV) fica só 20 mV acima, menos que o
  erro do SYSMON (±2 %, ~14 mV) somado à exatidão do módulo. Por isso o **piso da busca é de
  0,750 V em leitura**, e abaixo disso a busca para e registra "Vmin < 0,75 V" (censurado).
- Usados nos checkpoints antes e depois do burn-in: o deslocamento de Vmin e Fmax com o
  envelhecimento é a grandeza central de AVS, e a leitura de cada sensor no Vmin calibra o
  limiar do SLM4.

### SLM6. Estado ocioso do CPU selecionável

- O clock enable do CROC (já necessário para o modo `halted`, metodologia M4) e um modo de
  ocioso no firmware: `WFI` com clock parado, ou um laço com operandos complementares que
  equilibra o BTI DC (a mesma ideia da polaridade alternada das referências). O modo vai no
  registro de cada varredura.

### Onde cada gancho é feito

Pela divisão da §6:
- SLM1, SLM4 e o controlador de DRP do SLM3 vão no WP1 e no WP3 (repositório do colega; o DRP é
  bloco genérico do IC-Aging);
- SLM2 e SLM5 vão na fase P10 do fbs (SPEC, firmware do STM32, sequenciador);
- SLM6 e as políticas de AVS e proteção vão no WP8 (firmware do CROC, repositório do colega).

---|---|
| 1 | `slm_regs` (SLM1) substituindo o monitor OBI legado; SLM4 |
| 2 | `AVS_CONFIG`, `VCCINT_REQUEST` (SLM2) no SPEC e no firmware do STM32 (fbs) |
| 3 | controlador de DRP compartilhado por P3 e SLM3 |
| 5 | passos `vmin_search` / `fmax_search` (SLM5) no sequenciador |
| novo 8 | firmware do CROC: controlador de AVS, ações de proteção, modos de ocioso |

---

## 12. Fora de escopo por ora

- **ASIC:** tanto o CROC com SLM quanto o RCROC ficam para um futuro mais distante. O CROC
  original é do PDK aberto IHP SG13G2, e o RCROC tem um tapeout planejado (B-77). **A plataforma
  principal é a RV02A.** O RTL novo continua independente de tecnologia onde isso não custa nada,
  mas não se faz trabalho específico de ASIC agora.
- **Mudanças físicas** na placa ou no setup de burn-in (§10).

---

## 13. Contrato entre os repositórios

Proposta, a combinar com o colega:

- **O payload do CROC é do repositório dele.** O IC-Aging não depende de nenhum arquivo do
  repositório dele para funcionar, só do contrato abaixo, numa versão fixada.
- **Mensagens:** o colega é dono de `protocol/messages.croc.yaml` (tipos 0x44–0x48 e 0x52–0x55,
  §5, distintos dos do `fbs_aging`, para os dois conviverem num host só). O IC-Aging mantém uma
  cópia com a origem e o commit anotados e confere com `generate.py --check`. Uma mudança no
  contrato sobe a versão no `CROC_INFO` (`rtl_version`), e o plugin recusa versões que não
  conhece.
- **Mapa de canais:** fica no `CROC_INFO` (grupo, tipo tap/ref/nula, região de clock), e não em
  arquivos combinados à mão. O host lê da placa.
- **Blocos de instrumentação** (`aging_instruments/`, WP3 e WP4): ficam no IC-Aging e são
  oferecidos como RTL simples, sem IP, como o `fbs_platform`. O colega pode copiá-los com a
  origem anotada ou usar o IC-Aging como submódulo. Não é obrigatório: ele pode ter os seus,
  desde que reportem pelas mesmas mensagens.
- **Bitstream:** o host identifica o bitstream pelo `USR_ACCESS` e pelo hash no manifesto
  (prática C4 do croc-cve2-aging), venha ele de qual repositório vier.
- **Limitação:** o TVLSI---Slack-Scanner hoje é só local, sem remoto. Para o IC-Aging fixar uma
  versão do contrato, ele precisa de um remoto, ou de um commit exportado com hash.
