/*
 * TCC - FIRMWARE CONTROLADOR PID DO FORNO
 * MCU: Arduino Nano 33 IoT
 * OBJETIVO: Este firmware implementa o controlador PID sintonizado
 * para manter o forno em uma temperatura alvo (Setpoint).
 * * IMPLEMENTA:
 * 1. Ganhos PID (Kp, Ki, Kd) calculados via FOPDT/SIMC.
 * 2. Controle de SSR "Time-Proportioning" (PWM Lento).
 * 3. Rampa de Setpoint (para evitar overshoot).
 * 4. Anti-Windup (nativo da biblioteca PID).
 * 5. Leitura de NTC Ratiométrica (para precisão).
 * 6. Comandos seriais para controle via Python.
 */

// --- Inclusão da Biblioteca PID ---
#include <ArduPID.h>

// --- Pinos de Hardware ---
const int NTC_PIN = A0;   // Pino do sensor NTC do forno
const int SSR_PIN = A1;   // Pino de controle (via TIP31) para o SSR

// --- Constantes do ADC e NTC (Validadas) ---
const float VREF = 3.3f;            
const int   ADC_MAX_BITS = 12;      
const float ADC_MAX_VALUE = 4095.0f;  
const int   ADC_SAMPLES = 500;       // Aumentado para mais estabilidade
const float R_DIVISOR = 10000.0f;       
const float NTC_R_NOMINAL = 10000.0f;   
const float NTC_T_NOMINAL_C = 25.0f;    
const float NTC_B_VALUE = 3950.0f;      // (Ou 3380.0f, se você mudou)

// --- Parâmetros de Controle (JANELA DE 5 SEGUNDOS) ---
const long CONTROL_PERIOD_MS = 5000; // 5 segundos
const float RAMP_RATE_PER_SEC = 1.0f;  // Taxa da rampa: 0.1°C/seg (ou 6°C/min) 

// --- GANHOS PID (Calculados da sua análise SIMC) ---
const double KP = 2.78;
const double KI = 0.00106; // Testando Ki baixo
const double KD = 5.0; // Testando utilizar o Kd

// --- Variáveis Globais do PID ---
double currentCelsius;    // (Input) O que o forno ESTÁ
double pidOutput;         // (Output) O que o PID QUER (0-100%)
double rampedSetpoint;    // (Setpoint) O que o PID DEVE MIRAR agora

// Variável de controle do usuário
double targetSetpoint = 25.0; // O alvo final (ex: 125.0°C)
bool testRunning = false;

// Objeto PID
ArduPID myPID;

// --- Variáveis de Temporização ---
unsigned long ssrWindowStartTime = 0;
unsigned long pidCalcTimer = 0;

// =================================================================
//   SETUP
// =================================================================
void setup() {
  Serial.begin(115200);
  while (!Serial); // Espera o Python conectar
  
  analogReadResolution(ADC_MAX_BITS);
  
  pinMode(SSR_PIN, OUTPUT);
  digitalWrite(SSR_PIN, LOW);
  
  // --- Configuração do PID ---
  currentCelsius = getOvenTemperature(); // Leitura inicial
  rampedSetpoint = currentCelsius;       // Começa a rampa de onde estamos
  targetSetpoint = currentCelsius;
  
  // Define a janela de saída do PID (0% a 100%)
  // ISSO IMPLEMENTA O ANTI-WINDUP AUTOMATICAMENTE 
  myPID.begin(&currentCelsius, &pidOutput, &rampedSetpoint, KP, KI, KD);
  myPID.setOutputLimits(0, 100);
  myPID.setWindUpLimits(0, 100);
  myPID.setSampleTime(CONTROL_PERIOD_MS);
  myPID.setDeadBand(-0.2, 0.2);  // ignore small ±0.5°C fluctuations
  //myPID.setOutputRampRate(5); // limit rate of output change per cycle
  //myPID.setDerivativeFilter(0.8); // smooth derivative term
  myPID.stop();
  myPID.reset();

  pidOutput = 0;
  
  Serial.println("Arduino PID Controller Pronto.");
}

// =================================================================
//   LOOP PRINCIPAL
// =================================================================
void loop() {
  // 1. Processa comandos seriais vindos do Python
  handleSerialCommands();
  
  if (!testRunning) {
    digitalWrite(SSR_PIN, LOW); // Garante que SSR esteja desligado se o teste parar
    return;
  }
  
  unsigned long currentMillis = millis();

  // 2. Loop de Cálculo do PID (Roda a cada 5 segundos)
  //    A biblioteca PID_v1 gerencia isso internamente com SetSampleTime
  //    Mas precisamos da nossa própria lógica de rampa na mesma cadência.
  if (currentMillis - pidCalcTimer >= CONTROL_PERIOD_MS) {
    pidCalcTimer = currentMillis;

    // 2a. Ler a temperatura atual
    currentCelsius = getOvenTemperature();
    
    // 2b. Atualizar a Rampa de Setpoint 
    updateSetpointRamp();

    // 2c. Calcular a nova saída do PID
    myPID.compute(); 
  }

  // 3. Loop de Atuação do SSR (Roda continuamente)
  //    Usa o valor 'pidOutput' mais recente para controlar o SSR
  runSsrControl(pidOutput);
}

// =================================================================
//   FUNÇÕES DE CONTROLE
// =================================================================

/**
 * @brief Atualiza o 'rampedSetpoint' para subir/descer suavemente
 * em direção ao 'targetSetpoint'.
 */
void updateSetpointRamp() {
  float maxChange = RAMP_RATE_PER_SEC * (CONTROL_PERIOD_MS / 1000.0);

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

/**
 * @brief Interpreta os comandos de texto do Python.
 */
void handleSerialCommands() {
  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    
    // Ex: "SET_SP,125.0" (Define o Alvo Final)
    if (cmd.startsWith("SET_SP,")) {
      targetSetpoint = cmd.substring(7).toFloat();
      Serial.println("OK,SP_SET");
    }
    
    // Ex: "START_TEST" (Liga o PID e o relé do DUT)
    else if (cmd.equals("START_TEST")) {
      currentCelsius = getOvenTemperature();
      rampedSetpoint = currentCelsius; // Começa a rampa de onde estamos
      myPID.reset();
      myPID.start();
      testRunning = true;
      // (Aqui você também ligaria o relé de 3.3V do DUT)
      Serial.println("OK,TEST_STARTED");
    }
    
    // Ex: "STOP_TEST" (Desliga tudo)
    else if (cmd.equals("STOP_TEST")) {
      myPID.stop();
      myPID.reset();
      testRunning = false;
      digitalWrite(SSR_PIN, LOW);      // Garante SSR desligado
      targetSetpoint = getOvenTemperature();
      rampedSetpoint = targetSetpoint;
      Serial.println("OK,TEST_STOPPED");
    }
    
    // Ex: "GET_DATA" (Reporta o estado)
    else if (cmd.equals("GET_DATA")) {
      // Formato: "DATA,TempAtual,TempRampa,SaidaPID"
      Serial.print("DATA,");
      Serial.print(currentCelsius, 2);
      Serial.print(",");
      Serial.print(rampedSetpoint, 2);
      Serial.print(",");
      Serial.println(pidOutput, 2);
    }
  }
}

/**
 * @brief Executa a lógica de Time-Proportioning (PWM Lento) para o SSR.
 * [cite: 604-608]
 */
void runSsrControl(double dutyCycleOut) {
  unsigned long currentMillis = millis();

  // Reinicia a janela de 5 segundos se ela tiver terminado
  if (currentMillis - ssrWindowStartTime >= CONTROL_PERIOD_MS) {
    ssrWindowStartTime = currentMillis;
  }

  // Calcula quanto tempo (ms) o SSR deve ficar LIGADO dentro desta janela
  unsigned long onTime_ms = (CONTROL_PERIOD_MS * dutyCycleOut) / 100.0;

  // Lógica de acionamento do SSR
  if (currentMillis - ssrWindowStartTime < onTime_ms) {
    digitalWrite(SSR_PIN, HIGH);
  } else {
    digitalWrite(SSR_PIN, LOW);
  }
}

// =================================================================
//   FUNÇÕES DE LEITURA DO SENSOR (Validadas)
// =================================================================

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

/**
 * @brief Calcula a resistência do NTC (Ratiométrico)
 * @note  Assume o circuito "Pull-Down": 
 * VREF --- [R_DIVISOR] --- ADC_PIN --- [NTC] --- GND
 */
float ntc_resistance_from_adc(float adc_avg_val) {
  if (adc_avg_val >= ADC_MAX_VALUE - 1) {
    return 9999999.0f; // Resistência quase infinita
  }
  if (adc_avg_val < 1.0f) {
    return 0.1f; // Evita divisão por zero
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
  const float T0_K = NTC_T_NOMINAL_C + 273.15f;
  float invT = 1.0f / T0_K + (1.0f / NTC_B_VALUE) * log(R_ntc / NTC_R_NOMINAL);
  float T_K = 1.0f / invT;
  return T_K - 273.15f;
}