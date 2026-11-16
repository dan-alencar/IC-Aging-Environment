/*
 * telemetry.c
 *
 *  Created on: Mar 4, 2026
 *      Author: danilo alencar
 */


#include "main.h"
#include "cmsis_os.h"
#include "MYMGM1R.h"
#include "telemetry.h"
#include "protocol.h"
#include "Serial_Bridge.h"
#include "utils.h"
#include <stdio.h>
#include <string.h>

/* ---------------------------------------------------------------------------
 * Arquitetura B: um mutex para tudo o que formata e manda linhas pelo ST-Link.
 * Antes, $TEL (sendTelemetry), $BST/$LEVT (LatchupDetect e a interrupção da UART)
 * usavam o mesmo ctx->buffer sem proteção, e o snprintf com %f do newlib-nano
 * (que usa malloc) rodava em várias tarefas ao mesmo tempo.
 * -------------------------------------------------------------------------*/
extern osMutexId_t txMutexHandle;

static int tel_lock(void)
{
    if (txMutexHandle == NULL || __get_IPSR() != 0u || osKernelGetState() != osKernelRunning) {
        return 0;               /* antes do escalonador (o $BST do boot): uma tarefa só */
    }
    osMutexAcquire(txMutexHandle, osWaitForever);
    return 1;
}

static void tel_unlock(int locked)
{
    if (locked) {
        osMutexRelease(txMutexHandle);
    }
}

void Telemetry_Send_Line(const char *line, uint16_t length)
{
    int locked = tel_lock();
    send_raw_to_stlink((uint8_t *)line, length);
    tel_unlock(locked);
}

float Read_MCU_Temperature(uint32_t raw_temp)
{
	float temp;
	uint32_t raw;

	uint16_t TS_CAL1 = *(TS_CAL1_ADDR);
	uint16_t TS_CAL2 = *(TS_CAL2_ADDR);

	raw = (float)raw_temp * 1.1;
	temp = ((float)raw - (float)TS_CAL1) * 80 / ((float)TS_CAL2 - (float)TS_CAL1) + 30;
	return temp;
}

void Telemetry_Init(Telemetry_Context *ctx,
                   UART_HandleTypeDef *uart,
                   MYMGM1R_Struct *power_ctx,
                   ADC_HandleTypeDef *adc)
{
    if (ctx == NULL) return;

    ctx->uart = uart;
    ctx->power_ctx = power_ctx;
    ctx->adc = adc;
    ctx->enabled = 0;
    ctx->last_send = 0;
    ctx->max_current = INITIAL_MAX_CURRENT;
    ctx->interval_ms = TELEMETRY_INTERVAL_MS;

    memset(&ctx->latest, 0, sizeof(Telemetry_Data));
    memset(ctx->buffer, 0, TELEMETRY_BUFFER_SIZE);
    ctx->latest.output_enabled = 1;
    ctx->latest.latchup_state = 0;
    ctx->latest.trip_count = 0;
    ctx->latest.sequence = 0;
    strcpy(ctx->latest.last_reason, "NONE");
}

void Telemetry_Enable(Telemetry_Context *ctx)
{
    if (ctx == NULL) return;
    ctx->enabled = 1;
    ctx->last_send = HAL_GetTick();
}

void Telemetry_Disable(Telemetry_Context *ctx)
{
    if (ctx == NULL) return;
    ctx->enabled = 0;
}

uint32_t adc_buffer[3];

static uint8_t telemetry_checksum(const char *body)
{
	uint8_t checksum = 0;
	while (*body != '\0') {
		checksum ^= (uint8_t)(*body++);
	}
	return checksum;
}

static void send_ascii_payload(Telemetry_Context *ctx, uint8_t func, const char *prefix, const char *payload)
{
	int len;
	uint8_t checksum;
	(void)func;
	if (ctx == NULL || prefix == NULL || payload == NULL) {
		return;
	}
	len = snprintf((char *)ctx->buffer, sizeof(ctx->buffer), "$%s,%s", prefix, payload);
	if (len <= 0 || len >= (int)sizeof(ctx->buffer) - 6) {
		return;
	}
	checksum = telemetry_checksum((char *)ctx->buffer + 1);
	len += snprintf((char *)ctx->buffer + len, sizeof(ctx->buffer) - len, "*%02X", checksum);
	if (len > 0) {
		send_raw_to_stlink(ctx->buffer, (uint16_t)len);
	}
}

void Telemetry_Set_Output_State(Telemetry_Context *ctx, uint8_t enabled)
{
	if (ctx == NULL) {
		return;
	}
	ctx->latest.output_enabled = enabled ? 1u : 0u;
}

void Telemetry_Send_Board_Status(Telemetry_Context *ctx)
{
	char payload[160];
	if (ctx == NULL) {
		return;
	}
	int locked = tel_lock();
	ctx->latest.sequence += 1u;
	snprintf(
		payload,
		sizeof(payload),
		"Oe,%u,Mc,%.3f,Ls,%u,Tc,%lu,Rs,%s,Sq,%lu",
		ctx->latest.output_enabled,
		ctx->max_current,
		ctx->latest.latchup_state,
		(unsigned long)ctx->latest.trip_count,
		ctx->latest.last_reason,
		(unsigned long)ctx->latest.sequence
	);
	send_ascii_payload(ctx, FUNC_T, "BST", payload);
	tel_unlock(locked);
}

void Telemetry_Report_Latchup_Event(Telemetry_Context *ctx, const char *event_type, const char *reason)
{
	char payload[160];
	const char *safe_reason = (reason != NULL && reason[0] != '\0') ? reason : "NONE";
	const char *safe_type = (event_type != NULL && event_type[0] != '\0') ? event_type : "UNKNOWN";
	if (ctx == NULL) {
		return;
	}
	int locked = tel_lock();
	strncpy(ctx->latest.last_reason, safe_reason, sizeof(ctx->latest.last_reason) - 1u);
	ctx->latest.last_reason[sizeof(ctx->latest.last_reason) - 1u] = '\0';
	ctx->latest.sequence += 1u;
	snprintf(
		payload,
		sizeof(payload),
		"Ts,%lu,Type,%s,Reason,%s,Is,%.3f,Mc,%.3f,Oe,%u,Ls,%u,Tc,%lu,Sq,%lu",
		(unsigned long)HAL_GetTick(),
		safe_type,
		ctx->latest.last_reason,
		ctx->latest.iout,
		ctx->max_current,
		ctx->latest.output_enabled,
		ctx->latest.latchup_state,
		(unsigned long)ctx->latest.trip_count,
		(unsigned long)ctx->latest.sequence
	);
	send_ascii_payload(ctx, FUNC_M, "LEVT", payload);
	tel_unlock(locked);
}

void get_measures(void *argument) {
	Telemetry_Context *Telemetry_ctx = (Telemetry_Context *)argument;
	while(1) {
		if (Telemetry_ctx->power_ctx != NULL) {
			osMutexAcquire(i2cMutexHandle, osWaitForever);

			Telemetry_ctx->latest.ext_temp = MYMGM1R_Read_Temperature(Telemetry_ctx->power_ctx);
			Telemetry_ctx->latest.vin = MYMGM1R_Read_Vin(Telemetry_ctx->power_ctx);
			Telemetry_ctx->latest.vcore = MYMGM1R_Read_Vcore(Telemetry_ctx->power_ctx);
			Telemetry_ctx->latest.iout = MYMGM1R_Read_Iout(Telemetry_ctx->power_ctx);

			osMutexRelease(i2cMutexHandle);
		}

		HAL_ADC_Start(Telemetry_ctx->adc);

		for (int i = 0; i < 3; i++) {
			if (HAL_ADC_PollForConversion(Telemetry_ctx->adc, 10) == HAL_OK) {
				adc_buffer[i] = HAL_ADC_GetValue(Telemetry_ctx->adc);
			}
		}

		HAL_ADC_Stop(Telemetry_ctx->adc);

		Telemetry_ctx->latest.mcu_temp = Read_MCU_Temperature(adc_buffer[0]);

		float v_shunt = (((float)adc_buffer[1] * 3.3) / 4095 - ((float)adc_buffer[2] * 3.3) / 4095);
		/* ADC channels are in inverted order relative to shunt current direction —
		   use absolute value so i_sram is always non-negative regardless of channel polarity. */
		if (v_shunt < 0.0f) v_shunt = -v_shunt;
		Telemetry_ctx->latest.i_sram = v_shunt / (OPAMP_GAIN * R_SHUNT);

		Telemetry_ctx->latest.power_cons = R_SHUNT * Telemetry_ctx->latest.i_sram * Telemetry_ctx->latest.i_sram;

		Telemetry_ctx->max_current = get_max_current();

		osDelay(Telemetry_ctx->interval_ms);
	}
}

void send_telemetry(void *argument) {
	Telemetry_Context *Telemetry_ctx = (Telemetry_Context *)argument;
	while(1) {
		char payload[160];
		int locked = tel_lock();
		Telemetry_ctx->latest.sequence += 1u;
		snprintf(
			payload,
			sizeof(payload),
			"Vc,%.3f,Vi,%.3f,Io,%.3f,Et,%.2f,Mt,%.2f,Is,%.3f,Pc,%.3f,Mc,%.3f,Oe,%u,Ls,%u,Tc,%lu,Rs,%s,Sq,%lu",
			Telemetry_ctx->latest.vcore,
			Telemetry_ctx->latest.vin,
			Telemetry_ctx->latest.iout,
			Telemetry_ctx->latest.ext_temp,
			Telemetry_ctx->latest.mcu_temp,
			Telemetry_ctx->latest.i_sram,
			Telemetry_ctx->latest.power_cons,
			Telemetry_ctx->max_current,
			Telemetry_ctx->latest.output_enabled,
			Telemetry_ctx->latest.latchup_state,
			(unsigned long)Telemetry_ctx->latest.trip_count,
			Telemetry_ctx->latest.last_reason,
			(unsigned long)Telemetry_ctx->latest.sequence
		);
		send_ascii_payload(Telemetry_ctx, FUNC_T, "TEL", payload);
		tel_unlock(locked);
		osDelay(250);
	}
}
