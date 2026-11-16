/*
 * telemetry.h
 *
 *  Created on: Mar 4, 2026
 *      Author: caio felipe
 */

#ifndef INC_TELEMETRY_H_
#define INC_TELEMETRY_H_

#include "MYMGM1R.h"

#define R_SHUNT                  0.1

#define OPAMP_GAIN               2

#define TELEMETRY_BUFFER_SIZE    192

#define TELEMETRY_INTERVAL_MS    10

#define INITIAL_MAX_CURRENT      2

/** @brief Endereço onde fica uma tensão de referência para calibração da temperatura a 30°C. */
#define TS_CAL1_ADDR ((volatile uint16_t*)0x1FFF75A8)

/** @brief Endereço onde fica uma tensão de referência para calibração da temperatura a 130°C. */
#define TS_CAL2_ADDR ((volatile uint16_t*)0x1FFF75CA)

typedef struct {
    float vcore;
    float vin;
    float iout;
    float i_sram;
    float power_cons;
    float ext_temp;
    float mcu_temp;
    uint8_t output_enabled;
    uint8_t latchup_state;
    uint32_t trip_count;
    uint32_t sequence;
    char last_reason[24];
} Telemetry_Data;

/**
 * @struct Telemetry_Context
 * @brief Contexto do módulo de telemetria
 */
typedef struct {
    UART_HandleTypeDef *uart;
    MYMGM1R_Struct *power_ctx;
    ADC_HandleTypeDef *adc;
    uint32_t last_send;
    Telemetry_Data latest;
    uint16_t interval_ms;
    uint8_t buffer[TELEMETRY_BUFFER_SIZE];
    uint8_t enabled;
    float max_current;
} Telemetry_Context;


void Telemetry_Init(Telemetry_Context *ctx, UART_HandleTypeDef *uart, MYMGM1R_Struct *power_ctx, ADC_HandleTypeDef *adc);

void Telemetry_Enable(Telemetry_Context *ctx);

void Telemetry_Disable(Telemetry_Context *ctx);

void send_telemetry(void *argument);

void get_measures(void *argument);

void Telemetry_Set_Output_State(Telemetry_Context *ctx, uint8_t enabled);
void Telemetry_Report_Latchup_Event(Telemetry_Context *ctx, const char *event_type, const char *reason);
void Telemetry_Send_Board_Status(Telemetry_Context *ctx);

/* Arquitetura B: manda uma linha já pronta ("$KIND,...*CS", sem CRLF) pelo ST-Link,
 * com o mesmo mutex das outras linhas. */
void Telemetry_Send_Line(const char *line, uint16_t length);

#endif /* INC_TELEMETRY_H_ */
