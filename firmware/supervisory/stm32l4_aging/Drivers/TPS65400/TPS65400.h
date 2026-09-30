/******************************************************************************
 * @file    TPS65400.h
 * @brief   Interface pública do driver PMBus para o regulador TPS65400.
 *
 *          Define comandos PMBus, estruturas de dados, protótipos de função e
 *          constantes utilizadas pelo arquivo de implementação TPS65400.c.
 *
 * @author  Vitorino
 * @date    27 jun 2025
 *
 * @note    Este driver foi escrito para a família STM32L4 utilizando a HAL‑I2C.
 *          As escalas de tensão, corrente e temperatura seguem os valores
 *          especificados no datasheet do TPS65400.
 *****************************************************************************/

#ifndef TPS65400_TPS65400_H_
#define TPS65400_TPS65400_H_

#include "stm32l4xx_hal.h"       /* Dependência da HAL_I2C */
#include "MYMGM1R.h"

/* --------------------------------------------------------------------------
 * Constantes e macros
 * --------------------------------------------------------------------------*/

/** @brief Endereço I²C de 7 bits (já deslocado) definido por Rtrim = 4,99 kΩ. */
#define TPS65400_Addr     (0x69U << 1)

/** @brief Time‑out padrão (ms) para todas as transações I²C. */
#define TIMEOUT          1000U

/* --------------------------------------------------------------------------
 * Códigos de comando PMBus
 * --------------------------------------------------------------------------*/
/**
 * @enum pmbus_command_t
 * @brief Subconjunto de comandos PMBus suportado pelo TPS65400.
 */
typedef enum
{
    /* --- Básicos e de status ------------------------------------------------ */
    PMBUS_REG_PAGE               = 0x00, /**< Seleção de página                     */
    PMBUS_REG_OPERATION          = 0x01, /**< Liga / desliga (vide OPERATION)       */
    PMBUS_REG_CLEAR_FAULTS       = 0x03, /**< Limpa todos os flags de falha         */
    PMBUS_REG_WRITE_PROTECT      = 0x10, /**< Proteção de escrita                   */
    PMBUS_REG_STORE_DEFAULT_ALL  = 0x11, /**< Armazena configurações como padrão    */
    PMBUS_REG_CAPABILITY         = 0x19, /**< Capacidades do dispositivo            */

    PMBUS_REG_STATUS_BYTE        = 0x78, /**< Byte de status geral                  */
    PMBUS_REG_STATUS_WORD        = 0x79, /**< Word de status geral                  */
    PMBUS_REG_STATUS_VOUT        = 0x7A, /**< Status específico de VOUT             */
    PMBUS_REG_STATUS_MFR_SPEC    = 0x80, /**< Status específico do fabricante       */

    PMBUS_REG_PMBUS_REVISION     = 0x98, /**< Revisão do padrão PMBus               */
    PMBUS_REG_IC_DEVICE_ID       = 0xAD, /**< Identificação do CI                   */
    PMBUS_REG_IC_DEVICE_REV      = 0xAE, /**< Revisão do CI                         */

    /* --- Área de usuário / pinos ------------------------------------------- */
    PMBUS_REG_USER_DATA_BYTE_00  = 0xD0, /**< Dado de usuário 0                     */
    PMBUS_REG_USER_DATA_BYTE_01  = 0xD1, /**< Dado de usuário 1                     */
    PMBUS_REG_PIN_CONFIG_00      = 0xD2, /**< Configuração de pinos – parte 0       */
    PMBUS_REG_PIN_CONFIG_01      = 0xD3, /**< Configuração de pinos – parte 1       */

    /* --- Sequenciamento e temporização ------------------------------------- */
    PMBUS_REG_SEQUENCE_CONFIG    = 0xD4, /**< Configura sequenciamento              */
    PMBUS_REG_SEQUENCE_ORDER     = 0xD5, /**< Ordem de sequenciamento               */
    PMBUS_REG_IOUT_MODE          = 0xD6, /**< Formato do registrador IOUT           */
    PMBUS_REG_FREQUENCY_PHASE    = 0xD7, /**< Freq. de comutação / fase             */
    PMBUS_REG_VREF_COMMAND       = 0xD8, /**< Comando de VREF interno               */
    PMBUS_REG_IOUT_MAX           = 0xD9, /**< Corrente máxima                       */
    PMBUS_REG_USER_RAM_00        = 0xDA, /**< RAM de usuário                        */
    PMBUS_REG_SOFT_RESET         = 0xDB, /**< Soft-reset (send-byte)                */
    PMBUS_REG_RESET_DELAY        = 0xDC, /**< Atraso após reset                     */
    PMBUS_REG_TON_TOFF_DELAY     = 0xDD, /**< Delays de ligar / desligar            */
    PMBUS_REG_TON_TRANS_RATE     = 0xDE, /**< Taxa de subida de tensão (Vout-up)    */
    PMBUS_REG_VREF_TRANS_RATE    = 0xDF, /**< Taxa de transição de VREF             */

    /* 0xE0 – 0xEF: Reservados pelo fabricante                                */

    /* --- Ajustes de controle e calibração ---------------------------------- */
    PMBUS_REG_SLOPE_COMPENSATION = 0xF0, /**< Compensação de rampa                  */
    PMBUS_REG_ISENSE_GAIN        = 0xF1, /**< Ganho de detecção de corrente         */

    /* --- Identificação ------------------------------------------------------ */
    PMBUS_REG_DEVICE_CODE        = 0xFC  /**< Código do dispositivo (somente leitura) */
} PMBus_TPS65400_command_t;
/* --------------------------------------------------------------------------
 * Status de retorno
 * --------------------------------------------------------------------------*/
/**
 * @enum PMBus_StatusTypeDef
 * @brief Resultado de uma operação de comunicação PMBus.
 */

/* --------------------------------------------------------------------------
 * Estruturas de dados
 * --------------------------------------------------------------------------*/
/**
 * @struct TPS65400_Struct
 * @brief Estrutura de contexto mantida pelo aplicativo.
 *
 * Contém ponteiro para o handle I²C, buffers de TX/RX e metadados de comando.
 */
typedef struct {
    I2C_HandleTypeDef*            i2c_handler;                  /**< Handle HAL‑I2C. */
    PMBus_TPS65400_command_t      cmd;                          /**< Último comando.  */
    PMBus_StatusTypeDef           status;                       /**< Status da última transação. */
    uint8_t                       pdata_Send[0xD3];             /**< Buffer de escrita (máx. 211 B). */
    uint8_t                       pdata_Receive[0xD3];          /**< Buffer de leitura (idem).      */
    uint8_t                       qty;                          /**< Nº de bytes a TX/RX.           */
} TPS65400_Struct;

/* --------------------------------------------------------------------------
 * Protótipos de função pública
 * --------------------------------------------------------------------------*/
/**
 * @brief   Inicializa o driver e configura parâmetros padrão.
 * @param   i2c_handler Handle HAL‑I2C previamente configurado.
 * @param   ctx         Ponteiro para estrutura de contexto a ser preenchida.
 * @return  PMBus_OK em sucesso; código de erro caso contrário.
 */
PMBus_StatusTypeDef TPS65400_Init(I2C_HandleTypeDef *i2c_handler,
                                 TPS65400_Struct *ctx);

/**
 * @brief   Lê a tensão de saída (Vcore) em volts.
 * @param   ctx Estrutura de contexto.
 * @return  Vcore em volts (float).
 */
float TPS65400_Read_Vcore(TPS65400_Struct *ctx);

/**
 * @brief Lê a tensão de entrada (Vin) em volts.
 * @param ctx Estrutura de contexto.
 * @return Vin em volts (float).
 */
float TPS65400_Read_Vin(TPS65400_Struct *ctx);

/**
 * @brief Lê a corrente de saída (Iout) em amperes.
 * @param ctx Estrutura de contexto.
 * @return Corrente de saída em amperes (float).
 */
float TPS65400_Read_Iout(TPS65400_Struct *ctx);

/**
 * @brief Lê a temperatura interna do módulo em graus Celsius.
 * @param ctx Estrutura de contexto.
 * @return Temperatura em °C (float).
 */
float TPS65400_Read_Temperature(TPS65400_Struct *ctx);

/**
 * @brief   Configura nova tensão Vcore e margens ±10 %.
 * @param   ctx     Estrutura de contexto.
 * @param   Vout_f  Tensão desejada em volts.
 * @return  PMBus_OK em sucesso; código de erro caso contrário.
 */
PMBus_StatusTypeDef TPS65400_Set_Vcore(TPS65400_Struct *ctx, float Vout_f);

/**
 * @brief   Desliga a saída do regulador.
 * @param   ctx Estrutura de contexto.
 * @return  PMBus_OK em sucesso; código de erro caso contrário.
 */
PMBus_StatusTypeDef TPS65400_OUTPUT_Disable(TPS65400_Struct *ctx);

/**
 * @brief   Liga a saída do regulador.
 * @param   ctx Estrutura de contexto.
 * @return  PMBus_OK em sucesso; código de erro caso contrário.
 */
PMBus_StatusTypeDef TPS65400_OUTPUT_Enable(TPS65400_Struct *ctx);

#endif /* TPS65400_TPS65400_H_ */
