'MAX2871_Command_7.bas for Spectrum Analyzer Freq Synthesis.

Declare sub Math
Declare sub Transmit
Declare sub TransmitF

Declare Function Sweep (Fstart as single, Fstop as single, Freqs as integer) as integer
Declare Function newFreq (freq as string) as integer


dim shared as double Fvco, N, FracT
dim shared as ulong NI, registerNum, Reg(6,401), OldReg(6) ' Reg(6, 401) is Reg(registerNum, nSteps). 6 registers;401 max frequency steps
dim shared as string Swept, freq, ComStr, portNum, portSpeed, delaystr, FracOpt, LockDetect
dim shared as single Fpfd, Fref, RFOut, FvcoEst, FracErr, Frfv(401), Initial
dim shared as integer Range, delay, nSteps, Verbose, oldVerbose
dim shared as integer MOD1, Fracc, NewMOD1, NewFracc, Freqs, Div
dim shared as single Fstart,Fstop
dim shared as integer dispWidth, dispHeight



const as integer initialized = 1    ' MAX2871 state of initialization
dim shared as integer MAX2871

MAX2871 = not initialized

' Added for readability - Mark
dim shared as integer serPort = 1


' Add the ability to run automated testing by compiling without the user interface.
' Uses command line variables to replace the user input.
' The PRODUCTION value will need to be 0 for running the program in test-mode without user interaction.
const as integer PRODUCTION = 0
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
  
  ' Opening the serial port...
  portSpeed = "115200"

  input " Enter delay < 2 millseconds >"; delaystr
  if delaystr = "" then delaystr = "2"
  delay = val(delaystr)
  
  print
  input " Enter Fref in MHz (just press Enter for 60MHz) "; Fref ' Reference clock frequency 60 or 100 MHz for sa
  print
  input " <n> disables Lock Detect on Mux Line, <y> is default "; LockDetect
  print
  input " Enable Experimental Fraction Optimization <f> or Default <Enter> "; FracOpt
  print
  input " Enter <1> for Verbose Mode "; Verbose
  print
  input " Swept <s> or Default Fixed Frequency Mode<Enter>? "; Swept
  print

  if Swept="s" then 
    input " Enter Start Frequency [MHz] "; Fstart
    input " Enter Stop Frequency [MHz] "; Fstop
    input " Enter Number of Frequencies <2-401> "; Freqs
  else
    input " Enter Frequency [MHz] or <q> to quit"; freq
  endif

#elseif (TESTING)
  freq = *__FB_ARGV__[1]
  portSpeed = *__FB_ARGV__[2]
  portNum = *__FB_ARGV__[3]

  Verbose = 1
  Fref = 60
  LockDetect = "n"
  Swept = ""
#endif

  ' Open the serial port
  ComStr = "/dev/ttyACM" + portNum + ":" + portSpeed + ",N,8,1"      ' NOT a colon separated command
  open com ComStr as #serPort
  
  if Fref = 0 then Fref = 60
  RefDiv = 4                    ' Reference clock divider
  Fpfd = (Fref*1e6) / RefDiv		' Fpfd = 15MHz default

  if LockDetect="" then LockDetect = "y"
  
#if (PRODUCTION)
  if Swept="s" then
    Sweep(Fstart, Fstop, Freqs)
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
  Math 'Do The Math first so FracT is available to the Transmit/F functions.
  if MAX2871 = initialized then TransmitF else Transmit
  return 0
End Function


Function Sweep (Fstart as single, Fstop as single, Freqs as integer) as integer
  for nSteps = 0 to (Freqs-1)
    Frfv(nSteps) = Fstart + nSteps * (Fstop - Fstart)/(Freqs - 1)
    RFOut = Frfv(nSteps)
    Math 'Do The Math first: nSteps, Frfv(nSteps) >> Reg(registerNum, nSteps)
  next
  print " Math done! Press and hold <q> to quit sweeping"
  while inkey$ <> "q"
    for nSteps = 0 to (Freqs - 1)
      if MAX2871 = initialized then TransmitF else Transmit
    next
  wend
  return 0
End Function  ' Sweep

'''''''''''''''''''''''''''''''''''''''

Datarow1: 'For MAX2871 Initialization
  data  13093080,541097977,1476465218,4160782339,1674572284,2151677957 '374.596154 MHz with Lock Detect
Datarow2: 'For MAX2871 Initialization, no LockDetect on Mux Line
  data  13093080,541097977,1073812034,4160782339,1674572284,2151677957 '374.596154 MHz without Lock Detect


' This routine initializes MAX2871 with nSteps=0
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
        print " Transmit: Reg("; registerNum; ",0) = ";hex(Reg(registerNum,0));" NI=";NI;" Fracc=";Fracc;" MOD1=";MOD1
      endif
#endif
      sleep 100
      OldReg(registerNum) = Reg(registerNum, 0)
    next y
    Verbose = 0           ' Display registers only once
  next z
  Verbose = oldVerbose    ' Restore original verbosity state
  MAX2871 = initialized
end sub



' For changes in Frequency sweep or Power levels.
' Enter with Ref(registerNum, nSteps)
sub TransmitF
  for y = 0 to 5
    registerNum = (5 - y)
    if (Reg(registerNum, nSteps) = OldReg(registerNum)) then goto SkipOver
      write #serPort, Reg(registerNum, nSteps)
      sleep(delay)
      OldReg(registerNum) = Reg(registerNum, nSteps)
      if Verbose = 1 then 
        print " TransmitF: Reg("; registerNum; ",0) = "; hex(Reg(registerNum,0)); " NI="; NI; " Fracc="; Fracc; " MOD1="; MOD1
      endif
SkipOver:
  next
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
sub math   'Enter with Fpfd, RFOut, registerNum >> Leave with Reg(registerNum, nSteps)
  for registerNum = 0 to 6  'Determine divider range
    Div=(2^registerNum)
    if (RFOut * Div) >= 3000 then goto Main
  next
Main:  'Divider range now known
  Range = registerNum
  Fvco = Div * RFOut
  'Print "  Fvco= ";Fvco;" [MHz] Divider Ratio=";Div;" RFOut ="; RFOut;" [MHz]  Range= ";Range
  N = 1e6 * (Fvco/(Fpfd))
  NI = int(N)
  FracT = N - NI
  if FracOpt = "f" then Fraction_Opt : goto JumpMod
    MOD1 = 4095
    Fracc = int(FracT * MOD1)
JumpMod:
  FvcoEst = Fpfd * (1e-6) * (NI + (Fracc/MOD1))
  FrfEst = FvcoEst/(Div)
  'print "N = "; N; " NI = "; NI; " Fracc = "; Fracc; " MOD1 = "; MOD1; " Fpfd = "; Fpfd
  'print "FcvoEst = "; FvcoEst; "[MHz]    FrfEst = "; FrfEst; "[MHz]   FerrEst = "; int((1e6)*(FrfEst-RFOut)); "[Hz]"
 
  'restore Datarow1 'Restore Data Pointer 1 unless...
  if LockDetect = "y" then restore Datarow1 else restore Datarow2

  for registerNum = 0 to 5 : read Reg(registerNum, nSteps) : next 'Initialize Reg(registerNum, nSteps) default decimal Values

  ' These DON'T use registerNum but are hard coded as register number N for a damn reason!
  Reg(0,nSteps) = (NI * (2^15)) + (Fracc * (2^3))
  Reg(1,nSteps) = (2^29) + (2^15) + (MOD1*(2^3)) + 1
  Reg(4,nSteps) = 1670377980 + ((2^20) * Range)

end sub














