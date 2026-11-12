/*
 * =============================================================================
 *  Burn-in oven BANG-BANG controller (baseline), firmware 2.0
 * =============================================================================
 *  MCU: Arduino Nano 33 IoT (SAMD21). NTC on A0, SSR on A1.
 *
 *  CONTROL LAW (unchanged): heater on below SP - HYST_LOW, off above SP + HYST_HIGH,
 *  one decision per second on the 500-sample averaged temperature.
 *
 *  Firmware 2.0 shares the safety layer and protocol additions of PID_Controller 2.0
 *  (fpgaging-board-support SPEC §6.3): latched sensor / cutoff / no-rise / host-silence
 *  faults, hardware watchdog, non-blocking averaging (temperature updated while idle),
 *  a reply to every command, setpoint range check, version and safety settings in
 *  GET_CONFIG. The shared code is copied from PID_Controller.ino; keep the two in step.
 *
 *  PROTOCOL: as PID_Controller 2.0, plus GET_STATS. CONFIG starts with TYPE=BANGBANG.
 *    GET_DATA  -> DATA,<temp>,<sp>,<0|100>,<state>,<fault>[,<cutoff temp>]
 *    GET_STATS -> STATS,CYCLES=..,DUTY=..,CPM=..,ELAPSED_S=..
 * =============================================================================
 */

#include <Arduino.h>

static const char FW_VERSION[] = "2.0.0";

// ============================================================================ hardware
const int NTC_PIN = A0;            // oven NTC (control)
const int SSR_PIN = A1;            // SSR drive, HIGH = heater on
const int CUTOFF_NTC_PIN = -1;     // independent cutoff NTC (e.g. A2); -1 = not fitted

// ============================================================================ NTC
const float ADC_MAX_VALUE = 4095.0f;
const int   ADC_SAMPLES = 500;           // samples per reading, 1 ms apart (as in 1.x)
const float R_DIVISOR = 10000.0f;        // VREF -- R_DIVISOR -- ADC -- NTC -- GND
const float NTC_R_NOMINAL = 10000.0f;
const float NTC_T_NOMINAL_C = 25.0f;
const float NTC_B_VALUE = 3950.0f;

// Steinhart-Hart calibration (1/T = A + B ln R + C ln^3 R, T in K). Fill in from a
// three-point calibration against a reference thermometer (SAFETY.md) and set
// USE_STEINHART_HART = true; NTC_CAL names the calibration in GET_CONFIG.
const bool  USE_STEINHART_HART = false;
const double SH_A = 0.0, SH_B = 0.0, SH_C = 0.0;
static const char NTC_CAL[] = "BETA3950";

// ============================================================================ control (unchanged)
const float HYSTERESIS_HIGH = 2.0f;   // off when T > SP + HYST_HIGH
const float HYSTERESIS_LOW  = 2.0f;   // on  when T < SP - HYST_LOW
const long  SAMPLE_INTERVAL_MS = 1000;

// ============================================================================ safety
const float OVEN_SP_MIN_C = 20.0f;
const float OVEN_SP_MAX_C = 130.0f;
const float OVEN_CUTOFF_C = 140.0f;      // latched; the oven coasts ~14 degC after a stop
const float SENSOR_MIN_C = -20.0f;
const float SENSOR_MAX_C = 200.0f;
const float ADC_RAIL_MARGIN = 0.01f * ADC_MAX_VALUE;   // within 1 % of a rail = open/short
const float NO_RISE_OUTPUT_PCT = 80.0f;
const unsigned long NO_RISE_WINDOW_MS = 10UL * 60UL * 1000UL;
const float NO_RISE_MIN_C = 2.0f;
const float CLEAR_MARGIN_C = 5.0f;       // CLEAR_FAULT needs the oven this far below the cutoff
const unsigned int HOST_TIMEOUT_MAX_MIN = 1440;

// ============================================================================ state
enum State : uint8_t { ST_IDLE, ST_RUNNING, ST_FAULT };
enum Fault : uint8_t { F_NONE, F_SENSOR, F_OVERTEMP, F_NO_RISE, F_HOST_SILENT };
static const char *const STATE_NAME[] = {"IDLE", "RUNNING", "FAULT"};
static const char *const FAULT_NAME[] = {"NONE", "SENSOR", "OVERTEMP", "NO_RISE", "HOST_SILENT"};

State state = ST_IDLE;
Fault fault = F_NONE;

double currentCelsius = NAN;
double cutoffCelsius = NAN;
bool   haveReading = false;
bool   sensorBad = false;
double pidOutput = 0;            // 0 or 100: the heater duty, named as in the PID sketch
double targetSetpoint = 25.0;
bool   ssrState = false;

unsigned long lastCommandMs = 0;
unsigned int  hostTimeoutMin = 0;
unsigned long lastDecisionMs = 0;

// statistics (GET_STATS, as in 1.x)
unsigned long cycleCount = 0, totalOnTime = 0, testStartTime = 0;

unsigned long lastSampleMs = 0;
uint32_t adcSum = 0, cutoffSum = 0;
int adcCount = 0;
float lastAdcAvg = 0;

bool noRiseArmed = false;
unsigned long noRiseStartMs = 0;
double noRiseStartC = 0;

char line[48];
uint8_t lineLen = 0;
bool lineOverflow = false;

// ============================================================================ watchdog (SAMD21)
// GCLK4 = OSCULP32K / 32 = 1024 Hz; WDT period 4096 cycles = 4 s.
void watchdogStart() {
  GCLK->GENDIV.reg = GCLK_GENDIV_ID(4) | GCLK_GENDIV_DIV(4);
  GCLK->GENCTRL.reg = GCLK_GENCTRL_ID(4) | GCLK_GENCTRL_GENEN | GCLK_GENCTRL_SRC_OSCULP32K |
                      GCLK_GENCTRL_DIVSEL;
  while (GCLK->STATUS.bit.SYNCBUSY) {}
  GCLK->CLKCTRL.reg = GCLK_CLKCTRL_ID_WDT | GCLK_CLKCTRL_CLKEN | GCLK_CLKCTRL_GEN_GCLK4;
  while (GCLK->STATUS.bit.SYNCBUSY) {}
  WDT->CTRL.reg = 0;
  while (WDT->STATUS.bit.SYNCBUSY) {}
  WDT->CONFIG.reg = WDT_CONFIG_PER_4K;
  WDT->CTRL.reg = WDT_CTRL_ENABLE;
  while (WDT->STATUS.bit.SYNCBUSY) {}
}

void watchdogFeed() {
  if (!WDT->STATUS.bit.SYNCBUSY) WDT->CLEAR.reg = WDT_CLEAR_CLEAR_KEY;
}

// ============================================================================ NTC conversion
float ntcResistance(float adc) {
  return R_DIVISOR * (adc / (ADC_MAX_VALUE - adc));
}

float ntcCelsius(float adc) {
  float r = ntcResistance(adc);
  if (USE_STEINHART_HART) {
    double lnr = log(r);
    return (float)(1.0 / (SH_A + SH_B * lnr + SH_C * lnr * lnr * lnr) - 273.15);
  }
  const float T0_K = NTC_T_NOMINAL_C + 273.15f;
  float invT = 1.0f / T0_K + (1.0f / NTC_B_VALUE) * log(r / NTC_R_NOMINAL);
  return 1.0f / invT - 273.15f;
}

bool adcPlausible(float adc) {
  return adc > ADC_RAIL_MARGIN && adc < ADC_MAX_VALUE - ADC_RAIL_MARGIN;
}

// one sample per millisecond; a new averaged reading every ADC_SAMPLES samples
void sampleTemperature() {
  unsigned long now = millis();
  if (now - lastSampleMs < 1) return;
  lastSampleMs = now;
  adcSum += analogRead(NTC_PIN);
  if (CUTOFF_NTC_PIN >= 0) cutoffSum += analogRead(CUTOFF_NTC_PIN);
  if (++adcCount < ADC_SAMPLES) return;

  float avg = (float)adcSum / ADC_SAMPLES;
  float cavg = (float)cutoffSum / ADC_SAMPLES;
  adcSum = cutoffSum = 0;
  adcCount = 0;
  lastAdcAvg = avg;

  bool ok = adcPlausible(avg);
  float t = ok ? ntcCelsius(avg) : NAN;
  if (ok && (t < SENSOR_MIN_C || t > SENSOR_MAX_C)) ok = false;
  if (CUTOFF_NTC_PIN >= 0) {
    bool cok = adcPlausible(cavg);
    float ct = cok ? ntcCelsius(cavg) : NAN;
    if (!cok || ct < SENSOR_MIN_C || ct > SENSOR_MAX_C) ok = false;
    cutoffCelsius = ct;
  }
  sensorBad = !ok;
  currentCelsius = t;
  haveReading = true;
}

// ============================================================================ safety
void heaterOff() {
  ssrState = false;
  digitalWrite(SSR_PIN, LOW);
}

void latchFault(Fault f) {
  if (state == ST_FAULT) return;   // keep the first cause
  heaterOff();
  pidOutput = 0;
  fault = f;
  state = ST_FAULT;
  noRiseArmed = false;
  Serial.print("EVENT,FAULT,");
  Serial.println(FAULT_NAME[f]);
}

void safetyChecks() {
  if (!haveReading) return;
  if (sensorBad) { latchFault(F_SENSOR); return; }
  float hottest = currentCelsius;
  if (CUTOFF_NTC_PIN >= 0 && cutoffCelsius > hottest) hottest = cutoffCelsius;
  if (hottest > OVEN_CUTOFF_C) { latchFault(F_OVERTEMP); return; }
  if (state != ST_RUNNING) return;

  if (hostTimeoutMin > 0 && millis() - lastCommandMs > (unsigned long)hostTimeoutMin * 60000UL) {
    latchFault(F_HOST_SILENT);
    return;
  }
  // no rise: output high for a whole window without the oven warming up
  if (pidOutput > NO_RISE_OUTPUT_PCT) {
    if (!noRiseArmed) {
      noRiseArmed = true;
      noRiseStartMs = millis();
      noRiseStartC = currentCelsius;
    } else if (millis() - noRiseStartMs >= NO_RISE_WINDOW_MS) {
      if (currentCelsius - noRiseStartC < NO_RISE_MIN_C) { latchFault(F_NO_RISE); return; }
      noRiseStartMs = millis();          // it did rise: start a new window
      noRiseStartC = currentCelsius;
    }
  } else {
    noRiseArmed = false;
  }
}

// ============================================================================ control (as in 1.x)
void setSsr(bool on) {
  ssrState = on;
  pidOutput = on ? 100.0 : 0.0;
  digitalWrite(SSR_PIN, on ? HIGH : LOW);
}

void bangBangStep() {
  unsigned long now = millis();
  if (now - lastDecisionMs < (unsigned long)SAMPLE_INTERVAL_MS) return;
  lastDecisionMs = now;
  if (currentCelsius < targetSetpoint - HYSTERESIS_LOW) {
    if (!ssrState) {
      setSsr(true);
      cycleCount++;
    }
  } else if (currentCelsius > targetSetpoint + HYSTERESIS_HIGH) {
    if (ssrState) setSsr(false);
  }
  if (ssrState) totalOnTime += SAMPLE_INTERVAL_MS;
}

// ============================================================================ commands
void printData() {
  Serial.print("DATA,");
  Serial.print(currentCelsius, 2);
  Serial.print(",");
  Serial.print(targetSetpoint, 2);
  Serial.print(",");
  Serial.print(pidOutput, 2);
  Serial.print(",");
  Serial.print(STATE_NAME[state]);
  Serial.print(",");
  Serial.print(FAULT_NAME[fault]);
  if (CUTOFF_NTC_PIN >= 0) {
    Serial.print(",");
    Serial.print(cutoffCelsius, 2);
  }
  Serial.println();
}

void printConfig() {
  Serial.print("CONFIG,TYPE=BANGBANG,HYST_HIGH=");
  Serial.print(HYSTERESIS_HIGH, 1);
  Serial.print(",HYST_LOW=");
  Serial.print(HYSTERESIS_LOW, 1);
  Serial.print(",SAMPLE_MS=");
  Serial.print(SAMPLE_INTERVAL_MS);
  Serial.print(",FW=");
  Serial.print(FW_VERSION);
  Serial.print(",NTC_CAL=");
  Serial.print(NTC_CAL);
  Serial.print(",CUTOFF=");
  Serial.print(OVEN_CUTOFF_C, 1);
  Serial.print(",SP_MAX=");
  Serial.print(OVEN_SP_MAX_C, 1);
  Serial.print(",HOSTTO=");
  Serial.print(hostTimeoutMin);
  Serial.print(",CUTOFF_NTC=");
  Serial.println(CUTOFF_NTC_PIN >= 0 ? "YES" : "NO");
}

void printStats() {
  unsigned long elapsed = millis() - testStartTime;
  float duty = (elapsed > 0) ? (100.0 * totalOnTime / elapsed) : 0.0;
  float cpm = (elapsed > 60000) ? (cycleCount * 60000.0 / elapsed) : 0.0;
  Serial.print("STATS,CYCLES=");
  Serial.print(cycleCount);
  Serial.print(",DUTY=");
  Serial.print(duty, 1);
  Serial.print(",CPM=");
  Serial.print(cpm, 2);
  Serial.print(",ELAPSED_S=");
  Serial.println(elapsed / 1000);
}

bool parseFloatArg(const char *s, float &out) {
  char *end;
  out = strtof(s, &end);
  return end != s && *end == '\0';
}

void handleCommand(const char *cmd) {
  lastCommandMs = millis();
  if (strncmp(cmd, "SET_SP,", 7) == 0) {
    float v;
    if (!parseFloatArg(cmd + 7, v) || v < OVEN_SP_MIN_C || v > OVEN_SP_MAX_C) {
      Serial.println("ERR,RANGE");
      return;
    }
    targetSetpoint = v;
    Serial.println("OK,SP_SET");
  } else if (strcmp(cmd, "START_TEST") == 0) {
    if (state == ST_FAULT) { Serial.println("ERR,FAULT"); return; }
    if (!haveReading || sensorBad) { Serial.println("ERR,NO_READING"); return; }
    cycleCount = 0;
    totalOnTime = 0;
    testStartTime = millis();
    lastDecisionMs = millis() - SAMPLE_INTERVAL_MS;   // decide at once, as 1.x did
    noRiseArmed = false;
    state = ST_RUNNING;
    Serial.println("OK,TEST_STARTED");
    Serial.print("INFO,BANGBANG_CONFIG,HYST_HIGH=");
    Serial.print(HYSTERESIS_HIGH, 1);
    Serial.print(",HYST_LOW=");
    Serial.println(HYSTERESIS_LOW, 1);
  } else if (strcmp(cmd, "STOP_TEST") == 0) {
    setSsr(false);
    if (state == ST_RUNNING) state = ST_IDLE;
    printStats();
    Serial.println("OK,TEST_STOPPED");
  } else if (strcmp(cmd, "GET_DATA") == 0) {
    printData();
  } else if (strcmp(cmd, "GET_CONFIG") == 0) {
    printConfig();
  } else if (strcmp(cmd, "GET_STATS") == 0) {
    printStats();
  } else if (strncmp(cmd, "SET_HOST_TIMEOUT,", 17) == 0) {
    float v;
    if (!parseFloatArg(cmd + 17, v) || v < 0 || v > HOST_TIMEOUT_MAX_MIN || v != (float)(int)v) {
      Serial.println("ERR,RANGE");
      return;
    }
    hostTimeoutMin = (unsigned int)v;
    Serial.println("OK,HOSTTO");
  } else if (strcmp(cmd, "CLEAR_FAULT") == 0) {
    bool causeGone = haveReading && !sensorBad && currentCelsius < OVEN_CUTOFF_C - CLEAR_MARGIN_C;
    if (state == ST_FAULT && !causeGone) { Serial.println("ERR,ACTIVE"); return; }
    fault = F_NONE;
    state = ST_IDLE;
    Serial.println("OK,FAULT_CLEARED");
  } else {
    Serial.println("ERR,UNKNOWN");
  }
}

// non-blocking line reader (1.x used readStringUntil, which waits up to 1 s)
void pollSerial() {
  while (Serial.available() > 0) {
    char c = (char)Serial.read();
    if (c == '\n' || c == '\r') {
      if (lineOverflow) {
        Serial.println("ERR,UNKNOWN");
      } else if (lineLen > 0) {
        line[lineLen] = '\0';
        handleCommand(line);
      }
      lineLen = 0;
      lineOverflow = false;
    } else if (lineLen < sizeof(line) - 1) {
      line[lineLen++] = c;
    } else {
      lineOverflow = true;
    }
  }
}

// ============================================================================ setup / loop
void setup() {
  pinMode(SSR_PIN, OUTPUT);
  heaterOff();
  analogReadResolution(12);
  Serial.begin(115200);
  while (!Serial) {}
  watchdogStart();
  lastCommandMs = millis();
  Serial.println("=============================================");
  Serial.println("Burn-in oven BANG-BANG controller (baseline)");
  Serial.print("FW ");
  Serial.println(FW_VERSION);
  Serial.print("Hysteresis: +");
  Serial.print(HYSTERESIS_HIGH, 1);
  Serial.print("C / -");
  Serial.print(HYSTERESIS_LOW, 1);
  Serial.println("C");
  Serial.print("Cutoff: ");
  Serial.print(OVEN_CUTOFF_C, 1);
  Serial.println(" C");
  Serial.println("=============================================");
  Serial.println("READY");
}

void loop() {
  watchdogFeed();
  pollSerial();
  sampleTemperature();
  safetyChecks();
  if (state != ST_RUNNING) {
    if (ssrState) setSsr(false);
    heaterOff();
    return;
  }
  bangBangStep();
}
