/******************************************************************************
 * @file    MYMGM1R.h
 * @brief   Interface pública do driver PMBus para o regulador MYMGM1R.
 *
 *          Define comandos PMBus, estruturas de dados, protótipos de função e
 *          constantes utilizadas pelo arquivo de implementação MYMGM1R.c.
 *
 * @author  Vitorino
 * @date    27 jun 2025
 *
 * @note    Este driver foi escrito para a família STM32L4 utilizando a HAL‑I2C.
 *          As escalas de tensão, corrente e temperatura seguem os valores
 *          especificados no datasheet do MYMGM1R.
 *****************************************************************************/

#ifndef MYMGM1R_MYMGM1R_H_
#define MYMGM1R_MYMGM1R_H_

#include "stm32l4xx_hal.h"       /* Dependência da HAL_I2C */

/* --------------------------------------------------------------------------
 * Constantes e macros
 * --------------------------------------------------------------------------*/

/** @brief Endereço I²C de 7 bits (já deslocado) definido por Rtrim = 4,99 kΩ. */
#define MYMGM1R_Addr     (0x30U << 1)

/** @brief Time‑out padrão (ms) para todas as transações I²C. */
#define TIMEOUT          1000U

/* --------------------------------------------------------------------------
 * Códigos de comando PMBus
 * --------------------------------------------------------------------------*/
/**
 * @enum pmbus_command_t
 * @brief Subconjunto de comandos PMBus suportado pelo MYMGM1R.
 */
typedef enum {
    PMBUS_CMD_OPERATION           = 0x01, /**< Liga/desliga saída.              */
    PMBUS_CMD_ON_OFF_CONFIG       = 0x02, /**< Configura pinos de enable.       */
    PMBUS_CMD_CLEAR_FAULTS        = 0x03, /**< Limpa flags de falha.            */
    PMBUS_CMD_WRITE_PROTECT       = 0x10,
    PMBUS_CMD_CAPABILITY          = 0x19,
    PMBUS_CMD_VOUT_MODE           = 0x20,
    PMBUS_CMD_VOUT_COMMAND        = 0x21, /**< Programação de VOUT.             */
    PMBUS_CMD_VOUT_MARGIN_HIGH    = 0x25, /**< Margem alta (+%).                */
    PMBUS_CMD_VOUT_MARGIN_LOW     = 0x26, /**< Margem baixa (−%).               */
    PMBUS_CMD_VOUT_SCALE_LOOP     = 0x29,
    PMBUS_CMD_VIN_ON              = 0x35,
    PMBUS_CMD_VIN_OFF             = 0x36,
    PMBUS_CMD_IOUT_OC_WARN_LIMIT  = 0x4A,
    PMBUS_CMD_OT_WARN_LIMIT       = 0x51,
    PMBUS_CMD_VIN_OV_WARN_LIMIT   = 0x57,
    PMBUS_CMD_VIN_UV_WARN_LIMIT   = 0x58,
    PMBUS_CMD_TON_DELAY           = 0x60,
    PMBUS_CMD_TON_RISE            = 0x61,
    PMBUS_CMD_STATUS_BYTE         = 0x78,
    PMBUS_CMD_STATUS_WORD         = 0x79,
    PMBUS_CMD_STATUS_VOUT         = 0x7A,
    PMBUS_CMD_STATUS_IOUT         = 0x7B,
    PMBUS_CMD_STATUS_INPUT        = 0x7C,
    PMBUS_CMD_STATUS_TEMPERATURE  = 0x7D,
    PMBUS_CMD_STATUS_CML          = 0x7E,
    PMBUS_CMD_READ_VIN            = 0x88,
    PMBUS_CMD_READ_VOUT           = 0x8B,
    PMBUS_CMD_READ_IOUT           = 0x8C,
    PMBUS_CMD_READ_TEMPERATURE_1  = 0x8D,
    PMBUS_CMD_PMBUS_REVISION      = 0x98,
    PMBUS_CMD_MFR_CTRL_VOUT       = 0xD1,
    PMBUS_CMD_MFR_ADDR_PMBUS      = 0xD3
} pmbus_command_t;

/* --------------------------------------------------------------------------
 * Status de retorno
 * --------------------------------------------------------------------------*/
/**
 * @enum PMBus_StatusTypeDef
 * @brief Resultado de uma operação de comunicação PMBus.
 */
typedef enum
{
    PMBus_OK       = 0x00, /**< Operação concluída com sucesso.           */
    PMBus_ERROR    = 0x01, /**< Erro genérico (NACK, parâmetros inválidos)*/
    PMBus_BUSY     = 0x02, /**< Barramento/ou dispositivo ocupado.        */
    PMBus_TIMEOUT  = 0x03  /**< Time‑out expirado.                        */
} PMBus_StatusTypeDef;

/* --------------------------------------------------------------------------
 * Estruturas de dados
 * --------------------------------------------------------------------------*/
/**
 * @struct MYMGM1R_Struct
 * @brief Estrutura de contexto mantida pelo aplicativo.
 *
 * Contém ponteiro para o handle I²C, buffers de TX/RX e metadados de comando.
 */
typedef struct {
    I2C_HandleTypeDef*   i2c_handler;                  /**< Handle HAL‑I2C. */
    pmbus_command_t      cmd;                          /**< Último comando.  */
    PMBus_StatusTypeDef  status;                       /**< Status da última transação. */
    uint8_t              pdata_Send[0xD3];             /**< Buffer de escrita (máx. 211 B). */
    uint8_t              pdata_Receive[0xD3];          /**< Buffer de leitura (idem).      */
    uint8_t              qty;                          /**< Nº de bytes a TX/RX.           */
} MYMGM1R_Struct;

/* --------------------------------------------------------------------------
 * Protótipos de função pública
 * --------------------------------------------------------------------------*/
/**
 * @brief   Inicializa o driver e configura parâmetros padrão.
 * @param   i2c_handler Handle HAL‑I2C previamente configurado.
 * @param   ctx         Ponteiro para estrutura de contexto a ser preenchida.
 * @return  PMBus_OK em sucesso; código de erro caso contrário.
 */
PMBus_StatusTypeDef MYMGM1R_Init(I2C_HandleTypeDef *i2c_handler,
                                 MYMGM1R_Struct *ctx);

/**
 * @brief   Lê a tensão de saída (Vcore) em volts.
 * @param   ctx Estrutura de contexto.
 * @return  Vcore em volts (float).
 */
float MYMGM1R_Read_Vcore(MYMGM1R_Struct *ctx);

/**
 * @brief Lê a tensão de entrada (Vin) em volts.
 * @param ctx Estrutura de contexto.
 * @return Vin em volts (float).
 */
float MYMGM1R_Read_Vin(MYMGM1R_Struct *ctx);

/**
 * @brief Lê a corrente de saída (Iout) em amperes.
 * @param ctx Estrutura de contexto.
 * @return Corrente de saída em amperes (float).
 */
float MYMGM1R_Read_Iout(MYMGM1R_Struct *ctx);

/**
 * @brief Lê a temperatura interna do módulo em graus Celsius.
 * @param ctx Estrutura de contexto.
 * @return Temperatura em °C (float).
 */
float MYMGM1R_Read_Temperature(MYMGM1R_Struct *ctx);

/**
 * @brief   Configura nova tensão Vcore e margens ±10 %.
 * @param   ctx     Estrutura de contexto.
 * @param   Vout_f  Tensão desejada em volts.
 * @return  PMBus_OK em sucesso; código de erro caso contrário.
 */
PMBus_StatusTypeDef MYMGM1R_Set_Vcore(MYMGM1R_Struct *ctx, float Vout_f);

/**
 * @brief   Desliga a saída do regulador.
 * @param   ctx Estrutura de contexto.
 * @return  PMBus_OK em sucesso; código de erro caso contrário.
 */
PMBus_StatusTypeDef MYMGM1R_OUTPUT_Disable(MYMGM1R_Struct *ctx);

/**
 * @brief   Liga a saída do regulador.
 * @param   ctx Estrutura de contexto.
 * @return  PMBus_OK em sucesso; código de erro caso contrário.
 */
PMBus_StatusTypeDef MYMGM1R_OUTPUT_Enable(MYMGM1R_Struct *ctx);

#endif /* MYMGM1R_MYMGM1R_H_ */
