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

import serial_port as sp
import sys
import time
import logging

# Utility to simplify print debugging.
line = lambda: f'line {str(sys._getframe(1).f_lineno)},'
name = f'File \"{__name__}.py\",'

# Arduino and Device Commands
attenuator_sel    = 0x00FF   # Attenuates the RFinput from 0 to 31.75dB

LO1_device_sel    = 0x01FF   # Select device before sending a General Command
LO1_RF_off        = 0x09FF   # Specific commands
LO1_neg4dBm       = 0x11FF   # Change power and num freq steps
LO1_neg1dBm       = 0x19FF   #         .
LO1_pos2dBm       = 0x21FF   #         .
LO1_pos5dBm       = 0x29FF   #         .
LO1_no_change     = 0x31FF   # Select LO1 without changing the RF output power level
LO1_mux_tristate  = 0x39FF   # Disable or rather set tristate on the mux pin
LO1_mux_dig_lock  = 0x41FF   # Enable digital lock detect on the mux pin

LO2_device_sel    = 0x02FF   # Select device before sending a General Command
LO2_RF_off        = 0x0AFF   # Specific commands
LO2_neg4dBm       = 0x12FF   # Change power and num freq steps
LO2_neg1dBm       = 0x1AFF   #         .
LO2_pos2dBm       = 0x22FF   #         .
LO2_pos5dBm       = 0x2AFF   #         .
LO2_num_steps     = 0x32FF   # Change num freq steps only
LO2_mux_tristate  = 0x3AFF   # Disable or rather set tristate on the mux pin
LO2_mux_dig_lock  = 0x42FF   # Enable digital lock detect on the mux pin

LO3_device_sel    = 0x03FF   # Select device before sending a General Command
LO3_RF_off        = 0x0BFF   # Specific commands
LO3_neg4dBm       = 0x13FF   # Change power and num freq steps
LO3_neg1dBm       = 0x1BFF   #         .
LO3_pos2dBm       = 0x23FF   #         .
LO3_pos5dBm       = 0x2BFF   #         .
LO3_num_steps     = 0x33FF   # Change num freq steps only
LO3_mux_tristate  = 0x3BFF   # Disable or rather set tristate on the mux pin
LO3_mux_dig_lock  = 0x43FF   # Enable digital lock detect on the mux pin

# Reference clock Device Commands
all_ref_disable   = 0x04FF
ref_clock1_enable = 0x0CFF   # Enables 66.000 MHz reference and disables 66.666 MHz reference
ref_clock2_enable = 0x14FF   # Enables 66.666 MHz reference and disables 66.000 MHz reference

# Arduino status
Arduino_LED_on    = 0x0FFF   # LED blink test - The 'Hello World' of embedded dev
Arduino_LED_off   = 0x07FF
version_message   = 0x17FF   # Query Arduino type and Software version

# ADC selection and read request
sel_adc_LO2       = 0x27FF   # Enable 315 MHz LogAmp ADC and disable 45 MHz LogAmp ADC
sel_adc_LO3       = 0x2FFF   # Enable 45 MHz LogAmp ADC and disable 315 MHz LogAmp ADC

# Serial channel control
block_xfer_start  = 0x3FFF   # Serial communication flow control
block_xfer_stop   = 0x47FF   # Tell the Arduino that all data has been sent


# Attenuator Command & Control
def set_attenuator(decibels: float=31.75):
    """
    The level will be programmed into the deviceRegister and
    can be found by multiplying the desired attenuation dB by 4.
    The level is the merged with the 32 bit attenuator_sel
    command found in the Spectrum Analyzer Interface Standard 3.
    """
    level = int(decibels * 4) << 16
    _send_command(level | attenuator_sel)

# Set new LO2/3 frequency
def set_max2871_freq(fmn: int):
    _send_command(fmn)

# LO2 Command & Control
def disable_LO2_RFout():
    _send_command(LO2_RF_off)

# LO3 Command & Control
def disable_LO3_RFout():
    _send_command(LO3_RF_off)

def set_LO1(LO1_command, int_N: int=54):
    """
    Function 
    
    @param LO1_command (Choose one from the list of "Arduino and Device Commands" above)
    @type int_32
    @param int_N LO1, LO2, or LO3 control code (defaults to None)
    @type int (optional)
    """
    if int_N != None:
        if (54 <= int_N <= 100):
            N = int_N << 16
        else:
            logging.error(f'{name}, {line()}, N ({int_N}) is not within the limits of the ADF4356 (LO1)')
    else:
        N = 0
    _send_command(LO1_command | N)

def sel_LO2():
    _send_command(LO2_device_sel)

def set_LO2(LO2_command):
    _send_command(LO2_command)

def set_LO3(LO3_command):
    _send_command(LO3_command)

def LO_device_register(device_command: int):
    """
    Function LO_device_register

    @param device_command FMN data (LO2/LO3) or N data (LO1) for direct device control
    @type TYPE
    """
    _send_command(device_command)

def LED_on():
    _send_command(Arduino_LED_on)

def LED_off():
    _send_command(Arduino_LED_off)

def get_version_message():
    sp.ser.read(sp.ser.in_waiting)      # Clear out the serial buffer.
    _send_command(version_message)      # Request software report from controller
    time.sleep(0.01)
    software_version = sp.ser.read(64)  # Collect the report(s)
    return software_version

def disable_all_ref_clocks():
    _send_command(all_ref_disable)

def enable_ref_clock(ref_clock_command):
    _send_command(ref_clock_command)

def sel_315MHz_adc():
    _send_command(sel_adc_LO2)

def sel_45MHz_adc():
    _send_command(sel_adc_LO3)

def sweep_start():
    _send_command(block_xfer_start)

def sweep_end():
    _send_command(block_xfer_stop)


def _send_command(command):
    try:
        if sp.ser.is_open:
            cmd_bytes = command.to_bytes(4, 'little')
            sp.ser.write(cmd_bytes)
    except:
        print(name, line(), f': The serial port was not opened before sending the command <{command.__name__}>.')







