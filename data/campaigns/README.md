# Campaign data (versioned)

These are the raw logs behind the group's published burn-in papers. They were deleted from the working tree in the 2026-09-30 cleanup (`b908add`) and recovered from git history on 2026-11-05. Every file is byte-identical to a blob already in history (`git hash-object` matches), so tracking them adds no repository size. `SHA256SUMS` covers every file; cite those hashes in papers.

**Hardware:** all sensor campaigns ran on the **same physical Nexys 4 DDR board (Artix-7 xc7a100tcsg324-1)**. The monitored circuit (CUT) changed with the bitstream, as the table shows.

| Folder | Campaign | CUT | Used by |
|---|---|---|---|
| `2025-04_sbcci25_week1_bangbang/` | Week-1 burn-in, stock thermostat, 115 °C / 1.3 V, 164.2 h, 0.5 Hz | 50-inverter chain | SBCCI 2025 |
| `2025-04_sbcci26_bangbang_23h/` | First 23.08 h of the Week-1 log (byte-identical prefix) | 50-inverter chain | SBCCI 2026, D&T |
| `2026-01_sbcci26_pid_23h/` | PID oven, 115 °C target, 1.3 V on-die, 23.08 h, 1 Hz | 50-inverter chain | SBCCI 2026, D&T |
| `2026-05_rca_pid_212h/` | PID oven, ~125 °C die, 1.400 V on-die, 214.6 h, 1 Hz | 16-bit ripple-carry adder | TIP7266, D&T |
| `2026-01_oven_100C_controller_tests/` | 100 °C oven-air tests: stock thermostat, SIMC gains, fine-tuned PID (DUT outside the stress, ~37 °C / 1.0 V) | n/a | thesis, D&T |
| `oven_fopdt_step_test/` | 50 % open-loop step from 25.21 °C (FOPDT identification) | n/a | thesis, D&T |
| `recovered_misc/` | Every other CSV ever committed (tuning and debug logs), at its original path | various | none |

Schemas: `legacy` is `Data,Hora,Temperatura,Slack,Tensão`, with temperature and voltage in milli-units. `tcc9` is a `#` metadata header followed by `time_sec,oven_temp_c,oven_setpoint_c,oven_output_pct,psu_voltage_v,psu_current_a,dut_temp_c,dut_slack,dut_volt`. Slack is in integer MMCM phase steps.

Adding a campaign: create `YYYY-MM_<short_name>/`, add its line to this table, and append its hash to `SHA256SUMS`. Files over ~50 MB should go to Zenodo or the lab NAS instead (GitHub warns at 50 MB and rejects files over 100 MB).
