# -*- coding: utf-8 -*-

import numpy as np
import serial_port as sp
import sys
import time
#import serial       # requires 'pip install pyserial'

# Utility to simplify print debugging. ycecream is a lot better, though.
line = lambda : sys._getframe(1).f_lineno
name = __name__


# NOTE: This information was transported in from Mike Masterson's (WN2A) FreeBASIC code.
# Please retain for current documentation until it is incorporated into the Python source.
#
# ulong     NI, registerNum, Reg(6,401), OldReg(6) ' Reg(6, 401) is Reg(registerNum, stepNumber). 6 registers;401 max frequency steps
# string    Swept, freq, ComStr, portNum, portSpeed, delaystr, FracOpt, LockDetect
# single    Fstart, Fstop
# single    Fpfd, refClock, RFOut, FvcoEst, FracErr, Frfv(401), Initial
# integer   delay, stepNumber, Verbose, oldVerbose ', Range
# integer   MOD1, Fracc, NewMOD1, NewFracc, numFreqs, Div, dispWidth, dispHeight
# float    Fvco, N, FracT

lock_detect = True
Fvco = 0.0000       # Initialize as a type float
lockDetectOn  = 13093080,541097977,1476465218,4160782339,1674572284,2151677957   # 374.596154 MHz with Lock Detect
lockDetectOff = 13093080,541097977,1073812034,4160782339,1674572284,2151677957   # 374.596154 MHz no Lock Detect
readReg6      = 13093080,541097977,1342247490,4160782339,1674572284,2151940101   # Read register 6

dataRow = lockDetectOn      # default



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


oldChipRegisters = [0, 0, 0, 0, 0, 0]   # Set to zero's for initialization
# The steps required to program the chip is to start with the highest
# register and work your way down.
def write_registers(target_frequency, ref_clock, initialized = False):
    rfOut = target_frequency
    refClock = ref_clock
    stepNumber = 0

    if sp.ser.is_open:
        arduinoCmd = b'r'
        # Calculate and store a new set of register values used for
        # programming the MAX2871 chip with a new output frequency.
        registers = new_frequency_registers(rfOut, stepNumber, refClock)

        if initialized:
            for x, newChipRegister in enumerate(registers[::-1]):
                # Only write to a register if its value has changed.
                if newChipRegister != oldChipRegisters[x]:
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


def new_frequency_registers(newFreq, stepNumber=0, refClock=60, FracOpt=None, LockDetect="y"):
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
        N = 1e6 * (Fvco/(Fpfd))
        NI = int(N)
        FracT = N - NI

        if FracOpt != "f":      # Only run these lines if the user selected Fractional Optimization
            MOD1 = 4095
            Fracc = int(FracT * MOD1)

        Reg[stepNumber][0] = (NI * (2**15)) + (Fracc * (2**3))
        Reg[stepNumber][1] = (2**29) + (2**15) + (MOD1*(2**3)) + 1
        Reg[stepNumber][2] = dataRow[2]
        Reg[stepNumber][3] = dataRow[3]
        Reg[stepNumber][4] = 1670377980 + ((2**20) * Range)
        Reg[stepNumber][5] = dataRow[5]

        return Reg[stepNumber]


def set_lock_detect(checked):
    global lock_detect
    global dataRow
    if checked == True:
        dataRow = lockDetectOn
    else:
#        dataRow = lockDetectOff
        dataRow = readReg6


def Sweep():
    pass




# Find the highest signal amplitudes in a spectrum plot.
def peakSearch(amplitudeData, numPeaks):
    # Convert amplitudeData to a numpy.array so we can use argsort.
    amp = np.asarray(amplitudeData)
    # >>> amp(idx[0]) <<< returns highest value in amp and so on in descending order.
    idx = amp.argsort()[::-1][:numPeaks]
    return(idx)







