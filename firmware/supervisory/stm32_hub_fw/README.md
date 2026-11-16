# STM32 firmware B and board flash backups (reference only)

Binaries and source of the colleague's architecture-B bench (2026-11). Firmware B is RCROC
commit `361fc39` plus his changes; the source is in `src/` (moved here from branch `dt2027` on
2026-11-16). The current firmware for the
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

## Source (`src/`)

| Path | What |
|---|---|
| `src/Latchup_FW_hub/` | The STM32CubeIDE project of firmware B v6: `Core/` (his code: `fpga_link*`, `telemetry`, `protocol`, `Serial_Bridge`, `IHM`, the clock and CSS changes in `main.c`), the `.ioc` (STM32Cube FW_L4 V1.18.1; it still says MSI, see `LEIAME.md`), linker scripts, `tests_host/` |
| `src/hub_vs_361fc39.diff` | His changes against RCROC `361fc39` |
| `src/LEIAME.md`, `src/LEIAME_firmware_stm32.md` | His notes per version (v1–v6) and on the firmware folder, in Portuguese |
| `src/build.sh`, `src/Makefile.cubeide`, `src/gravar.sh` | His command-line build and flash scripts |
| `option_bytes/boardA.txt`, `boardB.txt` | Option bytes read from boards A and B |

`Drivers/` and `Middlewares/` (ST HAL, CMSIS, FreeRTOS and the OLED, MYMGM1R and TPS65400
drivers) are not copied: every file is byte-identical to RCROC `361fc39`. To build, copy them in:

    git -C <RCROC> archive 361fc39 STM_FW/Latchup_FW/Drivers STM_FW/Latchup_FW/Middlewares |
      tar -x --strip-components=2 -C src/Latchup_FW_hub

**What the source settles for the fbs bench (SPEC V8, §7.6):**

- `Is` (`telemetry.c`) is `|V(OPAMP1 out) − V(OPAMP2 out)| / (2 × 0.1 Ω)`: PA0 and PA6, each through
  an on-chip op-amp at gain 2 (`main.c` `MX_OPAMP1/2_Init`), read on ADC1 channels 8 and 15. The code
  calls it `i_sram`. It is **only reported**: the latch-up trip compares the module's `READ_IOUT`
  with `Mc` (2 A by default; off 3 s, settle 5 s; `main.c` `LatchupDetect`).
- Both option-byte dumps show `DBANK = 1` (dual-bank flash), which the fbs event log needs.
