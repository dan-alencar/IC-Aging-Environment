/*
 * utils.c
 *
 *  Created on: Mar 9, 2026
 *      Author: caio felipe
 */
#include "MYMGM1R.h"
#include "utils.h"
#include "main.h"
#include "telemetry.h"

MYMGM1R_Struct *MYMGM_ctx;
Telemetry_Context *Telemetry_cntx;
uint8_t Page;
float Max_Current;

MYMGM1R_Struct* Get_MYM_ctx()
{
	return MYMGM_ctx;
}

uint8_t *get_page()
{
	return &Page;
}

void change_page(uint8_t new_page)
{
	Page = new_page;
}

inline float get_max_current()
{
	return Max_Current;
}

Telemetry_Context* Get_Telemetry_CTX() {
	return Telemetry_cntx;
}

void change_max_current(float new_max_current)
{
	Max_Current = new_max_current;
}

void Init_Utils(MYMGM1R_Struct *MYMGM1R_ctx,
				Telemetry_Context *Telemetry_ctx)
{

	MYMGM_ctx = MYMGM1R_ctx;
	Page = 1;
	Telemetry_cntx = Telemetry_ctx;
	Max_Current = INITIAL_MAX_CURRENT;
}
