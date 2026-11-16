/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
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
/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "cmsis_os.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include "IHM.h"
#include "Serial_Bridge.h"
#include "TPS65400.h"
#include "MYMGM1R.h"
#include "telemetry.h"
#include "utils.h"
#include "protocol.h"
#include "fpga_link.h"

/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */

/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/
ADC_HandleTypeDef hadc1;

I2C_HandleTypeDef hi2c1;
I2C_HandleTypeDef hi2c2;

OPAMP_HandleTypeDef hopamp1;
OPAMP_HandleTypeDef hopamp2;

RTC_HandleTypeDef hrtc;

UART_HandleTypeDef huart1;
UART_HandleTypeDef huart2;
DMA_HandleTypeDef hdma_usart1_rx;
DMA_HandleTypeDef hdma_usart1_tx;
DMA_HandleTypeDef hdma_usart2_rx;
DMA_HandleTypeDef hdma_usart2_tx;

/* Definitions for defaultTask */
osThreadId_t defaultTaskHandle;
const osThreadAttr_t defaultTask_attributes = {
  .name = "defaultTask",
  .stack_size = 512 * 4,
  .priority = (osPriority_t) osPriorityNormal,
};
/* Definitions for sendTelemetry */
osThreadId_t sendTelemetryHandle;
const osThreadAttr_t sendTelemetry_attributes = {
  .name = "sendTelemetry",
  .stack_size = 512 * 4,
  .priority = (osPriority_t) osPriorityNormal,
};
/* Definitions for getMeasures */
osThreadId_t getMeasuresHandle;
const osThreadAttr_t getMeasures_attributes = {
  .name = "getMeasures",
  .stack_size = 512 * 4,
  .priority = (osPriority_t) osPriorityNormal,
};
/* Definitions for LatchupDetect */
osThreadId_t LatchupDetectHandle;
const osThreadAttr_t LatchupDetect_attributes = {
  .name = "LatchupDetect",
  .stack_size = 256 * 4,
  .priority = (osPriority_t) osPriorityNormal,
};
/* Definitions for i2cMutex */
osMutexId_t i2cMutexHandle;
const osMutexAttr_t i2cMutex_attributes = {
  .name = "i2cMutex"
};
/* Definitions for LatchupDetecSem */
osSemaphoreId_t LatchupDetecSemHandle;
const osSemaphoreAttr_t LatchupDetecSem_attributes = {
  .name = "LatchupDetecSem"
};
/* USER CODE BEGIN PV */

/* Arquitetura B (04/11/2026) ------------------------------------------------
 * txMutex: uma linha por vez no ST-Link ($TEL, $BST, $LEVT, $FPG, $FWV).
 * cmdTask: aplica os comandos do ST-Link fora da interrupção (protocol.c).
 * fpgaLink: repassa os quadros do FPGA ($FPG) e manda o STM_HELLO (fpga_link.c).
 * HUB_OLED = 0: a tarefa padrão não desenha mais no OLED (o OLED_Init já estava
 * comentado no 361fc39); assim ela não usa sprintf com %f nem o I2C2. */
#ifndef HUB_OLED
#define HUB_OLED 0
#endif
osMutexId_t txMutexHandle;
const osMutexAttr_t txMutex_attributes = {
  .name = "txMutex"
};
osThreadId_t cmdTaskHandle;
const osThreadAttr_t cmdTask_attributes = {
  .name = "cmdTask",
  .stack_size = 512 * 4,
  .priority = (osPriority_t) osPriorityNormal,
};
osThreadId_t fpgaLinkHandle;
const osThreadAttr_t fpgaLink_attributes = {
  .name = "fpgaLink",
  .stack_size = 512 * 4,
  .priority = (osPriority_t) osPriorityNormal,
};

MYMGM1R_Struct MYMGM1_ctx;
Telemetry_Context Telemetry_ctx;
TPS65400_Struct TPS65400_ctx;
HAL_StatusTypeDef HAL_Status = HAL_TIMEOUT;
uint8_t init = 1;
/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_DMA_Init(void);
static void MX_I2C1_Init(void);
static void MX_I2C2_Init(void);
static void MX_ADC1_Init(void);
static void MX_RTC_Init(void);
static void MX_USART1_UART_Init(void);
static void MX_USART2_UART_Init(void);
static void MX_OPAMP1_Init(void);
static void MX_OPAMP2_Init(void);
void StartDefaultTask(void *argument);
extern void send_telemetry(void *argument);
extern void get_measures(void *argument);
void LatchupProtection(void *argument);

/* USER CODE BEGIN PFP */

void OLED_Init(void);

/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */
void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin)
{
    if (GPIO_Pin == BUTTON_P_Pin)
    {
		uint8_t page = *(get_page());
		if (page == 6) {
			change_page(1);
		}
		else {
			change_page(page+1);
		}
    }
}

void HAL_ADC_LevelOutOfWindowCallback(ADC_HandleTypeDef *hadc) {
	if (hadc->Instance == ADC1) {
		/* Do NOT call MYMGM1R_OUTPUT_Disable here: I2C HAL must not be called
		 * from an ISR context and no mutex is held.  LatchupProtection polls
		 * i_sram every 10 ms and will perform the disable + LEVT + BST correctly. */
		osSemaphoreRelease(LatchupDetecSemHandle);
	}
}

/* v6 (06/11/2026): relógio pelo cristal de 16 MHz (HSE) em vez do MSI (RC interno). Na run de
 * 05–06/11, com o STM32 acima de ~80 °C, o MSI desviou e a USART2 (STM32 → ST-Link → PC) errou
 * (placa B: 745 janelas perdidas). HSE / 4 = 4 MHz, a mesma entrada que o MSI dava ao PLL: 120 MHz
 * e todos os divisores iguais. Sem o cristal no boot, volta ao MSI de antes. Com o CSS, se o
 * cristal parar com o firmware rodando, o hardware passa o SYSCLK ao MSI (4 MHz) e a tarefa padrão
 * refaz os 120 MHz pelo MSI. O ADC (proteção de latch-up) usa o PLLSAI1, que tem de seguir a fonte
 * do PLL principal (o HAL recusa fontes diferentes). */
const char *volatile hub_clk_source = "MSI";
static volatile uint8_t s_clk_css_event = 0;

static HAL_StatusTypeDef Clock_Pll_120MHz(uint32_t source)
{
  RCC_OscInitTypeDef osc = {0};
  osc.OscillatorType = RCC_OSCILLATORTYPE_LSI | RCC_OSCILLATORTYPE_MSI;
  osc.LSIState = RCC_LSI_ON;
  osc.MSIState = RCC_MSI_ON;
  osc.MSICalibrationValue = 0;
  osc.MSIClockRange = RCC_MSIRANGE_6;              /* 4 MHz */
  if (source == RCC_PLLSOURCE_HSE) {
    osc.OscillatorType |= RCC_OSCILLATORTYPE_HSE;
    osc.HSEState = RCC_HSE_ON;
  }
  osc.PLL.PLLState = RCC_PLL_ON;
  osc.PLL.PLLSource = source;
  osc.PLL.PLLM = (source == RCC_PLLSOURCE_HSE) ? 4 : 1;   /* 4 MHz na entrada do PLL */
  osc.PLL.PLLN = 60;
  osc.PLL.PLLP = RCC_PLLP_DIV2;
  osc.PLL.PLLQ = RCC_PLLQ_DIV2;
  osc.PLL.PLLR = RCC_PLLR_DIV2;
  return HAL_RCC_OscConfig(&osc);
}

static HAL_StatusTypeDef Clock_Sys_From_Pll(void)
{
  RCC_ClkInitTypeDef clk = {0};
  clk.ClockType = RCC_CLOCKTYPE_HCLK | RCC_CLOCKTYPE_SYSCLK | RCC_CLOCKTYPE_PCLK1 | RCC_CLOCKTYPE_PCLK2;
  clk.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  clk.AHBCLKDivider = RCC_SYSCLK_DIV1;
  clk.APB1CLKDivider = RCC_HCLK_DIV1;
  clk.APB2CLKDivider = RCC_HCLK_DIV1;
  return HAL_RCC_ClockConfig(&clk, FLASH_LATENCY_5);
}

/* ADC1 pelo PLLSAI1 a 32 MHz, com a mesma fonte do PLL principal (chamado no HAL_ADC_MspInit). */
HAL_StatusTypeDef Clock_Adc_Config(void)
{
  RCC_PeriphCLKInitTypeDef p = {0};
  p.PeriphClockSelection = RCC_PERIPHCLK_ADC;
  p.AdcClockSelection = RCC_ADCCLKSOURCE_PLLSAI1;
  p.PLLSAI1.PLLSAI1Source = __HAL_RCC_GET_PLL_OSCSOURCE();
  p.PLLSAI1.PLLSAI1M = (p.PLLSAI1.PLLSAI1Source == RCC_PLLSOURCE_HSE) ? 4 : 1;
  p.PLLSAI1.PLLSAI1N = 16;
  p.PLLSAI1.PLLSAI1P = RCC_PLLP_DIV2;
  p.PLLSAI1.PLLSAI1Q = RCC_PLLQ_DIV2;
  p.PLLSAI1.PLLSAI1R = RCC_PLLR_DIV2;
  p.PLLSAI1.PLLSAI1ClockOut = RCC_PLLSAI1_ADC1CLK;
  return HAL_RCCEx_PeriphCLKConfig(&p);
}

/* NMI do CSS: o cristal parou. O hardware já passou o SYSCLK ao MSI e desligou o PLL. */
void HAL_RCC_CSSCallback(void)
{
  hub_clk_source = "MSI-CSS";
  s_clk_css_event = 1;
}

/* Na tarefa padrão, fora da interrupção: 120 MHz de novo, agora pelo MSI. */
static void Clock_Css_Recover(void)
{
  __HAL_RCC_HSE_CONFIG(RCC_HSE_OFF);
  /* o HAL não muda o PLL principal com o PLLSAI1 ligado (a fonte é a mesma): desliga o do ADC antes */
  __HAL_RCC_PLLSAI1_DISABLE();
  uint32_t t0 = HAL_GetTick();
  while (READ_BIT(RCC->CR, RCC_CR_PLLSAI1RDY) != 0U && HAL_GetTick() - t0 < 10U) { }
  if (Clock_Pll_120MHz(RCC_PLLSOURCE_MSI) == HAL_OK && Clock_Sys_From_Pll() == HAL_OK) {
    (void)Clock_Adc_Config();
  }
}
/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{

  /* USER CODE BEGIN 1 */

  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_DMA_Init();
  MX_I2C1_Init();
  MX_I2C2_Init();
  MX_ADC1_Init();
  MX_RTC_Init();
  MX_USART1_UART_Init();
  MX_USART2_UART_Init();
  MX_OPAMP1_Init();
  MX_OPAMP2_Init();
  /* USER CODE BEGIN 2 */
  MYMGM1R_Init(&hi2c1, &MYMGM1_ctx);

  HAL_ADCEx_Calibration_Start(&hadc1, ADC_SINGLE_ENDED);

  HAL_OPAMP_Start(&hopamp1);
  HAL_OPAMP_Start(&hopamp2);


  //OLED_Init();

  Telemetry_Init(&Telemetry_ctx, &huart1, &MYMGM1_ctx, &hadc1);
  Telemetry_Enable(&Telemetry_ctx);
  Telemetry_Set_Output_State(&Telemetry_ctx, 1u);

  Start_Bridge(&huart1, &huart2);

  Init_Utils(&MYMGM1_ctx, &Telemetry_ctx);

  /* Emit startup $BST so the host knows the initial board state on connect. */
  Telemetry_Send_Board_Status(&Telemetry_ctx);

  /* USER CODE END 2 */

  /* Init scheduler */
  osKernelInitialize();
  /* Create the mutex(es) */
  /* creation of i2cMutex */
  i2cMutexHandle = osMutexNew(&i2cMutex_attributes);

  /* USER CODE BEGIN RTOS_MUTEX */
  /* add mutexes, ... */
  txMutexHandle = osMutexNew(&txMutex_attributes);
  /* USER CODE END RTOS_MUTEX */

  /* Create the semaphores(s) */
  /* creation of LatchupDetecSem */
  LatchupDetecSemHandle = osSemaphoreNew(1, 0, &LatchupDetecSem_attributes);

  /* USER CODE BEGIN RTOS_SEMAPHORES */
  /* add semaphores, ... */
  /* USER CODE END RTOS_SEMAPHORES */

  /* USER CODE BEGIN RTOS_TIMERS */
  /* start timers, add new ones, ... */
  /* USER CODE END RTOS_TIMERS */

  /* USER CODE BEGIN RTOS_QUEUES */
  /* add queues, ... */
  /* USER CODE END RTOS_QUEUES */

  /* Create the thread(s) */
  /* creation of defaultTask */
  defaultTaskHandle = osThreadNew(StartDefaultTask, NULL, &defaultTask_attributes);

  /* creation of sendTelemetry */
  sendTelemetryHandle = osThreadNew(send_telemetry, (void*) &Telemetry_ctx, &sendTelemetry_attributes);

  /* creation of getMeasures */
  getMeasuresHandle = osThreadNew(get_measures, (void*) &Telemetry_ctx, &getMeasures_attributes);

  /* creation of LatchupDetect */
  LatchupDetectHandle = osThreadNew(LatchupProtection, NULL, &LatchupDetect_attributes);

  /* USER CODE BEGIN RTOS_THREADS */
  /* add threads, ... */
  cmdTaskHandle = osThreadNew(Command_Task, NULL, &cmdTask_attributes);
  fpgaLinkHandle = osThreadNew(FPGA_Link_Task, NULL, &fpgaLink_attributes);
  /* USER CODE END RTOS_THREADS */

  /* USER CODE BEGIN RTOS_EVENTS */
  /* add events, ... */
  /* USER CODE END RTOS_EVENTS */

  /* Start scheduler */
  osKernelStart();

  /* We should never get here as control is now taken by the scheduler */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */


  while (1)
  {



//	  MYMGM1R_OUTPUT_Disable(&MYMGM1_ctx);
//
//	  HAL_Delay(200);


//	  MYMGM1R_Set_Vcore(&MYMGM1_ctx,  V_FPGA);


//	  HAL_GPIO_TogglePin(GPIOB, GPIO_PIN_6);
//	  HAL_Delay(100);
    /* USER CODE END WHILE */

    /* USER CODE BEGIN 3 */
  }
  /* USER CODE END 3 */
}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  /** Configure the main internal regulator output voltage
  */
  if (HAL_PWREx_ControlVoltageScaling(PWR_REGULATOR_VOLTAGE_SCALE1_BOOST) != HAL_OK)
  {
    Error_Handler();
  }

  /* v6: cristal de 16 MHz primeiro; se ele não oscilar (HSERDY em 100 ms), o MSI de antes.
     Ver Clock_Pll_120MHz no USER CODE 0. */
  if (Clock_Pll_120MHz(RCC_PLLSOURCE_HSE) == HAL_OK)
  {
    hub_clk_source = "HSE";
  }
  else
  {
    __HAL_RCC_HSE_CONFIG(RCC_HSE_OFF);
    if (Clock_Pll_120MHz(RCC_PLLSOURCE_MSI) != HAL_OK)
    {
      Error_Handler();
    }
    hub_clk_source = "MSI";
  }

  if (Clock_Sys_From_Pll() != HAL_OK)
  {
    Error_Handler();
  }

  if (hub_clk_source[0] == 'H')
  {
    HAL_RCC_EnableCSS();     /* cristal parou → NMI → HAL_RCC_CSSCallback */
  }
}

/**
  * @brief ADC1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_ADC1_Init(void)
{

  /* USER CODE BEGIN ADC1_Init 0 */

  /* USER CODE END ADC1_Init 0 */

  ADC_ChannelConfTypeDef sConfig = {0};

  /* USER CODE BEGIN ADC1_Init 1 */

  /* USER CODE END ADC1_Init 1 */

  /** Common config
  */
  hadc1.Instance = ADC1;
  hadc1.Init.ClockPrescaler = ADC_CLOCK_ASYNC_DIV1;
  hadc1.Init.Resolution = ADC_RESOLUTION_12B;
  hadc1.Init.DataAlign = ADC_DATAALIGN_RIGHT;
  hadc1.Init.ScanConvMode = ADC_SCAN_ENABLE;
  hadc1.Init.EOCSelection = ADC_EOC_SINGLE_CONV;
  hadc1.Init.LowPowerAutoWait = DISABLE;
  hadc1.Init.ContinuousConvMode = DISABLE;
  hadc1.Init.NbrOfConversion = 3;
  hadc1.Init.DiscontinuousConvMode = DISABLE;
  hadc1.Init.ExternalTrigConv = ADC_SOFTWARE_START;
  hadc1.Init.ExternalTrigConvEdge = ADC_EXTERNALTRIGCONVEDGE_NONE;
  hadc1.Init.DMAContinuousRequests = DISABLE;
  hadc1.Init.Overrun = ADC_OVR_DATA_PRESERVED;
  hadc1.Init.OversamplingMode = DISABLE;
  if (HAL_ADC_Init(&hadc1) != HAL_OK)
  {
    Error_Handler();
  }

  /** Configure Regular Channel
  */
  sConfig.Channel = ADC_CHANNEL_TEMPSENSOR;
  sConfig.Rank = ADC_REGULAR_RANK_1;
  sConfig.SamplingTime = ADC_SAMPLETIME_640CYCLES_5;
  sConfig.SingleDiff = ADC_SINGLE_ENDED;
  sConfig.OffsetNumber = ADC_OFFSET_NONE;
  sConfig.Offset = 0;
  if (HAL_ADC_ConfigChannel(&hadc1, &sConfig) != HAL_OK)
  {
    Error_Handler();
  }

  /** Configure Regular Channel
  */
  sConfig.Channel = ADC_CHANNEL_8;
  sConfig.Rank = ADC_REGULAR_RANK_2;
  if (HAL_ADC_ConfigChannel(&hadc1, &sConfig) != HAL_OK)
  {
    Error_Handler();
  }

  /** Configure Regular Channel
  */
  sConfig.Channel = ADC_CHANNEL_15;
  sConfig.Rank = ADC_REGULAR_RANK_3;
  if (HAL_ADC_ConfigChannel(&hadc1, &sConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN ADC1_Init 2 */

  /* USER CODE END ADC1_Init 2 */

}

/**
  * @brief I2C1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_I2C1_Init(void)
{

  /* USER CODE BEGIN I2C1_Init 0 */

  /* USER CODE END I2C1_Init 0 */

  /* USER CODE BEGIN I2C1_Init 1 */

  /* USER CODE END I2C1_Init 1 */
  hi2c1.Instance = I2C1;
  hi2c1.Init.Timing = 0x10820B75;
  hi2c1.Init.OwnAddress1 = 0;
  hi2c1.Init.AddressingMode = I2C_ADDRESSINGMODE_7BIT;
  hi2c1.Init.DualAddressMode = I2C_DUALADDRESS_DISABLE;
  hi2c1.Init.OwnAddress2 = 0;
  hi2c1.Init.OwnAddress2Masks = I2C_OA2_NOMASK;
  hi2c1.Init.GeneralCallMode = I2C_GENERALCALL_DISABLE;
  hi2c1.Init.NoStretchMode = I2C_NOSTRETCH_DISABLE;
  if (HAL_I2C_Init(&hi2c1) != HAL_OK)
  {
    Error_Handler();
  }

  /** Configure Analogue filter
  */
  if (HAL_I2CEx_ConfigAnalogFilter(&hi2c1, I2C_ANALOGFILTER_ENABLE) != HAL_OK)
  {
    Error_Handler();
  }

  /** Configure Digital filter
  */
  if (HAL_I2CEx_ConfigDigitalFilter(&hi2c1, 0) != HAL_OK)
  {
    Error_Handler();
  }

  /** I2C Fast mode Plus enable
  */
  HAL_I2CEx_EnableFastModePlus(I2C_FASTMODEPLUS_I2C1);
  /* USER CODE BEGIN I2C1_Init 2 */

  /* USER CODE END I2C1_Init 2 */

}

/**
  * @brief I2C2 Initialization Function
  * @param None
  * @retval None
  */
static void MX_I2C2_Init(void)
{

  /* USER CODE BEGIN I2C2_Init 0 */

  /* USER CODE END I2C2_Init 0 */

  /* USER CODE BEGIN I2C2_Init 1 */

  /* USER CODE END I2C2_Init 1 */
  hi2c2.Instance = I2C2;
  hi2c2.Init.Timing = 0x10820B75;
  hi2c2.Init.OwnAddress1 = 0;
  hi2c2.Init.AddressingMode = I2C_ADDRESSINGMODE_7BIT;
  hi2c2.Init.DualAddressMode = I2C_DUALADDRESS_DISABLE;
  hi2c2.Init.OwnAddress2 = 0;
  hi2c2.Init.OwnAddress2Masks = I2C_OA2_NOMASK;
  hi2c2.Init.GeneralCallMode = I2C_GENERALCALL_DISABLE;
  hi2c2.Init.NoStretchMode = I2C_NOSTRETCH_DISABLE;
  if (HAL_I2C_Init(&hi2c2) != HAL_OK)
  {
    Error_Handler();
  }

  /** Configure Analogue filter
  */
  if (HAL_I2CEx_ConfigAnalogFilter(&hi2c2, I2C_ANALOGFILTER_ENABLE) != HAL_OK)
  {
    Error_Handler();
  }

  /** Configure Digital filter
  */
  if (HAL_I2CEx_ConfigDigitalFilter(&hi2c2, 0) != HAL_OK)
  {
    Error_Handler();
  }

  /** I2C Fast mode Plus enable
  */
  HAL_I2CEx_EnableFastModePlus(I2C_FASTMODEPLUS_I2C2);
  /* USER CODE BEGIN I2C2_Init 2 */

  /* USER CODE END I2C2_Init 2 */

}

/**
  * @brief OPAMP1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_OPAMP1_Init(void)
{

  /* USER CODE BEGIN OPAMP1_Init 0 */

  /* USER CODE END OPAMP1_Init 0 */

  /* USER CODE BEGIN OPAMP1_Init 1 */

  /* USER CODE END OPAMP1_Init 1 */
  hopamp1.Instance = OPAMP1;
  hopamp1.Init.PowerSupplyRange = OPAMP_POWERSUPPLY_HIGH;
  hopamp1.Init.Mode = OPAMP_PGA_MODE;
  hopamp1.Init.NonInvertingInput = OPAMP_NONINVERTINGINPUT_IO0;
  hopamp1.Init.InvertingInput = OPAMP_INVERTINGINPUT_CONNECT_NO;
  hopamp1.Init.PgaGain = OPAMP_PGA_GAIN_2;
  hopamp1.Init.PowerMode = OPAMP_POWERMODE_NORMALPOWER;
  hopamp1.Init.UserTrimming = OPAMP_TRIMMING_USER;
  if (HAL_OPAMP_Init(&hopamp1) != HAL_OK)
  {
    Error_Handler();
  }
  if (HAL_OPAMP_SelfCalibrate(&hopamp1) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN OPAMP1_Init 2 */

  /* USER CODE END OPAMP1_Init 2 */

}

/**
  * @brief OPAMP2 Initialization Function
  * @param None
  * @retval None
  */
static void MX_OPAMP2_Init(void)
{

  /* USER CODE BEGIN OPAMP2_Init 0 */

  /* USER CODE END OPAMP2_Init 0 */

  /* USER CODE BEGIN OPAMP2_Init 1 */

  /* USER CODE END OPAMP2_Init 1 */
  hopamp2.Instance = OPAMP2;
  hopamp2.Init.PowerSupplyRange = OPAMP_POWERSUPPLY_HIGH;
  hopamp2.Init.Mode = OPAMP_PGA_MODE;
  hopamp2.Init.NonInvertingInput = OPAMP_NONINVERTINGINPUT_IO0;
  hopamp2.Init.InvertingInput = OPAMP_INVERTINGINPUT_CONNECT_NO;
  hopamp2.Init.PgaGain = OPAMP_PGA_GAIN_2;
  hopamp2.Init.PowerMode = OPAMP_POWERMODE_NORMALPOWER;
  hopamp2.Init.UserTrimming = OPAMP_TRIMMING_USER;
  if (HAL_OPAMP_Init(&hopamp2) != HAL_OK)
  {
    Error_Handler();
  }
  if (HAL_OPAMP_SelfCalibrate(&hopamp2) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN OPAMP2_Init 2 */

  /* USER CODE END OPAMP2_Init 2 */

}

/**
  * @brief RTC Initialization Function
  * @param None
  * @retval None
  */
static void MX_RTC_Init(void)
{

  /* USER CODE BEGIN RTC_Init 0 */

  /* USER CODE END RTC_Init 0 */

  /* USER CODE BEGIN RTC_Init 1 */

  /* USER CODE END RTC_Init 1 */

  /** Initialize RTC Only
  */
  hrtc.Instance = RTC;
  hrtc.Init.HourFormat = RTC_HOURFORMAT_24;
  hrtc.Init.AsynchPrediv = 127;
  hrtc.Init.SynchPrediv = 255;
  hrtc.Init.OutPut = RTC_OUTPUT_DISABLE;
  hrtc.Init.OutPutRemap = RTC_OUTPUT_REMAP_NONE;
  hrtc.Init.OutPutPolarity = RTC_OUTPUT_POLARITY_HIGH;
  hrtc.Init.OutPutType = RTC_OUTPUT_TYPE_OPENDRAIN;
  if (HAL_RTC_Init(&hrtc) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN RTC_Init 2 */

  /* USER CODE END RTC_Init 2 */

}

/**
  * @brief USART1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_USART1_UART_Init(void)
{

  /* USER CODE BEGIN USART1_Init 0 */

  /* USER CODE END USART1_Init 0 */

  /* USER CODE BEGIN USART1_Init 1 */

  /* USER CODE END USART1_Init 1 */
  huart1.Instance = USART1;
  huart1.Init.BaudRate = 125000;
  huart1.Init.WordLength = UART_WORDLENGTH_8B;
  huart1.Init.StopBits = UART_STOPBITS_1;
  huart1.Init.Parity = UART_PARITY_NONE;
  huart1.Init.Mode = UART_MODE_TX_RX;
  huart1.Init.HwFlowCtl = UART_HWCONTROL_NONE;
  huart1.Init.OverSampling = UART_OVERSAMPLING_16;
  huart1.Init.OneBitSampling = UART_ONE_BIT_SAMPLE_DISABLE;
  huart1.Init.ClockPrescaler = UART_PRESCALER_DIV1;
  huart1.AdvancedInit.AdvFeatureInit = UART_ADVFEATURE_NO_INIT;
  if (HAL_UART_Init(&huart1) != HAL_OK)
  {
    Error_Handler();
  }
  if (HAL_UARTEx_SetTxFifoThreshold(&huart1, UART_TXFIFO_THRESHOLD_1_8) != HAL_OK)
  {
    Error_Handler();
  }
  if (HAL_UARTEx_SetRxFifoThreshold(&huart1, UART_RXFIFO_THRESHOLD_1_8) != HAL_OK)
  {
    Error_Handler();
  }
  if (HAL_UARTEx_DisableFifoMode(&huart1) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN USART1_Init 2 */

  /* USER CODE END USART1_Init 2 */

}

/**
  * @brief USART2 Initialization Function
  * @param None
  * @retval None
  */
static void MX_USART2_UART_Init(void)
{

  /* USER CODE BEGIN USART2_Init 0 */

  /* USER CODE END USART2_Init 0 */

  /* USER CODE BEGIN USART2_Init 1 */

  /* USER CODE END USART2_Init 1 */
  huart2.Instance = USART2;
  huart2.Init.BaudRate = 125000;
  huart2.Init.WordLength = UART_WORDLENGTH_8B;
  huart2.Init.StopBits = UART_STOPBITS_1;
  huart2.Init.Parity = UART_PARITY_NONE;
  huart2.Init.Mode = UART_MODE_TX_RX;
  huart2.Init.HwFlowCtl = UART_HWCONTROL_NONE;
  huart2.Init.OverSampling = UART_OVERSAMPLING_16;
  huart2.Init.OneBitSampling = UART_ONE_BIT_SAMPLE_DISABLE;
  huart2.Init.ClockPrescaler = UART_PRESCALER_DIV1;
  huart2.AdvancedInit.AdvFeatureInit = UART_ADVFEATURE_NO_INIT;
  if (HAL_UART_Init(&huart2) != HAL_OK)
  {
    Error_Handler();
  }
  if (HAL_UARTEx_SetTxFifoThreshold(&huart2, UART_TXFIFO_THRESHOLD_1_8) != HAL_OK)
  {
    Error_Handler();
  }
  if (HAL_UARTEx_SetRxFifoThreshold(&huart2, UART_RXFIFO_THRESHOLD_1_8) != HAL_OK)
  {
    Error_Handler();
  }
  if (HAL_UARTEx_DisableFifoMode(&huart2) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN USART2_Init 2 */

  /* USER CODE END USART2_Init 2 */

}

/**
  * Enable DMA controller clock
  */
static void MX_DMA_Init(void)
{

  /* DMA controller clock enable */
  __HAL_RCC_DMAMUX1_CLK_ENABLE();
  __HAL_RCC_DMA1_CLK_ENABLE();
  __HAL_RCC_DMA2_CLK_ENABLE();

  /* DMA interrupt init */
  /* DMA1_Channel1_IRQn interrupt configuration */
  HAL_NVIC_SetPriority(DMA1_Channel1_IRQn, 5, 0);
  HAL_NVIC_EnableIRQ(DMA1_Channel1_IRQn);
  /* DMA1_Channel2_IRQn interrupt configuration */
  HAL_NVIC_SetPriority(DMA1_Channel2_IRQn, 5, 0);
  HAL_NVIC_EnableIRQ(DMA1_Channel2_IRQn);
  /* DMA2_Channel1_IRQn interrupt configuration */
  HAL_NVIC_SetPriority(DMA2_Channel1_IRQn, 5, 0);
  HAL_NVIC_EnableIRQ(DMA2_Channel1_IRQn);
  /* DMA2_Channel2_IRQn interrupt configuration */
  HAL_NVIC_SetPriority(DMA2_Channel2_IRQn, 5, 0);
  HAL_NVIC_EnableIRQ(DMA2_Channel2_IRQn);

}

/**
  * @brief GPIO Initialization Function
  * @param None
  * @retval None
  */
static void MX_GPIO_Init(void)
{
  GPIO_InitTypeDef GPIO_InitStruct = {0};
  /* USER CODE BEGIN MX_GPIO_Init_1 */

  /* USER CODE END MX_GPIO_Init_1 */

  /* GPIO Ports Clock Enable */
  __HAL_RCC_GPIOB_CLK_ENABLE();
  __HAL_RCC_GPIOA_CLK_ENABLE();
  __HAL_RCC_GPIOD_CLK_ENABLE();
  __HAL_RCC_GPIOC_CLK_ENABLE();
  __HAL_RCC_GPIOF_CLK_ENABLE();
  __HAL_RCC_GPIOH_CLK_ENABLE();

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(LED_D_GPIO_Port, LED_D_Pin, GPIO_PIN_RESET);

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(LED_E_GPIO_Port, LED_E_Pin, GPIO_PIN_RESET);

  /*Configure GPIO pin : BUTTON_P_Pin */
  GPIO_InitStruct.Pin = BUTTON_P_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_IT_FALLING;
  GPIO_InitStruct.Pull = GPIO_PULLUP;
  HAL_GPIO_Init(BUTTON_P_GPIO_Port, &GPIO_InitStruct);

  /*Configure GPIO pin : LED_D_Pin */
  GPIO_InitStruct.Pin = LED_D_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(LED_D_GPIO_Port, &GPIO_InitStruct);

  /*Configure GPIO pin : LED_E_Pin */
  GPIO_InitStruct.Pin = LED_E_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(LED_E_GPIO_Port, &GPIO_InitStruct);

  /*Configure GPIO pin : PA4 */
  GPIO_InitStruct.Pin = GPIO_PIN_4;
  GPIO_InitStruct.Mode = GPIO_MODE_ANALOG;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

  /* EXTI interrupt init*/
  HAL_NVIC_SetPriority(EXTI4_IRQn, 5, 0);
  HAL_NVIC_EnableIRQ(EXTI4_IRQn);

  /* USER CODE BEGIN MX_GPIO_Init_2 */

  /* USER CODE END MX_GPIO_Init_2 */
}

/* USER CODE BEGIN 4 */

/* USER CODE END 4 */

/* USER CODE BEGIN Header_StartDefaultTask */
/**
  * @brief  Function implementing the defaultTask thread.
  * @param  argument: Not used
  * @retval None
  */
/* USER CODE END Header_StartDefaultTask */
void StartDefaultTask(void *argument)
{
  /* USER CODE BEGIN 5 */
#if HUB_OLED
  Show_Stats(&MYMGM1_ctx, &Telemetry_ctx, &hadc1);
#endif
  /* Infinite loop */
  for(;;)
  {
    if (s_clk_css_event)            /* v6: o cristal parou (CSS) */
    {
      s_clk_css_event = 0;
      Clock_Css_Recover();
    }
    osDelay(1);
  }
  /* USER CODE END 5 */
}

/* USER CODE BEGIN Header_LatchupProtection */
/**
* @brief Function implementing the LatchupDetectio thread.
* @param argument: Not used
* @retval None
*/
/* USER CODE END Header_LatchupProtection */
void LatchupProtection(void *argument)
{
  /* USER CODE BEGIN LatchupProtection */
  /* Infinite loop */
	for (;;) {
		if (Telemetry_ctx.latest.iout > Telemetry_ctx.max_current) {

			/* ── 1. Cut power, record trip ──────────────────────────── */
			osMutexAcquire(i2cMutexHandle, osWaitForever);
			MYMGM1R_OUTPUT_Disable(Telemetry_ctx.power_ctx);
			osMutexRelease(i2cMutexHandle);
			Telemetry_Set_Output_State(&Telemetry_ctx, 0u);
			Telemetry_ctx.latest.latchup_state = 1u;
			Telemetry_ctx.latest.trip_count += 1u;
			Telemetry_Report_Latchup_Event(&Telemetry_ctx, "TRIP", "CURRENT_LIMIT");
			Telemetry_Send_Board_Status(&Telemetry_ctx);

			/* ── 2. Keep output OFF for LATCHUP_DELAY ───────────────── */
			osDelay(LATCHUP_DELAY);

			/* ── 3. Re-enable and wait for inrush to settle ─────────── */
			osMutexAcquire(i2cMutexHandle, osWaitForever);
			MYMGM1R_OUTPUT_Enable(Telemetry_ctx.power_ctx);
			osMutexRelease(i2cMutexHandle);
			Telemetry_Set_Output_State(&Telemetry_ctx, 1u);

			/* LATCHUP_SETTLE: let capacitors charge and inrush decay
			   before sampling iout.  Do not declare CLEAR yet.        */
			osDelay(LATCHUP_SETTLE);

			/* ── 4. Read iout after settle and decide ───────────────── */
			osMutexAcquire(i2cMutexHandle, osWaitForever);
			Telemetry_ctx.latest.iout = MYMGM1R_Read_Iout(Telemetry_ctx.power_ctx);
			osMutexRelease(i2cMutexHandle);

			if (Telemetry_ctx.latest.iout > Telemetry_ctx.max_current) {
				/* Current still elevated — latchup persists; cut again
				   without incrementing trip_count (same event).        */
				osMutexAcquire(i2cMutexHandle, osWaitForever);
				MYMGM1R_OUTPUT_Disable(Telemetry_ctx.power_ctx);
				osMutexRelease(i2cMutexHandle);
				Telemetry_Set_Output_State(&Telemetry_ctx, 0u);
				Telemetry_Report_Latchup_Event(&Telemetry_ctx, "TRIP", "PERSISTENT_LATCHUP");
				Telemetry_Send_Board_Status(&Telemetry_ctx);
				/* Stay in latchup_state=1; outer loop will re-enter
				   the trip branch on the next poll cycle.             */
			} else {
				/* Current within limits — latchup has cleared.        */
				Telemetry_ctx.latest.latchup_state = 0u;
				Telemetry_Report_Latchup_Event(&Telemetry_ctx, "CLEAR", "AUTO_REENABLE");
				Telemetry_Send_Board_Status(&Telemetry_ctx);
			}
		}
		osDelay(10);
	}
  /* USER CODE END LatchupProtection */
}

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */
  __disable_irq();
  while (1)
  {
  }
  /* USER CODE END Error_Handler_Debug */
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */
