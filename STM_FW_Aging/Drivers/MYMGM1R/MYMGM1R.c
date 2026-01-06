/******************************************************************************
 * @file    MYMGM1R.c
 * @brief   Driver PMBus para o módulo regulador MYMGM1R.
 *
 *          Implementa rotinas de inicialização, leitura e configuração do
 *          regulador via PMBus utilizando a HAL‑I2C da ST (linha STM32L4).
 *
 * @author  Vitorino
 * @date    27 jun 2025
 *
 * @note    Este código supõe que o endereço I²C do MYMGM1R está definido como
 *          MYMGM1R_Addr no cabeçalho MYMGM1R.h.  Timeouts fixos de 1000 ms
 *          são utilizados em todas as transações I²C.  Os fatores de escala
 *          para tensão, corrente e temperatura seguem o datasheet do dispositivo.
 *****************************************************************************/


#include "stm32l4xx_hal.h"
#include "MYMGM1R.h"


/***************************************************************************//**
 * @brief Envia dados ao MYMGM1R via PMBus (escrita em registrador).
 *
 * @param[in,out] ctx  Ponteiro para a estrutura de contexto do driver.
 *
 * @return PMBus_OK em sucesso; código de erro PMBus_StatusTypeDef caso contrário.
 ******************************************************************************/
PMBus_StatusTypeDef MYMGM1R_Send(MYMGM1R_Struct *ctx)
{
    ctx->status = HAL_I2C_Mem_Write(ctx->i2c_handler, MYMGM1R_Addr,
                                    ctx->cmd, 1,
                                    ctx->pdata_Send, ctx->qty, TIMEOUT);

    return ctx->status;
}


/***************************************************************************//**
 * @brief Envia apenas o comando (sem dados) ao MYMGM1R.
 *
 * @param[in,out] ctx  Ponteiro para a estrutura de contexto do driver.
 *
 * @return PMBus_OK em sucesso; código de erro PMBus_StatusTypeDef caso contrário.
 ******************************************************************************/
PMBus_StatusTypeDef MYMGM1R_Send_zero(MYMGM1R_Struct *ctx)
{
    ctx->status = HAL_I2C_Master_Transmit(ctx->i2c_handler, MYMGM1R_Addr,
                                          &ctx->cmd, 1, TIMEOUT);

    return ctx->status;
}


/***************************************************************************//**
 * @brief Lê dados do MYMGM1R via PMBus (leitura de registrador).
 *
 * @param[in,out] ctx  Ponteiro para a estrutura de contexto do driver.
 *
 * @return PMBus_OK em sucesso; código de erro PMBus_StatusTypeDef caso contrário.
 ******************************************************************************/
PMBus_StatusTypeDef MYMGM1R_Receive(MYMGM1R_Struct *ctx)
{
    ctx->status = HAL_I2C_Mem_Read(ctx->i2c_handler, MYMGM1R_Addr,
                                   ctx->cmd, 1,
                                   ctx->pdata_Receive, ctx->qty, TIMEOUT);

    return ctx->status;
}


/***************************************************************************//**
 * @brief Inicializa o MYMGM1R e ajusta parâmetros padrão (1,00 V @ ±10 %).
 *
 * @param[in]  i2c_handler  Handle HAL_I2C já configurado.
 * @param[out] ctx          Estrutura de contexto a ser inicializada.
 *
 * @return PMBus_OK em sucesso; PMBus_ERROR ou outro status em falha.
 *
 * @details
 * - Verifica a revisão PMBus.
 * - Configura VOUT_COMMAND, VOUT_SCALE_LOOP e margens alta/baixa.
 * - Limpa falhas pendentes.
 ******************************************************************************/
PMBus_StatusTypeDef MYMGM1R_Init(I2C_HandleTypeDef *i2c_handler,
                                 MYMGM1R_Struct *ctx)
{
    ctx->i2c_handler = i2c_handler;
    ctx->cmd         = PMBUS_CMD_PMBUS_REVISION;
    ctx->qty         = 1;

    MYMGM1R_Receive(ctx);

    if (ctx->pdata_Receive[0] != 0x33 || ctx->status != PMBus_OK)
        return PMBus_ERROR;

    MYMGM1R_OUTPUT_Disable(ctx);

    /* ---------- Configuração de tensão e escalas ---------- */
    ctx->cmd           = PMBUS_CMD_VOUT_COMMAND;
    ctx->pdata_Send[0] = 0xA9;          /* 0.85 V */
    ctx->pdata_Send[1] = 0x01;
    ctx->qty           = 2;
    if (MYMGM1R_Send(ctx) != PMBus_OK) return ctx->status;

    ctx->cmd           = PMBUS_CMD_VOUT_SCALE_LOOP;
    ctx->pdata_Send[0] = 0xF4;          /* 0,5 (para Rtrim 10 k) */
    ctx->pdata_Send[1] = 0x01;
    ctx->qty           = 2;
    if (MYMGM1R_Send(ctx) != PMBus_OK) return ctx->status;

    ctx->cmd           = PMBUS_CMD_VOUT_MARGIN_HIGH;
    ctx->pdata_Send[0] = 0xD3;          /* +10 % → 1,10 V */
    ctx->pdata_Send[1] = 0x01;
    ctx->qty           = 2;
    if (MYMGM1R_Send(ctx) != PMBus_OK) return ctx->status;

    ctx->cmd           = PMBUS_CMD_VOUT_MARGIN_LOW;
    ctx->pdata_Send[0] = 0x7E;          /* −10 % → 0,90 V */
    ctx->pdata_Send[1] = 0x01;
    ctx->qty           = 2;
    if (MYMGM1R_Send(ctx) != PMBus_OK) return ctx->status;

    /* TODO: Validar parâmetros críticos para evitar sobre‑tensão na FPGA */

    /* Limpa quaisquer falhas pendentes */
    ctx->cmd = PMBUS_CMD_CLEAR_FAULTS;
    if (MYMGM1R_Send_zero(ctx) != PMBus_OK) return ctx->status;

    HAL_Delay(300);
    MYMGM1R_OUTPUT_Enable(ctx);

    return ctx->status;
}


/***************************************************************************//**
 * @brief Lê a tensão de saída (Vcore) em volts.
 *
 * @param[in,out] ctx  Estrutura de contexto.
 *
 * @return Tensão Vcore em volts.
 ******************************************************************************/
float MYMGM1R_Read_Vcore(MYMGM1R_Struct *ctx)
{
    ctx->cmd = PMBUS_CMD_READ_VOUT;
    ctx->qty = 2;

    MYMGM1R_Receive(ctx);

    uint16_t Vcore = (ctx->pdata_Receive[1] << 8) | ctx->pdata_Receive[0];

    return (Vcore * 0.00125f);
}


/***************************************************************************//**
 * @brief Lê a tensão de entrada (Vin) em volts.
 *
 * @param[in,out] ctx  Estrutura de contexto.
 *
 * @return Tensão Vin em volts.
 ******************************************************************************/
float MYMGM1R_Read_Vin(MYMGM1R_Struct *ctx)
{
    ctx->cmd = PMBUS_CMD_READ_VIN;
    ctx->qty = 2;

    MYMGM1R_Receive(ctx);

    uint16_t Vin = (ctx->pdata_Receive[1] << 8) | ctx->pdata_Receive[0];

    return (Vin * 0.025f);
}


/***************************************************************************//**
 * @brief Lê a corrente de saída (Iout) em amperes.
 *
 * @param[in,out] ctx  Estrutura de contexto.
 *
 * @return Corrente de saída em amperes.
 ******************************************************************************/
float MYMGM1R_Read_Iout(MYMGM1R_Struct *ctx)
{
    ctx->cmd = PMBUS_CMD_READ_IOUT;
    ctx->qty = 2;

    MYMGM1R_Receive(ctx);

    uint16_t Iout = (ctx->pdata_Receive[1] << 8) | ctx->pdata_Receive[0];

    return (Iout * 0.0625f);
}


/***************************************************************************//**
 * @brief Lê a temperatura interna do módulo em graus Celsius.
 *
 * @param[in,out] ctx  Estrutura de contexto.
 *
 * @return Temperatura em °C.
 ******************************************************************************/
float MYMGM1R_Read_Temperature(MYMGM1R_Struct *ctx)
{
    ctx->cmd = PMBUS_CMD_READ_TEMPERATURE_1;
    ctx->qty = 2;

    MYMGM1R_Receive(ctx);

    uint8_t lsb = ctx->pdata_Receive[0];
    uint8_t msb = ctx->pdata_Receive[1];

    uint16_t word  = ((uint16_t)msb << 8) | lsb;
    uint16_t raw10 = word & 0x03FF;           /* bits 9‑0 */

    /* Extensão de sinal se bit 9 = 1 (temperatura negativa) */
    if (raw10 & 0x0200) raw10 |= 0xFC00;

    return (float)((int16_t)raw10);           /* 1 LSB = 1 °C */
}


/***************************************************************************//**
 * @brief Ajusta a tensão de saída (Vcore) e margens de ±10 %.
 *
 * @param[in,out] ctx     Estrutura de contexto.
 * @param[in]     Vout_f  Nova tensão desejada em volts.
 *
 * @return PMBus_OK em sucesso; código de erro PMBus_StatusTypeDef caso contrário.
 ******************************************************************************/
PMBus_StatusTypeDef MYMGM1R_Set_Vcore(MYMGM1R_Struct *ctx, float Vout_f)
{
    uint16_t Vout_i = (uint16_t)((Vout_f * 1000.0f) / 2.0f);

    ctx->cmd           = PMBUS_CMD_VOUT_COMMAND;
    ctx->pdata_Send[0] = (uint8_t)Vout_i;
    ctx->pdata_Send[1] = (uint8_t)(Vout_i >> 8);
    ctx->qty           = 2;
    if (MYMGM1R_Send(ctx) != PMBus_OK) return ctx->status;

    uint16_t Vout_max = (uint16_t)(Vout_i * 1.1f);   /* +10 % */
    ctx->cmd           = PMBUS_CMD_VOUT_MARGIN_HIGH;
    ctx->pdata_Send[0] = (uint8_t)Vout_max;
    ctx->pdata_Send[1] = (uint8_t)(Vout_max >> 8);
    ctx->qty           = 2;
    if (MYMGM1R_Send(ctx) != PMBus_OK) return ctx->status;

    uint16_t Vout_min = (uint16_t)(Vout_i * 0.9f);   /* −10 % */
    ctx->cmd           = PMBUS_CMD_VOUT_MARGIN_LOW;
    ctx->pdata_Send[0] = (uint8_t)Vout_min;
    ctx->pdata_Send[1] = (uint8_t)(Vout_min >> 8);
    ctx->qty           = 2;
    if (MYMGM1R_Send(ctx) != PMBus_OK) return ctx->status;

    return ctx->status;
}


/***************************************************************************//**
 * @brief Desabilita a saída do regulador.
 *
 * @param[in,out] ctx  Estrutura de contexto.
 *
 * @return PMBus_OK em sucesso; código de erro PMBus_StatusTypeDef caso contrário.
 ******************************************************************************/
PMBus_StatusTypeDef MYMGM1R_OUTPUT_Disable(MYMGM1R_Struct *ctx)
{
    ctx->cmd           = PMBUS_CMD_ON_OFF_CONFIG;
    ctx->pdata_Send[0] = 0x18;
    ctx->qty           = 1;

    MYMGM1R_Send(ctx);
    if (ctx->status != PMBus_OK) return ctx->status;

    ctx->cmd           = PMBUS_CMD_OPERATION;
    ctx->pdata_Send[0] = 0x00;
    ctx->qty           = 1;

    MYMGM1R_Send(ctx);

    return ctx->status;
}


/***************************************************************************//**
 * @brief Habilita a saída do regulador.
 *
 * @param[in,out] ctx  Estrutura de contexto.
 *
 * @return PMBus_OK em sucesso; código de erro PMBus_StatusTypeDef caso contrário.
 ******************************************************************************/
PMBus_StatusTypeDef MYMGM1R_OUTPUT_Enable(MYMGM1R_Struct *ctx)
{
    ctx->cmd           = PMBUS_CMD_OPERATION;
    ctx->pdata_Send[0] = 0x80;
    ctx->qty           = 1;

    MYMGM1R_Send(ctx);

    ctx->cmd           = PMBUS_CMD_ON_OFF_CONFIG;
    ctx->pdata_Send[0] = 0x16;
    ctx->qty           = 1;

    MYMGM1R_Send(ctx);

    return ctx->status;
}
