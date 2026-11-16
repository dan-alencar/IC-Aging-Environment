/******************************************************************************
 * @file    IHM.h
 * @brief   Interface para regulação e controle do display SSD_1306_128x32.
 *
 *          Define comandos, protótipos de função e constantes utilizadas
 *          pelo arquivo de implementação IHM.c para controle do display.
 *
 * @author  Caio Felipe
 * @date    27 jun 2025
 *
 * @note    Essa biblioteca foi escrita para a família STM32L4, o cálculo
 *          da temperatura segue os métodos especificados no datasheet do
 *          microcontrolador.
 *****************************************************************************/

#ifndef INC_IHM_H_
#define INC_IHM_H_

#include "stm32l4xx_hal.h"
#include "MYMGM1R.h"
#include "TPS65400.h"
#include "telemetry.h"

/* --------------------------------------------------------------------------
 * Constantes e macros
 * --------------------------------------------------------------------------*/

/** @brief Tamanho do buffer das filas que formam os gráficos de tensão, corrente e temperatura do core. */
#define QUEUE_SIZE 90

#define MEAN_WINDOW 15

/* --------------------------------------------------------------------------
 * Estruturas de dados
 * --------------------------------------------------------------------------*/
/**
 * @struct Queue
 * @brief Estrutura de fila para cálculo da média de correntes.
 */
typedef struct {
	float rx_buffer[QUEUE_SIZE];
	uint8_t last;
	uint8_t first;
	uint8_t qnt;
} Queue;

/* --------------------------------------------------------------------------
 * Protótipos de função pública
 * --------------------------------------------------------------------------*/

/**
 * @brief   Função para mudar a tensão Vcore.
 * @param   new_Vcore Novo valor de tensão que será utilizado.
 */
void change_Vcore(MYMGM1R_Struct *MYMGM1R_ctx, uint8_t new_Vcore);

/**
 * @brief   Inicializa e configura o display enquanto o código é carregado na FPGA.
 */
void OLED_Init(void);

/**
 * @brief   Exibe status no display, como tensões e temperaturas.
 * @param   MYMGM1_ctx Ponteiro para contexto de uma estrutura de uma fonte.
 * @param   hadc1 Ponteiro para adc previamente configurado.
 */
void Show_Stats(MYMGM1R_Struct *MYMGM1_ctx, Telemetry_Context *Telemetry_ctx, ADC_HandleTypeDef *hadc1);


#endif /* INC_IHM_H_ */
