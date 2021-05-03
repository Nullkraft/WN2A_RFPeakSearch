import numpy as np
#import serial       # requires 'pip install pyserial'


#float    Fvco, N, FracT
Fvco = 0.0000
# ulong     NI, registerNum, Reg(6,401), OldReg(6) ' Reg(6, 401) is Reg(registerNum, stepNumber). 6 registers;401 max frequency steps
# string    Swept, freq, ComStr, portNum, portSpeed, delaystr, FracOpt, LockDetect
# single    Fstart, Fstop
# single    Fpfd, refClock, RFOut, FvcoEst, FracErr, Frfv(401), Initial
# integer   delay, stepNumber, Verbose, oldVerbose ', Range
# integer   MOD1, Fracc, NewMOD1, NewFracc, numFreqs, Div, dispWidth, dispHeight

# Datarow1: 'For MAX2871 Initialization
dataRow1 = 13093080,541097977,1476465218,4160782339,1674572284,2151677957    # 374.596154 MHz with Lock Detect
# Datarow2: 'For MAX2871 Initialization, no LockDetect on Mux Line
dataRow2  = 13093080,541097977,1073812034,4160782339,1674572284,2151677957     # 374.596154 MHz without Lock Detect




## Eventually the serial port settings will be selected from the main menu of the gui.
#def serialPort(port=None, baudrate=None):
#    # Remove these defaults later and replace with values entered by the user
#    # from the GUI or assert that the user needs to select a device and speed.
##    device = '/dev/ttyACM0' # Default serial port device
#    device = '/dev/ttyUSB0' # Default serial port device
##    speed = 2_000_000       # Default serial port speed
#    speed = 9600       # Default serial port speed
#    
#    if port != None:        # Set a user defined serial port
#        device = port
#    if baudrate != None:    # Set a user defined port speed
#        speed = baudrate
#    
#    serDevice = serial.Serial(device, speed, timeout=100/speed)
#    return serDevice

#
#
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
            
    transmissionDelay = delay
    freq = frequency
#    Fstart = ?
#    Fstop = ?
#    numFreqs = ?
    
    if swept == True:
        Sweep(Fstart, Fstop, numFreqs)        # Timer triggers sweep after sweep?
    else:
        newFreq(freq)

#
#

def xmit():
    pass


def set_frequency():
    rfOut = 23.5
    stepNumber = 0
    refClock = 60
    initialized = False
    oldChipRegisters = [0, 0, 0, 0, 0, 0]

    # Calculate and store a new set of register values used for
    # programming the MAX2871 chip with a new output frequency.
    registers = new_frequency_registers(rfOut, stepNumber, refClock)

    # According to the spec-sheet the MAX2871 chip requires initialization
    # by sending a set of registers values twice with a >20ms delay between
    # writes. My testing shows that this is not necessary and if Maxim
    # engineers agree then I will remove the initialization code.
    #
    # The normal method of programming the chip is to start with the
    # highest register first and work your way down loading each one
    # after the other.
    if not initialized:
        # registers values stored in reverse order for later comparison.
        oldChipRegisters = registers[::-1]
        initialized = True
        print("mainWindow:109 - initializing")  # DelMe: Status information
        # Write all 6 registers to the MAX2871 chip
        for reg in registers[::-1]:
            ser.write(reg.to_bytes(4, 'big'))
        time.sleep(0.025)                       # Minimium 20 millisec delay
        # Write all 6 registers to the MAX2871 chip again...
        for reg in registers[::-1]:
            ser.write(reg.to_bytes(4, 'big'))
    else:
        # DelMe: Status information
        print("mainWindow:119 - ", oldChipRegisters, registers)
        for x, reg in enumerate(registers[::-1]):
            # It's only necessary to write to a register if its value
            # has changed since the last time the chip was programmed.
            if reg != oldChipRegisters[x]:
                ser.write(reg.to_bytes(4, 'big'))
                oldChipRegisters[x] = reg

def new_frequency_registers(newFreq, stepNumber=0, refClock=60, FracOpt=None, LockDetect="y"):
    if newFreq < 23.5:
        frequency_out = 23.5
    elif newFreq > 6000:
        frequency_out = 6000
    else:
        frequency_out = newFreq
        
    refClockDivider = 4
    Fpfd = (refClock * (1e6)) / refClockDivider    # Default Fpfd = 15 MHz
    rangeNum = 0
    Div = 1
    Reg = list(range(6)), list(range(402))
    
    while (frequency_out*Div) < 3000:
        rangeNum += 1           # Divider Range still not found.
        Div = 2**rangeNum       # Next Divider Range
    else:
        Range = rangeNum
        Fvco = frequency_out * Div
        N = 1e6 * (Fvco/(Fpfd))
        NI = int(N)
        FracT = N - NI

        if FracOpt != "f":      # Only run these lines if the user selected Fractional Optimization
            MOD1 = 4095
            Fracc = int(FracT * MOD1)

        # restore Datarow1 'Restore Data Pointer 1 unless...
        if LockDetect == "y":
            dataRow = dataRow1
        else:
            dataRow = dataRow2

        Reg[stepNumber][0] = (NI * (2**15)) + (Fracc * (2**3))
        Reg[stepNumber][1] = (2**29) + (2**15) + (MOD1*(2**3)) + 1
        Reg[stepNumber][2] = dataRow[2]
        Reg[stepNumber][3] = dataRow[3]
        Reg[stepNumber][4] = 1670377980 + ((2**20) * Range)
        Reg[stepNumber][5] = dataRow[5]

        # 
        return Reg[stepNumber]
    
    
    

def Sweep():
    pass
    



# By ordering just the amplitudeData array indexes the results can be used
# to position as many markers as you would like from highest to lowest peaks.
def peakSearch(amplitudeData, numPeaks):
    amp = np.asarray(amplitudeData)         # 
    idx = amp.argsort()[::-1][:numPeaks]    # New amplitude index array sorted by descending amplitude
    idx = np.resize(idx, (numPeaks, 1))     # Truncate array to number of desired peak markers
    idx = list(map(int, idx))               # pyqtgraph.marker(s) requires a list of integers
    return(idx)                             # Return list of descending amplitude indexes
    
# End function peakSearch







