/* Teste no PC do fpga_link_core.c: lê "t_ms byte_hex" por linha (stdin), alimenta o
 * remontador e imprime uma linha $FPG por quadro completo, mais os contadores no fim. */
#include <stdio.h>
#include <stdlib.h>
#include "fpga_link_core.h"

int main(void)
{
    fl_asm_t a;
    fl_asm_init(&a);
    char line[320];
    unsigned long t;
    unsigned b;
    while (scanf("%lu %x", &t, &b) == 2) {
        uint16_t n = fl_asm_feed(&a, (uint8_t)b, (uint32_t)t);
        if (n) {
            int k = fl_format_fpg(line, sizeof(line), (uint32_t)t, &a.c, a.buf, n);
            if (k < 0) { printf("ERRO formatando\n"); return 1; }
            printf("%s\n", line);
        }
    }
    printf("END ok=%lu ce=%lu he=%lu gaps=%lu junk=%lu\n", (unsigned long)a.c.frames_ok,
           (unsigned long)a.c.crc_err, (unsigned long)a.c.hdr_err, (unsigned long)a.c.gaps,
           (unsigned long)a.c.junk);
    return 0;
}
