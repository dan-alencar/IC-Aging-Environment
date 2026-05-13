#include <Arduino.h>
#include <stdarg.h>

/* =================================================================
   CONFIGURAÇÃO DE PINAGEM (ARDUINO NANO 33 IOT)
   =================================================================
   
   INTERFACE PC (USB):
   - Serial (USB Nativo) -> Monitor Serial do Computador
   
   INTERFACE SNIFFER (ALVO):
   - Objeto: Serial1
   - PINO FÍSICO RX: D0 (RX)  <-- CONECTE AQUI O SINAL DA FPGA
   - PINO FÍSICO TX: D1 (TX)  <-- Não conectado (apenas escuta)
   
   ATENÇÃO: Não use pinMode() nestes pinos após o begin!
   =================================================================
*/

// Configurações
#define TARGET_BAUD     125000 
#define LED_PIN         LED_BUILTIN // LED Laranja da placa (D13)

// --- PROTOCOLO ---
#define STM_SLAVE       0x00
#define STM_MASTER      0x80
#define FUNC_P          0x01
#define FUNC_M          0x02
#define FUNC_V          0x03
#define ERROR_MASK      0x70

// Buffers e Timers
uint8_t buffer[256];
int buf_index = 0;
unsigned long last_byte_time = 0;
const int TIMEOUT_RESET = 10; 

// Variáveis para o LED Heartbeat
unsigned long last_blink = 0;
bool led_state = false;

// --- FUNÇÃO AUXILIAR PRINTF ---
void debug_printf(const char *format, ...) {
  char buf[128];
  va_list args;
  va_start(args, format);
  vsnprintf(buf, sizeof(buf), format, args);
  va_end(args);
  Serial.print(buf);
}

void setup() {
  // 1. Configura LED para debug visual (Heartbeat)
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, HIGH); // Liga ao iniciar

  // 2. Inicia USB (PC)
  Serial.begin(115200);

  // 3. Inicia Hardware Serial (Sniffer)
  // No Nano 33 IoT, Serial1 é HARDWARE e está fixa em RX=0, TX=1
  Serial1.begin(TARGET_BAUD); 
  
  // *** CORREÇÃO CRÍTICA: ***
  // NÃO chame pinMode(0, INPUT) aqui! Isso desconecta a UART do pino no chip SAMD.
  // O Serial1.begin já configurou o multiplexador do pino corretamente.

  // Aguarda conexão USB (com timeout para não travar se usar bateria)
  unsigned long start_wait = millis();
  while (!Serial && millis() - start_wait < 3000);

  Serial.println("\n--- SNIFFER INICIADO (NANO 33 IOT) ---");
  Serial.println("STATUS: Aguardando dados...");
  digitalWrite(LED_PIN, LOW);
}

// --- CRC16 Modbus ---
uint16_t calc_crc16(const uint8_t *data, int len) {
    uint16_t crc = 0xFFFF;
    for (int i = 0; i < len; i++) {
        crc ^= data[i];
        for (int b = 0; b < 8; b++) {
            if (crc & 0x0001) crc = (crc >> 1) ^ 0xA001;
            else              crc >>= 1;
        }
    }
    return crc & 0xFFFF;
}

// --- DECODIFICADOR ---
void decode_packet(uint8_t *buf, int len) {
    // Pisca LED rápido ao decodificar pacote
    digitalWrite(LED_PIN, HIGH);
    
    if (len < 3) return;

    uint8_t ctrl = buf[0];
    uint16_t received_crc = buf[len-2] | (buf[len-1] << 8);
    uint16_t calculated_crc = calc_crc16(buf, len-2);
    bool crc_ok = (received_crc == calculated_crc);
    
    uint8_t direction = ctrl & 0x80;
    uint8_t func = ctrl & 0x03;
    uint8_t error = ctrl & ERROR_MASK;

    debug_printf("[%s] %s ", crc_ok ? "PROTO" : "CRC_ERR", direction == STM_MASTER ? "MST" : "SLV");

    if (error) {
        debug_printf("ERR:0x%02X ", error);
    } else {
        switch(func) {
            case FUNC_P:
                Serial.print("FUNC:Page ");
                if (len >= 4) debug_printf("Val:%c ", buf[1]);
                break;
            case FUNC_V:
                Serial.print("FUNC:Vcore ");
                if (len >= 7) {
                    char v_str[5];
                    memcpy(v_str, &buf[1], 4);
                    v_str[4] = 0;
                    debug_printf("Val:%sV ", v_str);
                }
                break;
            case FUNC_M:
                Serial.print("FUNC:Msg ");
                if (len >= 5) {
                    uint16_t msg_len = (buf[1] << 8) | buf[2]; 
                    debug_printf("Len:%d ", msg_len);
                }
                break;
            default:
                debug_printf("FUNC:UNK(0x%02X) ", func);
        }
    }
    Serial.println();
    digitalWrite(LED_PIN, LOW); // Apaga LED
}

void loop() {
  // --- Heartbeat (Pisca LED a cada 1s para indicar vida) ---
  if (millis() - last_blink > 1000) {
      last_blink = millis();
      led_state = !led_state;
      digitalWrite(LED_PIN, led_state);
  }

  // --- Leitura da UART ---
  if (Serial1.available()) {
    uint8_t b = Serial1.read();
    
    // Timeout para detectar fim de pacote ou lixo
    if (millis() - last_byte_time > TIMEOUT_RESET && buf_index > 0) {
        // Imprime RAW se não formou pacote válido (Debug de ruído)
        Serial.print("[RAW RX] ");
        for(int i=0; i<buf_index; i++) debug_printf("%02X ", buffer[i]);
        Serial.println();
        buf_index = 0;
    }
    
    last_byte_time = millis();
    
    if (buf_index < 255) {
        buffer[buf_index++] = b;
    }

    // Tenta identificar pacote válido
    if (buf_index > 0) {
        uint8_t func = buffer[0] & 0x03;
        bool packet_ready = false;

        if (func == FUNC_P && buf_index == 4) packet_ready = true;
        if (func == FUNC_V && buf_index == 7) packet_ready = true;
        if (func == FUNC_M && buf_index >= 5) {
             uint16_t expected_len = (buffer[1] << 8) | buffer[2];
             if (buf_index == (1 + 2 + expected_len + 2)) packet_ready = true;
        }

        if (packet_ready) {
            decode_packet(buffer, buf_index);
            buf_index = 0;
        }
    }
  }
}
