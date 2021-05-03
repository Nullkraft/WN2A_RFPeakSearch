'MAX2871_Command_6.bas for Spectrum Analyzer Freq Synthesis.

Declare sub Math
Declare sub Transmit
Declare sub TransmitF



dim shared as ulong NI, registerNum, Reg(6,401), OldReg(6) ' Reg(6, 401) is Reg(registerNum, nSteps). 6 registers;401 max frequency steps
dim shared as double Fvco, N, FracT
dim shared as string FracOpt, ComStr, delayStr
dim shared as single Fpfd, Fref, RFOut, FrfEst, FvcoEst, FracErr, Finc, Frfv(401)
dim shared as integer Range, OldRange, delay, RefDiv, nSteps, Verbose '
dim shared as integer MOD1, Fracc, NewMOD1, NewFracc, Mode

const as integer initialized = 1
dim shared as integer MAX2871 = not initialized

MAX2871 = not initialized

' Added for readability - Mark
dim shared as integer serPort = 1



' Begin execution of our program
Program_Start:
  dim as string freq = *__FB_ARGV__[1]
  dim as string portSpeed = *__FB_ARGV__[2]
  dim as string portNum = *__FB_ARGV__[3]
  
  ' Opening the serial port...
  ComStr = "/dev/ttyACM" + portNum + ":" + portSpeed + ",N,8,1"      ' NOT a colon separated command
  open com ComStr as #serPort
  delaystr="2"
  delay = val(delaystr)
                                ' input " Enter Fref in MHz (just press Enter for 60MHz) ";Fref		' Reference clock frequency 60 or 100 MHz for sa
  Fref = 60
  RefDiv=4                      ' Reference clock divider
  Fpfd = (Fref * 1e6) / RefDiv	' Fpfd = 15MHz default
  FracOpt = ""                  ' input " Enable Experimental Fraction Optimization <f> or Default <Enter> "; FracOpt
                                ' input " Swept <s> or Default Fixed Frequency Mode<Enter>? "; Sweep
                                ' if Sweep="s" then goto Swept
  Verbose = 1                   ' input " Enter <1> for Verbose Mode "; Verbose

  RFOut = val(freq)	 ' String to float
  if (RFOut < 23.5) then RFOut = 23.5
  if (RFOut > 6000) then RFOut = 6000
  Math   ' Sets FracT for Transmit/F functions.
  if MAX2871 = initialized then TransmitF else Transmit

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
  data  13093080,541097977,1476465218,4160782339,1674572284,2151677957 '374.596154 MHz


exitProg:
  close #serPort
  sleep


sub Transmit 'This routine initializes MAX2871 with nSteps=0
  oldVerbose = Verbose
  open "newRegisters.txt" for output as #42
  print " First we initialize the MAX2871 (twice)"
  for z=0 to 1 'do the Reg 5-4-3-2-1-0 cycle twice
    for y = 0 to 5 : registerNum = (5 - y)
      write #serPort, Reg(registerNum, 0)
      if Verbose then print #42, hex(Reg(registerNum,0))
      if Verbose then print "sub Transmit regN= ";regN;" Reg(regN,0)= ";hex(Reg(regN,0));" NI=";NI;" Fracc=";Fracc;" MOD1=";MOD1
      sleep 100
      OldReg(registerNum) = Reg(registerNum, 0)
    next y
    Verbose = 0
  next z
  Verbose = oldVerbose
  MAX2871 = initialized
  close #42
  End
end sub




sub TransmitF 'For changes in Frequency sweep or Power levels. Enter with Ref(registerNum,nSteps), nSteps
  for y = 0 to 5
    registerNum = (5 - y)
    if (Reg(registerNum, nSteps) = OldReg(registerNum)) then goto SkipOver
      write #serPort, Reg(registerNum, nSteps)
      sleep(delay)
      OldReg(registerNum) = Reg(registerNum, nSteps)
      if Verbose then print " TransmitF: Reg("; registerNum; ",0) = "; hex(Reg(registerNum,0)); " NI="; NI; " Fracc="; Fracc; " MOD1="; MOD1
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



' Math is called once for each frequency step in the sweep function
sub math   'Enter with Fpfd, RFOut, registerNum >> Leave with Reg(registerNum, nSteps)


' I'm off by registerNum+1 using this method
  registerNum = 0
  while (RFOut * Div) < 3000
    Div = 2^registerNum
    registerNum = registerNum + 1
    print registerNum
  wend
  registerNum = registerNum - 1
'  for registerNum = 0 to 6  'Determine divider range
'    Div = 2^registerNum
'    print registerNum
'    if (RFOut * Div) >= 3000 then goto Main
'  next

Main:  'Divider range now known
  Range = registerNum
  Fvco = Div * RFOut
  N = 1e6 * (Fvco/(Fpfd))
  NI = int(N)
  FracT = N - NI
  print Range, Fvco, N, NI, FracT
  if FracOpt="f" then Fraction_Opt : goto JumpMod
    MOD1 = 4095
    Fracc = int(FracT * MOD1)
JumpMod:
  FvcoEst = Fpfd * (1e-6) * (NI + (Fracc/MOD1))
  FrfEst = FvcoEst/(Div)
  restore Datarow1 'Restore Data Pointer 1

  for registerNum = 0 to 5 : read Reg(registerNum, nSteps) : next 'Initialize Reg(registerNum, nSteps) default decimal Values

  ' These DON'T use registerNum but are hard coded as register number N for a damn reason!
  Reg(0,nSteps) = (NI * (2^15)) + (Fracc * (2^3))
  Reg(1,nSteps) = (2^29) + (2^15) + (MOD1 * (2^3)) + 1
  Reg(4,nSteps) = 1670377980 + ((2^20) * Range)

end sub














