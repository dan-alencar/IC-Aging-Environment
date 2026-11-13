# AU15P bitstreams (xcau15p-ffvb676-1-i)

Frozen builds used on the bench, kept with their VIO probe files (`.ltx`) and reports. Use one
bitstream, by md5, from the reference measurement to the end of a run: the baseline slack
count changes from one build to another (the adder's routing changes even with the sensor
cells placed by hand).

## The colleague's architecture-B builds (Vivado 2025.2, never committed as source)

Built in the worktree `IC-Aging-Environment-au15p`, branch `au15p-telemetria`, from RTL that
was not committed (`src/rtl/hub/`, `src/rtl/multi/`). They speak the colleague's protocol v2
(`$FPG` lines through STM32 firmware B, `firmware/supervisory/stm32_hub_fw/`), not fbs.

| File | md5 | USR_ACCESS | What |
|---|---|---|---|
| `au15p_hub_B.bit` | `d6a64886e871487da64ddf394605231e` | `0x2DB4C51F` (2026-11-05 12:20:31) | One chain (the fixed 256-bit RCA), continuous sweeps, 1 s windows with count/min/max/sum/sum of squares; WNS +0.459 ns, 2.96 % LUTs |
| `au15p_multi_B.bit` | `b4f0b00946a7100a04c1ac03d4fe3cd3` | `0x55B4F7E0` (2026-11-10 15:31:32) | Nine chains (inferred 256, CARRY8 128/256/512/1024, LUT 8/16/24/32), one sensor each, placement fixed by XDC; WNS +0.450 ns, 8.45 % LUTs, 542 CARRY8 |

`au15p_multi_B_chains.txt` lists the chains' routed delays and predicted steps. First reading
on board A (2026-11-10, 52 °C, 0.875 V, oven off): measured steps ≈ 214.9 + 0.613 × predicted
(±11), about 27.5 ps per CARRY8 and 99 ps per LUT stage. Programming or resetting the STM32
clears the FPGA (it is configured in SRAM only).

Why the original `origin/main` design (`fpga_unified_top`) does not measure: its sensor input
was the adder's `error_flag`, which compares a sum with itself and never changes once timing
is met, so the sensor never alarms and the sweep never ends. The fix (the colleague's TESTE
adder) excites the adder so the top sum bit flips only after the carry crosses all 256 bits;
`fbs_aging_top` uses the same excitation.

## fbs builds

`fbs_aging_top` (IC-Aging on the fbs platform, `src/rtl/fbs_aging`, no IP) is built with
`scripts/build_fbs_aging.sh` into `build/fbs_aging/`. A build is copied here, with its md5 and
USR_ACCESS in this table, once it has passed the bench checks (fbs SPEC phase P7).

| File | md5 | USR_ACCESS | What |
|---|---|---|---|
| (none yet) | | | |
