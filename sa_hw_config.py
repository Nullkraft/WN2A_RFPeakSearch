# -*- coding: utf-8 -*-

# Utilities provided for print debugging.
line = lambda: f'line {str(sys._getframe(1).f_lineno)},'
name = f'File \"{__name__}.py\",'

import numpy as np
import sys
from multiprocessing import Pool as pool

import spectrumAnalyzer as specan

def round_freq(freq_in):
    return round(freq_in, 10)


class sa_hw_config():
    step = 0.001                # where (step size) * 1000 == (step size in kHz)
    RFin_min = 0.0
    RFin_max = 3000.0 + step    # Max input frequency for the spectrum analyzer
    RFin_list = list()
    
    def __init__(self):
        pass

    def create_SA_freq_step_file(self, fname: str='SA_full_range_1kHz_steps.csv'):
        """
        Public method
        Create the config file that contains every frequency from
        1-to-3000 MHz in 1 kHz increments.
        """
        LO1_list = [LO1_freq for LO1_freq in np.arange(self.RFin_min, self.RFin_max, self.step)]
        print(len(LO1_list))
        with open(fname, 'w') as f:
            with pool(processes=8) as executor:
                f.write(LO1_freq_list = executor.map(specan.MHz_to_fmn, LO1_list))

    

if __name__ == '__main__':
    print()











