# -*- coding: utf-8 -*-
#
# This file is part of WN2A_RFPeakSearch.
# 
# This file is part of the WN2A_RFPeakSearch distribution (https://github.com/Nullkraft/WN2A_RFPeakSearch).
# Copyright (c) 2021 Mark Stanley.
# 
# WN2A_RFPeakSearch is free software: you can redistribute it and/or modify  
# it under the terms of the GNU General Public License as published by  
# the Free Software Foundation, version 3.
#
# WN2A_RFPeakSearch is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU 
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License 
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

# Use these functions in all your print statements to display the filename 
# and the line number of the source file. Requires: import sys
name = lambda: f"File \'{__name__}.py\',"
line = lambda: f"line {str(sys._getframe(1).f_lineno)},"


import errno as error
import sys
import os
import serial  # 'pip3 install pyserial'.   https://pyserial.readthedocs.io/en/latest/pyserial_api.html
from serial.tools import list_ports
import configparser
from PyQt6.QtCore import QObject, pyqtSignal

# Serial port object that can be shared across source files.
""" NOTE: Investigate to see if we can used Dependency inversion
    to move this serial object outside the SimpleSerial class.
  
    1. Make SimpleSerial independent of the comms channel, eg. it
       could be serial, ethernet or even GPIB.
  
    2. YouTube Tutorial - Dependency INVERSION vs dependency INJECTION
       https://www.youtube.com/watch?v=2ejbLVkCndI
"""
ser = serial.Serial()

class SimpleSerial(QObject):
  finished = pyqtSignal(bytearray)
  progress = pyqtSignal(int)
  data_buffer_in = bytearray()       # Incoming serial buffer


  def __init__(self, parent=None):
#    super().__init__(parent)      # This is causing a segfault on exit from interpreter
    QObject.__init__(self, parent)
#    self.data_buffer_in = bytearray()       # Incoming serial buffer
    self.end_of_stream = bytearray([255, 255])  # Arduino A2D is only 10 bits so we can safely use 0xffff
    self.config_fname = 'serial.conf'
    self.default_serial_speed = '9600'
    # Set the default serial port name based on the user's platform.
    if sys.platform == "linux" or sys.platform == "linux2":
      self.default_serial_port = '/dev/ttyUSB0'
    elif sys.platform == "darwin":
      self.default_serial_port = '/dev/ttyUSB0'
    elif sys.platform == "win32":
      self.default_serial_port = 'COM1'

  @staticmethod
  def get_serial_port_list():
    """
    Function get_serial_port_list()

    @return List of available serial ports for the local system.
    @rtype List
    """
    serial_port_list = [serial_port.device for serial_port in list_ports.comports()]
    return serial_port_list

  @staticmethod
  def get_baud_rate_list(minimum_baud_rate=9600):
    """
    Function get_baud_rate_list()

    @return Return the list of serial speeds starting with minimum_baud_rate.
    @rtype Tuple
    """
    baud_rate_list = sorted(ser.BAUDRATES)        # List baud rates in ascending order
    idx_minimum_baud = baud_rate_list.index(minimum_baud_rate)
    baud_rate_list = baud_rate_list[idx_minimum_baud:]  # Rewrite the list starting from the minimum baud
    return baud_rate_list           

  def port_open(self, baud_rate=None, port=None):
    global ser
    self.port = port
    self.baud = baud_rate
    # Check for serial config file and create a new one, using default values, if it's missing
    if not os.path.isfile(self.config_fname):  # If needed create a new default serial.conf
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
        """ TODO: Move the serial object creation to the __init__ function above
          using the method of Dependency Injection found here:
            https://youtu.be/2ejbLVkCndI?t=434
          See also:
            https://pyserial.readthedocs.io/en/latest/shortintro.html#configuring-ports-later
        """
        ser_port = serial.Serial(self.port, self.baud, timeout=100/int(self.baud))
      except OSError as e:
        if e.errno == error.EBUSY:
          print(name(), line(), f': {self.port} has already been opened by another program. Arduino?')
          ser_port = None
      except TypeError:
        print(name(), line(), f': {self.config_fname} is corrupt. New default file created.')
        self._write_config(self.default_serial_speed, self.default_serial_port)   # Corrupted file contents so recreate a default.
      else:
        print(name(), line(), f'INFO::{ser_port.port} opened at {ser_port.baudrate} baud.')
      finally:
        if ser_port is not None:
          ser = ser_port
          self._write_config(current_speed=self.baud, current_port=self.port)
    else:
      print(name(), line(), 'No serial ports found')


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
      print(name(), line(), f': Can\'t write to {err.filename}')
    except AttributeError as err:
      print(name(), line(), f': Unable to open one of the keys in {err.filename}')


  def read_config(self):
    if os.path.isfile(self.config_fname):
      config = configparser.ConfigParser()
      config.read(self.config_fname)
      # Load port and speed from the serial.conf file.
      try:
        port = config['Last.opened']['serial_port']
        baud = config['Last.opened'].getint('port_speed')
      except KeyError as err:
        print(name(), line(), f': Missing key {err} from {self.config_fname}.')
      else:
        return [port, baud]
    else:
      print(name(), line(), f': Unable to read {self.config_fname}, file not found.')

  def read(self, num_bytes: int=1):
    return ser.read(num_bytes)

  def write(self, data_buf):
    ser.write(data_buf.to_bytes(4, 'little'))


# End SimpleSerial() class



# Dependency Injection video
# https://www.youtube.com/watch?v=-ghD-XjjO2g&t=622s

""" Dependency Inversion would remove the responsibility of open_port()
    from creating and opening the serial port object. """
# Dependency inversion: write BETTER PYTHON CODE
# https://www.youtube.com/watch?v=Kv5jhbSkqLE



if __name__ == '__main__':
  print("")
  print(SimpleSerial().get_baud_rate_list())
  print(SimpleSerial().get_serial_port_list())










