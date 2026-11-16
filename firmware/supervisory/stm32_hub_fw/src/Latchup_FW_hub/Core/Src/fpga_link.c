/******************************************************************************
 * @file    fpga_link.c
 * @brief   Arquitetura B: enlace FPGA → STM32 → PC. Ver fpga_link.h.
 *****************************************************************************/
#include "fpga_link.h"

#include <stdio.h>
#include <string.h>

#include "main.h"
#include "cmsis_os.h"
#include "Serial_Bridge.h"
#include "telemetry.h"

#define FL_QUEUE        4u
#define FL_FLAG_FRAME   0x0001u
#define HELLO_PERIOD_MS 1000u
#define FWV_PERIOD_MS   5000u     /* o app espera até 20 s pelo $FWV antes de avisar */

typedef struct {
    uint16_t len;
    uint32_t tick;
    uint8_t  data[FL_MAX_FWD_FRAME];
} fl_slot_t;

static fl_asm_t           s_asm;
static fl_slot_t          s_q[FL_QUEUE];
static volatile uint8_t   s_qw, s_qr;
static volatile osThreadId_t s_task;

void FPGA_Link_Init(void)
{
    fl_asm_init(&s_asm);
    s_qw = s_qr = 0u;
    s_task = NULL;
}

/* Interrupção da USART1 (DMA de 1 byte). Só remonta e enfileira. */
void FPGA_Link_Rx_Byte(uint8_t b)
{
    uint16_t n = fl_asm_feed(&s_asm, b, HAL_GetTick());
    if (n == 0u) {
        return;
    }
    if (n > FL_MAX_FWD_FRAME) {
        s_asm.c.hdr_err++;
        return;
    }
    uint8_t next = (uint8_t)((s_qw + 1u) % FL_QUEUE);
    if (next == s_qr) {
        s_asm.c.queue_drop++;
        return;
    }
    fl_slot_t *slot = &s_q[s_qw];
    slot->len = n;
    slot->tick = HAL_GetTick();
    memcpy(slot->data, s_asm.buf, n);
    s_qw = next;
    if (s_task != NULL) {
        osThreadFlagsSet((osThreadId_t)s_task, FL_FLAG_FRAME);
    }
}

void FPGA_Link_Uart_Error(void)
{
    s_asm.c.uart_err++;
    s_asm.pos = 0u;
}

void FPGA_Link_Get_Counters(fl_counters_t *out)
{
    uint32_t primask = __get_PRIMASK();
    __disable_irq();
    *out = s_asm.c;
    __set_PRIMASK(primask);
}

static void send_fwv(void)
{
    static char payload[128];
    static char line[160];
    const uint32_t *uid = (const uint32_t *)UID_BASE;
    snprintf(payload, sizeof(payload), "Fw,%s,Ver,%s,Base,%s,Build,%s,Uid,%08lX%08lX%08lX,Clk,%s",
             HUB_FW_NAME, HUB_FW_VERSION, HUB_FW_BASE, HUB_FW_BUILD,
             (unsigned long)uid[0], (unsigned long)uid[1], (unsigned long)uid[2], hub_clk_source);
    int n = fl_format_line(line, sizeof(line), "FWV", payload);
    if (n > 0) {
        Telemetry_Send_Line(line, (uint16_t)n);
    }
}

void FPGA_Link_Task(void *argument)
{
    (void)argument;
    static char line[256];
    fl_counters_t c;
    s_task = osThreadGetId();
    uint32_t next_hello = HAL_GetTick();
    uint32_t next_fwv = HAL_GetTick();

    for (;;) {
        uint32_t now = HAL_GetTick();
        if ((int32_t)(now - next_hello) >= 0) {
            Bridge_Send_Hello();
            next_hello = now + HELLO_PERIOD_MS;
        }
        if ((int32_t)(now - next_fwv) >= 0) {
            send_fwv();
            next_fwv = now + FWV_PERIOD_MS;
        }
        while (s_qr != s_qw) {
            fl_slot_t *slot = &s_q[s_qr];
            FPGA_Link_Get_Counters(&c);
            int n = fl_format_fpg(line, sizeof(line), slot->tick, &c, slot->data, slot->len);
            s_qr = (uint8_t)((s_qr + 1u) % FL_QUEUE);
            if (n > 0) {
                Telemetry_Send_Line(line, (uint16_t)n);
            }
        }
        int32_t wait = (int32_t)(next_hello - HAL_GetTick());
        if (wait < 1) {
            wait = 1;
        }
        osThreadFlagsWait(FL_FLAG_FRAME, osFlagsWaitAny, (uint32_t)wait);
    }
}
