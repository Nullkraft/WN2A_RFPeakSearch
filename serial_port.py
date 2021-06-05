# -*- coding: utf-8 -*-

from serial.tools import list_ports
import serial       # requires 'pip3 install pyserial'

import time
import errno as error
import sys
import configparser
import os

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




if __name__ == '__main__':
    print(list_os_ports())











