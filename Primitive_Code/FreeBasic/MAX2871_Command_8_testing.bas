'MAX2871_Command_7.bas for Spectrum Analyzer Freq Synthesis.

Declare sub Transmit
Declare sub TransmitF

Declare Function Sweep (Fstart as single, Fstop as single, numFreqs as integer) as integer
Declare Function newFreq (freq as string) as integer
Declare Function Math (RFOut as single) as integer


dim shared as double Fvco, N, FracT
dim shared as ulong NI, registerNum, Reg(6,401), OldReg(6) ' Reg(6, 401) is Reg(registerNum, stepNumber). 6 registers;401 max frequency steps
dim shared as string Swept, freq, ComStr, portNum, portSpeed, delaystr, FracOpt, LockDetect
dim shared as single Fstart, Fstop
dim shared as single Fpfd, refClock, RFOut, FvcoEst, FracErr, Frfv(401), Initial
dim shared as integer transmissionDelay, stepNumber, Verbose, oldVerbose ', Range
dim shared as integer MOD1, Fracc, NewMOD1, NewFracc, numFreqs, Div, dispWidth, dispHeight



const as integer initialized = 1    ' MAX2871 state of initialization
dim shared as integer MAX2871

MAX2871 = not initialized

' Added for readability - Mark
dim shared as integer serPort = 1


' Add the ability to run automated testing by compiling without the user interface.
' Uses command line variables to replace the user input.
' The PRODUCTION value will need to be 0 for running the program in test-mode without user interaction.
const as integer PRODUCTION = 1
const as integer TESTING = not PRODUCTION

' Begin execution of our program
Program_Start:
#if (PRODUCTION)
  screeninfo dispWidth, dispHeight
  if dispHeight < 600 then screen 18 else screen 20 
  cls ' cls isn't really used at this point (that true!)
  color 11,0
  
  print
  print " MAX2871_Command_7.bas by WN2A/MS for PROJECT#3 Signal Generator"
  print " Use with Arduino MAX2871_Load_Word_115200_ 4.ino"
  print " Supports 23.5-6000MHz. REF freq=60MHz, Experimental version with Fraction_Opt"
  print " ******* This version is just Beta...Don't Have a Cow,Man !!  *********"
  print "  1) With above sketch loaded into Arduino, connect Arduino UNO,"
  print "      and start the Arduino IDE"
  print "  2) Check for Serial Port#, open Serial Monitor, set Baud=115200. Close IDE"
  print " Refer to README_MAX2871_Command.bas.txt !!"
  print
  input " Now enter ttyACM Port 0,1 or 2 < 0 default> "; portNum : if portNum="" then portNum="0"

  input " Enter transmission delay < 2 millseconds >"; delaystr      ' Delay between xmitting one register value and the next
  print
  input " Enter refClock in MHz (just press Enter for 60MHz) "; refClock                        ' <<<<<<<<<<<
  print
  input " <n> disables Lock Detect on Mux Line, <y> is default "; LockDetect                    ' <<<<<<<<<<<
  print
  input " Enable Experimental Fraction Optimization <f> or Default <Enter> "; FracOpt           ' <<<<<<<<<<<
  print
  input " Enter <1> for Verbose Mode "; Verbose
  print
  input " Swept <s> or Default Fixed Frequency Mode<Enter>? "; Swept                            ' <<<<<<<<<<<
  print

  if Swept="s" then 
    input " Enter Start Frequency [MHz] "; Fstart
    input " Enter Stop Frequency [MHz] "; Fstop
    input " Enter Number of Frequencies <2-401> "; numFreqs
  else
    input " Enter Frequency [MHz] or <q> to quit"; freq
  endif


#elseif (TESTING)
  freq = *__FB_ARGV__[1]
  portSpeed = *__FB_ARGV__[2]
  portNum = *__FB_ARGV__[3]

  Verbose = 1
  refClock = 60
  LockDetect = "y"
  Swept = ""
#endif
  
' Opening the serial port...
  portSpeed = "38400"
'  ComStr = "/dev/ttyUSB" + portNum + ":" + portSpeed + ",N,8,1"      ' NOT a colon separated command
  ComStr = "/dev/ttyACM" + portNum + ":" + portSpeed + ",N,8,1"      ' NOT a colon separated command
  open com ComStr as #serPort
  
  if LockDetect="" then LockDetect = "y"
  
#if (PRODUCTION)
  if Swept="s" then
    Sweep(Fstart, Fstop, numFreqs)
  else
    while freq <> "q"
      newFreq(freq)
      input " Enter Frequency [MHz] or <q> to quit"; freq
    wend
  endif
#elseif (TESTING)
  newFreq(freq)
#endif

exitProg:
  close #serPort
#if (TESTING)
  End
#endif
  sleep


Function newFreq (freq as string) as integer
  RFOut = val(freq)	 ' String to float
  if (RFOut < 23.5) then RFOut = 23.5
  if (RFOut > 6000) then RFOut = 6000
  Math(RFOut) 'Do The Math first so FracT is available to the Transmit/F functions.
  if MAX2871 = initialized then TransmitF else Transmit
  return 0
End Function


Function Sweep (Fstart as single, Fstop as single, numFreqs as integer) as integer
  for stepNumber = 0 to (numFreqs-1)
    Frfv(stepNumber) = Fstart + stepNumber * (Fstop-Fstart) / (numFreqs-1)
    RFOut = Frfv(stepNumber)
    Math(RFOut) 'Do The Math first: stepNumber, Frfv(stepNumber) >> Reg(registerNum, stepNumber)
  next
  print " Math done! Press and hold <q> to quit sweeping"
  while inkey$ <> "q"
    for stepNumber = 0 to (numFreqs-1)
      if MAX2871 = initialized then TransmitF else Transmit
      count = count + 1
    next
  wend
  return 0
End Function  ' Sweep

'''''''''''''''''''''''''''''''''''''''

Datarow1: 'For MAX2871 Initialization
  data  13093080,541097977,1476465218,4160782339,1674572284,2151677957 '374.596154 MHz with Lock Detect
Datarow2: 'For MAX2871 Initialization, no LockDetect on Mux Line
  data  13093080,541097977,1073812034,4160782339,1674572284,2151677957 '374.596154 MHz without Lock Detect


' For changes in Frequency sweep or Power levels. 
' Enter with Ref(registerNum,stepNumber), stepNumber
sub TransmitF
  if delaystr = "" then delaystr = "2"
  transmissionDelay = val(delaystr)
  
  for y = 0 to 5
    registerNum = (5 - y)
    if (Reg(registerNum, stepNumber) <> OldReg(registerNum)) then   ' If the register value has changed...
      write #serPort, Reg(registerNum, stepNumber)                  ' then transmit the new value.
      if Verbose = 1 then
        print  stepNumber; " XmitF: Reg("; registerNum; ","; stepNumber; ") = "; hex(Reg(registerNum,stepNumber)); " NI="; NI; " Fracc="; Fracc; " MOD1="; MOD1
      endif
'      sleep(transmissionDelay)
      OldReg(registerNum) = Reg(registerNum, stepNumber)
    endif
  next
end sub



' This routine initializes MAX2871 with stepNumber=0
sub Transmit
  oldVerbose = Verbose
#if (PRODUCTION)
  print " First we initialize the MAX2871"
#endif
  for z = 0 to 1 'do the Reg 5-4-3-2-1-0 cycle twice
    for y = 0 to 5 : registerNum = (5 - y)
      write #serPort, Reg(registerNum, 0)
#if (TESTING)
      if Verbose then
        open "testRegisters.txt" for append as #42
        print #42, hex(Reg(registerNum,0))
        close #42
      endif
#endif
#if (PRODUCTION)
      if Verbose then 
        print " Reg("; registerNum; ",0) = "; hex(Reg(registerNum,0)); " NI=";NI; " Fracc="; Fracc; " MOD1="; MOD1
      endif
#endif
'      sleep 100
      OldReg(registerNum) = Reg(registerNum, 0)
    next y
    Verbose = 0           ' Display registers only once
  next z
  Verbose = oldVerbose    ' Restore original verbosity state
  MAX2871 = initialized
end sub



sub Fraction_Opt 'Enter with FracT, leave with Fracc , MOD1
  Initial = 2
  'print "From Fraction_Opt Fract = ";Fract
  for MOD1 = 4095 to 2 step -1
    Fracc = int(FracT * MOD1)
    FracErr = abs(FracT - (Fracc/MOD1))
    if (FracErr > Initial) then goto Jumpover
      NewFracc = Fracc
      Initial = FracErr
      NewMOD1 = MOD1
    Jumpover:
	next
  MOD1 = NewMOD1
  Fracc = NewFracc
end sub



' Math is called once for each step in the frequency sweep function
' Enter with Fpfd >> Leave with Reg(registerNum, stepNumber)
Function Math (RFOut as single) as integer
  if refClock = 0 then refClock = 60
  RefDiv = 4                        ' Reference clock divider
  Fpfd = (refClock*1e6) / RefDiv		' Fpfd = 15MHz default

  regNum = 0
  do
    Div = 2^regNum

    ' Determine the Divider Range 
    if (RFOut*Div) >= 3000 then
      Range = regNum
      Fvco = RFOut * Div
      print : print "Fvco = "; Fvco : print
      N = 1e6 * (Fvco/(Fpfd))
      NI = int(N)
      FracT = N - NI

      if FracOpt <> "f" then      ' Only run these lines if the user selected Fractional Optimization
        MOD1 = 4095
        Fracc = int(FracT * MOD1)
      endif

      ' These 2 lines appear to be dead code. Maybe they are used for testing?
      'FvcoEst = Fpfd * (1e-6) * (NI + (Fracc/MOD1))
      'FrfEst = FvcoEst/(Div)

      'restore Datarow1 'Restore Data Pointer 1 unless...
      if LockDetect = "y" then restore Datarow1 else restore Datarow2
      for nReg = 0 to 5 : read Reg(nReg, stepNumber) : next 'Initialize Reg(regNum, stepNumber) default decimal Values

      ' These use hardcoded regNum's for a damn reason. Leave them the-fuck alone!
      Reg(0,stepNumber) = (NI * (2^15)) + (Fracc * (2^3))
      Reg(1,stepNumber) = (2^29) + (2^15) + (MOD1*(2^3)) + 1
      Reg(4,stepNumber) = 1670377980 + ((2^20) * Range)
'      for nReg = 0 to 5 : print Reg(nReg, stepNumber) : next
            
      exit do
      
    endif

    regNum += 1   ' Divider Range still not found.
  loop


  Return 0

End Function    ' Math














