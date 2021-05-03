'ADF4356_2.bas for Spectrum Analyzer Freq synthesis. Uses Euclid
dim shared as ulong NI,x,y,z,r,Fract1,Fract2,MOD2,Reg(14),Fract2A,MOD2A
dim shared as double Fvco,Fpfd,N,FracT,Num,FpfdH,Fchsp,Re,Fout
dim shared as string Regstr,Ans,delay,Tx(14),T6(14)
dim shared as integer Div
screen 17 :cls
print "ADF4356_2.bas for Spectrum Analyzer Freq Synthesizer LO#1 3499-6500 MHz"
print "This program is used with Arduino programmed with ShiftOut_Word_7.ino"
sub Euclid  'Euclids Algorithm  Enter x<y, exit with GCD=z
do
r=x-y*(INT (x/y)) 'Calc Remainder
if r=0 then goto Exit1
x=y :z=r: y=r 'z will be GCD at Exit1
loop
Exit1:
end sub

input  "Enter ttyACM Port 0,1 or 3 or Q/q to Quit or Enter for 0";Ans :if Ans="" then Ans="0" 
if Ans="0" then open com "/dev/ttyACM0:9600,N,8,1" as #1
if Ans="1" then open com "/dev/ttyACM1:9600,N,8,1" as #1
if Ans="2" then open com "/dev/ttyACM2:9600,N,8,1" as #1
if Ans="Q" or Ans="q" then goto Sleepy
input "Enter millisec delay between words <100>";delay :if delay="" then delay="100"
Start:
for x=0 to 13 'Preload
read Tx(x) : 'Read in Hex Strings (default Values)
next
for x=0 to 6 : read T6(x) : next
print "Enter Fout in [MHz] or"
Input "Enter <0> to Program 4000MHz=LO,250MHz=RF (46.5MHz/2)=23.25MHz Fpfd";Fout :if Fout=0 then goto Transmit
for x=0 to 5
Div=(2^x)
if (Fout*Div)>=3400 then goto Exit2
next
Exit2:
Fvco=Div*Fout : Print "  Fvco= ";Fvco;"  [MHz]  Divider Ratio= ";Div
Tx(6)=T6(x)
input "Enter Fpfd (not Fref) in MHz  <61.44> ";Fpfd : N=Fvco/Fpfd 
input "Enter Fchsp Channel spacing in [kHz] <200> ";Fchsp 
 Fpfd=int (1e6)*Fpfd ' Convert to Hz
 Fchsp=int (1000*Fchsp) ' Convert to Hz
NI=int(N) : FracT=N-NI : Num=FracT*(2^24) :Fract1=int ((2^24)*FracT)
Re=((2^24)*(FracT))-Fract1 :x=Fpfd:y=Fchsp
print "Calling Euclid #1 to determine GCD" ;
Euclid ' Calls the Euclid subroutine above

print "   Fpfd=";Fpfd,"z= ";z 
MOD2=Fpfd/z : Fract2=Re*MOD2
print "  N value= ";N;"  INT= ";NI: print "  FracT=";FracT;"   Num= ";Num;" Fract1=";Fract1
print "  Remainder= ";Re;"  Fract2= ";Fract2;"    MOD2= ";MOD2 
'Reg 0:  0+ (NI*16)+2097152 (VCO Autocal)
print "Reg(0)=";(NI*16)+2097152 ': Regstr="0x"+Hex$(Reg(0),8)
Tx(0)=str(hex((NI*16)+2097152)) ': Regstr="0x"+Hex$(Reg(0),8)
print "Reg(1)=";1+(Fract1)*16
Tx(1)=str(hex((1+(Fract1)*16)))
x=Fract2 :y=MOD2 :print "  Fract2= ";Fract2;"  MOD2= ";MOD2
print "Calling Euclid #2 to reduce (Fract2/MOD2)";
Euclid
Fract2A=Fract2/z : MOD2A=MOD2/z : print "  Fract2A= ";Fract2A,"MOD2A= ";MOD2A
print "Reg(2)=";(2+((MOD2A)*(2^4))+Fract2A*(2^18))
Tx(2)=str(hex((2+((MOD2A)*(2^4))+Fract2A*(2^18))))
Tx(3)=str(hex((3)))

print: print"Now for 0 to 4": Input ans
for x=0 to 4 :print x;"  0x";Tx(x) :next
Transmit: 'In reverse order R13>>R0
for y=0 to 13 : x=13-y
Reg(x)=Val("&H"+Tx(x))
Regstr="0x"+Hex$(Reg(x),8)
print "Register ";x,Reg(x),"  0x";Tx(x)
  write #1,Reg(x)
  sleep val$(delay)
next

'Input "Enter <enter> to repeat or Q/q to Quit";Ans
'if Ans=""  then goto Start
Sleepy:
sleep 
data  "00200AC0","00B02C01","010005D2","00000003","32008984","00800025","358120F6" 'R0>>R6
data  "060000E7","15596568","0F09FCC9","00C00EBA","0061200B","000015FC","0000000D" 'R7>>R13
data "350120F6" ,"351120F6" ,"352120F6" ,"354120F6" ,"358120F6" ,"35A120F6" ,"35C120F6" 'R6

'data  "0000000D","000015FC","0061200B","00C00EBA","0F09FCC9","15596568","060000E7"
'data  "358120F6","00800025","32008984","00000003","010005D2","00B02C01","00200AC0"
