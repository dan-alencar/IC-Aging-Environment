# CROC FPGA Sensor Monitor & Programmer

A cross-platform desktop application for monitoring aging sensors on the CROC RISC-V FPGA and programming bitstreams via Vivado.

## Features

- **Visual Sensor Display**: Real-time grid visualization of 32-bit alarm registers (ALARM_F and ALARM_RF)
- **FPGA Programming**: Program bitstreams directly from the application using Vivado
- **STM32 Communication**: Send voltage and display commands to the STM32 MCU
- **Large Log Terminal**: Comprehensive logging of all communication and events
- **Cross-Platform**: Works on Windows 11 and Linux

## Screenshots

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ ● Connected: COM3                    Bitstream: test.bit       2025-01-13   │
├─────────────────────────────────────┬───────────────────────────────────────┤
│                                     │                                       │
│     ALARM_F (AM Sensor)             │     Communication Log                 │
│     ┌─────────────────────────┐     │                                       │
│     │ ■ ■ □ □ □ □ □ □ │ 31-24 │     │  [12:34:56] [CROC] F: 0x3 | RF: 0x0  │
│     │ □ □ □ □ □ □ □ □ │ 23-16 │     │  [12:34:57] [CROC] F: 0x3 | RF: 0x0  │
│     │ □ □ □ □ □ □ □ □ │ 15-8  │     │  [12:34:58] [STM32] OK - VOLT        │
│     │ □ □ □ □ □ □ □ □ │ 7-0   │     │  ...                                 │
│     └─────────────────────────┘     │                                       │
│                                     │                                       │
│     ALARM_RF (LF Sensor)            │                                       │
│     ┌─────────────────────────┐     │                                       │
│     │ □ □ □ □ □ □ □ □ │       │     │                                       │
│     │ □ □ □ □ □ □ □ □ │       │     │                                       │
│     │ □ □ □ □ □ □ □ □ │       │     │                                       │
│     │ □ □ □ □ □ □ □ □ │       │     │                                       │
│     └─────────────────────────┘     │                                       │
│                                     │                                       │
│  Total Active: 2/64  ● NOMINAL      │  [Auto-scroll ✓]  [Clear] [Save Log]  │
├─────────────────────────────────────┴───────────────────────────────────────┤
│  [FPGA Programming] [STM32 Control] [Settings]                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Installation

### Prerequisites

1. **Python 3.10+** - Download from [python.org](https://www.python.org/downloads/)
2. **Vivado** - Required for FPGA programming (Vivado Lab edition is sufficient)

### Windows

```powershell
# Clone or download the application
cd croc_app_v2

# Create virtual environment (recommended)
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python App.py
```

### Linux

```bash
# Clone or download the application
cd croc_app_v2

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Add user to dialout group for serial port access (if needed)
sudo usermod -a -G dialout $USER
# Log out and back in for group changes to take effect

# Run the application
python App.py
```

## Configuration

On first run, the application creates a `settings.json` file with default values.

### Serial Port
- **Windows**: Typically `COM3`, `COM4`, etc.
- **Linux**: Typically `/dev/ttyUSB0`, `/dev/ttyACM0`, etc.

### Vivado Path
The application attempts to auto-detect Vivado. If detection fails, configure manually:
- **Windows**: `C:\Xilinx\Vivado\2024.2\bin\vivado.bat`
- **Linux**: `/tools/Xilinx/Vivado/2024.2/bin/vivado`

### Bitstream Directory
Set the directory containing your `.bit` files for FPGA programming.

## Usage

### Connecting to FPGA

1. Go to **Settings** tab
2. Select the correct serial port from the dropdown
3. Set baud rate to **115200** (default)
4. Click **Connect**

### Monitoring Sensors

Once connected, the sensor visualization updates automatically when the CROC sends data in the format:
```
F: 0x<hex_value> | RF: 0x<hex_value>
```

- **Green cells**: Sensor inactive (bit = 0)
- **Red cells**: Sensor active/alarming (bit = 1)

### Programming FPGA

1. Go to **FPGA Programming** tab
2. Browse to your bitstream directory
3. Select a bitstream from the dropdown
4. Click **PROGRAM FPGA**

Progress is shown in the progress bar, and detailed output appears in the log.

### STM32 Control

1. Go to **STM32 Control** tab
2. **Voltage Control**: Set Vcore (0.0V - 1.8V)
3. **Display Control**: Change OLED page (1-6)
4. **Manual Command**: Send raw text to CROC or protocol commands to STM32

## File Structure

```
croc_app_v2/
├── App.py              # Application entry point
├── main_window.py      # Main GUI window
├── config.py           # Configuration management
├── router.py           # UART routing and parsing
├── serial_thread.py    # Serial communication thread
├── protocol.py         # STM32 protocol definitions
├── fpga_manager.py     # FPGA programming manager
├── sensor_widget.py    # Visual sensor display widget
├── history_logger.py   # Event logging for experiments
├── program_fpga.tcl    # Vivado TCL script for programming
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

## Protocol Reference

### CROC Output Format
The CROC firmware sends sensor data as text:
```
F: 0x<alarm_f_32bit> | RF: 0x<alarm_rf_32bit>
```

Example:
```
F: 0xDEADBEEF | RF: 0x12345678
```

### STM32 Protocol
Commands to STM32 use a binary protocol:
```
[Header:0x20][Ctrl][Len_H][Len_L][Payload...][CRC_L][CRC_H]
```

Control byte:
- Bits 7: Direction (0x00=Slave request)
- Bits 6-4: Error code
- Bits 3-0: Function (0x01=Page, 0x02=Message, 0x03=Voltage)

### Routing Headers
- `0x10`: Route to CROC
- `0x20`: Route to STM32

## Troubleshooting

### Serial Port Not Found
- **Windows**: Check Device Manager for COM port number
- **Linux**: Run `ls /dev/ttyUSB*` or `ls /dev/ttyACM*`
- **Linux**: Ensure user is in `dialout` group

### Vivado Not Found
1. Verify Vivado is installed
2. Check the path in Settings tab
3. Ensure `hw_server` can start (may need to run Vivado once manually)

### FPGA Programming Fails
1. Check JTAG cable connection
2. Verify FPGA is powered
3. Try running `hw_server` manually before programming
4. Check Vivado license

### No Sensor Data Received
1. Verify serial connection is established
2. Check baud rate matches firmware (115200)
3. Ensure CROC firmware is running and sending data

## License

See LICENSE file for details.

## Contributing

Issues and pull requests welcome!
