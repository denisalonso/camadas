// Transmissor por software (UART bit-banging)
// Paridade: par
// Baud: 9600
// TX pin: 8

const uint8_t txPin = 8;
const unsigned long baud = 9600;
const unsigned long bitPeriod = 1000000UL / baud; // micros por bit (~104)

void setup() {
  pinMode(txPin, OUTPUT);
  digitalWrite(txPin, HIGH); // linha idle = HIGH
}

// calcula paridade par: retorna 1 se número de 1s é ímpar (então paridade=1 para tornar total par)
uint8_t calculaParidade(uint8_t data) {
  uint8_t ones = 0;
  for (uint8_t i = 0; i < 8; ++i) if ((data >> i) & 0x01) ++ones;
  return ones & 0x01; // 1 se ímpar, 0 se par
}

// espera até micros() alcançar target, usando loop ativo (mais estável para timings curtos)
void esperaAte(unsigned long target) {
  // usa comparação com cast signed para lidar com wrap de micros()
  while ((long)(micros() - target) < 0) {
    asm volatile("nop");
  }
}

// envia um byte no formato: start(0) + 8 bits LSB->MSB + paridade + stop(1)
void enviaByte(uint8_t data) {
  unsigned long start = micros();

  // start bit (LOW)
  digitalWrite(txPin, LOW);
  esperaAte(start + bitPeriod);

  // bits de dados (LSB primeiro)
  for (uint8_t i = 0; i < 8; ++i) {
    uint8_t bit = (data >> i) & 0x01;
    digitalWrite(txPin, bit ? HIGH : LOW);
    esperaAte(start + bitPeriod * (i + 2)); // start consumed, this schedules successive bits
  }

  // bit de paridade (par)
  uint8_t par = calculaParidade(data);
  digitalWrite(txPin, par ? HIGH : LOW);
  esperaAte(start + bitPeriod * 10);

  // stop bit (HIGH)
  digitalWrite(txPin, HIGH);
  esperaAte(start + bitPeriod * 11); // garante stop pelo período do bit
}

void loop() {
  // exemplo: enviar sequência repetida de caracteres
  enviaByte('A');
  // pequeno intervalo entre frames (apenas para não saturar; não interfere no frame)
  delay(200);
}
