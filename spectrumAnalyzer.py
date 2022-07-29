# -*- coding: utf-8 -*-
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


# Utilities provided for print debugging.
line = lambda: f'line {str(sys._getframe(1).f_lineno)},'
name = f"File \'{__name__}.py\',"

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

def load_control_dict(file_name) -> dict:
    """
    NOTE: full_sweep_dict has a value that is a tuple of LO1_N and LO2_FMN.
          LO3_FMN will be added later. The key, RFin, is a string.

    EXAMPLE USAGE:  ref, N, FMN = full_sweep_dict[RFin]
                    print(name, line(), f'ref = {ref}, N ={N} and FMN ={FMN}')
    """
    full_sweep_dict = dict()
    with open(file_name, 'r') as f:
        for freq in f:
            RFin, ref, LO1_N, LO2_FMN = freq.split()
            RFin = float(RFin)
            ref = int(ref)
            LO1_N = int(LO1_N)
            LO2_FMN = int(LO2_FMN)
            full_sweep_dict[RFin] = (ref, LO1_N, LO2_FMN)
    return full_sweep_dict


def sweep(start_freq, stop_freq, step_freq, ref_clock):
    """
    Function sweep() : Search the input for any or all RF signals
    sa.sweep(sa.sweep_start, sa.sweep_stop, sa.sweep_step_size, sa.ref_clock)
    """
    prev_ref_clock = 0  # Used to decide if a new ref_clock code is to be sent
    prev_LO1_code = 0   # Used to decide if a new LO1_code is to be sent
    swept_frequencies_list.clear()
    
    sweep_start     = round(start_freq * 1000)  # kHz - Needs to be integer for slicing the RFin_array (list)
    sweep_stop      = round(stop_freq * 1000)  # kHz - Needs to be integer for slicing the RFin_array (list)
    sweep_step_size = ceil((sweep_stop - sweep_start) / sweep_num_steps)         # Slightly larger step forces python to go beyond sweep_stop
    sweep_stop_boundary = ceil(sweep_stop / sweep_step_size) * sweep_step_size   # ceil() ensures ending after sweep_stop

    # Perform the sweep
    cmd_proc.sel_315MHz_adc()                                   # Select for LO2 output data
    cmd_proc.set_LO2(cmd_proc.LO2_neg4dBm)                      # Bring the LO2 online
    cmd_proc.disable_LO3_RFout()
    for freq in cfg.RFin_array[sweep_start : sweep_stop_boundary : sweep_step_size]:
        reference, LO1_code, LO2_code = full_sweep_dict[freq]
        if reference != prev_ref_clock:
            cmd_proc.enable_ref_clock(reference)
            time.sleep(0.0025)
            prev_ref_clock = reference
            print(name, line(), f'New ref_clock set to {hex(reference)}')
        if LO1_code != prev_LO1_code:
            cmd_proc.set_LO1(cmd_proc.LO1_neg4dBm, LO1_code)    # Select LO1 with -4 dBm Rfout and frequency = LO1_code
            time.sleep(0.0025)
            prev_LO1_code = LO1_code
        cmd_proc.set_max2871_freq(LO2_code)
        swept_frequencies_list.append(freq)                     # Frequencies needed for plotting
        time.sleep(0.0025)
        print(name, line(), '\t', f'RFin {freq} : LO1 {LO1_code*66} MHz : LO2 {round(fmn_to_MHz(LO2_code, ref_clock), 3)} MHz')

    cmd_proc.sweep_done()   # Handshake signal to controller

    print('Sweep complete')


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
    cmd_proc.disable_all_ref_clocks()       # Stop both ref clocks before enabling one of them
    if clock_id == 0:
        ref_clock = None
    if clock_id == 1:
        ref_clock = cfg.ref_clock_1
        cmd_proc.enable_ref_clock(cmd_proc.ref_clock1_enable)
    if clock_id == 2:
        ref_clock = cfg.ref_clock_2
        cmd_proc.enable_ref_clock(cmd_proc.ref_clock2_enable)
    return ref_clock


if __name__ == '__main__':
    print()

    start_freq  = 1311.013
    stop_freq   = 1320.074
    step_freq   = 0.003
    sweep_range = np.arange(start_freq, stop_freq, step_freq)

    start = time.perf_counter()
    sweep_list = [round(freq, 6) for freq in sweep_range]
    d = load_control_dict('full_control_ref1.csv')
    stop = time.perf_counter()
    print(f'Time to load full_control_ref1.csv = {round(stop-start, 6)} seconds')

    sweep_dict = {}
    for freq in sweep_list:
        sweep_dict[freq] = d[freq]
    
    print(f'Len sweep dict = {len(sweep_dict)}')
    print(f'Len of sweep dict = {len(sweep_dict)}')
    print(f'Len of full control dict = {len(d)}')
#    print(f'Last record of sweep_dict[{stop_freq-.001}] = {sweep_dict[stop_freq-.001]}')
    

    print("Done")
















