# -*- coding: utf-8 -*-

from serial.tools import list_ports
import serial       # requires 'pip install pyserial'

import sys
line = lambda : sys._getframe(1).f_lineno
name = lambda : __name__

ser = None      # global so it can be shared across files.
_baud = None     #
_port = None

# Provide a list of baudrates to populate the gui drop down.
# It is sliced so that the lowest speed is at 9600 baud.
def get_baud_rates():
    return serial.Serial.BAUDRATES[12:]

def set_baudrate(speed):
    global _baud
    _baud = speed

def set_serial_port(selected_port):
    global ser
    global _port
    if selected_port != None:
        _port = selected_port
        ser = _open()
    print(name(), line(), ':', ser.port, ser.baudrate)

def list_all_ports():
    com_list = []
    ports = list_ports.comports()
    for port in ports:
        com_list.append(port.device)
    return com_list

def _open():
    ser_port = serial.Serial(_port, _baud, timeout=100/int(_baud))
    return ser_port


if __name__ == '__main__':
    print(list_all_ports())









