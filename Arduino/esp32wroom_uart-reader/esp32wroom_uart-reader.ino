#include <HardwareSerial.h>

// --- PIN CONFIGURATION FOR ESP32 WROOM ---
const int RX_PIN = 16; // RX2 (Connect to FPGA TX)
const int TX_PIN = 17; // TX2 (Connect to FPGA RX)

// O sistema todo foi alinhado para 125000 bps
const int TARGET_BAUD_RATE = 125000; 

// Instance UART2
HardwareSerial SerialSTM(2); 

void setup() {
  // USB Serial (PC Connection)
  // A velocidade aqui não é crítica para USB nativo, mas definimos igual para consistência
  Serial.begin(115200); 
  
  // UART2 Serial (FPGA/STM Connection)
  SerialSTM.begin(TARGET_BAUD_RATE, SERIAL_8N1, RX_PIN, TX_PIN);

  // NOTA: Não imprimimos mensagens de "Started" aqui porque isso
  // sujaria o protocolo que o Python está tentando ler.
}

void loop() {
  // 1. Sentido: PC (USB) -> FPGA (UART2)
  // Se o Python enviar comandos (Headers 0x10/0x20 + Dados), repassa imediatamente
  while (Serial.available()) {
    SerialSTM.write(Serial.read());
  }

  // 2. Sentido: FPGA (UART2) -> PC (USB)
  // Se a FPGA enviar respostas (Ticks, Acks), repassa imediatamente para o Python ler
  while (SerialSTM.available()) {
    Serial.write(SerialSTM.read());
  }
  
  // Pequeno yield para não travar o watchdog da ESP32 se não houver tráfego
  // (embora o HardwareSerial já gerencie bem)
  yield();
}
