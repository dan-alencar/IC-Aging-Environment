/******************************************************************************
 * @file    protocol.h
 * @brief   Interface para verificação do protocolo de comunicação.
 *****************************************************************************/
#ifndef INC_PROTOCOL_H_
#define INC_PROTOCOL_H_

#include <stdint.h>

/** @brief Tamanho do buffer de mensagens. */
#define MESSAGE_BUFFER_SIZE 64 // Se precisar de mensagens maiores (logs), aumente aqui.
#define RESPONSE_BUFFER_SIZE 3
#define TIMEOUT_MS 70u

#define DIRECTION_MASK 0x80
#define FUNCTION_MASK  0x03
#define ERROR_MASK     0x70   // <--- ADICIONADO: Máscara para verificar erro

#define CRC_OK         0x0000

#define ROUTER_HEADER_STM 0x20

// Formato da mensagem: 'sentido + tipo de erro + função' + crc
typedef enum {
	NO_ERROR    = 0x00,
	ERR_TIMEOUT = 0x10,
	ERR_CRC     = 0x20,
	ERR_LEN     = 0x30
} Communication_Errors;

typedef enum {
	FUNC_UNK       = 0x00,
	FUNC_P         = 0x01,
	FUNC_M         = 0x02,
	FUNC_V         = 0x03
} Communication_Functions;

typedef enum {
	IDLE_STATE          = 0x00,
	GET_MESSAGE_SIZE    = 0x01,
	GET_MESSAGE_CONTENT = 0x02,
	GET_PAGE_VALUE      = 0x03,
	GET_VOLTAGE_VALUE   = 0x04,
	VERIFY_CRC          = 0x05,
	SEND_RESPONSE       = 0x06
} Communication_States;

typedef enum {
	STM_MASTER  = 0x80,
	STM_SLAVE   = 0x00
} Communication_Direction;

typedef struct {
	uint8_t  direction;
	uint8_t  function;
	uint16_t  size;
	uint8_t  buffer[MESSAGE_BUFFER_SIZE];
	uint8_t  count;
	uint8_t  state;
	uint8_t  error;
	uint8_t  response[RESPONSE_BUFFER_SIZE];
	uint16_t crc;
	uint32_t timeout;
} Data_ctx;

/* --------------------------------------------------------------------------
 * Protótipos de função pública
 * --------------------------------------------------------------------------*/

int Data_Pooling(uint8_t data, Data_ctx *message);
int Send_Message();
void Initialize_Message(Data_ctx *message);
int crc_calc_hex(uint8_t *buf, int len); // Adicionado protótipo

#endif /* INC_PROTOCOL_H_ */
