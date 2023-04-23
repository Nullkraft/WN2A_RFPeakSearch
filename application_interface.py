# -*- coding: utf-8 -*-

# Utility functions used for displaying the name and the line number
# of the source file. Requires: import sys
name = lambda: f'File "{__name__}.py",'
line = lambda: f"line {str(sys._getframe(1).f_lineno)},"

import sys
from time import sleep, perf_counter
import pickle
import numpy as np
import threading
from pathlib import Path

import spectrumAnalyzer as sa
from spectrumAnalyzer import SA_Control as sa_ctl
import serial_port as sp

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
    start: int = sa_ctl().window_x_min
    stop: int = sa_ctl().window_x_max
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

