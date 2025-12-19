/******************************************************************************
 * @file    protocol.c
 * @brief   Interface de verificação dos dados recebdos na comunicação.
 *
 *          Implementa rotinas de verificação do tipo da mensagem, do CRC e
 *          permite a aplicação direta dos comandos recebidos.
 *
 * @author  Caio Felipe
 * @date    03 set 2025
 *
 * @note    Para nosso protocolo de comunicação, usamos um CRC16 com polinômio
 *          0xA001 e valor inicial 0xFFFF, recebendo 4 dígitos hexadecimais.
 *****************************************************************************/

#include "stm32l4xx_hal.h"
#include "protocol.h"
#include "Serial_Bridge.h"
#include "IHM.h"

int send_data = 0;
int crc_size = 0;

static inline uint32_t Get_Tick(void)
{
    return HAL_GetTick();
}

static inline void Enable_Send_data(void)
{
    send_data = 1;
}

static inline void Disable_Send_Data(void)
{
    send_data = 0;
}

/*******************************************************************************
 * @brief Faz o calculo para determinar o crc.
 *
 * @param[in] *data Ponteiro para posição inicial dos dados que serão usados no cálculo.
 * @param[in] len   Quantidade de dados usados no calculo.
 *
 * @return Valor do crc correspondente aos dados recebidos.
 ******************************************************************************/
static uint16_t calc_crc_ui(const uint8_t *data, int len)
{
    uint16_t crc = 0xFFFF;
    for (int i = 0; i < len; i++) {
        crc ^= data[i];
        for (int b = 0; b < 8; b++) {
            if (crc & 0x0001)
                crc = (crc >> 1) ^ 0xA001;
            else
                crc >>= 1;
        }
    }
    return crc;
}

static inline uint16_t crc_update(uint16_t crc, uint8_t data)
{
    crc ^= data;
    for (int b = 0; b < 8; b++) {
        if (crc & 0x0001) crc = (crc >> 1) ^ 0xA001;
        else              crc >>= 1;
    }
    return crc;
}

/*******************************************************************************
 * @brief Calcula o CRC16/Modbus do buffer (somente payload) e ANEXA 2 BYTES binários.
 *
 * Convenção: ordem Modbus (LSB primeiro): buf[len] = CRC_L, buf[len+1] = CRC_H
 *
 * @param[in,out] buf Buffer onde já está o payload e onde serão anexados os 2 bytes do CRC.
 * @param[in]     len Tamanho atual do payload (em bytes) SEM o CRC.
 *
 * @return Novo comprimento (len + 2) em caso de sucesso; -1 se parâmetros inválidos.
 *******************************************************************************/
int crc_calc_hex(uint8_t *buf, int len)
{
    if (buf == NULL || len < 0) {
        return -1;
    }

    uint16_t crc = calc_crc_ui(buf, len);


    buf[len + 0] = (uint8_t)(crc & 0xFF);
    buf[len + 1] = (uint8_t)((crc >> 8) & 0xFF);

    return len + 2;
}

/*******************************************************************************
 * @brief Verifica o tipo de comando e aplica ele.
 *
 * @param[in] buffer_cmd Buffer com os comandos.
 ******************************************************************************/
void Apply_Command(Data_ctx *message)
{
    MYMGM1R_Struct *MYMGM1R_ctx = Get_MYM_ctx();

    if ((message->function & 0x03) == FUNC_P) {
        int page = message->buffer[1] - '0';
        if (page < 1) {
        	page = 1;
        }
        if (page > 6) {
        	page = 6;
        }

		change_page((uint8_t)page);
    }
    else if ((message->function & 0x03) == FUNC_V) {
        int i1 = message->buffer[1] - '0';
        int d1 = message->buffer[3] - '0';
        int d2 = message->buffer[4] - '0';
        float new_Vcore = (float)i1 + d1/10.0f + d2/100.0f;

        if (new_Vcore < 0.7) {
        	new_Vcore = 0.70;
        }
        if (new_Vcore > 1.7) {
        	new_Vcore = 1.70;
        }

		if (MYMGM1R_ctx) {
			MYMGM1R_Set_Vcore(MYMGM1R_ctx, new_Vcore);
		}
    }
}

/*******************************************************************************
 * @brief Permite o envio dos dados.
 *
 * @return 1 caso seja permitido enviar os dados, 0 caso contrário.
 ******************************************************************************/
int Send_Message()
{
	return send_data;
}

void Initialize_Message(Data_ctx *message)
{
	message->count     = 0x00;
	message->function  = 0x00;
	message->size      = 0x00;
	message->state     = IDLE_STATE;
	message->error     = NO_ERROR;
	message->direction = STM_SLAVE;
	message->crc       = 0xFFFF;
	message->timeout   = Get_Tick();
}

int Data_Pooling(uint8_t data, Data_ctx *message)
{
    uint32_t now = Get_Tick();

    // ---------------------------------------------------------
    // NOVO BLOCO: Filtro de Cabeçalho do Roteador (Correção)
    // ---------------------------------------------------------
    // Se a máquina de estados está esperando um novo pacote (IDLE)
    // e recebe o byte 0x20, ignoramos completamente.
    if (message->state == IDLE_STATE && data == ROUTER_HEADER_STM) {
        // Retorna a contagem atual sem alterar nada na struct.
        // O firmware finge que não viu esse byte.
        return message->count;
    }
    // ---------------------------------------------------------

    // Detecta timeout entre bytes da mensagem atual (Código original segue abaixo...)
    if (message->state != IDLE_STATE && (uint32_t)(now - message->timeout) >= TIMEOUT_MS) {
    	message->error = ERR_TIMEOUT;
    }
    else {
    	message->timeout = now;
    }

    switch (message->state) {
        case IDLE_STATE:
            Initialize_Message(message);
            Disable_Send_Data();
            crc_size = 0;
            if ((data & DIRECTION_MASK) == STM_SLAVE) {
            	message->direction = STM_SLAVE;
				if ((data & FUNCTION_MASK) == FUNC_P) {
					message->function = FUNC_P;
					message->state = GET_PAGE_VALUE;
				}
				else if ((data & FUNCTION_MASK) == FUNC_V) {
					message->function = FUNC_V;
					message->state = GET_VOLTAGE_VALUE;
				}
				else if ((data & FUNCTION_MASK) == FUNC_M) {
					message->function = FUNC_M;
					message->state = GET_MESSAGE_SIZE;
				}
				else {
					message->function = FUNC_UNK;
					break;
				}
				message->buffer[message->count++] = data;
				message->crc = crc_update(message->crc, data);
				break;
            }
            else {
            	message->direction = STM_MASTER;
            	if ((data & FUNCTION_MASK) == FUNC_M) {

            	}
            	else if ((data & FUNCTION_MASK) == FUNC_V) {

            	}
            }

        case GET_MESSAGE_SIZE:
            if (message->count == 2) {
                message->size |= (uint16_t)data;
                if (message->size >= MESSAGE_BUFFER_SIZE - 5) {
                	message->error = ERR_LEN;
                }
                message->state = GET_MESSAGE_CONTENT;
            }
            else {
            	message->size = (uint16_t)data << 8;
            }

            message->buffer[message->count++] = data;
            message->crc = crc_update(message->crc, data);
            break;

        case GET_MESSAGE_CONTENT:
        	if (message->error == ERR_LEN) {
        		if (message->count == message->size + 3) {
        			message->state = SEND_RESPONSE;
        		}
        	}
            if (message->count - 2 == message->size && message->error != ERR_LEN) {
            	message->state = VERIFY_CRC;
            }
            message->buffer[message->count++] = data;
            message->crc = crc_update(message->crc, data);
            break;


        case GET_PAGE_VALUE:
            message->buffer[message->count++] = data;
            message->crc = crc_update(message->crc, data);
            message->state = VERIFY_CRC;
            break;

        case GET_VOLTAGE_VALUE:
            if (message->count == 4) {
            	message->state = VERIFY_CRC;
            }
            message->buffer[message->count++] = data;
            message->crc = crc_update(message->crc, data);
            break;

        case VERIFY_CRC:
            message->buffer[message->count++] = data;
            message->crc = crc_update(message->crc, data);

            if (++crc_size == 2) {
                if (message->crc == CRC_OK) {
                    if (message->function == FUNC_M) {
                    	if (message->error == NO_ERROR) {
                    		Enable_Send_data();
                    	}
                    }
                    else {
                    	if (message->error == NO_ERROR) {
                    		Apply_Command(message);
                    	}
                    }
                    message->state = SEND_RESPONSE;
                }
                else {
                	if (message->error == NO_ERROR) {
                		message->state = SEND_RESPONSE;
                		message->error = ERR_CRC;
                	}
                }
            }
            else {
            	break;
            }

        case SEND_RESPONSE: // erro (timeout/CRC)
        	if (message->direction == STM_SLAVE) {
        		message->response[0] = message->direction + message->error + message->function;
				message->state = IDLE_STATE;
				crc_size = crc_calc_hex(message->response, 1);
				Enable_Send_data();
				break;
        	}
    }
    return message->count;
}
