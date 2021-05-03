/************************************************
 * Name    : MAX2871_Load_Word_4.ino
 * Author  : WN2A and Mark Stanley
 * Date    : 27 June 2020
 * Version : 1.0
 * Notes   : Code for using MAX2871 Synth (1 Register at a time)
 * Use with FreeBasic Program MAX2871_Command_4.bas
 *************************************************/

unsigned long z;
int latchPin = A3;  // MAX2871 LE
int dataPin = A2;   // MAX2871 DATA
int clockPin = A1;  // MAX2871 SCLK
int strobe = 10;    // MAX2871 STROBE
int RF_En = 5;      // MAX2871 RF_EN


void setup() {
  // set pins to output because they are addressed in the main loop
  pinMode(RF_En, OUTPUT);
  pinMode(latchPin, OUTPUT);
  pinMode(dataPin, OUTPUT);
  pinMode(clockPin, OUTPUT);
  pinMode(strobe, OUTPUT);
//  Serial.begin(230400);
  Serial.begin(38400);
//  Serial.println("MAX2871_Load_Word_115200_4.ino 2 July 2020");
  digitalWrite(RF_En, HIGH);      // Turn on the MAX2871 RF Output
  digitalWrite(latchPin, LOW);    // Latch must start LOW
  digitalWrite(strobe, LOW);      // Strobe must start LOW
  z = 0;
}


void loop() {
  if (Serial.available()) {
    z = Serial.parseInt();
  }

  if (z > 0) {
    setFrequency();
  }
}

// Load 4 control registers of the MAX2871 for setting the frequency
void setFrequency() {
  digitalWrite (strobe, HIGH);
  delayMicroseconds(10);
  digitalWrite (strobe, LOW);
  shiftOut(dataPin, clockPin, MSBFIRST, z >> 24);
  shiftOut(dataPin, clockPin, MSBFIRST, z >> 16);
  shiftOut(dataPin, clockPin, MSBFIRST, z >> 8);
  shiftOut(dataPin, clockPin, MSBFIRST, z);
//  delayMicroseconds(1);
  digitalWrite(latchPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(latchPin, LOW);
}
