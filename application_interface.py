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
#        self.numFrequencySteps.setValue(num_steps_actual)   # Display the num_steps to the user
#        self.intStepKHz.setValue(step_size_khz)
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
