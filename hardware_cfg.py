# -*- coding: utf-8 -*-
#
# This file is part of WN2A_RFPeakSearch.
# 
# This file is part of the WN2A_RFPeakSearch distribution (https://github.com/Nullkraft/WN2A_RFPeakSearch).
# Copyright (c) 2021 Mark Stanley.
# 
# WN2A_RFPeakSearch is free software: you can redistribute it and/or modify  
# it under the terms of the GNU General Public License as published by  
# the Free Software Foundation, version 3.
#
# WN2A_RFPeakSearch is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU 
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License 
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

# Use these functions in all your print statements to display the filename 
# and the line number of the source file. Requires: import sys
name = lambda: f"File \'{__name__}.py\',"
line = lambda: f"line {str(sys._getframe(1).f_lineno)},"


import sys
from dataclasses import dataclass
from enum import Enum, auto
from functools import wraps
from numba import njit

class SPI_Device(Enum):
  """ Tracks which of the SPI capable chips is selected """
  ATTENUATOR = auto()
  LO1 = auto()
  LO2 = auto()
  LO3 = auto()


@dataclass
class Cfg():
  max_error = 2**32
  Vref = 2.595 #5.0           # Controller ADC reference voltage

  ref_clock_1 = 66.000
  ref_clock_2 = 66.666
  ref_divider: int = 1        # R from the MAX2871 spec sheet

  Fpfd1 = ref_clock_1 / ref_divider   # LO1 step size when using ref_clock 1
  Fpfd2 = ref_clock_2 / ref_divider   # LO1 step size when using ref_clock 2

  IF1: float = 3600.0         # First intermediate frequency in MHz
  IF2: float = 315.0          # Second intermediate frequency in MHz
  IF3: float = 45.0           # Third intermediate frequency in MHz

  RFin_max_freq = 3000        # No control codes available beyond this frequency



def memoize(func):
  cache = {}
  @wraps(func)
  def wrapper(*args, **kwargs):
    key = str(args) + str(kwargs)
    if key not in cache:
      cache[key] = func(*args, **kwargs)
    return cache[key]
  return wrapper


#@memoize
@njit(nogil=True)
def MHz_to_fmn(target_freq_MHz: float, ref_clock: float):
  """ Form a 32 bit word containing F, M and N for the MAX2871.
      Frac F is the fractional division value (0 to MOD-1)
      Mod M is the modulus value
      Int N is the 16-bit N counter value (In Frac-N mode min 19 to 4091)
  """
  R = 1
  max_error = 2**32
  Fvco = target_freq_MHz
  while Fvco < 3000:
    Fvco *= 2
    if Fvco >= 3000:
      break
  Fpfd = ref_clock/R
  NF = Fvco/Fpfd
  N = int(NF)     # Get the integer portion for N
  Fract = NF % 1  # Get the fraction portion for F
  for M in list(range(4095,1,-1)):
    F = round(Fract * M)
    Err1 = abs(Fvco - (Fpfd * (N + F/M)))
    if Err1 == 0:
      best_F = F
      best_M = M
      break
    if Err1 <= max_error:   # <= selects highest value of Best_M, more accurate target freq
      max_error = Err1
      best_F = F
      best_M = M
#  print(name(), line(), f'F = {best_F} : M = {best_M} : N = {N}')
  return best_F<<20 | best_M<<8 | N, Fvco 





