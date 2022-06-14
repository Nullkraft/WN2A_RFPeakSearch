import time

def freq_to_index(freq_MHz: float=4.0):
    return int(freq_MHz * 1000)

def index_to_freq(index: int=4000):
    return float(index / 1000)


if __name__ == '__main__':
    print()
    
    freq_start = .001
    freq_stop = 3000.001
    freq_step = 3.746       # 3.746 makes 801 frequency sweep steps
    
    idx_start = freq_to_index(freq_start)
    idx_stop = freq_to_index(freq_stop)
    idx_step = freq_to_index(freq_step)

    start = time.perf_counter()
    with open('RFin_1kHz_freq_steps.csv') as RFin_file:
        RFin_list = [float(x) for x in RFin_file]               # For sweeps and plots. Convert x from string to float
        
    with open('LO1_ref1_N_steps.csv') as n_file:
        LO1_n_list = [int(N) for N in n_file]                   # For sweeping. Convert N from a string to int
    
    with open('LO2_ref1_fmn_steps.csv') as LO2_fmn_file:
        LO2_fmn_list = [int(fmn) for fmn in LO2_fmn_file]       # For sweeping. Convert fmn from string to int

    with open('LO1_ref1_freq_steps.csv') as LO1_freq_file:
        LO1_freq_list = [float(f) for f in LO1_freq_file]       # For plotting. Convert f from a string to float

    with open('LO2_ref1_freq_steps.csv') as LO2_freq_file:
        LO2_freq_list = [float(freq) for freq in LO2_freq_file] # For plotting. Convert freq from string to float

    # Create the main dictionary, freq_step_dict. Using a dictionary makes for fast
    # lookups and by using floats for the keys it will allow direct manipulation of
    # the dictionary when handed a frequency from the user GUI.
    freq_sweep_dict = {freq:(LO1, LO2) for freq, LO1, LO2 in zip(RFin_list, LO1_n_list, LO2_fmn_list)}
    
    freq_dict = {freq:(LO1, LO2) for freq, LO1, LO2 in zip(RFin_list, LO1_freq_list, LO2_freq_list)}
    stop = time.perf_counter()
    
    # Use slicing to set our frequency sweep range and step size
    step_dict = dict(list(freq_sweep_dict.items())[idx_start:idx_stop:idx_step])
    for freq in step_dict:
#        print(f'Step: {freq}, data: {step_dict[freq]}')
        pass
    
    print(f'Step dict size: {len(step_dict)}')
    print(f'Elapsed time: {round(stop-start, 6)}')
    print("********** DONE! **********")

