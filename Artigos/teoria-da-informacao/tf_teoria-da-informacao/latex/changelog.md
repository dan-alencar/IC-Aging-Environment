# Changelog — redesign visual do deck TIP7266

## Arquivos novos
- `beamerthemeTFinfo.sty` — tema completo (cores, fontes, blocos, footline,
  título, painel `TFhonest`, macro `\guidequestion`, moldura `\figframe`).
  Requer só TeX Live: `FiraSans`, `newtxsf`, `appendixnumberbeamer`.
  Compila com pdflatex/latexmk, 16:9.

## Mudanças no seminar.tex (todas marcadas com `% [TFinfo]`)
1. **Linha 11:** `\usetheme{metropolis}` → `\usetheme{TFinfo}`.
2. **+6 linhas `\guidequestion{...}`** (fio condutor na footline; nenhum texto
   de slide alterado):
   - antes de "O modelo de canal + os dados": `quanto ambiente há na leitura?`
   - antes de "Correção PVT...": `dá para remover?`
   - antes de "Resolução efetiva...": `o que o sensor resolve?`
   - antes de "Limite de detectabilidade de RUL": `quando o envelhecimento aparece?`
   - antes de "Fidelidade de bancada...": `isso transfere entre bancadas?`
   - antes de "Ressalvas de honestidade": `\guidequestion{}` (limpa).
3. **Slide ★ MI (herói):** larguras das colunas `0.52/0.48` → `0.46/0.54`
   (mais espaço para a figura; texto intacto).
4. **Slide "Ressalvas de honestidade":** o `itemize` foi embrulhado em
   `\begin{TFhonest}...\end{TFhonest}` (painel de honestidade deliberada:
   régua laranja + fundo creme). Zero mudança de texto.

## O que NÃO mudou
- Nenhuma palavra, número, ordem de slide ou legenda. Todas as macros
  `\valXxx` e as de `notation.tex` intactas.
- Figuras: mesmos arquivos, sem regeneração; só o slide ★ MI ganhou coluna
  de figura maior.
- `\date{\today}` e `\institute{...}` como estavam. **Orientador não foi
  adicionado** (conteúdo congelado): se quiser, acrescente ao `\institute`.

## Comportamento herdado do tema
- Footline: pergunta-guia em itálico à esquerda + `n / total` à direita;
  o total exclui os backups (`appendixnumberbeamer`); backups mostram
  `backup n / total-backups`. Slide de título é `plain` e fora da contagem
  (numeração idêntica à do metropolis).
- `\alert{...}` = tratamento dos números-âncora: negrito + laranja-tinta
  `#A85A10` (AA sobre branco), casado com o laranja `#E67E22` das figuras.
- Blocos `block` = petróleo/cinza-névoa; `alertblock` = creme/laranja;
  `exampleblock` = verde-tinta `#18703D`.

## Build
`latexmk -pdf seminar.tex` (2+ passadas para o total da footline).
PDF não compilado aqui (sem TeX neste ambiente) — mockup HTML dos
slides-chave em `Mockup TFinfo.dc.html` para aprovação visual.
