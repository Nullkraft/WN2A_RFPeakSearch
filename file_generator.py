import psutil
from multiprocessing import Pool as pool
import numpy as np
import time
import sys
import spectrumAnalyzer as sa

# Instance of the spectrum analyzer hardware class
hw = sa.hardware()      # hardware class defines the frequency sweep parameters

# Utilities provided for print debugging.
line = lambda : sys._getframe(1).f_lineno
name = __name__

num_hw_cores = psutil.cpu_count(logical=False)



def round_to_9_decimals(x):
    """
    @Function The round() function requires two parameters but
    the map() function can only apply one.  Rounding makes the
    result more manageable by appearing to be exact.

    @param x A value that was a decimal approximation
    @type int or float
    @return The 'exact' representation of the decimal approximation.
    @rtype int or float
    """
    return round(x, 9)

def make_RFin_file():
    """
    Function Generates a 1 kHz step file for the Spectrum Analyzer.
    NOTE that generating this file does not require a reference frequency.
    """
    unit_step_MHz = 0.001
    unit_start_MHz = 0.0
    unit_stop_MHz = 3000.0 + unit_step_MHz
    freq_file = "RFin_1kHz_freq_steps.csv"
    with pool(processes=num_hw_cores) as executor:
        full_freq_list = executor.map(round_to_9_decimals, np.arange(unit_start_MHz, unit_stop_MHz, unit_step_MHz))
    with open(freq_file, 'w') as frq:
        [frq.write(str(round(freq, 3)) + '\n') for freq in full_freq_list]


def make_LO1_files(ref_clock: float=66.0, ref_divider: int=2):
    LO1_freq_file = "LO1_1kHz_freq_steps.csv"
    LO1_n_file = "LO1_1kHz_n_steps.csv"
    
    Fpfd = ref_clock / ref_divider      # This will be used as the LO1 freq step size
    print(f'Fpfd = {Fpfd}')
    n_list = []
    unit_freq_list = hw.load_RFin_list('RFin_1kHz_freq_steps.csv')  # Get 1kHz freq step list
    with pool(processes=num_hw_cores) as executor:
        LO1_freq_list = executor.map(sa.get_LO1_freq, unit_freq_list)
    with open(LO1_freq_file, 'w') as frq:
        for freq in LO1_freq_list:
            frq.write(str(round(freq, 3)) + '\n')   # Write the given frequency to the step file
            n = int(freq/Fpfd)                      # Calculate LO1_n for the given frequency
            n_list.append(n)                        # Creating the LO1_n_list
    with open(LO1_n_file, 'w') as f:
        for n in n_list:
            f.write(str(n) + '\n')                  # Copy the LO1_n_list contents to the n step file


def make_LO2_files(ref_clock: float=66.0, ref_divider: int=2):
    """
    Function Generates an FMN step file for use by LO2 and LO3.
    Only used to regenerate missing file or initially create the step file.
    """
    fmn_list = []
#    Fpfd = ref_clock / ref_divider      # This will be used as the LO1 freq step size
    unit_freq_list = hw.load_RFin_list('RFin_1kHz_freq_steps.csv')  # Get 1kHz freq step list
    start = time.perf_counter()
    with pool(processes=num_hw_cores) as executor:
        LO2_freq_list = executor.map(sa.get_LO2_freq, unit_freq_list)
    LO2_freq_file = "LO2_1kHz_freq_steps.csv"
    print(name, line(), f'Length LO2 Freq list = {len(LO2_freq_list)}')
    fmn_file = "LO2_1kHz_fmn_steps.csv"
    with open(LO2_freq_file, 'w') as frq:
        for freq in unit_freq_list:
#            step = time.perf_counter()
            frq.write(str(round(freq, 3)) + '\n')   # Write the given frequency to the step file
            fmn = sa.MHz_to_fmn(freq)          # Calculate LO2_fmn for the given frequency
            fmn_list.append(fmn)                    # Creating the LO2_fmn_list
#            print(name, line(), f'for freq in LO2_freq_list = {round(time.perf_counter()-step, 6)} seconds')
    with open(fmn_file, 'w') as f:
        for f_m_n in fmn_list:
            f.write(str(f_m_n) + '\n')              # Copy the LO2_fmn_list contents to the fmn step file
    print(name, line(), f'Wrote LO2_1kHz_freq_steps.csv in {round(time.perf_counter()-start, 3)} seconds')



if __name__ == '__main__':
    print()
    print(f'Number of physical CPUs = {num_hw_cores}')
    num_loops = 1
    
    IF1 = 3600                      # First intermediate frequency
    ref_divider = 2
    ref_list = [66.000, 66.666]
    RFin_start = 0.0
    RFin_stop = 3000.001
    RFin_step = 0.001
    
    start = time.perf_counter()
        
    Fpfd_list = [Fpfd/ref_divider for Fpfd in ref_list]
    RFin_list = [freq for freq in np.arange(RFin_start, RFin_stop, RFin_step)]
    LO1_ref1_list = [int((IF1+RFin)/Fpfd_list[0]) * Fpfd_list[0] for RFin in RFin_list]
    LO1_ref2_list = [int((IF1+RFin)/Fpfd_list[1]) * Fpfd_list[1] for RFin in RFin_list]

#    LO2_ref1_list = 
#    LO2_ref2_list = 
    """ TODO: Create 2 LO2 refn freq lists """
    
    """ TODO: Create 2 LO2 fmn lists """

    """ TODO: Create 2 LO1 dictionaries from RFin_list """
    
    """ TODO: Create 2 LO2 dictionaries from RFin_list """
    
    print(f'Time to create LO1 ref(n) lists = {time.perf_counter()-start}')
    print("Done")















