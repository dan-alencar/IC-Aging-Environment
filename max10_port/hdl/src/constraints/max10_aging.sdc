## ============================================================================
## Arquivo de restricoes de timing (SDC) para max10_aging_top
##
## Define o clock de entrada (clk50) e deriva automaticamente os clocks
## gerados pela PLL (sys_clk/c0, psclk/c1, catcher_clk/c2).
##
## Tambem declara como "false path" a travessia entre o dominio de
## catcher_clk e o dominio de scanclk (clk50) usada pelo sinal 'alarm' --
## essa travessia ja e tratada corretamente em HDL por um sincronizador
## de duplo flip-flop dentro do scc_controller, entao nao faz sentido
## que o TimeQuest exija fechamento de timing sincrono nela (ela e
## inerentemente assincrona por natureza).
## ============================================================================

# Clock de entrada: MAX10_CLK1_50, 50 MHz (periodo de 20 ns)
create_clock -name clk50 -period 20.000 [get_ports {clk50}]

# Deriva automaticamente os clocks de saida da PLL (c0, c1, c2) a partir
# da definicao acima
derive_pll_clocks

# Calcula a incerteza de clock (jitter/skew) automaticamente
derive_clock_uncertainty

# C3 -- Caminho interno do sensor: FF_sys_clk / FF_psclk -> XOR -> FF_alarm
# (catcher_clk, fase FIXA c = 2,5 ns = 14 passos de 178,57 ps).
#
# ANTES: set_false_path clk[0]->clk[2] e clk[1]->clk[2], que escondia do STA um
# caminho que PRECISA fechar: o XOR tem de assentar antes do catcher amostrar.
# Como psclk e deslocado em tempo real, a relacao de fase estatica entre clk[1]
# e clk[2] nao representa nada; so o ATRASO DE DADOS importa.
#
# AGORA (restricao do relatorio de revisao, C3 item 3): o XOR precisa estar
# estavel antes do catcher (c), com folga. 1,500 ns = c (2,5 ns) - 1,0 ns.
# CONFERIR no relatorio do Timing Analyzer que este caminho fecha. Se der slack
# negativo, nao relaxe o numero as cegas: veja o atraso real e decida entre
# aproximar os 3 FFs (LOCATION) ou subir c em multiplos de 178,57 ps
# (c tem que continuar < d_min ~ 10,5 ns).
set_max_delay -from [get_registers {*ff_sys_clk_q* *ff_psclk_q*}] -to [get_registers {*ff_alarm_q*}] 1.500

# Travessia assincrona do sinal alarm: catcher_clk (clk[2], saida da PLL)
# <-> scanclk/clk50 (dominio do scc_controller). Ja sincronizada em HDL
# por duplo flip-flop; mantida por seguranca, ainda que nao fosse a
# causa da violacao reportada.
set_false_path -from [get_clocks {u_aging_pll|altpll_component|auto_generated|pll1|clk[2]}] -to [get_clocks {clk50}]
set_false_path -from [get_clocks {clk50}] -to [get_clocks {u_aging_pll|altpll_component|auto_generated|pll1|clk[2]}]

# Caminho launch -> critical_path_chain (50 LUTs) -> FF_psclk:
# este lado NAO pode ser analisado estaticamente, pois psclk e
# deslocado em tempo real via phasestep (a analise estatica so enxerga
# a fase inicial, 0 graus, definida em tempo de compilacao).
set_false_path -from [get_registers {*launch*}] -to [get_registers {*ff_psclk_q*}]

# ATENCAO -- MUDANCA DE DIAGNOSTICO (retomada apos travamento persistente
# em hardware real, independente da fase do catcher_clk):
#
# O lado launch -> FF_sys_clk_q NAO foi mantido como false_path.
# O comentario anterior deste arquivo afirmava que esse caminho e
# "intencionalmente mais lento que um ciclo de clock" -- essa premissa
# CONTRADIZ o mecanismo descrito no artigo de referencia (Secao II-A):
# em psclk = sys_clk (fase 0, calibracao inicial), o alarme NAO deve
# disparar; o caminho critico precisa terminar DENTRO de um periodo de
# clock, com slack positivo confortavel, para que o barrido dinamico de
# fase tenha margem para explorar antes de encontrar a fronteira real.
#
# Alem disso, ao marcar esse caminho como false_path, o Fitter perde
# qualquer incentivo de timing para posicionar as 50 LUTs proximas
# entre si -- o roteamento entre elas fica livre para se espalhar pelo
# dispositivo, o que pode facilmente inflar o atraso real muito alem do
# esperado (o atraso de roteamento tipicamente domina sobre o atraso
# logico interno em FPGA).
#
# Reativando a analise real aqui, o proximo relatorio do TimeQuest
# (max10_aging_top.sta.rpt, secao "Slow ... Model", clock c0) vai
# reportar o slack/atraso REAL desse caminho em nanossegundos -- em vez
# de deixar isso como uma suposicao. Se o slack vier negativo (caminho
# mais lento que o periodo), isso CONFIRMA a causa raiz do alarme
# persistente observado em placa, com um numero concreto em maos para
# decidir o proximo ajuste (reduzir NUM_STAGES da cadeia, ou aumentar o
# periodo de c0/c1/c2 via divide_by na PLL).
