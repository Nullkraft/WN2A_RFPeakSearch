
//************************************************//
//  Name    : MAX2871_V360MHz_R60MHz_6.ino        //
//  Author  : WN2A                                //
//  Date    : 16 June 2020                          //
//  Version : 1.0  See MAX2871_Alpha_Code_ReadMe.txt             //
//  Notes   : Alpha Code for using MAX2871 VCO=374.596154/187.827839 MHz REF=60MHz PFD=15 MHz //
//************************************************//
// Fixed Frequency= MHz, 60 MHz Reference. Codes for 6 total registers//
//Digital Lock Detect Enabled, 3.2mA Charge Pump,10 sec Code Refresh//
//            R0   R1   R2   R3   R4   R5  //

 int Byte0[]={0xD8,0xF9,0x42,0x03,0xFC,0x05}; //374.596154 MHz
 int Byte1[]={0xC8,0x7F,0x12,0x80,0xF1,0x00};
 int Byte2[]={0xC7,0x40,0x01,0x00,0xCF,0x40};
 int Byte3[]={0x00,0x20,0x58,0xF8,0x63,0x80};

 int Byte10[]={0xC0,0xF9,0x42,0x03,0xFC,0x05}; //187.827839 MHz
 int Byte11[]={0x2C,0x7F,0x12,0x80,0xF1,0x00};
 int Byte12[]={0x64,0x40,0x01,0x00,0xCF,0x40};
 int Byte13[]={0x00,0x20,0x58,0xF8,0x63,0x80};

//Pin connected to LE of MAX2871
int latchPin = 17;
//Pin connected to SCLK of MAX2871
int clockPin = 15;
////Pin connected to DATA of MAX2871
int dataPin =16;
// Pin for strobe at start of tranmission
int strobe = 12;  //temp
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
  Serial.println ("MAX2871_V360MHz_R60MHz_6.ino ");
  Serial.println("Code for using MAX2871 Synthesizer  Ref=60 MHz PFD=15MHz (6 Registers)");
  Serial.println("This version supports Lock Detect signal, Toggles 374.596154 /187.827839, etc more");
  digitalWrite(5, HIGH); //This Turns on the RF Output//
   
 // for loop counts backwards from Reg 5 to Reg 0 2X Per Spec Sheet //
  int y; //to count 0 to 1
  int x; //to count 5-4-3-2-1-0
  for (int y=1;y>=0;y--) {
  delay(1);
  //   digitalWrite (strobe, LOW); //Scope Trigger(Optional) 
  //    digitalWrite (strobe, HIGH);
  //    delayMicroseconds(1);
  //    digitalWrite (strobe, LOW);
     for (int x=5;x>=0;x--) {
     Shifty(x); //Initally 360MHz 
     delay(30) ; //delay between each register
    }
  }  
}

// Toggle Between 360/187.5MHz //
void loop() {
  int x=0 ;
   //   digitalWrite (strobe, HIGH);
   //   delayMicroseconds(20);
   //   digitalWrite (strobe, LOW); 
    Shifty(x);
    delay(5);    
   //   digitalWrite (strobe, HIGH);
  //    delayMicroseconds(20);
  //    digitalWrite (strobe, LOW);
    Shiftz(x);
    delay(5);    
     }

  void Shifty(int x) {  //Send out 32 bits (4 x 8-Bit Bytes) then Latch//
        digitalWrite (strobe, HIGH);
      delayMicroseconds(50);
      digitalWrite (strobe, LOW); 
     digitalWrite(latchPin, LOW);
     shiftOut(dataPin, clockPin, MSBFIRST,Byte3[x]);
     shiftOut(dataPin, clockPin, MSBFIRST,Byte2[x]);
     shiftOut(dataPin, clockPin, MSBFIRST,Byte1[x]);
     shiftOut(dataPin, clockPin, MSBFIRST,Byte0[x]);
    digitalWrite(latchPin, HIGH);
 //   delayMicroseconds(1);
        digitalWrite(latchPin, LOW);
              digitalWrite (strobe, HIGH);
      delayMicroseconds(10);
      digitalWrite (strobe, LOW); 
    //    delayMicroseconds(5);
  }
  
  void Shiftz(int x) {  //Send out 32 bits (4 x 8-Bit Bytes) then Latch//
     digitalWrite(latchPin, LOW);
     shiftOut(dataPin, clockPin, MSBFIRST,Byte13[x]);
     shiftOut(dataPin, clockPin, MSBFIRST,Byte12[x]);
     shiftOut(dataPin, clockPin, MSBFIRST,Byte11[x]);
     shiftOut(dataPin, clockPin, MSBFIRST,Byte10[x]);
  //  delayMicroseconds(1); 
    digitalWrite(latchPin, HIGH);
    delayMicroseconds(1);
        digitalWrite(latchPin, LOW);
   //   delayMicroseconds(5);
  }
