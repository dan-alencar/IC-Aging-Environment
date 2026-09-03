# host/ — Software de aquisição do lado PC

*[Read in English](README.md)*

Vazio por enquanto. É aqui que a frente F4 (telemetria e aquisição) coloca a
aplicação do lado PC, assim que a decisão de transporte (JTAG UART vs. módulo
USB-serial externo — veja o documento de plano, Seção 4.4, tarefa 1) for tomada.

**Ponto de partida sugerido:** bifurcar (*fork*) `../../App_Nexys/` em vez de
começar do zero. Ela já tem as peças que a F4 precisa preservar ou adaptar:

- `App_Nexys/workers.py` — `DUTWorker` (leitura periódica de pacote), `ArduinoWorker`
  (protocolo serial do PID do forno), `TestSequencer` (orquestração, montagem da
  linha do CSV, limites de segurança). A lógica de decodificação de pacote em
  `DUTWorker.poll_data()` é a parte que mais muda — novo transporte, e sem campo de
  VCCINT derivado do XADC para decodificar até a frente F3 definir o que o substitui.
- `App_Nexys/logger.py` — o formato de CSV com o qual manter compatibilidade. O
  documento de plano é explícito (Seção 4.4, tarefa 2) que a compatibilidade de CSV
  com o *pipeline* existente em `analysis/` é um requisito, não um "bônus" — é o que
  torna a comparação Artix-7 vs. MAX10 na frente F6 direta, em vez de exigir
  reconciliação entre dois formatos diferentes.
- `App_Nexys/main_window.py` — estrutura de interface Qt (abas, gráficos ao vivo,
  painel de log), se a nova aplicação mantiver interface gráfica. Uma ferramenta de
  aquisição sem interface (*headless*/linha de comando) também é escolha legítima
  para uma ferramenta de pesquisa e pode ser mais simples de manter robusta ao longo
  de campanhas de vários dias (veja o teste de resistência de 72 horas do plano,
  Seção 4.4, tarefa 5).

Não copie os IDs seriais fixos ou os caminhos do Vivado hardcoded em
`App_Nexys/config.py` — são específicos da configuração de laboratório atual do
Nexys4.
