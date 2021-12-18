# -*- coding: utf-8 -*-

import numpy as np
import serial_port as sp
import sys
import time
#import serial       # requires 'pip install pyserial'

# Utilities provided for print debugging.
line = lambda : sys._getframe(1).f_lineno
name = __name__

lock_detect = True
Fvco = 0.0000       # Initialize as a type float
lockDetectOn  = 13093080,541097977,1476465218,4160782339,1674572284,  20971525   # 374.596154 MHz with Lock Detect
lockDetectOff = 13093080,541097977,1073812034,4160782339,1674572284,  20971525   # 374.596154 MHz no Lock Detect
readReg6      = 13093080,541097977,1342247490,4160782339,1674572284,2151940101   # Read register 6

dataRow = lockDetectOn      # default

M_list = []

def getSettingsFromUI(frequency=23.5, delay=2, refClock=60, lockDetect=True, fractionalOpt=False, freqMode=1):
    print(delay)           # milliseconds delay between one serial xmission and the next
    print(refClock)
    print(lockDetect)
    print(fractionalOpt)
    print(freqMode)

    # Select serial port
    # Select baud rate
    # Enter transmission delay
    # Enter reference clock frequency
    # Enable/Disable Lock Detect
    # Enable/Disable Fraction Optimization
    # Select Swept or Fixed frequency RF Output
        # If Swept...
            # Enter Start Frequency
            # Enter Stop Frequency
            # Enter Number of steps from Start to Stop Frequency
        # Else
            # Enter Fixed Frequency


def adf4356_write_registers(reg_num, reg_value):
    pass


oldChipRegisters = [0, 0, 0, 0, 0, 0]   # Set to zero's for initialization
# The steps required to program the chip is to start with the highest
# register and work your way down.
def max2871_write_registers(target_frequency, ref_clock, initialized = False):
    rfOut = target_frequency
    refClock = ref_clock
    stepNumber = 0

    if sp.ser.is_open:
        arduinoCmd = b'r'
        # Calculate and store a new set of register values used for
        # programming the MAX2871 chip with a new output frequency.
        registers = max2871_registers(rfOut, stepNumber, refClock)

        if initialized:
            for x, newChipRegister in enumerate(registers[::-1]):
                # Only write to a register if its value has changed.
                if newChipRegister != oldChipRegisters[x]:
                    print(name, line(), f'Changed reg[{newChipRegister & 7}] = {newChipRegister}')
                    sp.ser.write(arduinoCmd)       # Send command to the Arduino
                    sp.ser.write(newChipRegister.to_bytes(4, 'big'))
                    oldChipRegisters[x] = newChipRegister
        else:   # Initialize the MAX2871 in accordance with manufacturer.
            for x, newChipRegister in enumerate(registers[::-1]):
                sp.ser.write(arduinoCmd)       # Send command to the Arduino
                sp.ser.write(newChipRegister.to_bytes(4, 'big'))
            time.sleep(0.025)
            for x, newChipRegister in enumerate(registers[::-1]):
                sp.ser.write(arduinoCmd)       # Send command to the Arduino
                sp.ser.write(newChipRegister.to_bytes(4, 'big'))
                oldChipRegisters[x] = newChipRegister


def max2871_registers(newFreq, stepNumber=0, refClock=60, FracOpt=None, LockDetect="y"):
    global lock_detect
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
        print(name, line(), f'Fvco = newFreq * Div : {Fvco} = {newFreq} * {Div}')
        N = 1e6 * (Fvco/(Fpfd))
        NI = int(N)
        FracT = N - NI
        if FracOpt != "f":      # Only run these lines if the user selected Fractional Optimization
            MOD1 = 4095
            Fracc = int(FracT * MOD1)

        Reg[stepNumber][0] = (NI << 15) + (Fracc << 3)
        Reg[stepNumber][1] = 2**29 + 2**15 + (MOD1 << 3) + 1
        Reg[stepNumber][2] = dataRow[2]
        Reg[stepNumber][3] = dataRow[3]
        Reg[stepNumber][4] = 1670377980 + (Range << 20)
        Reg[stepNumber][5] = dataRow[5]

        for i, x in enumerate(Reg[0]):
            print(name, line(), f'reg[{i}] = {x}')
            if i == 4:
                print(name, line(), f'Range = {Range}')


        return Reg[stepNumber]


def set_lock_detect(checked):
    global lock_detect
    global dataRow
    if checked == True:
        dataRow = lockDetectOn
    else:
#        dataRow = lockDetectOff
        dataRow = readReg6


# THIS IS NOT FOR SWEEPING!!!
# If you have a frequency you want to focus on then this is the function for you.
def RF_to_LO1(freq_list, target_freq=1345):
    remainders = []
    for LO_freq in freq_list:
        # The lowest remainder will be at the index of the closest freq to the target freq
        remainders.append(np.abs(LO_freq - (target_freq + 3600)))
    lst = np.asarray(remainders)
    return lst.argmin()     # Returns the index of the lowest value in the array


def sweep():
    LO1_num_steps = int((6600 - 3600) / 30) + 1      # 3000MHz/30MHz = 100 steps
    LO2_num_steps = int((3930 - 3900) / 0.150) + 1   #  30MHz/150kHz = 200 steps

    LO1_freqs = np.linspace(3600, 6600, LO1_num_steps)    # List of LO1 freqs every 30 MHz
    LO2_freqs = np.linspace(3900, 3930, LO2_num_steps)    # List of LO2 freqs every 150 kHz

    for LO1_freq in LO1_freqs:
        int_n = adf4356_n(LO1_freq, 60, 2)
        for LO2_freq in LO2_freqs:
            fmn_data = max2871_fmn(target_freq=LO2_freq, ref_clock=60)


# Find the highest signal amplitudes in a spectrum plot.
def peakSearch(amplitudeData, numPeaks):
    # Convert amplitudeData to a numpy.array so we can use argsort.
    amp = np.asarray(amplitudeData)
    # >>> amp(idx[0]) <<< returns highest value in amp and so on in descending order.
    idx = amp.argsort()[::-1][:numPeaks]
    return(idx)


def max2871_fmn(target_freq=3000.0, ref_clock=60):
    """ Form a 32 bit word containing F, M and N.

    R, F, M and N are taken directly from the MAX2871 specsheet.
    The specsheet offers no better names for them.

    Given a target frequency the M.csv file contains a list of values for
    calculating the three register values that are needed to set the chip
    to a new frequency. This curated list of M-values provides sufficient
    frequency accuracy and is much shorter than looping through all 4093
    possible values of M.
    """
    err_list = []   # Find the best error and use the same index for the best F.
    F_list = []

    if len(M_list) == 0:
        with open('M.csv', 'r') as M_file:
            for M in M_file.readlines():
                M_list.append(int(M))
    R = 2
    Fpfd = ref_clock / R
    best_F = 0
    best_M = 0
    N = int(target_freq / Fpfd)
    fraction = (target_freq / Fpfd) - N

    F_list = [round(x * fraction) for x in M_list]
    for i, M in enumerate(M_list):
        err_list.append(abs(target_freq - (Fpfd * (N + F_list[i] / M))))
    idx = min(range(len(err_list)), key=err_list.__getitem__)

    best_F = F_list[idx]
    best_M = M_list[idx]

    # Create a 32 bit frequency_word from F, M and N to match the Arduino controller requirements
    frequency_word = (best_F << 20) | (best_M << 8) | N
    return frequency_word


def adf4356_n(Fvco: float = 3000.0, Fref: float = 60, R: int = 2) -> int:
    """ Returns the integer portion of N which is used to program
        the integer step register of the ADF4356 chip.
    """
    # TODO: Create the full register word. This is just a placeholder and is incorrect.
    INT_N = int(Fvco * R / Fref)
    return INT_N


if __name__ == '__main__':
    start = time.perf_counter()
    sweep()
    stop = time.perf_counter()
    print(f'Time to sweep = {round((stop-start), 2)}')








