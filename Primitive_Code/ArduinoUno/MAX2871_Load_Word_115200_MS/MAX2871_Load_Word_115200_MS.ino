////MAX2871_Load_Word_115200_MS//


//*********** parseInt_example.ino ****************************************
unsigned long q, last_q;
unsigned char byte3, byte2, byte1, byte0;     // Demonstrates parsing of 32 bit word
unsigned char byte_array[4];                        // for testing readBytesUntil() function
 
void setup() {
  Serial.begin(115200);
  q = last_q = 0;
}

void loop() {
  if (Serial.available()) {
    unsigned long t_start = micros();
    q = Serial.parseInt();                                           //  868 uS for 4 bytes
    // Serial.readBytesUntil('\n', byte_array, 4);          // 2800 uS for 4 bytes
    unsigned long t_stop = micros();
    Serial.print("Serial.parseInt() consumes ");
    Serial.print(t_stop - t_start);
    Serial.println(" microseconds.");
    byte3 = q>>24;
    byte2 = q>>16;
    byte1 = q>>8;
    byte0 = q;
  }

  if (q > 0) {
    Serial.println(q);
    Serial.print("byte3 = ");
    Serial.println(byte3);
    Serial.print("byte2 = ");
    Serial.println(byte2);
    Serial.print("byte1 = ");
    Serial.println(byte1);
    Serial.print("byte0 = ");
    Serial.println(byte0);
  }
 
}
//************* End example **************************************************