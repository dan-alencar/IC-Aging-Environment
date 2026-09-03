# analysis/ — Análise offline

*[Read in English](README.md)*

Vazio por enquanto. Este é o espaço de trabalho da frente F6 (caracterização, dados e
produção científica — Seção 4.6 do documento de plano): decomposição de variância
PVT do sinal de *slack*, estimação de σ_resid com incerteza declarada, ajuste de
modelo de degradação, e a comparação sistemática Artix-7 vs. MAX10.

**Requisito de compatibilidade (do plano, e vale repetir aqui):** o formato de CSV
produzido por `host/` precisa se manter compatível com o *pipeline* que já processa a
saída de `App_Nexys`/`App_2Nexys`, para que os números de σ_resid das duas
plataformas sejam calculados da mesma forma e sejam de fato comparáveis. Se um
*notebook* de análise específico do MAX10 divergir das premissas do *pipeline*
existente, documente exatamente onde e por quê neste diretório, não apenas no
relatório final.

**Requisito de proveniência:** todo número que aparecer em relatório ou artigo
precisa ser rastreável até o arquivo bruto em `../data/` que o originou, e até a
versão do código de análise que o calculou. Mantenha *notebooks*/scripts versionados
aqui, não como arquivos avulsos de rascunho.
