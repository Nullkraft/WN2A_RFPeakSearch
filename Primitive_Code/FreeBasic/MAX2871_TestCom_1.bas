'MAX2871_TestCom.bas for Spectrum Analyzer Freq Synthesis.
dim shared as ulong NI,x,y,z,r,Fract1,Fract2,MOD2,Reg(14),FpfdH,FchspH
dim shared as double Fvco,N,FracT,Num,Fchsp,Re,Fout
dim shared as string Regstr,Ans,Tx(6),ComStr,Ans1,Ans2,FchspStr
dim shared as string Frefstr,RefDivstr,Quote,delaystr,AnsT
dim shared as integer div,Flag,Range,OldRange,delay,RefDiv
dim shared as single Fstart,Fstop,Finc,Fpfd,Fref
Flag=0
sub Transmit
print
for z=0 to 1 'do the Reg 5-4-3-2-1-0 cycle twice
for y=0 to 5 : x=(5-y)
Reg(x)=Val("&H"+Tx(x))
Regstr="0x"+Hex$(Reg(x),8)
print "Register ";x,Reg(x),"  0x";Tx(x)
  write #1,Reg(x)
  sleep 100
next y
  sleep 100
next z
end sub

sub TransmitF 'For writing to Register 0 only for Frequency
x=0
Reg(x)=Val("&H"+Tx(x))
  write #1,Reg(x)
  sleep delay
 end sub


Setup:
screen 18 :cls
print "MAX2871_TestCom.bas by WN2A for Spectrum Analyzer Freq Synthesizer LO#2 AND #3"

print "Use with Arduino MAX2871_Load_Word_115200_1.ino"
print "This program initializes the 6 registers (5-4-3-2-1-0)twice"
print "Toggles 2 frequencies: 187.827839 [MHz] / 374.596154 [MHz]"
print "Refer to README_MAX2871_TestCom.bas.txt":print
input "Enter ttyACM Port 0,1 or 2 < 0 default> ";Ans1 : if Ans1="" then Ans1="0"
Ans2="115200"
ComStr="/dev/ttyACM"+Ans1+":"+Ans2+",N,8,1"
open com Comstr as #1
input "Enter delay < 3 millseconds >";delaystr : if delaystr="" then delaystr="3"
delay=val(delaystr)
input "Select Mode: Toggle Manually or Automatically <a> ";AnsT
print "T Quit, press <q> then Enter"

Start:
if inkey$="q" then goto Sleepy
restore Datarow1 'Restore Data Pointer 1
for x=0 to 5 'Preload
read Tx(x) : 'Read in Hex Strings (default Values)
next
if AnsT="a" then goto Jump1
input "Ready to Transmit 187.827839 MHz?"; Ans : if Ans="q" then goto Sleepy
Jump1:
if Flag=1 then TransmitF else Transmit
Flag=1
restore Datarow2 'Restore Data Pointer 2
for x=0 to 5 'Preload
read Tx(x) : 'Read in Hex Strings (default Values)
next
if AnsT="a" then goto Jump2
input "Ready to Transmit 374.596154 MHz?"; Ans : if Ans="q" then goto Sleepy
Jump2:
if Flag=1 then TransmitF else Transmit

goto Start
close #1
Sleepy:
sleep

system
Datarow1:
data  "00642CC0","20407FF9","58011242","F8008003","63CFF1FC","80400005" 'R0>>R5 187.827839
Datarow2:
data  "00C7C8D8","20407FF9","58011242","F8008003","63CFF1FC","80400005" 'R0>>R5 374.596154



