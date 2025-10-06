// Receptor por software (UART bit-banging)
// Paridade: par
// Baud: 9600
// RX pin: 7
// Imprime no Serial Monitor (USB) resultados

const uint8_t rxPin = 7;
const unsigned long baud = 9600;
const unsigned long bitPeriod = 1000000UL / baud; // micros por bit (~104)

// calcula paridade par: retorna 1 se número de 1s é ímpar
uint8_t calculaParidade(uint8_t data) {
  uint8_t ones = 0;
  for (uint8_t i = 0; i < 8; ++i) if ((data >> i) & 0x01) ++ones;
  return ones & 0x01;
}

void esperaAte(unsigned long target) {
  while ((long)(micros() - target) < 0) {
    asm volatile("nop");
  }
}

// função que bloqueia até detectar start bit (queda para LOW)
void esperaStart() {
  while (digitalRead(rxPin) == HIGH) {
    asm volatile("nop");
  }
}

// lê um byte com amostragem no centro de cada bit
// retorna o byte lido e também valida paridade/stop (printa no Serial)
uint8_t recebeByte() {
  // espera start (queda)
  esperaStart();
  unsigned long t0 = micros(); // instante em que se detectou a borda (queda)

  // queremos amostrar o primeiro bit de dado no centro do primeiro data bit:
  // centro do primeiro data bit = t0 + 1.5 * bitPeriod
  unsigned long sampleTime = t0 + (bitPeriod * 3) / 2;

  uint8_t data = 0;

  // ler 8 bits, amostrando a cada bitPeriod a partir de sampleTime
  for (uint8_t i = 0; i < 8; ++i) {
    esperaAte(sampleTime);
    int b = digitalRead(rxPin);
    if (b) data |= (1 << i); // LSB first
    sampleTime += bitPeriod;
  }

  // agora amostra bit de paridade
  esperaAte(sampleTime);
  int paridadeRecebida = digitalRead(rxPin);
  sampleTime += bitPeriod;

  // amostra stop bit
  esperaAte(sampleTime);
  int stopBit = digitalRead(rxPin);
  sampleTime += bitPeriod;

  // valida paridade
  uint8_t paridadeEsperada = calculaParidade(data);
  if (paridadeRecebida != paridadeEsperada) {
    Serial.print("PARITY ERROR: ");
    Serial.print((int)paridadeRecebida);
    Serial.print(" expected ");
    Serial.print((int)paridadeEsperada);
    Serial.print("  char: ");
    Serial.println((char)data);
  } else if (stopBit == LOW) {
    Serial.print("STOP BIT ERROR  char: ");
    Serial.println((char)data);
  } else {
    Serial.print("Recebido OK: ");
    Serial.println((char)data);
  }

  return data;
}

void setup() {
  pinMode(rxPin, INPUT);
  Serial.begin(9600);
  // espera Serial estabilizar
  while (!Serial) { ; }
  Serial.println("Receptor pronto - aguardando...");
}

void loop() {
  recebeByte();
  // não colocar delay aqui; função já sincroniza por micros()
}