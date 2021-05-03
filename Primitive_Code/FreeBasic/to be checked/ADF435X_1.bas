'ADF435X_1.bas for Spectrum Analyzer Freq synthesis. Uses Euclid
dim shared as ulong NI,x,y,z,r,Fract1,Fract2,MOD2,Fract2A,MOD2A,Reg(14)
dim shared as double Fvco,Fpfd,N,FracT,Num,FpfdH,Fchsp,Re,Fout
dim shared as string Regstr
dim shared as integer Div
screen 17 :cls

sub Euclid  'Euclids Algorithm  Enter x<y, exit with GCD=z
do
r=x-y*(INT (x/y)) 'Calc Remainder
if r=0 then goto Report
x=y :z=r: y=r 'z will be GCD at Report
loop
Report:
end sub

Print "ADF4356_1.bas Does the Frequency Math for R0,R1,R2. "
Input "Enter Fout in [MHz] (the Divided Output)";Fout 
for x=0 to 5
Div=(2^x)
if (Fout*Div)>=3400 then goto JumpOut
next

JumpOut:
Fvco=Div*Fout : Print "  Fvco= ";Fvco;"  [MHz]  Divider Ratio= ";Div
input "Enter Fpfd in MHz  <61.44> ";Fpfd : N=Fvco/Fpfd 
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
Reg(0)=(NI*16)+2097152 ': Regstr="0x"+Hex$(Reg(0),8)
Reg(1)=1+(Fract1)*16
x=Fract2 :y=MOD2 :print "  Fract2= ";Fract2;"  MOD2= ";MOD2
print "Calling Euclid #2 to reduce (Fract2/MOD2)";
Euclid

Fract2A=Fract2/z : MOD2A=MOD2/z : print "  Fract2A= ";Fract2A,"MOD2A= ";MOD2A
Reg(2)=2+((MOD2A)*(2^4))+Fract2A*(2^18)
Reg(3)=3
Reg(4)=838896004

print
for x=0 to 4
Regstr="0x"+Hex$(Reg(x))
print "Register ";x,Reg(x),Regstr
next

sleep 
