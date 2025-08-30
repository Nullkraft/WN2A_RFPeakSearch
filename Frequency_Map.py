import numpy as np
from time import perf_counter

Fref = 66.666
Fpfd = Fref / 2

print()

# Everything should be in MHz
def _LO1_frequency(RFin: float, Fref: float, R: int=1) -> float:
  Fpfd = Fref/R
  if RFin <= 2000:
    IF1 = 3800
  else:
    IF1 = 3700
#  print(f'{IF1 = }')
#  LO1 = Fpfd * round(int(RFin+Fpfd+IF1)/Fpfd, 0)
  LO1 = Fpfd * ((RFin+IF1)/Fpfd)  # This should be more accurate
#  print(f'{LO1 = }')
  LO1 = int(LO1*1000)/1000
#  print("int(LO1) =", LO1)
  IF1 = LO1 - RFin
#  print(f'{RFin=}, {LO1=}')
  return LO1, RFin, IF1

def _LO1a_frequency(RFin: float, Fref: float, R: int=1) -> float:
  Fpfd = Fref/R
  if RFin <= 2000:
    IF1 = 3800
  else:
    IF1 = 3700
  LO1 = Fpfd * int(RFin+Fpfd+IF1)/Fpfd
#  LO1 = Fpfd * round(int(RFin+IF1)/Fpfd, 0)  # This should be more accurate
  LO1 = int(LO1*1000)/1000
  IF1 = int((LO1 - RFin)*1000)/1000
#  print(f'{RFin=}, {LO1=}')
  return LO1, RFin, IF1

def _LO2_frequency(RFin: float, ref_clock: str, injection: str) -> float:
#  select_dict = {"ref1": LO1_ref1_freq_dict, "ref2": LO1_ref2_freq_dict}
#  LO1_freq = select_dict[ref_clock]
#  IF1_corrected = LO1_freq[RFin] - RFin     # Make correction to IF1
  if injection == "HI":
#    LO2_freq = IF1_corrected + hw.Cfg.IF2   # High-side injection
#  elif injection == "LO":
#    LO2_freq = IF1_corrected - hw.Cfg.IF2   # Low-side injection
#  return LO2_freq
    return 0


def _LO3_frequency(LO2_freq: float, ref_clock: str, injection: str) -> float:
  IF1 = 3600
  LO3_freq = (LO2_freq - IF1) - 45.000
  return LO3_freq

#
#
last_LO1 = 0
start = perf_counter()
congl = []
congla = []
print(f'{"":3}{"LO1":12}{"IF1":12}{"LO1a":12}{"IF1a":12}{"delta":12}RFin')
print('----------------------------------------------------------------------')
#for i, RFin in enumerate(np.arange(1899.943,1899.944,0.001)):
for i, RFin in enumerate(np.arange(0.0,3000.001,1.0)):
  LO1, RFin, IF1 = _LO1_frequency(RFin, Fpfd)
  LO1a, RFina, IF1a = _LO1a_frequency(RFin, Fpfd)
  IF1 = int(IF1*1000)/1000
  if not last_LO1 == LO1:
    RFin = int(RFin*1000)/1000
    delta = abs(round(LO1 - LO1a, 3))
    print(f'{LO1:<13}{IF1:<12}{LO1a:<13}{IF1a:<13}{delta:<12}{RFin}')
  #  print(LO1,'\t\t',IF1,'\t\t',LO1a,'\t\t',IF1a,'\t\t',delta,'\t\t',RFin)
  #  print(f'{LO1=:<8},\t\t{IF1=:<8},\t\t{LO1a=:<8},\t\t{IF1a=:<8},\t\t{delta=:<8},\t\t{RFin=:<8}')
    last_LO1 = LO1
#print(congl)
print(f'Elapsed time = {round(perf_counter()-start, 3)}')
