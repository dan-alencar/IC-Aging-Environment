# Prompt — Correções Finais do TF (TIP7266), rodada 3 (pré-submissão 22/08)

> Cole este prompt em uma sessão de trabalho **com acesso ao repositório completo** (`analysis/`, `latex/`, deck do seminário). Ele deriva da terceira rodada de revisão independente, feita sobre o PDF de 18/08 e o deck, com verificação contra `values.tex`. As correções das rodadas anteriores foram confirmadas como aplicadas; esta lista é **fechada e final** — 11 itens, sendo 1 único que exige rodar análise. Todos os demais são edição de texto/figuras.

---

## Papel e regras (idênticas às rodadas anteriores)

Você é o engenheiro de correção do artigo `latex/main.tex` (PT-BR), do pipeline `analysis/*.py` e do deck do seminário. Contrato de reprodutibilidade inegociável: nenhum número entra na prosa digitado à mão; todo escalar nasce em um script, vira `\newcommand` em `latex/generated/values.tex` e só então é usado. Edições de LaTeX aplicadas atomicamente via scripts Python. Commits em Conventional Commits, um por bloco. Após cada bloco: recompilar (`cd latex && latexmk -pdf main.tex`) e conferir o critério de aceitação.

---

## BLOCO A — O único item com análise: o KSG detrendizado (§6.1)

**Problema.** A §6.1 afirma, sobre a série detrendizada: "a MI medida com binning é 0.596 bits … e o KSG dá 0.656 bits". Não existe macro `\valMIdtKSG` em `values.tex`, e 0.656 coincide até a terceira casa com `\valPreMIrev{0.656}` — que é **outra grandeza** (MI binned detrendizada pré-correção, §6.2). Ou a seção reutiliza o macro errado, ou o número foi digitado; nos dois casos, o parágrafo mais importante do artigo (o achado negativo) contém um número não-rastreável.

**A.1 — Calcular o KSG detrendizado de verdade.**
- Em `tier1_pipeline.py`, aplicar o estimador KSG **exatamente à mesma série detrendizada** usada para `\valMIdtBinned{0.596}` (mesmo detrend, mesma padronização, mesma decimação usada na passada KSG bruta), emitindo `\valMIdtKSG` e, se o custo permitir, `\valMIdtKsgCiLo`/`\valMIdtKsgCiHi` pelo mesmo moving-block bootstrap do KSG bruto.
- Substituir o "0.656" da frase pelo macro novo. Emitir também `\valMIexcessPctDetrKSG` = `(MIdtKSG/0.736 − 1)·100` e reportar o déficit como faixa, simétrico ao tratamento do caso bruto (hoje o texto dá 17–26% para o bruto mas um único −19% para o detrendizado).
- **Fallback se o KSG detrendizado não puder ser computado a tempo:** remover a menção ao KSG dessa frase. O achado negativo se sustenta sozinho com o binned: IC [0.582, 0.632] inteiramente abaixo de 0.736.
- **Aceitação:** todo número da frase do achado negativo resolve para um macro de `values.tex`; `grep -rn "0\.656" latex/sections_pt/` só retorna usos legítimos de `\valPreMIrev` no contexto da §6.2.

**A.2 — Explicar 0.596 vs. 0.656.**
- Dois valores binned detrendizados de grandeza nominalmente igual diferem 0.06 bits: `\valMIdtBinned{0.596}` (§6.1) e `\valPreMIrev{0.656}` (§6.2). A §6.1 afirma usar "as séries detrendizadas usadas na correção PVT (seção 6.2)", o que os números desmentem. Inspecionar `tier1_pipeline.py` e identificar a diferença real de pré-processamento entre os dois cálculos (candidatos: detrend/padronização também de T,V no caminho da §6.1; discretização diferente do resíduo; janela). Adicionar **uma frase** na §6.1 declarando a diferença — por exemplo: "o valor difere do 0.656 da seção 6.2 porque lá apenas S é detrendizado, enquanto aqui [X]". Se a inspeção revelar que deveriam ser idênticos e não são, isso é um bug de pipeline: corrigir, reemitir, e propagar.
- **Aceitação:** um leitor consegue explicar por que os dois números diferem sem abrir o código.

## BLOCO B — Consistência pós-retratação (só texto)

**B.1 — Legenda da Figura 1.** Ainda fecha com "confirmando o acoplamento não-linear genuíno" — contradiz a retratação da §7.1. Trocar por: "confirmando acoplamento genuíno, muito acima do piso nulo (a atribuição do excesso é discutida na seção 7.1)". Ajustar em `make_figures.py`/caption conforme onde a string vive.

**B.2 — "Limite inferior" na Tabela 1 e na §5.** As duas ocorrências de "R² = 0.738 … é um limite inferior do verdadeiro acoplamento ambiental" afirmam algo que o próprio resultado detrendizado do artigo desmente como regra geral (para variável quantizada, a MI medida pode ficar abaixo do equivalente Gaussiano — foi exatamente o que a §6.1 mediu). Trocar por linguagem de hipótese/motivação: na Tabela 1, a coluna "Leitura" vira "motivação da análise de MI (seção 6.1)"; na prosa da §5, "é um limite inferior … e, portanto, a motivação central" vira "motivou a hipótese central deste trabalho — testada, e não confirmada, na seção 6.1".

**B.3 — §2.5, "precisamente a situação aqui".** Suavizar para "em princípio, a situação aqui" ou "precisamente o risco neste domínio" — a seção descreve corretamente a física e o ponto estrutural sobre R², mas após a §7.1 não se pode afirmar que este conjunto de dados instancia o caso.

**B.4 — Oração de cautela sobre o "déficit" (§6.1).** Após a frase do −19%, acrescentar uma oração qualificando a leitura, aproximadamente: "esse déficit numérico não deve ser lido como 'dependência menor que a linear' — o equivalente Gaussiano é um construto de variáveis contínuas, e para um resíduo quantizado em poucas contagens a MI discreta pode legitimamente ficar abaixo dele (teto entrópico do resíduo e viés descendente do estimador nesse regime); a leitura defensável é que nenhum excesso não-linear é resolvível acima do piso do estimador nesta série." Isso é também a resposta pronta para a pergunta de banca "como a MI pode ser *menor* que o equivalente do R²?".

- **Aceitação do bloco:** `grep -rn "limite inferior" latex/` não retorna a alegação sobre R²; a legenda da Figura 1 não contém "não-linear genuíno"; a §6.1 contém a oração de cautela.

## BLOCO C — Vírgulas decimais residuais (só texto)

Ocorrências restantes da convenção antiga, a trocar por ponto:
- §6.4: "p ≈ 0,49" → "p ≈ 0.49"; conferir o "CBSC ≈ 0" adjacente.
- §3.5: "p = 0,5" → "p = 0.5".
- §6.2: "+0,00" e "−0,00" → "+0.00" / "−0.00".
- §4.1: "1,0 h" → "1.0 h".
- Varredura final: `grep -rnE "[0-9],[0-9]" latex/sections_pt/ latex/tables_pt/` e triar manualmente (o separador de milhar "1{,}224" e datas são legítimos).
- **Aceitação:** a varredura só retorna milhares e datas.

## BLOCO D — Deck do seminário

**D.1 — Slide 7, CrI invertido.** "[−17.2, −19.2]" → "[−19.2, −17.2] m-cnt/h". É o mesmo bug já corrigido no paper; se o deck não consome `values.tex`, considerar passá-lo a consumir (os macros `\valBayesSlopeLo/Hi` já existem) — senão, corrigir o literal.

**D.2 — Slide 12, takeaway.** "R² says the environment explains 74% of the variance. Information theory says it writes 1.132 bits into every reading — and we remove 93% of them" mistura grandezas: o 93% remove os **0.656 bits reversíveis detrendizados** (§6.2), não os 1.132 brutos. Reescrever preservando o punch: "R² says the environment explains 74% of the variance. Information theory says it writes ~1.1 bits into every reading — and, of the reversible coupling, we strip 93%. Bits transfer; variance fractions don't."

**D.3 — Layout.** Slide 3: título do gráfico transborda/corta ("…R² (s") e a legenda colide com a anotação; slide 9: título e legenda apertados. Gerar variantes das figuras para o deck em `make_figures.py` (sufixo `_slide`) com `figsize` mais largo, fontes maiores e `tight_layout`/`constrained_layout`, em vez de reescalar os PDFs do paper.

**D.4 — Idioma.** Deck em inglês, figuras em português. Decidir pela língua da apresentação e unificar: se o seminário for em português, traduzir os slides (os títulos técnicos podem permanecer em inglês onde forem jargão consagrado); se for em inglês, gerar as variantes `_slide` das figuras com rótulos em inglês. Não manter o meio-termo.

- **Aceitação do bloco:** nenhum intervalo invertido no deck; takeaway com grandezas corretas; nenhuma figura com título cortado ou legenda sobreposta em projeção 16:9; idioma único.

## Checklist de saída (rodar por último, na ordem)

1. `cd analysis && python3 tier1_pipeline.py` (Bloco A) e demais scripts **apenas se tocados**; conferir que `values.tex` ganhou `\valMIdtKSG` (e CI, se computado) e que nenhum macro pré-existente mudou de valor sem motivo.
2. `cd latex && latexmk -pdf main.tex` limpo.
3. Verificação de rastreabilidade: nenhum número novo na prosa sem macro; `grep -rn "0\.656\|limite inferior\|não-linear genuíno" latex/sections_pt/` só retorna usos legítimos.
4. Varredura de vírgulas (Bloco C).
5. Recompilar o deck; revisar os 14 slides projetados em 16:9 (não no editor) para caça a overflow.
6. Ensaio de tempo: 12 slides + 2 backups em ≤ 12 min de fala, reservando 3 min para perguntas — com as respostas dos itens B.4 (déficit) e do backup bang-bang ensaiadas.

**Restrição final, idêntica às rodadas anteriores:** nenhuma dessas correções altera conclusões. O achado negativo e sua integração já estão certos; o objetivo desta rodada é eliminar os últimos pontos onde texto, figuras ou deck dizem algo que o pipeline não sustenta — e deixar o autor com as duas respostas de banca (déficit e capacidade por regime) prontas.
