# -*- coding: utf-8 -*-
#
# This file is part of WN2A_RFPeakSearch.
#
# This file is part of the WN2A_RFPeakSearch distribution
# (https://github.com/Nullkraft/WN2A_RFPeakSearch).
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


import serial_port as sp
import sys
import time
import logging


class CmdProcInterface():
  def __init__(self):
    # Arduino and Device Commands
    self.attenuator_sel    = 0x00FF   # Attenuates the RFinput from 0 to 31.75dB

    self.LO1_device_sel    = 0x01FF   # Select device before sending a General Command
    self.LO1_RF_off        = 0x09FF   # Specific commands
    self.LO1_neg4dBm       = 0x11FF   # Change power and num freq steps
    self.LO1_neg1dBm       = 0x19FF   #     .
    self.LO1_pos2dBm       = 0x21FF   #     .
    self.LO1_pos5dBm       = 0x29FF   #     .
    self.LO1_no_change     = 0x31FF   # Select LO1 without changing the RF output power level
    self.LO1_mux_tristate  = 0x39FF   # Disable or rather set tristate on the mux pin
    self.LO1_mux_dig_lock  = 0x41FF   # Enable digital lock detect on the mux pin

    self.LO2_device_sel    = 0x02FF   # Select device before sending a General Command
    self.LO2_RF_off        = 0x0AFF   # Specific commands
    self.LO2_neg4dBm       = 0x12FF   # Change power and num freq steps
    self.LO2_neg1dBm       = 0x1AFF   #     .
    self.LO2_pos2dBm       = 0x22FF   #     .
    self.LO2_pos5dBm       = 0x2AFF   #     .
    self.LO2_num_steps     = 0x32FF   # Change num freq steps only
    self.LO2_mux_tristate  = 0x3AFF   # Set tristate on the mux pin
    self.LO2_mux_dig_lock  = 0x42FF   # Enable digital lock detect on the mux pin
    self.LO2_divider_mode  = 0x4AFF   # Set the RFOut Output Divider Mode to 1, 2, 4, 8, 16, 32, 64, or 128

    self.LO3_device_sel    = 0x03FF   # Select device before sending a General Command
    self.LO3_RF_off        = 0x0BFF   # Specific commands
    self.LO3_neg4dBm       = 0x13FF   # Change power and num freq steps
    self.LO3_neg1dBm       = 0x1BFF   #     .
    self.LO3_pos2dBm       = 0x23FF   #     .
    self.LO3_pos5dBm       = 0x2BFF   #     .
    self.LO3_num_steps     = 0x33FF   # Change num freq steps only
    self.LO3_mux_tristate  = 0x3BFF   # Set tristate on the mux pin
    self.LO3_mux_dig_lock  = 0x43FF   # Enable digital lock detect on the mux pin
    self.LO3_divider_mode  = 0x4BFF   # Set the RFOut Output Divider Mode to 1, 2, 4, 8, 16, 32, 64, or 128

    # Reference clock Device Commands
    self.all_ref_disable   = 0x04FF
    self.ref_clock1_enable = 0x0CFF   # Enables 66.000 MHz reference and disables 66.666 MHz reference
    self.ref_clock2_enable = 0x14FF   # Enables 66.666 MHz reference and disables 66.000 MHz reference

    # Arduino status
    self.Arduino_LED_off   = 0x07FF
    self.Arduino_LED_on    = 0x0FFF   # LED blink test - The 'Hello World' of embedded dev
    self.version_message   = 0x17FF   # Query Arduino type and Software version
    self.sweep_start       = 0x1FFF   # Serial communication flow control
    self.sweep_end         = 0x27FF   # Tell the Arduino that all data has been sent
    self.reset_and_report  = 0x2FFF   # Reset the Spectrum Analyzer to default settings


class CommandProcessor(CmdProcInterface):

  # Attenuator Command & Control
  def set_attenuator(self, decibels: float = 31.75) -> None:
    """
    Function Attenuate the RFin signal from 0 to 31.75 dB. From the
    spec-sheet: To get the binary value for programming the register
    multiply the target dB attenuation by 4.
    Ex. 12.5 dB * 4 = 50 binary
    The 16 bit left shift moves the result to the 2 high bytes so
    the controller can decode it as Data.

    @param decibels DESCRIPTION (defaults to 31.75)
    @type float (optional)
    @return No return type
    @rtype None

    """
    level = int(decibels * 4) << 16
    self._send_command(level | self.attenuator_sel)


  def set_max2871_freq(self, fmn: int) -> None:
    """
    Function Set LO2 or LO3 to a new frequency.

    @param fmn is the F, M, and N values used to set the frequency.
    @type int

    """
    self._send_command(fmn)


  def disable_LO2_RFout(self) -> None:
    """Function LO2 Command and Control."""
    self._send_command(self.LO2_RF_off)


  def disable_LO3_RFout(self) -> None:
    """LO3 Command & Control."""
    self._send_command(self.LO3_RF_off)

  
  def sel_LO1(self) -> None:
    """Send command to select the LO1 chip for programming."""
    self._send_command(self.LO1_device_sel)


  def set_LO1(self, LO1_command: int, int_N: int = 54) -> None:
    """
    Function Set the LO1 chip to a new frequency.

    @param LO1_command (Choose one from the list of "Arduino and Device Commands" above)
    @type int_32
    @param int_N LO1, LO2, or LO3 control code (defaults to None)
    @type int (optional)

    """
    if int_N is not None:
      if (53 <= int_N <= 102):
        N = int_N << 16
      else:
        logging.error(f'{name}, {line()}, N ({int_N}) exceeds the limits of the ADF4356 (LO1)')
    else:
      N = 0
    self._send_command(LO1_command | N)


  def sel_LO2(self) -> None:
    """Send command to select the LO2 chip for programming."""
    self._send_command(self.LO2_device_sel)


  def set_LO2(self, LO2_command: int) -> None:
    """Send the command to set the LO2 chip to a new frequency."""
    self._send_command(LO2_command)


  def sel_LO3(self) -> None:
    """Send command to select the LO2 chip for programming."""
    self._send_command(self.LO3_device_sel)


  def set_LO3(self, LO3_command) -> None:
    """Send the command to set the LO3 chip to a new frequency."""
    self._send_command(LO3_command)


  def LO_device_register(self, device_command: int) -> None:
    """
    Function LO_device_register.

    @param device_command FMN data (LO2/LO3) or N data (LO1) for direct device control
    @type TYPE

    """
    self._send_command(device_command)


  def LED_on(self) -> None:
    """Command for testing communication with the controller board."""
    self._send_command(self.Arduino_LED_on)
    self.show_message()


  def LED_off(self) -> None:
    """Command for testing communication with the controller board."""
    self._send_command(self.Arduino_LED_off)
    self.show_message()


  def show_message(self) -> str:
    """ Get the last message string that was sent from the controller. """
    sp.ser.read(sp.ser.in_waiting)  # Clear serial buffer of any junk
    time.sleep(0.01)
    msg = sp.ser.read(64)           # Collect the report(s)
    if msg:
      print(name(), line(), f'Arduino message = {msg}')


  def get_version_message(self):
    """ Get the firmaware version string from the controller. """
    self._send_command(self.version_message)  # Request software report from controller
    self.show_message()


#  def get_version_message(self) -> str:
#    """
#    Get the firmaware version string from the controller.
#
#    @return str
#
#    """
#    sp.ser.read(sp.ser.in_waiting)  # Clear out the serial buffer.
#    self._send_command(self.version_message)  # Request software report from controller
#    time.sleep(0.01)
#    return sp.ser.read(64)      # Collect the report(s)
#
#
  def disable_all_ref_clocks(self) -> None:
    """Disable both reference clocks for testing."""
    self._send_command(self.all_ref_disable)


  def enable_ref_clock(self, ref_clock_command) -> None:
    """Turn on the selected reference clock. The controller automatically turns off the other."""
    self._send_command(ref_clock_command)


  def end_sweep(self) -> None:
    """Serial data stream stop command when done sweeping LO2 or LO3."""
    self._send_command(self.sweep_end)


  def _send_command(self, cmd) -> None:
    """Send the selected command to the controller."""
    command = int(cmd)
    try:
      if sp.ser.is_open:
        sp.SimpleSerial.write(object, command)
    except:
      print(name(), line(), f': Open the serial port before sending a command <{command.__name__}>.')







