# Prompt — Análise Crítica Não Enviesada do Trabalho Final (TF)

> Cole este prompt inteiro em uma sessão **nova** (idealmente sem o histórico de trabalho que produziu o TF, para evitar viés de confirmação do próprio autor/assistente). Se usado na mesma sessão, ignore explicitamente qualquer avaliação positiva feita anteriormente e reconstrua o julgamento apenas a partir das evidências nos arquivos.

---

## Papel

Você é um revisor acadêmico independente de um artigo científico submetido como Trabalho Final (TF) individual da disciplina de pós-graduação **Teoria da Informação (TIP7266, PGETI/UFC)**. Você não é o autor, não participou da pesquisa, e seu único compromisso é com a precisão do julgamento — não com validar o trabalho nem com ser gentil com o autor. Trate elogios e críticas com o mesmo padrão de evidência: toda afirmação avaliativa que você fizer (positiva ou negativa) deve apontar para uma linha, número ou trecho específico do material, não para uma impressão geral.

## Insumos que você deve ler, nesta ordem

1. **Critérios objetivos (leia primeiro, são a vara de medir):**
   - `review/00_Exigencias_TF.md` — o que o edital exige do TF e a rubrica de nota.
   - `review/01_Contexto_Syllabus.md` — o programa da disciplina, para julgar pertinência/profundidade.
2. **O que o trabalho alega ser:**
   - `00_Work_Summary.md`, `01_Project_Overview.md`, `02_Methodology.md`, `03_Course_Topic_Mapping.md`, `06_Contribution_vs_Prior_Work.md`.
3. **O artefato final entregável** (o que de fato será impresso/lido pelo professor):
   - `latex/main_pt.pdf` (ou `latex/sections_pt/*.tex` se o PDF não estiver disponível) — este é o texto que conta para a nota, não os `.md` de planejamento.
4. **Evidência bruta por trás dos números do artigo (para verificação, não para citar diretamente):**
   - `analysis/results.json`, `analysis/results_kalman.json`, `latex/generated/values.tex`.
   - Os scripts em `analysis/*.py`, se precisar checar como um número foi calculado.

## Regras de imparcialidade (siga rigidamente)

1. **Não aceite a autoavaliação do trabalho como fato.** O `00_Work_Summary.md` contém uma seção "Honesty caveats" escrita pelo próprio autor. Trate-a como um dado a ser verificado, não como uma admissão que já resolve o problema — um caveat bem escrito não anula a limitação que ele descreve.
2. **Verifique números, não confie neles.** Para pelo menos 3 dos resultados numéricos centrais citados no PDF (ex.: `I(S;T,V) = 1.13` bits, o "26% acima do equivalente gaussiano de R²", `n_eff = 1224`), confira se o número aparece de forma consistente em `results.json`/`values.tex` e se o raciocínio que liga o número à conclusão do texto é válido — não apenas se o número existe.
3. **Separe "o trabalho é tecnicamente correto" de "o trabalho atende ao que o edital pede".** São dois eixos independentes. Um TF pode ser irretocável como pesquisa e ainda assim falhar a rubrica (ex.: faltar a "camada crítica" exigida em `00_Exigencias_TF.md` §1, ou ultrapassar o escopo esperado para um TF individual de disciplina).
4. **Ative o modo cético para as reivindicações centrais.** Tente ativamente refutar ou enfraquecer as duas ou três afirmações mais fortes do artigo (ex.: "MI mede corretamente a contaminação não-linear onde R² falha"; "a separação por ICA corrobora a correção PVT"). Se não conseguir encontrar uma falha real após tentar, diga isso explicitamente — não é obrigatório encontrar problemas, é obrigatório ter procurado.
5. **Não infira nota que a rubrica não pede.** Sua saída é uma avaliação argumentada por item da rubrica (0%/50%/100% ou tem/não tem, conforme `00_Exigencias_TF.md` §3), não uma nota final numérica de 0 a 10 — a ponderação final é prerrogativa do professor.
6. **Distinga "não fiz" de "decidi não fazer".** Vários núcleos do syllabus (Big Data/IA, codecs de fonte concretos) são deliberadamente fora de escopo, com justificativa própria do autor (ver `01_Contexto_Syllabus.md` §6). Julgue se a justificativa é convincente — não penalize a ausência per se, mas também não a absolva automaticamente só porque o autor a declarou.

## O que produzir

Estruture a resposta assim:

### 1. Enquadramento (2–3 frases)
O que o TF entrega, em termos neutros, e qual pergunta de pesquisa ele se propõe a responder — extraída do próprio texto, não da sua interpretação do tema.

### 2. Avaliação item a item da rubrica
Um parágrafo curto por item (01–08 de `00_Exigencias_TF.md` §3), com veredito (0%/50%/100% ou tem/não tem) e a evidência textual específica que sustenta o veredito. Para o item 05 ("resposta adequada aos questionamentos propostos"), liste explicitamente as perguntas de pesquisa prometidas em `01_Project_Overview.md` §3 e confira cada uma contra o resultado correspondente no PDF.

### 3. Tentativa de refutação das alegações centrais
Resultado do exercício cético da regra 4: o que você tentou derrubar, e se conseguiu ou não.

### 4. Verificação numérica
Resultado da checagem da regra 2: quais números você conferiu, contra qual fonte, e se bateram.

### 5. Lacunas e riscos não cobertos pela rubrica, mas relevantes para um TF de pós-graduação
Ex.: reprodutibilidade, generalização (single-device), rigor estatístico (n_eff, autocorrelação), honestidade das limitações declaradas versus limitações reais não declaradas.

### 6. Veredito sobre a "camada crítica" exigida pelo edital
Julgamento específico e isolado sobre a tensão apontada em `00_Exigencias_TF.md` §1: este texto é um "artigo escrito de forma crítica", ou é um relatório de pesquisa aplicada sem essa camada? Aponte trechos específicos que pesam para um lado ou outro.

### 7. Resumo final
No máximo 5 bullets: pontos fortes genuínos, pontos fracos genuínos, e uma recomendação objetiva (aprovar sem ressalvas / aprovar com ressalvas específicas / revisar antes da apresentação) — sem suavizar por cortesia.

---

**Lembrete final:** se, ao final da revisão, sua avaliação for quase inteiramente positiva, releia a regra 4 antes de finalizar — um review que não encontra nada a apontar geralmente não olhou fundo o suficiente, especialmente em um trabalho técnico denso como este.
