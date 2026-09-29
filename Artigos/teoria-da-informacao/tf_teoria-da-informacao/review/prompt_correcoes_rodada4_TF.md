# Prompt — Correções pós-revisão independente (rodada 4)

> Cole este prompt em uma sessão com acesso ao repositório do TF. Origem: revisão
> independente de 19/08/2026 (executada sobre `main_pt.pdf` de 18/08, `values.tex`
> e os `.md` de planejamento). A revisão **não encontrou nenhuma divergência
> numérica** — 12 escalares centrais recomputados de primeiros princípios bateram
> com `values.tex` e com o PDF. Todas as correções abaixo são de **texto,
> legendas, citações e rotulagem**, não de análise. Nenhum resultado muda.

## Papel e regras

Você é um editor técnico executando correções pontuais e cirúrgicas. Regras:

1. **Edições atômicas**, uma por vez, via script Python ou `str_replace` — nunca
   reescrever parágrafos inteiros além do especificado em cada bloco.
2. **Contrato de reprodutibilidade intacto:** nenhum número entra na prosa
   digitado à mão. Se um bloco exigir um número novo, ele nasce no script de
   análise e chega ao LaTeX via macro em `latex/generated/values.tex`.
3. **Escopo:** apenas `main_pt.tex` + `sections_pt/` + `tables_pt/` +
   `analysis/make_figures.py` + `analysis/tier1_pipeline.py` (Bloco E) +
   `references.bib` + `seminar.tex`. O `main.tex` (inglês) continua fora de
   sincronia — **não tocar**; apenas registrar no `CLAUDE.md` que a rodada 4
   também não foi portada.
4. Commits no padrão Conventional Commits, um por bloco
   (ex.: `fix(latex): localiza cleveref para pt-BR (Bloco A)`).
5. Ao final, rodar a **verificação** da última seção e reportar o resultado de
   cada critério de aceite, item a item.

---

## Bloco A — Item 01 da rubrica: erros objetivos de texto (obrigatório)

**Problema.** O PDF impresso contém o conector inglês `and` em referências
cruzadas múltiplas — "seções 6.1 and 7", "seções 6.2 and 6.6", "seções 6.4 and
6.5" — bug de localização do `cleveref`. No §7.6 há adicionalmente erro de
concordância: **"na seções 6.1 and 7"**.

**Correção.**
1. No preâmbulo de `main_pt.tex`, garantir a localização do `cleveref`:
   carregar `\usepackage[portuguese]{cleveref}` **ou**, se a opção de idioma
   conflitar com o setup atual, redefinir explicitamente:
   ```latex
   \newcommand{\crefpairconjunction}{ e }
   \newcommand{\crefmiddleconjunction}{, }
   \newcommand{\creflastconjunction}{ e }
   \newcommand{\crefrangeconjunction}{ a }
   ```
   (usar `\renewcommand` se já definidos.)
2. Em `sections_pt/07_discussion.tex`, corrigir "na seções" → "nas seções"
   (buscar também "na figuras", "na tabelas", "no seções" por segurança).
3. Varrer `sections_pt/*.tex` por outros conectores não localizados
   (`ranges`, `\crefrange`) e conferir no PDF recompilado.

**Aceite A:** `pdftotext main_pt.pdf - | grep -nE "(seç|Seç)[^.]{0,40} and "`
retorna vazio; `grep -rn "na seções" sections_pt/` retorna vazio; as
referências bibliográficas em inglês permanecem intocadas.

## Bloco B — Item 04 da rubrica: legenda da Tabela 2 e rótulo da Figura 1 contradizem a retração (obrigatório)

**Problema.** O §6.1 e o §7.1 retratam a leitura causal ("excesso ⇒
não-linearidade instantânea"), mas a legenda da **Tabela 2** ainda afirma
"**evidenciando acoplamento não-linear**", e a anotação interna da **Figura 1**
rotula o excesso como "+17% (não-linear, série bruta)". Um leitor de legendas
encontra o artigo se contradizendo no ponto central.

**Correção.**
1. Em `tables_pt/mi_vs_r2.tex` (ou onde a legenda residir), substituir o trecho
   "..., evidenciando acoplamento não-linear" por linguagem pós-retração, p.ex.:
   "— um excesso real (sobrevive ao piso de viés do estimador), cuja atribuição
   à não-linearidade instantânea, porém, não sobrevive à remoção da tendência
   compartilhada (seções 6.1 e 7.1)."
2. Em `analysis/make_figures.py`, trocar o texto da anotação da Figura 1 de
   `+17% (não-linear, série bruta)` para `+17% (série bruta; atribuição: §7.1)`
   — mantendo o percentual vindo do mesmo valor que alimenta `\valMIexcessPct`,
   nunca hardcoded. Regenerar `figures/fig_mi.pdf` (ou nome equivalente).
3. A legenda da Figura 1 já remete à discussão — manter.
4. Recompilar também `seminar.tex` (o deck reusa a mesma figura).

**Aceite B:** `grep -rn "evidenciando acoplamento não-linear" tables_pt/ sections_pt/`
vazio; a figura regenerada não contém a palavra "não-linear" na anotação; os
demais elementos da figura (barras, tracejado, pontilhado, valores) idênticos.

## Bloco C — §6.5: "P(envelhecimento real)" é um salto de identificação (obrigatório)

**Problema.** O posterior Bayesiano dá P(inclinação < 0) ≈ 100%. O texto traduz
isso como probabilidade "de que o envelhecimento esteja presente" — mas
inclinação negativa ≠ causa envelhecimento (qualquer deriva lenta residual não
capturada por T, V medidos contaria). É a única frase do artigo em que a ressalva
de dispositivo único deveria ter sido re-invocada e não foi.

**Correção.**
1. Em `sections_pt/06_results.tex` (§6.5), reescrever a frase para manter a
   afirmação estatística e condicionar a leitura física, p.ex.:
   "e a probabilidade posterior de que a inclinação seja genuinamente negativa é
   de 100.00% — numericamente indistinguível de certeza; a leitura dessa deriva
   residual **como envelhecimento** permanece condicionada à hipótese de
   identificação deste estudo de dispositivo único (seção 7.6)."
   (o número continua vindo de `\valBayesPaging`.)
2. No deck (`seminar.tex`, slide do RUL), trocar
   "P(envelhecimento real) ≈ 100.00%" por "P(inclinação < 0) ≈ 100.00%".
3. Se `00_Work_Summary.md` §4 usar a formulação antiga, sincronizar.

**Aceite C:** nenhuma ocorrência de "P(aging real)" / "envelhecimento real"
associada ao posterior sem a condicional de identificação, em
`sections_pt/`, `seminar.tex` e `00_Work_Summary.md`.

## Bloco D — Item 08 da rubrica: bibliografia da disciplina ausente (obrigatório)

**Problema.** As seções 3.1–3.5 derivam material canônico (entropia, KL, MI,
codificação de fonte, capacidade) sem citar fonte alguma, e a seção de ICA
(§3.8, §6.7) não cita **nada** — num TF cuja súmula lista Cover & Thomas e
Hyvärinen/Oja/Karhunen na bibliografia.

**Correção.**
1. Adicionar a `references.bib`:
   - Cover & Thomas, *Elements of Information Theory*, 2ª ed., Wiley, 2006;
   - Hyvärinen, Karhunen & Oja, *Independent Component Analysis*, Wiley, 2001.
   (Opcional, juízo do autor: MacKay 2003 para a visão inferencial.)
2. Citar Cover & Thomas **uma vez por seção** nos pontos de primeira derivação:
   §3.1 (entropia), §3.2 (KL/MI), §3.4 (Kraft–McMillan/codificação de fonte),
   §3.5 (capacidade/BSC/Shannon–Hartley). Citar Hyvärinen et al. em §3.8
   (negentropia como contraste) e uma vez em §6.7 (FastICA). **Não** semear
   citações além disso — o objetivo é ancorar a teoria, não inflar.

**Aceite D:** `grep -c "cover2006\|hyvarinen2001" sections_pt/*.tex` ≥ 6;
`bibtex`/`biber` sem warnings de referência não usada ou faltante; as novas
entradas aparecem na lista de referências do PDF.

## Bloco E — §6.1: a faixa "17–26%" subdeclara a incerteza (recomendado)

**Problema.** 17–26% é o intervalo entre dois **pontos** estimados (binned e
KSG). Propagando os ICs de cada estimador, a faixa completa é ~13–32%
(binned: [1.091,1.176]/0.967 ⇒ +12.8% a +21.6%; KSG: [1.156,1.275]/0.967 ⇒
+19.5% a +31.9%). Nada muda qualitativamente — até o extremo inferior fica
acima do equivalente linear — mas a manchete deve dizer o que a faixa é.

**Correção (respeitando a regra 2 — números nascem no pipeline):**
1. Em `analysis/tier1_pipeline.py`, emitir quatro macros novas em `values.tex`:
   `\valMIexcessCiLoBinned` (13), `\valMIexcessCiHiBinned` (22),
   `\valMIexcessCiLoKSG` (20), `\valMIexcessCiHiKSG` (32) — arredondamento
   consistente com o padrão existente; os valores acima são o esperado para
   conferência, não para digitar.
2. Em `sections_pt/06_results.tex` (§6.1, parágrafo "O resultado de
   não-linearidade"), acrescentar **uma** frase após a faixa 17–26%:
   "essa faixa é o intervalo entre as estimativas pontuais dos dois
   estimadores; propagando o IC de cada um, o envelope completo é
   \valMIexcessCiLoBinned–\valMIexcessCiHiKSG\,%, cujo extremo inferior
   permanece acima do equivalente linear."
3. Rodar o pipeline e confirmar que **nenhum macro pré-existente mudou de
   valor** (diff de `values.tex` restrito às 4 linhas novas).

**Aceite E:** `git diff latex/generated/values.tex` mostra somente as 4 macros
novas; a frase nova usa somente macros; PDF recompila sem `??`.

## Bloco F — Anglicismos e uma frase do resumo (opcional, decisão do autor)

1. "camada de medição **information-teórica**" (resumo, §1, §8) →
   "**teórico-informacional**" ou "informacional". Se trocar, trocar em todas
   as ocorrências (`grep -rn "information-teóric" sections_pt/ main_pt.tex`)
   e no deck.
2. "detrendizada" / "denoised": manter é defensável (jargão consolidado no
   texto); se mantiver, padronizar itálico na primeira ocorrência de cada
   seção. Não converter termos dentro de legendas de figura sem regenerá-las.
3. Resumo: "um achado negativo que **reforça**, em vez de enfraquecer, o ponto
   metodológico central" — formulação mais generosa que o §7.1. Alternativa
   mais neutra: "um achado negativo que delimita com precisão o que o ponto
   metodológico central pode reivindicar: a informação mútua captura
   dependência que R² estruturalmente não vê, seja qual for sua origem."
   Decisão do autor; se alterar, sincronizar com o slide de contribuições.

**Aceite F:** apenas consistência — nenhuma ocorrência mista se a troca do
item 1 for feita; deck e paper com a mesma formulação escolhida no item 3.

---

## Verificação final (executar e reportar)

```bash
cd analysis && python3 tier1_pipeline.py            # Bloco E (se executado)
python3 make_figures.py                             # Bloco B
cd ../latex && latexmk -pdf main_pt.tex && latexmk -pdf seminar.tex

# Aceites automatizáveis:
pdftotext main_pt.pdf - | grep -nE "(seç|Seç)[^.]{0,40} and " || echo "A: OK"
grep -rn "na seções" sections_pt/ || echo "A2: OK"
grep -rn "evidenciando acoplamento não-linear" tables_pt/ sections_pt/ || echo "B: OK"
grep -rn "envelhecimento real" sections_pt/ seminar.tex                # C: inspecionar contexto
grep -c "cover2006\|hyvarinen2001" sections_pt/*.tex                   # D: >= 6
git diff --stat latex/generated/values.tex                             # E: só 4 linhas novas
```

Critérios transversais: (i) nenhum escalar pré-existente de `values.tex`
mudou; (ii) o PDF continua com o mesmo número de seções/figuras/tabelas;
(iii) `00_Work_Summary.md` e `06_Contribution_vs_Prior_Work.md` sincronizados
onde os Blocos C/F os afetarem; (iv) uma linha em `CLAUDE.md` registrando que
`main.tex` (EN) não recebeu a rodada 4.

**Lembrete:** o objetivo desta rodada é eliminar os quatro pontos que a revisão
identificou como risco de nota (itens 01, 04, 05-arguição e 08 da rubrica) sem
alterar uma vírgula da análise. Se qualquer edição exigir mudar um número,
pare e reporte — isso indicaria um problema que a revisão não viu.
