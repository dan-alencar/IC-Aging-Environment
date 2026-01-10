/*
 * =============================================================================
 * TCC - FIRMWARE CONTROLADOR PID DO FORNO (VERSÃO FINAL)
 * =============================================================================
 * MCU: Arduino Nano 33 IoT
 * Autor: [Seu Nome]
 * Data: Janeiro/2026
 * 
 * DESCRIÇÃO:
 * Controlador PID para estabilização térmica de forno de burn-in.
 * Ganhos fixos calculados via identificação FOPDT e método SIMC.
 * 
 * IMPLEMENTA:
 * 1. Ganhos PID fixos (Kp, Ki, Kd) - NÃO alteráveis em tempo de execução
 * 2. Controle de SSR via Time-Proportioning (PWM Lento, janela 5s)
 * 3. Rampa de Setpoint (1°C/s para evitar overshoot)
 * 4. Anti-Windup (nativo da biblioteca ArduPID)
 * 5. Leitura de NTC Ratiométrica (12-bit, 500 amostras)
 * 6. Protocolo serial para supervisório Python
 * 
 * PARÂMETROS IDENTIFICADOS (Step Test 50%, 6074s):
 *   K (ganho)     = 1.56 °C/%
 *   θ (tempo morto) = 150.6 s
 *   τ (constante)   = 1307.2 s
 *   θ/τ            = 0.115 (sistema com tempo morto pequeno)
 * 
 * GANHOS SIMC (τc = θ):
 *   Kp = 2.78
 *   Ki = 0.00106 (validado experimentalmente)
 *   Kd = 5.0
 * =============================================================================
 */

#include <ArduPID.h>

// =============================================================================
//   CONFIGURAÇÃO DE HARDWARE
// =============================================================================
const int NTC_PIN = A0;   // Pino do sensor NTC do forno
const int SSR_PIN = A1;   // Pino de controle (via TIP31) para o SSR

// =============================================================================
//   CONSTANTES DO ADC E NTC
// =============================================================================
const float VREF = 3.3f;            
const int   ADC_MAX_BITS = 12;      
const float ADC_MAX_VALUE = 4095.0f;  
const int   ADC_SAMPLES = 500;        // Amostras para média (estabilidade)
const float R_DIVISOR = 10000.0f;     // Resistor do divisor de tensão
const float NTC_R_NOMINAL = 10000.0f; // Resistência nominal do NTC @ 25°C
const float NTC_T_NOMINAL_C = 25.0f;  // Temperatura nominal
const float NTC_B_VALUE = 3950.0f;    // Coeficiente Beta do NTC

// =============================================================================
//   PARÂMETROS DE CONTROLE
// =============================================================================
const long  CONTROL_PERIOD_MS = 5000;    // Janela do time-proportioning (5s)
const float RAMP_RATE_PER_SEC = 1.0f;    // Taxa da rampa: 1°C/segundo

// =============================================================================
//   GANHOS PID (FIXOS - CALCULADOS VIA SIMC)
// =============================================================================
// IMPORTANTE: Estes valores foram validados experimentalmente e NÃO devem
// ser alterados em tempo de execução para garantir repetibilidade dos testes.
const double KP = 2.78;
const double KI = 0.00106;
const double KD = 5.0;

// =============================================================================
//   VARIÁVEIS GLOBAIS
// =============================================================================
double currentCelsius;    // (Input)  Temperatura atual do forno
double pidOutput;         // (Output) Saída do PID (0-100%)
double rampedSetpoint;    // (Setpoint) Setpoint com rampa aplicada

double targetSetpoint = 25.0;  // Setpoint alvo definido pelo usuário
bool testRunning = false;      // Flag de teste em execução

ArduPID myPID;

// Variáveis de temporização
unsigned long ssrWindowStartTime = 0;
unsigned long rampTimer = 0;

// =============================================================================
//   SETUP
// =============================================================================
void setup() {
  Serial.begin(115200);
  while (!Serial);  // Aguarda conexão USB
  
  analogReadResolution(ADC_MAX_BITS);
  
  pinMode(SSR_PIN, OUTPUT);
  digitalWrite(SSR_PIN, LOW);
  
  // --- Inicialização do PID ---
  currentCelsius = getOvenTemperature();
  rampedSetpoint = currentCelsius;
  targetSetpoint = currentCelsius;
  
  myPID.begin(&currentCelsius, &pidOutput, &rampedSetpoint, KP, KI, KD);
  myPID.setOutputLimits(0, 100);
  myPID.setWindUpLimits(0, 100);
  myPID.setSampleTime(CONTROL_PERIOD_MS);
  
  // NOTA: Dead Band removido para permitir acúmulo contínuo do termo integral
  // myPID.setDeadBand(-0.2, 0.2);  // DESABILITADO
  
  myPID.stop();
  myPID.reset();
  pidOutput = 0;
  
  // --- Mensagem de inicialização com parâmetros ---
  Serial.println("=====================================");
  Serial.println("TCC - Controlador PID do Forno");
  Serial.println("=====================================");
  Serial.print("Ganhos PID: Kp=");
  Serial.print(KP, 4);
  Serial.print(" Ki=");
  Serial.print(KI, 6);
  Serial.print(" Kd=");
  Serial.println(KD, 4);
  Serial.print("Janela PWM: ");
  Serial.print(CONTROL_PERIOD_MS);
  Serial.println(" ms");
  Serial.print("Taxa Rampa: ");
  Serial.print(RAMP_RATE_PER_SEC, 1);
  Serial.println(" C/s");
  Serial.println("=====================================");
  Serial.println("READY");
}

// =============================================================================
//   LOOP PRINCIPAL
// =============================================================================
void loop() {
  // 1. Processa comandos seriais
  handleSerialCommands();
  
  if (!testRunning) {
    digitalWrite(SSR_PIN, LOW);
    return;
  }
  
  // 2. Atualiza leitura do sensor
  currentCelsius = getOvenTemperature();
     
  // 3. Atualiza rampa de setpoint
  updateSetpointRamp();

  // 4. Calcula saída do PID
  myPID.compute();  
  
  // 5. Atua no SSR (time-proportioning)
  runSsrControl(pidOutput);
}

// =============================================================================
//   FUNÇÕES DE CONTROLE
// =============================================================================

/**
 * Atualiza o setpoint com rampa suave
 */
void updateSetpointRamp() {
  unsigned long currentMillis = millis();
  
  if (currentMillis - rampTimer >= 1000) {
    rampTimer = currentMillis;
    
    float maxChange = RAMP_RATE_PER_SEC * 1.0; 
  
    if (targetSetpoint > rampedSetpoint) {
      rampedSetpoint += maxChange;
      if (rampedSetpoint > targetSetpoint) {
        rampedSetpoint = targetSetpoint;
      }
    } 
    else if (targetSetpoint < rampedSetpoint) {
      rampedSetpoint -= maxChange;
      if (rampedSetpoint < targetSetpoint) {
        rampedSetpoint = targetSetpoint;
      }
    }
  }
}

/**
 * Interpreta comandos seriais do supervisório Python
 * 
 * COMANDOS SUPORTADOS:
 *   SET_SP,<valor>  - Define setpoint alvo (°C)
 *   START_TEST      - Inicia o controle PID
 *   STOP_TEST       - Para o controle PID
 *   GET_DATA        - Retorna dados atuais
 *   GET_CONFIG      - Retorna configuração do sistema
 */
void handleSerialCommands() {
  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    
    // SET_SP,<valor> - Define setpoint
    if (cmd.startsWith("SET_SP,")) {
      targetSetpoint = cmd.substring(7).toFloat();
      Serial.println("OK,SP_SET");
    }
    
    // START_TEST - Inicia o teste
    else if (cmd.equals("START_TEST")) {
      currentCelsius = getOvenTemperature();
      rampedSetpoint = currentCelsius;
      myPID.reset();
      myPID.start();
      
      rampTimer = millis();
      
      testRunning = true;
      Serial.println("OK,TEST_STARTED");
      
      // Log dos parâmetros no início do teste
      Serial.print("INFO,PID_CONFIG,");
      Serial.print(KP, 4);
      Serial.print(",");
      Serial.print(KI, 6);
      Serial.print(",");
      Serial.println(KD, 4);
    }
    
    // STOP_TEST - Para o teste
    else if (cmd.equals("STOP_TEST")) {
      myPID.stop();
      myPID.reset();
      testRunning = false;
      digitalWrite(SSR_PIN, LOW);
      targetSetpoint = getOvenTemperature();
      rampedSetpoint = targetSetpoint;
      Serial.println("OK,TEST_STOPPED");
    }
    
    // GET_DATA - Retorna dados atuais
    else if (cmd.equals("GET_DATA")) {
      // Formato: DATA,TempAtual,SetpointRampa,SaidaPID
      Serial.print("DATA,");
      Serial.print(currentCelsius, 2);
      Serial.print(",");
      Serial.print(rampedSetpoint, 2);
      Serial.print(",");
      Serial.println(pidOutput, 2);
    }
    
    // GET_CONFIG - Retorna configuração (para verificação)
    else if (cmd.equals("GET_CONFIG")) {
      Serial.print("CONFIG,KP=");
      Serial.print(KP, 4);
      Serial.print(",KI=");
      Serial.print(KI, 6);
      Serial.print(",KD=");
      Serial.print(KD, 4);
      Serial.print(",WINDOW=");
      Serial.print(CONTROL_PERIOD_MS);
      Serial.print(",RAMP=");
      Serial.println(RAMP_RATE_PER_SEC, 1);
    }
  }
}

/**
 * Controle Time-Proportioning do SSR
 * Converte a saída do PID (0-100%) em tempo ligado dentro da janela
 */
void runSsrControl(double dutyCycleOut) {
  unsigned long currentMillis = millis();

  if (currentMillis - ssrWindowStartTime >= CONTROL_PERIOD_MS) {
    ssrWindowStartTime = currentMillis;
  }

  unsigned long onTime_ms = (CONTROL_PERIOD_MS * dutyCycleOut) / 100.0;

  if (currentMillis - ssrWindowStartTime < onTime_ms) {
    digitalWrite(SSR_PIN, HIGH);
  } else {
    digitalWrite(SSR_PIN, LOW);
  }
}

// =============================================================================
//   FUNÇÕES DE LEITURA DO SENSOR
// =============================================================================

/**
 * Lê a temperatura do forno via NTC
 */
float getOvenTemperature() {
  float adc_avg = adc_read_averaged(NTC_PIN, ADC_SAMPLES);
  float r_ntc = ntc_resistance_from_adc(adc_avg);
  float celsius = ntc_temp_from_resistance(r_ntc);
  return celsius;
}

/**
 * Leitura ADC com média de múltiplas amostras
 */
float adc_read_averaged(int pin, int samples) {
  uint32_t sum = 0;
  for(int i = 0; i < samples; i++) {
    sum += analogRead(pin);
    delay(1); 
  }
  return (float)sum / (float)samples;
}

/**
 * Calcula resistência do NTC (método ratiométrico)
 * Circuito: VREF --- [R_DIVISOR] --- ADC_PIN --- [NTC] --- GND
 */
float ntc_resistance_from_adc(float adc_avg_val) {
  if (adc_avg_val >= ADC_MAX_VALUE - 1) {
    return 9999999.0f;
  }
  if (adc_avg_val < 1.0f) {
    return 0.1f;
  }

  float r_ntc = R_DIVISOR * (adc_avg_val / (ADC_MAX_VALUE - adc_avg_val));
  return r_ntc;
}

/**
 * Converte resistência em temperatura usando equação Beta
 */
float ntc_temp_from_resistance(float R_ntc) {
  const float T0_K = NTC_T_NOMINAL_C + 273.15f;
  float invT = 1.0f / T0_K + (1.0f / NTC_B_VALUE) * log(R_ntc / NTC_R_NOMINAL);
  float T_K = 1.0f / invT;
  return T_K - 273.15f;
}
