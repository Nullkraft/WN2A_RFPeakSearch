//************************************************//
//  Name    : Freq_Shift_3500_6500MHz_2.ino                                      //
//  Author  : WN2A                                                //
//  Date    : 21 Jan 2020                                          //
//  Version : 1.0                                                 //
//  Notes   : Code for using ADF4356 Synth (14 Registers!)        //
//************************************************//

// First Frequency= Codes for F1=3500/16=218.75MHz (14) registers//
//Digital Lock Detect Enabled, 900uA Charge Pump,100msec sec Code Ref//
//            R0   R1   R2   R3   R4   R5   R6   R7   R8   R9   R10  R11  R12  R13//
int F1B0[]={0x60,0x81,0xd2,0x03,0x84,0x25,0xF6,0xE7,0x68,0xC9,0xBA,0x0B,0xFC,0x0D};
int F1B1[]={0x09,0x26,0x05,0x00,0x89,0x00,0x20,0x00,0x65,0xFC,0x0E,0x20,0x15,0x00};
int F1B2[]={0x20,0x9A,0xE0,0x00,0x00,0x80,0x81,0x00,0x59,0x09,0xC0,0x61,0x00,0x00};
int F1B3[]={0x00,0x08,0x00,0x00,0x32,0x00,0x35,0x06,0x15,0x0F,0x00,0x00,0x00,0x00};

// Second Frequency= Codes for F2=6500/16=406.25MHz (14) registers//
//Digital Lock Detect Enabled, 900uA Charge Pump,100msec sec Code Ref//
//            R0   R1   R2   R3   R4   R5   R6   R7   R8   R9   R10  R11  R12  R13//
int F2B0[]={0x70,0x91,0xD2,0x03,0x84,0x25,0xF6,0xE7,0x68,0xC9,0xBA,0x0B,0xFC,0x0D};
int F2B1[]={0x11,0x47,0x05,0x00,0x89,0x00,0x20,0x00,0x65,0xFC,0x0E,0x20,0x15,0x00};
int F2B2[]={0x20,0x1E,0x2C,0x00,0x00,0x80,0x81,0x00,0x59,0x09,0xC0,0x61,0x00,0x00};
int F2B3[]={0x00,0x09,0x00,0x00,0x32,0x00,0x35,0x06,0x15,0x0F,0x00,0x00,0x00,0x00};

//Pin connected to LE of ADF4356
int latchPin = A0;
//Pin connected to SCLK of ADF4356
int clockPin = A2;
////Pin connected to DATA of ADF4356
int dataPin = A1;
// Pin for strobe at start of tranmission
int strobe = A3;

void setup() {
    //set pins to output because they are addressed in the main loop
  pinMode(latchPin, OUTPUT);
  pinMode(clockPin, OUTPUT);
  pinMode(dataPin, OUTPUT);  
  pinMode(strobe, OUTPUT);  
  Serial.begin(9600);
  Serial.println("Freq_Shift_3500_6500MHz_3.ino for ADF5356 PLL Lock Time tests RF Reduced Delays");
}
// for loop counts backwards from Reg 13 to Reg 0 //
  int MaxReg=13;
void loop() {
  int x;
  delayMicroseconds(1000);
     digitalWrite (strobe, LOW);
      digitalWrite (strobe, HIGH); //strobe for frame sync
       delayMicroseconds(1);
         digitalWrite (strobe, LOW);

 for (int x=MaxReg;x>=0;x--)
 ShiftF1(x);
  delay(20);
 MaxReg=2;
 for (int x=MaxReg;x>=0;x--)
 ShiftF2(x);
  delay(20);
}
  void ShiftF1(int x) {  //Send out 4 bytes then Latch 
    
    digitalWrite(latchPin, LOW);
     shiftOut(dataPin, clockPin, MSBFIRST,F1B3[x]);
     shiftOut(dataPin, clockPin, MSBFIRST,F1B2[x]);
     shiftOut(dataPin, clockPin, MSBFIRST,F1B1[x]);
     shiftOut(dataPin, clockPin, MSBFIRST,F1B0[x]);

    digitalWrite(latchPin, HIGH);
    delayMicroseconds(10);
    digitalWrite(latchPin, LOW);
    delayMicroseconds(5);
  }
  
    void ShiftF2(int x) {  //Send out 4 bytes then Latch 
    MaxReg=2;
    digitalWrite(latchPin, LOW);
     shiftOut(dataPin, clockPin, MSBFIRST,F2B3[x]);
     shiftOut(dataPin, clockPin, MSBFIRST,F2B2[x]);
     shiftOut(dataPin, clockPin, MSBFIRST,F2B1[x]);
     shiftOut(dataPin, clockPin, MSBFIRST,F2B0[x]);

    digitalWrite(latchPin, HIGH);
    delayMicroseconds(10);
    digitalWrite(latchPin, LOW);
    delayMicroseconds(5);
  }
  
  
