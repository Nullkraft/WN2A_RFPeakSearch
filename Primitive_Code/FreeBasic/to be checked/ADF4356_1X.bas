'ADF4356_1X.bas for Spectrum Analyzer Freq Synthesis. Uses Euclid
dim shared as ulong NI,x,y,z,r,Fract1,Fract2,MOD2,Reg(14),Fract2A,MOD2A
dim shared as double Fvco,Fpfd,N,FracT,Num,FpfdH,Fchsp,Re,Fout
dim shared as string Regstr,Ans,delay,Tx(14),T6(14)
dim shared as integer Div
screen 17 :cls
print "ADF4356_1X.bas for Spectrum Analyzer Freq Synthesizer LO#1 3499-6500 MHz"
print "For ADF4356 Fout=53.125-6800 MHz with Arduino ShiftOut_Word_7.ino"

sub Euclid  'Euclids Algorithm  Enter x<y, exit with GCD=z
do
r=x-y*(INT (x/y)) 'Calc Remainder
if r=0 then goto Exit1
x=y :z=r: y=r 'GCD=z at Exit1
loop
Exit1:
end sub

'input  "Enter ttyACM Port 0,1 or 2 or Q/q to Quit or Enter for 0";Ans :if Ans="" then Ans="0" 
'if Ans="0" then open com "/dev/ttyACM0:9600,N,8,1" as #1
'if Ans="1" then open com "/dev/ttyACM1:9600,N,8,1" as #1
'if Ans="2" then open com "/dev/ttyACM2:9600,N,8,1" as #1
'if Ans="Q" or Ans="q" then goto Sleepy
'input "Enter millisec delay between words <50>";delay :if delay="" then delay="50"
Start:
sleep 1000 :cls
input "Enter Fpfd (not Fref) in [MHz]";Fpfd ' N=Fvco/Fpfd :
input "Enter Fchsp Channel spacing in [kHz] <typ 200> ";Fchsp 
restore Sleepy
for x=0 to 13 'Preload
read Tx(x) : 'Read in Hex Strings (default Values)
next
for x=0 to 6 : read T6(x) : next
'Input "Enter Fout to Program [MHz]";Fout 
LoopBack:

Input "Enter Fout to Program [MHz]";Fout 
 for x=0 to 6  'Determine divider range
  Div=(2^x)
  if (Fout*Div)>=3400 then goto Main
 next
Main:  'Divider range now known
Fvco=Div*Fout : Print "  Fvco= ";Fvco;"  [MHz]  Divider Ratio= ";Div
 Tx(6)=T6(x) 
'input "Enter Fpfd (not Fref) in [MHz]";Fpfd ' N=Fvco/Fpfd :
'input "Enter Fchsp Channel spacing in [kHz] <typ 200> ";Fchsp 
 N=Fvco/Fpfd : Fpfd=int (1e6)*Fpfd ' Convert to Hz
 Fchsp=int (1000*Fchsp) ' Convert to Hz
NI=int(N) : FracT=N-NI : Num=FracT*(2^24) :Fract1=int ((2^24)*FracT)
Re=((2^24)*(FracT))-Fract1 :x=Fpfd:y=Fchsp
print "NI= ";NI;" Fract1= ";Fract1;" Remainder= ";Re

Euclid ' Calls the Euclid subroutine above

MOD2=Fpfd/z : Fract2=Re*MOD2

Tx(0)=str(hex((NI*16)+2097152)) 

Tx(1)=str(hex((1+(Fract1)*16)))
x=Fract2 :y=MOD2 :print "  Fract2= ";Fract2;"  MOD2= ";MOD2

Euclid ' Calls the Euclid subroutine above again
Fract2A=Fract2/z : MOD2A=MOD2/z 
Tx(2)=str(hex((2+((MOD2A)*(2^4))+Fract2A*(2^18))))
Tx(3)=str(hex((3)))

Transmit: 'In reverse order R13>>R0
for y=0 to 13 : x=13-y
Reg(x)=Val("&H"+Tx(x))
Regstr="0x"+Hex$(Reg(x),8)
print "Register ";x,Reg(x),"  0x";Tx(x)
'  write #1,Reg(x)
'  sleep val$(delay)
next
input "Another Fout Frequency?? Press Enter or <Q/q> to Quit";Ans : if Ans="" goto Start

Sleepy:
system
data  "00200AC0","00B02C01","010005D2","00000003","32008984","00800025","358120F6" 'R0>>R6
data  "060000E7","15596568","0F09FCC9","00C00EBA","0061200B","000015FC","0000000D" 'R7>>R13
data "350120F6","352120F6","354120F6","356120F6","358120F6","35A120F6","35C120F6" 'R6


