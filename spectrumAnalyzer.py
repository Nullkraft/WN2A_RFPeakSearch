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



# Utility functions used for displaying the name and the line number
# of the source file. Requires: import sys
name = lambda: f'File \"{__name__}.py\",'
line = lambda: f'line {str(sys._getframe(1).f_lineno)},'


import sys
import time

import numpy as np

import command_processor as cmd_proc
from hardware_cfg import cfg, spi_device
import serial_port as sp


ref_clock = cfg.ref_clock_1

last_sweep_start = 0.0
last_sweep_stop = 9999.0
last_sweep_step = 0.0

#amplitude_list = []     # The collected list of swept frequencies used for plotting amplitude vs. frequency

SWEEP: bool             # Flag to test for ESC key during a sweep

from pynput import keyboard

def on_release(key):
    global SWEEP
    if key == keyboard.Key.esc:
        SWEEP = False
#        print(name(), line(), f'{key} pressed by user.')
    if key == 'q':
        # Exit the key listener - for testing only
        return False

# Key listener in non-blocking mode:
listener = keyboard.Listener(on_release=on_release)
listener.start()

class DictionarySlicer(dict):
    """ Add slicing to a dictionary. """

    def __init__(self, d_items: {}, k_list: []=None) -> None:
        """
        Constructor Store d_items and k_list. If k_list is None then _keys
                    will be created from d_items.keys(). The result of
                    indexing or slicing _keys is used to create a new
                    list called self._keys that is a subset of k_list that
                    will return a subset of the values in d_items.

        @param d_items The dictionary that you want to slice.
        @type {}
        @param _keys The list of keys for d_items (defaults to None)
        @type [] (optional)
        @return None
        @rtype None

        """
        self.dict_slice = {}
        self._dict = d_items    # One data item = {RFin_freq: (RFin, LO1_N, LO2_FMN)}
        if k_list is None:
            self._keys = list(self._dict)   # Create index list from dictionary keys
        else:
            self._keys = k_list             # Copy index list from the provided k_list

    def __len__(self) -> {}:
        """
        Special method Reports the length of the sliced dictionary result.

        @return Length of sliced dictionary.
        @rtype dict
        """
        return len(self.dict_slice)

    def __getitem__(self, key: None) -> {}:
        """
        Special method Get a slice or single item from a dictionary.

        @param key A slice = [start:stop:step], index = [int], or None.
        @type slice, int, or NoneType
        @return A subset of items sliced from the full dictionary or a single item.
        @rtype dict

        """
        if isinstance(key, type(None)):             # When slice == [::] or [:]
            self.dict_slice = self._dict
        if isinstance(key, int):                    # Getting a single item
            try:
                self.dict_slice = {f: self._dict[f] for f in self._keys[key:key+1]}
            except TypeError:
                if not isinstance(self._dict, dict):
                    raise TypeError(f' d_items must be a type dict. d_items == {type(self._dict)}')
                if not isinstance(self._keys, list):
                    raise TypeError(f' k_list must be a type list. k_list == {type(self._keys)}')
        if isinstance(key, slice):                  # Getting a range of items
            try:
                self.dict_slice = {f: self._dict[f] for f in self._keys[key.start:key.stop:key.step]}
            except TypeError:
                if not isinstance(self._dict, dict):
                    raise TypeError(f' d_items must be a type dict. d_items == {type(self._dict)}')
                if not isinstance(self._keys, list):
                    raise TypeError(f' k_list must be a type list. k_list == {type(self._keys)}')
        return self.dict_slice


class sa_control():
    filter_width = 20               # Sets the +/- amplitude calibration smoothing half_window
    swept_freq_list = list()        # The list of frequencies that the user requested to be swept
    all_frequencies_dict = dict()   # ref_clock, LO1, LO2, and LO3 from 0 to 3000 MHz in 1 kHz steps

    def __init__(self):
        self.selected_device = spi_device.LO2   # Spectrum Analyzer chip we're talking to
        self.last_ref_code = 0   # Decide if a new ref_code is to be sent
        self.last_LO1_code = 0   # Decide if a new LO1_code is to be sent

    
    def adc_Vref(self):
        return cfg.Vref


    def set_reference_clock(self, ref_code: int, last_ref_code: int=0):
        """
        Public set_reference send the hardware ref_code to select a reference oscillator
        
        @param ref_code The Command Code found in the Instruction List document
        @type int
        @param last_ref_code prevents sending ref_code if it's the same as last time (defaults to 0)
        @type int (optional)
        @return The new_code in ref_code so it can be saved to an external last_code
        """
        if ref_code != last_ref_code:
            self.last_LO1_code = 0   # Force LO1 to update every time we select a new reference clock
            cmd_proc.enable_ref_clock(ref_code)
            self.last_ref_code = ref_code
            time.sleep(0.02)  # Wait for the new reference clock to warm up
        

    def set_attenuator(self, dB):
        cmd_proc.set_attenuator(dB)
        self.selected_device = spi_device.ATTENUATOR   # Update currently selected device to Attenuator

    
    def set_LO1(self, control_code: int, last_control_code: int=0):
        """
        Public set_LO1 sends the hardware control_code to set LO1's frequency

        @param control_code: N (reg[0] from the spec-sheet) sets the frequency of the ADF4356 (LO1)
        @type int
        @param last_control_code prevents sending N if it's the same as last time (defaults to 0)
        @type int (optional)
        @return The new_code in N so it can be saved to an external last_code
        """
        if control_code != last_control_code:
            cmd_proc.set_LO1(cmd_proc.LO1_neg4dBm, control_code) # Set to -4 dBm & freq=control_code
            time.sleep(0.002)                       # Wait 1 ms for LO1 to lock
            self.last_LO1_code = control_code
            self.selected_device = spi_device.LO1   # Update currently selected device to LO1

    def set_LO2(self, control_code: int):
        """
        Public set_LO2 sends the hardware control_code to set LO2's frequency

        @param control_code: FMN sets the frequency of the MAX2871 (LO2)
        @type int
        @param last_control_code prevents sending FMN if it's the same as last time (defaults to 0)
        @type int (optional)
        """
        if self.selected_device is not spi_device.LO2:
            cmd_proc.sel_LO2()
            self.selected_device = spi_device.LO2   # Update currently selected device to LO2
        cmd_proc.set_LO2(control_code)      # Set to freq=control_code

    
    def set_LO3(self, control_code: int, last_control_code: int=0):
        """
        Public set_LO3 sends the hardware control_code to set LO3's frequency

        @param control_code: FMN sets the frequency of the MAX2871 (LO3)
        @type int
        @param last_control_code prevents sending FMN if it's the same as last time (defaults to 0)
        @type int (optional)
        """
        if self.selected_device is not spi_device.LO3:
            cmd_proc.sel_LO3()
            self.selected_device = spi_device.LO3   # Update currently selected device to LO3
        cmd_proc.set_LO3(control_code)      # Set to freq=control_code


    def sweep(self):
        """
            Function sweep() : Search the RF input for any or all RF signals
        """
        global SWEEP
        last_freq = 0
        SWEEP = True                            # ESC key makes SWEEP=False and cancels the sweep
        interbyte_timeout = 0.1                 # If another byte takes too long to arrive...
        sp.ser.read(sp.ser.in_waiting)          # Clear the serial port buffer
        self.set_LO2(cmd_proc.LO2_mux_dig_lock)
        time.sleep(.001)
        bytes_rxd = bytearray()
        for freq in self.swept_freq_list:
            if not SWEEP:                       # The user pressed the ESC key so time to bail out
                break
            ''' Progress report '''
            if (freq % 10) == 0:
                print(name(), line(), f'Freq step {freq}')  # For monitor a sweep or calibration status
            ref_code, LO1_N_code, LO2_fmn_code = self.all_frequencies_dict[freq]    # Get hardware control codes
#            print(name(), line(), f'{str(self.all_frequencies_dict[freq]).strip()}')
            self.set_reference_clock(ref_code, self.last_ref_code);
            self.set_LO1(LO1_N_code, self.last_LO1_code)
            self.set_LO2(LO2_fmn_code)
            timeout_start = time.perf_counter() # Start the interbyte_timeout (don't put this inside while-loop)
            while len(bytes_rxd)<2:
                bytes_rxd += sp.ser.read(sp.ser.in_waiting)
                sp.simple_serial.data_buffer_in += bytes_rxd    # Amplitude data collected and stored
#                time.sleep(1e-9)  # Prevent CPU from going to 100% - It slows the loop by 30% when enabled
                if (time.perf_counter()-timeout_start) > interbyte_timeout:
                    if freq == self.swept_freq_list[0]:     # Decrease the timeout after setting the first frequency.
                        interbyte_timeout = 0.005
                    if freq != last_freq:
                        print(name(), line(), f'"*** Sweep failed ***" {freq = } : {list(bytes_rxd) = } : {bytes_rxd = }')
                        sp.simple_serial.data_buffer_in += b'\xFF\xFF'  # TESTING ONLY
                        last_freq = freq
                    timeout_start = time.perf_counter()     # Restart the interbyte timer
#            if freq == 630.0:
#                print(name(), line(), f'{freq = }, {bytes_rxd = }')
            bytes_rxd.clear()
        self.set_LO2(cmd_proc.LO2_mux_tristate)
        cmd_proc.end_sweep()   # Send handshake signal to controller
        return SWEEP

    def set_center_freq(self, freq: float):
        """
        Function
        """
        pass


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


def fmn_to_MHz(fmn_word, Fpfd=66.0):
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
        M = 1
    N = fmn_word & 0xFF
#    print(name(), line(), '\t', f'F = {F} : M = {M} : N = {N}')
    return Fpfd * (N + F/M)


def MHz_to_N(RFout_MHz, ref_clock, R: int=1) -> int:
    """ Returns the integer portion of N which is used to program
        the integer step register of the ADF4356 chip.
    """
    if ref_clock == None:
        print(name(), line(), 'WARNING: ref_clock can not be None when calling MHz_to_N()')
    N = int(RFout_MHz * (2/ref_clock))
    return (N)


def toggle_arduino_led(on_off):
    if on_off == True:
        cmd_proc.LED_on()
    else:
        cmd_proc.LED_off()


def get_version_message():
    print(name(), line(), f'Packets rcvd = {cmd_proc.get_version_message()}')




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
















