# data/ — Dados brutos de campanha

*[Read in English](README.md)*

Vazio por enquanto. É aqui que os CSVs brutos de campanha (e qualquer outra
telemetria bruta) ficam.

**Regra rígida do documento de plano (Seção 6.3): dado bruto é imutável.** Nenhum
arquivo de campanha é editado depois de gravado. Se um arquivo precisar de correção
(um canal com defeito conhecido, uma coluna com rótulo errado), essa correção
acontece na camada de processamento em `../analysis/`, com a própria correção
documentada e versionada — o arquivo bruto permanece exatamente como o instrumento o
produziu.

Conjuntos de dados brutos grandes podem não caber diretamente no histórico do git,
dependendo do tamanho e de quantas campanhas se acumularem — decida e documente a
abordagem de armazenamento aqui (Git LFS, um repositório de dados externo com um
manifesto commitado aqui, etc.) antes da primeira campanha longa, não depois.
