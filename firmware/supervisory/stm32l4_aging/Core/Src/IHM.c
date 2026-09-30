/******************************************************************************
 * @file    IHM.c (UPDATED - WITH TELEMETRY)
 * @brief   Driver de inicialização e configuração do display com telemetria
 *
 *          Implementa rotinas de inicialização, configuração e escrita no
 *          display SSD1306 utilizando a biblioteca "ssd1306.h".
 *
 *          NOVO: Integração com módulo de telemetria para envio de dados ao PC.
 *
 * @author  Caio Felipe / Updated
 * @date    2025
 *****************************************************************************/

#include "stm32l4xx_hal.h"
#include "IHM.h"
#include "Serial_Bridge.h"
#include "ssd1306.h"
#include "fonts.h"
#include "bitmap.h"
#include "telemetry.h"
#include <stdio.h>


static MYMGM1R_Struct *MYMGM1_ctx;
static Queue Vout_buffer;
static Queue Iout_buffer;
static Queue Temperature_buffer;
static Queue mean_buffer;
volatile int page = 1, qnt = 0;
float top_t = 40, base_t = 20;
float top_i = 1, base_i = 0;
float top_v = 2, base_v = 0;
float vcore = 1.00;

MYMGM1R_Struct* Get_MYM_ctx()
{
    return MYMGM1_ctx;
}

static inline uint8_t buffer_is_full(Queue *q)
{
    return ((q->last + 1) % QUEUE_SIZE) == q->first;
}

static inline void buffer_push(Queue *q, float data)
{
    if (!buffer_is_full(q)) {
        q->rx_buffer[q->last] = data;
        q->last = (q->last + 1) % QUEUE_SIZE;
        q->qnt += 1;
    }
}

static inline void buffer_pop(Queue *q)
{
    q->first = (q->first + 1) % QUEUE_SIZE;
    q->qnt -= 1;
}

void change_page(uint8_t new_page)
{
    page = new_page;
}

void rewrite_metrics(float top, float base, char *buffer, char type) {
    SSD1306_DrawFilledRectangle(7, 1, 13, 31, SSD1306_COLOR_BLACK);

    if(type == 'I' || type == 'V'){
        SSD1306_GotoXY(12, 1);
        sprintf(buffer, "%.2f", top);
        SSD1306_Puts(buffer, &Font_6x8, SSD1306_COLOR_WHITE);

        SSD1306_GotoXY(12, 25);
        sprintf(buffer, "%.2f", base);
        SSD1306_Puts(buffer, &Font_6x8, SSD1306_COLOR_WHITE);
    }
    else{
        SSD1306_GotoXY(12, 1);
        sprintf(buffer, "%.1f", top);
        SSD1306_Puts(buffer, &Font_6x8, SSD1306_COLOR_WHITE);

        SSD1306_GotoXY(12, 25);
        sprintf(buffer, "%.1f", base);
        SSD1306_Puts(buffer, &Font_6x8, SSD1306_COLOR_WHITE);
    }
}

float Read_Temp(ADC_HandleTypeDef *hadc1)
{
    float temp;
    uint32_t raw;

    uint16_t TS_CAL1 = *(TS_CAL1_ADDR);
    uint16_t TS_CAL2 = *(TS_CAL2_ADDR);
    HAL_ADC_Start(hadc1);
    HAL_ADC_PollForConversion(hadc1, HAL_MAX_DELAY);
    raw = HAL_ADC_GetValue(hadc1);
    HAL_ADC_Stop(hadc1);
    raw = (float)raw * 1.1;
    temp = ((float)raw - (float)TS_CAL1) * 80 / ((float)TS_CAL2 - (float)TS_CAL1) + 30;
    return temp;
}

/*****************************************************************************
 * @brief Inicializa e configura o display enquanto o código é carregado na FPGA.
 ******************************************************************************/
void OLED_Init(void)
{
    HAL_Delay(50);
    SSD1306_Init();

    SSD1306_Contrast(255);
    SSD1306_MirrorReflection(0);
    SSD1306_ScreenRotation(0);

    SSD1306_DrawRectangle(1, 1, 125, 61, SSD1306_COLOR_WHITE);
    SSD1306_GotoXY(10,14);
    SSD1306_Puts("Inicializando...", &Font_6x8, SSD1306_COLOR_WHITE);
    SSD1306_UpdateScreen();
    SSD1306_InvertDisplay(0);
    HAL_Delay(1000);

    SSD1306_Clear();

    SSD1306_DrawBitmap(90, 0, logo_funcap, 32, 32, SSD1306_COLOR_WHITE);
    SSD1306_GotoXY(6,12);
    SSD1306_Puts("Com apoio de:", &Font_6x8, SSD1306_COLOR_WHITE);
    SSD1306_UpdateScreen();
    HAL_Delay(4000);

    SSD1306_Clear();

    SSD1306_DrawBitmap(0, 0, logo_lesc, 32, 32, SSD1306_COLOR_WHITE);
    SSD1306_GotoXY(35,0);
    SSD1306_Puts("Laboratorio de", &Font_6x8, SSD1306_COLOR_WHITE);
    SSD1306_GotoXY(35,8);
    SSD1306_Puts("Engenharia de", &Font_6x8, SSD1306_COLOR_WHITE);
    SSD1306_GotoXY(35,16);
    SSD1306_Puts("Sistemas de", &Font_6x8, SSD1306_COLOR_WHITE);
    SSD1306_GotoXY(35,24);
    SSD1306_Puts("Computacao", &Font_6x8, SSD1306_COLOR_WHITE);
    SSD1306_UpdateScreen();

    HAL_Delay(4000);
}

/*****************************************************************************
 * @brief Page 1: MYMGM1R Stats with telemetry update
 ******************************************************************************/
void MYMGM1R_Stats_Telemetry(MYMGM1R_Struct *MYMGM1R_ctx, char *buffer,
                            Telemetry_Context *tel_ctx)
{
    float Temp, Vin, Vcore, Iout;

    SSD1306_Clear();

    SSD1306_GotoXY(1, 1);
    SSD1306_Puts("Temp:", &Font_6x8, SSD1306_COLOR_WHITE);
    SSD1306_GotoXY(1, 9);
    SSD1306_Puts("Vin:", &Font_6x8, SSD1306_COLOR_WHITE);
    SSD1306_GotoXY(1, 17);
    SSD1306_Puts("Vcore:", &Font_6x8, SSD1306_COLOR_WHITE);
    SSD1306_GotoXY(1, 25);
    SSD1306_Puts("Iout:", &Font_6x8, SSD1306_COLOR_WHITE);

    SSD1306_GotoXY(120,4);
    SSD1306_Putc('M', &Font_6x8, SSD1306_COLOR_WHITE);
    SSD1306_GotoXY(120,13);
    SSD1306_Putc('Y', &Font_6x8, SSD1306_COLOR_WHITE);
    SSD1306_GotoXY(120,21);
    SSD1306_Putc('M', &Font_6x8, SSD1306_COLOR_WHITE);

    while (page == 1) {
        // Update telemetry (non-blocking, checks interval internally)
        Telemetry_Update(tel_ctx);

        SSD1306_DrawFilledRectangle(43, 1, 60, 30, SSD1306_COLOR_BLACK);

        SSD1306_GotoXY(43, 1);
        Temp = MYMGM1R_Read_Temperature(MYMGM1R_ctx);
        sprintf(buffer, "%.2f C", Temp);
        SSD1306_Puts(buffer, &Font_6x8, SSD1306_COLOR_WHITE);

        SSD1306_GotoXY(43, 9);
        Vin = MYMGM1R_Read_Vin(MYMGM1R_ctx);
        sprintf(buffer, "%.3f V", Vin);
        SSD1306_Puts(buffer, &Font_6x8, SSD1306_COLOR_WHITE);

        SSD1306_GotoXY(43, 17);
        Vcore = MYMGM1R_Read_Vcore(MYMGM1R_ctx);
        sprintf(buffer, "%.3f V", Vcore);
        SSD1306_Puts(buffer, &Font_6x8, SSD1306_COLOR_WHITE);

        SSD1306_GotoXY(43, 25);
        Iout = MYMGM1R_Read_Iout(MYMGM1R_ctx);
        sprintf(buffer, "%.3f A", Iout);
        SSD1306_Puts(buffer, &Font_6x8, SSD1306_COLOR_WHITE);

        SSD1306_UpdateScreen();

        HAL_Delay(200);  // Faster update for better responsiveness
    }
}

/*****************************************************************************
 * @brief Page 2: Temperature graph with telemetry
 ******************************************************************************/
void FPGA_Graph_Temp_Telemetry(MYMGM1R_Struct *MYMGM1R_ctx, char *buffer,
                               Telemetry_Context *tel_ctx)
{
    float new_temp;
    int pos_y, pos_x, current_temp;
    float step = 10;
    float distance = 20;

    SSD1306_Clear();

    SSD1306_GotoXY(1,1);
    SSD1306_Putc('T', &Font_6x8, SSD1306_COLOR_WHITE);
    SSD1306_GotoXY(1,8);
    SSD1306_Putc('e', &Font_6x8, SSD1306_COLOR_WHITE);
    SSD1306_GotoXY(1,15);
    SSD1306_Putc('m', &Font_6x8, SSD1306_COLOR_WHITE);
    SSD1306_GotoXY(1,24);
    SSD1306_Putc('p', &Font_6x8, SSD1306_COLOR_WHITE);

    SSD1306_DrawLine(38, 31, 127, 31, SSD1306_COLOR_WHITE);
    SSD1306_DrawLine(38, 1, 38, 31, SSD1306_COLOR_WHITE);

    rewrite_metrics(top_t, base_t, buffer, 'T');

    while(page == 2){
        Telemetry_Update(tel_ctx);

        SSD1306_DrawFilledRectangle(39, 0, 89, 29, SSD1306_COLOR_BLACK);

        new_temp = MYMGM1R_Read_Temperature(MYMGM1R_ctx);
        if(buffer_is_full(&Temperature_buffer)){
            buffer_pop(&Temperature_buffer);
        }
        buffer_push(&Temperature_buffer, new_temp);

        if(new_temp > top_t) {
            top_t += step;
            rewrite_metrics(top_t, base_t, buffer, 'T');
        }
        else if (new_temp < base_t){
            base_t -= step;
            rewrite_metrics(top_t, base_t, buffer, 'T');
        }

        distance = top_t - base_t;
        if(distance < 1) {
            top_t = base_t + 10;
            distance = 10;
        }

        for(int i = 39; i < Temperature_buffer.qnt+39; i++){
            current_temp = (Temperature_buffer.first + i - 39) % QUEUE_SIZE;
            pos_y = 31 - (Temperature_buffer.rx_buffer[current_temp] - base_t) * 31/distance;
            pos_x = i - 1;
            SSD1306_DrawPixel(pos_x, pos_y, SSD1306_COLOR_WHITE);
        }

        SSD1306_DrawFilledRectangle(12, 13, 25, 10, SSD1306_COLOR_BLACK);
        SSD1306_GotoXY(12,13);
        sprintf(buffer, "%.1f", new_temp);
        SSD1306_Puts(buffer, &Font_6x8, SSD1306_COLOR_WHITE);

        SSD1306_UpdateScreen();
        HAL_Delay(10);
    }
}

/*****************************************************************************
 * @brief Page 3: Current graph with telemetry
 ******************************************************************************/
void FPGA_Graph_Iout_Telemetry(MYMGM1R_Struct *MYMGM1R_ctx, char *buffer,
                               Telemetry_Context *tel_ctx)
{
    int pos_y, pos_x, current_iout;
    float distance = 1, step = 0.2, Imean, new_iout;

    float last15[MEAN_WINDOW] = {0};
    int last = 0;
    int count = 0;
    float sum = 0;

    SSD1306_Clear();

    SSD1306_GotoXY(1,1);
    SSD1306_Putc('I', &Font_6x8, SSD1306_COLOR_WHITE);
    SSD1306_GotoXY(1,8);
    SSD1306_Putc('o', &Font_6x8, SSD1306_COLOR_WHITE);
    SSD1306_GotoXY(1,15);
    SSD1306_Putc('u', &Font_6x8, SSD1306_COLOR_WHITE);
    SSD1306_GotoXY(1,24);
    SSD1306_Putc('t', &Font_6x8, SSD1306_COLOR_WHITE);

    SSD1306_DrawLine(38, 31, 127, 31, SSD1306_COLOR_WHITE);
    SSD1306_DrawLine(38, 1, 38, 31, SSD1306_COLOR_WHITE);

    rewrite_metrics(top_i, base_i, buffer, 'I');

    while(page == 3){
        Telemetry_Update(tel_ctx);

        SSD1306_DrawFilledRectangle(39, 0, 89, 29, SSD1306_COLOR_BLACK);

        new_iout = MYMGM1R_Read_Iout(MYMGM1R_ctx);
        if(buffer_is_full(&Iout_buffer)){
            buffer_pop(&Iout_buffer);
        }
        buffer_push(&Iout_buffer, new_iout);

        if (count < MEAN_WINDOW) {
            sum += new_iout;
            last15[count++] = new_iout;
        }
        else {
            sum -= last15[last];
            last15[last] = new_iout;
            sum += new_iout;
            last = (last + 1) % MEAN_WINDOW;
        }
        Imean = (count > 0) ? sum / count : 0;

        if(buffer_is_full(&mean_buffer)){
            buffer_pop(&mean_buffer);
        }
        buffer_push(&mean_buffer, Imean);

        if(Imean > top_i) {
            top_i += step;
            rewrite_metrics(top_i, base_i, buffer, 'I');
        }
        else if (Imean < base_i){
            base_i -= step;
            rewrite_metrics(top_i, base_i, buffer, 'I');
        }

        distance = top_i - base_i;
        if(distance < 0.1) {
            top_i = base_i + 1;
            distance = 1;
        }

        for(int i = 39; i < mean_buffer.qnt+39; i++){
            current_iout = (mean_buffer.first + i - 39) % QUEUE_SIZE;
            pos_y = 31 - (mean_buffer.rx_buffer[current_iout] - base_i) * 31/distance;
            pos_x = i - 1;
            SSD1306_DrawPixel(pos_x, pos_y, SSD1306_COLOR_WHITE);
        }

        SSD1306_DrawFilledRectangle(12, 13, 25, 10, SSD1306_COLOR_BLACK);
        SSD1306_GotoXY(12,13);
        sprintf(buffer, "%.2f", Imean);
        SSD1306_Puts(buffer, &Font_6x8, SSD1306_COLOR_WHITE);

        SSD1306_UpdateScreen();
        HAL_Delay(10);
    }
}

/*****************************************************************************
 * @brief Page 4: Voltage graph with telemetry
 ******************************************************************************/
void FPGA_Graph_Vcore_Telemetry(MYMGM1R_Struct *MYMGM1R_ctx, char *buffer,
                                Telemetry_Context *tel_ctx)
{
    int pos_y, pos_x, current_vout;
    float distance = 2, step = 0.5, new_vout;

    SSD1306_Clear();

    SSD1306_GotoXY(1,1);
    SSD1306_Putc('V', &Font_6x8, SSD1306_COLOR_WHITE);
    SSD1306_GotoXY(1,8);
    SSD1306_Putc('c', &Font_6x8, SSD1306_COLOR_WHITE);
    SSD1306_GotoXY(1,15);
    SSD1306_Putc('o', &Font_6x8, SSD1306_COLOR_WHITE);
    SSD1306_GotoXY(1,23);
    SSD1306_Putc('r', &Font_6x8, SSD1306_COLOR_WHITE);

    SSD1306_DrawLine(38, 31, 127, 31, SSD1306_COLOR_WHITE);
    SSD1306_DrawLine(38, 1, 38, 31, SSD1306_COLOR_WHITE);

    rewrite_metrics(top_v, base_v, buffer, 'V');

    while(page == 4){
        Telemetry_Update(tel_ctx);

        SSD1306_DrawFilledRectangle(39, 0, 89, 29, SSD1306_COLOR_BLACK);

        new_vout = MYMGM1R_Read_Vcore(MYMGM1R_ctx);
        if(buffer_is_full(&Vout_buffer)){
            buffer_pop(&Vout_buffer);
        }
        buffer_push(&Vout_buffer, new_vout);

        if(new_vout > top_v) {
            top_v += step;
            rewrite_metrics(top_v, base_v, buffer, 'V');
        }
        else if (new_vout < base_v){
            base_v -= step;
            rewrite_metrics(top_v, base_v, buffer, 'V');
        }

        distance = top_v - base_v;
        if(distance < 1) {
            top_v = base_v + 10;
            distance = 10;
        }

        for(int i = 39; i < Vout_buffer.qnt+39; i++){
            current_vout = (Vout_buffer.first + i - 39) % QUEUE_SIZE;
            pos_y = 31 - (Vout_buffer.rx_buffer[current_vout] - base_v) * 31/distance;
            pos_x = i - 1;
            SSD1306_DrawPixel(pos_x, pos_y, SSD1306_COLOR_WHITE);
        }

        SSD1306_DrawFilledRectangle(12, 13, 25, 10, SSD1306_COLOR_BLACK);
        SSD1306_GotoXY(12,13);
        sprintf(buffer, "%.2f", new_vout);
        SSD1306_Puts(buffer, &Font_6x8, SSD1306_COLOR_WHITE);

        SSD1306_UpdateScreen();
        HAL_Delay(10);
    }
}

/*****************************************************************************
 * @brief Page 5: All temperatures with telemetry
 ******************************************************************************/
void All_Temperatures_Telemetry(MYMGM1R_Struct *MYMGM1R_ctx,
                                ADC_HandleTypeDef *hadc1,
                                char *buffer,
                                Telemetry_Context *tel_ctx)
{
    float temp_MYM, temp_FPGA, temp_MIC;

    SSD1306_Clear();

    SSD1306_GotoXY(1, 1);
    SSD1306_Puts("MYMGM1R:", &Font_6x8, SSD1306_COLOR_WHITE);
    SSD1306_GotoXY(1, 9);
    SSD1306_Puts("FPGA:", &Font_6x8, SSD1306_COLOR_WHITE);
    SSD1306_GotoXY(1, 17);
    SSD1306_Puts("MICRO:", &Font_6x8, SSD1306_COLOR_WHITE);

    while (page == 5) {
        Telemetry_Update(tel_ctx);

        SSD1306_DrawFilledRectangle(61, 1, 54, 30, SSD1306_COLOR_BLACK);

        SSD1306_GotoXY(61, 1);
        temp_MYM = MYMGM1R_Read_Temperature(MYMGM1R_ctx);
        sprintf(buffer, "%.3f C", temp_MYM);
        SSD1306_Puts(buffer, &Font_6x8, SSD1306_COLOR_WHITE);

        SSD1306_GotoXY(61, 9);
        temp_FPGA = 0.0f;  // TODO: Get from FPGA via UART if needed
        sprintf(buffer, "%.3f C", temp_FPGA);
        SSD1306_Puts(buffer, &Font_6x8, SSD1306_COLOR_WHITE);

        SSD1306_GotoXY(61, 17);
        temp_MIC = Read_Temp(hadc1);
        sprintf(buffer, "%.3f C", temp_MIC);
        SSD1306_Puts(buffer, &Font_6x8, SSD1306_COLOR_WHITE);

        SSD1306_UpdateScreen();

        HAL_Delay(500);
    }
}

/*****************************************************************************
 * @brief Page 6: Debug page with telemetry
 ******************************************************************************/
void Debug_Page_Telemetry(Telemetry_Context *tel_ctx)
{
    int line = 1, column = 1;
    uint8_t *buffer;

    while (page == 6) {
        Telemetry_Update(tel_ctx);

        line = 1;
        column = 1;
        SSD1306_Clear();

        buffer = Read_Messages_From_FPGA();

        for (int i = 1; i < DEBUG_BUFFER_SIZE; i++) {
            uint8_t current_byte = buffer[i];

            if (current_byte == '\0') continue;

            if (current_byte == '\n' || current_byte == '\r') {
                if (i + 1 < 25) {
                    uint8_t next = buffer[i + 1];
                    if (next == '\r' || next == '\n') i++;
                }
                line += 8;
                column = 1;
                continue;
            }

            if (column > 123) {
                line += 8;
                column = 1;
                if (line > 25) {
                    SSD1306_Clear();
                    line = 1;
                    column = 1;
                }
            }
            if (line > 25) {
                SSD1306_Clear();
                line = 1;
                column = 1;
            }

            SSD1306_GotoXY(column, line);
            SSD1306_Putc(current_byte, &Font_6x8, SSD1306_COLOR_WHITE);
            column += 6;
        }

        SSD1306_UpdateScreen();
        HAL_Delay(500);
    }
}

/*****************************************************************************
 * @brief Main stats display loop WITH telemetry integration
 *
 * This is the new function that replaces the original Show_Stats().
 * It calls Telemetry_Update() in each page loop to ensure periodic
 * data transmission to the PC regardless of which page is displayed.
 *
 * @param[in] MYMGM1R_ctx Pointer to power module context
 * @param[in] hadc1 Pointer to ADC handle for MCU temperature
 * @param[in] tel_ctx Pointer to telemetry context
 ******************************************************************************/
void Show_Stats_With_Telemetry(MYMGM1R_Struct *MYMGM1R_ctx,
                               ADC_HandleTypeDef *hadc1,
                               Telemetry_Context *tel_ctx)
{
    char buffer[32];

    MYMGM1_ctx = MYMGM1R_ctx;

    while(1) {
        switch(page) {
            case 1:  // Power module stats
                MYMGM1R_Stats_Telemetry(MYMGM1R_ctx, buffer, tel_ctx);
                break;
            case 2:  // Temperature graph
                FPGA_Graph_Temp_Telemetry(MYMGM1R_ctx, buffer, tel_ctx);
                break;
            case 3:  // Current graph
                FPGA_Graph_Iout_Telemetry(MYMGM1R_ctx, buffer, tel_ctx);
                break;
            case 4:  // Voltage graph
                FPGA_Graph_Vcore_Telemetry(MYMGM1R_ctx, buffer, tel_ctx);
                break;
            case 5:  // All temperatures
                All_Temperatures_Telemetry(MYMGM1R_ctx, hadc1, buffer, tel_ctx);
                break;
            case 6:  // Debug page
                Debug_Page_Telemetry(tel_ctx);
                break;
            default:
                Debug_Page_Telemetry(tel_ctx);
                break;
        }
    }
}

/*****************************************************************************
 * @brief Original Show_Stats (kept for backward compatibility)
 * @deprecated Use Show_Stats_With_Telemetry instead
 ******************************************************************************/
void Show_Stats(MYMGM1R_Struct *MYMGM1R_ctx, ADC_HandleTypeDef *hadc1)
{
    // Create a dummy telemetry context (disabled)
    Telemetry_Context dummy_ctx;
    dummy_ctx.enabled = 0;

    Show_Stats_With_Telemetry(MYMGM1R_ctx, hadc1, &dummy_ctx);
}
