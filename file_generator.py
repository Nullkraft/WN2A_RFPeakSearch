# -*- coding: utf-8 -*-

from hardware_cfg import cfg
import command_processor as cmd

class data_generator():
    """ These files will be used by calibrate_sa.py for creating the
        control dictionaries needed by the calibration scripts.
    """
    ref1 = cmd.ref_clock1_enable
    ref2 = cmd.ref_clock2_enable

    # RFin_array contains every frequency from 0 to 3000.001 MHz in 1 kHz steps
    RFin_array = cfg.RFin_array         # Test this redundant line: I think it sped things up

    def ref1_mhz_to_fmn(self, LO2_target_freq):
        fmn = cfg.MHz_to_fmn(LO2_target_freq, cfg.ref_clock_1)
        return fmn

    def ref2_mhz_to_fmn(self, LO2_target_freq):
        fmn = cfg.MHz_to_fmn(LO2_target_freq, cfg.ref_clock_2)
        return fmn

    def load_list(self, cntl_tuple) -> list:
        """
        Function Load the control codes for LO1, LO2 or LO3 into their associated lists.
        
        @param cntl_tuple A tuple of 2 values which contains the name of a file and the data type contained in the file.
        @type <class 'tuple'>
        @return A list containing the values of 'type'
        @rtype <class 'list'>
        """
        file_name, data_type = cntl_tuple
        tmp_list = list()
        with open(file_name, 'r') as f:
            for x in f:
                tmp_list.append(data_type(x))
        return tmp_list

    def write_dict(self, file_name, cntl_dict):
        """
        Function Saves the contents of a unit control dictionary to file
        
        @param file_name Name of the file to save the dictionary into
        @type <class 'str'>
        @param dict A dictionary where (key = RFin) and value = (LO1_n, LO2_fmn)
        @type <class 'dict'>
        """
        with open(file_name, 'w') as f:
            f.write("RFin ref LO1_N LO2_FMN\n")   # Header: what the data is used for.
            for freq, data in ctrl_dict.items():
                RFin = str(freq)
                ref = str(data[0])
                LO1_n = str(data[1])
                LO2_fmn = str(data[2])
                f.write(RFin + ' ' + ref + ' ' + LO1_n + ' ' + LO2_fmn + '\n')

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

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def create_ref1_control_file(self):
        LO1_n = self.load_list(('LO1_ref1_N_steps.csv', int))          # For sweeping. Convert N from a string to int
        LO2_fmn = self.load_list(('LO2_ref1_fmn_steps.csv', int))      # For sweeping. Convert fmn from string to int
        full_sweep_step_dict = {freq:(self.ref1, LO1, LO2) for freq, LO1, LO2 in zip(cfg.RFin_array, LO1_n, LO2_fmn)}
        self.write_dict('full_control_ref1.csv', full_sweep_step_dict)

    def create_ref2_control_file(self):
        LO1_n = self.load_list(('LO1_ref2_N_steps.csv', int))          # For sweeping. Convert N from a string to int
        LO2_fmn = self.load_list(('LO2_ref2_fmn_steps.csv', int))      # For sweeping. Convert fmn from string to int
        full_sweep_step_dict = {freq:(self.ref2, LO1, LO2) for freq, LO1, LO2 in zip(cfg.RFin_array, LO1_n, LO2_fmn)}
        self.write_dict('full_control_ref2.csv', full_sweep_step_dict)

    #full_sweep_freq_dict = {freq:(self.ref2, LO1, LO2) for freq, LO1, LO2 in zip(RFin, LO1_freq_list, LO2_freq_list)}
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__ == '__main__':
    print()

    print(f'Fpfd values are {cfg.Fpfd1} & {cfg.Fpfd2}')

    dg = data_generator()
    dg.create_data()
    dg.save_data_files()
    dg.create_ref1_control_file()
    dg.create_ref2_control_file()


    print("Generator done")













