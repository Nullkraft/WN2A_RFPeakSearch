# -*- coding: utf-8 -*-

from serial.tools import list_ports
import serial       # requires 'pip3 install pyserial'

import time
import errno as error
import sys
import configparser
import os
from PyQt5.QtCore import QObject, pyqtSignal


# Utils to print filename and linenumber, print(name, line(), ...), when using print debugging.
line = lambda : sys._getframe(1).f_lineno
name = __name__



# Set the default serial port name based on the user's platform.
if sys.platform == "linux" or sys.platform == "linux2":
    default_serial_port = '/dev/ttyUSB0'
elif sys.platform == "darwin":
    default_serial_port = '/dev/ttyUSB0'
elif sys.platform == "win32":
    default_serial_port = 'COM1'

default_serial_speed = '9600'
config_fname = 'serial.conf'

# Serial port object that can be shared across source files.
ser = serial.Serial()

_baud = None    # Current port speed being used by the system.
_port = None    # Current serial port being used by the system.


# Reports the list of baudrates available to this platform.
def get_os_baudrates():
    return serial.Serial.BAUDRATES[12:] # Slice off anything slower than 9600


def set_speed(selected_speed):
    global _baud
    read_config()    # Preset _baud and _port from config file
    _baud = selected_speed  # Set a new _baud rate
    _update_port()          # Open the port at the new speed and save it to the config


def set_port(selected_port):
    global _port
    read_config()    # Preset _baud and _port from config file
    _port = selected_port   # Set a new _port
    _update_port()          # Open the new port and save it to the config


def _update_port():
    write_config(_baud, _port)   # Saves new settings to the config file.
    port_open()                         # Re-opens the port using the new config file settings.


def list_os_ports():
    com_list = []
    ports = list_ports.comports()
    for port in ports:
        com_list.append(port.device)
    return com_list


def port_open():
    global ser
    global _baud
    global _port
    global config_fname
    ser_port = None
    if not os.path.isfile(config_fname):    # If needed create a new default serial.conf
        write_config()
    port_config = read_config()      # Get the port settings from the config file.
    active_ports = list_os_ports()          # Get a list of all the serial ports on this system.
    if port_config[0] in active_ports:      # If our port is alive on this system then open it.
        try:
            ser_port = serial.Serial(_port, _baud, timeout=100/int(_baud))
        except OSError as e:
            if e.errno == error.EBUSY:
                print(name, line(), ": Another program has already opened the port. Arduino?")
    #        print(name, line(), ": OSError e =", e.errno, e.strerror)
        except TypeError:
            print(name, line(), f': Missing or invalid key-value pair in {config_fname}.')
            write_config()   # Someone messed up our serial.conf keys so create a default copy.
        else:
            time.sleep(0.2)         # Give the port a moment to finish opening.
            print(name, line(), f': {ser_port.port} opened at {ser_port.baudrate} baud.')
        finally:
            ser = ser_port


def write_config(speed=default_serial_speed, port=default_serial_port):
    global config_fname
    config = configparser.ConfigParser()
    # Build the config file heirarchy.
    config['DEFAULT'] = {}
    config['DEFAULT']['port_speed'] = default_serial_speed
    config['DEFAULT']['serial_port'] = default_serial_port
    config['Last.opened'] = {}
    config['Last.opened']['port_speed'] = str(speed)
    config['Last.opened']['serial_port'] = port
    try:
        with open(config_fname, 'w') as config_file:
            config.write(config_file)
    except PermissionError as err:
        print(name, line(), f': Can\'t write to {err.filename}')
    except AttributeError as err:
        print(name, line(), f': Unable to open one of the keys in {err.filename}')


def read_config():
    global _port
    global _baud
    global config_fname
    if os.path.isfile(config_fname):
        config = configparser.ConfigParser()
        config.read(config_fname)
        # Load port and speed from the serial.conf file.
        try:
            _port = config['Last.opened']['serial_port']
            _baud = config['Last.opened'].getint('port_speed')
        except KeyError as err:
            print(name, line(), f': Missing key {err} from {config_fname}.')
        else:
            return [_port, _baud]
    else:
        print(name, line(), f': Unable to read {config_fname}, file not found.')







# serialWorker is for receiving large amounts of data of a known size from the Arduino.
class serialWorker(QObject):
    # signals
    finished = pyqtSignal(bytearray)
    progress = pyqtSignal(int)

    def __init__(self, numPoints, parent=None):
        QObject.__init__(self, parent)
        self.numDataPoints = numPoints

    def run(self):
        self.amplDataBytes = bytearray()                    # Store 8bit data from Arduino
        command = self.__cmd(self.numDataPoints)            # Command to send to Arduino
        ser.write(command)                               # Send command to the Arduino
        # Read response as raw bytes from the Arduino.
        while True:
            bytesToRead = ser.in_waiting
            self.amplDataBytes += ser.read(bytesToRead)
            reversed_data = self.amplDataBytes[::-1]        # Reverse list before searching
            array_position = reversed_data.find(255)        # Find the FIRST 0xFF (or 255)
            if list(reversed_data[array_position:array_position+2]) == [255, 255]:     # end-of-record found
                self.amplDataBytes = reversed_data[array_position:]
                self.amplDataBytes = self.amplDataBytes[::-1]
                break
        self.finished.emit(self.amplDataBytes)              # Return the Amplitude Array

    # The Arduino will only simulate a fixed number of RF data points.
    def __cmd(self, numPoints):
        # The Arduino sees 1=256*16bits 2=512 3=768 4=1024 5=1280 (6 or greater)=1536
        arduinoCmds = [b'1', b'2', b'3', b'4', b'5', b'6']
        selection = numPoints // 256 - 1                # selection = floor(numPoints/256)-1
        selection = 5 if selection > 5 else selection
        return arduinoCmds[selection]

# End serialWorker() class







if __name__ == '__main__':
    print(list_os_ports())











