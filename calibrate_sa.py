# -*- coding: utf-8 -*-
#
# This file is part of WN2A_RFPeakSearch.
#
# This file is part of the WN2A_RFPeakSearch distribution
# (https://github.com/Nullkraft/WN2A_RFPeakSearch).
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
"""
Spectrum Analyzer Calibration Module

Runs calibration sweeps for all reference clock / injection mode combinations
and saves amplitude data for later processing by make_control_dictionary().
"""

import sys
import numpy as np
from pathlib import Path
from time import perf_counter

name = lambda: f"File '{__name__}.py',"
line = lambda: f"line {str(sys._getframe(1).f_lineno)},"

import application_interface as api
import serial_port as sp


# Calibration configurations: (control_file, amplitude_output)
CALIBRATION_RUNS = [
    ('control_ref1_HI.npy', 'amplitude_ref1_HI.npy'),
    ('control_ref2_HI.npy', 'amplitude_ref2_HI.npy'),
    ('control_ref1_LO.npy', 'amplitude_ref1_LO.npy'),
    ('control_ref2_LO.npy', 'amplitude_ref2_LO.npy'),
]

CAL_START = 0
CAL_STOP = 3000
CAL_NUM_POINTS = 3_000_001


def load_control_npy(sa_ctl, control_fname: str) -> bool:
    """Load a calibration control numpy file into sa_ctl.all_frequencies."""
    control_file = Path(control_fname)
    if not control_file.exists():
        print(name(), line(), f'Missing control file "{control_file}"')
        return False
    sa_ctl.all_frequencies = np.load(control_file)
    return True


def setup_calibration_sweep(sa_ctl):
    """Configure sa_ctl for a full calibration sweep (0-3000 MHz, 1 kHz steps)."""
    sa_ctl.window_x_min = CAL_START
    sa_ctl.window_x_max = CAL_STOP
    sa_ctl.window_x_range = CAL_STOP - CAL_START
    # Build the full frequency list: 0.000, 0.001, 0.002, ... 3000.000
    sa_ctl.swept_freq_list = (np.arange(CAL_NUM_POINTS) / 1000.0).tolist()


def run_single_calibration(sa_ctl, control_file: str, amplitude_file: str) -> bool:
    """
    Run a single calibration sweep and save amplitude data.

    Returns True if completed, False if cancelled by user.
    """
    serial_buf = sp.SimpleSerial.data_buffer_in

    if not load_control_npy(sa_ctl, control_file):
        return False

    setup_calibration_sweep(sa_ctl)
    serial_buf.clear()
    calibration_complete = sa_ctl.sweep(CAL_START, CAL_STOP)

    if not calibration_complete:
        print(name(), line(), 'Calibration cancelled by user')
        return False

    # Convert to volts and save as numpy array
    volts = np.array([round(v, 3) for v in api._amplitude_bytes_to_volts(sa_ctl, serial_buf)],
                     dtype=np.float32)
    np.save(amplitude_file, volts)
    print(name(), line(), f'Saved {amplitude_file} ({len(volts):,} points)')

    return True


def run_full_calibration(sa_ctl, status_callback=None) -> bool:
    """
    Run all four calibration sweeps.

    Args:
        sa_ctl: Spectrum analyzer control object
        status_callback: Optional function(str) called with status updates

    Returns:
        True if all calibrations completed, False if cancelled
    """
    start = perf_counter()

    for control_file, amplitude_file in CALIBRATION_RUNS:
        if status_callback:
            status_callback(f"Calibrating with {control_file}...")

        if not run_single_calibration(sa_ctl, control_file, amplitude_file):
            return False

    elapsed = round(perf_counter() - start, 2)
    print(name(), line(), f'Full calibration completed in {elapsed} seconds')

    if status_callback:
        status_callback('Calibration complete')

    return True


if __name__ == '__main__':
    print('This module should be imported, not run directly.')
