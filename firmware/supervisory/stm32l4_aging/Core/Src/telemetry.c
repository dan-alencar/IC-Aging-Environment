/******************************************************************************
 * @file    telemetry.c
 * @brief   Implementação do módulo de telemetria
 *
 *          Formato do pacote:
 *          $TEL,Vcore,X.XXX,Vin,X.XXX,Iout,X.XXX,ExtT,XX.X,McuT,XX.X*CS\r\n
 *
 *          Onde CS é checksum XOR de todos os bytes entre $ e *
 *
 * @author  Auto-generated
 * @date    2025
 *****************************************************************************/

#include "telemetry.h"
#include <stdio.h>
#include <string.h>

/* --------------------------------------------------------------------------
 * Constantes internas
 * --------------------------------------------------------------------------*/

/** @brief Endereços de calibração de temperatura do STM32L4 */
#define TS_CAL1_ADDR  ((uint16_t*)0x1FFF75A8)
#define TS_CAL2_ADDR  ((uint16_t*)0x1FFF75CA)

/* --------------------------------------------------------------------------
 * Funções auxiliares
 * --------------------------------------------------------------------------*/

/**
 * @brief Lê temperatura interna do MCU via ADC
 */
static float Read_MCU_Temperature(ADC_HandleTypeDef *hadc)
{
    if (hadc == NULL) return 0.0f;
    
    uint16_t TS_CAL1 = *TS_CAL1_ADDR;
    uint16_t TS_CAL2 = *TS_CAL2_ADDR;
    
    HAL_ADC_Start(hadc);
    HAL_ADC_PollForConversion(hadc, 100);
    uint32_t raw = HAL_ADC_GetValue(hadc);
    HAL_ADC_Stop(hadc);
    
    // Ajuste de escala (fator 1.1 conforme código original)
    raw = (float)raw * 1.1f;
    
    // Conversão usando calibração de fábrica
    float temp = ((float)raw - (float)TS_CAL1) * 80.0f / 
                 ((float)TS_CAL2 - (float)TS_CAL1) + 30.0f;
    
    return temp;
}

/* --------------------------------------------------------------------------
 * Implementação das funções públicas
 * --------------------------------------------------------------------------*/

void Telemetry_Init(Telemetry_Context *ctx,
                   UART_HandleTypeDef *uart,
                   MYMGM1R_Struct *power_ctx,
                   ADC_HandleTypeDef *adc)
{
    if (ctx == NULL) return;
    
    ctx->uart = uart;
    ctx->power_ctx = power_ctx;
    ctx->adc = adc;
    ctx->enabled = 0;
    ctx->last_send = 0;
    ctx->interval_ms = TELEMETRY_INTERVAL_MS;
    
    // Zera dados
    memset(&ctx->latest, 0, sizeof(Telemetry_Data));
    memset(ctx->buffer, 0, TELEMETRY_BUFFER_SIZE);
}

void Telemetry_Enable(Telemetry_Context *ctx)
{
    if (ctx == NULL) return;
    ctx->enabled = 1;
    ctx->last_send = HAL_GetTick();
}

void Telemetry_Disable(Telemetry_Context *ctx)
{
    if (ctx == NULL) return;
    ctx->enabled = 0;
}

void Telemetry_SetInterval(Telemetry_Context *ctx, uint16_t interval_ms)
{
    if (ctx == NULL) return;
    ctx->interval_ms = (interval_ms < 100) ? 100 : interval_ms;
}

uint8_t Telemetry_CalcChecksum(const uint8_t *data, int len)
{
    uint8_t cs = 0;
    for (int i = 0; i < len; i++) {
        cs ^= data[i];
    }
    return cs;
}

int Telemetry_Update(Telemetry_Context *ctx)
{
    if (ctx == NULL || !ctx->enabled) return 0;
    
    uint32_t now = HAL_GetTick();
    
    // Verifica se é hora de enviar
    if ((now - ctx->last_send) < ctx->interval_ms) {
        return 0;
    }
    
    ctx->last_send = now;
    
    // Coleta dados
    if (ctx->power_ctx != NULL) {
        ctx->latest.vcore = MYMGM1R_Read_Vcore(ctx->power_ctx);
        ctx->latest.vin = MYMGM1R_Read_Vin(ctx->power_ctx);
        ctx->latest.iout = MYMGM1R_Read_Iout(ctx->power_ctx);
        ctx->latest.ext_temp = MYMGM1R_Read_Temperature(ctx->power_ctx);
    }
    
    ctx->latest.mcu_temp = Read_MCU_Temperature(ctx->adc);
    ctx->latest.timestamp = now;
    
    // Formata pacote (sem o $ inicial e * final para calcular checksum)
    char payload[100];
    int len = snprintf(payload, sizeof(payload),
        "TEL,Vc,%.3f,Vi,%.3f,Io,%.3f,Et,%.1f,Mt,%.1f",
        ctx->latest.vcore,
        ctx->latest.vin,
        ctx->latest.iout,
        ctx->latest.ext_temp,
        ctx->latest.mcu_temp
    );
    
    // Calcula checksum
    uint8_t cs = Telemetry_CalcChecksum((uint8_t*)payload, len);
    
    // Formata pacote completo com $ e *CS\r\n
    len = snprintf((char*)ctx->buffer, TELEMETRY_BUFFER_SIZE,
        "$%s*%02X\r\n", payload, cs);
    
    // Envia via UART
    if (ctx->uart != NULL) {
        HAL_UART_Transmit(ctx->uart, ctx->buffer, len, 100);
    }
    
    return 1;
}

void Telemetry_SendNow(Telemetry_Context *ctx)
{
    if (ctx == NULL) return;
    
    // Força próximo envio
    ctx->last_send = 0;
    Telemetry_Update(ctx);
}

Telemetry_Data* Telemetry_GetLatest(Telemetry_Context *ctx)
{
    if (ctx == NULL) return NULL;
    return &ctx->latest;
}
