# Firmware dos STM32 das placas AU15P

> **Arquitetura B (04/11/2026):** o firmware novo, que repassa os dados do FPGA pelo ST-Link
> (`$FPG`), está em [`hub_fw/`](hub_fw/LEIAME.md), com o projeto, o binário e o roteiro de
> gravação. Ele ainda não foi gravado. Os arquivos abaixo são o firmware de hoje e o backup.

Cópias lidas pelo SWD (ST-Link + STM32_Programmer_CLI) em 03/11/2026.

**De onde vem o firmware do `$TEL`:** é o firmware de proteção contra latch-up do projeto
`RCROC` (`/home/andre/Documentos/GitHub/RCROC`, hoje em `firmware/stm32_latchup/`). Mesmo
clock (MSI + PLLN 60 = 120 MHz), mesmo formato `$TEL,Vc,…,Sq` e mesmos campos. O binário das
placas tem a USART2 a 125 000 baud, como nos commits de 07/04/2026 (`862ba1b`, `361fc39`); a
partir de `bc1d33b` (11/04) e no tag `v1-beam-partrec-2026-04-08`, a USART2 passa a 115 200.
Ou seja, as placas têm um build de ~07/04/2026, não exatamente nenhum commit conhecido.

Conferido em 04/11/2026: um build do `361fc39` feito aqui tem **as mesmas strings** do binário
das placas (todos os formatos de `$TEL`/`$BST`/`$LEVT`, motivos e mensagens). O tamanho difere
em 312 bytes. A única diferença nas strings é o caminho do newlib: as placas foram compiladas
com o GNU Tools for STM32 13.3.rel1.**20250523**, e esta máquina tem o **20240926**. O único
commit seguinte que mexe no firmware (`4e8ecc1`) só troca a USART2 para 115 200, e as placas
estão a 125 000. Então o fonte das placas é o `361fc39`, que é a base do firmware B.
Esse firmware aceita comandos (CRC16 Modbus): Vcore (`FUNC_V`, 0.70–1.30 V em passos de
10 mV), liga/desliga a saída do core (`FUNC_E`), limite de corrente do latch-up (`FUNC_S`) e
página do OLED (`FUNC_P`).

| Arquivo | O que é | md5 |
|---|---|---|
| `placaA_UID0028001A_fw_TEL_125k.bin` | flash inteira (2 MB) da placa A: o firmware do `$TEL` (USART1 e USART2 a 125 000 baud, MSI + PLL a 120 MHz) | `995e595137c1679a4ea4c6b45e488b60` |
| `fw_TEL_125k_84KB.bin` | os primeiros 84 KB do arquivo acima (`0x08000000`–`0x08015000`), onde está tudo o que não é `0xFF` | `cda19662012767166e375207f6a1e8c6` |
| `placaB_UID002E002C_fw_original_BACKUP.bin` | **backup** da flash inteira da placa B antes da troca: o firmware do repositório (HSE 16 MHz, USART1 a 9600, USART2 desligada; tem um `TEL` antigo que sai só pela USART1) | `97bf5d7e03f5d5e3b5d195d36ad46cf4` |
| `option_bytes_placaA.txt`, `option_bytes_placaB.txt` | option bytes das duas: iguais (RDP nível 0, dual bank, sem WRP) | |

## O que foi feito na placa B (03/11/2026)

Apagada a flash inteira do STM32 da B (UID `002E002C 30325014 20343046`, ST-Link
`003E00243234511537333934`) e gravado `fw_TEL_125k_84KB.bin`. A leitura de volta da flash
inteira deu o mesmo md5 da placa A. Depois do reset, a B manda `$TEL` pelo ST-Link a
125 000 baud (32 linhas em 8 s, todas com checksum válido).

## Gravar de novo / voltar atrás

```bash
CLI=/opt/st/stm32cubeide_1.19.0/plugins/com.st.stm32cube.ide.mcu.externaltools.cubeprogrammer.linux64_2.2.200.202503041107/tools/bin/STM32_Programmer_CLI

# firmware do $TEL numa placa (troque o sn= pelo ST-Link dela)
$CLI -c port=SWD sn=<serial do ST-Link> -e all -w fw_TEL_125k_84KB.bin 0x08000000 -v -rst

# placa B de volta ao firmware que ela tinha
$CLI -c port=SWD sn=003E00243234511537333934 -e all -w placaB_UID002E002C_fw_original_BACKUP.bin 0x08000000 -v -rst
```

`-e all` apaga a flash inteira do STM32 antes de gravar.

## Cuidado: Nucleo ligada ao mesmo tempo

Com uma Nucleo (ST-Link V2.1, ex. NUCLEO-F411RE `066CFF525056805087053318`) no USB junto com os
STLINK-V3 das placas, o STM32_Programmer_CLI 2.2 (do CubeIDE 1.19) **troca os seriais**: em 03/11/2026
ele listou o ST-Link da placa B (`003E…`) com o serial da Nucleo, e `sn=003E…` deu "Serial number not
found", enquanto `sn=066C…` chegava no STM32 da placa B. Antes de gravar, desligue a Nucleo do USB ou
confira o UID do alvo (`-r32 0x1FFF7590 0xC`) antes de qualquer `-e`/`-w`.
