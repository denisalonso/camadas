const int txPin = 8;
const unsigned long baud = 19200;
const unsigned long bitPeriod = 1000000 / baud; // ~104 µs

void setup() {
  pinMode(txPin, OUTPUT);
  digitalWrite(txPin, HIGH);
}

uint8_t calculaParidade(uint8_t data) {
  uint8_t ones = 0;
  for (uint8_t i = 0; i < 8; ++i) if ((data >> i) & 0x01) ++ones;
  return ones & 0x01;
}

void enviaByte(uint8_t data) {
  // start
  digitalWrite(txPin, LOW);
  delayMicroseconds((unsigned int)bitPeriod);

  // dados
  for (uint8_t i = 0; i < 8; ++i) {
    digitalWrite(txPin, ((data >> i) & 0x01) ? HIGH : LOW);
    delayMicroseconds((unsigned int)bitPeriod);
  }

  // paridade
  digitalWrite(txPin, calculaParidade(data) ? HIGH : LOW);
  delayMicroseconds((unsigned int)bitPeriod);

  // stop
  digitalWrite(txPin, HIGH);
  delayMicroseconds((unsigned int)bitPeriod);
    delayMicroseconds((unsigned int)bitPeriod);
    delayMicroseconds((unsigned int)bitPeriod);
    delayMicroseconds((unsigned int)bitPeriod);
    
}

void loop() {
  enviaByte('A');
  enviaByte('B');
  enviaByte('C');
  delay(500);
}