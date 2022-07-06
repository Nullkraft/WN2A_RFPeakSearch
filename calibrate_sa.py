# -*- coding: utf-8 -*-
import sys
import psutil

import command_processor as cmd

# Utils to print filename and linenumber, print(name, line(), ...), when using print debugging.
line = lambda: f'line {str(sys._getframe(1).f_lineno)},'
name = f'File \"{__name__}.py\",'

cpu_hw_cores = psutil.cpu_count(logical=False)

RFin = list()
LO1_n = list()
LO2_fmn = list()
LO1_freq = list()
LO2_freq = list()

ref1 = cmd.ref1_enable
ref2 = cmd.ref2_enable

def load_list(var_tuple) -> list:
    """
    Function Load the control codes for LO1, LO2 or LO3 into their associated lists.
    
    @param var_tuple A tuple of 2 values which contains the name of a file and the data type contained in the file.
    @type <class 'tuple'>
    @return A list containing the values of 'type'
    @rtype <class 'list'>
    """
    file_name, data_type = var_tuple
    tmp_list = list()
    with open(file_name, 'r') as f:
        for x in f:
            tmp_list.append(data_type(x))
    return tmp_list

def write_dict(file_name, dict):
    """
    Function Saves the contents of a unit control dictionary to file
    
    @param file_name Name of the file to save the dictionary into
    @type <class 'str'>
    @param dict A dictionary where (key = RFin) and value = (LO1_n, LO2_fmn)
    @type <class 'dict'>
    """
    with open(file_name, 'w') as f:
        for freq in dict:
            RFin = str(freq)
            ref = str(dict[freq][0])
            LO1_n = str(dict[freq][1])
            LO2_fmn = str(dict[freq][2])
            f.write(RFin + ', ' + ref + ', ' + LO1_n + ', ' + LO2_fmn + '\n')

def read_dict(file_name) -> dict:
    with open(file_name, 'r') as in_file:
        new_dict = in_file.read()
    return new_dict

def freq_to_index(freq_MHz: float=4.0) -> int:
    return int(freq_MHz * 1000)

def index_to_freq(index: int=4000) -> float:
    return float(index / 1000)

RFin = load_list(('RFin_steps.csv', float))     # For sweeps and plots. Convert x from string to float

def create_control_file_1():
    LO1_n = load_list(('LO1_ref1_N_steps.csv', int))          # For sweeping. Convert N from a string to int
    LO2_fmn = load_list(('LO2_ref1_fmn_steps.csv', int))      # For sweeping. Convert fmn from string to int
    full_sweep_step_dict = {freq:(ref1, LO1, LO2) for freq, LO1, LO2 in zip(RFin, LO1_n, LO2_fmn)}
    write_dict('full_control_ref1.csv', full_sweep_step_dict)
#    LO1_freq = load_list(('LO1_ref1_freq_steps.csv', float))  # For plotting. Convert f from a string to float
#    LO2_freq = load_list(('LO2_ref1_freq_steps.csv', float))  # For plotting. Convert freq from string to float

def create_control_file_2():
    LO1_n = load_list(('LO1_ref2_N_steps.csv', int))          # For sweeping. Convert N from a string to int
    LO2_fmn = load_list(('LO2_ref2_fmn_steps.csv', int))      # For sweeping. Convert fmn from string to int
    full_sweep_step_dict = {freq:(ref2, LO1, LO2) for freq, LO1, LO2 in zip(RFin, LO1_n, LO2_fmn)}
    write_dict('full_control_ref2.csv', full_sweep_step_dict)
#    LO1_freq = load_list(('LO1_ref2_freq_steps.csv', float))  # For plotting. Convert f from a string to float
#    LO2_freq = load_list(('LO2_ref2_freq_steps.csv', float))  # For plotting. Convert freq from string to float

#full_sweep_freq_dict = {freq:(ref2, LO1, LO2) for freq, LO1, LO2 in zip(RFin, LO1_freq_list, LO2_freq_list)}


""" ********************* This block will move to spectrumAnalyzer.py ************************* """
"""
Reading the sweep dictionary from a file
"""
#test_dict = read_dict('full_control_ref1.csv')
"""
Set the sweep range and sweep step size
"""
#user_step_dict = dict(list(full_sweep_step_dict.items())[idx_start:idx_stop:idx_step])

""" ********************************************************************************************* """

print("********** Calibration done **********")

if __name__ == '__main__':
    print()
    create_control_file_1()
    create_control_file_2()
    print(len(RFin))
    
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
#            ref = hw.cfg.ref_clock_tuple[1]
#        else:
#            LO1, LO2 = sweep1[freq]
#            ref = hw.cfg.ref_clock_tuple[0]
#        tmp_dict = {RFin: (ref, LO1, LO2)}
#        control_dict.append(tmp_dict)
            

    print('Calibraion complete')












