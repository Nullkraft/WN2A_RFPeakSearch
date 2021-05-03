README_ADF4356_2.txt  Controls ADF4356 LO#1
for 3499-6500 MHz. Supports Multi-band 53.125-6800 MHz

For use with ShiftOut_Word_7.ino <9600 baud>
or ShiftOut_Word_7=115K.ino  <115200 baud>

1) Compile and Load the Arduino Uno R3 first.
2) Confirm sucessful program operation , by checking serial monitor. Note baud rate.
3) Shut down all Arduino IDE programs
4) Start ADF4356_2 . Enter the port number 0,1,2,etc.
5) Enter baud rate. To use 9600, just press Enter.
6) Enter delay between words. 50 msec is default
7) Enter the Phase detector frequency=Fpfd   For ADF4356_2, the Fpfd=Fref/2 , ex: 48/2=24 MHz
8) Fchsp=200 [kHz] (default). Press Enter
9) You can now program the Output Freq (Fout) in MHz.
10) The registers being programmed are displayed in the required programming order.
11) At the bottom of the list you are prompted for information:
      To program another frequency, just enter the value
      To change setup items (anything other than Fout) <S/s>
      To Quit Program <Q/q>
 1 March2020 WN2A      
  
