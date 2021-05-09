# -*- coding: utf-8 -*-

from serial.tools import list_ports
import serial       # requires 'pip3 install pyserial'
import time

import sys
line = lambda : sys._getframe(1).f_lineno
name = __name__

ser = None      # global so it can be shared across files.
_baud = None     #
_port = None

# Provide a list of baudrates to populate the gui drop down.
# It is sliced so that the lowest speed is at 9600 baud.
def get_os_baudrates():
    return serial.Serial.BAUDRATES[12:]

def set_speed(speed):
    global ser
    global _baud
    _baud = speed
    if get_port() != None:
        ser = _open()

def set_port(selected_port):
    global ser
    global _port
    _port = selected_port
    if get_speed() != None:
        ser = _open()

def get_speed():
    return _baud

def get_port():
    return _port

def set_serial_port(selected_port):
    global ser
    global _port

def list_os_ports():
    com_list = []
    ports = list_ports.comports()
    for port in ports:
        com_list.append(port.device)
    return com_list

def _open():
    ser_port = serial.Serial(_port, _baud, timeout=100/int(_baud))
    # Give the serial port a moment to open
    time.sleep(0.5)
    print(name, line(), ':', ser_port.port, ser_port.baudrate)
    return ser_port


if __name__ == '__main__':
    print(list_os_ports())









