/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.h
  * @brief          : Header for main.c file.
  *                   This file contains the common defines of the application.
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2025 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */

/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef __MAIN_H
#define __MAIN_H

#ifdef __cplusplus
extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/
#include "stm32l4xx_hal.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include "cmsis_os.h"
/* USER CODE END Includes */

/* Exported types ------------------------------------------------------------*/
/* USER CODE BEGIN ET */

/* USER CODE END ET */

/* Exported constants --------------------------------------------------------*/
/* USER CODE BEGIN EC */
extern osMutexId_t i2cMutexHandle;
/* USER CODE END EC */

/* Exported macro ------------------------------------------------------------*/
/* USER CODE BEGIN EM */

/* USER CODE END EM */

/* Exported functions prototypes ---------------------------------------------*/
void Error_Handler(void);

/* USER CODE BEGIN EFP */
HAL_StatusTypeDef Clock_Adc_Config(void);   /* v6: PLLSAI1 do ADC com a fonte do PLL principal */
/* USER CODE END EFP */

/* Private defines -----------------------------------------------------------*/
#define BUTTON_P_Pin GPIO_PIN_4
#define BUTTON_P_GPIO_Port GPIOB
#define BUTTON_P_EXTI_IRQn EXTI4_IRQn
#define LED_D_Pin GPIO_PIN_15
#define LED_D_GPIO_Port GPIOA
#define LED_E_Pin GPIO_PIN_0
#define LED_E_GPIO_Port GPIOD

/* USER CODE BEGIN Private defines */
//#define ENABLE_STLINK_DEBUG 1
#define LATCHUP_DELAY  3000   /* ms output stays OFF after a latchup trip   */
#define LATCHUP_SETTLE 5000   /* ms to wait after OUTPUT_Enable before reading iout —
                                 lets inrush / capacitor charge current decay before
                                 deciding whether the latchup has cleared         */
/* USER CODE END Private defines */

#ifdef __cplusplus
}
#endif

#endif /* __MAIN_H */
