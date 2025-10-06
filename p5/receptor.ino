const int rxPin = 7;          
const unsigned int baud = 9600;
const unsigned int bitPeriod = 1000000 / baud;

void setup() {
  pinMode(rxPin, INPUT);
  Serial.begin(9600); // usa UART nativa só pro debug com o PC
}

int calculaParidade(byte data) {
  int ones = 0;
  for (int i = 0; i < 8; i++) {
    if ((data >> i) & 0x01) ones++;
  }
  return ones % 2;
}

byte recebeByte() {
  byte data = 0;

  while (digitalRead(rxPin) == HIGH); // espera start bit (queda para 0)

  delayMicroseconds(bitPeriod + bitPeriod/2); // pula metade + 1 bit p/ centro do bit 0

  for (int i = 0; i < 8; i++) {               // lê 8 bits (LSB→MSB)
    int bitVal = digitalRead(rxPin);
    data |= (bitVal << i);
    delayMicroseconds(bitPeriod);
  }

  int paridadeRecebida = digitalRead(rxPin);  // lê bit de paridade
  delayMicroseconds(bitPeriod);

  int stopBit = digitalRead(rxPin);           // lê stop bit (esperado = 1)
  delayMicroseconds(bitPeriod);

  int paridadeEsperada = calculaParidade(data);
  if (paridadeRecebida != paridadeEsperada) {
    Serial.print("Erro de paridade! Recebido: ");
    Serial.println((char)data);
  } else {
    Serial.print("Recebido OK: ");
    Serial.println((char)data);
  }

  return data;
}

void loop() {
  recebeByte();
}