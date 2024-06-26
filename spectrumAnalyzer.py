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


# Use these functions in all your print statements to display the filename 
# and the line number of the source file. Requires: import sys
name = lambda: f'File "{__name__}.py",'
line = lambda: f"line {str(sys._getframe(1).f_lineno)},"


import sys
import time

import numpy as np

from command_processor import CmdProcInterface
from hardware_cfg import Cfg, SPI_Device, MHz_to_fmn
import serial_port as sp
#import dictionary_slice as ds


ref_clock = Cfg.ref_clock_1

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
#    print(name(), line(), f'{key} pressed by user.')
  if key == 'q':
    # Exit the key listener - for testing only
    return False

# Key listener in non-blocking mode:
listener = keyboard.Listener(on_release=on_release)
listener.start()


class SA_Control:
  lowpass_filter_width = 20       # Sets the +/- amplitude calibration smoothing half_window
  swept_freq_list = list()        # The list of frequencies that the user requested to be swept
  all_frequencies_dict = dict()   # ref_clock, LO1, LO2, and LO3 from 0 to 3000 MHz in 1 kHz steps
  window_x_min = 0.0
  window_x_max = 3000.0
  window_x_range = 3000

  def __init__(self, cmd_proc: CmdProcInterface):
#    print(name(), line(), 'SA_Control.__init__ was called')
    self.selected_device = SPI_Device.LO2   # Spectrum Analyzer chip we're talking to
    self.last_ref_code = 0      # Decide if a new ref_code is to be sent
    self.last_LO1_code = 0      # Decide if a new LO1_code is to be sent
    self.last_LO2_code = 0      # Decide if a new LO2_code is to be sent
    self.cmd_proc = cmd_proc

  
  def adc_Vref(self):
    return Cfg.Vref

  def get_x_range(self) -> float:
    if self.window_x_range is None:
      return 0, 3000, 3000
    else:
      return self.window_x_min, self.window_x_max, self.window_x_range

  def set_x_range(self, window_x_min: float = None, window_x_max: float = None):
    """The intent with this function is to have mainWindow set
    the min, max, and range values.
    """
    if window_x_min is not None:
      self.window_x_min = window_x_min  # X-axis min MHz of the plot window
    if window_x_max is not None:
      self.window_x_max = window_x_max  # X-axis min MHz of the plot window
    self.window_x_range = self.window_x_max - self.window_x_min

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
      self.last_LO1_code = 0   # Force LO1 to update each time a new ref_clock is selected
      self.cmd_proc.enable_ref_clock(ref_code)
      self.last_ref_code = ref_code
      time.sleep(0.02)  # Wait for the new reference clock to warm up

  def set_attenuator(self, dB):
    self.cmd_proc.set_attenuator(dB)
    self.selected_device = SPI_Device.ATTENUATOR   # Update currently selected device to Attenuator


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
      if self.selected_device is not SPI_Device.LO1:
#        self.cmd_proc.sel_LO1()
        self.selected_device = SPI_Device.LO1
      self.cmd_proc.set_LO1(self.cmd_proc.LO1_neg4dBm, control_code) # Set to -4 dBm & freq=control_code
      time.sleep(0.002)                       # Wait 1 ms for LO1 to lock
      self.last_LO1_code = control_code

  def set_LO2(self, control_code: int, last_control_code: int=0):
    """
    Public set_LO2 sends the hardware control_code to set LO2's frequency

    @param control_code: FMN sets the frequency of the MAX2871 (LO2)
    @type int
    @param last_control_code prevents sending FMN if it's the same as last time (defaults to 0)
    @type int (optional)
    """
    if control_code != last_control_code:
      control_code = int(control_code)
      if self.selected_device is not SPI_Device.LO2:
        self.cmd_proc.sel_LO2()
        self.selected_device = SPI_Device.LO2   # Update currently selected device to LO2
      self.cmd_proc.set_LO2(control_code)      # Set to freq=control_code
      self.last_LO2_code = control_code

  def set_LO3(self, control_code: int, last_control_code: int=0):
    """
    Public set_LO3 sends the hardware control_code to set LO3's frequency

    @param control_code: FMN sets the frequency of the MAX2871 (LO3)
    @type int
    @param last_control_code prevents sending FMN if it's the same as last time (defaults to 0)
    @type int (optional)
    """
    if control_code != last_control_code:
      control_code = int(control_code)
      if self.selected_device is not SPI_Device.LO3:
        self.cmd_proc.sel_LO3()
        self.selected_device = SPI_Device.LO3   # Update currently selected device to LO3
      self.cmd_proc.set_LO3(control_code)      # Set to freq=control_code
#      self.last_LO3_code = control_code

  def create_LO3_sweep_list(self, x_min, x_max, x_range) -> list:
    LO3_fmn_codes = []
    step_sizes = [.001, .002, .003, .005]
    """ Convert x_range MHz to an index used for setting the step size based on bandwidth """
    step_index = int(x_range)
    if step_index > 3:
      step_index = 3      # step_index must be 0 to 3
    """ Set frequency step size based on x_range bandwidth """
    step_size = step_sizes[step_index]
    freq_steps = [round(freq,3) for freq in np.arange(x_min, x_max, step_size)]
    ''' Now find a resonable LO2 freq near the middle of the LO3 sweep '''
    mid_freq = freq_steps[len(freq_steps)//2]
    ref_code, _, _ = self.all_frequencies_dict[mid_freq]    # Which reference clock is active
    if ref_code == 3327:
      ref_clock = Cfg.ref_clock_1
    else:
      ref_clock = Cfg.ref_clock_2
    ''' Convert freq steps in x into LO3 control codes '''
    for RFin in freq_steps:
      ref_code, LO1_N_code, LO2_fmn_code = self.all_frequencies_dict[RFin]    # Get hardware control codes
      if ref_code == 3327:
          ref_clock = Cfg.ref_clock_1
      else:
          ref_clock = Cfg.ref_clock_2
      LO1 = LO1_N_code * (ref_clock / Cfg.ref_divider)
      IF1 = LO1 - RFin
      LO2_real = round(fmn_to_MHz(LO2_fmn_code), 6)
      IF2 = round(LO2_real, 3) - IF1
      LO3 = IF2 - Cfg.IF3
      fmn, _ = MHz_to_fmn(LO3, ref_clock)
      LO3_fmn_codes.append(fmn)
    print(name(), line(), f'{len(LO3_fmn_codes) = }')
    return LO2_fmn_code, LO3_fmn_codes

  def sweep_45(self, x_min, x_max, x_range):
    bytes_rxd = bytearray()
    LO2_fmn_code, LO3_fmn_codes = self.create_LO3_sweep_list(x_min, x_max, x_range)
    self.set_LO2(self.cmd_proc.LO2_mux_tristate)
    """ Set hardware to next frequency """
    RFin_center_freq = round((x_min + x_max) / 2)
    ref_code, LO1_N_code, LO2_fmn_code = self.all_frequencies_dict[RFin_center_freq]    # Get hardware control codes
    self.set_reference_clock(ref_code, self.last_ref_code);
    self.set_LO1(LO1_N_code, self.last_LO1_code)
    self.set_LO2(LO2_fmn_code, self.last_LO2_code)
    time.sleep(.001)
    sp.ser.read(sp.ser.in_waiting)  # Clear out the serial buffer.
    delay_count = 0     # Prevents 100% CPU when reading the serial input
    print(name(), line(), f'{LO3_fmn_codes = }')
    for fmn in LO3_fmn_codes:
      self.set_LO3(fmn)
      """ Read the amplitude data from the serial input """
      while(True):
        delay_count += 1
        if sp.ser.in_waiting >= 2:
          bytes_rxd += sp.ser.read(sp.ser.in_waiting)
          break
        if delay_count > 25:
          time.sleep(1e-6)
          delay_count = 0
      sp.SimpleSerial.data_buffer_in += bytes_rxd    # Amplitude data collected and stored
      bytes_rxd.clear()
    self.set_LO3(self.cmd_proc.LO3_mux_tristate)

  def sweep_315(self):
    bytes_rxd = bytearray()
    self.set_LO2(self.cmd_proc.LO2_mux_dig_lock)
    time.sleep(.001)
    for freq in self.swept_freq_list:
      if not SWEEP:                       # The user pressed the ESC key so time to bail out
        break
      """ Set hardware to next frequency """
      ref_code, LO1_N_code, LO2_fmn_code = self.all_frequencies_dict[freq]    # Get hardware control codes
      self.set_reference_clock(ref_code, self.last_ref_code);
      self.set_LO1(LO1_N_code, self.last_LO1_code)
      self.set_LO2(LO2_fmn_code, self.last_LO2_code)
      delay_count = 0     # Prevents 100% CPU when reading the serial input
      """ Read the amplitude data from the serial input """
      while(True):
        delay_count += 1
        if sp.ser.in_waiting >= 2:
          bytes_rxd += sp.ser.read(sp.ser.in_waiting)
          break
        if delay_count > 25:
          time.sleep(1e-6)
          delay_count = 0
      sp.SimpleSerial.data_buffer_in += bytes_rxd    # Amplitude data collected and stored
#      print(name(), line(), bytes_rxd.hex())
      bytes_rxd.clear()
#            if freq % 5 == 0:
#                print(f'Progress {freq = }')
    self.set_LO2(self.cmd_proc.LO2_mux_tristate)


  def sweep(self, window_x_min, window_x_max):
    """ Function sweep() : Search the RF input for any or all RF signals
    """
    window_x_range = round(window_x_max - window_x_min, 9)
    global SWEEP
    SWEEP = True                            # ESC key makes SWEEP=False and cancels the sweep
    sp.ser.read(sp.ser.in_waiting)          # Clear the serial port buffer
    """ ********************************************************************* """
    if window_x_range < 4:  # Plot is less than 4 MHz wide ...
      self.sweep_45(window_x_min, window_x_max, window_x_range)
    else:
      self.sweep_315()
    """ ********************************************************************* """
    self.cmd_proc.end_sweep()   # Send handshake signal to controller
    return SWEEP

  def set_center_freq(self, freq: float):
    """
    Function
    """
    pass
    
  def toggle_arduino_led(self, on_off):
    if on_off == True:
      self.cmd_proc.LED_on()
    else:
      self.cmd_proc.LED_off()

  def get_version_message(self):
    self.cmd_proc.get_version_message()


def set_plot_window_xrange(x_min: float, x_max: float):
  global window_x_min
  global window_x_max
  if (x_min is not None):
    window_x_min = x_min   # X-axis min MHz of the plot window
  if (x_max is not None):
    window_x_max = x_max   # X-axis max MHz of the plot window

def get_plot_window_xrange() -> float:
  global window_x_min
  global window_x_max
  return (window_x_min, window_x_max)


# Find the highest signal amplitudes in a spectrum plot.
def peakSearch(amplitudeData, numPeaks):
  # Convert amplitudeData to a numpy.array so we can use argsort.
  amp = np.asarray(amplitudeData)
  # >>> amp(idx[0]) <<< returns highest value in amp and so on in descending order.
  idx = amp.argsort()[::-1]
  idx = idx.tolist()
#  idx = amp.argsort()[::-1][:numPeaks*2]
  peak_list = []
  for i in idx:
    if is_peak(amp, i):
      peak_list.append(i)
  print(name(), line(), f'{len(peak_list) = }')
  return(peak_list)


def is_peak(amplitude_list, idx):
  plus_delta = 0.15
  if idx == 0:                            # if we are at the first index...
    return amplitude_list[idx] > (amplitude_list[idx+1] + plus_delta)
  elif idx == (len(amplitude_list)-1):    # if we are at the last index...
    return amplitude_list[idx] > (amplitude_list[idx-1] + plus_delta)
  else:
    return (amplitude_list[idx-1] + plus_delta) < amplitude_list[idx] > (amplitude_list[idx+1] + plus_delta)


def fmn_to_MHz(fmn_word, Fpfd=66.0, show_fmn: bool=False):
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
  if show_fmn:
    print(name(), line(), '\t', f'M:F:N = {M,F,N}')
  freq_MHz = Fpfd * (N + F/M)
  return freq_MHz


def MHz_to_N(RFout_MHz, ref_clock, R: int=1) -> int:
  """ Returns the integer portion of N which is used to program
      the integer step register of the ADF4356 chip.
  """
  if ref_clock == None:
    print(name(), line(), 'WARNING: ref_clock can not be None when calling MHz_to_N()')
  N = int(RFout_MHz * (2/ref_clock))
  return (N)



if __name__ == '__main__':
  print()
















