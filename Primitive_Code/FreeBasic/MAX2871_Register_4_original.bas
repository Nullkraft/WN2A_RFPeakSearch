'MAX2871_Register_4.bas for calculating optimal register values
' for random frequencies 3000-6000 MHz 
dim shared as integer F,M,R,N,BestM,BestF,x,BadF,BadM,BadN,Tests,points
dim shared as double Fvco,Fref,Fpfd,Fract,minErr,maxErr,Err1,BadVco,Fcent,BW,Fmin,Fmax,Tstart,TotalTime,StepSize
dim shared as double maxErrHz,minErrHz

dim as string filename = "fb_200MHz_100k-steps.csv"


Start:
'screen 19 :cls
print "MAX2871_Register_4.bas for calculating optimal register values"
print "For Random Frequencies 3000-6000 MHz. Ref Freq=60MHz; R=2 "
input "Enter Minimum Frequency [MHz] ";Fmin 
input "Enter Maximum Frequency [MHz] ";Fmax
if (Fmin<3000) or (Fmax>6000) then goto Start
input "Enter Step Size [MHz] ";StepSize :if StepSize=0 then goto Start

BW=Fmax-Fmin 
points=(BW / StepSize)

maxErr=0
Tstart=timer
for x=0 to points

  Fvco=Fmin+(x*StepSize)
   Fref=60 :R=2
  'print "Fvco [MHz]= ";Fvco;

  Fpfd=Fref/R
  N=INT ((Fvco)/Fpfd)
  Fract=(Fvco/Fpfd)-N
  ' Loops to determine best F and M with least error
  minErr=2^24

  open filename for Output as #7

  for M=4095 to 2 step -1
  F=cint(Fract*M) 
  Err1 = abs(Fvco - (Fpfd * (N + F / M)))
  if Err1<minErr then
    minErr=Err1
    minErrHz=(1e6)*minErr
    BestM=M
    BestF=F
  endif
  next M
  if BestF = BestM then 
    F = 0
    BestM = 4095
    N = N + 1
  endif
     
  'print "Iteration= ";x;
  'print "  Fpfd= ";Fpfd;"  N=  ";N;"  Fract= ";Fract
  'print "BestF= ";BestF;"   BestM= ";BestM ; 
  'print "  Error [Hz]= ";minErrHz
  if minErrHz > maxErrHz then
    maxErrHz = minErrHz
    BadF = BestF
    BadM = BestM
    BadN = N
    BadVco = Fvco
  endif

  print #7, Fvco, (Fpfd * (N + BestF / BestM)), N

next x

TotalTime=timer-Tstart
print
print TotalTime; " sec  :  "; points; " steps"
print
print " Fmin = "; Fmin; " MHz  :  Fmax = "; Fmax; " MHz  :  StepSize = "; StepSize; " MHz"
print
print "       Bad Fvco  = "; BadVco; " MHz"
print "       Max Error = "; maxErrHz; " Hz"
print
print "Bad_F = "; BadF; "   Bad_M = "; BadM; "  Bad_N = "; BadN
print


Report:


'''''''sleep 
