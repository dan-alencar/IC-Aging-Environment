# Prompt — Correções e Aperfeiçoamentos do TF (TIP7266) pós-revisão independente

> Cole este prompt em uma sessão de trabalho **com acesso ao repositório completo** (`analysis/`, `latex/`, `material/`). Ele deriva de uma revisão acadêmica independente cujos achados foram verificados contra `results.json`, `results_kalman.json` e `values.tex`. Prazo de referência: submissão em **22/08/2026** — priorize P0 > P1 > P2; P2 só se sobrar tempo, pois exige reexecutar análise.

---

## Papel

Você é o engenheiro de correção do artigo final `latex/main.tex` (PT-BR) e do pipeline `analysis/*.py`. Seu trabalho é aplicar as correções abaixo **sem quebrar o contrato de reprodutibilidade**: nenhum número entra na prosa digitado à mão; todo escalar novo nasce em um script de `analysis/`, é emitido como `\newcommand` em `latex/generated/values.tex` e só então usado no `.tex`. Edições de LaTeX são aplicadas atomicamente via scripts Python (nunca edição manual solta). Commits em Conventional Commits. Ao final de cada bloco, recompile (`cd latex && latexmk -pdf main.tex`) e verifique o critério de aceitação.

## Contexto dos achados (resumo do parecer)

1. O resultado-manchete "+26%" é calculado pelo pipeline a partir do estimador **KSG** (`excess_pct = 26.319` = 1.2211/0.9667), mas o resumo e a Figura 1 o anexam ao valor **binned** (1.132 bits, cujo excesso real é **+17.05%**). Causa-raiz: existe um único macro `\valMIexcessPct{26}`.
2. A metodologia (§4.2 do PDF e `02_Methodology.md` §3.1) promete MI-vs-ambiente sobre a série **detrendizada**, mas o manchete 1.132 bits é da série **bruta** (o MI reversível detrendizado pré-correção é 0.656 bits, campo separado em `results.json`). A comparação bruta-vs-R²-bruto é válida (maçã-com-maçã), mas o texto não declara qual série sustenta qual número.
3. §3.3 alega "evitando qualquer escolha arbitrária de binning", porém `results.json` registra `bins: 16` (discretização de T,V) e `bin_sensitivity = [1.111, 1.156, 1.171]` — sensibilidade computada e **não reportada**, com faixa (~0.06 bits) comparável à largura do IC bootstrap.
4. O KSG (1.221) está **fora** do IC bootstrap do binned ([1.091, 1.176]); chamar isso de "concordância/robustez" é forte demais.
5. `\valHscondTV{2.298}` existe mas H(S|T,V) não é impresso em lugar nenhum do PDF — e a promessa 2 do projeto é literalmente "comparar H(S) a H(S|T,V)".
6. O CrI Bayesiano aparece invertido na prosa da §6.5: "[−17.2, −19.2]" (os macros `\valBayesSlopeLo{-19.2}`/`\valBayesSlopeHi{-17.2}` estão corretos; o bug é a ordem no template da seção).
7. O "1,67 bits" (KL Gaussiana fechada, §6.3) **não existe** em `results.json` nem em `values.tex` — número órfão que viola o contrato de reprodutibilidade. Recomputação independente dá ~1.66 com os σ arredondados.
8. Separador decimal inconsistente em todo o documento (ex.: "19.85 ps" na §2.1 vs "19,85 ps" na §3.3; "3.43" vs "0,73").
9. Figuras inteiramente em inglês num artigo em português.
10. Formulações sobrevendidas: (a) ICA "sem usar **nada** do acoplamento T,V" — o ICA recebe (S,T,V) e busca no mesmo espaço linear 3D da regressão; (b) "recuperar **83%** do sinal" confunde |corr|=0.834 com fração de sinal (variância compartilhada = 0.834² ≈ 70%); (c) §7.1 "isso **implica** que a comparação anterior subestima a diferença entre regimes" — extrapolação de regime único.
11. Promessa 3 do `01_Project_Overview.md` §3 (capacidade **bang-bang vs. PID**) foi entregue só em versão single-regime; o descope está declarado, mas a defesa no seminário precisa antecipar a pergunta.
12. O deck do seminário ainda não tem o slide da extensão Wiener/Kalman (pendência do `05_Execution_Plan.md` §4).

---

## P0 — Correções obrigatórias antes da submissão (só texto + macros novos; nada de reexecutar campanhas)

### P0.1 — Resolver o "+26%"
- Em `tier1_pipeline.py`, emitir **dois** excessos: `excess_pct_ksg` (atual 26.3) e `excess_pct_binned` = `(I_STV/mi_lin_equiv − 1)·100` (= 17.05). Emitir macros `\valMIexcessPctKSG` e `\valMIexcessPctBinned`; manter `\valMIexcessPct` como alias do escolhido para o manchete, documentado em comentário.
- **Política de reporte (adotar e aplicar):** o manchete usa o par consistente. Recomendação: manchete = binned (+17%), porque é o estimador com IC reportado; o KSG entra como verificação com seu próprio excesso (+26%), formulado como faixa: "o excesso não-linear é de **17–26%** conforme o estimador".
- Corrigir: resumo, §6.1 ("A dependência medida (1.221 bits) excede…" — hoje usa o KSG sem dizer), §7.1, Tabela 2 (caption), e a anotação da Figura 1 em `make_figures.py` (hoje "+26%" aponta para a barra de 1.13 — trocar por "+17%" ou anotar as duas).
- **Aceitação:** nenhum lugar do PDF anexa 26% ao valor 1.13; grep por `26` em `sections_pt/` só retorna usos corretos.

### P0.2 — Declarar bruta vs. detrendizada
- Na §6.1, adicionar uma frase explícita: o manchete I(S;T,V)=1.132 é sobre a série **pós-soak bruta**, comparável ao R²=0.738 calculado sobre a mesma série; o acoplamento **reversível** (detrendizado) é 0.656 bits e é a grandeza usada na avaliação da correção (§6.2).
- Na §4.2, corrigir a promessa: o detrending se aplica à análise do acoplamento reversível e à avaliação da correção — não ao manchete, que é deliberadamente bruto para parear com o R² do trabalho anterior.
- **Aceitação:** um leitor consegue dizer, para cada número de MI do artigo, qual série o sustenta.

### P0.3 — Sensibilidade de binning
- Restringir a alegação da §3.3: o eixo **S** usa níveis inteiros nativos; **T,V são contínuos e foram discretizados (16 bins)** — remover "evitando qualquer escolha arbitrária de binning" ou qualificá-la.
- Emitir macros da sensibilidade (`\valMIbins{16}`, `\valMIbinSensLo{1.111}`, `\valMIbinSensHi{1.171}`) e reportar em uma frase na §6.1 ou na validação (§4.6): a faixa de sensibilidade contém o valor reportado e não altera nenhuma conclusão (até o mínimo, 1.111, excede 0.967 + piso surrogate).
- **Aceitação:** a sensibilidade computada aparece no PDF; a alegação da §3.3 é factual.

### P0.4 — Reformular "concordância entre estimadores"
- Onde o texto diz que binned e KSG "concordam" como evidência de robustez (§4.2/§6.1), reformular: os dois estimadores **chegam à mesma conclusão qualitativa** (dependência ≫ piso; excesso sobre o equivalente Gaussiano positivo), mas diferem além do IC bootstrap do binned (1.221 ∉ [1.091, 1.176]) — diferença sistemática esperada entre um estimador com binning e um kNN, tratada como incerteza de estimador e origem da faixa 17–26% do P0.1.
- **Aceitação:** nenhuma frase alega concordância numérica entre estimadores que o IC contradiz.

### P0.5 — Imprimir H(S|T,V)
- Adicionar linha "H(S | T,V) = 2.298 bits" (`\valHscondTV`) à Tabela 2, logo abaixo de H(S), fechando visivelmente a identidade I = H(S) − H(S|T,V).
- **Aceitação:** 3.43 − 2.30 ≈ 1.13 verificável pelo leitor na própria tabela.

### P0.6 — Ordem do CrI na §6.5
- Corrigir para "[−19.2, −17.2] m-cnt/h" (usar `[\valBayesSlopeLo, \valBayesSlopeHi]` no template).
- **Aceitação:** limite inferior < superior em todos os intervalos do PDF (conferir também [33, 36] h — este está correto).

### P0.7 — Rastrear o "1,67 bits"
- Em `kl_benches.py`, calcular a KL Gaussiana fechada de média nula `[ln(σ_PID/σ_SBCCI) + σ²_SBCCI/(2σ²_PID) − ½]/ln 2` com os σ **não arredondados**, emitir `\valKLgauss`, e usar o macro na §6.3.
- **Aceitação:** o número impresso vem do macro; se divergir do 1.67 atual (recomputação dá ~1.66 com σ arredondados), o texto acompanha o valor do pipeline.

### P0.8 — Separador decimal
- Adotar **uma** convenção e aplicá-la: recomendação prática, dado o pipeline (Python emite ponto), é ponto em todo o documento com uma nota de convenção na primeira ocorrência; alternativa mais correta para PT-BR é vírgula via `siunitx` (`\num` com `locale`), mas exige envolver todos os macros — só faça se o tempo permitir. Corrigir em especial o LSB (19.85 vs 19,85) e os pares "0,73/0.84".
- **Aceitação:** grep não encontra a mesma grandeza com os dois separadores.

### P0.9 — Formulações sobrevendidas
- §6.7/Fig. 6: trocar "sem usar nada do acoplamento T,V" por "sem usar o **critério de ajuste** aos alvos T,V" e acrescentar meia frase honesta: regressão e ICA buscam no mesmo espaço linear de (S,T,V), por critérios distintos (MMQ vs. independência/não-Gaussianidade), de modo que a corroboração é de **critério**, não de espaço de busca.
- Trocar "recuperar 83% do sinal" por "|corr| = 0.834 (≈70% de variância compartilhada)".
- §7.1: trocar "implica" por "sugere", mantendo a ressalva já existente de que a comparação pareada exigiria execução no mesmo dispositivo.
- **Aceitação:** as três formulações corrigidas; nenhuma conclusão numérica alterada.

---

## P1 — Aperfeiçoamentos recomendados (pequenas adições de pipeline; reexecução barata dos scripts, sem novos dados)

### P1.1 — Excesso descontado do piso surrogate
- O artigo mede o viés do estimador sob independência (média 0.069 bits) mas nunca o desconta do **excesso** sobre o equivalente Gaussiano — e o excesso binned (0.165 bits) é da mesma ordem de poucas vezes esse piso. Emitir `\valMIexcessFloorAdj` = excesso binned − `mi_null_mean` e reportar em uma frase na §6.1: mesmo descontando o viés médio do estimador, o excesso permanece positivo (~0.10 bits / ~+10%). Isso transforma a maior fragilidade do manchete em demonstração de rigor.

### P1.2 — Par detrendizado completo
- Calcular em `tier1_pipeline.py` o **R² detrendizado** (mesma regressão sobre a série detrendizada que produz o 0.656) e o equivalente Gaussiano correspondente; reportar o par (MI 0.656 vs. R²_detr) como nota na §6.1 ou §6.2. Fecha de vez a ambiguidade do P0.2 e antecipa a pergunta óbvia da banca ("e detrendizado, o excesso não-linear sobrevive?").

### P1.3 — Figuras em português
- Em `make_figures.py`, traduzir títulos, legendas e eixos das 6 figuras (ou declarar em nota que as figuras estão em inglês por reuso em publicação futura — escolha uma das duas, não o meio-termo atual).

### P1.4 — Defesa da promessa 3 (capacidade por regime)
- Acrescentar meia frase na Conclusão/Trabalhos Futuros conectando explicitamente: a proposta original previa capacidade **por regime térmico**; sem log bruto bang-bang (cf. comentário em `values.tex`), este trabalho entrega a capacidade no regime PID e a comparação distribucional KL/JS como sucedâneo, e a campanha bang-bang pareada é o primeiro item de trabalho futuro. Preparar 1 slide de resposta para o seminário com esse encadeamento.

### P1.5 — Slide Wiener/Kalman no deck
- Pendência declarada no `05_Execution_Plan.md` §4: um slide com (i) trajetória suavizada + bandas (Fig. 5a), (ii) distribuição IG de RUL (Fig. 5b), (iii) a dupla confirmação de simplicidade (MDL + colapso do σ²_rate).

---

## P2 — Opcional, se houver tempo (altera metodologia; exige reexecução com análise nova)

### P2.1 — IC bootstrap para o KSG
- Rodar o mesmo moving-block bootstrap sobre o estimador KSG e reportar os dois ICs lado a lado. Se os ICs não se sobrepuserem, a diferença sistemática entre estimadores fica **caracterizada** (não só admitida), e a faixa 17–26% ganha barras de erro próprias. Custo: tempo de máquina (KSG é O(n log n) por réplica — decimar para n_eff antes, como já se faz no Bayes).

### P2.2 — Excesso não-linear na série detrendizada com IC
- Extensão do P1.2: bootstrap do excesso detrendizado. Se positivo com IC excluindo zero, o resultado central fica imune à crítica de confusão tendência/ambiente. Se **não** sobreviver, isso é um achado a reportar honestamente (o excesso não-linear se concentra na interação com a deriva) — o artigo já tem a cultura de reportar resultados negativos (σ²_rate, MDL); este entraria no mesmo espírito.

### P2.3 — Vírgula decimal via siunitx
- Versão completa do P0.8: envolver todos os macros numéricos em `\num{}` com `locale` PT. Mecânico, mas toca ~120 macros e todo o texto; só com folga de prazo e diff revisado.

---

## Ordem de execução e validação final

1. P0.1 → P0.2 → P0.4 (são o mesmo nó: o manchete) em um commit; depois P0.3, P0.5–P0.9 em commits atômicos separados; P1 na sequência; P2 somente com P0+P1 fechados.
2. Após cada commit: `python3 tier1_pipeline.py && python3 kl_benches.py && python3 make_figures.py` (e `ica_separation.py`/`kalman_rul.py` apenas se tocados), recompilar o PDF, e conferir o critério de aceitação do item.
3. **Checklist de saída (rodar por último):**
   - [ ] Nenhum número no PDF sem macro correspondente em `values.tex` (grep por dígitos soltos nas seções).
   - [ ] "+26%"/"+17%" anexados aos estimadores corretos em resumo, §6.1, §7.1, Tabela 2 e Figura 1.
   - [ ] Todos os intervalos em ordem crescente.
   - [ ] Separador decimal único.
   - [ ] `latexmk` limpo, 4–20 páginas conforme especificação da disciplina, referências intactas.
   - [ ] Deck com o slide Wiener/Kalman e o slide de resposta da promessa 3.

**Restrição final:** nenhuma dessas correções altera conclusões — a evidência bruta sustenta o mérito do trabalho. O objetivo é alinhar texto, figuras e pipeline para que a alegação central seja exatamente tão forte quanto os dados permitem, nem mais, nem menos.
