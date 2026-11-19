/*
  ESP32 como receptor UART do sensor de aging (DE10-Lite / MAX10)

  Pacote enviado pela FPGA (5 bytes, a cada 100 ms, 115200 baud, 8N1):
    byte 0: 0xAA (sincronismo)
    byte 1: slack_count[15:8]
    byte 2: slack_count[7:0]
    byte 3: status (bit0 alarm, bit1 calibrated, bit2 valid, bit3 sat_hi,
                    bit4 at_origin, bit5 timeout, bit6 pll_lost, bit7 seq)
    byte 4: checksum = byte1 ^ byte2 ^ byte3

  Ligacao (tudo em 3,3 V):
    FPGA JP1 pino 1 (PIN_V10, uart_txd)  ->  ESP32 GPIO25 (RX do Serial2)
    FPGA GND (JP1 pino 12 ou 30)         ->  ESP32 GND
  O TX do ESP32 (GPIO26) nao e usado: nao ligue nada nele. Cada placa fica ligada ao PC/fonte pelo proprio cabo USB.

  Abra o Monitor Serial do Arduino IDE em 115200 baud.
  Placa no IDE: "ESP32 Dev Module" (ou a sua).
*/

// ------------------------ PARSER (testado no PC) ------------------------
#include <math.h>
struct SensorFrame {
  unsigned int slack_count;
  unsigned char alarm;
  unsigned char calibrated;
  unsigned char valid, sat_hi, at_origin, timeout, pll_lost, seq;
};

struct FrameParser {
  unsigned char buf[5];
  unsigned char n = 0;

  // Alimenta 1 byte. Devolve true quando um pacote valido foi completado
  // (preenchido em 'out'). Um 0xAA dentro dos dados nao quebra o sincronismo:
  // se o checksum nao bater, descarta o 0xAA inicial e continua a partir do
  // proximo 0xAA que ja estiver no buffer.
  bool feed(unsigned char b, SensorFrame &out) {
    if (n == 0 && b != 0xAA) return false;      // espera o sincronismo
    buf[n++] = b;
    if (n < 5) return false;

    if ((unsigned char)(buf[1] ^ buf[2] ^ buf[3]) == buf[4]) {
      out.slack_count = ((unsigned int)buf[1] << 8) | buf[2];
      out.alarm       = buf[3] & 0x01;
      out.calibrated  = (buf[3] >> 1) & 0x01;
      out.valid       = (buf[3] >> 2) & 0x01;
      out.sat_hi      = (buf[3] >> 3) & 0x01;
      out.at_origin   = (buf[3] >> 4) & 0x01;
      out.timeout     = (buf[3] >> 5) & 0x01;
      out.pll_lost    = (buf[3] >> 6) & 0x01;
      out.seq         = (buf[3] >> 7) & 0x01;
      n = 0;
      return true;
    }
    // falso sincronismo: procura o proximo 0xAA dentro do que sobrou
    unsigned char i = 1;
    while (i < 5 && buf[i] != 0xAA) i++;
    n = 5 - i;
    for (unsigned char k = 0; k < n; k++) buf[k] = buf[i + k];
    return false;
  }
};
// Estatistica por janela de pacotes: da o sigma (em passos) que o relatorio
// pede no ensaio H3 (repetibilidade), sem precisar copiar milhares de linhas.
struct StatWindow {
  unsigned long total = 0, n = 0, invalid = 0, flagged = 0, seq_changes = 0;
  unsigned int mn = 0xFFFF, mx = 0;
  double sum = 0, sumsq = 0;
  int last_seq = -1;

  void add(const SensorFrame &f) {
    total++;
    if (f.sat_hi || f.at_origin || f.timeout || f.pll_lost) flagged++;
    if (last_seq >= 0 && (int)f.seq != last_seq) seq_changes++;
    last_seq = f.seq;
    if (!f.valid) { invalid++; return; }
    n++;
    if (f.slack_count < mn) mn = f.slack_count;
    if (f.slack_count > mx) mx = f.slack_count;
    sum   += f.slack_count;
    sumsq += (double)f.slack_count * f.slack_count;
  }
  double mean()  const { return n ? sum / n : 0.0; }
  double sigma() const {
    if (n < 2) return 0.0;
    double v = sumsq / n - mean() * mean();
    return v > 0 ? sqrt(v) : 0.0;
  }
  void reset() { unsigned long keep = last_seq; *this = StatWindow(); last_seq = (int)keep; }
};
// ---------------------- FIM DO PARSER (testado no PC) --------------------

#ifdef ARDUINO
constexpr int      RX_PIN  = 25;        // GPIO25 recebe o TX do FPGA
constexpr int      TX_PIN  = 26;        // so ocupa a configuracao; NAO ligue nada nele
constexpr uint32_t BAUD    = 115200;
constexpr float    STEP_PS = 178.571f;  // 1/8 do periodo do VCO de 700 MHz

FrameParser parser;
StatWindow  stats;
constexpr unsigned long WINDOW = 100;     // pacotes por resumo (100 pacotes = ~10 s)
#define PRINT_EACH_FRAME 0                 // 1 = imprime cada pacote (verboso)

void setup() {
  Serial.begin(115200);
  Serial2.begin(BAUD, SERIAL_8N1, RX_PIN, TX_PIN);   // so o RX e usado
  Serial.println("Aguardando pacotes do FPGA...");
}

void loop() {
  static uint32_t lastData = 0;
  static unsigned long totalBytes = 0;

  while (Serial2.available()) {
    unsigned char b = Serial2.read();
    totalBytes++;
    lastData = millis();
    SensorFrame f;
    if (parser.feed(b, f)) {
      stats.add(f);
#if PRINT_EACH_FRAME
      Serial.printf("slack_count=%u (0x%04X) = %.2f ns | valid=%u seq=%u calibrated=%u alarm=%u",
                    f.slack_count, f.slack_count,
                    f.slack_count * STEP_PS / 1000.0f,
                    (unsigned)f.valid, (unsigned)f.seq, (unsigned)f.calibrated, (unsigned)f.alarm);
      if (!f.valid)     Serial.print(" | INVALIDO");
      if (f.sat_hi)     Serial.print(" | SATURADO");
      if (f.at_origin)  Serial.print(" | ALARME_NA_ORIGEM");
      if (f.timeout)    Serial.print(" | TIMEOUT");
      if (f.pll_lost)   Serial.print(" | PLL_PERDEU_LOCK");
      Serial.println();
#endif
      if (stats.total >= WINDOW) {
        Serial.printf("[%lu pacotes] validos=%lu invalidos=%lu | min=%u max=%u media=%.2f sigma=%.2f passos (%.2f ps) | com_aviso=%lu trocas_de_seq=%lu\n",
                      stats.total, stats.n, stats.invalid, stats.n ? stats.mn : 0u, stats.mx,
                      stats.mean(), stats.sigma(), stats.sigma() * STEP_PS,
                      stats.flagged, stats.seq_changes);
        stats.reset();
      }
    }
  }

  // ajuda a diagnosticar quando nada chega
  static uint32_t lastWarn = 0;
  if (millis() - lastData > 3000 && millis() - lastWarn > 3000) {
    Serial.printf("(sem dados ha 3 s; bytes recebidos ate agora: %lu)\n", totalBytes);
    lastWarn = millis();
  }
}
#endif
