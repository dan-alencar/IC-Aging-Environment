// --- Pinos de Hardware ---
const int NTC_PIN = 19;         // pino A0; Pino do sensor NTC do forno
const int SSR_PIN = 5;         // pino D2; Pino que aciona o Relé de Estado Sólido (SSR)

// --- Parâmetros de Controle ---
const long TIME_PROPORTIONING_WINDOW = 5000; // Janela de 5 segundos (5000 ms)
float dutyCycle = 0.0;                       // (0.0 a 100.0)
bool testRunning = false;

// --- Variáveis de Temporização ---
unsigned long ssrWindowStartTime = 0;
String serialBuffer = "";

void setup() {
  Serial.begin(115200); // Inicia comunicação serial com o PC (Python)
  pinMode(SSR_PIN, OUTPUT);
  digitalWrite(SSR_PIN, LOW);
  serialBuffer.reserve(50); // Reserva espaço para comandos seriais
}

void loop() {
  // 1. Processa Comandos Seriais (vindo do Python)
  //    Não bloqueante!
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n') {
      processCommand(serialBuffer);
      serialBuffer = "";
    } else {
      serialBuffer += c;
    }
  }

  // 2. Executa o Controle Time-Proportioning (se o teste estiver rodando)
  //    [cite: 604-608]
  if (testRunning) {
    unsigned long currentMillis = millis();

    // Se a janela de 5s terminou, reinicia
    if (currentMillis - ssrWindowStartTime >= TIME_PROPORTIONING_WINDOW) {
      ssrWindowStartTime = currentMillis; // Reinicia a janela
    }

    // Calcula quanto tempo o SSR deve ficar ligado nesta janela
    unsigned long onTime = (TIME_PROPORTIONING_WINDOW * dutyCycle) / 100.0;

    // Lógica do SSR: LIGA no início, DESLIGA após o onTime
    if (currentMillis - ssrWindowStartTime < onTime) {
      digitalWrite(SSR_PIN, HIGH);
    } else {
      digitalWrite(SSR_PIN, LOW);
    }
  }
}

// --- Funções de Comando ---

void processCommand(String cmd) {
  cmd.trim(); // Limpa espaços em branco

  // Ex: "SET_DUTY,50.0"
  if (cmd.startsWith("SET_DUTY,")) {
    dutyCycle = cmd.substring(9).toFloat();
    testRunning = true;
    ssrWindowStartTime = millis(); // Inicia o controle
    Serial.println("OK");
  }
  
  // Ex: "STOP_TEST"
  else if (cmd.equals("STOP_TEST")) {
    testRunning = false;
    dutyCycle = 0.0;
    digitalWrite(SSR_PIN, LOW); // Garante que o forno desligue
    Serial.println("OK");
  }
  
  // Ex: "GET_DATA"
  else if (cmd.equals("GET_DATA")) {
    // Apenas envia a temperatura do forno.
    // (O loop de proteção com T_dut e I_dut será adicionado depois)
    
    // TODO: Adicionar sua lógica de leitura do NTC (média, etc.)
    int sensorRaw = analogRead(NTC_PIN); 
    float tempC = convertRawToCelsius(sensorRaw); // Função que você precisa criar
    
    // Formato: "DATA,TEMP_FORNO"
    Serial.print("DATA,");
    Serial.println(tempC);
  }
}

// Função de exemplo - você deve substituir pela calibração do seu NTC
float convertRawToCelsius(int raw) {
  // (Esta é uma lógica de placeholder. Use a tabela do seu NTC)
  float temp = (raw / 1023.0) * 100.0; 
  return temp;
}