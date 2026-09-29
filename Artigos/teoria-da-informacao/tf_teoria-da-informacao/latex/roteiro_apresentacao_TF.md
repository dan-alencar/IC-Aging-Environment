# Roteiro de apresentação — TF TIP7266 (15 min)
### Alinhado ao deck final (`seminar.tex` + tema TFinfo): 13 slides numerados + 3 backups

> Como usar: os horários são o relógio acumulado. Não decorar palavra a
> palavra — decorar as frases em **negrito** (âncoras) e os quatro
> checkpoints. As perguntas-guia da footline marcam as transições de bloco;
> use-as como deixa falada ("a pergunta agora muda: ...").

---

## Checkpoints de relógio (colar no monitor de notas)

| Relógio | Você deve estar em |
|---|---|
| **3:30** | terminando a manchete do slide 4 (antes do achado negativo) |
| **6:00** | saindo do slide 5 (n_eff) |
| **9:45** | saindo do slide 8 (CRLB) |
| **13:00** | entrando no slide 13 (Contribuições) |

Se estourar 20 s num checkpoint: comprimir os slides **10 (KL)** e **11
(ICA)** — nunca o achado negativo (4) nem o fecho (13).

As 3 frases que não podem sair erradas: a **retração** (slide 4), o
**veredito MDL** (slide 6), o **fecho** (slide 13).

---

## O roteiro

**[0:00–0:15] Slide 1 — Título.**
"Bom dia. Este trabalho pega um sensor de envelhecimento que já existia na
minha pesquisa e faz uma única mudança de ponto de vista: **trata o sensor
como um canal de comunicação ruidoso — e mede tudo em bits.**"

**[0:15–1:15] Slide 2 — Problema & objetivo.**
"O trabalho anterior mede a contaminação ambiental com um R² linear: 0,74.
Dois problemas. Primeiro: R² só enxerga dependência **linear** — e a física
aqui tem risco real de não-linearidade: Arrhenius em temperatura, super-linear
em tensão; covariância zero não implica independência. Segundo: 'fração de
variância explicada' **não tem unidade transferível** — não responde quantos
estados o sensor resolve nem quando uma tendência é detectável. Objetivo:
substituir o R² por informação mútua e deixar entropia, capacidade e teoria de
estimação responderem o resto."

*(footline muda: "quanto ambiente há na leitura?")*

**[1:15–2:15] Slide 3 — O modelo de canal + os dados.**
"Uma equação: o slack reportado é o envelhecimento latente, menos a flutuação
reversível de temperatura e tensão, mais quantização. No vocabulário de canal:
**transmissor, ruído — e o receptor é o estimador de vida útil.** Os dados:
214 horas de campanha PID, 768 mil amostras a 1 Hz, 27 níveis de slack,
entropia total de 3,43 bits. **Esse é o orçamento de incerteza que vamos
fatiar**: quanto é ambiente, quanto é envelhecimento, quanto é piso."

**[2:15–3:30] Slide 4 — ★ A manchete.** *(desacelerar; apontar os números)*
"A informação mútua entre o slack e o ambiente: **1,13 bits por leitura** no
estimador por histograma, 1,22 no KSG — um terço da entropia do sensor é
ambiente. Se a dependência fosse exatamente a linear que o R² enxerga, seriam
0,97 bits — **a MI medida excede isso em 17 a 26%**. E não é viés de
estimador: o piso nulo por surrogates fica **12 vezes abaixo** do medido. Dois
estimadores de famílias diferentes, cada um com seu IC, e a divergência entre
eles reportada como faixa — não escolhemos o número mais bonito."

**[3:30–5:00] Slide 4 ainda — o achado negativo.** *(o bloco de 90 s; a
ressalva já está escrita no slide — leia a sala, não o slide)*
"Só que havia **duas ameaças** a esse excesso, e são diferentes. A primeira —
viés de estimador — o surrogate elimina: descontando até o pior caso do piso,
sobra excesso. A segunda é mais sutil: **envelhecimento e deriva lenta do
ambiente compartilham o eixo do tempo** em 214 horas, e a MI bruta conta essa
co-tendência como dependência. Refizemos a comparação inteira nas séries sem
tendência: o excesso **desaparece** — vira déficit de 11 a 19%. Conclusão
honesta, que está no resumo do artigo: **retiramos a leitura causal** 'a
física é não-linear'. O que fica de pé é estrutural: a MI não tem ponto cego
de linearidade, seja qual for a origem da dependência — e foi o nosso próprio
protocolo que encontrou e corrigiu a leitura errada. **O achado negativo é o
protocolo funcionando.**"

**[5:00–6:00] Slide 5 — O pilar da honestidade: n_eff.**
"Tudo isso só é honesto por causa de um número. 768 mil amostras a 1 Hz são
massivamente redundantes: o tempo de autocorrelação integrado — estimado por
janelamento de Sokal sobre o slack sem a deriva de 1 hora — é de 314 segundos.
Então as 768 mil amostras **valem 1.224 amostras independentes**. Usar o n
bruto encolheria toda barra de erro por um fator 25 — certeza falsa. **Cada
IC, o piso surrogate, o ajuste Bayesiano e o Kalman usam n_eff, não n.**"

*(footline: "dá para remover?")*

**[6:00–7:15] Slide 6 — Correção PVT.**
"Identificada a contaminação, removemos: ajuste de Δ_PVT e subtração. A
métrica de sucesso não é correlação zerada — mínimos quadrados zeram
correlação por construção — é **informação reversível residual**: de 0,66 para
0,046 bits, **93% do acoplamento removido**, resíduo no piso do estimador.
Entre o modelo linear e o não-linear físico, o MDL escolhe o linear:
**curvatura insuficiente neste ponto de operação para pagar os parâmetros
extras** — guardem essa frase, ela volta. E o efeito colateral que importa:
remover o ambiente **expõe** o envelhecimento — a correlação com o tempo
dobra, de −0,35 para −0,73."

*(footline: "o que o sensor resolve?")*

**[7:15–8:30] Slide 7 — Resolução efetiva & alarme.**
"Com o sinal limpo, duas perguntas de engenharia. Quantos estados o sensor
resolve? SNR de 2,4, capacidade de 0,87 bits, **1,8 estados de envelhecimento
distinguíveis** na campanha — heurística de resolução, não taxa de Shannon:
não há codificador na física. E o alarme 'houve envelhecimento?': por hora, o
canal binário é uma moeda — capacidade zero. **Por janela de 24 horas: 0,99
bits por decisão** — quase perfeito. E a transição não é acaso: alarme e
limite de detecção compartilham a mesma escala com a janela — três figuras de
mérito, uma física."

*(footline: "quando o envelhecimento aparece?")*

**[8:30–9:45] Slide 8 — Limite de detectabilidade.**
"Quando a tendência se torna detectável? Cramér–Rao: com este ruído e este
n_eff, a menor taxa detectável a 3 sigma é 1,2 mili-contagens por hora. A taxa
medida é **quinze vezes o piso**. Invertendo a mesma lei: seriam necessárias
**34 horas** de observação para detectar essa taxa — e as campanhas anteriores
tinham 23. **Eis, num único número, por que elas não separavam envelhecimento
de ruído.** A rota Bayesiana independente dá −18,2, intervalo de −19,2 a
−17,2 — frequentista e Bayesiano concordam. E a precisão importante: P de
**inclinação** negativa ≈ 100% — inclinação, não causa; a leitura como
envelhecimento é condicionada ao estudo de dispositivo único. Isto é um
**limite de detectabilidade, não predição de vida útil**."

**[9:45–10:45] Slide 9 — RUL como distribuição: Wiener/Kalman.**
"Mesma caixa de ferramentas, pergunta sequencial: modelamos o resíduo como
processo de Wiener e filtramos com Kalman. Dois resultados. O MLE do ruído de
taxa colapsa a zero — os dados preferem deriva constante — **terceira rota
independente confirmando o 'sem curvatura'** do MDL e da MI detrendizada. E a
primeira passagem dá a **distribuição completa** do tempo até o próximo marco:
Gaussiana inversa, média de 53 horas mas mediana de 8 — cauda pesada
exatamente porque estamos no regime de SNR baixo do slide anterior.
**Capacidade e RUL amarrados pelo mesmo mecanismo.**"

*(footline: "isso transfere entre bancadas?")*

**[10:45–11:30] Slide 10 — Fidelidade de bancada: KL/JS.** *(compressível)*
"A mesma moeda responde a pergunta de bancada — em **outro dispositivo**, dito
explicitamente. Bancada não-conforme contra referência PID: KL de 1,94 bits
numa direção, 1,01 na outra — a assimetria é a própria lição de que KL não é
métrica; a Jensen–Shannon, simétrica, dá 0,28 bits. E um refinamento: **o KL
empírico excede a forma fechada Gaussiana** — a bancada ruidosa injeta caudas
pesadas não-Gaussianas. Guardem: caudas pesadas."

**[11:30–12:15] Slide 11 — ICA.** *(compressível)*
"Caudas pesadas são exatamente o que o ICA precisa. Separação cega, sem
nenhuma forma funcional para o ambiente: o componente temporal recuperado bate
com o resíduo da regressão em **correlação 0,83** — 70% de variância
compartilhada. Mesmo espaço, **critérios opostos** — mínimos quadrados versus
independência — mesmo componente: a correção não é artefato do critério.
Separação parcial, 0,57 bits residuais — corroborativa, não desmistura limpa."

*(footline limpa)*

**[12:15–13:00] Slide 12 — Ressalvas de honestidade.**
"O que este trabalho **não** afirma — e está no painel: o excesso bruto não
sobrevive ao detrend, então não demonstramos não-linearidade instantânea;
dispositivo e regime únicos, então RUL é limite, não predição validada;
capacidade é heurística de resolução; ICA é corroborativo; o KL é em
dispositivo separado, nunca misturado; e toda inferência usa n_eff, não n. A
comparação de capacidade por regime não foi entregue — sem log bang-bang
pareado, o KL entre bancadas é o sucedâneo declarado, primeiro item de
trabalho futuro."

**[13:00–14:15] Slide 13 — Contribuições & conclusão.** *(desacelerar)*
"Três coisas que o trabalho anterior não podia enunciar. Uma **métrica de
contaminação em bits**, sem hipótese de forma funcional e transferível. Uma
**definição principiada de qualidade de burn-in**: minimizar a informação
mútua entre sensor e ambiente. E a **especificação do sensor**: limite de
resolução, limite honesto de RUL estendido a distribuição completa, e
recuperação de envelhecimento livre de modelo. Fecho: **R² diz que o ambiente
explica 74% da variância. A teoria da informação diz que ele escreve 1,13
bits em cada leitura — e desses, removemos 93%. Bits são transferíveis;
frações de variância não são.** Obrigado."

**[14:15–15:00] Folga** — respiro, e um segundo de silêncio antes das
perguntas.

---

## Q&A — para onde apontar

- **"Como τ_int foi estimado?"** → resposta completa na cabeça (Sokal sobre o
  slack detrendizado de 1 h, FFT, corte w ≥ 5τ; sensibilidade: n_eff ∝ 1/τ,
  sd do CRLB ∝ √τ). Apostila, Bloco 2.1.3.
- **"Cadê o bang-bang?"** → backup 1 do deck.
- **"O déficit detrendizado não prova sub-linearidade?"** → backup 2 (teto
  entrópico do resíduo quantizado).
- **"Isso cobre a ementa?"** → backup 3 (mapa núcleo → resultado).
- Demais perguntas: simulado P1–P15 da apostila (Bloco 3.6), respostas de
  ≤90 s cada.

## Ensaio

Três passadas: (1) com o roteiro na mão, sem cronômetro; (2) cronometrada por
checkpoint, anotando desvios; (3) gravada, sem roteiro — ouvir e reler o bloco
da apostila correspondente a cada travamento. O bloco do achado negativo
(3:30–5:00) merece um ensaio extra isolado: é o momento da defesa.
