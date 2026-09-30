# Hardware & RTL

This directory contains all digital design assets for the IC-Aging research group, spanning multiple FPGA vendors and future ASIC targets.

## Directory Structure

```
hardware/
├── fpga/
│   ├── xilinx/
│   │   ├── nexys4_ddr/       # Digilent Nexys4 DDR (Artix-7 xc7a100t) - Primary burn-in target
│   │   └── ultrascale_plus/  # Custom UltraScale+ (xcau15p) - SBCCI target
│   └── intel/
│       └── de10_lite/        # Terasic DE10-Lite (MAX10 10M50DA) port
├── common/                   # Shared RTL modules across vendors (sensors, UART, filters)
└── asic/                     # Future ASIC PDKs (SkyWater 130nm, GlobalFoundries 180nm, etc.)
```

## FPGA Targets & Build Systems

### 1. Xilinx Artix-7 (Nexys4 DDR) — `hardware/fpga/xilinx/nexys4_ddr`
- **Device:** `xc7a100tcsg324-1`
- **Top:** `nexys4_aging_top`
- **Key Feature:** Fixed placement and routing (`src/constraints/fixed_pnr_constraints.xdc`) locking the carry-chain adder critical path to ensure reproducible aging measurements across rebuilds.
- **Build:**
  ```bash
  cd hardware/fpga/xilinx/nexys4_ddr
  scripts/check_layout.sh
  scripts/create_project.sh
  scripts/build_bitstream.sh --jobs 8
  ```

### 2. Xilinx Artix UltraScale+ (SBCCI) — `hardware/fpga/xilinx/ultrascale_plus`
- **Device:** `xcau15p-ffvb676-1-i`
- **Top:** `fpga_unified_top`
- **Key Feature:** Uses block design and XADC/SysMon for on-chip temperature and VCCINT telemetry. Interfaced via ESP32 router.
- **Build:**
  ```bash
  cd hardware/fpga/xilinx/ultrascale_plus
  scripts/check_layout.sh
  scripts/create_project.sh
  scripts/build_bitstream.sh --jobs 8
  ```

### 3. Intel MAX10 (DE10-Lite) — `hardware/fpga/intel/de10_lite`
- **Device:** `10M50DAF484C7G`
- **EDA:** Intel Quartus Prime
- **Documentation:** See `docs/fpga_ports/max10_de10lite/`
