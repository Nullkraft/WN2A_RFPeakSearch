
from dataclasses import dataclass

@dataclass
class cfg():
    ref_clock_1 = 0
    ref_clock_2 = 1

    RFin_list = list()
    LO1_n_list = list()
    LO2_fmn_list = list()
    LO1_freq_list = list()
    LO2_freq_list = list()

    """
    How to provide more than one argument to the function when using comprehension.
    """
    tuple_of_lists = RFin_list, LO1_n_list, LO2_fmn_list, LO1_freq_list, LO2_freq_list
    ref1_dat_files = 'RFin_steps.csv', 'LO1_ref1_N_steps.csv', 'LO2_ref1_fmn_steps.csv', 'LO1_ref1_freq_steps.csv', 'LO2_ref1_freq_steps.csv'
    ref2_dat_files = 'RFin_steps.csv', 'LO1_ref2_N_steps.csv', 'LO2_ref2_fmn_steps.csv', 'LO1_ref2_freq_steps.csv', 'LO2_ref2_freq_steps.csv'
    tuple_of_types = float, int, int, float, float

    """ Load all lists for ref1 """
    arg_list = list(zip(tuple_of_lists, ref1_dat_files, tuple_of_types))





    sweep_control_files = 'LO1_N_steps.csv', 'LO2_fmn_steps.csv', 'LO1_freq_steps.csv', 'LO2_freq_steps.csv', 'full_sweep_step_dict.csv'
















