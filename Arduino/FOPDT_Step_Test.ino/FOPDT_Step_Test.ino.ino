/*
 * TCC - FIRMWARE DE TESTE DE DEGRAU (FOPDT)
 * MCU: Arduino Nano 33 IoT
 * OBJETIVO: Este código NÃO é o controlador PID.
 * Ele serve apenas para o teste de identificação do sistema.
 * Ele recebe um comando serial (ex: "SET_DUTY,50.0") e aplica
 * essa potência constante no SSR, reportando a temperatura
 * para o PC (Python) que a registra.
 */

// --- Pinos de Hardware ---
const int NTC_PIN = A0;   // Pino do sensor NTC do forno
const int SSR_PIN = A1;   // Pino que aciona o Relé de Estado Sólido (SSR)

// --- Constantes do ADC e NTC (Portado do seu STM32) ---
const float VREF = 3.3f;            // Tensão de referência (correto para o Nano 33 IoT)
const int   ADC_MAX_BITS = 12;      // Vamos usar 12-bits de resolução (o Nano 33 IoT suporta)
const float ADC_MAX_VALUE = 4095.0f;  // 2^12 - 1
const int   ADC_SAMPLES = 100;       // Número de amostras para fazer a média (reduz ruído)

// --- Constantes do NTC (Baseado nas suas especificações) ---
const float R_DIVISOR = 10000.0f;       // Resistor divisor de 10k
const float NTC_R_NOMINAL = 10000.0f;   // 10k (Resistência nominal do NTC)
const float NTC_T_NOMINAL_C = 25.0f;    // 25°C (Temperatura nominal)

// !! ATENÇÃO: SUAS SPECS TÊM DOIS VALORES B. ESCOLHA O CORRETO !!
//    B=3950 (do "Tipo") ou B=3380 (da "B-constante")
//    Mude o valor abaixo para fazer seu fine-tuning.
const float NTC_B_VALUE = 3950.0f;      //
// const float NTC_B_VALUE = 3380.0f;   // (Descomente para testar este)


// --- Parâmetros de Controle do Teste ---
const long TIME_PROPORTIONING_WINDOW = 5000; // Janela de 5 segundos (5000 ms)
float dutyCycle = 0.0;                       // (0.0 a 100.0)
bool testRunning = false;

// --- Variáveis de Temporização ---
unsigned long ssrWindowStartTime = 0;

// =================================================================
//   SETUP
// =================================================================
void setup() {
  Serial.begin(115200); // Inicia comunicação serial com o PC (Python)
  
  // LINHA CRÍTICA: Espera o PC (Python) abrir a porta serial
  // Essencial para placas com USB nativo como o Nano 33 IoT
  while (!Serial);
  
  // Aumenta a resolução do ADC de 10-bit (padrão) para 12-bit
  analogReadResolution(ADC_MAX_BITS);
  
  pinMode(SSR_PIN, OUTPUT);
  digitalWrite(SSR_PIN, LOW);
  
  Serial.println("Arduino FOPDT Tester Pronto.");
}

// =================================================================
//   LOOP PRINCIPAL
// =================================================================
void loop() {
  // 1. Processa comandos seriais vindos do Python
  handleSerialCommands();
  
  // 2. Executa o controle do SSR (se o teste estiver rodando)
  runSsrControl();
}

// =================================================================
//   FUNÇÕES DE CONTROLE
// =================================================================

/**
 * @brief Verifica se há comandos seriais do Python e os processa.
 */
void handleSerialCommands() {
  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    processCommand(cmd);
  }
}

/**
 * @brief Executa a lógica de Time-Proportioning (PWM Lento) para o SSR.
 [cite_start]* [cite: 604-608]
 */
void runSsrControl() {
  if (!testRunning) {
    digitalWrite(SSR_PIN, LOW); // Garante que esteja desligado
    return;
  }

  unsigned long currentMillis = millis();

  // Reinicia a janela de 5 segundos se ela tiver terminado
  if (currentMillis - ssrWindowStartTime >= TIME_PROPORTIONING_WINDOW) {
    ssrWindowStartTime = currentMillis;
  }

  // Calcula quanto tempo (ms) o SSR deve ficar LIGADO dentro desta janela
  unsigned long onTime_ms = (TIME_PROPORTIONING_WINDOW * dutyCycle) / 100.0;

  // Lógica de acionamento do SSR
  if (currentMillis - ssrWindowStartTime < onTime_ms) {
    digitalWrite(SSR_PIN, HIGH);
  } else {
    digitalWrite(SSR_PIN, LOW);
  }
}

/**
 * @brief Interpreta os comandos de texto do Python.
 */
void processCommand(String cmd) {
  // Ex: "SET_DUTY,50.0"
  if (cmd.startsWith("SET_DUTY,")) {
    dutyCycle = cmd.substring(9).toFloat();
    testRunning = true;
    ssrWindowStartTime = millis(); // Inicia o controle imediatamente
    Serial.println("OK,DUTY_SET"); // Resposta clara
  }
  
  // Ex: "STOP_TEST"
  else if (cmd.equals("STOP_TEST")) {
    testRunning = false;
    dutyCycle = 0.0;
    digitalWrite(SSR_PIN, LOW); // Garante que o forno desligue
    Serial.println("OK,STOPPED"); // Resposta clara
  }
  
  // Ex: "GET_DATA"
  else if (cmd.equals("GET_DATA")) {
    float tempC = getOvenTemperature();
    
    // Formato: "DATA,TEMP_FORNO"
    Serial.print("DATA,");
    Serial.println(tempC, 2); // Envia com 2 casas decimais
  }
}

// =================================================================
//   FUNÇÕES DE LEITURA DO SENSOR (Portado do seu STM32)
// =================================================================

/**
 * @brief Pega a temperatura final do forno em Celsius.
 * Combina todas as etapas de conversão.
 */
float getOvenTemperature() {
  // 1. Ler a média de N amostras do ADC
  float adc_avg = adc_read_averaged(NTC_PIN, ADC_SAMPLES);

  // 2. Converter o valor do ADC em resistência
  float r_ntc = ntc_resistance_from_adc(adc_avg);

  // 3. Converter a resistência em temperatura
  float celsius = ntc_temp_from_resistance(r_ntc);
  
  return celsius;
}

/**
 * @brief Realiza a leitura de 'samples' amostras do ADC e retorna a média.
 */
float adc_read_averaged(int pin, int samples) {
  uint32_t sum = 0;
  for(int i = 0; i < samples; i++) {
    sum += analogRead(pin);
    delay(1); // Pequeno delay para estabilização
  }
  return (float)sum / (float)samples;
}

/**
 * @brief Calcula a resistência do NTC a partir do valor PURO do ADC (Ratiométrico).
 * @note  Assume o circuito: VREF --- [NTC] --- ADC_PIN --- [R_DIVISOR] --- GND
 * Esta fórmula é imune a flutuações na VREF (USB).
 */
float ntc_resistance_from_adc(float adc_avg_val) {
  
  // Proteção contra leitura máxima (NTC em curto ou V_adc = VREF)
  if (adc_avg_val >= ADC_MAX_VALUE - 1) {
    return 9999999.0f; // Resistência quase infinita
  }

  // Fórmula Ratiométrica para Pull-Down:
  // R_NTC = R_DIVISOR * (Leitura_ADC / (MAX_ADC - Leitura_ADC))
  float r_ntc = R_DIVISOR * (adc_avg_val / (ADC_MAX_VALUE - adc_avg_val));

  return r_ntc;
}
/**
 * @brief Calcula a temperatura em Celsius usando a fórmula Beta.
 */
float ntc_temp_from_resistance(float R_ntc) {
  // T0 em Kelvin (Temperatura nominal, 25°C)
  const float T0_K = NTC_T_NOMINAL_C + 273.15f;
  
  // T_K = 1 / ( (1/T0) + (1/B) * ln(R/R0) )
  float invT = 1.0f / T0_K + (1.0f / NTC_B_VALUE) * log(R_ntc / NTC_R_NOMINAL);
  
  float T_K = 1.0f / invT;
  
  // Retorna a temperatura em Celsius
  return T_K - 273.15f;
}
