# -*- coding: utf-8 -*-

# Use these functions in all your print statements to display the filename 
# and the line number of the source file. Requires: import sys
name = lambda: f'File "{__name__}.py",'
line = lambda: f"line {str(sys._getframe(1).f_lineno)},"

import sys
import pickle
import numpy as np
from pathlib import Path

import spectrumAnalyzer as sa
from command_processor import CommandProcessor
from spectrumAnalyzer import SA_Control
import serial_port as sp
from time import perf_counter

cmd_proc = CommandProcessor()
sa_ctl = SA_Control(cmd_proc)

def freq_steps(startMHz, stopMHz, step_size, num_steps):
    '''
    Public method I want this function to get the frequencies and indexes
    that will be used to slice the all_controls dictionary. It should be
    based upon the width, or x range, of the plot window.
    - First is to grab the start/stop/step from the user controls
    - I can get the start and stop freqs from the plot window x range.
    - Then I can access the indexes by feeding the freqs into the RFin_list
      where the RFin_list is populated at prgram startup.
    - Finally, populate the sweep control dictionary for this x range in
      the Spectrum Analyzer module.
    '''
    # Frequencies:  Grab start/stop freqs and step size from the user controls
    start_freq_mhz = round(startMHz, 3)
    stop_freq_mhz = round(stopMHz, 3)
    band_width = (stop_freq_mhz - start_freq_mhz) * 1000    # Convert MHz to kHz
    ''' 401 prevents calibration from working '''
    step_size_khz = int(band_width / num_steps)
    num_steps_actual = int(band_width / step_size_khz)
#    self.numFrequencySteps.setValue(num_steps_actual)   # Display the num_steps to the user
#    self.intStepKHz.setValue(step_size_khz)
    # Indexes:  At program start RFin_list doesn't exist so use the following
    # method to get the indexes.
    control_start_idx = int(start_freq_mhz * 1000)
    control_stop_idx = int(stop_freq_mhz * 1000)
    # Update the start/stop/step values in the Spectrum Analyzer module
    sa_ctl.window_x_min = control_start_idx
    sa_ctl.window_x_max = control_stop_idx
    sa_ctl.window_x_range = sa_ctl.window_x_max - sa_ctl.window_x_min
    # Get the start and stop indexes for the sweep frequencies list
    start: int = sa_ctl.window_x_min
    stop: int = sa_ctl.window_x_max
    # Fill the list with new sweep frequecies
    sa_ctl.swept_freq_list.clear()
    return start, stop, step_size_khz, num_steps_actual   # Return to display the num_steps to the user

def get_visible_plot_range(x_plot_data: list, y_plot_data: list, window_x_min: float, window_x_max: float):
    ''' Get the list of visible plot points after zooming the plot window '''
    # Get x_plot_min/max values nearest to the values from the plotWidget
    visible_x_min = min(x_plot_data, key=lambda x_data: abs(x_data-window_x_min)) # x is iterated from x_plot_data
    visible_x_max = min(x_plot_data, key=lambda x_data: abs(x_data-window_x_max))
    x_data_min = x_plot_data[0]
    x_data_max = x_plot_data[-1]
    if visible_x_min < x_data_min:
        visible_x_min = x_data_min
    if visible_x_max > x_data_max:
        visible_x_max = x_data_max
    # Find the indexes for the min/max values...
    idx_min = x_plot_data.index(visible_x_min)
    idx_max = x_plot_data.index(visible_x_max)
    # and return the portion of the list that is visible on the plot
    x_axis = x_plot_data[idx_min:idx_max]
    y_axis = y_plot_data[idx_min:idx_max]
    return x_axis, y_axis

def _amplitude_bytes_to_volts(amplBytes) -> list:
    volts_list = []
    # Convert two 8-bit serial bytes into one 16 bit amplitude
    hi_byte_list = amplBytes[::2]
    lo_byte_list = amplBytes[1::2]
    for idx, (hi_byte, lo_byte) in enumerate(zip(hi_byte_list, lo_byte_list)):
        if hi_byte > 3:
            hi_byte = (hi_byte & 15)        # Store the amplitude value despite it not locking
            print(name(), line(), f'WARNING:: PLL failed to lock at {sa_ctl.swept_freq_list[idx]} Mhz')
        ampl = (hi_byte << 8) | lo_byte     # Combine MSByte/LSByte into an amplitude word
        voltage = ampl * sa.SA_Control().adc_Vref()/(2**10-1)       # Convert 10 bit ADC counts to Voltage
        volts_list.append(voltage)
    return volts_list

def _volts_to_dBm(voltage: float) -> float:
    '''
    Convert ADC results from Volts to dBm for the y_axis

    @param voltage Found based on the number of ADC bits and reference voltage
    @type float
    @return Output power in the range of -80 to +20 dBm
    @rtype float
    '''
    x = voltage
    dBm = (((((((-9.460927*x + 110.57352)*x - 538.8610489)*x + 1423.9059205)*x - 2219.08322)*x + 2073.3123)*x - 1122.5121)*x + 355.7665)*x - 112.663
    return dBm

def make_control_dictionary(RFin_list):
    '''
    The full control dictionary is used for programming
    the 3 LO chips on the Spectrum Analyzer board. The dictionary is created
    by comparing the amplitudes that were found when running a full sweep
    with ref1 selected and then ref2. Whichever amplitude is lower then the
    control codes for that frequency are copied to the control_dict.
    '''
    r1_hi_amplitudes = []
    r1_lo_amplitudes = []
    r2_hi_amplitudes = []
    r2_lo_amplitudes = []
    sa_ctl.all_frequencies_dict.clear()
    ''' If one of these files is missing there is no need to check the others '''
    ampl_file_1 = Path('amplitude_ref1_HI.pickle')
    ampl_file_2 = Path('amplitude_ref2_HI.pickle')
    if ampl_file_1.exists() and ampl_file_2.exists():
        if r1_hi_amplitudes == []:    # If this list is empty then fill all 4 of the following lists
            ''' The contents of the amplitude files need to be compared to see which one
            has the lowest level of noise. Each entry depends on its position in the file,
            e.g. Line 132427 in the file came from the frequency 132.427 MHz RFin '''
            with open('amplitude_ref1_HI.pickle', 'rb') as f:   # 3 million amplitudes collected with ref1
                r1_hi_amplitudes = pickle.load(f)
            with open('amplitude_ref1_LO.pickle', 'rb') as f:   # 3 million amplitudes collected with ref1
                r1_lo_amplitudes = pickle.load(f)
            with open('amplitude_ref2_HI.pickle', 'rb') as f:   # 3 million amplitudes collected with ref2
                r2_hi_amplitudes = pickle.load(f)
            with open('amplitude_ref2_LO.pickle', 'rb') as f:   # 3 million amplitudes collected with ref2
                r2_lo_amplitudes = pickle.load(f)
            ''' These are the controls associated with the amplitude files. When the lowest
            noise level has been found then the control associated with that amplitude file
            is assigned to a single full_control dictionary, e.g. We found Line 132427 was
            lowest in amplitude_ref1_LO so the control from control_ref1_LO is copied into
            the full_control dictionary. '''
            with open('control_ref1_HI.pickle', 'rb') as f:
                control_ref1_hi_dict = pickle.load(f)
            with open('control_ref1_LO.pickle', 'rb') as f:
                control_ref1_lo_dict = pickle.load(f)
            with open('control_ref2_HI.pickle', 'rb') as f:
                control_ref2_hi_dict = pickle.load(f)
            with open('control_ref2_LO.pickle', 'rb') as f:
                control_ref2_lo_dict = pickle.load(f)

        def lp_filt(active_list, half_window: int, index: int = 0) -> float:
            ''' A Centered Moving Average is is used to smooth out the amplitude data.
            Otherwise random noise levels cause random control selection. This shows
            up as a comb effect when performing actual sweeps.
            '''
            start = index - half_window
            stop = index + half_window
            if start < 0:                   # too close to the start of the list
                start = 0
            if stop > len(active_list):       # too close to the end of the list
                stop = len(active_list)
            avg_value = round(np.average(active_list[start:stop]),3)
            return avg_value

        ''' We need smoothed amplitude data for performing the amplitude comparison step
            The lp_filt() def uses self.r1_lo_amplitudes, etc., directly. It's faster
            than passing the entire list.
        '''
        window = sa_ctl.lowpass_filter_width
        a1_filtered = [lp_filt(r1_hi_amplitudes, window, idx) for idx, _ in enumerate(r1_hi_amplitudes)]
        a2_filtered = [lp_filt(r1_lo_amplitudes, window, idx) for idx, _ in enumerate(r1_lo_amplitudes)]
        a3_filtered = [lp_filt(r2_hi_amplitudes, window, idx) for idx, _ in enumerate(r2_hi_amplitudes)]
        a4_filtered = [lp_filt(r2_lo_amplitudes, window, idx) for idx, _ in enumerate(r2_lo_amplitudes)]

        for idx, freq in enumerate(RFin_list):
            ''' For each RFin select the control code that generated the best (lowest) amplitude. '''
            a1 = a1_filtered[idx]
            a2 = a2_filtered[idx]
            a3 = a3_filtered[idx]
            a4 = a4_filtered[idx]
            if a1 <= a2 and a1 <= a3 and a1 <= a4:
                sa_ctl.all_frequencies_dict[freq] = control_ref1_hi_dict[freq]
            elif a2 < a1 and a2 <= a3 and a2 <= a4:
                sa_ctl.all_frequencies_dict[freq] = control_ref1_lo_dict[freq]
            elif a3 < a1 and a3 < a2 and a3 <= a4:
                sa_ctl.all_frequencies_dict[freq] = control_ref2_hi_dict[freq]
            elif a4 < a1 and a4 < a2 and a4 < a3:
                sa_ctl.all_frequencies_dict[freq] = control_ref2_lo_dict[freq]
            ''' Special cases requiring manual input '''
            if 208 < freq < 210.35:
                sa_ctl.all_frequencies_dict[freq] = control_ref2_lo_dict[freq]
            if 359.9 < freq < 360.1:
#                    sa_ctl.all_frequencies_dict[freq] = control_ref2_lo_dict[freq]
                sa_ctl.all_frequencies_dict[freq] = control_ref1_hi_dict[freq]
            if 2482 < freq < 2484:
                sa_ctl.all_frequencies_dict[freq] = control_ref1_hi_dict[freq]

    with open('control.pickle', 'wb') as f:
        pickle.dump(sa_ctl.all_frequencies_dict, f, protocol=pickle.HIGHEST_PROTOCOL)

    with open('control.csv', 'w') as fcsv:
        for f in sa_ctl.all_frequencies_dict:
            r, LO1_N, LO2_FMN = sa_ctl.all_frequencies_dict[f]
            freq = str(f)
            ref_clock = str(r)
            LO1 = str(LO1_N)
            LO2 = str(LO2_FMN)
            fcsv.write(f'{freq}:({ref_clock},{LO1},{LO2})\n')

def load_controls(control_fname: str=None):
    if control_fname is None:
        print(name(), line(), 'You must enter a control file name')
    else:
        sa_ctl.all_frequencies_dict.clear()     # get ready for a new set of control codes
        control_file = Path(control_fname)      # Filename containting new control codes
    if control_file.exists():
        ctrl_start = perf_counter()
        with open(control_file, 'rb', buffering=65536) as f:
            sa_ctl.all_frequencies_dict = pickle.load(f)
            delta = round(perf_counter()-ctrl_start, 2)
            print(name(), line(), f'Control file "{control_file}" loaded in {delta} seconds')
    else:
        print(name(), line(), f'Missing control file "{control_file}"')

def sweep():
    start = perf_counter()
    sp.SimpleSerial.data_buffer_in.clear()     # Clear the serial data buffer before sweeping
    window_x_min, window_x_max, _ = sa_ctl().get_x_range()
    sweep_complete = sa_ctl().sweep(window_x_min, window_x_max)
    print(name(), line(), f'Sweep completed in {round(perf_counter()-start, 6)} seconds')
    if not sweep_complete:
        print(name(), line(), 'Sweep stopped by user')
    return sweep_complete

