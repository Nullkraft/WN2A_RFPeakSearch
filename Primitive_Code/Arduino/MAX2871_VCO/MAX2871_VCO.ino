/*  Simulate an RF noise spectrum with a signal and harmonic at bins 100 and 200.
 * This is to create a serial stream for testing the Python software that will be 
 * used for running Project #3, the spectrum analyzer.
 * 
 * To reach max serial speeds it is necessary to write more than a single byte at
 * a time.  A chunk of 32 bytes is transferred as a block.  By experimention it
 * was found that a 32 byte chunk provides the greatest improvement in the data
 * transfer rate.
 */

#define EOS     0xFF  // 0xFF is reserved for End Of Serial transmission (EOS)
#define HIGH_Z   0    // Put MUX in High Z mode
#define MUX_VDD  1    // Put MUX in VDD mode
#define MUX_GND  2    // Put MUX in GND mode
#define MUX_READ 3    // Put MUX in Read mode

int latchPin = A3;  // MAX2871 LE
int dataPin = A2;   // MAX2871 DATA
int clockPin = A1;  // MAX2871 SCLK
int RF_En = 5;      // MAX2871 RF_EN

const unsigned int numBytesInReg = 4;
byte spiBuff[numBytesInReg] = {0};

const int szChunk = 32;
byte numChunks = 0;
byte numBlocks;
byte chunk[szChunk];

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
  digitalWrite(RF_En, HIGH);      // Turn on the MAX2871 RF Output
  digitalWrite(latchPin, LOW);    // Latch must start LOW

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
      case 'r':    // Program MAX2871 to a new output frequency
        Serial.readBytes(spiBuff, numBytesInReg);
        writeToVCO(spiBuff, numBytesInReg);
        break;
      case 'l':                   // Turn off built-in LED
        digitalWrite(LED_BUILTIN, LOW);
        break;
      case 'L':                   // Turn on built-in LED
        digitalWrite(LED_BUILTIN, HIGH);
        break;
      case 'e':                   // Disable RF output
        digitalWrite(RF_En, LOW);
        break;
      case 'E':                   // Enable RF output
        digitalWrite(RF_En, HIGH);
        break;
      case 'F':
        // Get target frequency in Hz (because binary) from PC.
        // IMPORTANT: 6-decimal places or get rounding errors.
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

/* Bits MUX[3:0] set the MUX pin.
 *  MUX[3] is bit 18 in reg5 and is named MUX MSB, 
 *  while MUX[2:0] are bits 28:26 in reg2 and are
 *  named MUX Configuration.
 *  
 *  From reg2 settings:
 *  Sets MUX pin mode (MSB bit located register 05).
 *  0000 = Three-state output
 *  0001 = D_VDD
 *  0010 = D_GND
 *  0011 = R-divider output    
 *  0100 = N-divider output/2    
 *  0101 = Analog lock detect    
 *  0110 = Digital lock detect    
 *  0111 = Sync Input    
 *  1000 to 1011 = Reserved    
 *  1100 = Read SPI registers 06    
 *  1101 to 1111= Reserved
 */
void muxPinMode(byte mode) {
  switch (mode) {
    case HIGH_Z:      // Set all to zero
      Serial.println("setting MUX to High Z ...");
      spiBuff[3] = 0x00;
      spiBuff[2] = 0x00;
      spiBuff[1] = 0x00;
      spiBuff[0] = 0x05;    // reg addr 5
      writeToVCO( spiBuff, numBytesInReg);  // 00_00_00_05
      spiBuff[0] = 0x02;    // reg addr 2
      writeToVCO( spiBuff, numBytesInReg);  // 00_00_00_02
      break;
    case MUX_VDD:
      Serial.println("setting MUX to VDD ...");
      spiBuff[3] = 0x02;
      spiBuff[2] = 0x00;
      spiBuff[1] = 0x00;
      spiBuff[0] = 0x02;    // reg addr 2
      writeToVCO(spiBuff, numBytesInReg);  // 02_00_00_02
      break;
    case MUX_GND:
      Serial.println("setting MUX to GND ...");
      spiBuff[3] = 0x04;
      spiBuff[2] = 0x00;
      spiBuff[1] = 0x00;
      spiBuff[0] = 0x02;    // reg addr 2
      writeToVCO(spiBuff, numBytesInReg);  // 04_00_00_02
      break;
    case MUX_READ:
      Serial.println("setting MUX to SPI read ...");
      spiBuff[3] = 0x00;
      spiBuff[2] = 0x02;
      spiBuff[1] = 0x00;
      spiBuff[0] = 0x05;    // reg addr 5
      writeToVCO(spiBuff, numBytesInReg);  // 00_02_00_05
      delay(20);
      spiBuff[3] = 0x08;
      spiBuff[2] = 0x00;
      spiBuff[1] = 0x00;
      spiBuff[0] = 0x02;    // reg addr 2
      writeToVCO( spiBuff, numBytesInReg );  // 08_00_00_02
      break;
    default:
      break;
  }
}


/* Time to program the MAX2871 chip to make it do what you want.
 *  This is basically a software SPI to the max chip.
*/
void writeToVCO(byte *selectedRegister, unsigned int numBytesToWrite) {
  digitalWrite(latchPin, LOW);

  for (int j=0; j<numBytesToWrite; j++) {
    shiftOut(dataPin, clockPin, MSBFIRST, selectedRegister[j]);
  }
  digitalWrite(latchPin, HIGH);
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
