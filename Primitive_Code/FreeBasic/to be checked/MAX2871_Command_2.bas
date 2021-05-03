'MAX2871_Command_2.bas for Spectrum Analyzer Freq Synthesis.
dim shared as ulong NI,x,y,z,r,Fract1,Fract2,MOD2,Reg(6),FpfdH,FchspH,OldReg(6)
dim shared as double Fvco,N,FracT,Num,Fchsp,Re,Fout
dim shared as string Regstr,Ans,Tx(6),ComStr,Ans1,Ans2,FchspStr,t
dim shared as string Frefstr,Quote,delaystr,AnsT,Message,Remark
dim shared as integer div,Flag,Range,OldRange,delay,RefDiv,f
dim shared as integer Swept,MOD1,Fracc,NewMOD1,NewFracc,Mode,Sweep
dim shared as single Fstart,Fstop,Freqs,Fpfd,Fref,Frf,FrfEst,FvcoEst,Initial,FracErr,Finc,Frfv(401)
Flag=0 : Remark=" Sorry Dave, I'm afraid can't do that "

sub Transmit 'This routine initializes MAX2871 
print "First we initialize the MAX2871 (twice)   "
for z=0 to 1 'do the Reg 5-4-3-2-1-0 cycle twice
for y=0 to 5 : x=(5-y) 
  write #1,Reg(x)
  sleep 100
  OldReg(x)=Reg(x)
next y
next z
Flag=1 
end sub

sub TransmitF 'For Frequency/Range or Power changes
 for x=0 to 5
 'print x;"  OldReg= ";OldReg(x);" Reg= ";Reg(x)
 if (Reg(x)<>OldReg(x)) then  write #1,Reg(x) 'Only write as required
  sleep delay
  OldReg(x)=Reg(x)
  next
end sub

sub Fraction_Opt 'Enter with FracT, leave with Fracc , MOD1
Initial=2 : print "From Fraction_Opt Fract= ";Fract
for MOD1=4095 to 2 step -1
Fracc=int(FracT*MOD1) : FracErr=abs(FracT-(Fracc/MOD1))
if (FracErr>Initial) then goto Jumpover
NewFracc=Fracc: Initial=FracErr : NewMOD1=MOD1
Jumpover:
next
MOD1=NewMOD1 :Fracc=NewFracc
print "From Fraction_Opt Fracc= ";Fracc;" MOD1= ";MOD1  
end sub

sub Euclid  'Euclids Algorithm  Enter x<y, exit with GCD=z
do
r=x-y*(INT (x/y)) 'Calc Remainder
if r=0 then goto Exit1
x=y :z=r: y=r 'GCD=z at Exit1
loop
Exit1:
end sub

sub math   'Enter with Fpdf,Frf. Leave with Tx(0),Tx(1) and Tx(4)
 for x=0 to 6  'Determine divider range
  Div=(2^x)
  if (Frf*Div)>=3000 then goto Main
 next
Main:  'Divider range now known
Range=x : Fvco=Div*Frf
'Print "  Fvco= ";Fvco;" [MHz] Divider Ratio=";Div;" Frf= ";Frf;" [MHz]  Range= ";Range
N=1e6*(Fvco/(Fpfd)) : NI=int(N) : FracT=N-NI : 
'if Mode=1 then Fraction_Opt
'if Mode=1 then goto JumpMod
MOD1=4095 : Fracc=int(FracT*MOD1)
'JumpMod: 
FvcoEst=Fpfd*(1e-6)*(NI+(Fracc/MOD1)) : FrfEst=FvcoEst/(Div) 
'print "N= ";N;" NI= ";NI;" Fracc= ";Fracc;" MOD1= ";MOD1;" Fpfd= ";Fpfd
'print "FcvoEst= ";FvcoEst;"[MHz]    FrfEst= ";FrfEst;"[MHz]   FerrEst= ";int((1e6)*(FrfEst-Frf));"[Hz]"

restore Datarow1 'Restore Data Pointer 1
for x=0 to 5 : read Reg(x) : next 'Read in Hex Strings (default Values)
Reg(0)=(NI*(2^15))+(Fracc*(2^3))
Reg(1)=(2^29)+(2^15)+(MOD1*(2^3))+1
Reg(4)=1670377980+((2^20)*Range)
'for x=0 to 5 : print Reg(x);tab(20);"0x";hex(Reg(x)) :next
end sub

Setup:
screen 18 :cls
print "MAX2871_Command_2.bas by WN2A for PROJECT#3 Signal Generator"
print "Use with Arduino MAX2871_Load_Word_115200_1.ino"
print "Allows user to enter a frequency 23.5-6000MHz. REF freq=60MHz"
print " 1) With above sketch loaded into Arduino, start the Arduino IDE"
print " 2) Check for Serial Port#, open Serial Monitor, and set Baud=115200. Close IDE" 
print "Refer to README_MAX2871_Command.bas.txt !!":print
input "Now enter ttyACM Port 0,1 or 2 < 0 default> ";Ans1 : if Ans1="" then Ans1="0"
Ans2="115200" : Fref=60e6 : RefDiv=4 : Fpfd=Fref/RefDiv
ComStr="/dev/ttyACM"+Ans1+":"+Ans2+",N,8,1"
open com Comstr as #1
 
input "Enter delay < 10 millseconds >";delaystr : if delaystr="" then delaystr="10"
input #1 ,Message : print Message  :print
delay=val(delaystr)
input "Manual <1> or Swept <2> Frequency Mode? ";Sweep :if Sweep=2 then goto Swept

Manual:
print
'input "Enter Mode <0> Fixed Modulus, <1> Optimum Modulus";Mode
input "Enter Frequency [MHz] <q> to quit";Ans : if Ans="q" then goto Sleepy
Frf=val(Ans) : if (23.5>Frf) or (Frf>6000) then print Remark 
Math
if Flag=0 then Transmit else TransmitF
goto Manual

Swept:
 input "Enter Start Frequency [MHz] ";Fstart
 input "Enter Stop Frequency [MHz] ";Fstop
 input "Enter Number of Frequencies <2-201> ";Freqs
WrapBack:
 for f=0 to (Freqs-1) :Frfv(f)=Fstart+f*(Fstop-Fstart)/(Freqs-1):Frf=Frfv(f)

 print "Press <q> (hold)to quit sweeping  " ;Frfv(f)

 Math
' print Frf
 if Flag=0 then Transmit else TransmitF
 next
 
 if inkey$<>"q" then goto Wrapback 
 
Sleepy:
close #1
sleep
'system

Datarow1: 'For MAX2871 Initialization
  data  13093080,541097977,1476465218,4160782339,1674572284,2151677957


