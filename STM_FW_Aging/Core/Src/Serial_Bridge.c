/******************************************************************************
 * @file    Serial_Bridge.c
 * @brief   Driver para criar ponte de comunicação USART
 *
 *          Implementa ponte de comunicação USART entre a FPGA e STLink via DMA.
 *
 * @author  Caio Felipe
 * @date    25 jul 2025
 *
 * @note    Nessa implementação cada USART possui um sistema de fila que contém
 *          dados importantes para a comunicação entre eles. Dessa forma, é possível
 *          que cada USART possa enviar e receber dados simultaneamente sem problemas.
 *****************************************************************************/

#include "stm32l4xx_hal.h"
#include "Serial_Bridge.h"
#include "protocol.h"
#include "IHM.h"
#include "main.h"

static Serial_Bridge_Struct buffer_fpga;

#ifdef ENABLE_STLINK_DEBUG
static Serial_Bridge_Struct buffer_stlink;
Data_ctx message_from_stlink;
#endif

Data_ctx message_from_fpga_cmd;

uint8_t buffer[DEBUG_BUFFER_SIZE] = {0};

int ind = 0, message_size = 0;

static inline uint8_t buffer_is_empty(Serial_Bridge_Struct *q)
{
    return q->last == q->first;
}

static inline uint8_t buffer_is_full(Serial_Bridge_Struct *q)
{
    return ((q->last + 1) % BUFFER_SIZE) == q->first;
}

static inline void buffer_push(Serial_Bridge_Struct *q, uint8_t data)
{
    if (!buffer_is_full(q)) {
        q->rx_buffer[q->last] = data;
        q->last = (q->last + 1) % BUFFER_SIZE;
    }
}

static inline uint8_t buffer_pop(Serial_Bridge_Struct *q)
{
    uint8_t data = q->rx_buffer[q->first];
    q->first = (q->first + 1) % BUFFER_SIZE;
    return data;
}

void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart)
{
#ifdef ENABLE_STLINK_DEBUG
	/* =========================================================================
	   MODO DEBUG:
	   - UART1 (FPGA): Apenas repassa dados crus para UART2 (STLink) e Buffer Debug.
	   - UART2 (STLink): Recebe comandos do protocolo.
	   ========================================================================= */
	if (huart->Instance == USART1) {
		uint8_t byte = buffer_fpga.receiver;
		buffer[ind] = byte;
		ind = (ind + 1) % DEBUG_BUFFER_SIZE;

		buffer_push(&buffer_stlink, byte);

		// Se a UART2 não estiver transmitindo, começa a transmissão
		if (!buffer_stlink.tx_in_progress && !buffer_is_empty(&buffer_stlink)) {
			buffer_stlink.tx_in_progress = 1;
			uint8_t data = buffer_pop(&buffer_stlink);
			HAL_UART_Transmit_DMA(buffer_stlink.uart, &data, 1);
		}

		HAL_UART_Receive_DMA(buffer_fpga.uart, &buffer_fpga.receiver, 1);
	}

	else if (huart->Instance == USART2) {
		uint8_t byte2 = buffer_stlink.receiver;

		message_size = Data_Pooling(byte2, &message_from_stlink);

		if(Send_Message()){
			// Lógica original de resposta para STLink e Forward para FPGA
			if(message_from_stlink.error == NO_ERROR && message_from_stlink.function == FUNC_M) {
				for (int l = 0; l < RESPONSE_BUFFER_SIZE; l++) {
					buffer_push(&buffer_stlink, message_from_stlink.response[l]);
				}
				if (!buffer_stlink.tx_in_progress && !buffer_is_empty(&buffer_stlink)) {
					buffer_stlink.tx_in_progress = 1;
					uint8_t data = buffer_pop(&buffer_stlink);
					HAL_UART_Transmit_DMA(buffer_stlink.uart, &data, 1);
				}
				for(int l = 0; l < message_size; l++) {
					buffer_push(&buffer_fpga, message_from_stlink.buffer[l]);
				}
			}
			else {
				for(int l = 0; l < RESPONSE_BUFFER_SIZE; l++) {
					buffer_push(&buffer_stlink, message_from_stlink.response[l]);
				}
				if (!buffer_stlink.tx_in_progress && !buffer_is_empty(&buffer_stlink)) {
					buffer_stlink.tx_in_progress = 1;
					uint8_t data = buffer_pop(&buffer_stlink);
					HAL_UART_Transmit_DMA(buffer_stlink.uart, &data, 1);
				}
			}

			if (!buffer_fpga.tx_in_progress && !buffer_is_empty(&buffer_fpga)) {
				buffer_fpga.tx_in_progress = 1;
				uint8_t data2 = buffer_pop(&buffer_fpga);
				HAL_UART_Transmit_DMA(buffer_fpga.uart, &data2, 1);
			}
			HAL_UART_Receive_DMA(buffer_stlink.uart, &buffer_stlink.receiver, 1);
		}
        else {
            // Se Data_Pooling não completou mensagem, reativa recepção
            HAL_UART_Receive_DMA(buffer_stlink.uart, &buffer_stlink.receiver, 1);
        }
	}

#else
	/* =========================================================================
	   MODO RELEASE (BYPASS):
	   - UART1 (FPGA): Recebe COMANDOS vindos do PC (via bypass da FPGA).
	   - UART2: Desligada.
	   - O buffer de debug visual (OLED Page 6) é desativado ou reduzido, pois
	     agora a linha recebe protocolo binário e não strings de debug.
	   ========================================================================= */
	if (huart->Instance == USART1) {
		uint8_t byte = buffer_fpga.receiver;

		// Processa o byte como parte do protocolo (agora vindo da FPGA)
		message_size = Data_Pooling(byte, &message_from_fpga_cmd);

		if(Send_Message()){
			// Se a mensagem foi processada e exige resposta, enviamos DE VOLTA para a FPGA (UART1)
            // Nota: No código original, a resposta do STM sempre ia para o STLink.
            // Agora ela deve voltar para a FPGA para retornar ao PC.

            // Prepara a resposta no buffer de transmissão da FPGA
			for(int l = 0; l < RESPONSE_BUFFER_SIZE; l++) {
				buffer_push(&buffer_fpga, message_from_fpga_cmd.response[l]);
			}

			// Se houver dados adicionais (ex: no caso de FUNC_M ou erro), adicionar aqui conforme lógica original
            // Se FUNC_M for "Mensagem", e a FPGA for a fonte, talvez não precise de echo.
            // Mantendo simples: Envia resposta de status.

			// Inicia transmissão na UART1 se não estiver ocupada
			if (!buffer_fpga.tx_in_progress && !buffer_is_empty(&buffer_fpga)) {
				buffer_fpga.tx_in_progress = 1;
				uint8_t data_resp = buffer_pop(&buffer_fpga);
				HAL_UART_Transmit_DMA(buffer_fpga.uart, &data_resp, 1);
			}
		}

		// Reativa a escuta na UART1
		HAL_UART_Receive_DMA(buffer_fpga.uart, &buffer_fpga.receiver, 1);
	}
#endif
}

void HAL_UART_TxCpltCallback(UART_HandleTypeDef *huart)
{
	Serial_Bridge_Struct *q = NULL;

		if (huart->Instance == USART1) q = &buffer_fpga;
	#ifdef ENABLE_STLINK_DEBUG
		else if (huart->Instance == USART2) q = &buffer_stlink;
	#endif
		else return;

		if (!buffer_is_empty(q)) {
			uint8_t data3 = buffer_pop(q);
			HAL_UART_Transmit_DMA(q->uart, &data3, 1);
		}
		else {
			q->tx_in_progress = 0;
		}
}

/*****************************************************************************
 * @brief Inicializa ponte de comunicação via UART com DMA.
 *
 * @param[in] huart1 Ponteiro para primeira uart previamente configurado.
 * @param[in] huart2 Ponteiro para segunda uart previamente configurado.
 ******************************************************************************/
void Start_Bridge(UART_HandleTypeDef *huart1, UART_HandleTypeDef *huart2)
{
	// Inicializa estrutura da UART1 (FPGA) - Sempre usada
	    Initialize_Message(&message_from_fpga_cmd); // Inicializa struct de comando da FPGA
		buffer_fpga.last = 0;
		buffer_fpga.first = 0;
		buffer_fpga.tx_in_progress = 0;
		buffer_fpga.uart = huart1;
		HAL_UART_Receive_DMA(huart1, &buffer_fpga.receiver, 1);

	#ifdef ENABLE_STLINK_DEBUG
		if (huart2 != NULL) {
			Initialize_Message(&message_from_stlink);
			buffer_stlink.last = 0;
			buffer_stlink.first = 0;
			buffer_stlink.tx_in_progress = 0;
			buffer_stlink.uart = huart2;
			HAL_UART_Receive_DMA(huart2, &buffer_stlink.receiver, 1);
		}
	#endif
}

/**
 * @brief   Permite leitura de dados enviados pela FPGA.
 * @return  Ponteiro para buffer de debug com dados enviados pela FPGA.
 */
uint8_t* Read_Messages_From_FPGA(){
	return buffer;
}

/**
 * @brief  Função chamada pela HAL quando ocorre erro na UART (Ruído, Overrun, Frame).
 * Essencial para reiniciar a recepção se a comunicação falhar.
 */
void HAL_UART_ErrorCallback(UART_HandleTypeDef *huart)
{
    // Se o erro for na UART da FPGA (UART1)
    if (huart->Instance == USART1) {
        // Limpa flags de erro (Opcional, a HAL geralmente faz, mas garante reinicio)
        __HAL_UART_CLEAR_OREFLAG(huart);
        __HAL_UART_CLEAR_NEFLAG(huart);
        __HAL_UART_CLEAR_FEFLAG(huart);

        // REINICIA A ESCUTA VIA DMA IMEDIATAMENTE
        // Sem isso, o STM32 para de ouvir para sempre após o primeiro ruído.
        HAL_UART_Receive_DMA(huart, &buffer_fpga.receiver, 1);
    }

    #ifdef ENABLE_STLINK_DEBUG
    else if (huart->Instance == USART2) {
        HAL_UART_Receive_DMA(huart, &buffer_stlink.receiver, 1);
    }
    #endif
}
