# -*- coding: utf-8 -*-

from serial.tools import list_ports
import serial       # requires 'pip install pyserial'

ser = None              # Made this global so it can be reached from anywhere
baud = None

# This function is called by the gui and is used to create a drop down
# for setting the serial speed.  It uses BAUDRATES, which is found in
# pySerial API, and is sliced so that the lowest speed is 9600 baud.
def get_baud_rates():
    return ser.BAUDRATES[12:]

def set_baud_rate(speed):
    global baud
    baud = speed

def set_serial_port(port):
    global ser
    if baud == None:
        rate = 2_000_000
    else:
        rate = int(baud)
    ser = serial.Serial(port, rate, timeout=100/rate)
    print(__name__, '26 :', ser.port, ser.baudrate)

def list_all_ports():
    com_list = []
    ports = list_ports.comports()
    for port in ports:
        com_list.append(port.device)
    return com_list




if __name__ == '__main__':
    print(list_all_ports())









