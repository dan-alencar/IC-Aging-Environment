/******************************************************************************
 * @file    Serial_Bridge.c
 * @brief   Driver para criar ponte de comunicação USART
 *
 *          Arquitetura B (04/11/2026): a USART1 só recebe os quadros v2 do FPGA
 *          (fpga_link.c) e só transmite o STM_HELLO. Ela NUNCA executa comandos:
 *          num fluxo binário, um CRC certo por acaso viraria um FUNC_V aleatório.
 *
 *          USART1 (FPGA path)  — (original) receives commands forwarded from the FPGA
 *                                uart_router; responds back via USART1.
 *          USART2 (STLink path) — primary App ↔ STM32 channel.
 *                                 Telemetry ($TEL/$BST/$LEVT) is always sent
 *                                 here.  Commands arriving here are processed
 *                                 and responses returned on the same port.
 *                                 This path stays alive even when FPGA output
 *                                 is disabled.
 *
 * @author  Caio Felipe / dan-alencar
 * @date    25 jul 2025 / 2026-04-07
 *****************************************************************************/

#include "stm32l4xx_hal.h"
#include "Serial_Bridge.h"
#include "protocol.h"
#include "IHM.h"
#include "main.h"
#include "utils.h"
#include "fpga_link.h"
#include "cmsis_os.h"

static Serial_Bridge_Struct buffer_fpga;

/* USART1 RX (quadros do FPGA): DMA circular com evento de linha ociosa. Com o DMA de 1 byte
 * (361fc39 e versões 1–2), cada byte esperava a interrupção; com as interrupções desligadas
 * por mais de um byte (~80 µs, por exemplo ao enfileirar uma linha de 150 bytes), o byte
 * seguinte sobrescrevia o anterior e o quadro era descartado sem erro (~1 % das janelas em
 * 05/11/2026). Aqui o DMA guarda os bytes sozinho; a interrupção só os entrega ao montador. */
#define FPGA_RX_DMA_SIZE 256u
static uint8_t  fpga_rx_dma[FPGA_RX_DMA_SIZE];
static uint16_t fpga_rx_old;

static void fpga_rx_start(void)
{
    fpga_rx_old = 0u;
    HAL_UARTEx_ReceiveToIdle_DMA(buffer_fpga.uart, fpga_rx_dma, FPGA_RX_DMA_SIZE);
}

static void fpga_rx_feed(uint16_t from, uint16_t to)
{
    for (uint16_t i = from; i < to; i++) {
        FPGA_Link_Rx_Byte(fpga_rx_dma[i]);
    }
}
static volatile uint32_t stlink_drops;
static Serial_Bridge_Struct buffer_stlink;

Data_ctx message_from_fpga;
Data_ctx message_from_stlink;

uint8_t buffer[DEBUG_BUFFER_SIZE] = {0};
uint16_t ind = 0;

/* --------------------------------------------------------------------------
 * Ring-buffer helpers
 * --------------------------------------------------------------------------*/
static inline uint8_t buffer_is_empty(Serial_Bridge_Struct *q)
{
    return q->last == q->first;
}

static inline uint8_t buffer_is_full(Serial_Bridge_Struct *q)
{
    return ((q->last + 1) % BRIDGE_RING_SIZE) == q->first;
}

static inline void buffer_push(Serial_Bridge_Struct *q, uint8_t data)
{
    if (!buffer_is_full(q)) {
        q->rx_buffer[q->last] = data;
        q->last = (q->last + 1) % BRIDGE_RING_SIZE;
    }
}

static inline uint8_t buffer_pop(Serial_Bridge_Struct *q)
{
    uint8_t data = q->rx_buffer[q->first];
    q->first = (q->first + 1) % BRIDGE_RING_SIZE;
    return data;
}

static void kick_tx_if_idle(Serial_Bridge_Struct *q)
{
    if (q == NULL) {
        return;
    }
    if (!q->tx_in_progress && !buffer_is_empty(q)) {
        q->tx_in_progress = 1;
        q->tx_byte = buffer_pop(q);
        if (HAL_UART_Transmit_DMA(q->uart, &q->tx_byte, 1) != HAL_OK) {
            q->tx_in_progress = 0;
        }
    }
}

static void restart_rx_dma(Serial_Bridge_Struct *q, Data_ctx *message)
{
    if (q == NULL || q->uart == NULL) {
        return;
    }
    HAL_UART_DMAStop(q->uart);
    q->first = 0;
    q->last = 0;
    q->tx_in_progress = 0;
    if (message != NULL) {
        Initialize_Message(message);
    }
    HAL_UART_Receive_DMA(q->uart, &q->receiver, 1);
}

/* --------------------------------------------------------------------------
 * Public send helpers
 * --------------------------------------------------------------------------*/

/**
 * @brief Send raw bytes + CRLF to the STLink port (USART2).
 *        Used by the telemetry module to emit $TEL/$BST/$LEVT lines.
 *        This path remains alive even when FPGA output is disabled.
 */
static int ring_space(Serial_Bridge_Struct *q)
{
    return (q->first > q->last) ? (int)(q->first - q->last)
                                : (int)(BRIDGE_RING_SIZE - q->last + q->first);
}

static int in_task_context(void)
{
    return (__get_IPSR() == 0u) && (osKernelGetState() == osKernelRunning);
}

/* Numa tarefa, espera até BRIDGE_TX_WAIT_MS por espaço na fila (antes descartava). */
static void wait_space(Serial_Bridge_Struct *q, int needed)
{
    if (!in_task_context()) {
        return;
    }
    for (int t = 0; t < BRIDGE_TX_WAIT_MS && ring_space(q) < needed; t++) {
        osDelay(1);
    }
}

uint32_t Bridge_Stlink_Drops(void)
{
    return stlink_drops;
}

/* Bytes sem CRLF (as respostas de 3 bytes dos comandos). */
int send_bytes_to_stlink(const uint8_t *payload, uint16_t length)
{
    Serial_Bridge_Struct *q = &buffer_stlink;
    wait_space(q, (int)length + 1);
    uint32_t primask = __get_PRIMASK();
    __disable_irq();
    if (ring_space(q) < (int)length + 1) {
        stlink_drops++;
        __set_PRIMASK(primask);
        return -1;
    }
    for (uint16_t i = 0; i < length; i++) {
        buffer_push(q, payload[i]);
    }
    kick_tx_if_idle(q);
    __set_PRIMASK(primask);
    return 0;
}

/* STM_HELLO = protocol_v2.encode_frame(0x12, 0, b"HUB1"): destrava a linha do FPGA
 * para o STM32 (stm_hello_gate.v). Mandado pela FPGA_Link_Task uma vez por segundo. */
void Bridge_Send_Hello(void)
{
    static const uint8_t hello[12] = {0xA5, 0x5A, 0x02, 0x12, 0x00, 0x04,
                                      'H', 'U', 'B', '1', 0xF4, 0xD7};
    Serial_Bridge_Struct *q = &buffer_fpga;
    uint32_t primask = __get_PRIMASK();
    __disable_irq();
    if (ring_space(q) > (int)sizeof(hello)) {
        for (unsigned i = 0; i < sizeof(hello); i++) {
            buffer_push(q, hello[i]);
        }
        kick_tx_if_idle(q);
    }
    __set_PRIMASK(primask);
}

int send_raw_to_stlink(uint8_t *payload, uint16_t length)
{
    Serial_Bridge_Struct *q = &buffer_stlink;

    wait_space(q, (int)length + 3);
    uint32_t primask = __get_PRIMASK();
    __disable_irq();

    int open_space = ring_space(q);

    if (open_space < (int)(length + 3)) {
        stlink_drops++;
        __set_PRIMASK(primask);
        return -1;
    }

    for (uint16_t i = 0; i < length; i++) {
        buffer_push(q, payload[i]);
    }
    buffer_push(q, '\r');
    buffer_push(q, '\n');

    kick_tx_if_idle(q);
    __set_PRIMASK(primask);
    return 0;
}

/**
 * @brief Send raw bytes + CRLF to the FPGA port (USART1).
 *        Kept for optional debug use; telemetry no longer calls this.
 */
int send_raw_to_fpga(uint8_t *payload, uint16_t length)
{
    Serial_Bridge_Struct *q = &buffer_fpga;

    uint32_t primask = __get_PRIMASK();
    __disable_irq();

    int open_space = (q->first > q->last)
                     ? (q->first - q->last)
                     : (BRIDGE_RING_SIZE - q->last + q->first);

    if (open_space < (int)(length + 2)) {
        __set_PRIMASK(primask);
        return -1;
    }

    for (uint16_t i = 0; i < length; i++) {
        buffer_push(q, payload[i]);
    }
    buffer_push(q, '\r');
    buffer_push(q, '\n');

    kick_tx_if_idle(q);
    __set_PRIMASK(primask);
    return 0;
}

/**
 * @brief Legacy binary-framed send.  Routes to STLink port.
 *        Kept so existing callers compile; telemetry no longer uses this.
 */
int send_data_to_stlink(uint8_t type, uint8_t lenght, uint8_t *payload)
{
    Serial_Bridge_Struct *q = &buffer_stlink;

    uint8_t ident = make_identifier(type);
    uint16_t crc = 0xFFFF;

    uint8_t len_low  = (uint8_t)(lenght & 0xFF);
    uint8_t len_high = (uint8_t)((lenght >> 8) & 0xFF);

    crc = crc_update(crc, ident);
    crc = crc_update(crc, len_high);
    crc = crc_update(crc, len_low);

    for (int i = 0; i < lenght; i++) {
        crc = crc_update(crc, payload[i]);
    }

    uint8_t crc_low  = (uint8_t)(crc & 0xFF);
    uint8_t crc_high = (uint8_t)((crc >> 8) & 0xFF);

    uint32_t primask = __get_PRIMASK();
    __disable_irq();

    int open_space = (q->first > q->last)
                     ? (q->first - q->last)
                     : (BRIDGE_RING_SIZE - q->last + q->first);

    if (open_space < lenght + 10) {
        __set_PRIMASK(primask);
        return -1;
    }

    buffer_push(q, ident);
    buffer_push(q, len_high);
    buffer_push(q, len_low);

    for (int i = 0; i < lenght; i++) {
        buffer_push(q, payload[i]);
    }
    buffer_push(q, crc_low);
    buffer_push(q, crc_high);

    kick_tx_if_idle(q);
    __set_PRIMASK(primask);
    return 0;
}

/* --------------------------------------------------------------------------
 * UART callbacks
 * --------------------------------------------------------------------------*/

/* USART1: chamada pelo HAL na metade e no fim do buffer circular (interrupção do DMA) e
 * quando a linha fica ociosa, no fim de um quadro (interrupção da USART). Só quadros v2 do
 * FPGA: nada que chega aqui vira comando.
 *
 * A posição vem do contador do DMA, e não do Size: as duas interrupções podem chegar fora de
 * ordem (um "meio do buffer" atrasado, depois de a linha ociosa já ter passado do meio), e um
 * Size antigo parecia uma volta inteira do buffer, que reentregava 256 bytes velhos (v3:
 * janelas perdidas e repetidas, Qd e Jk subindo). O contador do hardware só anda para frente. */
void HAL_UARTEx_RxEventCallback(UART_HandleTypeDef *huart, uint16_t Size)
{
    (void)Size;
    if (huart->Instance != USART1 || huart->hdmarx == NULL) {
        return;
    }
    uint16_t pos = (uint16_t)(FPGA_RX_DMA_SIZE - __HAL_DMA_GET_COUNTER(huart->hdmarx));
    if (pos >= FPGA_RX_DMA_SIZE) {
        pos = 0u;                            /* contador recarregado: posição 0 */
    }
    if (pos == fpga_rx_old) {
        return;
    }
    if (pos > fpga_rx_old) {
        fpga_rx_feed(fpga_rx_old, pos);
    } else {
        fpga_rx_feed(fpga_rx_old, FPGA_RX_DMA_SIZE);
        fpga_rx_feed(0u, pos);
    }
    fpga_rx_old = pos;
}

void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart)
{
    /* USART1 usa o HAL_UARTEx_RxEventCallback acima. */
    if (huart->Instance == USART2) {
        /* STLink path: primary App ↔ STM32 channel.
         * Process commands and respond on the same port.
         * Active even when FPGA output is off. */
        uint8_t byte = buffer_stlink.receiver;
        Data_Pooling(byte, &message_from_stlink);
        if (Send_Message()) {
            for (int l = 0; l < RESPONSE_BUFFER_SIZE; l++) {
                buffer_push(&buffer_stlink, message_from_stlink.response[l]);
            }
            kick_tx_if_idle(&buffer_stlink);
        }
        HAL_UART_Receive_DMA(buffer_stlink.uart, &buffer_stlink.receiver, 1);
    }
}

void HAL_UART_TxCpltCallback(UART_HandleTypeDef *huart)
{
    Serial_Bridge_Struct *q = NULL;

    if      (huart->Instance == USART1) q = &buffer_fpga;
    else if (huart->Instance == USART2) q = &buffer_stlink;
    else return;

    if (!buffer_is_empty(q)) {
        q->tx_byte = buffer_pop(q);
        HAL_UART_Transmit_DMA(q->uart, &q->tx_byte, 1);
    } else {
        q->tx_in_progress = 0;
    }
}

/*****************************************************************************
 * @brief Inicializa a ponte de comunicação via UART com DMA.
 *
 * @param[in] huart1  UART1 — FPGA path (secondary command channel).
 * @param[in] huart2  UART2 — STLink path (primary App ↔ STM32 channel).
 ******************************************************************************/
void Start_Bridge(UART_HandleTypeDef *huart1, UART_HandleTypeDef *huart2)
{
    Initialize_Message(&message_from_fpga);
    Initialize_Message(&message_from_stlink);

    /* UART1 — FPGA side */
    FPGA_Link_Init();
    buffer_fpga.last           = 0;
    buffer_fpga.first          = 0;
    buffer_fpga.tx_in_progress = 0;
    buffer_fpga.uart           = huart1;
    fpga_rx_start();

    /* UART2 — STLink side (always initialised) */
    if (huart2 != NULL) {
        buffer_stlink.last           = 0;
        buffer_stlink.first          = 0;
        buffer_stlink.tx_in_progress = 0;
        buffer_stlink.uart           = huart2;
        HAL_UART_Receive_DMA(huart2, &buffer_stlink.receiver, 1);
    }
}

void HAL_UART_ErrorCallback(UART_HandleTypeDef *huart)
{
    if (huart->Instance == USART1) {
        __HAL_UART_CLEAR_OREFLAG(huart);
        __HAL_UART_CLEAR_NEFLAG(huart);
        __HAL_UART_CLEAR_FEFLAG(huart);
        FPGA_Link_Uart_Error();
        /* No modo DMA o HAL encerra a recepção em qualquer erro: recomeça. A fila de
         * saída (o STM_HELLO) não é tocada. */
        if (huart->RxState == HAL_UART_STATE_READY) {
            fpga_rx_start();
        }
        return;
    }
    if (huart->Instance == USART2) {
        __HAL_UART_CLEAR_OREFLAG(huart);
        __HAL_UART_CLEAR_NEFLAG(huart);
        __HAL_UART_CLEAR_FEFLAG(huart);
        restart_rx_dma(&buffer_stlink, &message_from_stlink);
    }
}

/**
 * @brief   Permite leitura de dados enviados pela FPGA.
 * @return  Ponteiro para buffer de debug com dados enviados pela FPGA.
 */
uint8_t* Read_Messages_From_FPGA()
{
    return buffer;
}
