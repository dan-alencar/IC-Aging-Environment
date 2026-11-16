/******************************************************************************
 * @file    fpga_link_core.c
 * @brief   Remontagem dos quadros v2 do FPGA e formatação da linha $FPG.
 *          Ver fpga_link_core.h. Sem HAL nem RTOS.
 *****************************************************************************/
#include "fpga_link_core.h"

#include <stdio.h>
#include <string.h>

uint16_t fl_crc16_update(uint16_t crc, uint8_t b)
{
    crc ^= b;
    for (int i = 0; i < 8; i++) {
        crc = (crc & 1u) ? (uint16_t)((crc >> 1) ^ 0xA001u) : (uint16_t)(crc >> 1);
    }
    return crc;
}

uint16_t fl_crc16(const uint8_t *d, uint16_t n)
{
    uint16_t crc = 0xFFFFu;
    for (uint16_t i = 0; i < n; i++) {
        crc = fl_crc16_update(crc, d[i]);
    }
    return crc;
}

void fl_asm_init(fl_asm_t *a)
{
    memset(a, 0, sizeof(*a));
}

uint16_t fl_asm_feed(fl_asm_t *a, uint8_t b, uint32_t now_ms)
{
    if (a->pos != 0u && (uint32_t)(now_ms - a->last_ms) > FL_GAP_MS) {
        a->c.gaps++;                          /* quadro cortado: o resto não vem mais */
        a->pos = 0u;
    }
    a->last_ms = now_ms;

    if (a->pos == 0u) {
        if (b == FL_SYNC0) {
            a->buf[0] = b;
            a->pos = 1u;
        } else {
            a->c.junk++;
        }
        return 0u;
    }
    if (a->pos == 1u) {
        if (b == FL_SYNC1) {
            a->buf[1] = b;
            a->pos = 2u;
            a->crc = 0xFFFFu;
        } else if (b == FL_SYNC0) {
            a->c.junk++;                      /* A5 A5 5A …: o segundo A5 pode ser o início */
        } else {
            a->c.junk += 2u;
            a->pos = 0u;
        }
        return 0u;
    }

    uint16_t i = a->pos;
    a->buf[i] = b;
    a->pos = (uint16_t)(i + 1u);

    if (i < FL_HDR_LEN) {                   /* VER, TYPE, SEQ, LEN */
        a->crc = fl_crc16_update(a->crc, b);
        if (i == FL_HDR_LEN - 1u) {
            if (a->buf[2] != FL_VERSION || b > FL_MAX_PAYLOAD) {
                a->c.hdr_err++;
                a->pos = 0u;
                return 0u;
            }
            a->need = (uint16_t)(FL_HDR_LEN + b + FL_CRC_LEN);
        }
        return 0u;
    }
    if (i < a->need - FL_CRC_LEN) {         /* payload */
        a->crc = fl_crc16_update(a->crc, b);
        return 0u;
    }
    if (a->pos < a->need) {                 /* primeiro byte do CRC */
        return 0u;
    }
    a->pos = 0u;                            /* quadro completo */
    uint16_t rx = (uint16_t)(a->buf[a->need - 2u] | (a->buf[a->need - 1u] << 8));
    if (rx != a->crc) {
        a->c.crc_err++;
        return 0u;
    }
    a->c.frames_ok++;
    return a->need;
}

static int append_checksum(char *out, size_t cap, int len)
{
    uint8_t cs = 0;
    for (int i = 1; i < len; i++) {         /* tudo depois do '$' */
        cs ^= (uint8_t)out[i];
    }
    if ((size_t)len + 4u > cap) {
        return -1;
    }
    int n = snprintf(out + len, cap - (size_t)len, "*%02X", cs);
    return (n == 3) ? len + 3 : -1;
}

int fl_format_line(char *out, size_t cap, const char *kind, const char *payload)
{
    int len = snprintf(out, cap, "$%s,%s", kind, payload);
    if (len <= 0 || (size_t)len >= cap) {
        return -1;
    }
    return append_checksum(out, cap, len);
}

int fl_format_fpg(char *out, size_t cap, uint32_t tick_ms, const fl_counters_t *c,
                  const uint8_t *frame, uint16_t len)
{
    static const char hex[] = "0123456789ABCDEF";
    int n = snprintf(out, cap, "$FPG,Tk,%lu,Ok,%lu,Ce,%lu,He,%lu,Ue,%lu,Qd,%lu,Gp,%lu,Jk,%lu,Hx,",
                     (unsigned long)tick_ms, (unsigned long)c->frames_ok,
                     (unsigned long)c->crc_err, (unsigned long)c->hdr_err,
                     (unsigned long)c->uart_err, (unsigned long)c->queue_drop,
                     (unsigned long)c->gaps, (unsigned long)c->junk);
    if (n <= 0 || (size_t)n + 2u * len + 4u > cap) {
        return -1;
    }
    for (uint16_t i = 0; i < len; i++) {
        out[n++] = hex[frame[i] >> 4];
        out[n++] = hex[frame[i] & 0x0Fu];
    }
    out[n] = '\0';
    return append_checksum(out, cap, n);
}
