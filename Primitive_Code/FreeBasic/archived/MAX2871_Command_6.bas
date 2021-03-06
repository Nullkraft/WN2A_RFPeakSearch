'MAX2871_Command_6.bas for Spectrum Analyzer Freq Synthesis.

Declare sub Math
Declare sub Transmit
Declare sub TransmitF



dim shared as ulong NI, regN,x,y, z, r, Fract1, Fract2, MOD2, Reg(6,401), FpfdH, FchspH, OldReg(6), slow
 ' Reg(6,401) is Reg(regN,nSteps). 6 registers;401 max frequency steps
dim shared as double Fvco, N, FracT, Num, Fchsp, Re, Fout, TimeA, TimeB
dim shared as string freq, ComStr, portNum, portSpeed, delaystr, FracOpt
dim shared as string Message, Remark, Sweep
dim shared as integer div, Flag, Range, OldRange, delay, RefDiv, nSteps,Verbose
dim shared as integer MOD1, Fracc, NewMOD1, NewFracc, Mode
dim shared as single Fstart, Fstop, Freqs, Fpfd, Fref, Frf, FrfEst, FvcoEst, Initial, FracErr, Finc, Frfv(401)
Flag=0 : Remark=" Sorry Dave, I'm afraid I can't do that "    ' Remarking on what Flag=0 means?

dim shared as integer serPort = 1

dim as integer count = 0    ' debugging only



' Begin execution of our program
Program_Start:
screeninfo w,h :if h<600 then screen 18 else screen 20 
color 10,0 

print
print "MAX2871_Command_6.bas by WN2A/MS for PROJECT#3 Signal Generator"
print "Use with Arduino MAX2871_Load_Word_115200_3.ino or 4.ino"
print "Supports 23.5-6000MHz. REF freq=60MHz, Experimental version with Fraction_Opt"
print "********   This version is only Beta!  ********************"
print " 1) With above sketch loaded into Arduino, connect Arduino UNO,"
print "     and start the Arduino IDE"
print " 2) Check for Serial Port#, open Serial Monitor, set Baud=115200. Close IDE"
print "Refer to README_MAX2871_Command.bas.txt !!":print
input "Now enter ttyACM Port 0,1 or 2 < 0 default> "; portNum : if portNum="" then portNum="0"

' Opening the serial port...
portSpeed="9600"
ComStr="/dev/ttyUSB" + portNum + ":" + portSpeed + ",N,8,1"      ' NOT a colon separated command
open com ComStr as #serPort
input "Enter delay < 2 millseconds >"; delaystr : if delaystr="" then delaystr="2"
delay=val(delaystr)
input #serPort, Message : print Message  : 'print

  input "Enter Fref in MHz (just press Enter for 60MHz) ";Fref :if Fref=0 then Fref=60
  RefDiv=4            ' Reference clock divider
  Fpfd=(Fref*1e6)/RefDiv		' Fpfd = 15MHz default
  input "Enable Experimental Fraction Optimization <f> or Default <Enter> "; FracOpt
  print
  input "Enter <1> for Verbose Mode ";Verbose
  print
  input "Swept <s> or Default Fixed Frequency Mode<Enter>? "; Sweep : if Sweep="s" then goto Swept
 
Manual:
  print	' Prints an empty line
  input "Enter Frequency [MHz] or <q> to quit"; freq : if freq="q" then goto Sleepy
  Frf=val(freq) : if (23.5<=Frf) and (Frf<=6000) then goto OkayValue
  Print Remark : goto  Manual
OkayValue:  
  Math
  if Flag=0 then Transmit else TransmitF
  goto Manual

Swept:
  input "Enter Start Frequency [MHz] "; Fstart
  input "Enter Stop Frequency [MHz] "; Fstop
  input "Enter Number of Frequencies <2-401> "; Freqs
  for nSteps=0 to (Freqs-1) : Frfv(nSteps) = Fstart+nSteps*(Fstop-Fstart)/(Freqs-1) : Frf=Frfv(nSteps)
    Math 'Do The Math First: nSteps, Frfv(nSteps) >> Reg(regN,nSteps)
  next
  print "Math done! Press and hold <q> to quit sweeping"
WrapBack:
  for nSteps=0 to (Freqs-1)
    if Flag=0 then Transmit else TransmitF
  next
  if inkey$<>"q" then goto Wrapback
Sleepy:
  close #serPort
  sleep

Datarow1: 'For MAX2871 Initialization
  data  13093080,541097977,1476465218,4160782339,1674572284,2151677957 '374.596154 MHz



''''''''''''''''''''''''''''''''''''''''


sub Transmit 'This routine initializes MAX2871 with nSteps=0
  oldVerbose = Verbose
  open "registers.txt" for output as #42
  print "First we initialize the MAX2871 (twice)"
  for z = 0 to 1 'do the Reg 5-4-3-2-1-0 cycle twice
    for y = 0 to 5 : regN=(5 - y)
      write #serPort, Reg(regN, 0)
      if Verbose then print #42, hex(Reg(regN, 0))
      if Verbose then print "sub Transmit regN= ";regN;" Reg(regN,0)= ";hex(Reg(regN,0));" NI=";NI;" Fracc=";Fracc;" MOD1=";MOD1
      sleep 100
      OldReg(regN) = Reg(regN, 0)
    next y
    Verbose = 0
  next z
  Verbose = oldVerbose
  Flag = 1
  close #42
end sub



sub TransmitF 'For Frequency/Range or Power changes. Enter with Ref(regN,f), f
  for y=0 to 5 : regN=(5-y)
  if (Reg(regN,nSteps)=OldReg(regN)) then goto SkipOver
    write #serPort, Reg(regN,nSteps) : sleep(delay)
    OldReg(regN)=Reg(regN,nSteps)
    if Verbose then print "sub TransmitF regN= ";regN;" Reg(regN,0)= ";hex(Reg(regN,0));" NI=";NI;" Fracc=";Fracc;" MOD1=";MOD1
SkipOver:  
  next
end sub




sub Fraction_Opt 'Enter with FracT, leave with Fracc , MOD1
  Initial=2 ': print "From Fraction_Opt Fract= ";Fract
  for MOD1=4095 to 2 step -1
    Fracc=int(FracT*MOD1) : FracErr=abs(FracT-(Fracc/MOD1))
    if (FracErr>Initial) then goto Jumpover
      NewFracc=Fracc : Initial=FracErr : NewMOD1=MOD1
    Jumpover:
  next
  MOD1=NewMOD1 : Fracc=NewFracc
end sub



' Math is called once for each step in the frequency sweep function
sub math   'Enter with Fpfd, Frf, regN >> Leave with Reg(regN, nSteps)
  for regN = 0 to 6  'Determine divider range
    Div=(2^regN)
    if (Frf*Div) >= 3000 then goto Main
  next
Main:  'Divider range now known
  Range = regN : Fvco=Div*Frf
  'Print "  Fvco= ";Fvco;" [MHz] Divider Ratio=";Div;" Frf= ";Frf;" [MHz]  Range= ";Range
  N=1e6*(Fvco/(Fpfd)) : NI=int(N) : FracT=N-NI
  if FracOpt="f" then Fraction_Opt : goto JumpMod
    MOD1=4095 : Fracc=int(FracT*MOD1)
JumpMod:
  FvcoEst=Fpfd*(1e-6)*(NI+(Fracc/MOD1)) : FrfEst=FvcoEst/(Div)
  'print "N= ";N;" NI= ";NI;" Fracc= ";Fracc;" MOD1= ";MOD1;" Fpfd= ";Fpfd
  'print "FcvoEst= ";FvcoEst;"[MHz]    FrfEst= ";FrfEst;"[MHz]   FerrEst= ";int((1e6)*(FrfEst-Frf));"[Hz]"
  restore Datarow1 'Restore Data Pointer 1

  for regN = 0 to 5 : read Reg(regN, nSteps) : next 'Initialize Reg(regN, nSteps) default decimal Values

  Reg(0,nSteps) = (NI*(2^15))+(Fracc*(2^3))
  Reg(1,nSteps) = (2^29)+(2^15)+(MOD1*(2^3))+1
  Reg(4,nSteps) = 1670377980+((2^20)*Range)

end sub













