# STM32 firmware B and board flash backups (reference only)

Binaries from the colleague's architecture-B bench (2026-11). There is no source here: firmware
B was built from RCROC commit `361fc39` plus his changes (branch `dt2027`,
`D&T 2027/10_DT_Monitor/firmware_stm32/hub_fw/Latchup_FW_hub`). The current firmware for the
boards is fpgaging-board-support's `firmware/stm32` (fbs protocol); these files exist so a
board can be put back exactly as it was.

| File | What | md5 |
|---|---|---|
| `bin/fw_hub_v6_20261106.bin` (+ `.map`) | Firmware B v6: relays the FPGA's `$FPG` frames to the ST-LINK, HSE clock with CSS fallback to MSI; passed the hot test (STM32 at 83.6 °C, 0 CRC errors) | `2719cf22ea77c8fc3aaca2c9df02de69` |
| `bin/fw_TEL_125k_84KB.bin` | The `$TEL` latch-up firmware that was on the boards before firmware B (first 84 KB of board A's flash) | `cda19662012767166e375207f6a1e8c6` |
| `bin/boardA_UID0028001A_flash_fw_TEL_125k.bin` | Full 2 MB flash of board A, 2026-11-03 | `995e595137c1679a4ea4c6b45e488b60` |
| `bin/boardB_UID002E002C_flash_original_backup.bin` | Full flash of board B before any change (HSE, USART1 at 9600, USART2 off) | `97bf5d7e03f5d5e3b5d195d36ad46cf4` |
| `bin/boardC_UID000F0029_flash_before_20261111_1121.bin` | Full flash of board C, 2026-11-11 11:21 (UID starts `000F0029`) | `fd3b8352e1efd6a76f89a9d5e16c18de` |

Firmware B v1–v5, the duplicate ESP32 builds and the old app's `.venv` were not kept (fbs SPEC §6.4).

Restore a board (ST-LINK serial in `sn=`; the board's UID is checked by
`external/fpgaging-board-support/tools/flash_stm32.sh` for fbs images):

    STM32_Programmer_CLI -c port=SWD sn=<ST-LINK serial> -e all -w <file>.bin 0x08000000 -v -rst
