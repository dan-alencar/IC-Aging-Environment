/******************************************************************************
 * @file    protocol.c
 * @brief   Interface de verificação dos dados recebidos.
 * FIX: Resposta imediata para evitar falso erro de Timeout.
 *****************************************************************************/

#include "stm32l4xx_hal.h"
#include "protocol.h"
#include "Serial_Bridge.h"
#include "IHM.h"

int send_data = 0;
int crc_size = 0;

static inline uint32_t Get_Tick(void) {
    return HAL_GetTick();
}

static inline void Enable_Send_data(void) {
    send_data = 1;
}

static inline void Disable_Send_Data(void) {
    send_data = 0;
}

static inline uint16_t crc_update(uint16_t crc, uint8_t data) {
    crc ^= data;
    for (int b = 0; b < 8; b++) {
        if (crc & 0x0001) crc = (crc >> 1) ^ 0xA001;
        else              crc >>= 1;
    }
    return crc;
}

static uint16_t calc_crc_ui(const uint8_t *data, int len) {
    uint16_t crc = 0xFFFF;
    for (int i = 0; i < len; i++) {
        crc = crc_update(crc, data[i]);
    }
    return crc;
}

int crc_calc_hex(uint8_t *buf, int len) {
    if (buf == NULL || len < 0) return -1;
    uint16_t crc = calc_crc_ui(buf, len);
    buf[len + 0] = (uint8_t)(crc & 0xFF);
    buf[len + 1] = (uint8_t)((crc >> 8) & 0xFF);
    return len + 2;
}

void Apply_Command(Data_ctx *message) {
    MYMGM1R_Struct *MYMGM1R_ctx = Get_MYM_ctx();

    if ((message->function & 0x03) == FUNC_P) {
        int page = message->buffer[1] - '0';
        if (page < 1) page = 1;
        if (page > 6) page = 6;
        change_page((uint8_t)page);
    }
    else if ((message->function & 0x03) == FUNC_V) {
        // Parse "1.00"
        int i1 = message->buffer[1] - '0';
        int d1 = message->buffer[3] - '0';
        int d2 = message->buffer[4] - '0';
        float new_Vcore = (float)i1 + d1/10.0f + d2/100.0f;

        if (new_Vcore < 0.7f) new_Vcore = 0.70f;
        if (new_Vcore > 1.7f) new_Vcore = 1.70f;

        if (MYMGM1R_ctx) {
            MYMGM1R_Set_Vcore(MYMGM1R_ctx, new_Vcore);
        }
    }
}

int Send_Message() {
    return send_data;
}

void Initialize_Message(Data_ctx *message) {
    message->count     = 0x00;
    message->function  = 0x00;
    message->size      = 0x00;
    message->state     = IDLE_STATE;
    message->error     = NO_ERROR;
    message->direction = STM_SLAVE;
    message->crc       = 0xFFFF;
    message->timeout   = Get_Tick();
}

// Helper para enviar resposta imediatamente
static void Prepare_Response(Data_ctx *message) {
    if (message->direction == STM_SLAVE) {
        message->response[0] = message->direction + message->error + message->function;
        // Calcula CRC da resposta (1 byte payload + 2 CRC)
        crc_calc_hex(message->response, 1);
        Enable_Send_data();
    }
    // Reseta para esperar próximo comando
    message->state = IDLE_STATE;
}

int Data_Pooling(uint8_t data, Data_ctx *message)
{
    uint32_t now = Get_Tick();

    // Filtro de Header do Roteador (ignora byte 0x20 isolado em IDLE)
    if (message->state == IDLE_STATE && data == ROUTER_HEADER_STM) {
        return message->count;
    }

    // Timeout Check (não aplica se estivermos em IDLE)
    if (message->state != IDLE_STATE && (uint32_t)(now - message->timeout) >= TIMEOUT_MS) {
        message->error = ERR_TIMEOUT;
        // Se der timeout no meio do pacote, aborta e manda erro agora mesmo?
        // Ou reseta para IDLE. Vamos resetar para IDLE para evitar travar.
        // Mas se quiser reportar o erro, chamamos Prepare_Response.
        Prepare_Response(message);
        return message->count;
    }
    else {
        message->timeout = now;
    }

    switch (message->state) {
        case IDLE_STATE:
            // --- BLINDAGEM DE ROTEAMENTO ---
            if ((data & DIRECTION_MASK) != STM_SLAVE) return message->count;
            if ((data & ERROR_MASK) != NO_ERROR) return message->count;
            if ((data & FUNCTION_MASK) == FUNC_UNK) return message->count;
            // -------------------------------

            Initialize_Message(message);
            Disable_Send_Data();
            crc_size = 0;

            message->direction = STM_SLAVE;
            message->function  = data & FUNCTION_MASK;

            if (message->function == FUNC_P) message->state = GET_PAGE_VALUE;
            else if (message->function == FUNC_V) message->state = GET_VOLTAGE_VALUE;
            else if (message->function == FUNC_M) message->state = GET_MESSAGE_SIZE;

            message->buffer[message->count++] = data;
            message->crc = crc_update(message->crc, data);
            break;

        case GET_MESSAGE_SIZE:
            if (message->count == 2) {
                message->size |= (uint16_t)data;
                if (message->size >= MESSAGE_BUFFER_SIZE - 5) message->error = ERR_LEN;
                message->state = GET_MESSAGE_CONTENT;
            } else {
                message->size = (uint16_t)data << 8;
            }
            message->buffer[message->count++] = data;
            message->crc = crc_update(message->crc, data);
            break;

        case GET_MESSAGE_CONTENT:
            if (message->error == ERR_LEN) {
                // Se erro de tamanho, consome até acabar e depois responde erro
                if (message->count == message->size + 3) {
                    Prepare_Response(message);
                }
            }
            else if (message->count - 2 == message->size) {
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
            if (message->count == 4) message->state = VERIFY_CRC;
            message->buffer[message->count++] = data;
            message->crc = crc_update(message->crc, data);
            break;

        case VERIFY_CRC:
            message->buffer[message->count++] = data;
            message->crc = crc_update(message->crc, data);

            if (++crc_size == 2) {
                // Checagem final do CRC
                if (message->crc == CRC_OK) {
                    if (message->error == NO_ERROR) {
                        // SUCESSO: Executa o comando
                        Apply_Command(message);
                    }
                } else {
                    // FALHA: Erro de CRC
                    if (message->error == NO_ERROR) {
                        message->error = ERR_CRC;
                    }
                }

                // --- FIX CRÍTICO: RESPOSTA IMEDIATA ---
                // Não usamos 'state = SEND_RESPONSE'. Respondemos agora.
                Prepare_Response(message);
            }
            break;

        case SEND_RESPONSE:
            // Este estado não é mais usado para esperar bytes.
            // Se cair aqui por algum motivo, reseta.
            message->state = IDLE_STATE;
            break;
    }
    return message->count;
}
