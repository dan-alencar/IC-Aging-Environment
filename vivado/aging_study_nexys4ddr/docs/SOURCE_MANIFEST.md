# Source Manifest

This file lists the reproducible inputs used by `scripts/create_project.tcl`.
Generated Vivado folders such as `.runs`, `.gen`, `.cache`, `.hw`, `.sim`,
`ip_user_files`, and all `.dcp` checkpoints are intentionally excluded.

This project uses a **pure RTL flow** — no Vivado Block Design.
The former BD-based `design_1.bd` was removed; the top module is now
`nexys4_aging_top.sv`, which instantiates all modules directly in SystemVerilog.

## Active Build Inputs

| Path | Purpose |
| --- | --- |
| `src/rtl/top/nexys4_aging_top.sv` | SystemVerilog top module — instantiates all RTL modules and the XADC Unisim primitive |
| `src/ip/clk_wiz_0/clk_wiz_0.xci` | Standalone clock wizard IP (3× 100 MHz outputs: clk\_en 100°, psclk DPS, clk\_sys 0°) |
| `src/constraints/Nexys-4-DDR-Master.xdc` | Nexys4 DDR pin, timing, and board constraints |
| `src/constraints/fixed_pnr_constraints.xdc` | Fixed BEL/LOC placement for `u_sensor` FFs/LUT and PBLOCK for `u_adder/u_canary` ripple chain |
| `src/rtl/aging_sensor/adder_canary.sv` | 16-bit LUT ripple-carry adder aging sensor with error counting |
| `src/rtl/aging_sensor/controller_controller.sv` | Phase-sweep FSM — drives MMCM DPS until metastability alarm |
| `src/rtl/aging_sensor/failure_holder.sv` | Sticky latch for functional failures |
| `src/rtl/aging_sensor/lut_full_adder.sv` | Single-bit LUT full adder cell (used by ripple_adder) |
| `src/rtl/aging_sensor/modern_sensible.sv` | Three-FF XOR metastability sensor across phase-shifted clock domains |
| `src/rtl/aging_sensor/ripple_adder.sv` | 16-stage ripple-carry adder instantiating lut_full_adder |
| `src/rtl/aging_sensor/temp_catcher.sv` | XADC DRP polling — reads die temperature and VCCINT |
| `src/rtl/display/BINtoBCD.sv` | Binary-to-BCD converter for the 7-segment display |
| `src/rtl/display/DisplayController.sv` | 8-digit multiplexed 7-segment display driver |
| `src/rtl/uart/sensor_stream.sv` | Sensor packet serialiser |
| `src/rtl/uart/uart_tx.sv` | UART transmitter |

## Preserved Reference Inputs

| Path | Reason |
| --- | --- |
| `references/fixed_pnr.dcp` | Routed checkpoint from the original BD-based flow; useful for auditing the fixed-route XDC. **Not used as a Vivado build input.** Note: hierarchy inside this DCP reflects old BD paths — `extract_fixed_pnr_constraints.tcl` should be run against a checkpoint built from the current pure-RTL flow. |
| `src/sim/sim.v` | Original behavioral simulation source (not added to project) |

## DCP Policy

Do not commit generated `.dcp` files. Build checkpoints are regenerated under
`build/` (gitignored) on each machine.

The exception is `references/fixed_pnr.dcp`, which is source-controlled as a
reference artifact for the aging experiment. The active build consumes the
hand-edited XDC constraints in `src/constraints/fixed_pnr_constraints.xdc`
directly.
