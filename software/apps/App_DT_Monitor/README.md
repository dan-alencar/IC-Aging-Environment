# App_DT_Monitor

The burn-in app for RV02A boards (AU15P + STM32L4R9) on the fpgaging-board-support bench kit
(fbs SPEC §6.2, §9). It replaces App_FPGAging_Slack_Sensor and carries the colleague's
D&T Monitor features over to the fbs protocol and platform.

```
App_DT_Monitor (Qt window)  ──JSON lines──►  fbs-service ──► boards (ST-LINK relay or J9)
     a client: attach,                        owns the ports, records sessions,      └► oven (firmware 2.0)
     detach, crash freely                     runs the plan, watchdog
```

## Run

    ./run.sh sim            # the whole bench on the simulator (2 boards, oven): service + window
    ./run.sh                # the lab bench: bench/rv02a_lab.yaml (edit the ports first)
    ./run.sh service        # only the service (e.g. under systemd); then ./run.sh gui rv02a
    ./run.sh corners rv02a --volts 0.85 0.90 0.95 0.85
    ./run.sh oven-test /dev/ttyACM0 --sp 45            # service stopped
    ./run.sh check-board /dev/serial/by-id/...-if02 --board A   # service stopped

`run.sh` makes `.venv` on first use with the fbs submodule (`[qt]`) and this package in
editable mode, which also registers the plugins.

In the window: **Take control** (the control lease), **Start run plan…** (e.g.
`bench/burnin_115C_0v85.yaml`), **Stop run**, **Note…**. Per board: STM32 state and power
(setpoint, output, arm with countdown), SYSMON, rails, link health, identity, and the aging
panel (all chains, the reference chain, ring oscillators, live slack mean/std, trend with its
standard error, Arrhenius factor and equivalent hours at T_use = 55 °C, Ea = 0.7 eV, both
editable). Plots, a data-quality table (missing windows, chain-0 mismatches, CRC errors,
sequence gaps) and the service log.

## What runs where

| Part | Module | Notes |
|---|---|---|
| Experiment plugin `ic_aging.burnin` | `dt_monitor/experiment.py` | summary.csv columns per board, the chain-0 = AGING_WINDOW check, missing windows; sets the payload (continuous, 1 s windows, reference chain 3 windows per minute, histogram 300 + 16×8) at run start |
| Oven plugin `ic_aging_oven` | `dt_monitor/oven.py` | firmware 2.0 ASCII protocol; `EVENT,FAULT` lines are kept |
| Simulator payload | `dt_monitor/sim_app.py` | the same AGING_* frames and commands as the RTL, with the colleague's slack model |
| Statistics | `dt_monitor/stats.py` | window mean/std from sums, OLS trend, Arrhenius, equivalent hours |
| Scripts | `corners.py`, `oven_test.py`, `check_board.py` | ports of medir_corners, teste_forno, verificar_hub |
| Messages | `dt_monitor/protocol_aging.py` | generated from `protocol/messages.icaging.yaml` |

## Files

A session folder (`data/campaigns/sessions/<date>_<name>/`, git-ignored) holds the raw
`.fbslog` per board (the primary record), `summary.csv` (one row per second: oven, every
board's power, die, SYSMON VCCINT, and the aging columns `slack_mean`, `slack_std`,
`slack_min`, `slack_max`, `sweeps`, `window_id`, `aging_flags`, `c1..c8_slack_mean/std`,
`ref_slack_mean/std`, `ro0_hz`, `ro1_hz`, `lock_loss`, `missing_windows`, `chain0_mismatch`),
one CSV per message type (`A_AGING_WINDOW.csv`, `A_AGING_CHAIN.csv`, …), `events.log`,
`oven.log` and `session.json`. Empty fields mean no data, never 0.
`fbs session rebuild <folder>` regenerates the CSVs from the raw logs.
Analysis: `analysis/dt2027/sbcci_metrics.py --session <folder> --board A`.

## Tests

    pytest software/apps/App_DT_Monitor        # or tools/check_fbs.sh for everything

They run the service with this app's plugins on the simulator (a short burn-in plan and the
corners script end to end), the oven driver against the simulated firmware, check-board, and
the window offscreen.
