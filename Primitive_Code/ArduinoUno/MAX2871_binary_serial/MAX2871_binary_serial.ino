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

#define MAXBLOCKS 6
#define EOS 0x255       // 0x255 is reserved for EOS (End Of Serial transmission)
#define DATA_MAX 0x254  // Maximum allowed byte value for *ANY* data

static bool start_stream = false;      // Data streaming request flag
byte szChunk = 32;
byte numChunks = MAXBLOCKS * 512/szChunk;
static unsigned int chunkCount = numChunks;  // Track which chunk is being used

int latchPin = A3;  // MAX2871 LE
int dataPin = A2;   // MAX2871 DATA
int clockPin = A1;  // MAX2871 SCLK
int strobe = 10;    // MAX2871 STROBE
int RF_En = 5;      // MAX2871 RF_EN

int LED = 13;

//const unsigned int bytesInWord = 4;
const unsigned int bufLength = 4;     // buffer is 'bufLength' bytes long
byte reg[bufLength];

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
}


void program_max2871() {
  if (Serial.available()) {
    Serial.readBytes(reg, bufLength);
  
    // ******* DON'T ADD ANYTHING BETWEEN THESE LINES *********
    digitalWrite (strobe, HIGH);
    digitalWrite (strobe, LOW);
    for (int j=0; j<bufLength; j++) {
      shiftOut(dataPin, clockPin, MSBFIRST, reg[j]);
    }
    digitalWrite(latchPin, HIGH);
    digitalWrite(latchPin, LOW);
    // ********************************************************
  }
}

// Called when serial data is available for reading
void serialEvent() {
  char commandChar = Serial.read();
  
  switch(commandChar) {
    case '\n':
      break;
    case 'a':
      digitalWrite(LED, !digitalRead(LED));
//      start_stream = true;
      break;
    case 'b':
      program_max2871();
      break;
    case '1': case '2': case '3': case '4': case '5':  case '6':
      byte numBlocks = commandChar - '0';       // byte numBlocks = atoi(commandChar);
      numChunks = numBlocks * 512/szChunk;
      chunkCount = numChunks;
      break;
    default:
//      numChunks = MAXBLOCKS * 512/szChunk;
      break;
  }
}
