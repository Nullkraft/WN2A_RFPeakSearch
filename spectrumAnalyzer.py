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

# Import logging_setup to configure logging once for the application.
from dataclasses import dataclass
import logging
import logging_setup    # Used for its side effects
_ = logging_setup   # silence Warning: 'logging_setup' imported but unused

import time

import numpy as np

from command_processor import CmdProcInterface
from hardware_cfg import Cfg, SPI_Device, MHz_to_fmn, fmn_to_MHz
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


@dataclass
class SweepPoint:
  rf_freq_mhz: float
  ref_code: int
  lo1_n: int
  lo2_fmn: int
  amplitude: float = 0


class SA_Control:
  lowpass_filter_width = 20       # Sets the +/- amplitude calibration smoothing half_window
  swept_freq_list = list()        # The list of frequencies that the user requested to be swept
  all_frequencies_dict = dict()   # ref_clock, LO1, LO2 from 0 to 3000 MHz in 1 kHz steps
  all_frequencies = None          # NumPy array for runtime lookups
  window_x_min = 0.0
  window_x_max = 3000.0
  window_x_range = 3000

  def __init__(self, cmd_proc: CmdProcInterface):
#    print(name(), line(), 'SA_Control.__init__ was called')
    self.selected_device = SPI_Device.LO2   # Spectrum Analyzer chip we're talking to
    self.last_ref_code = 0      # Decide if a new ref_code is to be sent
    self.last_LO1_code = 0      # Decide if a new LO1_code is to be sent
    self.last_LO2_code = 0      # Decide if a new LO2_code is to be sent
    self.sweep_points = []
    self.cmd_proc = cmd_proc

  def get_control_codes(self, freq_mhz):
    """Lookup control codes for a frequency from the numpy array."""
    idx = int(round(freq_mhz * 1000))
    return tuple(self.all_frequencies[idx])

  def build_sweep_points(self, plot_freq_list: list) -> list:
    ref1_points = []
    ref2_points = []
    for freq in plot_freq_list:
      ref_code, lo1_n, lo2_fmn = self.get_control_codes(freq)
      point = SweepPoint(freq, int(ref_code), int(lo1_n), int(lo2_fmn))
      if ref_code == self.cmd_proc.ref_clock1_enable:
        ref1_points.append(point)
      elif ref_code == self.cmd_proc.ref_clock2_enable:
        ref2_points.append(point)
      else:
        ref1_points.append(point)
    self.sweep_points = ref1_points + ref2_points
    return self.sweep_points

  def _get_active_sweep_entries(self) -> list:
    if self.sweep_points and len(self.sweep_points) == len(self.swept_freq_list):
      for step, freq in zip(self.sweep_points, self.swept_freq_list):
        if int(round(step.rf_freq_mhz * 1000)) != int(round(freq * 1000)):
          return self.swept_freq_list
      return self.sweep_points
    return self.swept_freq_list

  def _unpack_sweep_entry(self, entry):
    if isinstance(entry, SweepPoint):
      return entry.rf_freq_mhz, entry.ref_code, entry.lo1_n, entry.lo2_fmn
    ref_code, lo1_n, lo2_fmn = self.get_control_codes(entry)
    return entry, ref_code, lo1_n, lo2_fmn

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

  def sweep_315(self):
    bytes_rxd = bytearray()
    self.set_LO2(self.cmd_proc.LO2_mux_dig_lock)
    time.sleep(.001)
    for entry in self._get_active_sweep_entries():
      if not SWEEP:                       # The user pressed the ESC key so time to bail out
        break
      """ Set hardware to next frequency """
      _, ref_code, LO1_N_code, LO2_fmn_code = self._unpack_sweep_entry(entry)
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
    global SWEEP
    SWEEP = True                            # ESC key makes SWEEP=False and cancels the sweep
    sp.ser.read(sp.ser.in_waiting)          # Clear the serial port buffer
    self.sweep_315()
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
  logging.info(f'{len(peak_list) = }')
  return(peak_list)


def is_peak(amplitude_list, idx):
  plus_delta = 0.15
  if idx == 0:                            # if we are at the first index...
    return amplitude_list[idx] > (amplitude_list[idx+1] + plus_delta)
  elif idx == (len(amplitude_list)-1):    # if we are at the last index...
    return amplitude_list[idx] > (amplitude_list[idx-1] + plus_delta)
  else:
    return (amplitude_list[idx-1] + plus_delta) < amplitude_list[idx] > (amplitude_list[idx+1] + plus_delta)

if __name__ == '__main__':
  print()




