# Dual-Adder Sensor Architecture: Rationale and Design

## 1. Context

The `aging_study_nexys4ddr` project is a hardware-in-the-loop FPGA aging monitor
targeting the Artix-7 (Nexys4 DDR, xc7a100tcsg324-1).  The central measurement
goal is to observe the degradation of a combinational critical path over time by
correlating two independent metrics:

1. **Timing metric** — the number of MMCM phase-shift steps required before the
   metastability sensor (`modern_sensible`) detects a setup/hold violation on the
   critical path output.  A fresh device requires many steps; an aged, slower
   device requires fewer.

2. **Functional metric** — the number of wrong results produced by the same
   circuit when it is clocked at the nominal frequency.  This counts actual
   computation errors caused by timing violations.

The connection between these two metrics is the scientific core of the
experiment: the timing metric should degrade (decrease) in a way that *predicts*
the onset of functional errors, creating a continuous, non-destructive aging
indicator.  For this prediction to be credible, both metrics must observe the
**same** aging-sensitive circuit.

---

## 2. The Original Problem: Why `display_value` Reached ~9 000

### 2.1 How the phase sensor works

The sensor contains three flip-flops driven by three different clock phases
(from a single MMCM):

```
in_sensor ──┬──► FF1 (psclk, 0° + dynamic shift)─┐
            │                                      ├──► XOR ──► FF3 (clk_en, 99°) ──► alarm
            └──► FF2 (sclk, 0° reference)──────────┘
```

Phase is decremented one step at a time.  At each step the controller checks
whether FF1 and FF2 captured different values of `in_sensor`.  They differ when
the psclk edge falls within the setup/hold window of the signal transition —
i.e., when the critical path has not settled before psclk samples it.  The step
count at first alarm (`display_value`) is the timing metric.

For this to work deterministically, `in_sensor` **must transition at or near
every clock cycle**, so that at the correct phase offset the sensor always has a
transition to detect.

### 2.2 What `crit_bit = sum_canary[15]` actually does

In the original `aging_study_nexys4ddr` implementation:

```
in_sensor = crit_bit = sum_canary[15]
```

where `sum_canary` is the output of a free-running 16-bit LUT ripple-carry adder
(`a` increments by 1 every clock cycle, `B = 0xAAAA` is constant).

The MSB of this sum (`sum_canary[15]`) transitions only when a carry ripples
through **all 16 stages** — specifically at the boundaries:

```
a = 0x5555:  0x5555 + 0xAAAA = 0xFFFF  →  bit 15 = 1
a = 0x5556:  0x5556 + 0xAAAA = 0x10000 →  bit 15 = 0  (TOGGLE)
a = 0xD555:  0xD555 + 0xAAAA = 0x17FFF →  bit 15 = 1
a = 0xD556:  0xD556 + 0xAAAA = 0x18000 →  bit 15 = 0  (TOGGLE)
```

With `a` as a free-running counter, these boundaries occur **twice per 65 536
clock cycles**.  At ~14 cycles per phase step (INIT_SHIFT + psdone wait), the
phase sweep visits each step for only 14 clock cycles — far too few to wait for
the rare carry event.

### 2.3 Consequence: stochastic, large measurements

The alarm fires by statistical coincidence: it triggers when a full-carry
transition happens to overlap with the phase window at the current step count.
This produces:

- **Unpredictable `display_value` readings**, ranging up to ~9 000 steps.
- **High jitter** (±hundreds of steps) rather than the ±2 steps seen in
  reference designs.
- **No deterministic relationship** between phase count and actual propagation
  delay, undermining the scientific validity of the timing metric.

The 9 000-step range is not evidence of a severely degraded path; it is noise
caused by the extremely low duty cycle of the relevant transition on `in_sensor`.

### 2.4 Comparison with reference designs

| Design | `in_sensor` source | Transition rate | Observed range |
|--------|--------------------|-----------------|----------------|
| `aging-study` | NOT/NAND chain driven by `change` (toggles every ~14 cycles) | ~every 14 clk | ~800 ± 2 steps |
| `sbcci_fpga_aging` | Registered `error_flag` FF output (transitions each eval) | ~every cycle | ~800 ± 2 steps |
| `aging_study_nexys4ddr` (original) | `sum_canary[15]` combinatorial MSB | ~every 32 768 clk | ~9 000 ± hundreds |

Both reference designs provide a continuously-toggling `in_sensor`, making the
alarm deterministic.  The new design does not.

### 2.5 The auto-retriggering mechanism is not the direct cause

The 1 Hz periodic timer (`ctrl_rst_n`) resets `inc_count` and the FSM state once
per second.  A sweep of 9 000 steps takes approximately
`9 000 × 14 cycles / 100 MHz ≈ 1.26 ms`, well within the 1-second window.  The
back-off phase (restoring MMCM phase) takes another 1.26 ms.  The timer does
**not** interrupt the sweep.

The timer mechanism and the `controller_controller` FSM are otherwise correct.
In fact, the new controller improves on the reference designs: it uses
**edge-detection** on `psdone` (`psdone && !psdone_prev`) rather than
level-sensitivity, and keeps all counters synchronous to `clk_sys`.

---

## 3. Scientific Requirements for a Journal Paper

For a submission to a venue such as the Journal of Integrated Circuits and
Systems (JICS), the central scientific argument requires:

> *Both the timing metric (phase-sensor step count) and the functional metric
> (error count) measure the degradation of the same circuit element, so that the
> observed correlation between them reflects the aging of that element rather
> than a coincidental statistical relationship between two unrelated paths.*

If `in_sensor` comes from a NAND chain and `error_count` comes from the ripple
adder, a reviewer can correctly argue that:

- The two metrics may age at different rates (different logic structures, different
  placement, different stress conditions).
- Any observed correlation may be incidental rather than causal.
- The NAND chain provides no information about the adder's timing margin.

**Option B (separate NAND chain for sensor, adder for canary) does not satisfy
this requirement.**

The options considered and their scientific validity are summarized below.

### 3.1 Options evaluated

| Option | `in_sensor` source | `error_count` source | Same path? | Transition rate | Assessment |
|--------|--------------------|----------------------|------------|-----------------|------------|
| A — NAND chain (aging-study style) | NAND/NOT chain | ripple adder | **No** | High ✓ | Weak: different circuits |
| B — Registered `crit_bit` | `crit_bit` latched by FF | ripple adder | Yes ✓ | Still rare (same boundary) | Weak: transition rate unchanged |
| C — Lower bit (`sum_canary[7]`) | 8-stage carry MSB | ripple adder | Partial | High ✓ | Weak: measures only half the path |
| D — Time-multiplexed single adder | worst-case toggle when sweeping | same adder, counter when idle | Yes ✓ | High ✓ | Acceptable but adds mode-switching complexity |
| **E — Dual parallel adder instances** | **sensor adder, toggle-driven** | **canary adder, counter-driven** | **Yes ✓** | **High ✓** | **Recommended** |

### 3.2 Why Option E is chosen

Option E satisfies every requirement:

1. **Same circuit structure**: Both adders are 16-bit LUT ripple-carry adders
   instantiated from the same RTL module (`ripple_adder #(.N(16))`), with the
   same operand B (`0xAAAA`), the same `DONT_TOUCH` attributes, and constrained
   to the same die region.

2. **Maximum timing sensitivity**: The sensor adder is driven with the
   worst-case pattern (carry ripples through all 16 stages at every clock
   cycle), exercising the full critical path continuously.

3. **Comprehensive functional coverage**: The canary adder retains the
   free-running counter, accumulating errors across all input values.

4. **Deterministic phase measurement**: `sum_sensor[15]` toggles every clock
   cycle, providing a reliable periodic transition for the sensor — restoring
   the ±2-step jitter behavior of the reference designs.

5. **Minimal invasiveness**: Changes are confined to `adder_canary.sv` (one
   new adder instance, one toggle FF, one output reassignment) plus a Pblock
   constraint entry.

---

## 4. Architecture of the Dual-Adder Sensor

### 4.1 System-level overview

```
                     ┌──────────────────────────────────────────────────────┐
                     │                  adder_canary                        │
                     │                                                      │
  clk_sys ──────────►│  toggle FF  ─► a_sensor (0x5555/0x5556) ─►         │
                     │                         ripple_adder (SENSOR)  ─► crit_bit ──► modern_sensible.in_sensor
                     │                                                      │
                     │  counter (a) ─────────────────────────────►         │
                     │                         ripple_adder (CANARY) ─► sum_canary[15:0]
                     │                                              ┌─────► wrong, correct
                     │                                              └─────► error_count, error_any
                     │                                                      │
                     │  ref_bit = (a + 0xAAAA)[15]  (behavioral)           │
                     └──────────────────────────────────────────────────────┘
                                                                         
  crit_bit ─────────────────────────────────────────────────────► modern_sensible.in_sensor
                                                                         ▼
                                                               FF1 (psclk) ─┐
                                                               FF2 (sclk)  ─┴─► XOR ─► FF3 (clk_en) ─► alarm_sig
                                                                         ▼
                                                         2-FF sync ─► alarm_sync ─► controller_controller
```

### 4.2 The sensor adder (worst-case toggle path)

A single-bit flip-flop `toggle` is registered on `clk_sys` and inverts each
cycle:

```
toggle[N+1] = ~toggle[N]
```

The sensor adder input is derived from `toggle` by selecting between the two
carry-critical boundary values of `a`:

```
a_sensor = toggle ? 16'h5556 : 16'h5555
```

With `B = 0xAAAA`, the addition produces:

| `toggle` | `a_sensor` | `a_sensor + B` | `sum_sensor[15]` | Carry-out to bit 15 |
|----------|-----------|----------------|------------------|---------------------|
| 0 | 0x5555 | 0xFFFF | **1** | 0 |
| 1 | 0x5556 | 0x10000 | **0** | 1 |
| 0 | 0x5555 | 0xFFFF | **1** | 0 |
| … | … | … | … | … |

The MSB toggles on **every clock cycle**, and the carry ripple propagates
through **all 16 LUT stages** on each transition.  The propagation delay of this
transition is the maximum delay of the 16-bit LUT chain — the same quantity
measured by the phase sensor.

`crit_bit = sum_sensor[15]` is the output assigned to
`modern_sensible.in_sensor`.

### 4.3 The canary adder (functional error path)

The canary adder is unchanged from its original role.  It adds a free-running
16-bit counter `a` (increments each cycle) to `B = 0xAAAA`, producing
`sum_canary`.  A freely-synthesised reference `sum_ref = a + B` (may use
CARRY4) provides the expected result.

On the rising edge of `alarm_sync` (first alarm of each sweep), `wrong` and
`correct` latch the adder's computed vs. expected MSB.  `error_count` is a
wrapping counter incremented whenever `sum_canary[15:0] != sum_ref[15:0]`.

### 4.4 Why the transition rate matches the reference designs

In the `aging-study` reference design, `in_sensor` is driven by a NAND chain
whose input is `change` — a signal that toggles once per `CHECK_ALARM` state
visit, approximately every 14 `clk_sys` cycles during a sweep.  The sensor
fires because each toggle propagates through the chain, producing a transition
on `in_sensor` every ~14 cycles.

With the dual-adder approach, `toggle` toggles **every** cycle (faster), and
the worst-case carry propagation occurs every cycle.  The alarm still fires at
the same physical step count (determined by the critical path delay), but the
sensor has far more opportunities per step to detect the transition.  This
eliminates the stochastic behavior and restores small jitter.

### 4.5 What the phase step count means

Let `T_prop` be the propagation delay of the worst-case carry through all 16
LUT stages.  At the step count `N_alarm`:

```
psclk edge offset = N_alarm × T_step ≈ N_alarm × 17.86 ps
```

The sensor fires when the psclk edge falls within the metastability window
centered on `T_prop`.  As the device ages and gates slow down, `T_prop`
increases.  The psclk edge needs **fewer** steps to reach the (later) transition
window.  Therefore `N_alarm` **decreases** monotonically with aging.

The canary `error_count` begins to accumulate when `T_prop` exceeds the clock
period minus the setup time — the point at which functional failures begin.
The timeline is:

```
N_alarm (high, ~800)  →  aging  →  N_alarm decreases  →  error_count starts rising
```

The two metrics are **causally connected** because they both measure the delay of
the 16-bit carry chain on the same die.

### 4.6 Physical implementation requirements

To ensure both adder instances age at the same rate and that the phase
measurement is valid for the canary path:

1. **Co-location**: Both `u_sensor` and `u_canary` instances must be constrained
   to the same Pblock (or adjacent CLB columns).  The existing
   `fixed_pnr_constraints.xdc` approach applies.

2. **Identical routing**: Both instances carry the same `DONT_TOUCH` attribute
   on every `lut_full_adder` cell.  Vivado will preserve the LUT-chain structure
   and not introduce CARRY4 primitives.

3. **Operand B**: Both instances use `B = 16'hAAAA`.  The alternating pattern
   1010...10 maximizes the number of carry-generate/propagate combinations,
   stressing the full carry chain.

4. **No shared logic**: `a_sensor` is driven by the local `toggle` FF only; it
   does not share any LUT with the `a` counter driving the canary adder.

### 4.7 Impact on the UART packet and Python app

`crit_bit` is now the output of `u_sensor` rather than `u_canary`.  The
functional outputs (`wrong`, `correct`, `error_count`, `error_any`) remain
from `u_canary` and are unchanged.  The 15-byte UART packet layout is
unaffected; `display_value` (phase step count from `sensor[15:0]`) and
`error_count` retain their existing packet positions.

---

## 5. Summary of Changes Required

| File | Change |
|------|--------|
| `src/rtl/aging_sensor/adder_canary.sv` | Add `toggle` FF, `a_sensor` signal, `u_sensor` `ripple_adder` instance; reassign `crit_bit` to `sum_sensor[15]` |
| `src/rtl/aging_sensor/ripple_adder.sv` | None (reused as-is) |
| `src/rtl/aging_sensor/lut_full_adder.sv` | None |
| `src/rtl/top/nexys4_aging_top.sv` | None (interface unchanged) |
| `src/constraints/` | Add Pblock constraint co-locating `u_adder/u_sensor` and `u_adder/u_canary` |
| All other RTL, Python apps, UART protocol | None |

---

## 6. Paper Narrative Summary

> We deploy two structurally identical 16-bit LUT ripple-carry adder instances
> on the same device, co-located within the same floorplan region.  The first
> (sensor adder) is driven with a worst-case alternating input pattern that
> forces carry propagation through all 16 LUT stages at every clock cycle.  Its
> MSB feeds the three-flip-flop metastability sensor, which measures the phase
> margin of the carry chain by sweeping the MMCM dynamic phase shift until a
> setup/hold violation is detected.  The second (canary adder) receives a
> free-running counter input and compares its output against a fast reference to
> accumulate functional error counts.  Because both adders are physically
> adjacent and structurally identical, they degrade at the same rate.  The
> timing metric (phase step count at first alarm) therefore serves as a
> continuous, non-destructive predictor of the functional failure onset observed
> in the canary, establishing a direct, causal link between timing degradation
> and computation error in an aging FPGA fabric.
