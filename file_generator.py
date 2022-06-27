import psutil
import numpy as np
import sys
import spectrumAnalyzer as sa
from hardware_cfg import cfg

# Utilities provided for print debugging.
line = lambda: f'line {str(sys._getframe(1).f_lineno)},'
name = f'File \"{__name__}.py\",'

cpu_hw_cores = psutil.cpu_count(logical=False)

if __name__ == '__main__':
    print()
    print(f'Number of physical CPUs = {cpu_hw_cores}')
    num_loops = 1

    """ See if you can replace these two functions with a lambda  """
    def ref1_mhz_to_fmn(LO2_target_freq):
        fmn_list = sa.MHz_to_fmn(LO2_target_freq, Fref=66.0)
        return fmn_list

    def ref2_mhz_to_fmn(LO2_target_freq):
        fmn_list = sa.MHz_to_fmn(LO2_target_freq, Fref=66.666)
        return fmn_list

    # Fpfd sets the LO1 step size. 'ref_divider' is R and can be 1 for any RFin above 46.7 MHz
    Fpfd_list = [Fpfd/cfg.ref_divider for Fpfd in cfg.ref_list]
    # RFin_list contains every frequency from 0 to 3000.001 MHz in 1 kHz steps
    RFin_list = [freq for freq in np.arange(cfg._RFin_start, cfg._RFin_stop, cfg._RFin_step)]
    # Create the list of LO1 frequencies when using reference clock 1.
    LO1_ref1_freq_list = [int((cfg.IF1+RFin)/Fpfd_list[0]) * Fpfd_list[0] for RFin in RFin_list]
    LO1_ref1_freq_list = [round(x, 9) for x in LO1_ref1_freq_list]
    # Create the list of LO1 frequencies when using reference clock 2.
    LO1_ref2_freq_list = [int((cfg.IF1+RFin)/Fpfd_list[1]) * Fpfd_list[1] for RFin in RFin_list]
    LO1_ref2_freq_list = [round(x, 9) for x in LO1_ref2_freq_list]
    # Create the list of LO1 N values for setting the frequency of the ADF4356 chip when using reference clock 1
    LO1_ref1_N_list = [int(n/Fpfd_list[0]) for n in LO1_ref1_freq_list]
    # Create the list of LO1 N values for setting the frequency of the ADF4356 chip when using reference clock 2
    LO1_ref2_N_list = [int(n/Fpfd_list[1]) for n in LO1_ref2_freq_list]
    # Create the frequency lookup tables for LO1
    LO1_ref1_freq_dict = dict(zip(RFin_list, LO1_ref1_freq_list))
    LO1_ref2_freq_dict = dict(zip(RFin_list, LO1_ref2_freq_list))
    # Create the frequency lookup tables for LO2. (LO2_freq = LO1 - RFin + cfg.IF2)
    LO2_ref1_freq_list = [LO1_ref1_freq_dict[RFin] - RFin + cfg.IF2 for RFin in RFin_list]
    LO2_ref2_freq_list = [LO1_ref2_freq_dict[RFin] - RFin + cfg.IF2 for RFin in RFin_list]
    # Create the LO2 control codes for setting the frequency of the MAX2871 chip for ref clocks 1 and 2
    LO2_ref1_fmn_list = map(ref1_mhz_to_fmn, LO2_ref1_freq_list)
    LO2_ref2_fmn_list = map(ref2_mhz_to_fmn, LO2_ref2_freq_list)

    # Save LO1 files for ref1 and ref2
    with open("LO1_ref1_freq_steps.csv", 'w') as f:
        [f.write(str(freq) + '\n') for freq in LO1_ref1_freq_list]
    with open("LO1_ref2_freq_steps.csv", 'w') as f:
        [f.write(str(freq) + '\n') for freq in LO1_ref2_freq_list]
    with open("LO1_ref1_N_steps.csv", 'w') as f:
        [f.write(str(N) + '\n') for N in LO1_ref1_N_list]
    with open("LO1_ref2_N_steps.csv", 'w') as f:
        [f.write(str(N) + '\n') for N in LO1_ref2_N_list]
    # Save LO2 files for ref1 and ref2
    with open("LO2_ref1_freq_steps.csv", 'w') as f:
        [f.write(str(round(freq, 9)) + '\n') for freq in LO2_ref1_freq_list]
    with open("LO2_ref2_freq_steps.csv", 'w') as f:
        [f.write(str(round(freq, 9)) + '\n') for freq in LO2_ref2_freq_list]
    with open("LO2_ref1_fmn_steps.csv", 'w') as f:
        [f.write(str(fmn) + '\n') for fmn in LO2_ref1_fmn_list]
    with open("LO2_ref2_fmn_steps.csv", 'w') as f:
        [f.write(str(fmn) + '\n') for fmn in LO2_ref2_fmn_list]

    print("Done")













