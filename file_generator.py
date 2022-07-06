""" File Generator
    The generated files are used for creating the pre-calibration
    control dictionaries to be used by calibrate_sa.py
"""
import numpy as np

import spectrumAnalyzer as sa
from hardware_cfg import cfg

def ref1_mhz_to_fmn(LO2_target_freq):
    fmn = sa.MHz_to_fmn(LO2_target_freq, cfg.ref_clock_tuple[0])
    return fmn

def ref2_mhz_to_fmn(LO2_target_freq):
    fmn = sa.MHz_to_fmn(LO2_target_freq, cfg.ref_clock_tuple[1])
    return fmn

if __name__ == '__main__':
    print()

    # Fpfd sets the LO1 step size where ref_divider=1 for LO1 frequencies >= 3000 MHz
    Fpfd1 = cfg.ref_clock_tuple[0] / cfg.ref_divider
    Fpfd2 = cfg.ref_clock_tuple[1] / cfg.ref_divider
    # RFin_array contains every frequency from 0 to 3000.001 MHz in 1 kHz steps
    RFin_array = np.arange(cfg._RFin_start, cfg._RFin_stop, cfg._RFin_step)
    # Create the list of LO1 frequencies when using reference clock 1.
    LO1_ref1_freq_list = [int((cfg.IF1 + freq) / Fpfd1) * Fpfd1 for freq in RFin_array]
    LO1_ref1_freq_list = [round(x, 9) for x in LO1_ref1_freq_list]
    # Create the list of LO1 frequencies when using reference clock 2.
    LO1_ref2_freq_list = [int((cfg.IF1 + freq) / Fpfd2) * Fpfd2 for freq in RFin_array]
    LO1_ref2_freq_list = [round(x, 9) for x in LO1_ref2_freq_list]
    # Create the list of LO1 N values for setting the frequency of the ADF4356 chip when using reference clock 1
    LO1_ref1_N_list = [int(n/Fpfd1) for n in LO1_ref1_freq_list]
    # Create the list of LO1 N values for setting the frequency of the ADF4356 chip when using reference clock 2
    LO1_ref2_N_list = [int(n/Fpfd2) for n in LO1_ref2_freq_list]
    # Create the frequency lookup tables for LO1
    LO1_ref1_freq_dict = dict(zip(RFin_array, LO1_ref1_freq_list))
    LO1_ref2_freq_dict = dict(zip(RFin_array, LO1_ref2_freq_list))
    # Create the frequency lookup tables for LO2. (LO2_freq = LO1 - freq + cfg.IF2)
    LO2_ref1_freq_list = [LO1_ref1_freq_dict[freq] - freq + cfg.IF2 for freq in RFin_array]
    LO2_ref2_freq_list = [LO1_ref2_freq_dict[freq] - freq + cfg.IF2 for freq in RFin_array]
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













