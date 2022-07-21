# -*- coding: utf-8 -*-
""" Spectrum Analyzer Notes:

    LO1 = int({IF1 + RFin} - [{IF1 + RFin} / Fpfd])
    LO2 = LO1 - RFin + IF2
    RFin = LO1 + IF2 - LO2
    
"""
import sys
import numpy as np
from dataclasses import dataclass
from time import perf_counter

import command_processor as cmd_proc
from hardware_cfg import cfg


# Utilities provided for print debugging.
line = lambda: f'line {str(sys._getframe(1).f_lineno)},'
name = f'File \"{__name__}.py\",'

ref_clock = cfg.ref_clock_1
sweep_start = 4.0
sweep_stop = 3000.0
sweep_step = 250
last_sweep_start = 4.0
last_sweep_stop = 3000.0
last_sweep_step = 250
full_sweep_dict = {}    # Dictionary of ref_clock, LO1, LO2, and LO3 from 0 to 3000 MHz in 1 kHz steps


x_axis_list = list()        # List of frequencies that sychronizes plotting with sweeping.
y_axis_list = list()        # List of amplitudes that are sychronized with plotting.

@dataclass
class LO1():
    """
        The LO1 register values are stored in reverse. That means
        register value 13 is stored in Reg[0] and register value 0
        is stored in Reg[13].

        This is done to match the requirement that the chip is
        programmed starting from the highest register first.
    """
    Reg = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    Reg[0]  = 0x0000000D  # Reg[13]
    Reg[1]  = 0x000015FC  # .
    Reg[2]  = 0x0061200B  # .
    Reg[3]  = 0x00C00EBA  # .
    Reg[4]  = 0x0F09FCC9  # .
    Reg[5]  = 0x15596568  # .
    Reg[6]  = 0x060000F7  # .
    Reg[7]  = 0x95012046  # .
    Reg[8]  = 0x00800025  # .
    Reg[9]  = 0x32008984  # .
    Reg[10] = 0x00000003  # .
    Reg[11] = 0x00000012  # .
    Reg[12] = 0x00000001  # .
    Reg[13] = 0x002007C0  # Reg[0]


@dataclass
class LO2():
    """
        The LO2 register values are stored in reverse. That means
        register value 5 is stored in Reg[0] and register value 0
        is stored in Reg[5].

        This is done so the chip can be programmed starting from
        the highest register first.
    """
    Reg = [0, 0, 0, 0, 0, 0]
    Reg[0] = 0x00400005     # Register 5 on the MAX2871 chip
    Reg[1] = 0x638FF1C4     # .
    Reg[2] = 0xF8008003     # .
    Reg[3] = 0xD8008042     # . (Digital Lock detect ON), (if Fpfd > 32 MHz Bit[31] must be 1)
    Reg[4] = 0x2000FFE9     # .
    Reg[5] = 0x00419550     # Register 0 on the MAX2871 chip


@dataclass
class LO3():
    """
        The LO3 device registers are stored in reverse.  That means
        device register 5 is stored in Reg[0] and device register 0
        is stored in Reg[5].

        This is done so the chip can be programmed starting from
        the highest register first.
    """
    Reg = [0, 0, 0, 0, 0, 0]
    Reg[0] = 0x00400005
    Reg[1] = 0x63CFF104
    Reg[2] = 0xF8008003
    Reg[3] = 0xD8008042    # Digital Lock detect ON  (if Fpfd > 32 MHz Bit[31] must be 1
    Reg[4] = 0x20008011
    Reg[5] = 0x00480000


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


def update_LO2_fmn_list(freq_step: float=0.25):
    """
    @Function Get the MAX2871 fmn values from a file (it's way faster than a for-loop)

    @param freq_step DESCRIPTION For plotting the amplitude vs. frequencie for each step
    @type float (optional)
    """
    global sweep_step
    fmn_LT = [()]
    file_name = "LO2_1kHz_fmn_steps.csv"
    if 0.001 <= freq_step <= .25:
        sweep_step = int(freq_step * 1000)
    with open(file_name) as f:
        fmn_LT = [int(x) for x in f]
    return fmn_LT


def sweep(start_freq, stop_freq, step_freq, ref_clock):
    """
    Function sweep() : Search the input for any or all RF signals
    """
    print()
    global last_sweep_start
    global last_sweep_stop
    global last_sweep_step
    
#    start_idx = full_sweep_dict.index(start_freq)
#    print(name, line(), f'Stat freq index = {start_idx}')
    
    # sweep_start, sweep_stop, and sweep_step_kHz need to be indexes
    if last_sweep_start != start_freq or last_sweep_stop != stop_freq or last_sweep_step != step_freq:
        print(name, line(), 'last sweep was different!')
#        step_MHz = round(step_freq / 1000, 3)
        last_sweep_start = start_freq
        last_sweep_stop = stop_freq
        last_sweep_step = step_freq

    cmd_proc.sweep_done()
#    sweep_list = [round(freq, 3) for freq in np.arange(start_freq, stop_freq, step_MHz)]
#    print(name, line(), f'Len sweep_list = {len(sweep_list)}')
#    for freq in sweep_list:
#        control_data = full_sweep_dict[freq]
#        print(name, line(), f'Control Data = {control_data} and is type {type(control_data)}')
    
#    x_axis_list.clear()
#    intermediate_freq_1 = 3600          # Defined by the Spectrum Analyzer hardware design
#    Fpfd = int(ref_clock / 2)      # Fpfd is equivalent to Fpfd
#    LO1_start_freq = int(intermediate_freq_1 + (start_freq - start_freq % Fpfd))
#    LO1_stop_freq = int(intermediate_freq_1 + (stop_freq - stop_freq % Fpfd) + Fpfd)
#    sweep_start = LO1_start_freq - intermediate_freq_1
#    sweep_stop = LO1_stop_freq - intermediate_freq_1
#    cmd_proc.sel_315MHz_adc()               # Select the ADC for the LO2 output
#    cmd_proc.enable_ref_clock1()       # Select 60 Mhz reference clock
#
#    LO1_N_list = [MHz_to_N(freq) for freq in range(LO1_start_freq, LO1_stop_freq, Fpfd)]
#
##    mixer1_freq_list = [(N * Fpfd + 315) for N in LO1_N_list]
#    print(name, line(), f'sweep_step = {sweep_step}, {type(sweep_step)}')

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#    step_list = list(LO2_30Fpfd_steps)[::sweep_step]    # sweep_step needs to be index_step

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#    for LO1_N in LO1_N_list:
#        mixer1_freq = LO1_N * Fpfd + 315
#        cmd_proc.set_LO(cmd_proc.LO1_neg4dBm, LO1_N)    # Set LO1 to next frequency
#        cmd_proc.set_LO(cmd_proc.LO2_pos5dBm)           # Select LO2
#        for i, LO2_freq in enumerate(step_list):
#            LO2_fmn = LO2_30Fpfd_steps[LO2_freq]
#            RFin = mixer1_freq - LO2_freq
#            if start_freq < RFin < stop_freq:
#                cmd_proc.set_max2871_freq(LO2_fmn)      # why were you called 1200 times for a single LO1
#                x_axis_list.append(RFin)
#                time.sleep(0.0025)

#    cmd_proc.sweep_done()   # Handshake signal to Arduino


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
    print(name, line(), f'F = {F} : M = {M} : N = {N}')
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
        cmd_proc.enable_ref_clock1()
    if clock_id == 2:
        ref_clock = cfg.ref_clock_2
        cmd_proc.enable_ref_clock2()
    return ref_clock


if __name__ == '__main__':
    print()

    start_freq  = 1311.013
    stop_freq   = 1320.074
    step_freq   = 0.003
    sweep_range = np.arange(start_freq, stop_freq, step_freq)

    start = perf_counter()
    sweep_list = [round(freq, 6) for freq in sweep_range]
    d = load_control_dict('full_control_ref1.csv')
    stop = perf_counter()
    print(f'Time to load full_control_ref1.csv = {round(stop-start, 6)} seconds')

    sweep_dict = {}
    for freq in sweep_list:
        sweep_dict[freq] = d[freq]
    
    print(f'Len sweep dict = {len(sweep_dict)}')
    print(f'Len of sweep dict = {len(sweep_dict)}')
    print(f'Len of full control dict = {len(d)}')
#    print(f'Last record of sweep_dict[{stop_freq-.001}] = {sweep_dict[stop_freq-.001]}')
    

    print("Done")
















