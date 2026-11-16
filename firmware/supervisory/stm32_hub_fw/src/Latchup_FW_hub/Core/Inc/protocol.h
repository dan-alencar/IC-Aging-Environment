/******************************************************************************
 * @file    protocol.h
 * @brief   Interface para verificação do protocolo de comunicação.
 *
 *          Define funções que verificam os dados recebidos na comunicação
 *          e permitem o envio desses dados para a FPGA.
 *
 * @author  Caio Felipe
 * @date    03 set 2025
 *
 * @note
 *****************************************************************************/
#ifndef INC_PROTOCOL_H_
#define INC_PROTOCOL_H_


/** @brief Tamanho do buffer de mensagens. */
#define MESSAGE_BUFFER_SIZE 192
#define RESPONSE_BUFFER_SIZE 3
#define TIMEOUT_MS 70u

#define DIRECTION_MASK 0x80
#define FUNCTION_MASK  0x07
#define ERROR_MASK     0x70
#define ROUTER_HEADER_STM 0x20

#define CRC_OK         0x0000

// Formato da mensagem: 'sentido + tipo de erro + função' + crc
typedef enum {
	NO_ERROR    = 0x00,
	ERR_TIMEOUT = 0x10,
	ERR_CRC     = 0x20,
	ERR_LEN     = 0x30
} Communication_Errors;

typedef enum {
	FUNC_UNK       = 0x00, // Unknown command
	FUNC_P         = 0x01, // Page command
	FUNC_M         = 0x02, // Message command
	FUNC_V         = 0x03, // Voltage command
	FUNC_T         = 0x04, // Telemetry command
	FUNC_E         = 0x05, // Enable/Disable MYM command
	FUNC_S         = 0x06  // Set max current command
} Communication_Functions;

typedef enum {
	IDLE_STATE          = 0x00,
	GET_MESSAGE_SIZE    = 0x01,
	GET_MESSAGE_CONTENT = 0x02,
	GET_PAGE_VALUE      = 0x03,
	GET_VOLTAGE_VALUE   = 0x04,
	GET_ENABLE_VALUE    = 0x05,
	VERIFY_CRC          = 0x06,
	SEND_RESPONSE       = 0x07
} Communication_States;

typedef enum {
	STM_MASTER  = 0x80,
	STM_SLAVE   = 0x00
} Communication_Direction;

typedef struct {
	uint8_t  direction;
	uint8_t  function;
	uint32_t  size;
	uint8_t  buffer[MESSAGE_BUFFER_SIZE];
	uint32_t  count;
	uint8_t  state;
	uint8_t  error;
	uint16_t crc;
	uint8_t  response[RESPONSE_BUFFER_SIZE];
	uint32_t timeout;
	uint8_t  deferred;   /* arquitetura B: a Command_Task aplica e responde */
} Data_ctx;

/* --------------------------------------------------------------------------
 * Protótipos de função pública
 * --------------------------------------------------------------------------*/

/**
 * @brief   Verifica o tipo de dados recebidos e valida eles.
 * @param   data    Byte que será verificado.
 * @param   message Struct de mensagem com dados relevantes para identificação dela.
 * @return  Tamanho da mensagema ser enviada.
 */
uint16_t Data_Pooling(uint8_t data, Data_ctx *message);

/**
 * @brief   Função que permite o envio de dados para a FPGA.
 * @return  Retorna 1 caso possa enviar os dados, 0 caso contrário.
 */
int Send_Message();

void Initialize_Message(Data_ctx *message);

uint8_t make_identifier(uint8_t function);

uint16_t crc_update(uint16_t crc, uint8_t data);
int crc_calc_hex(uint8_t *buf, int len);

uint8_t is_cmd_enable();

/* Arquitetura B: os comandos válidos que chegam pelo ST-Link são aplicados nesta
 * tarefa, fora da interrupção da UART (I2C com o mutex, $BST sem disputar o buffer). */
void Command_Task(void *argument);

#endif /* INC_PROTOCOL_H_ */
