/*
 * utils.h
 *
 *  Created on: Mar 9, 2026
 *      Author: caio felipe
 */

#ifndef INC_UTILS_H_
#define INC_UTILS_H_

#include "telemetry.h"

MYMGM1R_Struct* Get_MYM_ctx();
Telemetry_Context* Get_Telemetry_CTX();

/**
 * @brief   Função para mudar a página do display.
 * @param   new_page Número da nova página que será apresentada no display.
 */
uint8_t *get_page();

/**
 * @brief   Função para mudar a página do display.
 * @param   new_page Número da nova página que será apresentada no display.
 */
void change_page(uint8_t new_page);

float get_max_current();

void change_max_current(float new_max_current);

void Init_Utils(MYMGM1R_Struct *MYMGM1R_ctx,
				Telemetry_Context *Telemetry_ctx);

#endif /* INC_UTILS_H_ */
