import psutil
from multiprocessing import Pool as pool
import numpy as np
import time
import sys
import spectrumAnalyzer as sa

# Utilities provided for print debugging.
line = lambda : sys._getframe(1).f_lineno
name = __name__

cpu_hw_cores = psutil.cpu_count(logical=False)

if __name__ == '__main__':
    print()
    print(f'Number of physical CPUs = {cpu_hw_cores}')
    num_loops = 1

    ref_list = [66.000, 66.666]
    ref_divider = 2
    IF1 = 3600                      # First intermediate frequency in MHz
    IF2 = 315                       # Second intermediate frequency in MHz
    RFin_start = 0.0
    RFin_stop = 3000.001            # Spectrum analyzer bandwidth is 3 GHz
    RFin_step = 0.001
    
    """ See if you can replace these two functions with a lambda  """
    def ref1_mhz_to_fmn(LO2_target_freq):
        fmn = sa.MHz_to_fmn(LO2_target_freq, Fref=66.0)
        return fmn

    def ref2_mhz_to_fmn(LO2_target_freq):
        fmn = sa.MHz_to_fmn(LO2_target_freq, Fref=66.666)
        return fmn

    start = time.perf_counter()

    # Fpfd is the LO1 step size
    Fpfd_list = [Fpfd/ref_divider for Fpfd in ref_list]
    # RFin_list contains every frequency from 0 to 3000.001 MHz in 1 kHz steps
    RFin_list = [freq for freq in np.arange(RFin_start, RFin_stop, RFin_step)]

    # List of LO1 frequencies when using reference clock 1.
    LO1_ref1_list = [int((IF1+RFin)/Fpfd_list[0]) * Fpfd_list[0] for RFin in RFin_list]
    # List of LO1 frequencies when using reference clock 2.
    LO1_ref2_list = [int((IF1+RFin)/Fpfd_list[1]) * Fpfd_list[1] for RFin in RFin_list]
    # Save LO1 frequency files for ref1 and ref2
    with open("LO1_ref1_freq_steps.csv", 'w') as f:
        [f.write(str(freq) + '\n') for freq in LO1_ref1_list]
    with open("LO1_ref2_freq_steps.csv", 'w') as f:
        [f.write(str(freq) + '\n') for freq in LO1_ref2_list]

    # List of LO1 N values for setting the frequency of the ADF435 chip when using reference clock 1
    LO1_ref1_N_list = [int(n/Fpfd_list[0]) for n in LO1_ref1_list]
    # List of LO1 N values for setting the frequency of the ADF435 chip when using reference clock 2
    LO1_ref2_N_list = [int(n/Fpfd_list[1]) for n in LO1_ref2_list]
    with open("LO1_ref1_N_steps.csv", 'w') as f:
        [f.write(str(N) + '\n') for N in LO1_ref1_N_list]
    with open("LO1_ref2_N_steps.csv", 'w') as f:
        [f.write(str(N) + '\n') for N in LO1_ref2_N_list]

    LO1_ref1_dict = dict(zip(RFin_list, LO1_ref1_list))
    LO1_ref2_dict = dict(zip(RFin_list, LO1_ref2_list))

    # LO2 = LO1 - RFin + IF2
    LO2_ref1_list = [LO1_ref1_dict[RFin] - RFin + IF2 for RFin in RFin_list]
    LO2_ref2_list = [LO1_ref2_dict[RFin] - RFin + IF2 for RFin in RFin_list]
    with open("LO2_ref1_freq_steps.csv", 'w') as f:
        [f.write(str(round(freq, 9)) + '\n') for freq in LO2_ref1_list]
    with open("LO2_ref2_freq_steps.csv", 'w') as f:
        [f.write(str(round(freq, 9)) + '\n') for freq in LO2_ref2_list]

    with pool(cpu_hw_cores) as executor:
        LO2_ref1_fmn_list = executor.map(ref1_mhz_to_fmn, LO2_ref1_list)
        LO2_ref2_fmn_list = executor.map(ref2_mhz_to_fmn, LO2_ref2_list)
    with open("LO2_ref1_fmn_steps.csv", 'w') as f:
        [f.write(str(fmn) + '\n') for fmn in LO2_ref1_fmn_list]
    with open("LO2_ref2_fmn_steps.csv", 'w') as f:
        [f.write(str(fmn) + '\n') for fmn in LO2_ref1_fmn_list]

    stop = time.perf_counter()

    print(f'Time to create files = {round((stop - start)/60, 2)} min(s)')
    print("Done")















