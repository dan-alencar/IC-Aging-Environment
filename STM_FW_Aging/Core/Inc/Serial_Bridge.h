/******************************************************************************
 * @file    Serial_Bridge.h
 * @brief   Interface para configuração da ponte de comunicação.
 *
 *          Define funções, estruturas e constantes utilizadas na ponte de
 *          comunicação entre FPGA, micro e STLink, utilizados no arquivo
 *          Serial_Bridge.c.
 *
 * @author  Caio Felipe
 * @date    28 jul 2025
 *
 * @note
 *****************************************************************************/

#ifndef INC_SERIAL_BRIDGE_H_
#define INC_SERIAL_BRIDGE_H_

#include "stm32l4xx_hal.h"


/* --------------------------------------------------------------------------
 * Constantes e macros
 * --------------------------------------------------------------------------*/

/** @brief Tamanho do buffer de dados recebidos nas filas. */
#define BUFFER_SIZE 64

/** @brief Tamanho do buffer de debug. */
#define DEBUG_BUFFER_SIZE 24

/* --------------------------------------------------------------------------
 * Estruturas de dados
 * --------------------------------------------------------------------------*/
/**
 * @struct Serial_Bridge_Struct
 * @brief Estrutura de estado de cada USART da ponte serial
 *
 * Contém buffer dos dados e informações do sistema de fila dos buffers
 */
typedef struct {
	uint8_t rx_buffer[BUFFER_SIZE];
	uint8_t last;              // Próximo a escrever
	uint8_t first;             // Próximo a enviar
	uint8_t tx_in_progress;
	uint8_t receiver;          // byte atual recebido
	UART_HandleTypeDef *uart;  // UART associada
} Serial_Bridge_Struct;

/* --------------------------------------------------------------------------
 * Protótipos de função pública
 * --------------------------------------------------------------------------*/

/**
 * @brief   Inicializa a ponte de comunicação entre FPGA e STLink.
 * @param   huart1 Ponteiro para uart previamente configurado.
 * @param   huart2 Ponteiro para uart previamente configurado.
 */
void Start_Bridge(UART_HandleTypeDef *huart1, UART_HandleTypeDef *huart2);

/**
 * @brief   Permite leitura de dados enviados pela FPGA.
 * @return  Ponteiro para buffer de debug com dados enviados pela FPGA.
 */
uint8_t* Read_Messages_From_FPGA();

/**
 * @brief   Define a posição atual do buffer de comando para zero.
 */
void Set_CMD_Index_Zero();

/**
 * @brief   Define a posição atual do buffer de mensagens para zero.
 */
void Set_MSG_Index_Zero();

#endif /* INC_SERIAL_BRIDGE_H_ */
