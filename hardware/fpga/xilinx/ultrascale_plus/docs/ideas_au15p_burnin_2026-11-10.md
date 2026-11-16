> **Note (2026-11-16):** the colleague's ideas for the AU15P burn-in, written on 2026-11-10 (in
> Portuguese), moved here from branch `dt2027`. A thinking document, not an approved plan. Some ideas
> are already in `fbs_aging_top` (the unstressed reference chain, the ring oscillators, fixed placement);
> paths such as `src/rtl/multi/` refer to his worktree, which was never committed.

# Ideias de melhoria e inovação para o burn-in das AU15P

Escrito em 10/11/2026, logo depois de congelar o `au15p_multi_B.bit` (9 cadeias, posição e
rota fixas). É um documento de pensamento, não um plano aprovado: cada ideia traz o que ganha,
o que custa (RTL, app, firmware, bancada) e o que precisa ser conferido antes. Os números do
sistema atual vêm do `src/rtl/multi/LEIAME.md` (worktree) e dos corners de 07 e 09/11.

## 0. O problema de fundo: a deriva de 16 nm é menor que um passo do sensor

| Grandeza | Valor hoje | Origem |
|---|---|---|
| Passo do sensor (fase fina do MMCM) | 19,84 ps (VCO 900 MHz / 56) | `clk_wiz_0`: 100 MHz × 9 |
| Caminho medido nas placas (`au15p_hub_B`) | 3,30 ns, 72 % roteamento | checkpoint roteado |
| Cadeias da variante | 1,96 a 7,49 ns | tabela do LEIAME |
| Resolução relativa de um passo | 0,6 % (3,3 ns) a 0,27 % (7,5 ns) | 19,84 ps / atraso |
| Deriva medida na A, run de 37,4 h a 1,00 V e ~113 °C | ≤ 0,5 contagem nos corners depois | `corners_20261109.txt` |
| Estado da arte em 16 nm FinFET (ROs, Zynq US+) | < 0,1 % de deriva de frequência em 1000 h a 100 °C | Sobas & Marc, 2022/2024 (ver §10) |

Contas de ordem de grandeza: com lei de potência BTI (t^0,2), 0,1 % em 1000 h vale ~0,05 % em
37 h; a 115 °C em vez de 100 °C (Ea 0,7 eV) o fator é ~2,3×, então ~0,1 %. Em 3,3 ns isso são
~3 ps (0,17 passo); na cadeia de 1024 CARRY8 (7,5 ns), ~7 ps (0,4 passo). Bate com o que vimos.
Dobrar a duração da run rende só 2^0,2 ≈ 1,15× em BTI; passar de 37 h para 200 h rende ~1,4×.

Conclusão que organiza todo o resto: **o gargalo é resolução e estatística, não tempo de
forno.** A ordem de alavancas é:

1. resolução e método de medida (§4): ganhos de 2× a 100×;
2. estruturas certas e referência de modo comum (§1), e modos de estresse que separem mecanismos (§3);
3. disposição no die (§2), que vale para atribuição e variação espacial, não para sensibilidade;
4. aceleração (§5): a tensão já está no máximo absoluto (1,00 V); a temperatura rende no máximo ~1,7×.

## 1. Trocar ou ampliar as cadeias (as "estruturas de estresse")

### 1.1 Cadeia de comprimento zero (referência de modo comum)

O sensor mede a cadeia contra o clock de fase deslocada. Envelhecem também o FF1, o BUFG, a
árvore de clock e o MMCM. Uma "cadeia" só com o registrador de estímulo ligado direto ao sensor
(sem lógica) mede esse modo comum. Todas as outras passam a ser lidas como diferença contra
ela. Custo: uma cadeia a mais no `fpga_multi_top` (tipo novo no `CHAIN_KIND`). Ganho: separa
"a cadeia envelheceu" de "o sensor envelheceu", que hoje é indistinguível.

### 1.2 Cadeia só de roteamento

72 % do caminho das placas é fio. Uma cadeia de LUT1 (buffers) com rota fixa longa e sinuosa
(muitos PIPs, poucos LUTs) isola a interconexão (buffers de rota e chaves) da lógica. Com a
`FIXED_ROUTE` já dominada, dá para desenhar rotas com tipos de fio diferentes (curtos, longos,
verticais, horizontais) e comparar. Sobas & Marc separam lógica de roteamento com ROs de
geometrias diferentes; aqui a separação seria direta, por construção.

### 1.3 Cadeia em modo duplo: RCA no estresse, oscilador em anel na medida

É a ideia de maior ganho em resolução sem abandonar o RCA. Um mux na entrada do bit 0 escolhe:

- **modo estresse** (como hoje): `op_a[0]` alterna a cada ciclo e o sensor de folga mede;
- **modo oscilador**: a saída da cadeia volta invertida ao bit 0; a cadeia vira um RO cujo
  período é 2 × (atraso + volta). Um contador de 1 s lê a frequência.

Com a cadeia de 1024 CARRY8, o RO oscila a ~60 MHz; em 1 s são 6 × 10^7 contagens, quantização
de 2 × 10^-8. Na prática a resolução fica limitada por T e V (10^-5 a 10^-4), ainda 50 a 500×
melhor que um passo de 19,84 ps. A mesma estrutura dá então duas leituras: a folga do sensor
(a grandeza que interessa ao projetista: margem de timing) e a frequência (a grandeza de
referência da literatura). Cuidados: o mux acrescenta um LUT fixo no caminho; no modo
oscilador a cadeia se estressa de outro jeito (HCI a 60 MHz), então o modo tem de ser curto
(por exemplo 100 ms por janela de 1 s) ou, de propósito, contínuo numa cópia; a realimentação
precisa de um ciclo de apropriação limpo (sem glitch) ao trocar de modo. Custo: RTL médio,
quadro novo com a contagem, app.

### 1.4 Osciladores em anel convencionais como acompanhantes

Mesmo sem o modo duplo, ROs clássicos (LUT) espalhados pelo die são baratos (um LUT por
estágio, um contador) e são o padrão da literatura de 16 nm. Dois usos distintos, os dois
válidos:

- **medidores** com habilitação só na medida (1 % de duty): estressam pouco e servem de
  termômetro distribuído depois de calibrados contra o SYSMON (ver §2.2);
- **estressados** em oscilação contínua: estrutura de HCI puro, para comparar com as cadeias.

### 1.5 Outros recursos do die

Caminhos de DSP48E2 (cascata PCIN/PCOUT) e de BRAM (leitura) usam transistores e layouts
diferentes dos CLBs. Uma cadeia de cada diz se a lógica do CLB é representativa do die. O
AU15P tem DSP e BRAM de sobra. Custo: RTL baixo; vale só se houver tempo de run para mais
cadeias (a varredura termina na cadeia com mais folga; a de DSP seria longa, sem problema).

### 1.6 Variantes da mesma cadeia: pino do LUT e geometria

A entrada de um LUT6 tem atrasos diferentes por pino (A1 é o mais lento). Com `LOCK_PINS`
fixo, duas cadeias de LUT iguais, uma entrando sempre por A1 e outra por A6, perguntam se o
envelhecimento está no mux interno do LUT ou na entrada. Também: cadeia de CARRY8 numa coluna
só (vertical, como hoje) contra a mesma cadeia espalhada em colunas (roteamento entre
blocos). Custo baixo depois da §2.1.

### 1.7 O que já existe no repositório e pode ser reaproveitado

- `inverter-chain-sensor` (Danilo, 02/09): cadeia de 50 inversores no lugar do RCA.
- `src/rtl/aging_sensor/nand_series.v`: cadeia de NAND.
- `experimental-multi-sensor`: 4 canais RCA com protocolo próprio (tem o defeito do `error_flag`).

Nenhum é compatível com o app sem adaptação, mas as estruturas valem como cadeias novas
dentro do `fpga_multi_top` (o quadro 0x03 já tem o campo tipo).

### 1.8 Trocar o RCA por um circuito "de verdade"

Um datapath pequeno (um multiplicador, um núcleo RISC-V mínimo) com o sensor no caminho
crítico real responde a crítica de que RCAs sintéticos não representam um projeto. Custo alto
(RTL, caminho crítico instável sem posição fixa) e ganho incerto em sensibilidade. Fica como
opção para depois, se a revista pedir realismo.

## 2. Disposição no die

### 2.1 Floorplan deliberado, por pblock

Hoje a posição é fixa, mas foi escolhida pelo placer. Dois arranjos têm sentido, e a escolha
tem de ser consciente:

- **agrupado**: todas as cadeias numa região pequena, perto do SYSMON, para verem a mesma
  temperatura e a mesma queda de VCCINT (comparação entre tipos de estrutura);
- **espalhado**: réplicas da mesma cadeia nos quatro quadrantes e no centro, para medir a
  variação intra-die (gradiente térmico, variação de processo, queda de IR). A literatura de ROs
  faz isso com milhares de ROs; aqui bastam 4 ou 5 réplicas de 2 tipos.

Com o `fpga_multi_top` parametrizado, a diferença é um pblock por cadeia na XDC e gerar a
`fpga_multi_fixed_pnr.xdc` de novo. Regra aprendida: cada sensor no mesmo slice ou no slice
vizinho do fim da cadeia, com o D do FF1 entrando pelo pino direto (AX); nunca deixar um FF de
uma cadeia cair no slice de outra (o caso do FF1 da cadeia 0).

### 2.2 Aquecedores no die e controle térmico elétrico

Hoje a temperatura do die vem do forno, com constante de tempo de ~1300 s, laço externo que
move o setpoint ±1 °C a cada 30 min, e o STM32 chegando a 84 °C (onde a USART começou a
errar antes da v6). Um aquecedor no die (blocos de LUT/FF alternando, DSP ou BRAM em
atividade, com PWM lento) permite:

- **die a 115 °C com o forno mais frio** (por exemplo 60 °C): menos estresse em STM32, PMIC,
  conectores e cabos, que não são o DUT;
- **laço interno elétrico** sobre a temperatura do SYSMON, com resposta em segundos: é o
  mesmo tema do artigo (fidelidade do controle térmico) um nível abaixo, e permite perfis
  (degraus, ciclos térmicos) impossíveis com o forno;
- **gradiente intencional**: aquecedor num canto e réplicas a distâncias diferentes dão várias
  temperaturas no mesmo die e na mesma run, com termômetros locais (ROs de §1.4 calibrados
  contra o SYSMON a forno uniforme). Em princípio isso extrai a energia de ativação de uma run
  só.

O que precisa ser conferido antes: o orçamento de corrente. O STM32 corta em 2,0 A e o VCCINT
já está em ~1,1 A a 115 °C (1,05 A de fuga estática); sobram ~0,75 W, que talvez levantem o die
alguns °C e não 50. Elevar o die 40 °C acima do forno exige saber a capacidade do canal de
VCCINT do TPS65400 e a resistência térmica junção-ambiente do FFVB676 sem dissipador. A placa B
"esquenta sozinha a 97 °C" mostra que o autoaquecimento é real, mas também que a B não serve
para experimentos térmicos (die lendo 172 °C, suspeito).

### 2.3 Proximidade da raiz de clock e do SYSMON

Da árvore de clock só a raiz fica fixa (folga do FF1 varia ±1 passo entre rebuilds). Cadeias
perto da raiz (`USER_CLOCK_ROOT`) sofrem menos com o restante da árvore; e o SYSMON tem um
sensor só, então a cadeia de referência (§1.1) deveria ficar colada nele.

## 3. Modos de estresse: separar BTI de HCI

Hoje todas as cadeias alternam a cada ciclo. Mas repare o padrão: `op_a` vai de `0x55…55` a
`0x55…56`, então **só o bit 0 alterna; os outros 255 bits de `op_a` e todo o `op_b` são
estáticos**. Nos LUT2 de propagação, as entradas são DC (estresse BTI) e só a linha de carry é
AC. É um misto, e vale dizer isso no artigo. Propostas, todas selecionáveis em tempo de
execução por um comando no quadro de controle (um bitstream, vários protocolos):

| Modo | O que faz | Mecanismo alvo |
|---|---|---|
| alterna (hoje) | transição a cada ciclo de 10 ns | HCI no carry + BTI nos operandos |
| estático 0 / estático 1 | operandos fixos, sem transição; mede só em janelas curtas | BTI puro (NBTI × PBTI pelo nível) |
| alterna rápido | clock de estresse 2 a 4× (200 a 400 MHz) só no estímulo; a medida continua a 100 MHz | HCI acelerado |
| só medida | clock da cadeia parado fora da medida (duty ~1 %) | controle "não estressado" |

Na mesma linha, dois acréscimos baratos no sensor:

- **borda de subida e de descida separadas**: o `toggle` diz qual valor é esperado em cada
  ciclo; guardar o passo do primeiro alarme separadamente para ciclos esperados 1 e 0. NBTI
  (PMOS) e PBTI/HCI (NMOS) puxam bordas diferentes; a diferença entre as duas curvas é um
  observável novo, mesmo que o mapeamento em LUT e mux de carry não seja limpo.
- **ciclos estresse–relaxamento**: parar o estresse por 10 min a cada 6 h, com T e V
  constantes, e registrar a recuperação. BTI recupera em minutos; HCI não. Hoje os corners
  depois da run são medidos com o forno frio, horas depois: parte da deriva de BTI já
  recuperou. Isso sozinho pode explicar o "≤ 0,5 contagem".

Expectativa da literatura para 16 nm FinFET (Bender/Bernstein, MTOL em Xilinx 16 nm): BTI
domina sobre HCI, EM e TDDB, e ROs mais curtos (mais rápidos) degradam um pouco mais, por
autoaquecimento dos fins. Então o modo estático deve ser o que mais deriva, e o "alterna rápido"
acrescenta autoaquecimento, não só HCI.

## 4. Sensor e medida: onde está o ganho grande

### 4.1 VCO a 1600 MHz: passo de 11 ps (ganho 1,8×, custo quase zero)

A resolução da fase fina é a do VCO. O UG572 dá ~30 ps a 600 MHz e ~11 ps a 1,6 GHz (1/56 do
período do VCO). Hoje o VCO está em 900 MHz (100 × 9). Com 100 × 16 = 1600 MHz e divisores 16,
as três saídas continuam a 100 MHz e o passo cai para 11,16 ps. Conferir na DS931 o
`MMCM_FVCOMAX` do -1 (nas DS923/DS925 é 1600 MHz; a DS931 não foi lida hoje). Efeitos: o `.xci`
do `clk_wiz_0` muda (e com ele o bitstream, logo novo congelamento), a varredura tem 1,8× mais
passos (cai de ~8000 para ~4400 varreduras/s, sem problema), a escala em ps do app muda, e a
saturação (hoje 1008 passos) tem de ser reconferida. A XDC fixa das cadeias continua válida.

### 4.2 Medida estatística abaixo do passo (a curva de probabilidade)

O `multi_capture` guarda o passo do **primeiro** `CHECK_ALARM` com alarme. Isso mede a cauda da
distribuição de jitter, não o centro: quando a borda do dado está longe de um limite de passo,
o resultado é um inteiro "pegajoso" (os corners mostram 407,00 e 417,00 com σ 0), e a fração
só aparece quando a borda cai dentro do jitter. É também a explicação mais simples da
"histerese" vista em 07/11.

Alternativa clássica (Wong, Sedcole & Cheung, 2009, automedida de atrasos em FPGA): em cada
passo da fase, contar os erros do XOR em N ciclos (por exemplo 2^12) e registrar a fração
p(passo). A transição é uma curva em S de largura ~σ do jitter; o centro (ajuste de erfc ou
centroide) tem resolução ~σ/√N por varredura e, acumulado por janela, muito abaixo de 1 ps.
Ganha-se ainda σ como observável (jitter e janela de metaestabilidade, que também podem
mudar com a idade). Custo: um contador de erros por cadeia e um campo novo no quadro (ou um
quadro por passo em volta da transição); o agendador só precisa parar alguns passos antes e
depois do primeiro alarme. Combinado com §4.1, a medida de folga passa a ter resolução de
ordem de 0,1 ps, comparável à de um RO, mantendo a semântica de margem de timing.

### 4.3 Período maior para cadeias mais longas

A deriva em ps cresce com o atraso da cadeia e a resolução em ps é fixa. Com `clk_sys` a 50 MHz
(divisor 18 no VCO de 900, ou 32 no de 1600), a cadeia pode ter até ~18 ns (2,4× a de 1024
CARRY8). Custo: metade da taxa de estresse HCI; conferir o alcance da fase dinâmica (hoje a
saturação em 1008 passos corresponde a 20 ns). É um ganho linear, menor que os de §4.1–4.2,
mas composto com eles.

### 4.4 Referência de atraso estável em PVT com IDELAYE3

O IDELAYE3 aceita entrada da lógica (`DELAY_SRC = DATAIN`), e em modo TIME o IDELAYCTRL o
recalibra continuamente contra um clock de referência: o atraso fica constante em V, T e, até
onde a calibração alcança, idade. Uma "cadeia" feita só de um IDELAYE3 de valor fixo seria uma
régua: o que o sensor lê dela só muda se o sensor (clock, FF1) mudar. Precisa de um banco de
I/O com VCCO alimentado e de um REFCLK (300 MHz do MMCM). Especulativo: conferir se a placa
RV02A alimenta um banco HP e a precisão de calibração na DS931 (`TIDELAY_RESOLUTION`).

### 4.5 TDC de carry no lugar da varredura

Uma linha de atraso de CARRY8 com FFs em cada tap mede, a cada ciclo, onde a borda chegou
(bins de ~5 a 10 ps), sem varrer a fase: milhões de amostras por segundo, histograma completo.
É o estado da arte de medida de tempo em FPGA, mas o TDC também envelhece e precisa de
autocalibração (teste de densidade de código). Custo alto; vale só se §4.2 não bastar.

## 5. Aceleração: o que ainda dá

- **Tensão:** 1,00 V é o máximo absoluto da DS931 e já é o limite da bancada. Não há mais.
- **Temperatura:** de 115 para 125 °C (máximo absoluto de Tj) rende ~1,7× com Ea 0,7 eV. É
  risco real para as placas e a B já lê 172 °C; só com decisão do grupo.
- **Duração:** t^0,2 (BTI) rende 1,4× de 37 h para 200 h; HCI (t^0,5) renderia 2,3×. Runs
  longas valem mais para HCI e para separar mecanismos pelo expoente do que para "ver mais".
- **Frequência de estresse** (§3, alterna rápido): 4× em HCI e autoaquecimento extra.
- **Aquecedores** (§2.2): a única alavanca térmica que não passa pelo forno.

Também vale registrar o que a bancada já faz bem e deve continuar: trim de VCCINT pelo SYSMON
(σ 0,17 mV na run de 37 h; com ~83 passos/V medidos nos corners da A, isso é 0,014 passo de
ruído, desprezível), medida contínua a 1 Hz durante a run (é a medida "sob estresse", a mais
honesta contra recuperação), e o bitstream congelado por md5 e USR_ACCESS.

## 6. Protocolo experimental e análise

1. **Corners quentes e frios.** Medir os corners de V com o forno ainda na temperatura da run,
   imediatamente ao fim (minutos, não horas), e depois frios. A diferença entre os dois é a
   recuperação. A ordem e o estado inicial têm de ser os mesmos antes e depois (lição de 07/11).
2. **Mini-corners de V durante a run.** V muda em segundos pelo PMIC; T não. A cada 6 h, um
   degrau de 0,85 → 0,90 → 0,85 V por 30 s dá a sensibilidade a V de cada cadeia ao longo do
   tempo (ela própria pode envelhecer) sem perturbar o forno.
3. **Modelo por cadeia.** Generalizar o R² do artigo: folga_i(t) = a_i + b_i·T + c_i·V + d_i·t^n.
   Os b_i e c_i vêm dos corners; o resíduo é a idade. As diferenças entre cadeias cancelam o modo
   comum (§1.1), e o expoente n distingue BTI (~0,2) de HCI (~0,5).
4. **Réplicas e potência estatística.** Com σ por leitura conhecido e N leituras por hora, o erro
   padrão da deriva é σ/√N; definir antes da run quantas réplicas e horas são precisas para
   detectar 0,05 % com 95 % de confiança. Hoje isso não é calculado.
5. **Placa de controle.** Uma terceira placa à temperatura ambiente, com o mesmo bitstream,
   lida nas mesmas horas, separa envelhecimento de deriva da medida (ou alternar papéis entre
   as duas placas em runs sucessivas). Com a B suspeita, as réplicas espaciais na A (§2.1)
   ganham importância.
6. **Observação a confirmar nos corners:** a 16 nm e tensão nominal, o atraso varia pouco com T
   (inversão de temperatura); se confirmado, o lado "fidelidade do sensor" da Eq. (3) do artigo
   muda de natureza (o confundidor dominante passa a ser V, que a bancada já controla bem).

## 7. Infraestrutura

- **App (D&T Monitor):** decodificar o `FPGA_CHAIN` 0x03, colunas por cadeia no CSV,
  reconhecer o USR_ACCESS do `au15p_multi_B`, modo de estresse por comando, corners automáticos
  (quente e frio) e mini-corners; `verificar_hub.py` e o modo hub só conhecem o `au15p_hub_B`.
- **Firmware STM32:** já corrigido para HSE (v6). Se vierem quadros maiores (curva de
  probabilidade, contagens de RO), rever a fila de 4 posições e os ~10 ms por `$FPG` no ST-Link.
- **Bancada:** orçamento de corrente para aquecedores (trip de 2,0 A do STM32, canal do PMIC);
  placa de controle; o die da B precisa de diagnóstico antes de qualquer conclusão térmica.
- **Reprodutibilidade:** o fluxo posição fixa → XDC gerada → bitstream congelado → md5 e
  USR_ACCESS no LEIAME já é material de tutorial (a D&T exige 15 %), incluindo a armadilha do
  LUT vazio (route-thru) e o `LOCK_PINS` que o `write_xdc` não emite.

## 8. Prioridade sugerida

| # | Ideia | Custo | Ganho | Depende de |
|---|---|---|---|---|
| 1 | Gravar o `au15p_multi_B` numa placa; app decodificando 0x03 | app | base por cadeia, confirma o vernier | nada |
| 2 | Run curta (48 h) com as 9 cadeias; corners quentes e frios (§6.1) | bancada | primeira deriva por tipo; mede a recuperação | 1 |
| 3 | RTL v4: VCO 1600 MHz, curva de probabilidade, bordas separadas, cadeia zero (§4.1, 4.2, 3, 1.1) | RTL médio + app | resolução de ~20 ps para < 1 ps; modo comum separado | 1 |
| 4 | Modos de estresse por comando e réplicas em pblocks (§3, 2.1) | RTL baixo + XDC + app | BTI × HCI e variação intra-die na mesma run | 3 |
| 5 | Modo duplo RCA/RO e ROs acompanhantes (§1.3, 1.4) | RTL médio + app | leitura em ppm, comparável à literatura | 3 |
| 6 | Aquecedores e laço térmico elétrico (§2.2) | hardware a conferir + RTL + app | forno mais frio, controle rápido, gradiente | orçamento de corrente |
| 7 | Run longa (≥ 200 h) com o projeto final, placa de controle | bancada | expoente temporal, mecanismos | 3–5 |
| 8 | Roteamento puro, DSP/BRAM, pino do LUT (§1.2, 1.5, 1.6) | RTL baixo | atribuição por recurso | 4 |
| 9 | IDELAYE3 como régua, TDC (§4.4, 4.5) | alto | só se o resto não bastar | 3 |

Os itens 1 a 3 cabem antes da próxima run e mudam o que ela pode mostrar. O 6 é o de maior
alcance para o artigo (controle térmico no die, o tema da D&T), mas é o que mais depende de
hardware.

## 9. O que isso daria ao artigo da D&T 2027

- **Resultado novo substancial:** caracterização in situ de envelhecimento num FPGA 16 nm
  FinFET com várias estruturas (carry, LUT, roteamento), modos de estresse separando BTI de
  HCI, e um sensor de folga com resolução abaixo do picossegundo, tudo sob controle térmico
  medido (o fio condutor do SBCCI).
- **Comparação direta** entre um sensor de margem de timing (o que o projetista quer) e ROs
  (o que a literatura mede), na mesma run e no mesmo die.
- **Tutorial:** como congelar posição e rota para medir deriva (fixed PnR), por que a
  resolução do MMCM é o teto e como passar dele, e por que corners frios subestimam BTI.
- **Lição de projeto de bancada:** aquecer o DUT e não o forno (se §2.2 vingar).

## 10. Leituras (conferir antes de citar; a D&T permite 12 referências)

- J. Sobas, F. Marc, "Degradation Measurement and Modelling under Ageing in a 16 nm FinFET
  FPGA", Micromachines 15(1):19, 2024, doi 10.3390/mi15010019. 5103 ROs em 9 FPGAs, 8000 h,
  25 a 115 °C, até 1,3× a tensão nominal; separa lógica de roteamento. Não consegui ler o texto
  hoje (acesso bloqueado); os números acima vêm do resumo.
- J. Sobas, T.-B. Airimitoaie, F. Marc, "Development of a high accuracy and stability test
  bench for ageing measurement of 16 nm FinFETs based FPGA", Microelectronics Reliability, 2022.
  Zynq UltraScale+, 1000 h a 100 °C: deriva < 0,1 %.
- E. Bender, J. B. Bernstein, A. Bensoussan, "Reliability prediction of FinFET FPGAs by MTOL",
  Microelectronics Reliability 114:113809, 2020, doi 10.1016/j.microrel.2020.113809. Xilinx
  16 nm; BTI domina; ROs mais curtos degradam um pouco mais (autoaquecimento).
- J. S. J. Wong, P. Sedcole, P. Y. K. Cheung, "Self-measurement of combinatorial circuit
  delays in FPGAs", ACM TRETS, 2009. Base da medida por probabilidade de falha (§4.2).
- E. Stott, J. S. J. Wong, P. Sedcole, P. Y. K. Cheung, "Degradation in FPGAs: measurement and
  modelling", FPGA 2010. Estresse DC × AC em ROs, planar.
- A. Amouri et al., "Aging effects in FPGAs: an experimental analysis", FPL 2014.
- K. Zick, J. Hayes, "Low-cost sensing with ring oscillator arrays for healthier reconfigurable
  systems", ACM TRETS 2012. ROs como termômetros distribuídos.
- AMD UG572 (fase fina do MMCM: ~11 ps a 1,6 GHz), UG974/UG571 (IDELAYE3 com `DATAIN`),
  DS931 (máximos absolutos; VCO do -1 a conferir), UG116 (relatório de confiabilidade), JEDEC
  JEP122 (modelos de mecanismos de falha).
