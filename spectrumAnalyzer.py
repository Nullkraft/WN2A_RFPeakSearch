# -*- coding: utf-8 -*-

import yappi

import numpy as np
import sys
import time
import command_processor as cmd_proc

# Utilities provided for print debugging.
line = lambda : sys._getframe(1).f_lineno
name = __name__

reference_freq = 0
sweep_start = 0
sweep_stop = 0
sweep_step = 250


swept_frequency_list = []

LO2_30Fpfd_steps = ()
x_axis_list = []        # List of frequencies that sychronizes plotting with sweeping.
y_axis_list = []        # List of amplitudes that are sychronized with plotting.
#LO2_50Fpfd_steps = ()


class LO1():
    """
        The LO1 register values are stored in reverse. That means
        register value 13 is stored in Reg[0] and register value 0
        is stored in Reg[13].

        This is done to match the requirement that the chip is
        programmed starting from the highest register first.
    """
    Reg = []
    Reg.append(0x0000000D)
    Reg.append(0x000015FC)
    Reg.append(0x0061200B)
    Reg.append(0x00C00EBA)
    Reg.append(0x0F09FCC9)
    Reg.append(0x15596568)
    Reg.append(0x060000F7)
    Reg.append(0x95012046)
    Reg.append(0x00800025)
    Reg.append(0x32008984)
    Reg.append(0x00000003)
    Reg.append(0x00000012)
    Reg.append(0x00000001)
    Reg.append(0x002007C0)


class LO2():
    """
        The LO2 register values are stored in reverse. That means
        register value 5 is stored in Reg[0] and register value 0
        is stored in Reg[5].

        This is done to match the requirement that the chip is
        programmed starting from the highest register first.
    """
    Reg = []
    Reg.append(0x00419550)
    Reg.append(0x2000FFE9)
    Reg.append(0x58008042)    # Digital Lock detect ON
    Reg.append(0xF8008003)
    Reg.append(0x638FF1C4)
    Reg.append(0x00400005)


class LO3():
    """
        The LO3 device registers are stored in reverse.  That means
        device register 5 is stored in Reg[0] and device register 0
        is stored in Reg[5].

        This matches the requirement that the chip is programmed
        starting from the highest device register first.
    """
    Reg = []
    Reg.append(0x00480000)
    Reg.append(0x20008011)
    Reg.append(0x58008042)    # Digital Lock detect ON
    Reg.append(0xF8008003)
    Reg.append(0x63CFF104)
    Reg.append(0x00400005)


def update_LO2_fmn_list(freq_step: float=0.25):
    """
    Function Get the MAX2871 fmn values from a file (it's way faster than a for-loop)

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


#@yappi.profile(clock_type="wall")
def sweep(start_freq: int=4, stop_freq: int=3000, freq_step: float=0.25, reference_freq: int=60):
    """
    Function sweep() : Search the input for any or all RF signals
    """
    global sweep_start
    global sweep_stop
    global x_axis_list
    x_axis_list.clear()
    intermediate_freq_1 = 3600           # Defined by the Spectrum Analyzer hardware design
    Fpfd = int(reference_freq / 2)  # Fpfd is equivalent to Fpfd
    LO1_start_freq = int(intermediate_freq_1 + (start_freq - start_freq % Fpfd))
    LO1_stop_freq = int(intermediate_freq_1 + (stop_freq - stop_freq % Fpfd) + Fpfd)
    sweep_start = LO1_start_freq - intermediate_freq_1
    sweep_stop = LO1_stop_freq - intermediate_freq_1
    cmd_proc.sel_315MHz_adc()               # Select the ADC for the LO2 output
    cmd_proc.enable_60MHz_ref_clock()       # Select 60 Mhz reference clock
    LO1_N_list = [MHz_to_N(freq) for freq in range(LO1_start_freq, LO1_stop_freq, Fpfd)]
#    print(name, line(), f'Len LO1 N list = {len(LO1_N_list)}')
    for LO1_N in LO1_N_list:
        mixer1_freq = LO1_N * Fpfd + 315
        cmd_proc.set_LO(cmd_proc.LO1_neg4dBm, LO1_N)    # Set LO1 to next frequency
        cmd_proc.set_LO(cmd_proc.LO2_pos5dBm)           # Select LO2
        step_list = list(LO2_30Fpfd_steps)[::sweep_step]    # Move this to when user sets a new sweep
        time.sleep(.001)
        for LO2_freq in step_list:
            start = time.perf_counter()
            LO2_fmn = LO2_30Fpfd_steps[LO2_freq]
            RFin = mixer1_freq - LO2_freq
            if start_freq < RFin < stop_freq:
                cmd_proc.set_max2871_freq(LO2_fmn)      # why were you called 1200 times for a single LO1
                x_axis_list.append(RFin)
                time.sleep(0.0025)
        print(name, line(), round(time.perf_counter()-start, 3))
        start = 0
    cmd_proc.sweep_done()   # Handshake signal to Arduino





def max2871_registers(newFreq, stepNumber=0, LO=None, refClock=60, FracOpt=None, LockDetect="y"):
    global dataRow

    refClockDivider = 4
    Fpfd = (refClock * (1e6)) / refClockDivider    # Default Fpfd = 15 MHz
    rangeNum = 0
    Div = 1
    Reg = list(range(6)), list(range(402))

    while (newFreq*Div) < 3000:
        rangeNum += 1           # Divider Range still not found.
        Div = 2**rangeNum       # Next Divider Range
    else:
        Range = rangeNum
        Fvco = newFreq * Div
#        print(name, line(), f'Fvco = newFreq * Div : {Fvco} = {newFreq} * {Div}')
        N = 1e6 * (Fvco/(Fpfd))
        NI = int(N)
        FracT = N - NI
        if FracOpt != "f":      # Only run these lines if the user selected Fractional Optimization
            MOD1 = 4095
            Fracc = int(FracT * MOD1)

        Reg[stepNumber][0] = (NI << 15) + (Fracc << 3)
        Reg[stepNumber][1] = 2**29 + 2**15 + (MOD1 << 3) + 1
        Reg[stepNumber][2] = LO2.Reg[2]
        Reg[stepNumber][3] = LO2.Reg[3]
        Reg[stepNumber][4] = 1670377980 + (Range << 20)
        Reg[stepNumber][5] = LO2.Reg[5]

        for i, x in enumerate(Reg[0]):
            print(name, line(), f'reg[{i}] = {x}')


        return Reg[stepNumber]



# THIS IS NOT FOR SWEEPING!!!
# If you have a frequency you want to focus on then this is the function for you.
def RF_to_LO1(freq_list, target_freq=1345):
    remainders = []
    for LO_freq in freq_list:
        # The lowest remainder will be at the index of the closest freq to the target freq
        remainders.append(np.abs(LO_freq - (target_freq + 3600)))
    lst = np.asarray(remainders)
    return lst.argmin()     # Returns the index of the lowest value in the array


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


def MHz_to_fmn(RFout_MHz: float, Fref: float=60) -> int:
    """ Form a 32 bit word containing F, M and N.

        F, M, and N are defined in the manufacturer's specsheet.
        Frac F is the fractional division value (0 to MOD-1)
        Mod M is the modulus value
        Int N is the 16-bit N counter value (In Frac-N mode min 19 to 4091)
    """
    R = 2
    Fvco = 0
    div_range = 0
    max_error = 2**32
    for div_range in range(8):
        div = 2**div_range
        Fvco = div * RFout_MHz
        if Fvco >= 3000:
            break
    Fpfd = Fref / R
    N = int(Fvco / Fpfd)
    Fract = Fvco / Fpfd - N
    for M in range(2, 4096):
        F = round(Fract * M)
        Err1 = abs(Fvco - (Fpfd * (N + F/M)))
        if Err1 < max_error:
            max_error = Err1
            best_F = F
            best_M = M
        if Err1 == 0:
            # Found the exact solution - Stop looking!
            break
    return best_F<<20 | best_M<<8 | N


def fmn_to_MHz(fmn_word, Fpfd=30):
    """
    Function: fmn_to_freq is a utility for verifying that your fmn value
              correctly matches the frequency that you think it does.

    @param fmn_word is a 32 bit word that contains the F, M, and N values
    @type <class 'int'>
    @param Fpfd is half the frequency of the reference clock (defaults to 30)
    @return Frequency in MHz
    @rtype float
    """
    F = fmn_word >> 20
    M = (fmn_word & 0xFFFFF) >> 8
    if M == 0:
        print(fmn_word)
    N = fmn_word & 0xFF
    return Fpfd*(N + F/M)


def MHz_to_N(RFout_MHz: float = 3600, Fref: float = 60, R: int = 2) -> int:
    """ Returns the integer portion of N which is used to program
        the integer step register of the ADF4356 chip.
    """
    N = int(RFout_MHz * (2/Fref))
    return (N)


def make_fmn_file():
    """
    Function Generates an FMN step file for use by LO2 and LO3.
    Only used to regenerate missing file or initially create the step file.
    """
    freq_file = "LO2_1kHz_freq_steps.csv"
    fmn_file = "LO2_1kHz_fmn_steps.csv"
    fmn_list = []
    with open(freq_file, 'w') as frq:
        for freq in np.arange(3914.999, 3884.999, -.001):   # Assumes Fpfd = 30 MHz
            frq.write(str(round(freq, 3)) + '\n')   # Write the given frequency to the step file
            fmn = MHz_to_fmn(freq)                  # Calculate LO2_fmn for the given frequency
            fmn_list.append(fmn)                    # Creating the LO2_fmn_list
    with open(fmn_file, 'w') as f:
        for f_m_n in fmn_list:
            f.write(str(f_m_n) + '\n')              # Copy the LO2_fmn_list contents to the fmn step file


def load_LO2_freq_steps(fmn_file='LO2_1kHz_fmn_steps.csv', freq_file="LO2_1kHz_freq_steps.csv"):
    global LO2_30Fpfd_steps
    with open(fmn_file) as R:
        fmn_list = [int(x) for x in R]
    with open(freq_file) as F:
        freq_list = [float(x) for x in F]
    LO2_30Fpfd_steps = dict(zip(freq_list, fmn_list))   # We now have a blazing fast dictionary




if __name__ == '__main__':
    print()

#    make_fmn_file()
    load_LO2_freq_steps()

    print("Done")












