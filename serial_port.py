# -*- coding: utf-8 -*-

import serial       # requires 'pip3 install pyserial'
from serial.tools import list_ports

import time
import errno as error
import sys
import configparser
import os
from PyQt6.QtCore import QObject, pyqtSignal


# Utils to print filename and linenumber, print(name, line(), ...), when using print debugging.
line = lambda: f'line {str(sys._getframe(1).f_lineno)},'
name = f'File \"{__name__}.py\",'


# Serial port object that can be shared across source files.
ser = serial.Serial()


class simple_serial(QObject):
    """
    simple_serial will receive large amounts of data of a known size from the Arduino.
    """

    default_serial_speed = '9600'
    # Set the default serial port name based on the user's platform.
    if sys.platform == "linux" or sys.platform == "linux2":
        default_serial_port = '/dev/ttyUSB0'
    elif sys.platform == "darwin":
        default_serial_port = '/dev/ttyUSB0'
    elif sys.platform == "win32":
        default_serial_port = 'COM1'

    _baud = None
    _port = None
    config_fname = 'serial.conf'

    finished = pyqtSignal(bytearray)
    progress = pyqtSignal(int)

    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        self.end_of_record = bytearray([255, 255])  # Arduino A2D is only 10 bits so we can safely use 0xffff
        self._read_config()          # Preset _baud and _port from config file


    def get_serial_port_list(self):
        """
        Function get_serial_port_list()

        @return List of available serial ports from the local system.
        @rtype List
        """
        port_list = list()
        ports = list_ports.comports()
        for port in ports:
            port_list.append(port.device)
        return port_list


    def get_baud_rate_list(self):
        """
        Function get_baud_rate_list()

        @return Return the list of serial speeds starting at 9600 baud.
        @rtype Tuple
        """
        baud_rate_list = sorted(ser.BAUDRATES)          # Make sure the list of baud rates is in ascending order
        idx_9600_baud = baud_rate_list.index(9600)
        baud_rate_list = baud_rate_list[idx_9600_baud:] # Limit baud rate list to speeds starting from 9600 baud
        return baud_rate_list                     


    def set_serial_port_speed(self, selected_speed):
        self._baud = int(selected_speed)                # Set a new _baud rate
#        self._write_config(self._baud, self._port)      # Saves new baud rate to the config file.

    def set_port(self, selected_port):
        self._port = selected_port   # Set a new _port
#        self._write_config(self._baud, self._port)      # Saves new port to the config file.

    def port_open(self):
        global ser
        ser_port = None
        if not os.path.isfile(self.config_fname):    # If needed create a new default serial.conf
            self._write_config(self.default_serial_speed, self.default_serial_port)
        config_port = self._read_config()            # Get the port settings from the config file.
        active_ports = self.get_serial_port_list()   # Get a list of all the serial ports on this system.
        if config_port[0] in active_ports:
            selected_port = config_port[0]
            print(name, line(), f'selected config_port = {selected_port}')
        else:
            selected_port = active_ports[0]
            print(name, line(), f'selected active_port = {selected_port}')

        if selected_port != None:           # If our port is alive on this system then open it.
            try:
                ser_port = serial.Serial(selected_port, self._baud, timeout=100/int(self._baud))
                self._port = selected_port
            except OSError as e:
                if e.errno == error.EBUSY:
                    print(name, line(), ": Another program has already opened the port. Arduino?")
        #        print(name, line(), ": OSError e =", e.errno, e.strerror)
            except TypeError:
                print(name, line(), f': One of the lines in {self.config_fname} is messed up.')
                self._write_config(self.default_serial_speed, self.default_serial_port)     # Messed up serial.conf keys so recreate a default copy.
            else:
                time.sleep(0.2)                                 # Give the port a moment to finish opening.
                self._write_config(self._baud, self._port)      # Saves new settings to the config file.
                print(name, line(), f'{ser_port.port} opened at {ser_port.baudrate} baud.')
            finally:
                ser = ser_port
        else:
            print(name, line(), f'config_port[0], {config_port[0]}, is NOT in active_ports')


    def _write_config(self, speed=None, port=None):
        config = configparser.ConfigParser()
        # Build the config file heirarchy.
        config['DEFAULT'] = {}
        config['DEFAULT']['port_speed'] = self.default_serial_speed
        config['DEFAULT']['serial_port'] = self.default_serial_port
        config['Last.opened'] = {}
        config['Last.opened']['port_speed'] = str(speed)
        config['Last.opened']['serial_port'] = port
        try:
            with open(self.config_fname, 'w') as config_file:
                config.write(config_file)
        except PermissionError as err:
            print(name, line(), f': Can\'t write to {err.filename}')
        except AttributeError as err:
            print(name, line(), f': Unable to open one of the keys in {err.filename}')


    def _read_config(self):
        if os.path.isfile(self.config_fname):
            config = configparser.ConfigParser()
            config.read(self.config_fname)
            # Load port and speed from the serial.conf file.
            try:
                self._port = config['Last.opened']['serial_port']
                self._baud = config['Last.opened'].getint('port_speed')
            except KeyError as err:
                print(name, line(), f': Missing key {err} from {self.config_fname}.')
            else:
                return [self._port, self._baud]
        else:
            print(name, line(), f': Unable to read {self.config_fname}, file not found.')


    def read_serial(self):
        """
        Worker thread for streaming incoming serial data
        """
        serial_bytes = bytearray()       # Incoming serial buffer
        while True:
            serial_bytes += ser.read(ser.in_waiting)                    # Accumulate the data bytes
            end_of_data_bytes = serial_bytes.find(self.end_of_record)
            if end_of_data_bytes > 0:                                   # end-of-stream found
                self.finished.emit(serial_bytes[:end_of_data_bytes])    # slice off excess data bytes
                break


# End simple_serial() class




if __name__ == '__main__':
    print("")
    print(simple_serial().get_baud_rate_list())










