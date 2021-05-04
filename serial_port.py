# -*- coding: utf-8 -*-

from serial.tools import list_ports
import serial       # requires 'pip install pyserial'


serial_port = None      # Made this global for set_ and get_ to share
ser = None              # Made this global so it can be reached from anywhere


def set_serial_port(port):
    global serial_port
    global ser
    baud = 2000000
    ser = serial.Serial(port, baud, timeout=100/baud)
    print('sp:16 - serial port = ', ser.port)
    print('sp:17 - usable BAUDRATES = ', ser.BAUDRATES[12:])

def get_serial_port():
    return serial_port

def list_all_ports():
    com_list = []
    ports = list_ports.comports()
    for port in ports:
        com_list.append(port.device)
    return com_list




if __name__ == '__main__':
    print(list_all_ports())









