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
    NOTE: Generating this file does not require a reference frequency.
    """
    num_hw_cores = psutil.cpu_count(logical=False)
    print(f'Number of physical CPUs = {num_hw_cores}')
    unit_step_MHz = 0.001
    unit_start_MHz = 0.0
    unit_stop_MHz = 3000.0 + unit_step_MHz
    freq_file = "RFin_1kHz_freq_steps.csv"
    with pool(processes=num_hw_cores) as executor:
        full_freq_list = executor.map(round_to_9_decimals, np.arange(unit_start_MHz, unit_stop_MHz, unit_step_MHz))
    start = time.perf_counter()
    with open(freq_file, 'w') as frq:
        [frq.write(str(round(freq, 3)) + '\n') for freq in full_freq_list]
    print(name, line(), f'Wrote RFin_1kHz_freq_steps.csv in {time.perf_counter()-start} seconds')


def make_LO1_files():
    n_list = []
    unit_freq_list = hw.load_RFin_list('RFin_1kHz_freq_steps.csv')
    with pool(processes=4) as executor:
        LO1_freq_list = executor.map(sa.get_LO1_freq, unit_freq_list)
    LO1_freq_file = "LO1_1kHz_freq_steps.csv"
    n_file = "LO1_1kHz_n_steps.csv"
    with open(LO1_freq_file, 'w') as frq:
        for freq in LO1_freq_list:                  # Assumes Fpfd = 30 MHz
            frq.write(str(round(freq, 3)) + '\n')   # Write the given frequency to the step file
            n = int(freq/30)                        # Calculate LO1_n for the given frequency
            n_list.append(n)                        # Creating the LO1_n_list
    with open(n_file, 'w') as f:
        for n in n_list:
            f.write(str(n) + '\n')                  # Copy the LO1_n_list contents to the n step file


def make_LO2_files():
    """
    Function Generates an FMN step file for use by LO2 and LO3.
    Only used to regenerate missing file or initially create the step file.
    """
    fmn_list = []
    unit_freq_list = hw.load_RFin_list()
    with pool(processes=4) as executor:
        LO2_freq_list = executor.map(sa.get_LO2_freq, unit_freq_list)
    freq_file = "LO2_1kHz_freq_steps.csv"
    fmn_file = "LO2_1kHz_fmn_steps.csv"
    with open(freq_file, 'w') as frq:
        for freq in LO2_freq_list:                  # Assumes Fpfd = 30 MHz
            frq.write(str(round(freq, 3)) + '\n')   # Write the given frequency to the step file
            fmn = sa.MHz_to_fmn(freq)                  # Calculate LO2_fmn for the given frequency
            fmn_list.append(fmn)                    # Creating the LO2_fmn_list
    with open(fmn_file, 'w') as f:
        for f_m_n in fmn_list:
            f.write(str(f_m_n) + '\n')              # Copy the LO2_fmn_list contents to the fmn step file




if __name__ == '__main__':
    print()
    num_loops = 1

    make_RFin_file()
#    make_LO1_files()
#    make_LO2_files()

#    full_freq_list = load_LO2_freq_steps()
#    LO2_list = list(LO2_30Fpfd_steps)
#    LO2_dict = dict(LO2_30Fpfd_steps)


    print("Done")

