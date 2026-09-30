/*
 * =============================================================================
 * TCC - FIRMWARE CONTROLE BANG-BANG (TERMOSTÁTICO) - BASELINE
 * =============================================================================
 * MCU: Arduino Nano 33 IoT
 * Autor: [Seu Nome]
 * Data: Janeiro/2026
 * 
 * DESCRIÇÃO:
 * Controlador termostático simples (On-Off) para comparação de desempenho
 * com o sistema PID desenvolvido. Este firmware replica o comportamento
 * de um forno convencional com controle por histerese.
 * 
 * IMPLEMENTA:
 * 1. Controle Bang-Bang com histerese configurável
 * 2. Leitura de NTC Ratiométrica (idêntica ao firmware PID)
 * 3. Protocolo serial compatível com supervisório Python
 * 4. Registro de ciclos de comutação para análise
 * 
 * OBJETIVO:
 * Demonstrar as limitações do controle termostático e quantificar
 * a melhoria proporcionada pelo controlador PID em termos de:
 *   - Oscilação pico-a-pico
 *   - Desvio padrão da temperatura
 *   - Frequência de comutação do atuador
 *   - Conformidade com normas JEDEC/MIL-STD
 * 
 * =============================================================================
 */

// =============================================================================
//   CONFIGURAÇÃO DE HARDWARE (Idêntica ao PID)
// =============================================================================
const int NTC_PIN = A0;   // Pino do sensor NTC do forno
const int SSR_PIN = A1;   // Pino de controle para o SSR

// =============================================================================
//   CONSTANTES DO ADC E NTC (Idênticas ao PID para comparação justa)
// =============================================================================
const float VREF = 3.3f;            
const int   ADC_MAX_BITS = 12;      
const float ADC_MAX_VALUE = 4095.0f;  
const int   ADC_SAMPLES = 500;        // Mesma quantidade de amostras
const float R_DIVISOR = 10000.0f;     
const float NTC_R_NOMINAL = 10000.0f; 
const float NTC_T_NOMINAL_C = 25.0f;  
const float NTC_B_VALUE = 3950.0f;    

// =============================================================================
//   PARÂMETROS DO CONTROLE BANG-BANG
// =============================================================================
// HISTERESE: Define a banda morta do controle termostático
// Valores típicos de fornos comerciais: 2-5°C
// Valores de fornos de laboratório baratos: 3-10°C
const float HYSTERESIS_HIGH = 2.0f;  // Desliga quando T > SP + HYST_HIGH
const float HYSTERESIS_LOW  = 2.0f;  // Liga quando T < SP - HYST_LOW

// Intervalo de amostragem (ms) - mesmo do PID para comparação
const long SAMPLE_INTERVAL_MS = 1000;

// =============================================================================
//   VARIÁVEIS GLOBAIS
// =============================================================================
float currentCelsius = 25.0f;     // Temperatura atual do forno
float targetSetpoint = 25.0f;     // Setpoint definido pelo usuário
bool  ssrState = false;           // Estado atual do SSR (true=ON, false=OFF)
bool  testRunning = false;        // Flag de teste em execução

// Estatísticas de operação
unsigned long cycleCount = 0;           // Contador de ciclos ON/OFF
unsigned long lastSwitchTime = 0;       // Timestamp da última comutação
unsigned long totalOnTime = 0;          // Tempo total ligado (ms)
unsigned long testStartTime = 0;        // Início do teste

// Temporização
unsigned long lastSampleTime = 0;

// =============================================================================
//   SETUP
// =============================================================================
void setup() {
  Serial.begin(115200);
  while (!Serial);
  
  analogReadResolution(ADC_MAX_BITS);
  
  pinMode(SSR_PIN, OUTPUT);
  digitalWrite(SSR_PIN, LOW);
  
  currentCelsius = getOvenTemperature();
  targetSetpoint = currentCelsius;
  
  // Mensagem de inicialização
  Serial.println("=============================================");
  Serial.println("TCC - Controlador BANG-BANG (Baseline)");
  Serial.println("=============================================");
  Serial.print("Histerese: +");
  Serial.print(HYSTERESIS_HIGH, 1);
  Serial.print("C / -");
  Serial.print(HYSTERESIS_LOW, 1);
  Serial.println("C");
  Serial.print("Intervalo Amostragem: ");
  Serial.print(SAMPLE_INTERVAL_MS);
  Serial.println(" ms");
  Serial.println("=============================================");
  Serial.println("READY");
}

// =============================================================================
//   LOOP PRINCIPAL
// =============================================================================
void loop() {
  // 1. Processa comandos seriais
  handleSerialCommands();
  
  // 2. Se teste não está rodando, garante SSR desligado
  if (!testRunning) {
    if (ssrState) {
      setSsrState(false);
    }
    return;
  }
  
  // 3. Amostragem periódica
  unsigned long currentMillis = millis();
  if (currentMillis - lastSampleTime >= SAMPLE_INTERVAL_MS) {
    lastSampleTime = currentMillis;
    
    // 4. Atualiza leitura do sensor
    currentCelsius = getOvenTemperature();
    
    // 5. Executa lógica Bang-Bang
    executeBangBangControl();
    
    // 6. Atualiza estatísticas de tempo ligado
    if (ssrState) {
      totalOnTime += SAMPLE_INTERVAL_MS;
    }
  }
}

// =============================================================================
//   LÓGICA DE CONTROLE BANG-BANG
// =============================================================================

/**
 * Implementa o controle termostático com histerese.
 * 
 * Comportamento:
 *   - Se T < (SP - HYST_LOW)  -> Liga aquecedor (100% ON)
 *   - Se T > (SP + HYST_HIGH) -> Desliga aquecedor (100% OFF)
 *   - Se dentro da banda de histerese -> Mantém estado anterior
 * 
 * Este é o comportamento típico de um termostato mecânico ou
 * controlador digital simples encontrado em fornos de laboratório.
 */
void executeBangBangControl() {
  float lowerThreshold = targetSetpoint - HYSTERESIS_LOW;
  float upperThreshold = targetSetpoint + HYSTERESIS_HIGH;
  
  // Temperatura abaixo do limite inferior -> LIGA
  if (currentCelsius < lowerThreshold) {
    if (!ssrState) {
      setSsrState(true);
      cycleCount++;
    }
  }
  // Temperatura acima do limite superior -> DESLIGA
  else if (currentCelsius > upperThreshold) {
    if (ssrState) {
      setSsrState(false);
    }
  }
  // Dentro da banda de histerese -> mantém estado atual
  // (não faz nada, ssrState permanece como está)
}

/**
 * Altera o estado do SSR e registra a comutação.
 */
void setSsrState(bool newState) {
  ssrState = newState;
  digitalWrite(SSR_PIN, ssrState ? HIGH : LOW);
  lastSwitchTime = millis();
}

// =============================================================================
//   COMUNICAÇÃO SERIAL
// =============================================================================

/**
 * Protocolo de comandos (compatível com supervisório):
 *   SET_SP,<valor>  - Define setpoint
 *   START_TEST      - Inicia controle
 *   STOP_TEST       - Para controle
 *   GET_DATA        - Retorna dados atuais
 *   GET_CONFIG      - Retorna configuração
 *   GET_STATS       - Retorna estatísticas de operação
 */
void handleSerialCommands() {
  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    
    // SET_SP,<valor>
    if (cmd.startsWith("SET_SP,")) {
      targetSetpoint = cmd.substring(7).toFloat();
      Serial.println("OK,SP_SET");
    }
    
    // START_TEST
    else if (cmd.equals("START_TEST")) {
      currentCelsius = getOvenTemperature();
      
      // Reset estatísticas
      cycleCount = 0;
      totalOnTime = 0;
      testStartTime = millis();
      lastSwitchTime = millis();
      
      testRunning = true;
      Serial.println("OK,TEST_STARTED");
      
      // Log da configuração
      Serial.print("INFO,BANGBANG_CONFIG,HYST_HIGH=");
      Serial.print(HYSTERESIS_HIGH, 1);
      Serial.print(",HYST_LOW=");
      Serial.println(HYSTERESIS_LOW, 1);
    }
    
    // STOP_TEST
    else if (cmd.equals("STOP_TEST")) {
      testRunning = false;
      setSsrState(false);
      
      // Reporta estatísticas finais
      reportFinalStats();
      
      Serial.println("OK,TEST_STOPPED");
    }
    
    // GET_DATA - Formato compatível com PID: DATA,Temp,Setpoint,Output
    else if (cmd.equals("GET_DATA")) {
      float outputPercent = ssrState ? 100.0 : 0.0;
      
      Serial.print("DATA,");
      Serial.print(currentCelsius, 2);
      Serial.print(",");
      Serial.print(targetSetpoint, 2);
      Serial.print(",");
      Serial.println(outputPercent, 2);
    }
    
    // GET_CONFIG
    else if (cmd.equals("GET_CONFIG")) {
      Serial.print("CONFIG,TYPE=BANGBANG");
      Serial.print(",HYST_HIGH=");
      Serial.print(HYSTERESIS_HIGH, 1);
      Serial.print(",HYST_LOW=");
      Serial.print(HYSTERESIS_LOW, 1);
      Serial.print(",SAMPLE_MS=");
      Serial.println(SAMPLE_INTERVAL_MS);
    }
    
    // GET_STATS - Estatísticas em tempo real
    else if (cmd.equals("GET_STATS")) {
      unsigned long elapsed = millis() - testStartTime;
      float dutyCycle = (elapsed > 0) ? (100.0 * totalOnTime / elapsed) : 0.0;
      float cyclesPerMin = (elapsed > 60000) ? (cycleCount * 60000.0 / elapsed) : 0.0;
      
      Serial.print("STATS,CYCLES=");
      Serial.print(cycleCount);
      Serial.print(",DUTY=");
      Serial.print(dutyCycle, 1);
      Serial.print(",CPM=");  // Cycles Per Minute
      Serial.print(cyclesPerMin, 2);
      Serial.print(",ELAPSED_S=");
      Serial.println(elapsed / 1000);
    }
  }
}

/**
 * Reporta estatísticas finais do teste.
 */
void reportFinalStats() {
  unsigned long elapsed = millis() - testStartTime;
  float dutyCycle = (elapsed > 0) ? (100.0 * totalOnTime / elapsed) : 0.0;
  float cyclesPerMin = (elapsed > 60000) ? (cycleCount * 60000.0 / elapsed) : 0.0;
  
  Serial.println("=====================================");
  Serial.println("ESTATISTICAS FINAIS - BANG-BANG");
  Serial.println("=====================================");
  Serial.print("Duracao do teste: ");
  Serial.print(elapsed / 1000);
  Serial.println(" s");
  Serial.print("Ciclos ON/OFF: ");
  Serial.println(cycleCount);
  Serial.print("Ciclos por minuto: ");
  Serial.println(cyclesPerMin, 2);
  Serial.print("Duty cycle medio: ");
  Serial.print(dutyCycle, 1);
  Serial.println("%");
  Serial.print("Tempo total ON: ");
  Serial.print(totalOnTime / 1000);
  Serial.println(" s");
  Serial.println("=====================================");
}

// =============================================================================
//   FUNÇÕES DE LEITURA DO SENSOR (Idênticas ao PID)
// =============================================================================

float getOvenTemperature() {
  float adc_avg = adc_read_averaged(NTC_PIN, ADC_SAMPLES);
  float r_ntc = ntc_resistance_from_adc(adc_avg);
  float celsius = ntc_temp_from_resistance(r_ntc);
  return celsius;
}

float adc_read_averaged(int pin, int samples) {
  uint32_t sum = 0;
  for(int i = 0; i < samples; i++) {
    sum += analogRead(pin);
    delay(1); 
  }
  return (float)sum / (float)samples;
}

float ntc_resistance_from_adc(float adc_avg_val) {
  if (adc_avg_val >= ADC_MAX_VALUE - 1) {
    return 9999999.0f;
  }
  if (adc_avg_val < 1.0f) {
    return 0.1f;
  }
  return R_DIVISOR * (adc_avg_val / (ADC_MAX_VALUE - adc_avg_val));
}

float ntc_temp_from_resistance(float R_ntc) {
  const float T0_K = NTC_T_NOMINAL_C + 273.15f;
  float invT = 1.0f / T0_K + (1.0f / NTC_B_VALUE) * log(R_ntc / NTC_R_NOMINAL);
  float T_K = 1.0f / invT;
  return T_K - 273.15f;
}
