# Contexto do Syllabus — TIP7266 Teoria da Informação (PGETI/UFC, 2026.1)

> Fonte: `material/Sumula Teoria_da_Informacao - TIP-7266-2026-1.pdf`. Serve para que a análise crítica julgue *pertinência* e *profundidade* do TF em relação ao que a disciplina realmente cobre — nem mais nem menos do que o programa declara.

## 1. Ementa (o que a disciplina promete cobrir)

Sistemas de comunicação e teoria da informação de forma ampla; medidas de informação e entropia; modelo matemático da informação; mecanismos de transmissão da informação (Telecom); transformações e filtragens; teorema de Shannon; taxa de distorção; compressão de dados; aquisição de dados com Big Data e IA.

## 2. Objetivos

**Geral:** habilitar os alunos a reconhecer quais técnicas se aplicam para adquirir dados com informação relevante e quais mecanismos agregam valor ao dado (fontes de codificação, modelos de fontes, compressão, denoise).

**Específicos:**
- Apresentar teoria da informação;
- Limites da comunicação, algoritmos de Shannon;
- Métricas e parâmetros para extração de informação dos dados;
- Técnicas de compressão e otimização de canal;
- Apresentar ferramentas de Big Data e IA para tratamento de dados.

## 3. Núcleos de conteúdo (programa completo, na ordem do documento)

1. **Princípios de sistema de comunicação e da teoria da informação** — introdução aos sistemas de comunicação e à teoria da informação; limites da comunicação: codificação de fonte, capacidade de canal, codificação de canal.
2. **Medida da informação** — modelo matemático da informação; informação mútua; entropia, entropia conjunta e condicional, informação média.
3. **Transmissão da informação** — tipos de fontes, modelos de transmissão conforme a fonte, DeNoise, modelos de canais, teorema de Shannon; Divergência de Kullback-Leibler (KLD); taxa de distorção; codificação de canais, compressão de dados (teorema de Huffman), codificação de Lempel-Ziv; capacidade de canais (canal BSC), Teorema da Capacidade de Informação (limite de Shannon).
4. **Complexidade de Kolmogorov, medida de confiabilidade de transmissão; medidas de otimização e estimação do sinal** — método dos momentos, mínimos quadrados, MLE, método bayesiano, uso de fdp; Independent Component Analysis (ICA); medidas de independência/gaussianidade; aproximações da negentropia; separação cega de fontes.
5. **Técnicas de Big Data e IA para tratamento de dados** — MapReduce, Streaming Processing, Spark, IA para extração de features.

## 4. Metodologia da disciplina

Aulas dialogadas e práticas (VMs), trabalho em grupo para TLs, artigos em formato científico, seminários. TF é a exceção explícita: **individual**.

## 5. Bibliografia declarada

**Básica:** Cover & Thomas (*Elements of Information Theory*); Haykin (*Neural Networks and Learning Machines*); Yeung (*Information Theory and Network Coding*); Ruiz/Pérez/Bonev (*Information Theory in Computer Vision and Pattern Recognition*); Goodfellow/Bengio/Courville (*Deep Learning*); Leskovec/Rajaraman/Ullman (*Mining of Massive Datasets*).

**Complementar:** Deco & Obradovic; Gallager (*Information Theory and Reliable Communication*); MacKay (*Information Theory, Inference and Learning Algorithms*); Hyvärinen/Oja/Karhunen (*Independent Component Analysis*); Nielsen & Chuang (*Computação Quântica e Informação Quântica*); Mañé (*Teoria Ergódica*); Ash (*Information Theory*); Kullback (*Information Theory and Statistics*); "artigos da área".

## 6. Mapeamento núcleo → o que o TF alega usar

(Cruzar com `03_Course_Topic_Mapping.md` do próprio TF para checar se a alegação é fiel.)

| Núcleo do syllabus | Coberto pelo TF? (alegação do próprio trabalho) |
|---|---|
| 1. Limites da comunicação (codificação de fonte, capacidade de canal, codificação de canal) | Sim — capacidade de canal usada; codificação de fonte citada apenas como limite teórico (`H(S)` como cota), sem codec implementado |
| 2. Medida da informação (entropia, entropia conjunta/condicional, informação mútua) | Sim — núcleo central do trabalho |
| 3. Transmissão (DeNoise, Shannon, KLD, capacidade/BSC) | Sim — DeNoise = correção PVT; KLD e JS entre bancadas; canal BSC para alarme de envelhecimento |
| 3. Compressão de dados (Huffman), codificação de Lempel-Ziv | **Não usado** — decisão de escopo explícita do TF |
| 4. Kolmogorov / MDL, estimação (momentos, MQ, MLE, bayesiano), ICA/negentropia/separação cega | Sim — usado extensivamente (MDL/BIC, OLS/GLS, MLE, momentos, bayesiano, Cramér-Rao, ICA) |
| 5. Big Data / IA (MapReduce, Streaming, Spark) | **Não usado** — decisão de escopo explícita do TF |

**Ponto para a análise crítica avaliar:** os núcleos 1 (parcial) e 5 (integral) do programa da disciplina são conscientemente deixados de fora pelo TF, com justificativa própria de "correlação fraca com o problema de pesquisa" (ver `00_Work_Summary.md`, seção 3, "Deliberately NOT used"). Isso é uma escolha de escopo legítima para um TF ligado à pesquisa de doutorado/mestrado do aluno — mas a revisão deve julgar se essa omissão compromete o item 03 da rubrica ("metodologia adequada") ou se é suficientemente justificada no texto para não ser penalizada.
