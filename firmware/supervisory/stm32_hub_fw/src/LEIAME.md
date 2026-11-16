# Firmware B do STM32 (arquitetura B, 04/11/2026)

Firmware das placas AU15P para a arquitetura B: o FPGA manda os dados ao STM32, e o STM32
repassa tudo ao PC pelo ST-Link. Parte do firmware que está nas placas: o de latch-up do
repositório `RCROC`, commit `361fc39` (as strings do binário das placas são idênticas às de
um build desse commit; o único commit seguinte só troca a USART2 para 115 200). Clock, HAL,
PMIC (MYMGM1R), proteção de latch-up, ADC e o formato do `$TEL` não mudaram.

**Versão 6 (06/11/2026): gravada nas duas placas (~10:40) e aprovada no teste quente.** `verificar_hub` OK nas duas, com `Ver,6` e `Clk,HSE`. Teste `test_logs/AU15P_20261106_20261106_113140*` (forno 80 °C, pico 87 °C): com o STM32 da B a 83,6 °C e o da A a 79,5 °C, 0 erros de CRC, 0 janelas perdidas e 100 % dos segundos com dados (a v5, a 83 °C, errava 400–590 linhas a cada 2 min). O relógio passa a vir do
cristal de 16 MHz (HSE) da placa, e não mais do MSI (oscilador RC interno). Na run de teste de
05–06/11 (`test_logs/Testedanoite_20261105_224603*`), com o STM32 acima de ~80 °C, o MSI
desviou e a USART2 (STM32 → ST-Link → PC) passou a errar: na placa B, 3202 linhas com CRC
errado e 745 janelas perdidas entre 23:14 e 23:45; o enlace FPGA → STM32 seguiu sem erro.
- HSE / 4 = 4 MHz na entrada do PLL, a mesma que o MSI dava: os 120 MHz e todos os divisores
  (USART, I²C, ADC, tick) ficam iguais. O cristal está no esquemático (`FPGAging_RV02A.PDF`:
  16 MHz no OSC_IN/OSC_OUT, 32,768 kHz no OSC32) e o firmware original da placa B já o usava.
- Se o cristal não oscilar no boot (HSERDY em 100 ms), o firmware volta ao MSI de antes.
- CSS ligado: se o cristal parar com o firmware rodando, o hardware passa o SYSCLK ao MSI
  (4 MHz), o NMI só marca o evento e a tarefa padrão refaz os 120 MHz pelo MSI.
- O ADC (proteção de latch-up) usa o PLLSAI1, que precisa da mesma fonte do PLL principal:
  `Clock_Adc_Config()` escolhe o divisor pela fonte (o HAL recusa fontes diferentes e travaria
  no `Error_Handler`).
- O `$FWV` ganha `Clk,HSE` (cristal), `Clk,MSI` (o cristal não oscilou) ou `Clk,MSI-CSS`.
- Mudanças: `main.c` (`SystemClock_Config`, USER CODE 0 e 5), `stm32l4xx_hal_msp.c` (ADC),
  `stm32l4xx_it.c` (NMI), `fpga_link.c/.h`. O `.ioc` não foi atualizado (ainda diz MSI):
  regenerar pelo CubeMX desfaria a `SystemClock_Config` e a `HAL_ADC_MspInit`.
- Conferir depois de gravar: o `$FWV` com `Ver,6` e `Clk,HSE`, e um teste com o forno quente
  (STM32 acima de 80 °C) sem CRC errado.

**Versão 5 (05/11/2026): gravada nas duas placas e aprovada.** Teste de 30 min (15:21–15:51,
`test_logs/AU15P_hub_v5_teste30min_20261105_152125*`): 1800 janelas por placa, **nenhuma
faltando nem repetida**, contadores `Ce`/`He`/`Qd`/`Gp`/`Jk` parados durante o teste, nenhum
`$TEL` perdido, e as 1800 janelas idênticas às dos sniffers do J9.

Histórico da v4: Teste de 30 min com a v4 (14:47–15:17): 2 janelas
perdidas na A e 3 na B, em 1800, todas nas que trazem o `FPGA_INFO` (360, 900, 1380). Nelas o
SENSOR e o INFO saem colados (77 bytes, 6,2 ms); se o meio ou o fim do buffer do DMA cai no
começo da rajada, o resto do quadro chega num segundo lote mais de 5 ms depois, e o montador o
descartava como cortado (`Gp`). A v5 usa 20 ms (`FL_GAP_MS`); o teste do PC ganhou esse caso.
Fora isso, a v4 bateu 100 % com os sniffers: nenhuma janela diferente nem só no app.

Histórico da versão 4: A v3 lia a posição do DMA pelo valor que o HAL
passa ao evento; as interrupções de "meio/fim do buffer" (DMA) e de "linha ociosa" (USART)
chegam fora de ordem, e um evento atrasado parecia uma volta inteira do buffer: 256 bytes velhos
eram entregues de novo (teste de 05/11 14:31: 7 janelas perdidas e 2 repetidas em 6 min na A,
`Qd` e `Jk` subindo; a ESP32 no J9 da B recebeu tudo, sem erro). A v4 lê o contador do DMA,
que só anda para frente.

Histórico da versão 3: Teste de 30 min com a v2 nas duas placas
(05/11, 13:19–13:49): o enlace funciona, mas ~1 % das janelas não chegaram (20 de 1800 na
A, 9 na B). O STM32 recebia a USART1 com DMA de 1 byte, e cada byte esperava a interrupção;
com as interrupções desligadas por mais de ~80 µs (por exemplo, ao enfileirar uma linha de
150 bytes), um byte se perdia e o quadro era descartado **sem acusar erro**. Lido por SWD:
35 quadros cortados na A e 24 na B (`gaps`, que não saía no `$FPG`). A v3 recebe por DMA
circular de 256 bytes com evento de linha ociosa (`HAL_UARTEx_ReceiveToIdle_DMA`) e manda
`Gp` (quadros cortados) e `Jk` (bytes fora de quadro) no `$FPG`.

Histórico da versão 2: A versão 1 foi gravada nas duas placas em
05/11 (às 11:54, o `$TEL` e o `$FWV` com o UID certo saíam nas duas), mas **não funciona**:
ela manda o STM_HELLO pelo PA9, que não está ligado a nada na placa. A TX da USART1 que vai
ao FPGA é o **PB6** (esquemático `FPGAging_RV02A.PDF`, folha 33: PB6 = `MCU_USART1_TX` →
AB16 do FPGA, TP2; PB7 = `MCU_USART1_RX` ← W12, TP1). Sem o HELLO, a trava do FPGA nunca
abre e não chega nenhum `$FPG`. O erro vem do 361fc39, que também tinha a TX no PA9.
Ninguém notou porque o firmware antigo nunca mandava nada ao FPGA.

Como foi achado (05/11, leitura por SWD sem parar o STM32 e pela JTAG, sem gravar nada):
o STM32 mandava o HELLO a cada 1 s e a recepção da USART1 estava armada, mas só tinha
chegado 1 byte desde o boot. O FPGA estava com o `au15p_hub_B`, MMCM travado, varrendo
(`phase_count` 403 na A e 391 na B) e com o SYSMON do design atualizando.

| Arquivo | O que é |
|---|---|
| `bin/fw_hub_v6_20261106.bin` | **o binário para gravar** (77 168 bytes  md5 `2719cf22ea77c8fc3aaca2c9df02de69`) |
| `bin/fw_hub_v5_20261105.bin` | a versão 5 (relógio pelo MSI: a serial erra com o STM32 acima de ~80 °C) (76 660 bytes  md5 `c68a77d2f76a709bd91a6dba6c3a8591`) |
| `bin/fw_hub_v4_20261105.bin` | a versão 4 (perde ~0,1 %, as janelas do `FPGA_INFO`) |
| `bin/fw_hub_v3_20261105.bin` | a versão 3 (perde e repete quadros) (76 628 bytes  md5 `a75cb3ed83982b70110f0c20b2cf3a98`) |

O primeiro build da v3 (md5 `a29e6b4e…`, gravado por engano na placa A e substituído) saiu de um build
incremental que não recompilou o `fpga_link.c` depois da mudança no `.h`: mandava `Ver,2` e misturava
duas versões da estrutura dos contadores. O `build.sh` agora compila sempre do zero e o Makefile
acompanha os `.h` (`-MMD`).
| `bin/fw_hub_v2_20261105.bin` | a versão 2 (TX no PB6, recepção byte a byte; perde ~1 % dos quadros) |
| `bin/fw_hub_v1_20261104.bin` | a versão 1, com a TX no PA9 (não usar; fica para registro) |
| `bin/*.elf`, `bin/*.map` | o mesmo build com símbolos, para depurar |
| `Latchup_FW_hub/` | o projeto completo do STM32CubeIDE (abre e compila na IDE) |
| `hub_vs_361fc39.diff` | tudo o que mudou em `Core/` em relação ao 361fc39 |
| `build.sh`, `Makefile.cubeide` | build sem a IDE, com os flags do `.cproject` (Debug, `-O0`, `-u _printf_float`) e o GCC 13.3 do CubeIDE 1.19 |
| `Latchup_FW_hub/tests_host/` | teste no PC do remontador de quadros e da linha `$FPG`, conferido com o decodificador do app |

## O que mudou

1. **A USART1 (linha do FPGA) não executa mais comandos.** Ela só remonta os quadros v2 do
   FPGA (`fpga_link.c`) e confere o CRC. Cada quadro sai pelo ST-Link numa linha `$FPG`
   (`PROTOCOL_V2.md`, seção "Arquitetura B"). No 361fc39, os bytes que chegavam ali iam
   para o leitor de comandos. Com o FPGA mandando dados binários, um CRC certo por acaso
   viraria um `FUNC_V` aleatório (até 1.30 V) ou um desliga.
2. **STM_HELLO pela USART1 TX a cada 1 s.** É o que destrava a linha do FPGA para o STM32
   (`stm_hello_gate.v`). Com o firmware antigo, o FPGA não manda nada ao STM32.
3. **`$FWV` a cada 5 s** (`Fw,hub,Ver,5,Base,361fc39,Build,…,Uid,…`). O app só grava o
   bitstream B depois de ver essa linha. Com `Ver` menor que 5, o app e o
   `verificar_hub.py` avisam qual é o problema daquela versão.
4. **Comandos aplicados numa tarefa (`Command_Task`), não na interrupção.** No 361fc39 o
   `FUNC_V` rodava dentro da interrupção da USART2. Ali o mutex do I2C não funciona, então o
   comando às vezes achava o I2C ocupado e não chegava ao PMIC. O `$BST` também disputava o
   buffer do `$TEL`. A resposta de 3 bytes é a mesma e sai depois de aplicado.
5. **Fila de saída da USART2 de 192 bytes para 2 KB**, e uma tarefa espera até 50 ms por
   espaço em vez de descartar a linha. Com 192 bytes, um `$FPG` atrás de um `$TEL` não cabia.
6. **Um mutex para todas as linhas** (`$TEL`, `$BST`, `$LEVT`, `$FPG`, `$FWV`). O `snprintf` com
   `%f` do newlib-nano usa `malloc` e não pode rodar em duas tarefas ao mesmo tempo.
7. **Vcore limitado a 1.00 V** (era 1.30 V; `HUB_VCORE_MAX_V` em `protocol.c`). É o máximo
   absoluto do VCCINT da Artix UltraScale+; o app já para em 0.95 V.
8. **OLED desligado** (`HUB_OLED = 0` em `main.c`). O `OLED_Init` já estava comentado no
   361fc39, mas a tarefa padrão continuava desenhando, com `sprintf` de float e I2C2 a cada 1 s.
9. Heap do FreeRTOS de 15 000 para 32 768 bytes (duas tarefas novas).
10. **TX da USART1 no PB6** (era PA9; versão 2). O `.ioc` também foi corrigido, então
    regenerar o código no CubeMX mantém o PB6.
11. **USART1 RX por DMA circular** com evento de linha ociosa (versão 3), e os contadores
    `Gp` e `Jk` no `$FPG`. Um erro na USART1 só recomeça a recepção; não esvazia mais a fila
    do STM_HELLO.

Uso: 75,9 KB de flash (era 81,2 KB) e 46,5 KB de RAM estática, de 640 KB. A pilha mais funda
das tarefas novas fica abaixo de 1 KB, de 2 KB disponíveis (`-fstack-usage`).

## Compilar e testar

    ./build.sh test      # compila (out/Teste_Aging.bin) e roda o teste do enlace no PC

O build a partir desta pasta dá o mesmo binário de `bin/` (md5 acima). O teste do PC manda
199 quadros, com lixo, CRC errado, quadro cortado e cabeçalho inválido, e confere se os 199
quadros válidos saem idênticos e se a linha passa pelo `parse_tel` do app.

## Gravar (só com o OK do responsável pela bancada)

Ordem: **primeiro este firmware, depois o bitstream B** (`PROTOCOLO_RUN.md`). O firmware B
funciona com o bitstream de hoje (TESTE) e com o modo "atual" do app. Ele só passa a mandar
`$FPG` quando o FPGA estiver com o `au15p_hub_B`.

O jeito mais simples é o `gravar.sh` desta pasta. Ele escolhe o ST-Link pelo **UID do STM32**,
e não pelo serial, e não grava nada se não achar o UID da placa pedida:

    ./gravar.sh listar      # só mostra qual ST-Link chega em qual STM32
    ./gravar.sh A           # firmware B na placa A
    ./gravar.sh B           # firmware B na placa B
    ./gravar.sh C           # firmware B na placa C (3ª placa, 11/11/2026, UID 000F0029 32325009 20363646)
    ./gravar.sh A antigo    # volta ao firmware de antes

Na primeira gravação de um STM32 que ainda não tem cópia em `../`, o script lê antes a flash
inteira (2 MB, modo HOTPLUG, sem reset) para `../placa<X>_UID<...>_antes_<data>.bin` e só apaga
se a cópia vier completa e com o UID certo. A placa C tinha um terceiro firmware (~62 KB, com um
`TEL,Vc,…,Mt` antigo e nada na USART2).

Em 04/11/2026 (20:05), com a Nucleo no USB, o CLI listava o ST-Link da placa A com o serial
da Nucleo (`066CFF525056805087053318`) e não achava o `0048…`. O `003E…` chegava na placa B.
O `gravar.sh` resolve isso sozinho. Na mão, seria:

```bash
CLI=/opt/st/stm32cubeide_1.19.0/plugins/com.st.stm32cube.ide.mcu.externaltools.cubeprogrammer.linux64_2.2.200.202503041107/tools/bin/STM32_Programmer_CLI

# 0. Feche o D&T Monitor (ele usa a porta do ST-Link) e desligue a Nucleo do USB
#    (com ela ligada, o CLI troca os seriais dos ST-Link; ver ../LEIAME.md).
# 1. Confira o UID do alvo antes de apagar
$CLI -c port=SWD sn=<serial do ST-Link> -r32 0x1FFF7590 0xC
#    placa A: 0028001A 30325015 20343046    placa B: 002E002C 30325014 20343046
# 2. Grave e confira
$CLI -c port=SWD sn=<serial do ST-Link> -e all -w bin/fw_hub_v5_20261105.bin 0x08000000 -v -rst
```

ST-Link da placa A: `004800283133510937363734`; da placa B: `003E00243234511537333934`.
Depois do reset, a porta do ST-Link mostra `$TEL` 4 vezes por segundo e um `$FWV` a cada 5 s:

    $FWV,Fw,hub,Ver,5,Base,361fc39,Build,20261105,Uid,002E002C3032501420343046*..

## Voltar ao firmware de antes

```bash
$CLI -c port=SWD sn=<serial do ST-Link> -e all -w ../fw_TEL_125k_84KB.bin 0x08000000 -v -rst
```

Com o firmware antigo, a trava do RTL deixa a linha do FPGA para o STM32 parada, mesmo com o
bitstream B carregado. Para o FPGA voltar ao bitstream TESTE, religue a placa (o design fica
só na SRAM) e abra o app no modo atual.
