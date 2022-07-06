# -*- coding: utf-8 -*-

from numpy import arange
from dataclasses import dataclass


RFin_list = list()         # List of every kHz step from 0 to 3,000,000 kHz


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
    RFin_array = [round(RFin, 9) for RFin in arange(_RFin_start, _RFin_stop, _RFin_step)]








