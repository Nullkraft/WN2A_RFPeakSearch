
//************************************************//
//  Name    : Function_Change_Variable_1.ino        //
//  Author  : WN2A                                //
//  Date    : 15 March 2021                          //
//  Version : 1.0             //
// Notes: There is no problem with this program as it is, because there is no problem calling 
// a Function: void Load1() or void Load2(), and changing one value in an array. But modifying the
// values of a whole array results in errors. There are two lines below commented out:
// see "Method of redefining Byte[] as array fails" . Enable these two lines and comment out the 
// two lines that redefine Byte[4]. You get error messages, they seem to relate to programming syntax,
// not related to scope.
// Changing multiple values of an array within a called function will help reduce program code, as re-use 
// can occur.

 int Byte[]={0xED,0x11,0x42,0x03,0xAA,0x05};// Declaring the Byte[] Array and its its initial values
 // int Byte[5]; // Alternate way of declaring Byte[] array, all clear to zero
void setup() {
  Serial.begin(9600);
  Serial.println ("Function_Change_Variable_1.ino  15 March 2021 ");
}


void loop() {

  Load1();  // calls Load1() for Value

  Transmit();//
  delay(1000);

  Load2();  // calls Load2() for Value

  Transmit();//
  delay(1000);  
}

void Transmit(){ 
  Serial.print ("Sent From ShiftL01 void Transmit()   Byte[4]= ");
  Serial.println (Byte[4]);
  Serial.println(" A single element of the array can be modified from a called function, no problem" );
  Serial.println(" But this doesn't work when trying to change the array values at once " );
  Serial.println ();
}

void Load1() {
 Byte[4]=0x11;  // This method works....but...
//  Byte[]={0xFF,0xFE,0xFD,0xDF,0xFC,0xFB};  // Method of redefining Byte[] as array fails
}

void Load2 () {
   Byte[4]=0x22; // This method works....but...
//  Byte[]={0x00,0x11,0x42,0x03,0xAA,0x05}; // Method of redefining Byte[] as array fails
}


