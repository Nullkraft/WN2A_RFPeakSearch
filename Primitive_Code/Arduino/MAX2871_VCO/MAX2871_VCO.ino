/*  Simulate an RF noise spectrum with a signal and harmonic at bins 100 and 200.
 * This is to create a serial stream for testing the Python software that will be 
 * used for running Project #3, the spectrum analyzer.
 * 
 * To reach max serial speeds it is necessary to write more than a single byte at
 * a time.  A chunk of 32 bytes is transferred as a block.  By experimention it
 * was found that a 32 byte chunk provides the greatest improvement in the data
 * transfer rate.
 */

#define EOS 0xFF        // 0xFF is reserved for EOS (End Of Serial transmission)

int latchPin = A3;  // MAX2871 LE
int dataPin = A2;   // MAX2871 DATA
int clockPin = A1;  // MAX2871 SCLK
int strobe = 10;    // MAX2871 STROBE
int RF_En = 5;      // MAX2871 RF_EN

const unsigned int numBytesInReg = 4;
byte buff[numBytesInReg] = {0};

const int szChunk = 32;
byte numChunks = 0;
byte numBlocks;
byte chunk[szChunk];

unsigned int rfNoise;
byte* noiseByte = (byte *) &rfNoise;

char commandChar;

unsigned int chunkIndex = 0;  // Track which chunk is being used
byte frequencyInHz[3];


void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, HIGH);
  pinMode(RF_En, OUTPUT);
  pinMode(latchPin, OUTPUT);
  pinMode(dataPin, OUTPUT);
  pinMode(clockPin, OUTPUT);
  pinMode(strobe, OUTPUT);
  digitalWrite(RF_En, HIGH);      // Turn on the MAX2871 RF Output
  digitalWrite(latchPin, LOW);    // Latch must start LOW
  digitalWrite(strobe, LOW);      // Strobe must start LOW

  Serial.begin(2000000);
  Serial.setTimeout(5);
  randomSeed(analogRead(A0));
}



void loop() {
  if (Serial.available() > 0) {
    commandChar = Serial.read();
    switch(commandChar) {
      case '1': case '2': case '3': case '4': case '5':  case '6':
        numBlocks = commandChar - '0';       // byte numBlocks = atoi(commandChar);
        numChunks = numBlocks * 512/szChunk;
        chunkIndex = numChunks;
        break;
      case 'r':
        // register reg[] 
        Serial.readBytes(buff, numBytesInReg);
        writeToVCO(buff, numBytesInReg);
        break;
      case 'l':
        digitalWrite(LED_BUILTIN, LOW);   // Built-in LED OFF
        break;
      case 'L':
        digitalWrite(LED_BUILTIN, HIGH);  // Built-in LED ON
        break;
      case 'e':
        digitalWrite(RF_En, LOW);         // RF Output OFF
        break;
      case 'E':
        digitalWrite(RF_En, HIGH);        // RF Output ON
        break;
      case 'F':
        // Get target frequency in Hz (because binary) from PC
        // Limit floats to 6 decimal places to avoid rounding errors
        Serial.readBytes(frequencyInHz, 3);
        frequencyToRegisterValues(frequencyInHz);
        break;
      case 'S':
        hwState();
        break;
      default:
        break;
    }
  }

  /* chunkIndex gets the same index as the active chunk. As long
   * as it stays above 0 the next chunk will be created and sent.
   */
  if (chunkIndex) {
    simRF();
    writeToHost();
  }
}


void readFromVCO() {
  // pass
}


/* Time to program the MAX2871 chip to make it do what you want.
 *  This is basically a software SPI to the max chip.
*/
void writeToVCO(byte *selectedRegister, unsigned int numBytesToWrite) {
  digitalWrite (strobe, HIGH);
  digitalWrite (strobe, LOW);

  for (int j=0; j<numBytesToWrite; j++) {
    shiftOut(dataPin, clockPin, MSBFIRST, selectedRegister[j]);
  }
  
  digitalWrite(latchPin, HIGH);
  digitalWrite(latchPin, LOW);
}


/* Given a frequency generate the register values for the MAX2871
 * based on the refClock, lockDetect and fracOpt settings.
 */
void frequencyToRegisterValues(int frequencyInHz) {
  double target_frequency = pow(frequencyInHz, 6);
  Serial.println(target_frequency, 6);
}


/*
 * You must fill the chunk array with data before calling this function.
 */
void writeToHost() {
  if(Serial.availableForWrite() > 0) {
    Serial.write(chunk, szChunk);
  }

  /* Send the End-Of-Stream marker 0xFF/0xFF after all the other chunks. It's
   * a double byte of 0xFF because the A/D uses less than 16 bits. That means
   * the full-scale value of the A/D (0xFF/0xC0) is less than the EOS marker.
   */
  if (chunkIndex == 0) {
    Serial.write(EOS);
    Serial.write(EOS);
  }
}



/*
 * Simulate a series of RF test data for testing the Spectrum Analyzer 
 * plotting program written in python.
 */
void simRF() {
  unsigned int i = numChunks - chunkIndex;
  unsigned int index;
  unsigned int spur = 255; //(numChunks * szChunk) / 2;

  chunkIndex--;
  
  // Fill a buffer with szChunk number of bytes.
  for(int j=0; j<szChunk; j+=2) {
    rfNoise = random(analogRead(A0));
    rfNoise = rfNoise<<4;             // Use top 12 bits of RF amplitude value
    
    index = (i*szChunk+j)>>1;         // Convert 8bit index into a 16bit index

    if(index == random(spur)) {       // Create a random spur
      rfNoise = random(250, 3000);    // Randomly select an amplitude for this spur
      rfNoise = rfNoise<<4;
    }

    if(index==100) { rfNoise = 250; }      // Create the fundamental
    if(index==200) { rfNoise = 250<<4; }   // Create the harmonic

    chunk[j] = noiseByte[0];      // Buffer HIGH Byte for rfNoise
    chunk[j+1] = noiseByte[1];    // Buffer LOW Byte for rfNoise
  }
}


void hwState() {
  // Report back the state of RF_En.
  if(Serial.availableForWrite() > 0) {
    byte enable = digitalRead(RF_En);
    int mux_value = analogRead(A0);
    Serial.write(enable);
  }
}
