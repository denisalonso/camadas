const int txPin = 8;          
const unsigned int baud = 9600;
const unsigned int bitPeriod = 1000000 / baud; // ~104 µs

void setup() {
  pinMode(txPin, OUTPUT);
  digitalWrite(txPin, HIGH); // linha idle = HIGH
}

int calculaParidade(byte data) {
  int ones = 0;
  for (int i = 0; i < 8; i++) {
    if ((data >> i) & 0x01) ones++;
  }
  return ones % 2; // 1 se número de 1s ímpar
}

void enviaByte(byte data) {
  digitalWrite(txPin, LOW);             // start bit = 0
  delayMicroseconds(bitPeriod);

  for (int i = 0; i < 8; i++) {        // 8 bits de dados (LSB→MSB)
    digitalWrite(txPin, (data >> i) & 0x01);
    delayMicroseconds(bitPeriod);
  }

  int paridade = calculaParidade(data); // bit de paridade par
  digitalWrite(txPin, paridade);
  delayMicroseconds(bitPeriod);

  digitalWrite(txPin, HIGH);            // stop bit = 1
  delayMicroseconds(bitPeriod);
}

void loop() {
  enviaByte('A');
  enviaByte('B');
  enviaByte('C');
  delay(500);
}