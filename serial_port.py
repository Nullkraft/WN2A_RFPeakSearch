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
    simple_serial is used to receive large amounts of data of a given bit width from the Arduino.
    """
    finished = pyqtSignal(bytearray)
    progress = pyqtSignal(int)


    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        self.end_of_record = bytearray([255, 255])  # Arduino A2D is only 10 bits so we can safely use 0xffff
        self.minimum_baud_rate = 9600
        self.config_fname = 'serial.conf'
        self.default_serial_speed = '9600'
        # Set the default serial port name based on the user's platform.
        if sys.platform == "linux" or sys.platform == "linux2":
            self.default_serial_port = '/dev/ttyUSB0'
        elif sys.platform == "darwin":
            self.default_serial_port = '/dev/ttyUSB0'
        elif sys.platform == "win32":
            self.default_serial_port = 'COM1'


    def get_serial_port_list(self):
        """
        Function get_serial_port_list()

        @return List of available serial ports for the local system.
        @rtype List
        """
        port_list = [port.device for port in list_ports.comports()]
        return port_list


    def get_baud_rate_list(self):
        """
        Function get_baud_rate_list()

        @return Return the list of serial speeds starting with minimum_baud_rate.
        @rtype Tuple
        """
        baud_rate_list = sorted(ser.BAUDRATES)              # List baud rates in ascending order
        idx_minimum_baud = baud_rate_list.index(self.minimum_baud_rate)
        baud_rate_list = baud_rate_list[idx_minimum_baud:]  # Rewrite the list starting from the minimum baud
        return baud_rate_list                     


    def port_open(self, baud_rate=None, port=None):
        global ser
        self.port = port
        self.baud = baud_rate
        # Check for serial config file and create a new one, using default values, if it's missing
        if not os.path.isfile(self.config_fname):    # If needed create a new default serial.conf
            self._write_config(self.default_serial_speed, self.default_serial_port)
        # Get the port settings from the config file.
        last_open_port = self.read_config()
        if self.port is None:
            self.port = last_open_port[0]
        if self.baud is None:
            self.baud = last_open_port[1]
        # Get the list of all serial ports on this system.
        active_ports_list = self.get_serial_port_list()
        if self.port in active_ports_list:
            try:
                ser_port = serial.Serial(self.port, self.baud, timeout=100/int(self.baud))
            except OSError as e:
                if e.errno == error.EBUSY:
                    print(name, line(), f': {self.port} has already been opened by another program. Arduino?')
            except TypeError:
                print(name, line(), f': {self.config_fname} is corrupt. New default file created.')
                self._write_config(self.default_serial_speed, self.default_serial_port)     # Corrupted file contents so recreate a default.
            else:
                time.sleep(0.2)                                 # Give the port a moment to finish opening.
                print(name, line(), f'{ser_port.port} opened at {ser_port.baudrate} baud.')
            finally:
                ser = ser_port
                self._write_config(current_speed=self.baud, current_port=self.port)
        else:
            print(name, line(), 'No serial ports found')


    def _write_config(self, current_speed=None, current_port=None):
        config = configparser.ConfigParser()
        # Build the config file heirarchy.
        config['Last.opened'] = {}
        config['Last.opened']['port_speed'] = str(current_speed)
        config['Last.opened']['serial_port'] = current_port
        try:
            with open(self.config_fname, 'w') as config_file:
                config.write(config_file)
        except PermissionError as err:
            print(name, line(), f': Can\'t write to {err.filename}')
        except AttributeError as err:
            print(name, line(), f': Unable to open one of the keys in {err.filename}')


    def read_config(self):
        if os.path.isfile(self.config_fname):
            config = configparser.ConfigParser()
            config.read(self.config_fname)
            # Load port and speed from the serial.conf file.
            try:
                port = config['Last.opened']['serial_port']
                baud = config['Last.opened'].getint('port_speed')
            except KeyError as err:
                print(name, line(), f': Missing key {err} from {self.config_fname}.')
            else:
                return [port, baud]
        else:
            print(name, line(), f': Unable to read {self.config_fname}, file not found.')


    def read_serial(self):
        """
        Worker thread for collecting incoming serial data
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
    print(simple_serial().get_serial_port_list())










