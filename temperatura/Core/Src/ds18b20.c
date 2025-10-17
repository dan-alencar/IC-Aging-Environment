/*
 * DS18B20.c
 *
 * Implements 1-Wire communication and DS18B20 sensor reading.
 * The GPIO control functions (Input_Pin, Output_Pin) have been replaced
 * with a single HAL-compatible Onewire_Init function that uses the
 * GPIO_InitTypeDef struct to correctly configure the pin mode for the STM32F3.
 *
 * NOTE: This code assumes the existence of the following macros/variables
 * in main.h or ds18b20.h:
 * - ONEWIRE_GPIO_Port (e.g., GPIOA)
 * - ONEWIRE_Pin (e.g., GPIO_PIN_x)
 * - HAL_RCC_GetHCLKFreq() returns the system clock frequency for DWT delay.
 * - CoreDebug, DWT structures are available.
 */

#include "ds18b20.h"
#include "stm32f3xx_hal.h" // Correct HAL include for STM32F3

// =================================================================================
// 1. DWT Delay Functions
// =================================================================================

// Initialize the DWT for microsecond delay function
void delay_us_dwt_init(void) {
    // Enable DWT
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
    // Enable cycle counter
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
}

// Delay for the specified number of microseconds using DWT
void delay_us_dwt(uint32_t us) {
    // Calculate the number of cycles needed for the delay
    uint32_t delay_cycles = (HAL_RCC_GetHCLKFreq() / 1000000) * us;
    uint32_t start_cycle = DWT->CYCCNT;

    // Wait until the required number of cycles has elapsed
    while ((DWT->CYCCNT - start_cycle) < delay_cycles);
}

// =================================================================================
// 2. HAL-COMPATIBLE GPIO Initialization (Replaces Input_Pin and Output_Pin)
// =================================================================================

/*
 * @brief Configures the 1-Wire pin mode using HAL functions.
 * @param Mode: GPIO_MODE_OUTPUT_OD for driving the bus, GPIO_MODE_INPUT for reading.
 */
void Onewire_Pin_Init(uint32_t Mode) {
    GPIO_InitTypeDef GPIO_InitStruct = {0};

    // Pin parameters common to both modes
    GPIO_InitStruct.Pin = ONEWIRE_Pin;
    GPIO_InitStruct.Pull = GPIO_PULLUP; // Essential for 1-Wire communication
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;

    // Set the specific mode (Output Open-Drain or Input)
    GPIO_InitStruct.Mode = Mode;

    // Apply the configuration
    HAL_GPIO_Init(ONEWIRE_GPIO_Port, &GPIO_InitStruct);
}


// =================================================================================
// 3. 1-Wire Protocol Functions
// =================================================================================

// Initialize OneWire bus and check for sensor presence
uint8_t onewire_reset(void) {
    uint8_t sensor_present = 0;

    // 1. Configure as Output Open-Drain and drive low
    Onewire_Pin_Init(GPIO_MODE_OUTPUT_OD);
    HAL_GPIO_WritePin(ONEWIRE_GPIO_Port, ONEWIRE_Pin, GPIO_PIN_RESET);
    delay_us_dwt(480);  // Pull low for 480µs (Reset Pulse)

    // 2. Switch to Input mode (release bus)
    Onewire_Pin_Init(GPIO_MODE_INPUT);
    delay_us_dwt(60);   // Wait for sensor response (Presence Pulse)

    // 3. Check for Presence Pulse (pin should be low)
    if (HAL_GPIO_ReadPin(ONEWIRE_GPIO_Port, ONEWIRE_Pin) == GPIO_PIN_RESET) {
        sensor_present = 1;
    }

    delay_us_dwt(480 - 60);  // Complete the reset sequence (Total time: 480µs + 60µs + 420µs)

    return sensor_present;
}

// Write a byte to the OneWire bus
void onewire_Write(uint8_t dato) {
    for (int i = 0; i < 8; i++) {
        uint8_t bit = (dato >> i) & 0x01;

        // Pin must be Output Open-Drain for writing
        Onewire_Pin_Init(GPIO_MODE_OUTPUT_OD);

        if (bit) {
            // Write '1' time slot: pull low briefly (6µs), then release/wait
            HAL_GPIO_WritePin(ONEWIRE_GPIO_Port, ONEWIRE_Pin, GPIO_PIN_RESET);
            delay_us_dwt(6);

            Onewire_Pin_Init(GPIO_MODE_INPUT); // Release bus
            delay_us_dwt(64);                  // Complete the slot (70µs total)
        } else {
            // Write '0' time slot: pull low for longer (60µs), then release/wait
            HAL_GPIO_WritePin(ONEWIRE_GPIO_Port, ONEWIRE_Pin, GPIO_PIN_RESET);
            delay_us_dwt(60);

            Onewire_Pin_Init(GPIO_MODE_INPUT); // Release bus
            delay_us_dwt(10);                  // Complete the slot (70µs total)
        }
    }
}

// Read a byte from the OneWire bus
uint8_t onewire_Read(void) {
    uint8_t read_byte = 0;

    for (int i = 0; i < 8; i++) {
        // Step 1: Start the read time slot (pull low for 6us)
        Onewire_Pin_Init(GPIO_MODE_OUTPUT_OD);
        HAL_GPIO_WritePin(ONEWIRE_GPIO_Port, ONEWIRE_Pin, GPIO_PIN_RESET);
        delay_us_dwt(6);

        // Step 2: Release bus (switch to Input) and sample the line 9us later
        Onewire_Pin_Init(GPIO_MODE_INPUT);
        delay_us_dwt(9);

        // Step 3: Read the bit state
        if (HAL_GPIO_ReadPin(ONEWIRE_GPIO_Port, ONEWIRE_Pin) == GPIO_PIN_SET) {
            read_byte |= (1 << i);
        }

        // Step 4: Wait for the rest of the time slot
        delay_us_dwt(55); // Remaining time for 70µs slot (70 - 6 - 9 = 55)
    }

    return read_byte;
}

// =================================================================================
// 4. DS18B20 Application Function
// =================================================================================

// Read temperature from DS18B20 sensor
float DS18b20_temp(void) {
    uint8_t temp_lsb, temp_msb;
    int16_t raw_temp;

    // 1. Start Conversion
    if (!onewire_reset()) return -999.0f; // Check for presence
    onewire_Write(0xCC);  // Skip ROM command
    onewire_Write(0x44);  // Start temperature conversion
    HAL_Delay(750);       // Wait for conversion (typical 750ms for 12-bit resolution)

    // 2. Read Scratchpad
    if (!onewire_reset()) return -999.0f; // Check for presence again
    onewire_Write(0xCC);  // Skip ROM command
    onewire_Write(0xBE);  // Read scratchpad command

    temp_lsb = onewire_Read();
    temp_msb = onewire_Read();

    // 3. Process data
    raw_temp = (temp_msb << 8) | temp_lsb;
    return (float)raw_temp / 16.0;
}
