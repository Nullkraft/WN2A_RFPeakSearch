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
    global ser
    global _baud
    read_serial_config()    # Preset _baud and _port from config file
    _baud = speed           # Set a new _baud rate
    write_serial_config(_baud, _port)
    port_open()

def set_port(selected_port):
    global ser
    global _port
    read_serial_config()    # Preset _baud and _port from config file
    _port = selected_port   # Set a new _port
    write_serial_config(_baud, _port)
    port_open()

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
    ser_port = None
    read_serial_config()
    try:
        ser_port = serial.Serial(_port, _baud, timeout=100/int(_baud))
    except OSError as e:
        if e.errno == error.EBUSY:
            print(name, line(), ": Another program has already opened the port. Arduino?")
#        print(name, line(), ": OSError e =", e.errno, e.strerror)
    except Exception as e:
        print(name, line(), e)
    else:
        # Give the serial port a moment to open
        time.sleep(0.2)
        print(name, line(), f': {ser_port.port}, {ser_port.baudrate}')
    finally:
        ser = ser_port


def write_serial_config(speed=None, port=None):
    config = configparser.ConfigParser()
    config['DEFAULT'] = {'baud_rate': '9600', 'serial_port': '/dev/ttyUSB0'}
    config['Last.opened'] = {}

    # Prepare the baud_rate and serial_port settings to be written to the config file.
    if speed != None:
        config['Last.opened']['baud_rate'] = str(speed)
    if port != None:
        config['Last.opened']['serial_port'] = port

    try:
        with open('serial.conf', 'w') as config_file:
            config.write(config_file)
    except PermissionError as err:
        print(name, line(), f': Can\'t write to the file, {err.filename}')


def read_serial_config():
    global _port
    global _baud
    file_name = 'serial.conf'
    config = configparser.ConfigParser()
    config.read(file_name)

    # Load port and speed from the serial.conf file.
    try:
        _port = config['Last.opened']['serial_port']
        _baud = config['Last.opened'].getint('baud_rate')
    except KeyError as err:
        if os.path.isfile(file_name):
            print(name, line(), f': The key {err} was not assigned a value.')
        else:
            print(name, line(), f': The file {file_name} is missing.')
    else:
        return [_port, _baud]




if __name__ == '__main__':
    print(list_os_ports())











