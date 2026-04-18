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
import logging
import logging_setup    # Used for its side effects
_ = logging_setup   # silence Warning: 'logging_setup' imported but unused
import os
import platform
import numpy as np
from time import perf_counter
from concurrent.futures import ProcessPoolExecutor

try:
  import torch
except ImportError:
  torch = None

import hardware_cfg as hw
import command_processor as cmd


NUM_FREQUENCIES = 3_000_001
NPY_DATA_DIR = 'npy_data_files'


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
    self.parallel_workers = None
    self._report_environment()
    self._report_array_storage()


  def _report_environment(self) -> None:
    python_version = platform.python_version()
    logging.info(f'Python version: {python_version} ({platform.python_implementation()})')
    logging.info(f'NumPy version: {np.__version__}')
    if torch is None:
      logging.info('Torch version: not installed')
      logging.info('Torch device: unavailable')
    else:
      try:
        torch_version = torch.__version__
      except AttributeError:
        torch_version = 'unknown'
      logging.info(f'Torch version: {torch_version}')
      if torch.cuda.is_available():
        try:
          device_index = torch.cuda.current_device()
          device_name = torch.cuda.get_device_name(device_index)
          torch_device = f'cuda:{device_index} ({device_name})'
        except Exception:
          torch_device = 'cuda (device details unavailable)'
      else:
        torch_device = 'cpu'
      logging.info(f'Torch device: {torch_device}')
    logging.info(f'Available CPU processes: {self.num_cpus}')


  def _report_array_storage(self, extra_arrays=None) -> None:
    tracked_arrays = {
      'RFin_list': self.RFin_list,
    }
    if extra_arrays:
      tracked_arrays.update(extra_arrays)
    memmap_arrays = [name for name, arr in tracked_arrays.items() if isinstance(arr, np.memmap)]
    if memmap_arrays:
      formatted = ', '.join(memmap_arrays)
      logging.info(f'Memory-mapped arrays: {formatted}')
    else:
      logging.info('Tracked arrays currently reside in RAM (NumPy ndarray).')


  def _log_num_workers(self, num_workers: int, parallel: bool) -> None:
    if parallel:
      logging.info(f'Configured process pool workers: {num_workers}')
    else:
      logging.info(f'Configured workers: {num_workers} (serial execution)')


  def _LO1_frequency_vectorized(self, RFin: np.ndarray, Fref: float, R: int = 1) -> np.ndarray:
    """
    Vectorized LO1 frequency calculation for entire RFin array.

    @param RFin is the array of Spectrum Analyzer input frequencies
    @type np.ndarray
    @param Fref is the frequency of the selected reference clock
    @type float
    @param R is from the manufacturer's specsheet (defaults to 1)
    @type int (optional)
    @return Array of LO1 frequencies that step by the Fpfd value
    @rtype np.ndarray
    """
    Fpfd = Fref / R
    IF1 = np.where(RFin <= 2000, 3800, 3700)
    return Fpfd * np.round((RFin + IF1) / Fpfd)


  def _LO2_frequency_vectorized(self, RFin: np.ndarray, LO1_freq: np.ndarray, injection: str) -> np.ndarray:
    """
    Vectorized LO2 frequency calculation.

    @param RFin is the array of Spectrum Analyzer input frequencies
    @type np.ndarray
    @param LO1_freq is the array of LO1 frequencies (already computed)
    @type np.ndarray
    @param injection is 'HI' for high-side or 'LO' for low-side injection
    @type str
    @return Array of LO2 frequencies
    @rtype np.ndarray
    """
    IF1_corrected = LO1_freq - RFin
    if injection == "HI":
        return IF1_corrected + hw.Cfg.IF2
    else:  # "LO"
        return IF1_corrected - hw.Cfg.IF2


  def _LO3_frequency(self, LO2_freq: float, ref_clock: str, injection: str) -> float:
    # TODO: Implement when hardware is available for testing
    IF1 = 3600
    LO3_freq = (LO2_freq - IF1) - 45.000
    return LO3_freq


  def _compute_fmn_serial(self):
    """Compute FMN lists sequentially (single CPU)."""
    logging.info('Computing FMN values (single-threaded)...')
    self.LO2_ref1_hi_fmn_list = [hw.MHz_to_fmn(freq, hw.Cfg.ref_clock_1)[0] for freq in self.LO2_ref1_hi_freq_list]
    self.LO2_ref2_hi_fmn_list = [hw.MHz_to_fmn(freq, hw.Cfg.ref_clock_2)[0] for freq in self.LO2_ref2_hi_freq_list]
    self.LO2_ref1_lo_fmn_list = [hw.MHz_to_fmn(freq, hw.Cfg.ref_clock_1)[0] for freq in self.LO2_ref1_lo_freq_list]
    self.LO2_ref2_lo_fmn_list = [hw.MHz_to_fmn(freq, hw.Cfg.ref_clock_2)[0] for freq in self.LO2_ref2_lo_freq_list]


  def _compute_fmn_parallel(self, num_workers: int):
    """Compute FMN lists in parallel (multiple CPUs)."""
    worker_label = 'worker' if num_workers == 1 else 'workers'
    logging.info(f'Computing FMN values (parallel, {num_workers} {worker_label})...')

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
    lo1_start = perf_counter()
    # Create the list of LO1 frequencies when using reference clock 1.
    self.LO1_ref1_freq_list = np.round(
        self._LO1_frequency_vectorized(self.RFin_list, hw.Cfg.Fpfd1), decimals=9
    )
    # Create the list of LO1 frequencies when using reference clock 2.
    self.LO1_ref2_freq_list = np.round(
        self._LO1_frequency_vectorized(self.RFin_list, hw.Cfg.Fpfd2), decimals=9
    )
    logging.info(f'LO1 elapsed time = {round(perf_counter()-lo1_start, 3)} seconds')
    # Create the list of LO1 N values for setting the frequency of the ADF4356 chip when using reference clock 1
    self.LO1_ref1_N_list = np.divide(self.LO1_ref1_freq_list, hw.Cfg.Fpfd1)
    self.LO1_ref1_N_list = self.LO1_ref1_N_list.astype(int)
    # Create the list of LO1 N values for setting the frequency of the ADF4356 chip when using reference clock 2
    self.LO1_ref2_N_list = np.divide(self.LO1_ref2_freq_list, hw.Cfg.Fpfd2)
    self.LO1_ref2_N_list = self.LO1_ref2_N_list.astype(int)
    # Create the frequency lists for LO2. (LO2_freq = LO1 - RFin ± IF2)
    lo2_start = perf_counter()
    self.LO2_ref1_hi_freq_list = np.round(
        self._LO2_frequency_vectorized(self.RFin_list, self.LO1_ref1_freq_list, "HI"), decimals=9
    )
    self.LO2_ref1_lo_freq_list = np.round(
        self._LO2_frequency_vectorized(self.RFin_list, self.LO1_ref1_freq_list, "LO"), decimals=9
    )
    self.LO2_ref2_hi_freq_list = np.round(
        self._LO2_frequency_vectorized(self.RFin_list, self.LO1_ref2_freq_list, "HI"), decimals=9
    )
    self.LO2_ref2_lo_freq_list = np.round(
        self._LO2_frequency_vectorized(self.RFin_list, self.LO1_ref2_freq_list, "LO"), decimals=9
    )
    logging.info(f'LO2 elapsed time = {round(perf_counter()-lo2_start, 3)} seconds')

    # Create the LO2 control codes - this is the slow part
    print('Starting FMN calculation...')
    fmn_start = perf_counter()

    # Auto-detect parallelism if not specified
    if use_parallel is None:
        use_parallel = self.num_cpus > 1

    if use_parallel:
        num_workers = min(4, self.num_cpus)  # Max 4 workers since we have 4 tasks
        self.parallel_workers = num_workers
        self._log_num_workers(num_workers, parallel=True)
        self._compute_fmn_parallel(num_workers)
    else:
        self.parallel_workers = 1
        self._log_num_workers(1, parallel=False)
        self._compute_fmn_serial()

    logging.info(f'FMN elapsed time = {round(perf_counter()-fmn_start, 3)} seconds')
    print()


  def save_ref1_hi_control_file(self) -> None:
    data = np.zeros((NUM_FREQUENCIES, 3), dtype=np.uint32)
    data[:, 0] = self.ref1_control_code
    data[:, 1] = self.LO1_ref1_N_list
    data[:, 2] = self.LO2_ref1_hi_fmn_list
    np.save(f'{NPY_DATA_DIR}/control_ref1_HI.npy', data)


  def save_ref2_hi_control_file(self) -> None:
    data = np.zeros((NUM_FREQUENCIES, 3), dtype=np.uint32)
    data[:, 0] = self.ref2_control_code
    data[:, 1] = self.LO1_ref2_N_list
    data[:, 2] = self.LO2_ref2_hi_fmn_list
    np.save(f'{NPY_DATA_DIR}/control_ref2_HI.npy', data)


  def save_ref1_lo_control_file(self) -> None:
    data = np.zeros((NUM_FREQUENCIES, 3), dtype=np.uint32)
    data[:, 0] = self.ref1_control_code
    data[:, 1] = self.LO1_ref1_N_list
    data[:, 2] = self.LO2_ref1_lo_fmn_list
    np.save(f'{NPY_DATA_DIR}/control_ref1_LO.npy', data)


  def save_ref2_lo_control_file(self) -> None:
    data = np.zeros((NUM_FREQUENCIES, 3), dtype=np.uint32)
    data[:, 0] = self.ref2_control_code
    data[:, 1] = self.LO1_ref2_N_list
    data[:, 2] = self.LO2_ref2_lo_fmn_list
    np.save(f'{NPY_DATA_DIR}/control_ref2_LO.npy', data)



if __name__ == '__main__':
  print()
  print(f'Fpfd values are {hw.Cfg.Fpfd1} & {hw.Cfg.Fpfd2}')
  dg = DataGenerator()

  start = perf_counter()
  dg.create_data()  # Auto-detects parallel vs serial

  dg.save_ref1_hi_control_file()
  dg.save_ref2_hi_control_file()
  dg.save_ref1_lo_control_file()
  dg.save_ref2_lo_control_file()
  print(f'Time to generate all the files = {round(perf_counter()-start, 6)} seconds')

  print("Generator done")
