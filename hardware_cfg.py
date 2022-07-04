
from dataclasses import dataclass

import spectrumAnalyzer as sa


RFin_list = list()         # List of every kHz step from 0 to 3,000,000 kHz


@dataclass
class cfg():
    ref_clock_tuple: float = 66.000, 66.666 # Ref_1, Ref_2
    ref_divider: int = 1                    # R from the MAX2871 spec sheet
    IF1: float = 3600.0                     # First intermediate frequency in MHz
    IF2: float = 315.0                      # Second intermediate frequency in MHz

    vco_fundamental_freq = 3000             # MAX2871 VCO Fundamental

    _RFin_start: float = 0.0                #
    _RFin_stop:  float = 3000.001           # Maximum hardware bandwidth 
    _RFin_step:  float = 0.001              #


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

#    def __init__(self):
#        super().__init__()

    def load_RFin_list(self, freq_file: str='RFin_1kHz_freq_steps.csv'):
        with open(freq_file) as record:
            RFin_list = [float(x) for x in record]     # For sweeping and plotting
        return RFin_list

    def load_LO1_freq_steps(self, n_file='LO1_ref1_N_steps.csv', freq_file='LO1_ref1_freq_steps.csv'):
        with open(n_file) as n:
            self.LO1_n_list = [int(x) for x in n]           # For sweeping
        with open(freq_file) as freq:
            self.LO1_freq_list = [float(x) for x in freq]   # For plotting
        self.LO1_30Fpfd_steps = dict(zip(RFin_list, self.LO1_n_list))

    def load_LO2_freq_steps(self, fmn_file='LO2_ref1_fmn_steps.csv', freq_file='LO2_ref1_freq_steps.csv'):
        with open(fmn_file) as fmn:
            self.LO2_fmn_list = [int(x) for x in fmn]       # For sweeping
        with open(freq_file) as freq:
            self.LO2_freq_list = [float(x) for x in freq]   # For plotting
        self.LO2_30Fpfd_steps = dict(zip(RFin_list, self.LO2_fmn_list))

    def MHz_to_LO1_freq(self, freq_in_MHz=0, Fpfd=30.0):
        LO1_N = sa.MHz_to_N(freq_in_MHz)
        LO1_freq = LO1_N * Fpfd
        return LO1_freq
