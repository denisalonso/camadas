byte byteRead;


void setup() {
  // configura a comunicacao com serial baud rate de 9600
  Serial.begin(9600);
}

void loop() {
  if (Serial.available()) //se tiverem dados disponíveis para leitura
  {
    byteRead = Serial.read(); // le o byte mais recente no buffer da serial
    Serial.write(byteRead);   // reenvia para o pc o dado recebido
  }

}
