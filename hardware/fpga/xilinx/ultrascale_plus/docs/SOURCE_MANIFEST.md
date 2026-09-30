# Source Manifest

This file lists the reproducible inputs used by `scripts/create_project.tcl`.
Generated Vivado folders such as `.runs`, `.gen`, `.cache`, `.hw`, `.sim`, and
`ip_user_files` are intentionally excluded from this clean project.

This tree is the consolidated version of the former
`auto_tuning_fpgaging/sbcci_fpga_aging/` project. The duplicate auto-tuning
project copy has been removed.

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

The clean tree consolidates sources that were scattered across generated Vivado
project directories. These legacy folders are retained only for reference.

| Clean area | Legacy reference area |
| --- | --- |
| `src/rtl/top/` | `../../aging_study_ultrascale/aging_study_ultrascale.srcs/sources_1/new/` and cleaned integration work |
| `src/rtl/monitor/` | Cleaned integration work around the XADC/System Monitor IP |
| `src/rtl/aging_sensor/` | `../../aging_study_ultrascale/aging_study_ultrascale.srcs/sources_1/imports/...` and `../../aging-study/aging-study.srcs/sources_1/imports/...` |
| `src/rtl/uart/` | `../../aging-study/aging-study.srcs/sources_1/imports/Projects/uart_test/...` |
| `src/constraints/` | `../../aging_study_ultrascale/aging_study_ultrascale.srcs/constrs_1/new/` with board-specific cleanup |
| `src/ip/` | `../../aging_study_ultrascale/aging_study_ultrascale.srcs/sources_1/ip/` and regenerated active IP configurations |

## Generated Outputs

The scripts create local generated output only in these ignored directories:

| Path | Contents |
| --- | --- |
| `build/` | Recreated `.xpr`, Vivado runs, generated IP products, and intermediate outputs |
| `artifacts/` | Copied bitstream, timing report, utilization report, IP status report, and optional debug probes |
