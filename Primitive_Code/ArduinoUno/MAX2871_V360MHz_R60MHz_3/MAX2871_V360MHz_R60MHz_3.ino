
//************************************************//
//  Name    : MAX2871_V360MHz_R60MHz_3.ino        //
//  Author  : WN2A                                //
//  Date    : 16 June 2020                          //
//  Version : 1.0  See MAX2871_Alpha_Code_ReadMe.txt             //
//  Notes   : Alpha Code for using MAX2871 VCO=360MHz REF=60MHz PFD=15 MHz //
//************************************************//
// Fixed Frequency= MHz, 60 MHz Reference. Codes for 6 total registers//
//Digital Lock Detect Enabled, 3.2mA Charge Pump,10 sec Code Refresh//
//            R0   R1   R2   R3   R4   R5  //
int Byte0[]={0x00,0x61,0x42,0x03,0xFC,0x05};
int Byte1[]={0x00,0x00,0x12,0x00,0xF1,0x00};
int Byte2[]={0xC0,0x40,0x01,0x01,0xCF,0x40};
int Byte3[]={0x00,0x00,0x34,0xF8,0x63,0x80};
//Pin connected to LE of MAX2871
int latchPin = 17;
//Pin connected to SCLK of MAX2871
int clockPin = 15;
////Pin connected to DATA of MAX2871
int dataPin =16;
// Pin for strobe at start of tranmission
int strobe = 10;  //temp
int LD; //Lock Detect

void setup() {
    //set pins to output because they are addressed in the main loop
  pinMode(latchPin, OUTPUT);
  pinMode(clockPin, OUTPUT);
  pinMode(dataPin, OUTPUT);  
  pinMode(strobe, OUTPUT);  
  pinMode(13,OUTPUT);
  pinMode(5,OUTPUT); //RF_En//
  pinMode(2, INPUT);//Lock Detect//
  Serial.begin(9600);
  Serial.println ("MAX2871_V360MHz_R60MHz_3.ino ");
  Serial.println("Code for using MAX2871 Synthesizer Vco=360MHz Ref=60 MHz PFD=15MHz (6 Registers)");
  Serial.println("This version supports Lock Detect signal and more");
  digitalWrite(5, HIGH); //This Turns on the RF Output//
}
// for loop counts backwards from Reg 5 to Reg 0 //
void loop() {
    digitalWrite(13,HIGH);
     LD= digitalRead(3);
     if (LD ==  LOW) {
  digitalWrite (13, LOW);
  int x;
  delayMicroseconds(1000);
     digitalWrite (strobe, LOW);
      digitalWrite (strobe, HIGH);
       delayMicroseconds(1);
         digitalWrite (strobe, LOW);
 for (int x=5;x>=0;x--)
     Shifty(x);
   // delay(1000);
     }
}

  void Shifty(int x) {  //Send out (4) 8-Bit Bytes then Latch//
     digitalWrite(latchPin, LOW);
     shiftOut(dataPin, clockPin, MSBFIRST,Byte3[x]);
     shiftOut(dataPin, clockPin, MSBFIRST,Byte2[x]);
     shiftOut(dataPin, clockPin, MSBFIRST,Byte1[x]);
     shiftOut(dataPin, clockPin, MSBFIRST,Byte0[x]);
    delayMicroseconds(1); 
    digitalWrite(latchPin, HIGH);
    delayMicroseconds(10);
        digitalWrite(latchPin, LOW);
        delayMicroseconds(50);
  }
