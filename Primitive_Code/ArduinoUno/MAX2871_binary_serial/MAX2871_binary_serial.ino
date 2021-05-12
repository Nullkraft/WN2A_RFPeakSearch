/************************************************
 * Name    : MAX2871_Load_Word_4.ino
 * Author  : WN2A and Mark Stanley
 * Date    : 27 June 2020
 * Version : 1.0
 * Notes   : Code for using MAX2871 Synth (1 Register at a time)
 * Use with FreeBasic Program MAX2871_Command_4.bas
 * 
 * See: https://os.mbed.com/users/MI/code/max2871/#b47819dab536
 * This link is a C++ source and header file implementing all(?)
 * the functions of the MAX2871
 * 
 *************************************************/

int latchPin = A3;  // MAX2871 LE
int dataPin = A2;   // MAX2871 DATA
int clockPin = A1;  // MAX2871 SCLK
int strobe = 10;    // MAX2871 STROBE
int RF_En = 5;      // MAX2871 RF_EN

int LED = 13;

//const unsigned int bytesInWord = 4;
const unsigned int numBytesInReg = 4;     // buffer is 'numBytesInReg' bytes long
byte reg[numBytesInReg];

unsigned int pulseWidth = 1;

void setup() {
  Serial.begin(2000000);
//  Serial.println("MAX2871_Load_Word_115200_4.ino 2 July 2020");
  // set pins to output because they are addressed in the main loop
  pinMode(RF_En, OUTPUT);
  pinMode(latchPin, OUTPUT);
  pinMode(dataPin, OUTPUT);
  pinMode(clockPin, OUTPUT);
  pinMode(strobe, OUTPUT);
  pinMode(LED, OUTPUT);
  digitalWrite(LED, LOW);         // Turn off the LED
  digitalWrite(RF_En, HIGH);      // Turn on the MAX2871 RF Output
  digitalWrite(latchPin, LOW);    // Latch must start LOW
  digitalWrite(strobe, LOW);      // Strobe must start LOW

  Serial.setTimeout(5);
}


void loop() {
  if (Serial.available()) {
    Serial.readBytes(reg, numBytesInReg);
  
    // ******* DON'T ADD ANYTHING BETWEEN THESE LINES *********
    digitalWrite (strobe, HIGH);
    digitalWrite (strobe, LOW);
    for (int j=0; j<numBytesInReg; j++) {
      shiftOut(dataPin, clockPin, MSBFIRST, reg[j]);
    }
    digitalWrite(latchPin, HIGH);
    digitalWrite(latchPin, LOW);
    // ********************************************************
  }
}
