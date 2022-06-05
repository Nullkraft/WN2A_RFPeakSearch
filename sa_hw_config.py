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

    
    def create_LO1_freq_step_file(self, in_file: str='SA_full_range_1kHz_steps.csv', out_file: str='LO1_dict_keys.csv'):
        """
        Public method
        Create the config file that contains every value of LO1 frequency from
        3000-to-6000 MHz using the SA_full_range_freq_steps as input.
        """
        with open(in_file, 'r') as in_freq:
            print(in_freq)
#        RF_in = 1700.0
#        LO1_freq_lo_ref = specan.get_LO1_freq(RFin=RF_in, Fref_MHz=66.000, IF1_MHz=3600.0)
#        LO1_freq_hi_ref = specan.get_LO1_freq(RFin=RF_in, Fref_MHz=66.666, IF1_MHz=3600.0)
#        return LO1_freq_lo_ref,  LO1_freq_hi_ref
        
    
    def create_LO1_n_file(self, fname: str='LO1_dict_values.csv'):
        """
        Public method 
        
        """
        pass
        
    
    def create_freq_step_file(self, fname: str='SA_1kHz_freq_steps.csv'):
        """
        Public method
        Create the config file that contains every frequency from
        1-to-3000 MHz in 1 kHz increments.
        """
        pass
        
    
    def create_LO2_fmn_file(self, fname: str='LO2_fmn_steps.csv'):
        """
        Public method
        Create the config file that contains the LO2 FMN values for each frequency
        found in the 1 kHz freq step file.
        Each FMN value is found by choosing one of the two reference oscillators. 
        The selection of the reference oscillator is made such that it will avoid 
        being within 180 kHz of an integer multiple of the IF1 frequency.
        """
        pass


if __name__ == '__main__':
    print()
#    RF_in = 1700.0
#    low_ref = 33.000        # MHz
#    hi_ref = 33.333         # MHz
    sahw = sa_hw_config
#    LO1_low, LO1_hi = sa_hw_config.create_LO1_freq_step_file(sahw)
#    IF1_low = np.around(LO1_low - RF_in, 6)
#    IF1_hi = np.around(LO1_hi - RF_in, 6)
#    print(f'LO1_low = {LO1_low}   MHz;\tIF1_low = {IF1_low};\tIF1_low % low_ref = {np.around(IF1_low % low_ref, 6)}')
#    print(f'LO1_hi  = {LO1_hi} MHz;\tIF1_hi  = {IF1_hi};\tIF1_hi % hi_ref   = {np.around(IF1_hi % hi_ref, 6)}')
    LO1_list = sa_hw_config.create_SA_freq_step_file(sahw)











