# IC Aging Core (`ic_aging_core`)

Shared Python package containing instrument drivers, wire protocol parsers, and UI components used across all desktop applications in `software/apps/`.

## Modules

- `ic_aging_core.instruments`: Hardware drivers for programmable power supplies (ITECH IT6502D, Agilent E3634A) and Arduino/ESP thermal chamber controllers.
- `ic_aging_core.protocols`: Binary and ASCII protocol decoders for FPGA DUT packets (15-byte, 9-byte) and CRC16-Modbus framing.
- `ic_aging_core.ui`: Theme definitions (Catppuccin Mocha), custom Qt plot widgets, and status components.

## Installation
For local development:
```bash
pip install -e software/core
```
Or simply add `software/core` to `PYTHONPATH`.
