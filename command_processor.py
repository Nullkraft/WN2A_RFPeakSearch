import serial_port as sp
import sys
import time
import logging

# Utility to simplify print debugging.
line = lambda: f'line {str(sys._getframe(1).f_lineno)},'
name = f'File \"{__name__}.py\",'

# Arduino and Device Commands
attenuator_sel    = 0x000000FF   # Attenuates the RFinput from 0 to 31.75dB

LO1_device_sel    = 0x000001FF   # Select device before sending a General Command
LO1_RF_off        = 0x000009FF   # Specific commands
LO1_neg4dBm       = 0x000011FF   # Change power and num freq steps
LO1_neg1dBm       = 0x000019FF   #         .
LO1_pos2dBm       = 0x000021FF   #         .
LO1_pos5dBm       = 0x000029FF   #         .
LO1_num_steps     = 0x000031FF   # Change num freq steps only
LO1_mux_tristate  = 0x000039FF   # Disable or rather set tristate on the mux pin
LO1_mux_dig_lock  = 0x000041FF   # Enable digital lock detect on the mux pin

LO2_device_sel    = 0x000002FF   # Select device before sending a General Command
LO2_RF_off        = 0x00000AFF   # Specific commands
LO2_neg4dBm       = 0x000012FF   # Change power and num freq steps
LO2_neg1dBm       = 0x00001AFF   #         .
LO2_pos2dBm       = 0x000022FF   #         .
LO2_pos5dBm       = 0x00002AFF   #         .
LO2_num_steps     = 0x000032FF   # Change num freq steps only
LO2_mux_tristate  = 0x00003AFF   # Disable or rather set tristate on the mux pin
LO2_mux_dig_lock  = 0x000042FF   # Enable digital lock detect on the mux pin

LO3_device_sel    = 0x000003FF   # Select device before sending a General Command
LO3_RF_off        = 0x00000BFF   # Specific commands
LO3_neg4dBm       = 0x000013FF   # Change power and num freq steps
LO3_neg1dBm       = 0x00001BFF   #         .
LO3_pos2dBm       = 0x000023FF   #         .
LO3_pos5dBm       = 0x00002BFF   #         .
LO3_num_steps     = 0x000033FF   # Change num freq steps only
LO3_mux_tristate  = 0x00003BFF   # Disable or rather set tristate on the mux pin
LO3_mux_dig_lock  = 0x000043FF   # Enable digital lock detect on the mux pin

# Reference clock Device Commands
all_ref_disable   = 0x000004FF
ref_clock1_enable = 0x00000CFF   # Enables 66.000 MHz reference and disables 66.666 MHz reference
ref_clock2_enable = 0x000014FF   # Enables 66.666 MHz reference and disables 66.000 MHz reference

# Arduino status
Arduino_LED_on    = 0x00000FFF   # LED blink test - The 'Hello World' of embedded dev
Arduino_LED_off   = 0x000007FF
version_message   = 0x000017FF   # Query Arduino type and Software version

# ADC selection and read request
sel_adc_LO2       = 0x000027FF   # Enable 315 MHz LogAmp ADC and disable 45 MHz LogAmp ADC
sel_adc_LO3       = 0x00002FFF   # Enable 45 MHz LogAmp ADC and disable 315 MHz LogAmp ADC

# Serial channel control
ready_to_send     = 0x000047FF   # Serial communication flow control
sweep_complete    = 0x000037FF   # Tell the Arduino that all data has been sent


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

def set_LO1(LO1_command, int_N: int=None):
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

def sweep_done():
    _send_command(sweep_complete)


def _send_command(command):
    try:
        if sp.ser.is_open:
            cmd_bytes = command.to_bytes(4, 'little')
            sp.ser.write(cmd_bytes)
    except:
        print(name, line(), f': The serial port was not opened before sending the command <{command.__name__}>.')







