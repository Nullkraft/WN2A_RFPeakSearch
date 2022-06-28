# -*- coding: utf-8 -*-
import sys
import psutil
import software_cfg as sw


# Utils to print filename and linenumber, print(name, line(), ...), when using print debugging.
line = lambda: f'line {str(sys._getframe(1).f_lineno)},'
name = f'File \"{__name__}.py\",'

cpu_hw_cores = psutil.cpu_count(logical=False)

#RFin_list = [0.1]
#LO1_n_list = [1]
#LO2_fmn_list = [1]
#LO1_freq_list = [0.1]
#LO2_freq_list = [0.1]
RFin_list = list()
LO1_n_list = list()
LO2_fmn_list = list()
LO1_freq_list = list()
LO2_freq_list = list()

# This needs to be set to nothing (not None) and the 'if calibrate'
# block needs be changed to an __init__ function in a class(calibrate)
calibrate = sw.cfg.ref_clock_1


def load_list(var_tuple):
    file_name, data_type = var_tuple
    tmp_list = list()
    with open(file_name, 'r') as f:
        for x in f:
            tmp_list.append(data_type(x))
    return tmp_list

def write_dict(file_name, dict):
    with open(file_name, 'w') as f:
        for freq in dict:
            f.write(str(freq) + ', ' + str(dict[freq][0]) + ', ' + str(dict[freq][1]) + '\n')

def read_dict(file_name) -> dict:
    with open(file_name, 'r') as in_file:
        new_dict = in_file.read()
    return new_dict

def freq_to_index(freq_MHz: float=4.0) -> int:
    return int(freq_MHz * 1000)

def index_to_freq(index: int=4000) -> float:
    return float(index / 1000)

freq_start = .001
freq_stop = 3000.001
freq_step = 3.746       # 3.746 makes 801 frequency sweep steps

idx_start = freq_to_index(freq_start)
idx_stop = freq_to_index(freq_stop)
idx_step = freq_to_index(freq_step)

# I *REALLY* want to use a threadpool when loading these lists from file(s)
from time import perf_counter
start = perf_counter()
RFin_list = load_list(('RFin_steps.csv', float))     # For sweeps and plots. Convert x from string to float
if calibrate is sw.cfg.ref_clock_1:
    LO1_n_list = load_list(('LO1_ref1_N_steps.csv', int))          # For sweeping. Convert N from a string to int
    LO2_fmn_list = load_list(('LO2_ref1_fmn_steps.csv', int))      # For sweeping. Convert fmn from string to int
    LO1_freq_list = load_list(('LO1_ref1_freq_steps.csv', float))  # For plotting. Convert f from a string to float
    LO2_freq_list = load_list(('LO2_ref1_freq_steps.csv', float))  # For plotting. Convert freq from string to float
elif calibrate is sw.cfg.ref_clock_2:
    LO1_n_list = load_list(('LO1_ref2_N_steps.csv', int))          # For sweeping. Convert N from a string to int
    LO2_fmn_list = load_list(('LO2_ref2_fmn_steps.csv', int))      # For sweeping. Convert fmn from string to int
    LO1_freq_list = load_list(('LO1_ref2_freq_steps.csv', float))  # For plotting. Convert f from a string to float
    LO2_freq_list = load_list(('LO2_ref2_freq_steps.csv', float))  # For plotting. Convert freq from string to float
if calibrate is None:
    LO1_n_list = load_list(('LO1_N_steps.csv', int))               # For sweeping. Convert N from a string to int
    LO2_fmn_list = load_list(('LO2_fmn_steps.csv', int))           # For sweeping. Convert fmn from string to int
    LO1_freq_list = load_list(('LO1_freq_steps.csv', float))       # For plotting. Convert f from a string to float
    LO2_freq_list = load_list(('LO2_freq_steps.csv', float))       # For plotting. Convert freq from string to float

# Create the main lookup table, freq_step_dict, where the
# key == RFin_freq in Hz and the value is a tuple that
# contains the 
full_sweep_step_dict = {freq:(LO1, LO2) for freq, LO1, LO2 in zip(RFin_list, LO1_n_list, LO2_fmn_list)}
full_sweep_freq_dict = {freq:(LO1, LO2) for freq, LO1, LO2 in zip(RFin_list, LO1_freq_list, LO2_freq_list)}


if calibrate is sw.cfg.ref_clock_1:
    write_dict('full_sweep_dict_1.csv', full_sweep_step_dict)
if calibrate is sw.cfg.ref_clock_2:
    write_dict('full_sweep_dict_2.csv', full_sweep_step_dict)
if calibrate is None:
    write_dict('full_sweep_dict.csv', full_sweep_step_dict)

print(f'Time to load lists = {round(perf_counter()-start, 2)} seconds')

""" ********************* This block will move to spectrumAnalyzer.py ************************* """
"""
Reading the sweep dictionary from a file
"""
test_dict = read_dict('full_sweep_dict_1.csv')
"""
Set the sweep range and sweep step size
"""
user_step_dict = dict(list(full_sweep_step_dict.items())[idx_start:idx_stop:idx_step])

""" ********************************************************************************************* """

print("********** Calibration done **********")

if __name__ == '__main__':
    print()
    
    RFin_list = load_list(('RFin_steps.csv', float))     # For sweeps and plots. Convert x from string to float
    LO1_n_list = load_list(('LO1_ref1_N_steps.csv', int))          # For sweeping. Convert N from a string to int
    LO2_fmn_list = load_list(('LO2_ref1_fmn_steps.csv', int))      # For sweeping. Convert fmn from string to int
    
    full_sweep_step_dict = {freq:(LO1, LO2) for freq, LO1, LO2 in zip(RFin_list, LO1_n_list, LO2_fmn_list)}
    write_dict('full_sweep_dict_1.csv', full_sweep_step_dict)













