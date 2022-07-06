# -*- coding: utf-8 -*-

import spectrumAnalyzer as sa
from hardware_cfg import cfg

class data_generator():
    """ These files will be used by calibrate_sa.py for creating the
        control dictionaries needed by the calibration scripts.
    """
    # RFin_array contains every frequency from 0 to 3000.001 MHz in 1 kHz steps
    RFin_array = cfg.RFin_array

    def ref1_mhz_to_fmn(self, LO2_target_freq):
        fmn = sa.MHz_to_fmn(LO2_target_freq, cfg.ref_clock_1)
        return fmn

    def ref2_mhz_to_fmn(self, LO2_target_freq):
        fmn = sa.MHz_to_fmn(LO2_target_freq, cfg.ref_clock_2)
        return fmn

    def create_data(self):
        # Create the list of LO1 frequencies when using reference clock 1.
        self.LO1_ref1_freq_list = [int((cfg.IF1 + freq) / cfg.Fpfd1) * cfg.Fpfd1 for freq in self.RFin_array]
        self.LO1_ref1_freq_list = [round(x, 9) for x in self.LO1_ref1_freq_list]
        # Create the list of LO1 frequencies when using reference clock 2.
        self.LO1_ref2_freq_list = [int((cfg.IF1 + freq) / cfg.Fpfd2) * cfg.Fpfd2 for freq in self.RFin_array]
        self.LO1_ref2_freq_list = [round(x, 9) for x in self.LO1_ref2_freq_list]
        # Create the list of LO1 N values for setting the frequency of the ADF4356 chip when using reference clock 1
        self.LO1_ref1_N_list = [int(n/cfg.Fpfd1) for n in self.LO1_ref1_freq_list]
        # Create the list of LO1 N values for setting the frequency of the ADF4356 chip when using reference clock 2
        self.LO1_ref2_N_list = [int(n/cfg.Fpfd2) for n in self.LO1_ref2_freq_list]
        # Create the frequency lookup tables for LO1
        self.LO1_ref1_freq_dict = dict(zip(self.RFin_array, self.LO1_ref1_freq_list))
        self.LO1_ref2_freq_dict = dict(zip(self.RFin_array, self.LO1_ref2_freq_list))
        # Create the frequency lookup tables for LO2. (LO2_freq = LO1 - freq + cfg.IF2)
        self.LO2_ref1_freq_list = [self.LO1_ref1_freq_dict[freq] - freq + cfg.IF2 for freq in self.RFin_array]
        self.LO2_ref2_freq_list = [self.LO1_ref2_freq_dict[freq] - freq + cfg.IF2 for freq in self.RFin_array]
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

    print(f'Fpfd values are {cfg.Fpfd1} & {cfg.Fpfd2}')

    dg = data_generator()
    dg.create_data()
    dg.save_data_files()


    print("Generator done")













