from serial.tools import list_ports
import serial       # requires 'pip install pyserial'
import time


# Functions specific to the operation of the WN2A Spectrum Analyzer hardware, hopefully.
# Including setting up the serial port.
import spectrumAnalyzer as sa


# Eventually the serial port settings will be selected from the main menu of the gui.
def serialPort(port=None, baudrate=None):
    # Remove these defaults later and replace with values entered by the user
    # from the GUI or assert that the user needs to select a device and speed.
#    device = '/dev/ttyACM0' # Default serial port device
    device = '/dev/ttyUSB0' # Default serial port device
#    speed = 2_000_000       # Default serial port speed
    speed = 9600       # Default serial port speed

    if port != None:        # Set a user defined serial port
        device = port
    if baudrate != None:    # Set a user defined port speed
        speed = baudrate

    serDevice = serial.Serial(device, speed, timeout=100/speed)
    return serDevice


# Let's create the default serial port with /dev/ttyUSB0 and 2Mbs
#ser = serialPort(port='/dev/ttyACM0', baudrate=9600)
ser = serialPort(port='/dev/ttyACM0', baudrate=2000000)


def write_registers(target_frequency, ref_clock, initialized = False):
    rfOut = target_frequency
    refClock = ref_clock
    stepNumber = 0
    oldChipRegisters = [0, 0, 0, 0, 0, 0]


    # Calculate and store a new set of register values used for
    # programming the MAX2871 chip with a new output frequency.
    registers = sa.new_frequency_registers(rfOut, stepNumber, refClock)

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
        # Write all 6 registers to the MAX2871 chip
        ser.write(b'b')
        for reg in registers[::-1]:
            ser.write(reg.to_bytes(4, 'big'))
        time.sleep(0.025)                       # Minimium 20 millisec delay
        # Write all 6 registers to the MAX2871 chip again...
        ser.write(b'b')
        for reg in registers[::-1]:
            ser.write(reg.to_bytes(4, 'big'))
    else:
        # DelMe: Status information
        ser.write(b'b')
        for x, reg in enumerate(registers[::-1]):
            # It's only necessary to write to a register if its value
            # has changed from one frequency to the next.
            if reg != oldChipRegisters[x]:
                ser.write(reg.to_bytes(4, 'big'))
                oldChipRegisters[x] = reg


def list_all_ports():
    com_list = []
    ports = list_ports.comports()
    for port in ports:
        com_list.append(port.device)
    return com_list


if __name__ == '__main__':
    print(list_all_ports())









