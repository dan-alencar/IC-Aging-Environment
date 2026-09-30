# Firmware & Embedded Systems

This directory contains all embedded firmware controlling thermal chambers, supervisory MCUs, and communication routers.

## Directory Structure

```
firmware/
├── thermal_chamber/       # Oven temperature controllers & calibration tools
│   ├── PID_Controller/    # Active PID controller using ArduPID 1.0.1 (SIMC-tuned)
│   ├── arduino_termostato/# Bang-bang hysteretic thermostat controller
│   ├── FOPDT_Step_Test/   # Step-test logger to identify plant transfer function
│   ├── SSR_TEST/          # Hardware validation sketch for Solid-State Relay
│   ├── arduino_uart_tp_sniffer/ # Passive UART sniffer tool
│   └── legacy/            # Superseded sketches
│
├── uart_router/           # Communication routers
│   └── esp32_uart_router/ # ESP32 multiplexer (0x10 -> FPGA CROC, 0x20 -> STM32)
│
└── supervisory/           # Supervisory microcontrollers
    └── stm32l4_aging/     # STM32L4R9 firmware (PMIC TPS65400, OLED SSD1306)
```

## Thermal Chamber Notes
- **PID Tuning Constants:** `Kp = 2.78`, `Ki = 0.00106`, `Kd = 5.0` (derived via SIMC with `τc = θ` from FOPDT step-test model `G(s) = 1.56 * exp(-150.6s) / (1307.2s + 1)`). Do not modify without re-running the step test.
- **Protocol:** `GET_DATA\n` -> `DATA,<temp>,<sp>,<out>\n`, `GET_CONFIG\n` -> controller metadata string.
