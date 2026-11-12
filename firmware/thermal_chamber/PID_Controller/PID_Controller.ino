/*
 * =============================================================================
 *  Burn-in oven PID controller, firmware 2.0
 * =============================================================================
 *  MCU: Arduino Nano 33 IoT (SAMD21). NTC on A0, SSR (through a TIP31) on A1.
 *
 *  CONTROL LAW (unchanged from the SBCCI 2026 runs, so results stay comparable):
 *    PID with fixed SIMC gains Kp = 2.78, Ki = 0.00106, Kd = 5.0 (FOPDT step test:
 *    K = 1.56 degC/%, theta = 150.6 s, tau = 1307.2 s), recomputed once per 5 s
 *    window (ArduPID 1.0.1 gates compute() on setDtMs), time-proportioning SSR
 *    with a 5 s window, setpoint ramp of 1 degC/s, output 0..100 %.
 *
 *  WHAT 2.0 ADDS (fpgaging-board-support SPEC §6.3):
 *    - safety checks in the firmware, each latching a fault that keeps the SSR off
 *      until CLEAR_FAULT: sensor fault (ADC near a rail, or temperature outside
 *      -20..200 degC), hard cutoff (OVEN_CUTOFF_C), no rise (output > 80 % for
 *      10 min with < 2 degC rise), optional host-silence timeout;
 *    - SAMD21 hardware watchdog (~4 s); the SSR pin is low from reset;
 *    - non-blocking temperature averaging (500 samples, 1 ms apart, as before), so
 *      commands are answered within milliseconds and the temperature is updated
 *      while idle too (1.x froze it at the boot value until START_TEST);
 *    - a reply to every command (ERR,UNKNOWN for unknown ones), setpoint range check,
 *      firmware version, calibration and safety settings in GET_CONFIG;
 *    - optional Steinhart-Hart NTC calibration and optional independent cutoff NTC.
 *
 *  PROTOCOL (115200 Bd, one command per line). Backwards compatible: old apps read
 *  the first four DATA fields and the KEY=VALUE pairs of CONFIG they know.
 *    GET_DATA                -> DATA,<temp>,<ramped sp>,<output %>,<state>,<fault>[,<cutoff temp>]
 *    SET_SP,<degC>           -> OK,SP_SET | ERR,RANGE
 *    START_TEST              -> OK,TEST_STARTED + INFO,PID_CONFIG,... | ERR,FAULT | ERR,NO_READING
 *    STOP_TEST               -> OK,TEST_STOPPED
 *    GET_CONFIG              -> CONFIG,KP=..,KI=..,KD=..,WINDOW=..,RAMP=..,FW=..,NTC_CAL=..,
 *                                CUTOFF=..,SP_MAX=..,HOSTTO=..
 *    SET_HOST_TIMEOUT,<min>  -> OK,HOSTTO | ERR,RANGE   (0 = hold the setpoint if the PC goes silent)
 *    CLEAR_FAULT             -> OK,FAULT_CLEARED | ERR,ACTIVE
 *    anything else           -> ERR,UNKNOWN
 *  <state> = IDLE | RUNNING | FAULT; <fault> = NONE | SENSOR | OVERTEMP | NO_RISE | HOST_SILENT
 *
 *  Build (arduino-cli; ArduHelpers 0.0.1 needs C++14 and <type_traits>):
 *    ./build.sh            or see build.sh for the command
 *  Bench checks before use: SAFETY.md.
 * =============================================================================
 */

#include <ArduPID.h>

// ============================================================================ build info
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
const long  CONTROL_PERIOD_MS = 5000;    // time-proportioning window and PID period
const float RAMP_RATE_PER_SEC = 1.0f;    // setpoint ramp
const double KP = 2.78;
const double KI = 0.00106;
const double KD = 5.0;

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

double currentCelsius = NAN;     // latest averaged reading (control NTC)
double cutoffCelsius = NAN;      // latest averaged reading (cutoff NTC, if fitted)
bool   haveReading = false;
bool   sensorBad = false;
double pidOutput = 0;
double rampedSetpoint = 25.0;
double targetSetpoint = 25.0;

ArduPID myPID;

unsigned long ssrWindowStartTime = 0;
unsigned long rampTimer = 0;
unsigned long lastCommandMs = 0;
unsigned int  hostTimeoutMin = 0;   // 0 = hold the setpoint when the PC goes silent

// non-blocking averaging
unsigned long lastSampleMs = 0;
uint32_t adcSum = 0, cutoffSum = 0;
int adcCount = 0;
float lastAdcAvg = 0;

// no-rise detection
bool noRiseArmed = false;
unsigned long noRiseStartMs = 0;
double noRiseStartC = 0;

// serial line buffer
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
  digitalWrite(SSR_PIN, LOW);
}

void latchFault(Fault f) {
  if (state == ST_FAULT) return;   // keep the first cause
  heaterOff();
  myPID.reset();
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
void updateSetpointRamp() {
  unsigned long currentMillis = millis();
  if (currentMillis - rampTimer >= 1000) {
    rampTimer = currentMillis;
    float maxChange = RAMP_RATE_PER_SEC * 1.0f;
    if (targetSetpoint > rampedSetpoint) {
      rampedSetpoint += maxChange;
      if (rampedSetpoint > targetSetpoint) rampedSetpoint = targetSetpoint;
    } else if (targetSetpoint < rampedSetpoint) {
      rampedSetpoint -= maxChange;
      if (rampedSetpoint < targetSetpoint) rampedSetpoint = targetSetpoint;
    }
  }
}

void runSsrControl(double dutyCycleOut) {
  unsigned long currentMillis = millis();
  if (currentMillis - ssrWindowStartTime >= (unsigned long)CONTROL_PERIOD_MS) {
    ssrWindowStartTime = currentMillis;
  }
  unsigned long onTime_ms = (CONTROL_PERIOD_MS * dutyCycleOut) / 100.0;
  digitalWrite(SSR_PIN, (currentMillis - ssrWindowStartTime < onTime_ms) ? HIGH : LOW);
}

// ============================================================================ commands
void printData() {
  Serial.print("DATA,");
  Serial.print(currentCelsius, 2);
  Serial.print(",");
  Serial.print(rampedSetpoint, 2);
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
  Serial.print("CONFIG,KP=");
  Serial.print(KP, 4);
  Serial.print(",KI=");
  Serial.print(KI, 6);
  Serial.print(",KD=");
  Serial.print(KD, 4);
  Serial.print(",WINDOW=");
  Serial.print(CONTROL_PERIOD_MS);
  Serial.print(",RAMP=");
  Serial.print(RAMP_RATE_PER_SEC, 1);
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
    rampedSetpoint = currentCelsius;
    myPID.reset();
    myPID.setSetpoint(rampedSetpoint);
    rampTimer = millis();
    noRiseArmed = false;
    state = ST_RUNNING;
    Serial.println("OK,TEST_STARTED");
    Serial.print("INFO,PID_CONFIG,");
    Serial.print(KP, 4);
    Serial.print(",");
    Serial.print(KI, 6);
    Serial.print(",");
    Serial.println(KD, 4);
  } else if (strcmp(cmd, "STOP_TEST") == 0) {
    myPID.reset();
    heaterOff();
    pidOutput = 0;
    if (state == ST_RUNNING) state = ST_IDLE;
    if (haveReading && !sensorBad) targetSetpoint = currentCelsius;
    rampedSetpoint = targetSetpoint;
    Serial.println("OK,TEST_STOPPED");
  } else if (strcmp(cmd, "GET_DATA") == 0) {
    printData();
  } else if (strcmp(cmd, "GET_CONFIG") == 0) {
    printConfig();
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
  while (!Serial) {}          // as in 1.x: the PC is required; the heater stays off meanwhile

  myPID.setTunings(KP, KI, KD);
  myPID.setOutputLimits(0, 100);
  myPID.setILimits(0, 100);
  myPID.setDtMs(CONTROL_PERIOD_MS);
  myPID.reset();
  pidOutput = 0;

  watchdogStart();
  lastCommandMs = millis();

  Serial.println("=====================================");
  Serial.println("Burn-in oven PID controller");
  Serial.print("FW ");
  Serial.println(FW_VERSION);
  Serial.print("PID gains: Kp=");
  Serial.print(KP, 4);
  Serial.print(" Ki=");
  Serial.print(KI, 6);
  Serial.print(" Kd=");
  Serial.println(KD, 4);
  Serial.print("PWM window: ");
  Serial.print(CONTROL_PERIOD_MS);
  Serial.println(" ms");
  Serial.print("Ramp: ");
  Serial.print(RAMP_RATE_PER_SEC, 1);
  Serial.println(" C/s");
  Serial.print("Cutoff: ");
  Serial.print(OVEN_CUTOFF_C, 1);
  Serial.println(" C");
  Serial.println("=====================================");
  Serial.println("READY");
}

void loop() {
  watchdogFeed();
  pollSerial();
  sampleTemperature();
  safetyChecks();

  if (state != ST_RUNNING) {
    heaterOff();
    return;
  }
  updateSetpointRamp();
  myPID.setSetpoint(rampedSetpoint);
  pidOutput = myPID.compute(currentCelsius);
  runSsrControl(pidOutput);
}
