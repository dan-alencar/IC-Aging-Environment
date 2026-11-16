/******************************************************************************
 * @file    fpga_link.h
 * @brief   Arquitetura B (04/11/2026): FPGA → STM32 (USART1) → PC (ST-Link).
 *
 *  - FPGA_Link_Rx_Byte(): na interrupção da USART1, remonta os quadros v2 do
 *    FPGA e os põe numa fila (nunca executa nada que venha por essa porta).
 *  - FPGA_Link_Task(): repassa cada quadro numa linha $FPG pela USART2, manda
 *    o STM_HELLO ao FPGA uma vez por segundo (destrava a linha do FPGA para o
 *    STM32, ver stm_hello_gate.v) e o $FWV (versão do firmware) a cada 5 s.
 *****************************************************************************/
#ifndef INC_FPGA_LINK_H_
#define INC_FPGA_LINK_H_

#include <stdint.h>
#include "fpga_link_core.h"

#define HUB_FW_NAME     "hub"
#define HUB_FW_VERSION  "6"
#define HUB_FW_BASE     "361fc39"
#ifndef HUB_FW_BUILD
#define HUB_FW_BUILD    "0"
#endif

/* Fonte do relógio (main.c, v6): "HSE" (cristal de 16 MHz), "MSI" (o cristal não oscilou no
 * boot) ou "MSI-CSS" (o cristal parou com o firmware rodando). Vai no $FWV como Clk. */
extern const char *volatile hub_clk_source;

void FPGA_Link_Init(void);
void FPGA_Link_Rx_Byte(uint8_t b);     /* interrupção da USART1 */
void FPGA_Link_Uart_Error(void);       /* interrupção da USART1 */
void FPGA_Link_Task(void *argument);
void FPGA_Link_Get_Counters(fl_counters_t *out);

#endif /* INC_FPGA_LINK_H_ */
