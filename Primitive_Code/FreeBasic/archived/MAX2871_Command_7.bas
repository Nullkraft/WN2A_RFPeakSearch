'MAX2871_Command_7.bas for Spectrum Analyzer Freq Synthesis.

Declare sub Math
Declare sub Transmit
Declare sub TransmitF

dim shared as double Fvco, N, FracT
dim shared as ulong NI, registerNum, Reg(6,401), OldReg(6) ' Reg(6, 401) is Reg(registerNum, nSteps). 6 registers;401 max frequency steps
dim shared as string Sweep, freq, ComStr, portNum, portSpeed, delaystr, FracOpt, Message, LockDetect
dim shared as single Fpfd, Fref, RFOut, FrfEst, FvcoEst, FracErr, Finc, Frfv(401),Initial
dim shared as integer Range, OldRange, delay, RefDiv, nSteps, Verbose,oldVerbose '
dim shared as integer MOD1, Fracc, NewMOD1, NewFracc, Mode,Freqs,Div
dim shared as single Fstart,Fstop
dim shared as integer y,z,w,h


const as integer initialized = 1    ' MAX2871 state of initialization
dim shared as integer MAX2871

MAX2871 = not initialized

' Added for readability - Mark
dim shared as integer serPort = 1



' Begin execution of our program
Program_Start:
  screeninfo w,h :if h<600 then screen 18 else screen 20 
  cls ' cls isn't really used at this point(that true!)
  color 11,0

  print
  print " MAX2871_Command_7.bas by WN2A/MS for PROJECT#3 Signal Generator"
  print " Use with Arduino MAX2871_Load_Word_115200_ 4.ino"
  print " Supports 23.5-6000MHz. REF freq=60MHz, Experimental version with Fraction_Opt"
  print " ******* This version is just Beta...Don't Have a Cow,Man !!  *********"
  print "  1) With above sketch loaded into Arduino, connect Arduino UNO,"
  print "      and start the Arduino IDE"
  print "  2) Check for Serial Port#, open Serial Monitor, set Baud=115200. Close IDE"
  print " Refer to README_MAX2871_Command.bas.txt !!":print
  input " Now enter ttyACM Port 0,1 or 2 < 0 default> "; portNum : if portNum="" then portNum="0"

  ' Opening the serial port...
  portSpeed="115200"
  ComStr = "/dev/ttyACM" + portNum + ":" + portSpeed + ",N,8,1"      ' NOT a colon separated command
  open com ComStr as #serPort
  input " Enter delay < 2 millseconds >"; delaystr : if delaystr="" then delaystr="2"
  delay = val(delaystr)
  input #serPort, Message
  if Message="" then print " No Arduino Message" else print " Arduino Message: ";Message

  input " Enter Fref in MHz (just press Enter for 60MHz) ";Fref ' Reference clock frequency 60 or 100 MHz for sa
  if Fref=0 then Fref=60
  RefDiv=4            ' Reference clock divider
  Fpfd=(Fref*1e6)/RefDiv		' Fpfd = 15MHz default
  
  input " <n> disables Lock Detect on Mux Line, <y> is default ";LockDetect
  if LockDetect="" then LockDetect = "y"
  
  input " Enter <1> for Verbose Mode "; Verbose

  input " Enable Experimental Fraction Optimization <f> or Default <Enter> "; FracOpt
  input " Swept <s> or Default Fixed Frequency Mode<Enter>? "; Sweep
  if Sweep="s" then goto Swept

Manual:
  print	' Prints an empty line
  input " Enter Frequency [MHz] or <q> to quit"; freq
  if freq="q" then goto exitProg
  RFOut=val(freq)	 ' String to float
  if (23.5<=RFOut) and (RFOut<=6000) then goto OkayValue
  Print " Sorry Dave, I'm afraid I can't do that."	' Warn user: Requested frequency exceeds range of MAX2871
  goto Manual

OkayValue:
  Math 'Do The Math first so FracT is available to the Transmit/F functions.
  if MAX2871 = initialized then TransmitF else Transmit
  goto Manual

Swept:
  input " Enter Start Frequency [MHz] "; Fstart
  input " Enter Stop Frequency [MHz] "; Fstop
  input " Enter Number of Frequencies <2-401> "; Freqs
  for nSteps=0 to (Freqs-1)
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
  goto exitProg



''''''''''''''''''''''''''''''''''''''''

Datarow1: 'For MAX2871 Initialization
  data  13093080,541097977,1476465218,4160782339,1674572284,2151677957 '374.596154 MHz with Lock Detect
Datarow2: 'For MAX2871 Initialization, no LockDetect on Mux Line
  data  13093080,541097977,1073812034,4160782339,1674572284,2151677957 '374.596154 MHz without Lock Detect

exitProg:
  close #serPort
  sleep


sub Transmit 'This routine initializes MAX2871 with nSteps=0
  oldVerbose = Verbose
  open "registers.txt" for output as #42
  print " First we initialize the MAX2871 (twice)"
  for z=0 to 1 'do the Reg 5-4-3-2-1-0 cycle twice
    for y = 0 to 5 : registerNum = (5 - y)
      write #serPort, Reg(registerNum, 0)
      if Verbose then print #42, hex(Reg(registerNum,0))
      if Verbose then print"   Xmit: Reg("; registerNum; ",0) = ";hex(Reg(registerNum,0));" NI=";NI;" Fracc=";Fracc;" MOD1=";MOD1
      sleep 100
      OldReg(registerNum) = Reg(registerNum, 0)
    next y
    Verbose = 0 ' Ok, enough then, just display registers once
  next z
  Verbose = oldVerbose
  MAX2871 = initialized
  close #42
end sub




sub TransmitF 'For changes in Frequency sweep or Power levels. Enter with Ref(registerNum,nSteps), nSteps
  for y = 0 to 5
    registerNum = (5 - y)
    if (Reg(registerNum, nSteps) = OldReg(registerNum)) then goto SkipOver
'      print "Write serPort = Reg("; registerNum; ","; nSteps; ") = "; Reg(registerNum, nSteps)
      write #serPort, Reg(registerNum, nSteps)
      if Verbose = 1 then
        print  nSteps; " XmitF: Reg("; registerNum; ","; nSteps; ") = "; hex(Reg(registerNum,nSteps)); " NI="; NI; " Fracc="; Fracc; " MOD1="; MOD1
      endif
      sleep(delay)
      OldReg(registerNum) = Reg(registerNum, nSteps)
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
  if FracOpt="f" then Fraction_Opt : goto JumpMod
    MOD1 = 4095
    Fracc = int(FracT * MOD1)
JumpMod:
  FvcoEst = Fpfd * (1e-6) * (NI + (Fracc/MOD1))
  FrfEst = FvcoEst/(Div)
  'print "N = "; N; " NI = "; NI; " Fracc = "; Fracc; " MOD1 = "; MOD1; " Fpfd = "; Fpfd
  
  print "FcvoEst = "; FvcoEst; "[MHz]    FrfEst = "; FrfEst; "[MHz]   FerrEst = "; int((1e6)*(FrfEst-RFOut)); "[Hz]"
 
  'restore Datarow1 'Restore Data Pointer 1 unless...
  if LockDetect = "y" then restore Datarow1 else restore Datarow2

  for registerNum = 0 to 5 : read Reg(registerNum, nSteps) : next 'Initialize Reg(registerNum, nSteps) default decimal Values

  ' These DON'T use registerNum but are hard coded as register number N for a damn reason!
  Reg(0,nSteps) = (NI * (2^15)) + (Fracc * (2^3))
  Reg(1,nSteps) = (2^29) + (2^15) + (MOD1*(2^3)) + 1
  Reg(4,nSteps) = 1670377980 + ((2^20) * Range)

end sub














