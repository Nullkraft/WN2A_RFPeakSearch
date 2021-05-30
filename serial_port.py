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

ser = serial.Serial()      # Object that can be shared across source files.
_baud = None     #
_port = None


# Provide a list of baudrates to populate the gui drop down.
def get_os_baudrates():
    return serial.Serial.BAUDRATES[12:] # Slice off anything slower than 9600


def set_speed(speed):
    global _baud
    read_serial_config()    # Preset _baud and _port from config file
    _baud = speed           # Set a new _baud rate
    _update_port()


def set_port(selected_port):
    global _port
    read_serial_config()    # Preset _baud and _port from config file
    _port = selected_port   # Set a new _port
    _update_port()


def _update_port():
    write_serial_config(_baud, _port)
    port_open()     # fkn dependency! port_open() *must* come after write_serial_config()


def get_speed():
    return _baud


def get_port():
    return _port


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
    ser_port = None
    file_name = 'serial.conf'
    if not os.path.isfile(file_name):
        write_serial_config()           # If needed create a default serial.conf
    port_config = read_serial_config()  # Get the port we want from the config file.
    active_ports = list_os_ports()      # List all the serial ports on this system.
    if port_config[0] in active_ports:  # Find out if the port we want is actually alive.
        print(name, line(), f': {_port} was found in the list {active_ports}')
        try:
            ser_port = serial.Serial(_port, _baud, timeout=100/int(_baud))
        except OSError as e:
            if e.errno == error.EBUSY:
                print(name, line(), ": Another program has already opened the port. Arduino?")
    #        print(name, line(), ": OSError e =", e.errno, e.strerror)
        except TypeError:
            print(name, line(), f': Missing or invalid key-value pair in {file_name}.')
            write_serial_config()   # Someone messed up our serial.conf keys so create a default copy.
        else:
            time.sleep(0.2)        # The serial port needs a moment before calling ser_port.port, etc.
            print(name, line(), f': {ser_port.port} opened at {ser_port.baudrate} baud.')
        finally:
            ser = ser_port


def write_serial_config(speed=9600, port='/dev/ttyUSB0'):
    config = configparser.ConfigParser()
    # Build the config file heirarchy and include some preset values
    config['DEFAULT'] = {'port_speed': '9600', 'serial_port': '/dev/ttyUSB0'}
    config['Last.opened'] = {}
    config['Last.opened']['port_speed'] = str(speed)
    config['Last.opened']['serial_port'] = port

    try:
        with open('serial.conf', 'w') as config_file:
            config.write(config_file)
    except PermissionError as err:
        print(name, line(), f': Can\'t write to the file, {err.filename}')
    except AttributeError as err:
        print(name, line(), f': Unable to open one of the keys in {err.filename}')


def read_serial_config():
    global _port
    global _baud
    file_name = 'serial.conf'
    if os.path.isfile(file_name):
        config = configparser.ConfigParser()
        config.read(file_name)
        # Load port and speed from the serial.conf file.
        try:
            _port = config['Last.opened']['serial_port']
            _baud = config['Last.opened'].getint('port_speed')
        except KeyError as err:
            print(name, line(), f': Missing key {err} from {file_name}.')
        else:
            return [_port, _baud]

    else:
        print(name, line(), f': Unable to read {file_name}, file not found.')




if __name__ == '__main__':
    print(list_os_ports())











