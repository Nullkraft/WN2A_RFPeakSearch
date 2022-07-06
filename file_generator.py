""" File Generator
    The generated files are used for creating the pre-calibration
    control dictionaries to be used by calibrate_sa.py
"""
import numpy as np

import spectrumAnalyzer as sa
from hardware_cfg import cfg

class data_generator():
    # Fpfd sets the LO1 step size where ref_divider=1 for LO1 frequencies >= 3000 MHz
    fpfd1 = cfg.Fpfd1
    fpfd2 = cfg.Fpfd2
    
    start = cfg._RFin_start
    stop = cfg._RFin_stop
    step = cfg._RFin_step

    def ref1_mhz_to_fmn(self, LO2_target_freq):
        fmn = sa.MHz_to_fmn(LO2_target_freq, cfg.ref_clock_tuple[0])
        return fmn

    def ref2_mhz_to_fmn(self, LO2_target_freq):
        fmn = sa.MHz_to_fmn(LO2_target_freq, cfg.ref_clock_tuple[1])
        return fmn

    def create_data(self):
        # RFin_array contains every frequency from 0 to 3000.001 MHz in 1 kHz steps
        RFin_array = np.arange(self.start, self.stop, self.step)
        # Create the list of LO1 frequencies when using reference clock 1.
        self.LO1_ref1_freq_list = [int((cfg.IF1 + freq) / self.fpfd1) * self.fpfd1 for freq in RFin_array]
        self.LO1_ref1_freq_list = [round(x, 9) for x in self.LO1_ref1_freq_list]
        # Create the list of LO1 frequencies when using reference clock 2.
        self.LO1_ref2_freq_list = [int((cfg.IF1 + freq) / self.fpfd2) * self.fpfd2 for freq in RFin_array]
        self.LO1_ref2_freq_list = [round(x, 9) for x in self.LO1_ref2_freq_list]
        # Create the list of LO1 N values for setting the frequency of the ADF4356 chip when using reference clock 1
        self.LO1_ref1_N_list = [int(n/self.fpfd1) for n in self.LO1_ref1_freq_list]
        # Create the list of LO1 N values for setting the frequency of the ADF4356 chip when using reference clock 2
        self.LO1_ref2_N_list = [int(n/self.fpfd2) for n in self.LO1_ref2_freq_list]
        # Create the frequency lookup tables for LO1
        self.LO1_ref1_freq_dict = dict(zip(RFin_array, self.LO1_ref1_freq_list))
        self.LO1_ref2_freq_dict = dict(zip(RFin_array, self.LO1_ref2_freq_list))
        # Create the frequency lookup tables for LO2. (LO2_freq = LO1 - freq + cfg.IF2)
        self.LO2_ref1_freq_list = [self.LO1_ref1_freq_dict[freq] - freq + cfg.IF2 for freq in RFin_array]
        self.LO2_ref2_freq_list = [self.LO1_ref2_freq_dict[freq] - freq + cfg.IF2 for freq in RFin_array]
        # Create the LO2 control codes for setting the frequency of the MAX2871 chip for ref clocks 1 and 2
        self.LO2_ref1_fmn_list = map(self.ref1_mhz_to_fmn, self.LO2_ref1_freq_list)
        self.LO2_ref2_fmn_list = map(self.ref2_mhz_to_fmn, self.LO2_ref2_freq_list)

    def save_data_files(self):
        """
        Save LO1 files for ref1 and ref2
        """
        with open("LO1_ref1_freq_steps.csv", 'w') as f:
            [f.write(str(freq) + '\n') for freq in self.LO1_ref1_freq_list]
        with open("LO1_ref2_freq_steps.csv", 'w') as f:
            [f.write(str(freq) + '\n') for freq in self.LO1_ref2_freq_list]
        with open("LO1_ref1_N_steps.csv", 'w') as f:
            [f.write(str(N) + '\n') for N in self.LO1_ref1_N_list]
        with open("LO1_ref2_N_steps.csv", 'w') as f:
            [f.write(str(N) + '\n') for N in self.LO1_ref2_N_list]
        """
        Save LO2 files for ref1 and ref2
        """
        with open("LO2_ref1_freq_steps.csv", 'w') as f:
            [f.write(str(round(freq, 9)) + '\n') for freq in self.LO2_ref1_freq_list]
        with open("LO2_ref2_freq_steps.csv", 'w') as f:
            [f.write(str(round(freq, 9)) + '\n') for freq in self.LO2_ref2_freq_list]
        with open("LO2_ref1_fmn_steps.csv", 'w') as f:
            [f.write(str(fmn) + '\n') for fmn in self.LO2_ref1_fmn_list]
        with open("LO2_ref2_fmn_steps.csv", 'w') as f:
            [f.write(str(fmn) + '\n') for fmn in self.LO2_ref2_fmn_list]

if __name__ == '__main__':
    print()

    dg = data_generator()
    print(f'Fpfd values are {dg.fpfd1} & {dg.fpfd2}')
    
    dg.create_data()
    dg.save_data_files()


    print("Generator done")













