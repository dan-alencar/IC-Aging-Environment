# Implementation Roadmap — Dual-Adder Sensor Architecture

Reference design document: [`SENSOR_ARCHITECTURE.md`](SENSOR_ARCHITECTURE.md)

---

## Phase 0 — Baseline capture (before any change)

> Goal: record the broken behavior so the fix can be measured against it.

- [ ] Build current bitstream and program the Nexys4 DDR
- [ ] Connect App_Nexys (or App_2Nexys) and start a test session
- [ ] Record at least 20 consecutive `display_value` readings and note the
      range (expected: widely scattered, up to ~9 000)
- [ ] Save a short CSV log as `test_logs/baseline_broken_YYYYMMDD.csv`
- [ ] Verify `error_count` behavior is plausible (should be 0 or very low on a
      fresh board at nominal voltage)

---

## Phase 1 — RTL: modify `adder_canary.sv`

> Goal: add the sensor adder driven by the worst-case toggle pattern and
> reassign `crit_bit` to its output.

### 1.1 Add `toggle` flip-flop

Inside the existing `always_ff` block (after reset and before the counter
increment), add:

```systemverilog
logic toggle;
// in the reset branch: toggle <= 1'b0;
// in the else branch:  toggle <= ~toggle;
```

`toggle` inverts every `clk_sys` cycle.  It drives `a_sensor` exclusively and
must not share any fanout with other logic.

### 1.2 Derive `a_sensor`

```systemverilog
logic [15:0] a_sensor;
assign a_sensor = toggle ? 16'h5556 : 16'h5555;
```

Verify: with `B = 16'hAAAA`:
- `toggle=0`: `0x5555 + 0xAAAA = 0xFFFF` → `sum_sensor[15] = 1`
- `toggle=1`: `0x5556 + 0xAAAA = 0x10000` → `sum_sensor[15] = 0`

Bit 15 must toggle on every clock cycle.

### 1.3 Instantiate the sensor `ripple_adder`

```systemverilog
logic [16:0] sum_sensor;

(* DONT_TOUCH = "yes" *)
ripple_adder #(.N(16)) u_sensor (
    .a  (a_sensor),
    .b  (B),
    .sum(sum_sensor)
);
```

Keep the existing canary instance name `u_canary` unchanged.

### 1.4 Reassign `crit_bit`

Change the existing `assign crit_bit = sum_canary[15];` to:

```systemverilog
assign crit_bit = sum_sensor[15];
```

`sum_canary` continues to feed `wrong`, `correct`, `error_count`, `error_any`,
and `ref_bit` exactly as before.

### 1.5 Verify the module interface is unchanged

The ports of `adder_canary` (`clk`, `reset`, `alarm`, `crit_bit`, `ref_bit`,
`wrong`, `correct`, `error_count`, `error_any`) must not change.  No edits to
`nexys4_aging_top.sv` should be needed.

- [ ] Run `scripts/check_layout.sh` — must pass with no errors
- [ ] Confirm synthesis-only run (`synth_design`) completes without critical
      warnings on `adder_canary`

---

## Phase 2 — Constraints: co-locate both adder instances

> Goal: ensure `u_sensor` and `u_canary` occupy the same or immediately
> adjacent CLB columns so they age at the same rate.

### 2.1 Identify existing Pblock (or LOC constraints)

Check `src/constraints/fixed_pnr_constraints.xdc` for any existing placement
constraints on `u_adder/u_canary`.

- [ ] Open the post-implementation checkpoint in Vivado GUI after the first
      build (`build/.../impl_1/*.dcp`)
- [ ] Locate `u_adder/u_canary/FA[*]` cells in the device view
- [ ] Note the XY range of the canary placement (e.g., `SLICE_X10Y50` to
      `SLICE_X11Y65`)

### 2.2 Add Pblock constraint

In `src/constraints/` create or append a constraint that groups both adder
instances:

```tcl
create_pblock pblock_adders
add_cells_to_pblock pblock_adders [get_cells {u_adder/u_canary/FA[*] u_adder/u_sensor/FA[*]}]
resize_pblock pblock_adders -add {SLICE_X<x0>Y<y0>:SLICE_X<x1>Y<y1>}
set_property CONTAIN_ROUTING true [get_pblocks pblock_adders]
```

Replace `<x0>`, `<y0>`, `<x1>`, `<y1>` with coordinates that encompass both
adder instances (approximately double the height of the canary region or
side-by-side).

- [ ] Confirm the Pblock is accepted by Vivado without DRC errors
- [ ] Confirm both instances are placed inside the Pblock after
      `place_design`

### 2.3 Check critical path timing report

After implementation, open the timing summary:

- [ ] Confirm `WNS ≥ 0` (no setup violations at nominal voltage and
      temperature — the device is not yet aged)
- [ ] Locate the worst negative slack path; it should pass through
      `u_adder/u_sensor/FA[*]` LUT carry stages
- [ ] Note the slack value — this gives the expected `display_value` range:
      `N_alarm ≈ (slack_ns + T_setup) / T_step_ps × 1000`

---

## Phase 3 — Build and program

- [ ] Run `scripts/build_bitstream.sh --jobs 8` to completion
- [ ] Confirm bitstream lands in `artifacts/nexys4_aging_top.bit`
- [ ] Program the board via Vivado Hardware Manager or `openFPGALoader`
- [ ] If using App_2Nexys: update `BITSTREAM_DUT0` path in
      `App_2Nexys/config.py` if the artifact path changed

---

## Phase 4 — Hardware validation

> Goal: confirm the fix restores deterministic behavior in the expected range.

### 4.1 VIO smoke test (no Python app required)

With the board connected to Vivado Hardware Manager:

- [ ] Open VIO core `u_vio`
- [ ] Confirm `probe_in3` (`locked`) = 1
- [ ] Confirm `probe_in2` (`alarm_sync`) pulses periodically (~1 Hz)
- [ ] Observe `probe_in0` (`display_value`) over 10+ sweeps — values should
      cluster tightly (target: ±5 steps or less)
- [ ] Confirm `probe_in0` is in a plausible range (100–900 steps for a fresh
      device at nominal voltage)

### 4.2 Python app validation

- [ ] Start App_Nexys with the correct serial port
- [ ] Let it run for at least 5 minutes, collecting CSV data
- [ ] Verify the `sensor` column in the CSV has low variance (std-dev < 5)
- [ ] Verify `error_count` is stable at 0 (or a low value, indicating no
      functional failures at nominal conditions)

### 4.3 Jitter characterization

- [ ] Collect 100+ consecutive `display_value` readings at room temperature
      and nominal voltage
- [ ] Compute mean (μ) and standard deviation (σ)
- [ ] Target: σ ≤ 2 steps (matches reference designs aging-study and
      sbcci_fpga_aging)
- [ ] Save results as `test_logs/validation_fixed_YYYYMMDD.csv`

---

## Phase 5 — External UART trigger (optional but recommended)

> Goal: replace the 1 Hz auto-trigger timer with a Python-controlled trigger,
> giving explicit confirmation that each sweep has completed before the next
> one starts.

### 5.1 RTL side — add RX command decoder

- [ ] In `nexys4_aging_top.sv`, instantiate a minimal UART RX module
      (reuse or adapt `uart_tx.sv` logic for RX)
- [ ] Decode command byte `0x54` (`'T'`) as "trigger sweep"
- [ ] Route the decoded trigger to the same `combined_trigger` OR-gate
      that the 1 Hz timer feeds
- [ ] Optionally disable or keep the 1 Hz timer as a fallback

### 5.2 Python side — DUTWorker modification

In `App_Nexys/dut_worker.py` (or equivalent):

```python
# After successfully reading and parsing a 15-byte packet:
self._serial.write(b'\x54')   # send 'T' to trigger next sweep
```

This creates a closed loop: Python receives a result, immediately re-arms the
sweep, and processes the next result when it arrives (~200 ms round-trip).

- [ ] Test that the UART RX decoding does not interfere with the TX stream
      (use separate baud-rate timing or a simple state machine)
- [ ] Confirm the trigger byte is not echoed back in the UART output stream
- [ ] Verify `display_value` arrives ~200 ms after each trigger in the
      Python log

---

## Phase 6 — Regression check

- [ ] Re-run `scripts/check_layout.sh`
- [ ] Confirm no new critical warnings in the implementation log
- [ ] Confirm `error_count` still increments correctly when the voltage is
      reduced below the functional margin (manual test: lower PSU by ~50 mV)
- [ ] Confirm `display_value` decreases monotonically as voltage is reduced
      (timing margin shrinks → alarm fires earlier)
- [ ] Confirm `wrong`/`correct` fields in the UART packet reflect the adder
      canary output at alarm (not the sensor adder output)

---

## Phase 7 — Data collection for paper

> Goal: produce the measurement data needed to demonstrate the timing-to-error
> correlation in the journal submission.

- [ ] Define the experimental matrix:
      - Temperatures: 25 °C, 60 °C, 100 °C, 120 °C (use oven + Arduino PID)
      - Voltages: nominal (1.0 V), −5%, −10%, −15% VCCINT
      - Duration: minimum 1 hour per condition
- [ ] For each condition, collect CSV with columns:
      `timestamp, temp_die, vccint, display_value, error_count, wrong, correct`
- [ ] Plot `display_value` vs. time per condition to show drift
- [ ] Plot `error_count` onset vs. `display_value` threshold to demonstrate
      predictive correlation
- [ ] Capture `wrong`/`correct` snapshots at first functional failure per
      condition

---

## Dependency graph

```
Phase 0 (baseline capture)
    │
    ▼
Phase 1 (RTL: adder_canary.sv)
    │
    ▼
Phase 2 (constraints: Pblock)
    │
    ▼
Phase 3 (build bitstream)
    │
    ├──► Phase 4 (hardware validation) ──► Phase 6 (regression)
    │                                               │
    ├──► Phase 5 (UART trigger, optional)           │
    │                                               ▼
    └───────────────────────────────────► Phase 7 (data collection)
```

---

## Quick reference: files to edit

| File | Phase | Nature of change |
|------|-------|-----------------|
| `src/rtl/aging_sensor/adder_canary.sv` | 1 | Add `toggle` FF, `a_sensor`, `u_sensor` instance; reassign `crit_bit` |
| `src/constraints/*.xdc` | 2 | Add Pblock for `u_sensor` + `u_canary` co-location |
| `src/rtl/top/nexys4_aging_top.sv` | 5 (optional) | Add UART RX decoder; route trigger byte to `combined_trigger` |
| `App_Nexys/dut_worker.py` (or equivalent) | 5 (optional) | Send `'T'` after each successful packet parse |
