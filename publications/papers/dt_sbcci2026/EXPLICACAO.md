# O que mudou no artigo D&T, e por quê (explicação passo a passo)

Este arquivo é interno; não vai para a submissão.

## 1. De onde partimos

A versão anterior ("Burn-In Thermal Control Sets What Aging Sensors Can See") fazia uma cadeia de três afirmações:

1. **Estresse.** O termostato entregou 1,65× menos aceleração (AF) que o PID. A causa era a média da temperatura do die, não o ripple.
2. **Ruído.** O termostato deixou 1,24× mais ruído residual no sensor.
3. **Detecção.** Juntando os dois, uma bancada com termostato levaria 1,29–1,69× mais tempo para "ver" o envelhecimento.

A afirmação 1 sobreviveu a todas as revisões. As afirmações 2 e 3 tinham uma fragilidade escondida. O ruído foi medido com um único número (o desvio-padrão σ, amostra a amostra), e a projeção supunha que esse ruído era "branco", isto é, sem memória. O envelhecimento, porém, aparece em escalas de dezenas de horas, e nelas o ruído não se comporta como branco.

## 2. Como chegamos ao híbrido

1. **Auditoria externa (feedback que você recebeu).** Apontou que o par de 23 h não é um teste A/B, que a deriva depende dos regressores, que o T_min era otimista, e problemas de referências.
2. **Correções A, B e C**, aplicadas na versão principal.
3. **Dois revisores independentes.** Confirmaram as correções e acharam resíduos: o 1,65× ainda sem ressalva, a MIL-STD imprecisa e o Sobas mal posicionado.
4. **Dois caminhos em paralelo.**
   - O **B** poliu o artigo existente.
   - O **A** se reestruturou em torno de uma ideia nova: olhar o ruído por *tempo de média*.
5. **Quatro revisores cruzados** (metodologia, normas, editor e reprodutibilidade). Os quatro preferiram A como base. Também acharam o erro mais grave da série: **o PID de 23 h (jan/2026) não tinha malha externa**. Ela só entrou no código em 16/05/2026, no commit `2070e38`, e o setpoint de 83 °C foi ajustado à mão nos primeiros 4 min.
6. **Híbrido.** Usa A como espinha. Traz de B as frases práticas e a parte de normas. Corrige tudo o que os quatro revisores e o auditor verificaram nos dados.

## 3. Os ângulos de análise novos

Para cada ângulo: o que é, como apareceu, por que importa e o que deu.

### 3.1 Olhar o ruído por tempo de média (desvio de Allan/Hadamard)

- **O que é.** Divide-se o sinal em janelas de duração τ e mede-se quanto as médias de janelas vizinhas diferem. O resultado é plotado contra τ em escala log-log.
  - Ruído branco cai como τ^(−1/2).
  - Um **piso** (trecho plano) é ruído que mais média não reduz.
  - Um ciclo periódico aparece como uma "corcova".
  - Uma deriva sobe como uma reta.
  - A versão de **Hadamard** usa segunda diferença, então ignora deriva linear e mede só o ruído.
- **Como apareceu.** O revisor da primeira rodada observou que a variância de longo prazo do resíduo crescia 17× entre blocos de 15 min e de 8 h. Isso é a assinatura de ruído não branco. A ferramenta-padrão da metrologia para esse caso (relógios atômicos, giroscópios) é o desvio de Allan. O caminho A a aplicou.
- **Por que importa.** É o enquadramento certo para a pergunta do artigo: *quanto tempo até ver o envelhecimento?* Engenheiros de D&T conhecem Allan, e a ferramenta é didática, o que ajuda nos 15% de conteúdo tutorial.
- **O que deu.**
  - O ciclo do termostato é grande: 2,8 °C, com pico perto de 11 min de média. Mesmo assim, a correção PVT linear remove **96%** do seu efeito no sensor.
  - Acima de 1 h, todo resíduo achata num piso.

### 3.2 O piso, e não o σ, define o tempo de detecção

- **O que é.**
  - Com ruído branco, o erro da inclinação cai como T^(−3/2) e o tempo de detecção escala com σ^(2/3).
  - Com um piso, o erro cai só como 1/T, e o tempo escala com piso/deriva.
- **Como apareceu.** Foi consequência direta do ângulo 3.1.
- **Por que importa.** O número que o artigo antigo usava, T_min = 20 h, supõe ruído branco. Três estimadores do ruído real dão **66–149 h**. A faixa foi revisada duas vezes: na 2ª rodada, a leitura de Allan passou a usar o piso declarado (116 h); na 3ª, entrou o patamar de 6–30 h da corrida longa (0,32 cnt), que dá 149 h.
  - variância de longo prazo;
  - dispersão de inclinações em janelas;
  - duas janelas de Allan.
- **Ressalva honesta.** Os três medem o mesmo conteúdo de baixa frequência, então não são independentes. Por isso o artigo dá uma faixa, e não "91 h".

### 3.3 Inclinações em janelas deslizantes

- **O que é.** Calcula-se a inclinação da deriva em todas as janelas de W horas ao longo da corrida e olha-se a dispersão.
- **Como apareceu.** Estava no feedback: janelas de 34 h vão de −76 a +44 mcnt/h.
- **Por que importa.** É a prova mais intuitiva para um leitor de que um dia não basta.
  - Em janelas de 34 h, 30% das inclinações têm o sinal *contrário* ao envelhecimento.
  - Em janelas de 72 h, todas são negativas.
  - Também responde a uma pergunta que o SBCCI deixou aberta: as inclinações tardias não nulas de 23 h são deriva dentro da corrida, mas não dá para chamá-las de envelhecimento.

### 3.4 Quais regressores são legítimos ("bad controls")

- **O que é.** Para corrigir PVT, regride-se o slack em canais ambientais. Se um canal *responde ao próprio envelhecimento*, incluí-lo apaga parte do sinal que se procura. O teste é ver se o canal deriva com temperatura e tensão do die fixas.
- **Como apareceu.** O feedback mostrou que a deriva caía de −18,3 para −10,6 mcnt/h com a tensão da fonte. Pelo nosso cálculo, ela cai para −5,9.
- **O que deu.** Com T e V fixos, ao longo da corrida longa:
  - a corrente da fonte subiu 9,5 mA;
  - a tensão da fonte subiu 4,0 mV;
  - o ar do forno subiu 2,4 °C.

  Nenhum desses canais é "seguro". A estimativa principal usa só T e V (−18,3 mcnt/h, que um ajuste conjunto S~T+V+t confirma com −18,4). As outras viram faixa de sensibilidade.
- **Por que importa.** Vira uma regra do tutorial que qualquer laboratório pode aplicar. Também desarma o revisor que pergunta "por que esses regressores?".

### 3.5 A corrente como segundo termômetro

- **O que é.** A corrente de fuga sobe com a temperatura, então ela funciona como um termômetro independente do XADC.
- **O que deu.** A deriva da corrente equivale a só 13% da deriva de temperatura que explicaria a deriva do slack.
- **Por que importa.** Torna improvável a objeção "o XADC derivou, não o circuito". A ressalva é que o envelhecimento também pode reduzir a fuga.

### 3.6 Decompor o gap de estresse (1,65×)

- **O que é.** Separar a parte do gap que vem do controlador da parte que vem do setpoint (83 contra 80 °C).
- **Como apareceu.**
  - O auditor externo mostrou o setpoint de 83 °C.
  - A corrida longa, em que o ar se moveu 49 vezes, permitiu medir quanto o die segue o ar: 1,0 a 1,8 °C por °C de ar, conforme a escolha de bloco e defasagem.
- **O que deu.** Igualando o ar, o gap fica em **1,22–1,41×**.
  - Com ganho 1:1, fica em 1,40×.
  - O offset die–ar também mudou de uma corrida para outra: 34,1 contra 31,1 °C.
- **Por que importa.** Mantém a mensagem ("a média do die decide") sem atribuir ao termostato o que é do setpoint. O offset variável é o melhor argumento empírico para ler a JESD22-A108 pela junção: a câmara não fixa o die.

### 3.7 Incerteza da comparação entre bancadas

- **O que é.** Mede-se quanto o piso varia *dentro da mesma bancada*, usando 7 segmentos de 23 h da corrida termostática de uma semana.
- **O que deu.** Com regressão PVT feita dentro de cada segmento, o piso varia de 0,031 a 0,055 cnt. A razão BB/PID de 1,13 cai dentro dessa faixa: **os dados não separam as duas bancadas nessa escala**. O teste tem pouco poder, então isso não prova que elas sejam iguais.
- **Por que importa.** Isso muda a conclusão sobre a penalidade do termostato. A diferença de ruído de 1,24× vale na taxa de amostragem, mas não sobrevive na escala de horas. O que sobra da penalidade é o déficit de estresse.
  - É uma extensão do SBCCI, não uma correção: o 1,24× continua correto na escala em que foi medido.

### 3.8 A deriva se concentra no começo

- **O que deu.** O primeiro dia tem a inclinação mais íngreme, −74 mcnt/h. Na 2ª rodada, os revisores mostraram que o z = 8,1 era artefato: o estimador HAC fica mal calibrado em janelas curtas quando há piso. Comparada à dispersão das inclinações em janelas de 24 h (36 mcnt/h), essa inclinação é só uma leitura de ~2σ.
- **Por que importa.** Esse é o exemplo de um erro que o próprio enquadramento do artigo corrige: confiar no erro-padrão de curto prazo leva a uma detecção falsa. Um transiente de partida produziria o mesmo padrão.

### 3.9 Resultados negativos que fortalecem o artigo

- **A deriva lenta do die explica pouco do piso.** Mesmo com sensibilidades ajustadas só na banda rápida, a temperatura do die, o ar e dT/dt explicam no máximo R² = 0,25 do resíduo lento. O valor de 0,05 da 1ª versão era parcialmente tautológico.
  - Isso derrubou a tese do caminho A de que "a malha externa cria o piso". O híbrido diz que a origem não está identificada e lista as candidatas: gradiente XADC–caminho e deriva do relógio.
  - O artigo afirma o que os dados sustentam: o piso existe, sobreviveu a uma malha referenciada no die e define a detecção.
- **Atraso térmico não é o limite.** A diferença aquecimento–resfriamento é de só 0,11 cnt, e dT/dt melhora o ajuste em menos de 1%.
- **Não há ciclo diurno.** O R² com um ciclo de 24 h é no máximo 0,05.

### 3.10 Verificação no código e no RTL (git)

- **Recalibração do sensor.** O controlador do bitstream da corrida longa (commit `9d72faa`) refaz cada leitura a partir da fase de referência, sem linha de base guardada. A recalibração automática, portanto, não absorve deriva lenta.
- **Malha externa.** Os parâmetros (±3 °C, 1 °C a cada 30 min) estão no commit `3b92e9d`. O código mostra que ela não existia em janeiro de 2026.

### 3.11 A penalidade do termostato sob piso (corrigida na 2ª rodada)

- **O que é.** Quando o ruído tem piso, uma corrida só detecta a deriva depois de acumular uma quantidade fixa dela.
- **O que deu.** Com D = a·(AF·t)^n, isso exige AF·T constante. A penalidade de tempo é então a própria razão de AF (1,65×, ou 1,22–1,41× ajustada ao setpoint), qualquer que seja n. O 1,19× anterior comparava taxas no mesmo tempo, não tempos de detecção.
- **Por que importa.** Reforça a conclusão: no regime que importa, o custo do termostato é o déficit de estresse, não o ruído.

## 4. O que saiu, e por quê

| Removido | Motivo |
|---|---|
| Informação mútua | Terminava "inconclusiva": a quantização inteira do slack gera informação mútua falsa. |
| Alarme como canal binário (BSC) | Jargão sem uso prático e apoiado no ruído branco. |
| Teste sequencial "16 h" | Uma realização com várias olhadas, e não um limite. |
| Projeção 1,29–1,69× do ruído | Usava a escala branca que os próprios dados refutam. |
| "A malha externa cria o piso" | Sem suporte (R² de 0,05; o PID de 23 h nem tinha malha). |
| "0,05 °C" do Sobas | Vem de outro artigo do grupo, não do de 2022. |
| Referência Skogestad | Abriu vaga para a patente da Xilinx; o SIMC passou a ser citado via SBCCI 2026. |
