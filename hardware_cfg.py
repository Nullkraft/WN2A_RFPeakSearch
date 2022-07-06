# -*- coding: utf-8 -*-

from numpy import arange
from dataclasses import dataclass

import spectrumAnalyzer as sa


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



class hardware():
    """ HARDWARE DEFINITIONS for the Spectrum Analyzer board. RFin_list contains 1kHz frequency
    steps from 0.0 to 3000MHz. It is only necessary to perform a slice in order to provide
    different sweep ranges and step sizes.  For example,

    # User requested sweep start, stop, and step frequencies in MHz
    sweep_step = .025
    sweep_start = 0.0
    sweep_stop = 3000.0

    # Convert user frequency sweep parameters to machine step parameters
    step_size = int(sweep_step * 1000)
    step_start = int(sweep_start * 1000)
    step_stop = int((sweep_stop + sweep_step) * 1000)

    #~~~  sweep_list contains the list of frequencies to be swept  ~~~~
    sweep_list = hw.RFin_list[step_start:step_stop:step_size]
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    """

    def load_LO2_freq_steps(self, fmn_file='LO2_ref1_fmn_steps.csv', freq_file='LO2_ref1_freq_steps.csv'):
        with open(fmn_file) as fmn:
            self.LO2_fmn_list = [int(x) for x in fmn]       # For sweeping
        with open(freq_file) as freq:
            self.LO2_freq_list = [float(x) for x in freq]   # For plotting
        self.LO2_30Fpfd_steps = dict(zip(RFin_list, self.LO2_fmn_list))








