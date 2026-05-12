# Source Manifest

This file lists the reproducible inputs used by `scripts/create_project.tcl`.
Generated Vivado folders such as `.runs`, `.gen`, `.cache`, `.hw`, `.sim`, and
`ip_user_files` are intentionally excluded from this clean project.

## Active Build Inputs

| Path | Module / Core | Purpose |
| --- | --- | --- |
| `src/rtl/top/fpga_unified_top.sv` | `fpga_unified_top` | Top-level design |
| `src/rtl/aging_sensor/controller_controller.v` | `controller_controller` | Phase-shift controller |
| `src/rtl/aging_sensor/modern_sensible.v` | `modern_sensible` | Aging sensor sampler |
| `src/rtl/aging_sensor/nand_series.v` | `not_series` | Critical path chain |
| `src/rtl/monitor/sysmon_monitor.sv` | `sysmon_reader` | XADC read sequencer |
| `src/rtl/uart/sensor_stream.v` | `sensor_stream` | Packetizes monitor data |
| `src/rtl/uart/uart_tx.v` | `uart_tx` | UART transmitter |
| `src/rtl/uart/uart_router.sv` | `uart_router` | Routes UART traffic |
| `src/rtl/uart/uart_arbiter.sv` | `uart_arbiter` | Arbitrates monitor and routed UART TX |
| `src/constraints/fpga_aging_constraints.xdc` | XDC | Pins, clocks, and bitstream properties |
| `src/ip/clk_wiz_0/clk_wiz_0.xci` | `clk_wiz_0` | Clock wizard |
| `src/ip/vio_0/vio_0.xci` | `vio_0` | Debug/control VIO |
| `src/ip/xadc_wiz_0/xadc_wiz_0.xci` | `xadc_wiz_0` | XADC/System Monitor wizard |

## Preserved Legacy Inputs

These files were present in the old Vivado project but were disabled or unused
in the current `fpga_unified_top` build. They are preserved for reference under
`src/rtl/legacy/` and are not added by `create_project.tcl`.

| Path | Module | Reason excluded |
| --- | --- | --- |
| `src/rtl/legacy/fpga_aging_top.v` | `fpga_unified_top` | Older alternate top with duplicate module name |
| `src/rtl/legacy/xadc_raw.v` | `xadc_raw` | Disabled in old project |
| `src/rtl/legacy/temp_catcher.v` | `temp_catcher` | Disabled in old project |
| `src/rtl/legacy/failure_holder.v` | `failure_holder` | Disabled in old project |
| `src/rtl/legacy/holder_button.v` | `holder_button` | Disabled in old project |

## Original Source Locations

The clean tree was copied from the old project paths below:

| Clean area | Original area |
| --- | --- |
| `src/rtl/top/` | `../../sbcci_fpga_aging/sbcci_fpga_aging.srcs/sources_1/new/` |
| `src/rtl/monitor/` | `../../sbcci_fpga_aging/sbcci_fpga_aging.srcs/sources_1/new/` |
| `src/rtl/aging_sensor/` | `../../sbcci_fpga_aging/sbcci_fpga_aging.srcs/sources_1/imports/sources_1/...` |
| `src/rtl/uart/` | `../../sbcci_fpga_aging/sbcci_fpga_aging.srcs/sources_1/imports/...` |
| `src/constraints/` | `../../sbcci_fpga_aging/sbcci_fpga_aging.srcs/constrs_1/imports/constraints/` |
| `src/ip/` | `../../sbcci_fpga_aging/sbcci_fpga_aging.srcs/sources_1/ip/` |
