# -*- coding: utf-8 -*-

import sys
from numba import njit
from dataclasses import dataclass


# Utilities provided for print debugging.
line = lambda: f'line {str(sys._getframe(1).f_lineno)},'
name = f'File \"{__name__}.py\",'


@njit(nogil=True)
def round9(freq):
    return round(freq, 9)


@dataclass
class cfg():
    ref_clock_1 = 66.000
    ref_clock_2 = 66.666
    ref_divider: int = 1                        # R from the MAX2871 spec sheet

    Fpfd1 = ref_clock_1 / ref_divider    # LO1 step size when using ref_clock 1
    Fpfd2 = ref_clock_2 / ref_divider    # LO1 step size when using ref_clock 2

    IF1: float = 3600.0                         # First intermediate frequency in MHz
    IF2: float = 315.0                          # Second intermediate frequency in MHz

    vco_fundamental_freq = 3000                 # MAX2871 VCO Fundamental

    _RFin_start: float = 0.0                    #
    _RFin_stop:  float = 3000.001               # Maximum hardware bandwidth 
    _RFin_step:  float = 0.001                  #
    
    # RFin_array contains every frequency from 0 to 3000.0 MHz in 1 kHz steps
    RFin_array = list()
    with open('RFin_steps.csv', 'r') as f:
        for freq in f:
            RFin = float(freq)
            RFin_array.append(RFin)


    @njit(nogil=True)
    def MHz_to_fmn(LO2_target_freq_MHz, ref_clock) -> int:
        """ Form a 32 bit word containing F, M and N for the MAX2871.

            Frac F is the fractional division value (0 to MOD-1)
            Mod M is the modulus value
            Int N is the 16-bit N counter value (In Frac-N mode min 19 to 4091)
        """
        R = 1
        max_error = 2**32
        for div_range in range(8):
            div = 2**div_range
            Fvco = div * LO2_target_freq_MHz
            if Fvco >= 3000:                    # vco fundamental freq = 3000 MHz (numba requires a constant?)
                break
        Fpfd = ref_clock / R
        N = int(Fvco / Fpfd)
        Fract = Fvco / Fpfd - N
        for M in range(2, 4096):
            F = round(Fract * M)
            Err1 = abs(Fvco - (Fpfd * (N + F/M)))
            if Err1 < max_error:
                max_error = Err1
                best_F = F
                best_M = M
        return best_F<<20 | best_M<<8 | N






