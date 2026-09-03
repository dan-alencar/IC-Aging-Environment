# hdl/src/ — RTL and constraints

Not populated yet — this is where front F1 (RTL) and front F2 (constraints/fitter
flow) put their deliverables. Expected subdirectories, mirroring
`../../../vivado/aging_study_nexys4ddr/src/`:

- `rtl/top/` — top-level module.
- `rtl/aging_sensor/` — the ported sensor: PLL phase-sweep controller, metastability
  sampler, critical-path element(s).
- `rtl/uart/` — telemetry packet serializer / UART (or JTAG UART) interface.
- `rtl/display/` (optional) — if the port keeps a 7-segment/LED debug readout.
- `constraints/` — `.sdc` (timing exceptions for the intentionally-violated sensor
  path) and the `.qsf` location assignments that pin the sensor's placement, per
  front F2's reproducibility requirement.

`scripts/check_layout.sh` in the parent directory checks for
`src/rtl/top/max10_aging_top.sv`, `src/constraints/max10_aging.sdc`, and
`src/constraints/max10_aging.qsf` as placeholder expected paths — rename these in
both that script and `scripts/create_project.tcl` if the team settles on different
names.
