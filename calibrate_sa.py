# -*- coding: utf-8 -*-

RFin_list = list()
LO1_n_list = list()
LO2_fmn_list = list()
LO1_freq_list = list()
LO2_freq_list = list()

ref_clock_1, ref_clock_2, both_refs = 1, 2, 4
calibrate = ref_clock_1

def load_list(list_name, file_name, data_type):
    with open(file_name, 'r') as f:
        [list_name.append(data_type(x)) for x in f]

def write_dict(file_name, dict):
    with open(file_name, 'w') as save_file:
        save_file.write(str(dict))

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
load_list(RFin_list, 'RFin_1kHz_freq_steps.csv', float)     # For sweeps and plots. Convert x from string to float
if calibrate is ref_clock_1:
    load_list(LO1_n_list, 'LO1_ref1_N_steps.csv', int)          # For sweeping. Convert N from a string to int
    load_list(LO2_fmn_list, 'LO2_ref1_fmn_steps.csv', int)      # For sweeping. Convert fmn from string to int
    load_list(LO1_freq_list, 'LO1_ref1_freq_steps.csv', float)  # For plotting. Convert f from a string to float
    load_list(LO2_freq_list, 'LO2_ref1_freq_steps.csv', float)  # For plotting. Convert freq from string to float
elif calibrate is ref_clock_2:
    load_list(LO1_n_list, 'LO1_ref2_N_steps.csv', int)          # For sweeping. Convert N from a string to int
    load_list(LO2_fmn_list, 'LO2_ref2_fmn_steps.csv', int)      # For sweeping. Convert fmn from string to int
    load_list(LO1_freq_list, 'LO1_ref2_freq_steps.csv', float)  # For plotting. Convert f from a string to float
    load_list(LO2_freq_list, 'LO2_ref2_freq_steps.csv', float)  # For plotting. Convert freq from string to float
if calibrate is both_refs:
    load_list(LO1_n_list, 'LO1_N_steps.csv', int)               # For sweeping. Convert N from a string to int
    load_list(LO2_fmn_list, 'LO2_fmn_steps.csv', int)           # For sweeping. Convert fmn from string to int
    load_list(LO1_freq_list, 'LO1_freq_steps.csv', float)       # For plotting. Convert f from a string to float
    load_list(LO2_freq_list, 'LO2_freq_steps.csv', float)       # For plotting. Convert freq from string to float

# Create the main lookup table, freq_step_dict, where the
# key == RFin_freq in Hz and the value is a tuple that
# contains the 
full_sweep_step_dict = {freq:(LO1, LO2) for freq, LO1, LO2 in zip(RFin_list, LO1_n_list, LO2_fmn_list)}
full_sweep_freq_dict = {freq:(LO1, LO2) for freq, LO1, LO2 in zip(RFin_list, LO1_freq_list, LO2_freq_list)}

write_dict('full_sweep_step_dict.csv', full_sweep_step_dict)


""" ********************* This block will move to spectrumAnalyzer.py ************************* """
"""
Reading the sweep dictionary from a file
"""
test_dict = read_dict('full_sweep_step_dict.csv')
"""
Set the sweep range and sweep step size
"""
user_step_dict = dict(list(full_sweep_step_dict.items())[idx_start:idx_stop:idx_step])

""" ********************************************************************************************* """

print("********** Calibration done **********")

if __name__ == '__main__':
    print()














