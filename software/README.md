# Software & Desktop Instrumentation

This directory houses the host software used to configure, monitor, control, and log accelerated IC aging experiments.

## Directory Structure

```
software/
├── apps/                         # Standalone desktop GUI applications
│   ├── App_Nexys/                # Single DUT (Nexys4 DDR Artix-7)
│   ├── App_2Nexys/               # Dual DUT (Two Nexys4 DDR boards, closed-loop VCCINT)
│   ├── App_CornerSweep/          # Characterization tool (failure boundary voltage sweep)
│   └── App_FPGAging_Slack_Sensor/# UltraScale+ CROC target with STM32 bridge
├── core/                         # Shared Python package (ic_aging_core)
└── launcher.py                   # Unified selector dialog
```

## Running the Applications

### Via Root Launcher (Recommended)
From the repository root:
```bash
./run.sh
```
This presents a dark-themed GUI selector to launch any of the four applications.

### Direct Standalone Launch
Each application can be launched directly:
```bash
cd software/apps/App_Nexys && ./run.sh
cd software/apps/App_2Nexys && ./run.sh
cd software/apps/App_CornerSweep && ./run.sh
cd software/apps/App_FPGAging_Slack_Sensor && ./run.sh
```
*Note: Virtual environments (`.venv/`) are created automatically inside each app directory on first launch.*
