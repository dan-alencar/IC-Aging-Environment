# Análise do deck + Roteiro de 15 min + Prompt para o Claude Design
### TF TIP7266 — defesa de 22/08/2026

> Base da análise: `seminar_deck_outline.md` (estrutura oficial do deck, 13
> slides + backups) e o estado verificado do `seminar.pdf` na revisão da
> rodada 4 (Figura 1 regenerada no slide da manchete; "P(inclinação < 0)"
> corrigido; subtítulo "teórico-informacional"). O `seminar.pdf` final não
> está nesta sessão — os quatro itens marcados **[VERIFICAR NO PDF]** exigem
> uma conferência visual de 5 minutos no arquivo compilado.

---
---

# PARTE 1 — Análise dos slides

## 1.1 O que já está forte (não mexer)

- **Arquitetura rubrica-orientada.** Problema→objetivo nos primeiros 90 s
  (item 02), cada slide etiquetado com o núcleo da ementa (item 03), slide de
  ressalvas dedicado (item 05), mapa núcleo→resultado no backup. É um deck
  desenhado para a grade de avaliação — raro e certo.
- **Disciplina de números.** Tudo via macros do `values.tex`, nada digitado.
  Numa arguição, isso permite dizer "todo número da tela nasce no pipeline".
- **A frase de fechamento** ("R² diz que o ambiente explica 74% da variância.
  A teoria da informação diz que ele escreve 1,13 bits em cada leitura — e que
  removemos 93% deles. Bits transferem; frações de variância, não.") é o
  melhor take-away possível. Manter intocada.
- **Backups certos**: sensibilidade de bins, MDL-linear, bang-bang/sucedâneo.

## 1.2 Correções e verificações (custo baixo, risco de nota)

**(a) [VERIFICAR NO PDF] Ordem do intervalo de credibilidade no slide 8.**
O outline escreve `CrI [\valBayesSlopeHi, \valBayesSlopeLo]` — se as macros
significam o que os nomes dizem, isso imprime **[−17,2, −19,2]**, invertido.
O correto é [−19,2, −17,2]. Conferir no PDF compilado; se estiver invertido,
é troca de duas macros de lugar.

**(b) Linguagem pré-retração no slide 12 (Contribuições).** O outline ainda
diz *"a transferable noise metric in bits (MI) that **sees non-linear coupling
R² misses**"*. Essa é exatamente a formulação que a rodada 4 retirou do resumo
do artigo. Um avaliador que leu o paper verá o deck reafirmando no fechamento
o que o artigo retratou. Trocar por: **"uma métrica de contaminação em bits
que captura dependência que o R² estruturalmente não vê — qualquer que seja a
origem dessa dependência"**. [VERIFICAR NO PDF se o slide compilado herdou a
frase do outline ou já foi sincronizado.]

**(c) Slide 2, mesma família.** *"but the physics **is** non-linear"* →
pós-retração, o defensável é "a física **tem risco** de não-linearidade
(Arrhenius em T, super-linear em V) que uma métrica linear não testaria".
Sutil, mas é a diferença entre motivação e alegação.

**(d) [VERIFICAR NO PDF] Idioma 100% PT.** O outline é em inglês; conferir
que títulos de slides, labels internos das figuras matplotlib e a barra de
rodapé estão todos em português (as figuras regeneradas na rodada 4 já
estavam; conferir as demais: `fig_capacity_rul`, `fig_kl`, `fig_ica`,
`fig_wiener_rul`).

## 1.3 Abrangência — duas lacunas que a arguição vai achar

**(A) O slide 5 (n_eff) não diz COMO τ_int foi estimado.** É a pergunta de
arguição mais provável de todas (é a única grandeza-chave cujo método não está
nem no PDF do artigo). Correção mínima: meia-linha no slide 5 —
*"τ_int por janelamento automatizado (Sokal) sobre o slack detrendizado
(média móvel de 1 h)"* — e um **backup novo** "Como estimamos τ_int" com três
bullets: (i) FAC via FFT do resíduo pós-detrend de 1 h (para medir dependência
de curto alcance, não a deriva de envelhecimento); (ii) soma com corte de
Sokal em w ≥ 5τ; (iii) sensibilidade: n_eff ∝ 1/τ, sd do CRLB ∝ √τ — a
conclusão "15× o piso" sobrevive a variações amplas. Mata a pergunta antes de
ela nascer.

**(B) O achado negativo está espremido num bullet.** Hoje a lógica mais
delicada e mais impressionante do trabalho (excesso real → sobrevive ao
surrogate → não sobrevive ao detrend → retração da causa, manutenção da
estrutura) vive num bullet do slide 4 + uma linha falada. Isso subvende o
momento em que o trabalho mais demonstra maturidade. Recomendação: **dividir o
slide 4 em dois**:
- **4 (manchete, 3 números + Figura 1):** I = 1,132/1,221 bits vs equivalente
  0,967 → excesso +17–26%; piso surrogate 12× abaixo. Só isso.
- **4b (o teste que quase destruiu a manchete):** a comparação bruta vs
  detrendizada lado a lado com ICs (a figura "duas ameaças" da apostila serve
  de modelo — barras de erro brutas acima do equivalente, detrendizadas
  abaixo). Título sugerido: *"E se for só a tendência compartilhada?"*. É o
  slide que transforma "achado negativo" em "protocolo que funciona".

Custo: +1 slide. Compensação de tempo indicada no roteiro (Parte 2).

**(C — opcional, se quiser polimento) Fio condutor visual.** São 10 análises
em 13 slides; sem um fio, vira lista. Um recurso barato: uma pergunta-guia no
rodapé de cada bloco — *"quanto ambiente há na leitura?"* (sl. 3–5) →
*"dá para remover?"* (6) → *"o que o sensor resolve?"* (7) → *"quando o
envelhecimento aparece?"* (8–8b) → *"isso transfere entre bancadas?"* (9–10).
No Beamer, é um `\setbeamertemplate{footline}` por seção. (Este item pode ir
direto no prompt do Claude Design, Parte 3.)

## 1.4 Profundidade — três acréscimos de uma linha cada

1. **Slide 7 ou 8 (fala, não texto):** BSC e CRLB compartilham a mesma escala
   W^{3/2} — por isso a transição do alarme coincide com o tempo mínimo de
   observação. *"Três figuras de mérito, uma física — não são heurísticas
   soltas."* É o tipo de frase que sinaliza domínio.
2. **Slide 9:** incluir o número da forma fechada Gaussiana ao lado do
   empírico — **1,94 (empírico) > 1,67 (Gaussiano)** → caudas pesadas — que é
   a premissa que o ICA confirma no slide seguinte (curtose +29,9). Amarra os
   dois slides.
3. **Slide 6:** o veredito MDL na formulação exata — *"curvatura insuficiente
   NESTE ponto de operação para pagar os parâmetros extras"* — e a deixa para
   o 8b (*"guarda essa frase: ela volta duas vezes"*), preparando o momento
   "três rotas independentes, um veredito".

## 1.5 Timing — diagnóstico

O orçamento do outline soma ~14,5 min, mas o slide 4 como está (5 ideias em
2 min) vai estourar. Com a divisão 4/4b e os cortes de 15 s nos slides 6 e 9,
o roteiro abaixo fecha em 14:15 + 45 s de folga — folga que você vai querer,
porque a manchete e o achado negativo merecem respiração, não pressa.

---
---

# PARTE 2 — Roteiro de fala (15 min)

> Formato: [relógio acumulado] — o que dizer (não decorar palavra a palavra;
> decorar as frases em **negrito**, que são as âncoras). Assume a estrutura com
> o slide 4b; se mantiver o deck atual, o bloco 4b é falado sobre o slide 4.

**[0:00–0:15] Slide 1 — Título.**
"Bom dia. Este trabalho pega um sensor de envelhecimento que já existia na
minha pesquisa e faz uma única mudança de ponto de vista: **trata o sensor
como um canal de comunicação ruidoso — e mede tudo em bits.**"

**[0:15–1:15] Slide 2 — Problema e objetivo.**
"O trabalho anterior mede a contaminação ambiental do sensor com um R² linear:
0,74. Dois problemas. Primeiro: R² só enxerga dependência **linear** — e a
física aqui tem risco real de não-linearidade: Arrhenius em temperatura,
super-linear em tensão. Cov = 0 não implica independência. Segundo: 'fração de
variância explicada' **não tem unidade transferível** — não responde quantos
estados o sensor resolve, nem quando uma tendência é detectável. Objetivo:
substituir R² por informação mútua e deixar entropia, capacidade e teoria de
estimação responderem o resto."

**[1:15–2:15] Slide 3 — O canal e os dados.**
"Uma equação: o slack reportado é o envelhecimento latente, menos a flutuação
reversível de temperatura e tensão, mais quantização. No vocabulário de canal:
**transmissor, ruído, e o receptor é o estimador de vida útil.** Os dados: 214
horas de campanha PID, 768 mil amostras a 1 Hz, 27 níveis de slack — entropia
total de 3,43 bits. **Esse é o orçamento de incerteza que vamos fatiar**: o
que é ambiente, o que é envelhecimento, o que é piso."

**[2:15–3:30] Slide 4 — MANCHETE.** *(desacelerar; apontar os números)*
"A informação mútua entre slack e ambiente: **1,13 bits por leitura** no
estimador por histograma, 1,22 no estimador KSG — um terço da entropia do
sensor é ambiente. Se a dependência fosse exatamente a linear que o R² vê,
seriam 0,97 bits — **a MI medida excede isso em 17 a 26%**. E não é viés de
estimador: o piso nulo por surrogates fica 12 vezes abaixo. Dois estimadores
independentes, ICs próprios, faixa reportada como incerteza — não escolhemos o
número mais bonito."

**[3:30–5:00] Slide 4b — O teste que quase destruiu a manchete.**
*(o bloco de 90 s treinado na apostila)*
"Só que havia **duas ameaças** a esse excesso, e elas são diferentes. A
primeira — viés de estimador — o surrogate elimina: descontando até o pior
caso do piso, sobra excesso. A segunda é mais sutil: **envelhecimento e deriva
lenta do ambiente compartilham o eixo do tempo** em 214 horas; a MI bruta
conta essa co-tendência como dependência. Refizemos a comparação inteira nas
séries sem tendência: o excesso **desaparece** — vira déficit de 11 a 19%.
Conclusão honesta, que está no resumo do artigo: **retiramos a leitura causal**
'a física é não-linear'. O que fica de pé é estrutural: a MI não tem ponto
cego de linearidade, seja qual for a origem da dependência — e foi o nosso
próprio protocolo que encontrou e corrigiu a leitura errada. **O achado
negativo é o protocolo funcionando.**"

**[5:00–6:00] Slide 5 — O pilar: n_eff.**
"Tudo isso só é honesto por causa de um número: 768 mil amostras a 1 Hz são
massivamente redundantes. O tempo de autocorrelação integrado — estimado por
janelamento de Sokal sobre o slack sem a deriva — é de 314 segundos, então as
768 mil amostras **valem 1.224 amostras independentes**. Usar o n bruto
encolheria toda barra de erro por um fator 25 — certeza falsa. **Cada IC,
o piso surrogate, o ajuste Bayesiano e o Kalman usam n_eff, não n.**"

**[6:00–7:15] Slide 6 — Correção PVT.**
"Identificada a contaminação, removemos: ajuste de Δ_PVT e subtração. A
métrica de sucesso não é correlação zerada — OLS zera correlação por
construção — é **informação reversível residual**: de 0,66 para 0,046 bits,
**93% do acoplamento removido**, resíduo no piso do estimador. Entre o modelo
linear e o não-linear físico, o MDL escolhe o linear: **curvatura insuficiente
neste ponto de operação para pagar os parâmetros** — guardem essa frase, ela
volta. E o efeito colateral importante: remover o ambiente **expõe** o
envelhecimento — a correlação com o tempo dobra, de −0,35 para −0,73."

**[7:15–8:30] Slide 7 — Resolução e alarme.**
"Com o sinal limpo, duas perguntas de engenharia. Quantos estados o sensor
resolve? SNR de 2,4 → capacidade de 0,87 bits → **1,8 estados de
envelhecimento distinguíveis** na campanha — heurística de resolução, não taxa
de Shannon: não há codificador na física. E o alarme 'houve envelhecimento?':
por hora, o canal binário é uma moeda — capacidade zero. **Por janela de 24
horas: 0,99 bits por decisão** — quase perfeito. A transição não é acaso: o
alarme e o limite de detecção compartilham a mesma escala W^{3/2}."

**[8:30–9:45] Slide 8 — Limite de detectabilidade.**
"Quando a tendência se torna detectável? Cramér–Rao: com este ruído e este
n_eff, a menor taxa detectável a 3σ é 1,2 mili-contagens por hora. A taxa
medida é **−18,3 — quinze vezes o piso**. Invertendo a mesma lei: seriam
necessárias **34 horas** de observação para detectar essa taxa — e as
campanhas anteriores tinham 23. **Eis, num número, por que elas não separavam
envelhecimento de ruído.** A rota Bayesiana independente dá −18,2, intervalo
[−19,2, −17,2], tempo mínimo entre 33 e 36 horas — frequentista e Bayesiano
concordam. E precisão: P de inclinação negativa ≈ 100% — inclinação, não
causa; a leitura como envelhecimento é condicionada ao estudo de dispositivo
único. Isto é um **limite de detectabilidade, não predição de vida útil**."

**[9:45–10:45] Slide 8b — RUL como distribuição.**
"Mesma caixa de ferramentas, pergunta sequencial: modelamos o resíduo como
processo de Wiener e filtramos com Kalman. Dois resultados. O MLE do ruído de
taxa colapsa a zero — os dados preferem deriva constante — **terceira rota
independente confirmando o 'sem curvatura'** do MDL e da MI detrendizada. E a
primeira passagem dá a **distribuição completa** do tempo até o próximo marco:
Gaussiana inversa, média 53 horas mas mediana 8 — cauda pesada exatamente
porque estamos no regime de SNR baixo do slide anterior. **Capacidade e RUL
amarrados pelo mesmo mecanismo.**"

**[10:45–11:30] Slide 9 — Fidelidade de bancada.**
"Isso transfere para a pergunta de bancada — em outro dispositivo, dito
explicitamente. Bancada não-conforme vs referência PID: KL de 1,94 bits numa
direção, 1,01 na outra — a assimetria é a própria lição de que KL não é
métrica; JS simétrica, 0,28 bits. E um refinamento: **o KL empírico, 1,94,
excede a forma fechada Gaussiana, 1,67** — a bancada ruidosa injeta caudas
pesadas não-Gaussianas. Guardem: caudas pesadas."

**[11:30–12:15] Slide 10 — ICA.**
"As caudas pesadas são exatamente o que o ICA precisa. Separação cega, sem
nenhuma forma funcional para o ambiente: o componente temporal recuperado bate
com o resíduo da regressão em **|corr| = 0,83** — 70% de variância
compartilhada. Mesmo espaço, **critérios opostos** — mínimos quadrados versus
independência — mesmo componente: a correção não é artefato do critério.
Separação parcial, 0,57 bits residuais — reportada como corroborativa,
não como desmistura limpa."

**[12:15–13:00] Slide 11 — Ressalvas.**
"O que este trabalho **não** afirma: dispositivo único e regime único — por
isso limite e metodologia, não predição validada; capacidade é heurística de
resolução; ICA é corroborativo; a comparação de capacidade por regime não foi
entregue — sem log bang-bang pareado, o KL entre bancadas é o sucedâneo
declarado e é o primeiro item de trabalho futuro; e n_eff, não n, em tudo."

**[13:00–14:15] Slide 12 — Contribuições e fecho.** *(desacelerar de novo)*
"Três coisas que o trabalho anterior não podia enunciar. Uma métrica de
contaminação **em bits**, sem ponto cego de linearidade e transferível. Um
**protocolo anti-confundimento** — n_eff, surrogates, detrend, dois
estimadores — rigoroso o bastante para detectar e retratar a nossa própria
hipótese motivadora. E a **especificação do sensor**: 1,8 estados, 0,99
bits por decisão diária, detectável em 34 horas — que explica por que 23 horas
nunca bastaram. Fecho: **R² diz que o ambiente explica 74% da variância. A
teoria da informação diz que ele escreve 1,13 bits em cada leitura — e que
removemos 93% deles. Bits transferem; frações de variância, não.** Obrigado."

**[14:15–15:00] Folga** para respiro, transição de slides e o primeiro
segundo de silêncio antes das perguntas.

### Notas de execução
- Ensaiar com cronômetro **por bloco**, não só o total: os checkpoints são
  3:30 (fim da manchete), 6:00 (fim do n_eff), 9:45 (fim do CRLB), 13:00
  (início das contribuições). Se passar 20 s num checkpoint, recuperar no
  slide 9 ou 10 (são os compressíveis), nunca no 4b nem no 12.
- As três frases que não podem sair erradas: a retração (4b), o veredito MDL
  (6) e o fecho (12). São as que o professor vai lembrar.
- Perguntas prováveis e respostas: P1–P15 da apostola (Bloco 3.6), com o
  τ_int agora respondido.

---
---

# PARTE 3 — Prompt para o Claude Design

> Anexe ao prompt: `seminar.tex` (+ tema/preâmbulo se separado), a pasta
> `figures/` usada pelo deck, e o `latex/generated/values.tex`. Cole o texto
> abaixo como está.

```
Você vai redesenhar visualmente um deck Beamer acadêmico SEM alterar uma
palavra do conteúdo. Contexto: defesa de Trabalho Final da disciplina
TIP7266 (Teoria da Informação, PGETI/UFC), 15 minutos, banca de professores
de engenharia elétrica. O deck apresenta um trabalho que trata um sensor de
envelhecimento em FPGA como canal de comunicação ruidoso e mede tudo em bits.

ARQUIVOS: seminar.tex (Beamer, pt-BR), figures/ (PDFs gerados por
matplotlib), values.tex (macros \valXxx com todos os números).

RESTRIÇÕES INEGOCIÁVEIS
1. Conteúdo congelado: nenhum texto, número, ordem de slides ou legenda muda.
   Todos os números vêm de macros \valXxx do values.tex — jamais substituir
   uma macro por número digitado.
2. O resultado deve continuar compilando com pdflatex/latexmk padrão
   (TeX Live), 16:9. Se usar fontes, apenas as disponíveis no TeX Live
   (ex.: newtx, FiraSans via pacote) — sem XeLaTeX a menos que entregue
   também um fallback pdflatex.
3. As figuras matplotlib são a fonte da verdade e não serão regeradas:
   pode ajustar tamanho, posição, molduras e espaço em branco ao redor,
   não o conteúdo delas.
4. Entregar como tema reutilizável: um beamerthemeTFinfo.sty (cores, fontes,
   templates de bloco, footline) + o seminar.tex com mudanças mínimas
   (idealmente só \usetheme e ajustes de layout por slide). Listar cada
   mudança feita no .tex.

DIREÇÃO DE DESIGN
- Sóbrio e técnico, denso em informação mas com hierarquia clara. Referência
  de tom: decks de defesa de engenharia bem tipografados, não pitch deck.
- Paleta: um azul-petróleo escuro como cor estrutural, um verde e um laranja
  como cores de dado (batendo com as cores das figuras matplotlib existentes,
  que usam verde #27ae60 e laranja #e67e22), fundo branco, cinzas para
  apoio. Contraste AA no mínimo.
- Números-âncora (1,132 bits; +17–26%; n_eff = 1.224; 93%; 1,8 estados;
  34 h; 0,99 bits) devem ter um tratamento tipográfico consistente e
  destacado — são o esqueleto da apresentação.
- Slides 4 e 4b (manchete e achado negativo) e slide 5 (n_eff) são os heróis:
  máximo espaço para figura + um take-away por slide; os demais podem ser
  mais densos.
- Fio condutor: adicionar na footline uma pergunta-guia por seção, discreta:
  "quanto ambiente há na leitura?" (slides 3–5) → "dá para remover?" (6) →
  "o que o sensor resolve?" (7) → "quando o envelhecimento aparece?" (8–8b) →
  "isso transfere entre bancadas?" (9–10). Além dela: número do slide/total.
- Slide de título: limpo, com título, autor, disciplina/PPGETI-UFC,
  orientador e data; sem imagem decorativa genérica.
- Slide 11 (ressalvas): design que comunique "honestidade deliberada" —
  não esconder num canto; pode usar o template de bloco de destaque.
- Backups após \appendix com numeração própria (não inflar o total do
  footline).

ENTREGA: (1) beamerthemeTFinfo.sty; (2) seminar.tex ajustado; (3) PDF
compilado; (4) changelog das mudanças no .tex. Se alguma restrição for
impossível no seu ambiente, pare e pergunte antes de contornar.
```

**Nota sobre o Claude Design:** ele é mais forte gerando design em
HTML/prototipagem do que editando Beamer diretamente. Se a resposta vier como
slides HTML, use-a como *referência visual* e peça em seguida: "agora traduza
este design para um beamerthemeTFinfo.sty com as mesmas cores, tipografia e
footline, mantendo o seminar.tex intacto". O prompt acima já induz a saída
correta, mas esse é o plano B.
