# -*- coding: utf-8 -*-

from hardware_cfg import cfg
import command_processor as cmd

class calibrate():
    ref1 = cmd.ref1_enable
    ref2 = cmd.ref2_enable

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
            for freq in cntl_dict:
                RFin = str(freq)
                ref = str(cntl_dict[freq][0])
                LO1_n = str(cntl_dict[freq][1])
                LO2_fmn = str(cntl_dict[freq][2])
                f.write(RFin + ' ' + ref + ' ' + LO1_n + ' ' + LO2_fmn + '\n')

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


""" ********************* This block will move to spectrumAnalyzer.py ************************* """
#LO1_freq = self.load_list(('LO1_ref1_freq_steps.csv', float))  # For plotting. Convert f from a string to float
#LO2_freq = self.load_list(('LO2_ref1_freq_steps.csv', float))  # For plotting. Convert freq from string to float
#LO1_freq = self.load_list(('LO1_ref2_freq_steps.csv', float))  # For plotting. Convert f from a string to float
#LO2_freq = self.load_list(('LO2_ref2_freq_steps.csv', float))  # For plotting. Convert freq from string to float
"""
Reading the sweep dictionary from a file
"""
#test_dict = read_dict('full_control_ref1.csv')
"""
Set the sweep range and sweep step size
"""
#user_step_dict = dict(list(full_sweep_step_dict.items())[idx_start:idx_stop:idx_step])

""" ********************************************************************************************* """

if __name__ == '__main__':
    print()
    from time import perf_counter
    
    start_freq = 100.0
    stop_freq = 1000.430
    step_freq = 0.003
    
    start = perf_counter()
    cal = calibrate()

    cal.create_ref1_control_file()
#    cal.create_ref2_control_file()

    stop = perf_counter()

    print(f'cal took {round(stop-start, 10)} seconds')
    
#     1) Load the generated files for ref1
#     2) Program the SA with reference 1
#     3) Program the SA with LO1 and LO2 for each RFin
#     4) amplitude is collected from the 315 MHz filter A2D output
#     5) Create ampl_1_dict = {RFin: amplitude}
#     6) Save ampl_1_dict to ampl_ref1.csv
#    **** Next ****
#     7) Load the generated files for ref2
#     8) Program the SA with reference 2
#     9) Program the SA with LO1 and LO2 for each RFin
#    10) amplitude is collected from the 315 MHz filter A2D output
#    11) Create ampl_2_dict = {RFin: amplitude}
#    12) Save ampl_2_dict to ampl_ref2.csv
#    **** Next ****
#    13) Load sweep1 from full_control_ref1.csv
#    14) Load sweep2 from full_control_ref2.csv
#    15) Load Rfin_list from RFin_steps.csv
#    control_dict = dict()
#    for freq in RFin:
#        a1 = ampl_ref1_dict[freq]
#        a2 = ampl_ref2_dict[freq]
#        RFin = freq
#        if a2 < a1:
#            LO1, LO2 = sweep2[freq]
#            ref = cal.ref1
#        else:
#            LO1, LO2 = sweep1[freq]
#            ref = cal.ref2
#        tmp_dict = {RFin: (ref, LO1, LO2)}
#        control_dict.append(tmp_dict)
            

    print('Calibraion complete')












