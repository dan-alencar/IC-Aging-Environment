/******************************************************************************
 * @file    telemetry.h
 * @brief   Módulo de telemetria para envio periódico de dados ao PC via FPGA
 *
 *          Envia periodicamente: Vcore, Vin, Iout, Temperatura externa
 *          Formato: $TEL,Vcore,X.XXX,Vin,X.XXX,Iout,X.XXX,ExtT,XX.X*CS\r\n
 *
 * @author  Auto-generated
 * @date    2025
 *****************************************************************************/

#ifndef TELEMETRY_H_
#define TELEMETRY_H_

#include "stm32l4xx_hal.h"
#include "MYMGM1R.h"

/* --------------------------------------------------------------------------
 * Configuração
 * --------------------------------------------------------------------------*/

/** @brief Intervalo de envio de telemetria em ms */
#define TELEMETRY_INTERVAL_MS    500

/** @brief Tamanho máximo do buffer de telemetria */
#define TELEMETRY_BUFFER_SIZE    128

/* --------------------------------------------------------------------------
 * Estrutura de dados de telemetria
 * --------------------------------------------------------------------------*/

/**
 * @struct Telemetry_Data
 * @brief Estrutura contendo todos os dados de telemetria
 */
typedef struct {
    float vcore;        /**< Tensão de saída para FPGA (V) */
    float vin;          /**< Tensão de entrada da placa (V) */
    float iout;         /**< Corrente de saída (A) */
    float ext_temp;     /**< Temperatura externa via termistor (°C) */
    float mcu_temp;     /**< Temperatura do MCU (°C) */
    uint32_t timestamp; /**< Timestamp em ms */
} Telemetry_Data;

/**
 * @struct Telemetry_Context
 * @brief Contexto do módulo de telemetria
 */
typedef struct {
    UART_HandleTypeDef *uart;       /**< Handle UART para transmissão */
    MYMGM1R_Struct *power_ctx;      /**< Contexto do módulo de potência */
    ADC_HandleTypeDef *adc;         /**< Handle ADC para temperatura MCU */
    uint8_t buffer[TELEMETRY_BUFFER_SIZE]; /**< Buffer de transmissão */
    uint8_t enabled;                /**< Flag de habilitação */
    uint32_t last_send;             /**< Último timestamp de envio */
    uint16_t interval_ms;           /**< Intervalo entre envios */
    Telemetry_Data latest;          /**< Últimos dados coletados */
} Telemetry_Context;

/* --------------------------------------------------------------------------
 * Protótipos de função pública
 * --------------------------------------------------------------------------*/

/**
 * @brief   Inicializa o módulo de telemetria
 * @param   ctx         Ponteiro para contexto de telemetria
 * @param   uart        Handle UART para transmissão
 * @param   power_ctx   Contexto do módulo MYMGM1R
 * @param   adc         Handle ADC para temperatura do MCU
 */
void Telemetry_Init(Telemetry_Context *ctx,
                   UART_HandleTypeDef *uart,
                   MYMGM1R_Struct *power_ctx,
                   ADC_HandleTypeDef *adc);

/**
 * @brief   Habilita o envio de telemetria
 * @param   ctx Contexto de telemetria
 */
void Telemetry_Enable(Telemetry_Context *ctx);

/**
 * @brief   Desabilita o envio de telemetria
 * @param   ctx Contexto de telemetria
 */
void Telemetry_Disable(Telemetry_Context *ctx);

/**
 * @brief   Define o intervalo de envio
 * @param   ctx         Contexto de telemetria
 * @param   interval_ms Intervalo em milissegundos
 */
void Telemetry_SetInterval(Telemetry_Context *ctx, uint16_t interval_ms);

/**
 * @brief   Coleta e envia dados de telemetria (chamar periodicamente)
 * @param   ctx Contexto de telemetria
 * @return  1 se enviou dados, 0 caso contrário
 */
int Telemetry_Update(Telemetry_Context *ctx);

/**
 * @brief   Força envio imediato de telemetria
 * @param   ctx Contexto de telemetria
 */
void Telemetry_SendNow(Telemetry_Context *ctx);

/**
 * @brief   Retorna os últimos dados coletados
 * @param   ctx Contexto de telemetria
 * @return  Ponteiro para estrutura com dados
 */
Telemetry_Data* Telemetry_GetLatest(Telemetry_Context *ctx);

/**
 * @brief   Calcula checksum XOR para o pacote
 * @param   data    Dados para calcular checksum
 * @param   len     Tamanho dos dados
 * @return  Checksum XOR
 */
uint8_t Telemetry_CalcChecksum(const uint8_t *data, int len);

#endif /* TELEMETRY_H_ */
