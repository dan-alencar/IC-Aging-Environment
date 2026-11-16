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
#include "protocol.h"


/* --------------------------------------------------------------------------
 * Constantes e macros
 * --------------------------------------------------------------------------*/

/** @brief Tamanho do buffer de debug. */
#define DEBUG_BUFFER_SIZE 24

/** @brief Fila de saída de cada USART (arquitetura B: era MESSAGE_BUFFER_SIZE = 192, que
 *         não cabia um $TEL e um $FPG juntos e descartava linhas em silêncio). */
#define BRIDGE_RING_SIZE 2048

/** @brief Quanto uma tarefa espera por espaço na fila antes de desistir da linha (ms). */
#define BRIDGE_TX_WAIT_MS 50

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
	uint8_t rx_buffer[BRIDGE_RING_SIZE];   // fila de SAÍDA (o nome vem do original)
	uint32_t last;              // Próximo a escrever
	uint32_t first;             // Próximo a enviar
	uint8_t tx_in_progress;
	uint8_t receiver;           // byte atual recebido
	uint8_t tx_byte;            // byte atual sendo transmitido via DMA
	UART_HandleTypeDef *uart;   // UART associada
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

int send_data_to_stlink(uint8_t type, uint8_t lenght, uint8_t *payload);
int send_raw_to_fpga(uint8_t *payload, uint16_t length);
int send_raw_to_stlink(uint8_t *payload, uint16_t length);

/* Arquitetura B */
int send_bytes_to_stlink(const uint8_t *payload, uint16_t length);  /* sem CRLF (respostas) */
void Bridge_Send_Hello(void);                                        /* STM_HELLO pela USART1 */
uint32_t Bridge_Stlink_Drops(void);                                  /* linhas descartadas */

#endif /* INC_SERIAL_BRIDGE_H_ */
