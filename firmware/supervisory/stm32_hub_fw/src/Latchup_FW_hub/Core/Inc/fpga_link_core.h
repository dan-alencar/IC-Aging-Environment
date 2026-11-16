/******************************************************************************
 * @file    fpga_link_core.h
 * @brief   Arquitetura B (04/11/2026): parte portátil do enlace FPGA → STM32.
 *
 *          Remonta os quadros do protocolo v2 (PROTOCOL_V2.md do D&T Monitor)
 *          que o FPGA manda pela USART1 e formata a linha de texto que o STM32
 *          repassa ao PC pelo ST-Link:
 *
 *            $FPG,Tk,<ms>,Ok,<n>,Ce,<n>,He,<n>,Ue,<n>,Qd,<n>,Gp,<n>,Jk,<n>,Hx,<quadro em hex>*CS
 *
 *          O quadro vai inteiro e sem alteração no campo Hx: o app decodifica
 *          com o mesmo código que usa para o sniffer do J9. Sem HAL nem RTOS,
 *          para poder ser testado no PC (tests/fw_host).
 *****************************************************************************/
#ifndef INC_FPGA_LINK_CORE_H_
#define INC_FPGA_LINK_CORE_H_

#include <stddef.h>
#include <stdint.h>

#define FL_SYNC0           0xA5u
#define FL_SYNC1           0x5Au
#define FL_VERSION         0x02u
#define FL_HDR_LEN         6u
#define FL_CRC_LEN         2u
#define FL_MAX_PAYLOAD     200u
#define FL_MAX_FRAME       (FL_HDR_LEN + FL_MAX_PAYLOAD + FL_CRC_LEN)
#define FL_MAX_FWD_FRAME   64u      /* maior quadro repassado no $FPG (o FPGA manda 44 e 33) */
/* Mais que isso sem byte no meio de um quadro: recomeça. Desde a v3 os bytes chegam em lotes
 * (meio/fim do buffer do DMA e linha ociosa), e um quadro pode vir em dois lotes separados
 * pela rajada inteira (SENSOR + INFO colados = 77 bytes = 6,2 ms). Com 5 ms (v4), ~0,1 % das
 * janelas se perdiam, todas nas que trazem o FPGA_INFO. O FPGA manda 1 rajada por segundo. */
#define FL_GAP_MS          20u

/* Contadores que vão na linha $FPG */
typedef struct {
    uint32_t frames_ok;    /* Ok: quadros com CRC certo */
    uint32_t crc_err;      /* Ce: CRC errado */
    uint32_t hdr_err;      /* He: VER ou LEN inválidos, ou quadro grande demais para repassar */
    uint32_t uart_err;     /* Ue: erros da USART1 (ruído, framing, overrun) */
    uint32_t queue_drop;   /* Qd: fila cheia entre a interrupção e a tarefa */
    uint32_t gaps;         /* Gp: quadros cortados por FL_GAP_MS sem byte (bytes perdidos) */
    uint32_t junk;         /* Jk: bytes descartados fora de quadro */
} fl_counters_t;

typedef struct {
    uint8_t  buf[FL_MAX_FRAME];
    uint16_t pos;          /* bytes já guardados do quadro atual */
    uint16_t need;         /* tamanho total esperado (depois do cabeçalho) */
    uint16_t crc;
    uint32_t last_ms;
    fl_counters_t c;
} fl_asm_t;

uint16_t fl_crc16_update(uint16_t crc, uint8_t b);
uint16_t fl_crc16(const uint8_t *d, uint16_t n);

void fl_asm_init(fl_asm_t *a);

/* Um byte da USART1. Devolve o tamanho do quadro quando a->buf tem um quadro
 * completo e com CRC certo (o chamador copia antes do próximo byte), senão 0. */
uint16_t fl_asm_feed(fl_asm_t *a, uint8_t b, uint32_t now_ms);

/* "$KIND,payload*CS" sem CRLF (checksum XOR de tudo entre '$' e '*', como no $TEL).
 * Devolve o tamanho, ou -1 se não couber. */
int fl_format_line(char *out, size_t cap, const char *kind, const char *payload);

/* Linha $FPG de um quadro. Devolve o tamanho, ou -1 se não couber. */
int fl_format_fpg(char *out, size_t cap, uint32_t tick_ms, const fl_counters_t *c,
                  const uint8_t *frame, uint16_t len);

#endif /* INC_FPGA_LINK_CORE_H_ */
