/*
 * Código de Teste "Blink" para o SSR
 *
 * OBJETIVO:
 * Este código apenas liga e desliga o pino D2 a cada 1 segundo.
 * Ele serve para verificar se o seu circuito com o transistor TIP31
 * está montado corretamente.
 *
 * O QUE VOCÊ DEVE VER:
 * O LED no seu relé SSR deve acender por 1 segundo e apagar por 1 segundo,
 * repetidamente.
 */

// Pino de controle que vai para o Resistor de 1k -> Base do TIP31
const int SSR_PIN = A1;

void setup() {
  // Configura o pino do SSR como saída
  pinMode(SSR_PIN, OUTPUT);
  
  // Inicia o monitor serial para vermos o que está acontecendo
  Serial.begin(115200);
  
  // Espera o monitor serial conectar (importante para o Nano 33 IoT)
  while (!Serial);
  
  Serial.println("Iniciando teste de Blink do SSR...");
}

void loop() {
  // 1. Liga o pino
  digitalWrite(SSR_PIN, HIGH);
  Serial.println("Pino D2: HIGH (SSR deve estar LIGADO)");
  
  // 2. Espera 1 segundo
  delay(1000);

  // 3. Desliga o pino
  digitalWrite(SSR_PIN, LOW);
  Serial.println("Pino D2: LOW (SSR deve estar DESLIGADO)");
  
  // 4. Espera 1 segundo
  delay(1000);
}