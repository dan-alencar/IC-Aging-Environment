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
 *          0xA001 e valor inicial 0xFFFF, recebendo 2 bytes hexadecimais.
 *****************************************************************************/

#include "stm32l4xx_hal.h"
#include "protocol.h"
#include "Serial_Bridge.h"
#include "IHM.h"
#include "cmsis_os.h"
#include "main.h"
#include "utils.h"

int send_data = 0;
int crc_size = 0;

#ifndef HUB_VCORE_MAX_V
#define HUB_VCORE_MAX_V 1.00f
#endif

/* ---------------------------------------------------------------------------
 * Arquitetura B: fila de comandos entre a interrupção da USART2 e a Command_Task.
 * Antes, Apply_Command rodava dentro da interrupção: o osMutexAcquire do I2C não
 * funciona ali (volta osErrorISR na hora), então o FUNC_V podia achar o I2C ocupado
 * pela get_measures e não chegar ao PMIC, e o $BST disputava o buffer do $TEL.
 * -------------------------------------------------------------------------*/
#define CMD_QUEUE 4u
#define CMD_FLAG  0x0001u
static Data_ctx cmd_q[CMD_QUEUE];
static volatile uint8_t cmd_w, cmd_r;
static volatile osThreadId_t cmd_task;

static int Queue_Command(const Data_ctx *message)
{
    uint8_t next = (uint8_t)((cmd_w + 1u) % CMD_QUEUE);
    if (next == cmd_r) {
        return -1;                                 /* fila cheia */
    }
    Data_ctx *slot = &cmd_q[cmd_w];
    slot->function  = message->function;
    slot->direction = message->direction;
    slot->count     = message->count;
    for (uint32_t i = 0; i < 8u && i < MESSAGE_BUFFER_SIZE; i++) {
        slot->buffer[i] = message->buffer[i];
    }
    cmd_w = next;
    if (cmd_task != NULL) {
        osThreadFlagsSet((osThreadId_t)cmd_task, CMD_FLAG);
    }
    return 0;
}
float max_current = 2.00;
uint8_t is_cmd_e = 0;

/*******************************************************************************
 * @brief Permite o envio dos dados.
 *
 * @return 1 caso seja permitido enviar os dados, 0 caso contrário.
 ******************************************************************************/
int Send_Message()
{
	return send_data;
}


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

uint8_t is_cmd_enable() {
	return is_cmd_e;
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
            if (crc & 0x0001){
            	crc = (crc >> 1) ^ 0xA001;
            }
            else{
                crc >>= 1;
            }
        }
    }
    return crc;
}

uint16_t crc_update(uint16_t crc, uint8_t data)
{
    crc ^= data;
    for (int b = 0; b < 8; b++) {
        if (crc & 0x0001) {
        	crc = (crc >> 1) ^ 0xA001;
        }
        else {
        	crc >>= 1;
        }
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
    Telemetry_Context *telemetry_ctx = Get_Telemetry_CTX();

    if ((message->function & FUNCTION_MASK) == FUNC_P) {
        uint8_t page = message->buffer[1] - '0';
        if (page < 1) {
        	page = 1;
        }
        if (page > 6) {
        	page = 6;
        }

		change_page(page);
    }
    else if ((message->function & FUNCTION_MASK) == FUNC_V) {
        int i1 = message->buffer[1] - '0';
        int d1 = message->buffer[3] - '0';
        int d2 = message->buffer[4] - '0';
        float new_Vcore = (float)i1 + d1/10.0f + d2/100.0f;

        if (new_Vcore < 0.7) {
        	new_Vcore = 0.70;
        }
        /* Arquitetura B: o 361fc39 deixava até 1.30 V. O máximo absoluto do VCCINT da
         * Artix UltraScale+ é 1.0 V (o D&T Monitor já para em 0.95 V). */
        if (new_Vcore > HUB_VCORE_MAX_V) {
        	new_Vcore = HUB_VCORE_MAX_V;
        }

		if (MYMGM1R_ctx) {
			osMutexAcquire(i2cMutexHandle, osWaitForever);
			MYMGM1R_Set_Vcore(MYMGM1R_ctx, new_Vcore);
			osMutexRelease(i2cMutexHandle);
		}

		change_max_current(get_max_current());
        if (telemetry_ctx != NULL) {
            Telemetry_Send_Board_Status(telemetry_ctx);
        }
    }
    else if ((message->function & FUNCTION_MASK) == FUNC_E) {
    	if (message->buffer[1] == 'V') {
    		is_cmd_e = 0;
    		osMutexAcquire(i2cMutexHandle, osWaitForever);
    		MYMGM1R_OUTPUT_Enable(MYMGM1R_ctx);
    		osMutexRelease(i2cMutexHandle);
            Telemetry_Set_Output_State(telemetry_ctx, 1u);
    	}
    	else if (message->buffer[1] == 'F') {
    		is_cmd_e = 1;
    		osMutexAcquire(i2cMutexHandle, osWaitForever);
    		MYMGM1R_OUTPUT_Disable(MYMGM1R_ctx);
    		osMutexRelease(i2cMutexHandle);
            Telemetry_Set_Output_State(telemetry_ctx, 0u);
    	}
        if (telemetry_ctx != NULL) {
            Telemetry_Send_Board_Status(telemetry_ctx);
        }
    }
    else if ((message->function & FUNCTION_MASK) == FUNC_S) {
    	int i1 = message->buffer[1] - '0';
		int d1 = message->buffer[3] - '0';
		int d2 = message->buffer[4] - '0';
		float new_max_current = (float)i1 + d1/10.0f + d2/100.0f;
		change_max_current(new_max_current);
        if (telemetry_ctx != NULL) {
            Telemetry_Send_Board_Status(telemetry_ctx);
        }
    }
}

uint8_t make_identifier(uint8_t function) {
	return STM_MASTER + function + NO_ERROR; //TODO: Fazer check se function é uma função válida
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
	message->deferred  = 0;
}

static void Prepare_Response(Data_ctx *message)
{
    /* Comando enfileirado: a resposta sai da Command_Task, depois de aplicado. */
    if (message->direction == STM_SLAVE && !message->deferred) {
        message->response[0] = message->direction + message->error + message->function;
        crc_calc_hex(message->response, 1);
        Enable_Send_data();
    }
    message->deferred = 0;
    message->state = IDLE_STATE;
}

void Command_Task(void *argument)
{
    (void)argument;
    cmd_task = osThreadGetId();
    for (;;) {
        osThreadFlagsWait(CMD_FLAG, osFlagsWaitAny, osWaitForever);
        while (cmd_r != cmd_w) {
            Data_ctx *c = &cmd_q[cmd_r];
            Apply_Command(c);
            uint8_t resp[RESPONSE_BUFFER_SIZE];
            resp[0] = (uint8_t)(STM_SLAVE + NO_ERROR + c->function);   /* "aplicado" */
            crc_calc_hex(resp, 1);
            cmd_r = (uint8_t)((cmd_r + 1u) % CMD_QUEUE);
            send_bytes_to_stlink(resp, RESPONSE_BUFFER_SIZE);
        }
    }
}

uint16_t Data_Pooling(uint8_t data, Data_ctx *message)
{
    uint32_t now = Get_Tick();

    if (message->state == IDLE_STATE && data == ROUTER_HEADER_STM) {
        return message->count;
    }

    if (message->state != IDLE_STATE && (uint32_t)(now - message->timeout) >= TIMEOUT_MS) {
        message->error = ERR_TIMEOUT;
        Prepare_Response(message);
        return message->count;
    }
    message->timeout = now;

    switch (message->state) {
        case IDLE_STATE:
            Initialize_Message(message);
            Disable_Send_Data();
            crc_size = 0;
            if ((data & DIRECTION_MASK) != STM_SLAVE) {
                return message->count;
            }
            if ((data & ERROR_MASK) != NO_ERROR) {
                return message->count;
            }

            message->direction = STM_SLAVE;
            message->function = data & FUNCTION_MASK;

            if (message->function == FUNC_P) {
                message->state = GET_PAGE_VALUE;
            }
            else if (message->function == FUNC_V || message->function == FUNC_S) {
                message->state = GET_VOLTAGE_VALUE;
            }
            else if (message->function == FUNC_M) {
                message->state = GET_MESSAGE_SIZE;
            }
            else if (message->function == FUNC_E) {
                message->state = GET_ENABLE_VALUE;
            }
            else {
                return message->count;
            }

            message->buffer[message->count++] = data;
            message->crc = crc_update(message->crc, data);
            break;

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
        		message->count++;
        		if (message->count == message->size + 4) {
                    Prepare_Response(message);
        		}
        		break;
        	}
            if (message->count - 2 == message->size) {
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

        case GET_ENABLE_VALUE:
			message->buffer[message->count++] = data;
			message->crc = crc_update(message->crc, data);
			message->state = VERIFY_CRC;
			break;

        case VERIFY_CRC:
            message->buffer[message->count++] = data;
            message->crc = crc_update(message->crc, data);

            if (++crc_size == 2) {
                if (message->crc == CRC_OK) {
                    if (message->error == NO_ERROR) {
                        /* Arquitetura B: aplica na Command_Task, fora da interrupção */
                        if (Queue_Command(message) == 0) {
                            message->deferred = 1;
                        } else {
                            message->error = ERR_LEN;       /* fila cheia (4 comandos) */
                        }
                    }
                }
                else {
                    if (message->error == NO_ERROR) {
                        message->error = ERR_CRC;
                    }
                }
                Prepare_Response(message);
            }
            else {
            	break;
            }
            break;

        case SEND_RESPONSE:
            message->state = IDLE_STATE;
            break;
    }
    return message->count;
}
