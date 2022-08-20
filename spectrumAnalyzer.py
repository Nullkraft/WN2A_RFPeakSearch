# -*- coding: utf-8 -*-
#
# This file is part of WN2A_RFPeakSearch.
# 
# This file is part of the WN2A_RFPeakSearch distribution (https://github.com/Nullkraft/WN2A_RFPeakSearch).
# Copyright (c) 2021 Mark Stanley.
# 
# WN2A_RFPeakSearch is free software: you can redistribute it and/or modify  
# it under the terms of the GNU General Public License as published by  
# the Free Software Foundation, version 3.
#
# WN2A_RFPeakSearch is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU 
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License 
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#


""" Spectrum Analyzer Notes:

    LO1 = int({IF1 + RFin} - [{IF1 + RFin} / Fpfd])
    LO2 = LO1 - RFin + IF2
    RFin = LO1 + IF2 - LO2
    
"""
import sys
import time
from math import ceil

import numpy as np

import command_processor as cmd_proc
from hardware_cfg import cfg


def line() -> str:
    """
    Function Utility to simplify print debugging.

    @return The line number of the source code file.
    @rtype str

    """
    return f'line {str(sys._getframe(1).f_lineno)},'


name = f'File \"{__name__}.py\",'


ref_clock = cfg.ref_clock_1
sweep_start = 4.0
sweep_stop = 3000.0
sweep_step_size = 250
sweep_num_steps = 1601

last_sweep_start = 4.0
last_sweep_stop = 3000.0
last_sweep_step = 250
full_sweep_dict = {}    # Dictionary of ref_clock, LO1, LO2, and LO3 from 0 to 3000 MHz in 1 kHz steps

swept_frequencies_list = []     # The collected list of swept frequencies used for plotting amplitude vs. frequency

def load_control_dict(dict_name, file_name):
    """
    NOTE: full_sweep_dict has a value that is a tuple of LO1_N and LO2_FMN.
          LO3_FMN will be added later. The key, RFin, is a string.

    EXAMPLE USAGE:  ref, N, FMN = full_sweep_dict[RFin]
                    print(name, line(), f'ref = {ref}, N ={N} and FMN ={FMN}')
    """
#    full_sweep_dict = dict()
    with open(file_name, 'r') as f:
        _ = f.readline()    # Throw away the file header
        for freq in f:
            RFin, ref, LO1_N, LO2_FMN = freq.split()
            RFin = float(RFin)
            dict_name[RFin] = (int(ref), int(LO1_N), int(LO2_FMN))


class sa_control():
    
    def __init__(self):
        self.last_ref_clock = 0  # Decide if a new ref_clock code is to be sent
        self.last_LO1_code = 0   # Decide if a new LO1_code is to be sent

    
    def set_reference(self, ref_clock: float):
        if ref_clock != self.last_ref_clock:
            cmd_proc.enable_ref_clock(ref_clock)
            time.sleep(0.0025)  # Give the slow Arduino time to update the ref_clock selection
            self.last_ref_clock = ref_clock
            print(name, line(), f'New ref_clock set to {hex(ref_clock)}')
        
    
    def set_LO1(self, control_code: int, last_control_code: int=0) -> int:
        """
        Public set_LO1 sends the hardware control_code to set LO1's frequency

        @param control_code: N (reg[0] from the spec-sheet) sets the frequency of the ADF4356 (LO1)
        @type int
        @param last_control_code prevents sending N if it's the same as last time (defaults to 0)
        @type int (optional)
        @return The new_code in N so it can be saved to an external last_code
        @rtype int

        """
        if control_code != last_control_code:
            cmd_proc.set_LO1(cmd_proc.LO1_neg4dBm, control_code) # Set to -4 dBm & freq=control_code
            time.sleep(0.0025)  # Give the slow Arduino time to update the local oscillator, LO1
            return control_code
        
    
    def set_LO2(self, control_code: int):
        pass
        
    
    def set_LO3(self, control_code: int):
        pass


    # WHAT IF???
    def set_frequency(self, RFin_kHz: int):
        ref, LO1_code, LO2_code = full_sweep_dict[RFin_kHz]
        cmd_proc.set_max2871_freq(LO2_code)     # Most frequently called so don't bother to check last value
        time.sleep(0.0025)      # Give the slow Arduino time to update the local oscillator, LO2
        self.set_reference(ref);
        self.last_LO1_code = self.set_LO1(LO1_code, self.last_LO1_code)


def sweep(start_freq, stop_freq, step_freq, ref_clock):
    """
    Function sweep() : Search the input for any or all RF signals
    sa.sweep(sa.sweep_start, sa.sweep_stop, sa.sweep_step_size, sa.ref_clock)
    """
    
    sweep_start = round(start_freq * 1000)  # kHz - Needs to be integer for slicing the RFin_array (list)
    sweep_stop = round(stop_freq * 1000)  # kHz - Needs to be integer for slicing the RFin_array (list)
    sweep_step = ceil((sweep_stop - sweep_start) / sweep_num_steps)         # Slightly larger step forces python to go beyond sweep_stop
    sweep_stop = ceil(sweep_stop / sweep_step_size) * sweep_step_size   # ceil() ensures ending after sweep_stop

    # Perform the sweep
    cmd_proc.sel_315MHz_adc()                                   # Select for LO2 output data
    cmd_proc.set_LO2(cmd_proc.LO2_neg4dBm)                      # Bring the LO2 online
    cmd_proc.disable_LO3_RFout()
    
    plot_freq_list = [sa_control.set_frequency(freq) for freq in cfg.RFin_array[sweep_start : sweep_stop : sweep_step]]
    cmd_proc.sweep_end()   # Handshake signal to controller
    print(f'Sweep complete for {len(plot_freq_list)} frequencies')


# Find the highest signal amplitudes in a spectrum plot.
def peakSearch(amplitudeData, numPeaks):
    # Convert amplitudeData to a numpy.array so we can use argsort.
    amp = np.asarray(amplitudeData)
    # >>> amp(idx[0]) <<< returns highest value in amp and so on in descending order.
    idx = amp.argsort()[::-1]
    idx = idx.tolist()
#    idx = amp.argsort()[::-1][:numPeaks*2]
    peak_list = []
    for i in idx:
        if is_peak(amp, i):
            peak_list.append(i)
    return(peak_list)


def is_peak(amplitude_list, idx):
    plus_delta = 0.15
    if idx == 0:                            # if we are at the first index...
        return amplitude_list[idx] > (amplitude_list[idx+1] + plus_delta)
    elif idx == (len(amplitude_list)-1):    # if we are at the last index...
        return amplitude_list[idx] > (amplitude_list[idx-1] + plus_delta)
    else:
        return (amplitude_list[idx-1] + plus_delta) < amplitude_list[idx] > (amplitude_list[idx+1] + plus_delta)


def fmn_to_MHz(fmn_word, Fpfd=33.0):
    """
    Function: fmn_to_freq is a utility for verifying that your fmn value
              correctly matches the frequency that you think it does.

    @param fmn_word is a 32 bit word that contains the F, M, and N values
    @type <class 'int'>
    @param Fpfd is half the frequency of the reference clock (defaults to ref_clock_LO)
    @return Frequency in MHz
    @rtype float
    """
    F = fmn_word >> 20
    M = (fmn_word & 0xFFFFF) >> 8
    if M == 0:
        print(fmn_word)
    N = fmn_word & 0xFF
    print(name, line(), '\t', f'F = {F} : M = {M} : N = {N}')
    return Fpfd * (N + F/M)


def MHz_to_N(RFout_MHz, ref_clock, R: int=1) -> int:
    """ Returns the integer portion of N which is used to program
        the integer step register of the ADF4356 chip.
    """
    if ref_clock == None:
        print(name, line(), 'WARNING: ref_clock can not be None when calling MHz_to_N()')
    N = int(RFout_MHz * (2/ref_clock))
    return (N)


def toggle_arduino_led(on_off):
    if on_off == True:
        cmd_proc.LED_on()
    else:
        cmd_proc.LED_off()


def get_version_message():
    print(name, line(), f'Arduino Message = {cmd_proc.get_version_message()}')


def set_attenuator(dB):
    cmd_proc.set_attenuator(dB)


def set_reference_clock(clock_id):
    if clock_id == 0:
        ref_clock = None
        cmd_proc.disable_all_ref_clocks()       # Stop both ref clocks before enabling one of them
    if clock_id == 1:
        ref_clock = cfg.ref_clock_1
        cmd_proc.enable_ref_clock(cmd_proc.ref_clock1_enable)
    if clock_id == 2:
        ref_clock = cfg.ref_clock_2
        cmd_proc.enable_ref_clock(cmd_proc.ref_clock2_enable)
    return ref_clock


if __name__ == '__main__':
    print()

    start = time.perf_counter()
    d = dict()
    load_control_dict(d, 'full_control_ref1.csv')
    stop = time.perf_counter()
    print(f'Time to load full_control_ref1.csv = {round(stop-start, 6)} seconds')

    print("Done")
















