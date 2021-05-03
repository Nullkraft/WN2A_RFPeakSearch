
//************************************************//
//  Name    : ShiftOut_Word_7-115.ino                 //
//  Author  : WN2A                                //
//  Date    : 29 Feb 2020                         //
//  Version : 1.0                                //
//  Notes   : Code for using ADF4356 Synth (14 Registers!)  115.2K //
//************************************************//

unsigned long z;
unsigned long q;
int (x);
String readString;
int latchPin = A0;  //LE
int clockPin = A2;  //SCLK
int dataPin = A1;   //DATA
int strobe = A3;  //STROBE

void setup() {
    //set pins to output because they are addressed in the main loop
  pinMode(latchPin, OUTPUT);
  pinMode(clockPin, OUTPUT);
  pinMode(dataPin, OUTPUT);  
  pinMode(strobe, OUTPUT);  
  Serial.begin(115200);
  Serial.println("ShiftOut_Word_7-115K.ino  29 Feb 2020 Takes U32 word from USB to SPI Bus ShiftOut 115200");
}
void loop() {
  
  while (Serial.available()) {
   delay(2);  //delay to allow byte to arrive in input buffer
   char c = Serial.read();
   readString += c;
 }
 if (readString.length() >0) {
   z=readString.toInt();
      readString=""; 
 // Serial.print ("Hex Value=");
     Serial.println (z,HEX);
      q=z/65536;
    //  Serial.println (q,HEX);  
  delayMicroseconds(1000);
     digitalWrite (strobe, LOW);
      digitalWrite (strobe, HIGH);
       delayMicroseconds(100);
         digitalWrite (strobe, LOW);
Shifty(x);
 }
}

 void Shifty(int x) {  //Send out 4 bytes then Latch 

     digitalWrite(latchPin, LOW);
  
     shiftOut(dataPin, clockPin, MSBFIRST,(q>>8)); 
     shiftOut(dataPin, clockPin, MSBFIRST,q); 
     shiftOut(dataPin, clockPin, MSBFIRST,(z>>8));
     shiftOut(dataPin, clockPin, MSBFIRST,z);
    delayMicroseconds(1); 
    digitalWrite(latchPin, HIGH);
    delayMicroseconds(20);
        digitalWrite(latchPin, LOW);
        delayMicroseconds(10);
  }
