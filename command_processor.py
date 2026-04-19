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

# Import logging_setup to configure logging once for the application.
import logging
import logging_setup    # Used for its side effects
_ = logging_setup   # silence Warning: 'logging_setup' imported but unused

import serial_port as sp
import time


"""Controller protocol command words and compatibility helpers."""
class CmdProcInterface():
  _instance = None
  
  def __new__(cls):
    if cls._instance is None:
      cls._instance = super(CmdProcInterface, cls).__new__(cls)
      # Controller protocol command words.
      cls._instance.attenuator_sel    = 0x00FF   # Attenuates the RFinput from 0 to 31.75dB

      cls._instance.LO1_device_sel    = 0x01FF   # Select device before sending a General Command
      cls._instance.LO1_RF_off        = 0x09FF   # Specific commands
      cls._instance.LO1_neg4dBm       = 0x11FF   # Change LO1 RF output power
      cls._instance.LO1_neg1dBm       = 0x19FF   #     .
      cls._instance.LO1_pos2dBm       = 0x21FF   #     .
      cls._instance.LO1_pos5dBm       = 0x29FF   #     .
      cls._instance.LO1_no_change     = 0x31FF   # Select LO1 without changing the RF output power
      cls._instance.LO1_mux_tristate  = 0x39FF   # Disable or rather set tristate on the mux pin
      cls._instance.LO1_mux_dig_lock  = 0x41FF   # Enable digital lock detect on the mux pin

      cls._instance.LO2_device_sel    = 0x02FF   # Select device before sending a General Command
      cls._instance.LO2_RF_off        = 0x0AFF   # Specific commands
      cls._instance.LO2_neg4dBm       = 0x12FF   # Change power and num freq steps
      cls._instance.LO2_neg1dBm       = 0x1AFF   #     .
      cls._instance.LO2_pos2dBm       = 0x22FF   #     .
      cls._instance.LO2_pos5dBm       = 0x2AFF   #     .
      cls._instance.LO2_num_steps     = 0x32FF   # Change num freq steps only
      cls._instance.LO2_mux_tristate  = 0x3AFF   # Set tristate on the mux pin
      cls._instance.LO2_mux_dig_lock  = 0x42FF   # Enable digital lock detect on the mux pin
      cls._instance.LO2_divider_mode  = 0x4AFF   # Set the RFOut Output Divider Mode to 1, 2, 4, 8, 16, 32, 64, or 128

      cls._instance.LO3_device_sel    = 0x03FF   # Select device before sending a General Command
      cls._instance.LO3_RF_off        = 0x0BFF   # Specific commands
      cls._instance.LO3_neg4dBm       = 0x13FF   # Change power and num freq steps
      cls._instance.LO3_neg1dBm       = 0x1BFF   #     .
      cls._instance.LO3_pos2dBm       = 0x23FF   #     .
      cls._instance.LO3_pos5dBm       = 0x2BFF   #     .
      cls._instance.LO3_num_steps     = 0x33FF   # Change num freq steps only
      cls._instance.LO3_mux_tristate  = 0x3BFF   # Set tristate on the mux pin
      cls._instance.LO3_mux_dig_lock  = 0x43FF   # Enable digital lock detect on the mux pin
      cls._instance.LO3_divider_mode  = 0x4BFF   # Set the RFOut Output Divider Mode to 1, 2, 4, 8, 16, 32, 64, or 128

      # Reference clock command words.
      cls._instance.all_ref_disable   = 0x04FF
      cls._instance.ref_clock1_enable = 0x0CFF   # Enables 66.000 MHz reference and disables 66.666 MHz reference
      cls._instance.ref_clock2_enable = 0x14FF   # Enables 66.666 MHz reference and disables 66.000 MHz reference

      # Controller status and query command words.
      cls._instance.Arduino_LED_off   = 0x07FF
      cls._instance.Arduino_LED_on    = 0x0FFF   # LED blink test - The 'Hello World' of embedded dev
      cls._instance.version_message   = 0x17FF   # Query Arduino type and Software version
      cls._instance.sweep_start       = 0x1FFF   # Serial communication flow control
      cls._instance.sweep_end         = 0x27FF   # Tell the Arduino that all data has been sent
      cls._instance.reset_and_report  = 0x2FFF   # Reset the Spectrum Analyzer to default settings
    return cls._instance
    
  def __init__(self):
    pass # Initialization is handled in __new__


class CommandProcessor(CmdProcInterface):
  """Serialize protocol words for the controller without changing byte layout.

  The public API still exposes legacy chip-shaped names such as `sel_LO1()`
  and `set_LO2()`. Phase 3 keeps those names for compatibility with the rest
  of the codebase while treating this module as a protocol/serialization
  layer rather than a device-model layer.
  """

  def set_attenuator(self, decibels: float = 31.75) -> None:
    """
    Send the attenuator payload expected by the controller protocol.

    The attenuator setting is encoded as quarter-dB steps in the upper
    16 bits, ORed with the `attenuator_sel` command word.
    """
    level = int(decibels * 4) << 16
    self._send_command(level | self.attenuator_sel)


  def set_max2871_freq(self, fmn: int) -> None:
    """
    Legacy direct-programming helper for sending a raw FMN payload.
    """
    self._send_command(fmn)


  def disable_LO2_RFout(self) -> None:
    """Legacy helper that sends the LO2 RF-disable command word."""
    self._send_command(self.LO2_RF_off)


  def disable_LO3_RFout(self) -> None:
    """Legacy helper that sends the LO3 RF-disable command word."""
    self._send_command(self.LO3_RF_off)

  
  def sel_LO1(self) -> None:
    """Legacy helper that sends the LO1 device-select command word."""
    self._send_command(self.LO1_device_sel)


  def set_LO1(self, LO1_command: int, int_N: int = 54) -> None:
    """
    Legacy helper that sends an LO1 command word plus its integer-N payload.

    `LO1_command` stays public for compatibility. The upper 16 bits carry the
    integer-N value and the low bits carry the controller command word.
    """
    if int_N is not None:
      if (53 <= int_N <= 102):
        N = int_N << 16
      else:
        logging.error(f'N ({int_N}) exceeds the limits of the ADF4356 (LO1)')
    else:
      N = 0
    self._send_command(LO1_command | N)


  def sel_LO2(self) -> None:
    """Legacy helper that sends the LO2 device-select command word."""
    self._send_command(self.LO2_device_sel)


  def set_LO2(self, LO2_command: int) -> None:
    """Legacy helper that sends an LO2 protocol payload unchanged."""
    self._send_command(LO2_command)


  def sel_LO3(self) -> None:
    """Legacy helper that sends the LO3 device-select command word."""
    self._send_command(self.LO3_device_sel)


  def set_LO3(self, LO3_command) -> None:
    """Legacy helper that sends an LO3 protocol payload unchanged."""
    self._send_command(LO3_command)


  def LO_device_register(self, device_command: int) -> None:
    """
    Legacy direct-programming helper for raw LO register payloads.
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
    """Read and log the most recent controller message, if present."""
    sp.ser.read(sp.ser.in_waiting)  # Clear serial buffer of any junk
    time.sleep(0.01)
    msg = sp.ser.read(64)           # Collect the report(s)
    if msg:
      logging.info(f'Arduino message = {msg}')


  def get_version_message(self):
    """Request and log the controller firmware version string."""
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
    """Send the protocol command word for the selected reference source."""
    if ref_clock_command == 1:
      self._send_command(self.ref_clock1_enable)
    else:
      self._send_command(self.ref_clock2_enable)
    self.show_message()


  def end_sweep(self) -> None:
    """Send the protocol word that terminates a sweep data stream."""
    self._send_command(self.sweep_end)


  def _send_command(self, cmd) -> None:
    """Serialize one protocol word to the controller transport."""
    command = int(cmd)
    try:
      if sp.ser.is_open:
        sp.SimpleSerial.write(object, command)
    except:
      logging.warning(f'Open the serial port before sending command {command}.')

#    # This can be used to echo a copy of the message from the Arduino controller
#    # To simplify the result go into the Arduino and uncomment '#define MESSAGE_TESTING'
#    msg = bytes(4)
#    while(sp.ser.in_waiting):
#      msg += sp.ser.read(sp.ser.in_waiting)  # Clear serial buffer of any junk
#      time.sleep(0.01)
#    print(name(), line(), f"msg = {msg}")





