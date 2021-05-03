'ADF4356_2.bas for Spectrum Analyzer Freq Synthesis. Uses Euclid
dim shared as ulong NI,x,y,z,r,Fract1,Fract2,MOD2,Reg(14),Fract2A,MOD2A,FpfdH,FchspH
dim shared as double Fvco,Fpfd,N,FracT,Num,Fchsp,Re,Fout
dim shared as string Regstr,Ans,delay,Tx(14),T6(14),ComStr,Ans1,Ans2,FchspStr
dim shared as integer Div,Flag,Range,OldRange


sub Euclid  'Euclids Algorithm  Enter x<y, exit with GCD=z
do
r=x-y*(INT (x/y)) 'Calc Remainder
if r=0 then goto Exit1
x=y :z=r: y=r 'GCD=z at Exit1
loop
Exit1:
end sub
Setup:
screen 17 :cls
print "ADF4356_2.bas for Spectrum Analyzer Freq Synthesizer LO#1 3499-6500 MHz"
print "For ADF4356 Fout=53.125-6800 MHz with Arduino ShiftOut_Word_7.ino"
print "Refer to README_ADF4356_2.txt":print
input  "Enter ttyACM Port 0,1 or 2 ";Ans1 
input "Enter Baud Rate such as 9600 or 115200 <9600 default> ";Ans2
if Ans2="" then Ans2="9600"
ComStr="/dev/ttyACM"+Ans1+":"+Ans2+",N,8,1"
open com Comstr as #1


input "Enter millisec delay between words <50>";delay :if delay="" then delay="50"
input "Enter Fpfd (not Fref) in [MHz]";Fpfd 
input "Enter Fchsp Channel spacing in [kHz] <typ 200> ";FchspStr :if FchspStr ="" then FchspStr="200"
Fchsp=val(FchspStr)
Start:
cls
restore Sleepy 'Restore Data Pointer
for x=0 to 13 'Preload
read Tx(x) : 'Read in Hex Strings (default Values)
next
for x=0 to 6 : read T6(x) : next
Flag=0
LoopBack:
cls :OldRange=Range
print "ADF4356_2.bas for Spectrum Analyzer Freq Synthesizer LO#1 3499-6500 MHz"
print "For ADF4356 Fout=53.125-6800 MHz with Arduino ShiftOut_Word_7.ino" 
print "Refer to README_ADF4356_2.txt":print
Print "Current Fpfd= ";Fpfd;" [MHz]   Fchsp= ";Fchsp;" [kHz]"
if flag=0 then input "Enter Fout to Program [MHz]";Fout 
 for x=0 to 6  'Determine divider range
  Div=(2^x)
  if (Fout*Div)>=3400 then goto Main
 next
Main:  'Divider range now known
Range=x : if OldRange<>Range then Flag=0
Fvco=Div*Fout : Print "  Fvco= ";Fvco;" [MHz] Divider Ratio=";Div;" Fout= ";Fout;" [MHz]"
 Tx(6)=T6(x)  

 N=Fvco/Fpfd 
 FpfdH=int (1e6)*Fpfd ' Convert to Hz
 FchspH=int (1000*Fchsp) ' Convert to Hz
NI=int(N) : FracT=N-NI : Num=FracT*(2^24) :Fract1=int ((2^24)*FracT)
Re=((2^24)*(FracT))-Fract1 :x=FpfdH:y=FchspH
'print "NI= ";NI;" Fract1= ";Fract1;" Remainder= ";Re

Euclid ' Calls the Euclid subroutine above

MOD2=FpfdH/z : Fract2=Re*MOD2

Tx(0)=str(hex((NI*16)+2097152)) 

Tx(1)=str(hex((1+(Fract1)*16)))
x=Fract2 :y=MOD2 :'print "  Fract2= ";Fract2;"  MOD2= ";MOD2

Euclid ' Calls the Euclid subroutine above again
Fract2A=Fract2/z : MOD2A=MOD2/z 
Tx(2)=str(hex((2+((MOD2A)*(2^4))+Fract2A*(2^18))))
Tx(3)=str(hex((3)))

Transmit:
for y=Flag to 13 : x=13-y
Reg(x)=Val("&H"+Tx(x))
Regstr="0x"+Hex$(Reg(x),8)
print "Register ";x,Reg(x),"  0x";Tx(x)
  write #1,Reg(x)
  sleep val$(delay)
next
Flag=11
input "Enter Fout Frequency?? <S/s> to  Setup, <Q/q> to Quit";Ans 
if Ans="Q" or Ans="q" goto Sleepy
if Ans="S" or Ans="s" goto Setup
Fout=val(Ans) :goto LoopBack
Sleepy:
system
data  "00200AC0","00B02C01","010005D2","00000003","32008984","00800025","358120F6" 'R0>>R6
data  "060000E7","15596568","0F09FCC9","00C00EBA","0061200B","000015FC","0000000D" 'R7>>R13
data "350120F6","352120F6","354120F6","356120F6","358120F6","35A120F6","35C120F6" 'R6


