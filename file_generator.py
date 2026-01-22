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
name = lambda: f"File '{__name__}.py',"
line = lambda: f"line {str(sys._getframe(1).f_lineno)},"


import sys
import os
import numpy as np
from time import perf_counter
from concurrent.futures import ProcessPoolExecutor

import hardware_cfg as hw
import command_processor as cmd


NUM_FREQUENCIES = 3_000_001


def _compute_fmn_list(args):
    """
    Worker function for parallel FMN computation.
    Must be defined at module level for multiprocessing to work.
    """
    freq_list, ref_clock = args
    return [hw.MHz_to_fmn(freq, ref_clock)[0] for freq in freq_list]


class DataGenerator():
  """ These files will be used by calibrate_sa.py for creating the
  control dictionaries needed by the calibration scripts.
  """
  def __init__(self):
    self.ref1_control_code = cmd.CmdProcInterface().ref_clock1_enable
    self.ref2_control_code = cmd.CmdProcInterface().ref_clock2_enable
    # RFin_list contains every frequency from 0 to 3000.0 MHz in 1 kHz steps
    self.RFin_list = np.arange(NUM_FREQUENCIES) / 1000.0
    # Detect available CPUs
    self.num_cpus = os.cpu_count() or 1
    print(name(), line(), f'Detected {self.num_cpus} CPU(s)')


  def _LO1_frequency(self, RFin: float, Fref: float, R: int=1) -> float:
    """
    Protected method calculates the frequency for LO1 from RFin, Fpfd, and R
    where the Phase Frequency Detector frequency is Fpfd=Fref/R

    @param RFin is the Spectrum Anaylzer input frequency
    @type float
    @param Fref is the frequency of the selected reference clock
    @type float
    @param R is from the manufacturer's specsheet (defaults to 1)
    @type int (optional)
    @return The LO1 frequency that steps by the Fpfd value
    @rtype float
    """
    Fpfd = Fref/R     # Fpfd1 = reference clock_1 and Fpfd2 = reference clock_2
    if RFin <= 2000:
      IF1 = 3800
    else:
      IF1 = 3700
    LO1_freq = Fpfd * round((RFin+IF1)/Fpfd, 0)
    return LO1_freq


  def _LO2_frequency(self, RFin: float, ref_clock: str, injection: str) -> float:
    """
    Protected method calculates the frequency for LO2 from LO1, RFin, and
    the selected reference clock

    @param RFin is the Spectrum Anaylzer input frequency
    @type float
    @param ref_clock is the name of the reference clock 'ref1' or 'ref2'
    @type str
    @return LO2 frequency
    @rtype float
    """
    select_dict = {"ref1": self.LO1_ref1_freq_dict, "ref2": self.LO1_ref2_freq_dict}
    LO1_freq = select_dict[ref_clock]
    IF1_corrected = LO1_freq[RFin] - RFin     # Make correction to IF1
    if injection == "HI":
      LO2_freq = IF1_corrected + hw.Cfg.IF2   # High-side injection
    elif injection == "LO":
      LO2_freq = IF1_corrected - hw.Cfg.IF2   # Low-side injection
    return LO2_freq


  def _LO3_frequency(self, LO2_freq: float, ref_clock: str, injection: str) -> float:
    IF1 = 3600
    LO3_freq = (LO2_freq - IF1) - 45.000
    return LO3_freq


  def _compute_fmn_serial(self):
    """Compute FMN lists sequentially (single CPU)."""
    print(name(), line(), 'Computing FMN values (single-threaded)...')
    self.LO2_ref1_hi_fmn_list = [hw.MHz_to_fmn(freq, hw.Cfg.ref_clock_1)[0] for freq in self.LO2_ref1_hi_freq_list]
    self.LO2_ref2_hi_fmn_list = [hw.MHz_to_fmn(freq, hw.Cfg.ref_clock_2)[0] for freq in self.LO2_ref2_hi_freq_list]
    self.LO2_ref1_lo_fmn_list = [hw.MHz_to_fmn(freq, hw.Cfg.ref_clock_1)[0] for freq in self.LO2_ref1_lo_freq_list]
    self.LO2_ref2_lo_fmn_list = [hw.MHz_to_fmn(freq, hw.Cfg.ref_clock_2)[0] for freq in self.LO2_ref2_lo_freq_list]


  def _compute_fmn_parallel(self):
    """Compute FMN lists in parallel (multiple CPUs)."""
    num_workers = min(4, self.num_cpus)  # Max 4 workers since we have 4 tasks
    print(name(), line(), f'Computing FMN values (parallel, {num_workers} workers)...')

    # Prepare arguments for each worker
    tasks = [
        (self.LO2_ref1_hi_freq_list, hw.Cfg.ref_clock_1),
        (self.LO2_ref2_hi_freq_list, hw.Cfg.ref_clock_2),
        (self.LO2_ref1_lo_freq_list, hw.Cfg.ref_clock_1),
        (self.LO2_ref2_lo_freq_list, hw.Cfg.ref_clock_2),
    ]

    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        results = list(executor.map(_compute_fmn_list, tasks))

    self.LO2_ref1_hi_fmn_list = results[0]
    self.LO2_ref2_hi_fmn_list = results[1]
    self.LO2_ref1_lo_fmn_list = results[2]
    self.LO2_ref2_lo_fmn_list = results[3]


  def create_data(self, use_parallel: bool = None) -> None:
    """
    Create all frequency and control data.

    @param use_parallel: True for parallel, False for serial, None for auto-detect
    """
    # Create the list of LO1 frequencies when using reference clock 1.
    self.LO1_ref1_freq_list = [self._LO1_frequency(RFin, hw.Cfg.Fpfd1) for RFin in self.RFin_list]
    self.LO1_ref1_freq_list = np.round(self.LO1_ref1_freq_list, decimals=9)
    # Create the list of LO1 frequencies when using reference clock 2.
    self.LO1_ref2_freq_list = [self._LO1_frequency(RFin, hw.Cfg.Fpfd2) for RFin in self.RFin_list]
    self.LO1_ref2_freq_list = np.round(self.LO1_ref2_freq_list, decimals=9)
    # Create the list of LO1 N values for setting the frequency of the ADF4356 chip when using reference clock 1
    self.LO1_ref1_N_list = np.divide(self.LO1_ref1_freq_list, hw.Cfg.Fpfd1)
    self.LO1_ref1_N_list = self.LO1_ref1_N_list.astype(int)
    # Create the list of LO1 N values for setting the frequency of the ADF4356 chip when using reference clock 2
    self.LO1_ref2_N_list = np.divide(self.LO1_ref2_freq_list, hw.Cfg.Fpfd2)
    self.LO1_ref2_N_list = self.LO1_ref2_N_list.astype(int)
    # Create the frequency lookup tables for LO1
    self.LO1_ref1_freq_dict = dict(zip(self.RFin_list, self.LO1_ref1_freq_list))
    self.LO1_ref2_freq_dict = dict(zip(self.RFin_list, self.LO1_ref2_freq_list))
    # Create the frequency lookup tables for LO2. (LO2_freq = LO1 - freq + hw.Cfg.IF2)
    freq_func = lambda freq, ref, inj: self._LO2_frequency(freq, ref, inj)
    vfunc = np.vectorize(freq_func)
    self.LO2_ref1_hi_freq_list = np.round(vfunc(self.RFin_list, "ref1", "HI"), decimals=9)
    self.LO2_ref1_lo_freq_list = np.round(vfunc(self.RFin_list, "ref1", "LO"), decimals=9)
    self.LO2_ref2_hi_freq_list = np.round(vfunc(self.RFin_list, "ref2", "HI"), decimals=9)
    self.LO2_ref2_lo_freq_list = np.round(vfunc(self.RFin_list, "ref2", "LO"), decimals=9)

    # Create the LO2 control codes - this is the slow part
    print('Starting FMN calculation...')
    fmn_start = perf_counter()

    # Auto-detect parallelism if not specified
    if use_parallel is None:
        use_parallel = self.num_cpus > 1

    if use_parallel:
        self._compute_fmn_parallel()
    else:
        self._compute_fmn_serial()

    print(name(), line(), f'FMN elapsed time = {round(perf_counter()-fmn_start, 3)} seconds')
    print()


  def dump_LO2_ref1_HI_freq(self):
    with open('LO2_ref1_hi_fmn_list.csv', 'w') as f:
      for LO2_freq in self.LO2_ref1_hi_fmn_list:
        f.write(f'{LO2_freq}\n')

  def dump_LO2_ref2_HI_freq(self):
    with open('freq_LO2_ref2_HI.csv', 'w') as f:
      for LO2_freq in self.LO2_ref2_hi_freq_list:
        f.write(f'{LO2_freq}\n')

  def dump_LO2_ref1_LO_freq(self):
    with open('freq_LO2_ref1_LO.csv', 'w') as f:
      for LO2_freq in self.LO2_ref1_lo_freq_list:
        f.write(f'{LO2_freq}\n')

  def dump_LO2_ref2_LO_freq(self):
    with open('freq_LO2_ref2_LO.csv', 'w') as f:
      for LO2_freq in self.LO2_ref2_lo_freq_list:
        f.write(f'{LO2_freq}\n')


  def save_ref1_hi_control_file(self) -> None:
    data = np.zeros((NUM_FREQUENCIES, 3), dtype=np.uint32)
    data[:, 0] = self.ref1_control_code
    data[:, 1] = self.LO1_ref1_N_list
    data[:, 2] = self.LO2_ref1_hi_fmn_list
    np.save('control_ref1_HI.npy', data)


  def save_ref2_hi_control_file(self):
    data = np.zeros((NUM_FREQUENCIES, 3), dtype=np.uint32)
    data[:, 0] = self.ref2_control_code
    data[:, 1] = self.LO1_ref2_N_list
    data[:, 2] = self.LO2_ref2_hi_fmn_list
    np.save('control_ref2_HI.npy', data)


  def save_ref1_lo_control_file(self) -> None:
    data = np.zeros((NUM_FREQUENCIES, 3), dtype=np.uint32)
    data[:, 0] = self.ref1_control_code
    data[:, 1] = self.LO1_ref1_N_list
    data[:, 2] = self.LO2_ref1_lo_fmn_list
    np.save('control_ref1_LO.npy', data)


  def save_ref2_lo_control_file(self):
    data = np.zeros((NUM_FREQUENCIES, 3), dtype=np.uint32)
    data[:, 0] = self.ref2_control_code
    data[:, 1] = self.LO1_ref2_N_list
    data[:, 2] = self.LO2_ref2_lo_fmn_list
    np.save('control_ref2_LO.npy', data)


  def dump_csv_control_files(self):
    # ref1 HI
    with open('control_ref1_HI.csv', 'w') as f:
      for freq, lo1, lo2 in zip(self.RFin_list, self.LO1_ref1_N_list, self.LO2_ref1_hi_fmn_list):
        f.write(f'{freq}:({self.ref1_control_code},{lo1},{lo2})\n')

    # ref2 HI
    with open('control_ref2_HI.csv', 'w') as f:
      for freq, lo1, lo2 in zip(self.RFin_list, self.LO1_ref2_N_list, self.LO2_ref2_hi_fmn_list):
        f.write(f'{freq}:({self.ref2_control_code},{lo1},{lo2})\n')

    # ref1 LO
    with open('control_ref1_LO.csv', 'w') as f:
      for freq, lo1, lo2 in zip(self.RFin_list, self.LO1_ref1_N_list, self.LO2_ref1_lo_fmn_list):
        f.write(f'{freq}:({self.ref1_control_code},{lo1},{lo2})\n')

    # ref2 LO
    with open('control_ref2_LO.csv', 'w') as f:
      for freq, lo1, lo2 in zip(self.RFin_list, self.LO1_ref2_N_list, self.LO2_ref2_lo_fmn_list):
        f.write(f'{freq}:({self.ref2_control_code},{lo1},{lo2})\n')



if __name__ == '__main__':
  print()
  print(f'Fpfd values are {hw.Cfg.Fpfd1} & {hw.Cfg.Fpfd2}')
  dg = DataGenerator()

  start = perf_counter()
  dg.create_data()  # Auto-detects parallel vs serial

#  dg.dump_LO2_ref1_HI_freq()
#  dg.dump_LO2_ref2_HI_freq()
#  dg.dump_LO2_ref1_LO_freq()
#  dg.dump_LO2_ref2_LO_freq()
  dg.save_ref1_hi_control_file()
  dg.save_ref2_hi_control_file()
  dg.save_ref1_lo_control_file()
  dg.save_ref2_lo_control_file()
  print(f'Time to generate all the files = {round(perf_counter()-start, 6)} seconds')

#  dg.dump_csv_control_files()

  print("Generator done")
