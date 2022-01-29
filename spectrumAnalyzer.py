# -*- coding: utf-8 -*-

import numpy as np
import serial_port as sp
import sys
import time
import command_processor as cmd_proc

# Utilities provided for print debugging.
line = lambda : sys._getframe(1).f_lineno
name = __name__

Fvco = 0.0000       # Initialize as a type float

M_list = []
FMN_list = []




"""
    NOTE: The LO1, LO2 and LO3 register values are stored in reverse.
          For LO1 that means register value 13 is stored in Reg[0]
          and register value 0 is stored in Reg[13].

          Likewise for LO2 and LO3 where register value 5 is stored
          in Reg[0] and register value 0 is stored in Reg[5].

          This is done to match the requirement that the chip
          registers are programmed from highest to lowest.
"""

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


def sweep(start_freq: int=25, stop_freq: int=3000):
    """
    Function sweep() : Search the input for any or all RF signals
    """
    cmd_proc.enable_315MHz_adc()    # LO2 ADC selected
    cmd_proc.enable_60MHz_ref_clock()
    reference_freq = 60
    IF1 = 3600   # Intermediate Frequency 1
    step_size = int(reference_freq / 2)  # step_size is equivalent to Fpfd

    F_start = int(IF1 + (start_freq - start_freq % step_size))           # Find LO1 start freq
    F_stop = int(IF1 + (stop_freq - stop_freq % step_size) + step_size)  # Find LO1 stop freq
    LO1_freq_list = [f for f in range(F_start, F_stop, step_size)]
    LO1_num_steps = len(LO1_freq_list)

    for LO1_freq in LO1_freq_list:
        N = adf4356_n(LO1_freq)
        cmd_proc.set_LO(cmd_proc.LO1_neg1dBm | N, LO1_num_steps)  # Select LO1, set frequency to N and RFout to -1dBm
        cmd_proc.set_LO(cmd_proc.LO2_neg4dBm)
        LO2_freq_list = [freq for freq in np.arange(3900, 3930, 0.25)]
        for LO2_freq in LO2_freq_list:
            FMN = MHz_to_fmn(LO2_freq)
            FMN_bytes = FMN.to_bytes(4, byteorder='little')
            sp.ser.write(FMN_bytes)                # Send FMN as bytes to set LO2 to a new freq
            read_adc(0)


def read_adc(selected_adc):
    pass


def write_adf4356_registers(reg_num, reg_value):
    pass


oldChipRegisters = [0, 0, 0, 0, 0, 0]   # Set to zero's for initialization
# The steps required to program the chip is to start with the highest
# register and work your way down.
def max2871_write_registers(target_frequency, LO=None, ref_clock = 60):
    rfOut = target_frequency
    stepNumber = 0

    # Calculate and store a new set of MAX2871 register values
    # used for setting LO2 or LO3 output frequency.
    registers = max2871_registers(rfOut, stepNumber, LO, ref_clock)

    if sp.ser.is_open:
        for x, newChipRegister in enumerate(registers[::-1]):
            # Only write to a register if its value has changed.
            if newChipRegister != oldChipRegisters[x]:
                print(name, line(), f'Changed reg[{newChipRegister & 7}] = {newChipRegister}')
                sp.ser.write(newChipRegister.to_bytes(4, 'little'))
                oldChipRegisters[x] = newChipRegister


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
    idx = amp.argsort()[::-1][:numPeaks]
    return(idx)


def read_fmn_file(file_name='FMN.csv'):
    with open(file_name, 'r') as FMN_file:
        for FMN in FMN_file.readlines():
            FMN_list.append(int(FMN))


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
    M_list = range(2, 4096)
    for M in M_list:
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


def adf4356_n(Fvco: float = 3600, Fref: float = 60, R: int = 2) -> int:
    """ Returns the integer portion of N which is used to program
        the integer step register of the ADF4356 chip.
    """
    int_N = int(Fvco * R / Fref)    # OR Fvco/Fpfd == Fvco/30
    return (int_N << 16)


if __name__ == '__main__':
    print()















