import serial_port as sp
import sys
import time
import logging

# Utility to simplify print debugging.
line = lambda : sys._getframe(1).f_lineno
name = __name__

# Arduino and Device Commands
Attenuator_level = 0x007F00FF   # Attenuates the RFinput from 0 to 32dB - default 32 dBm

LO1_device_sel   = 0x000001FF   # Select device before sending a General Command
LO1_RF_off       = 0x000009FF   # Specific commands
LO1_neg4dBm      = 0x000011FF   # Change power and num freq steps
LO1_neg1dBm      = 0x000019FF   #         .
LO1_pos2dBm      = 0x000021FF   #         .
LO1_pos5dBm      = 0x000029FF   #         .
LO1_num_steps    = 0x000031FF   # Change num freq steps only
LO1_mux_tristate = 0x000039FF   # Disable or rather set tristate on the mux pin
LO1_mux_dig_lock = 0x000041FF   # Enable digital lock detect on the mux pin

LO2_device_sel   = 0x000002FF   # Select device before sending a General Command
LO2_RF_off       = 0x00000AFF   # Specific commands
LO2_neg4dBm      = 0x000012FF   # Change power and num freq steps
LO2_neg1dBm      = 0x00001AFF   #         .
LO2_pos2dBm      = 0x000022FF   #         .
LO2_pos5dBm      = 0x00002AFF   #         .
LO2_num_steps    = 0x000032FF   # Change num freq steps only
LO2_mux_tristate = 0x00003AFF   # Disable or rather set tristate on the mux pin
LO2_mux_dig_lock = 0x000042FF   # Enable digital lock detect on the mux pin

LO3_device_sel   = 0x000003FF   # Select device before sending a General Command
LO3_RF_off       = 0x00000BFF   # Specific commands
LO3_neg4dBm      = 0x000013FF   # Change power and num freq steps
LO3_neg1dBm      = 0x00001BFF   #         .
LO3_pos2dBm      = 0x000023FF   #         .
LO3_pos5dBm      = 0x00002BFF   #         .
LO3_num_steps    = 0x000033FF   # Change num freq steps only
LO3_mux_tristate = 0x00003BFF   # Disable or rather set tristate on the mux pin
LO3_mux_dig_lock = 0x000043FF   # Enable digital lock detect on the mux pin

# Reference clock Device Commands
all_ref_disable  = 0x000004FF
ref_60_enable    = 0x00000CFF   # Enables 60 MHz reference and disables 100 MHz reference
ref_100_enable   = 0x000014FF   # Enables 100 MHz reference and disables 60 MHz reference

# Arduino status
Arduino_LED_on   = 0x00000FFF   # LED blink test - The 'Hello World' of embedded dev
Arduino_LED_off  = 0x000007FF
Arduino_message  = 0x000017FF   # Query Arduino type and Software version

# Serial channel control
Ready_to_send    = 0x000047FF   # Serial communication flow control

# ADC selection and read request
enable_adc_LO2   = 0x000027FF   # Enable 315 MHz LogAmp ADC and disable 45 MHz LogAmp ADC
enable_adc_LO3   = 0x00002FFF   # Enable 45 MHz LogAmp ADC and disable 315 MHz LogAmp ADC


# LO1 Command & Control
def set_LO1(LO_command, N: int=0):
    if not (15 < N < 65536):
        logging.error(f'{name}, {line()}, The value of N ({N}) exceeded the allowed limits for the ADF4356 (LO1)')
    _send_command(LO_command | N)

# LO2 Command & Control
def disable_LO2_RFout():
    _send_command(LO2_RF_off)

# Set new frequency
def set_max2871_freq(fmn: int):
    _send_command(fmn)

# LO3 Command & Control
def disable_LO3_RFout():
    _send_command(LO3_RF_off)

def set_LO(LO_command, num_frequency_steps: int=0):
    if num_frequency_steps > 0xFFFF:
        num_steps = 0xFFFF0000    # Set and left shift to maximum frequency steps
        logging.error(f'{name}, {line()}, Requested too many frequency steps:  Max is 65,535.')
    else:
        num_steps = int(num_frequency_steps) << 16
    _send_command(LO_command | num_steps)

def LO_device_register(device_command: int):
    """
    Function LO_device_register

    @param device_command FMN data (LO2/LO3) or N data (LO1) for direct device control
    @type TYPE
    """
    _send_command(device_command)

def turn_Arduino_LED_on():
    _send_command(Arduino_LED_on)

def turn_Arduino_LED_off():
    _send_command(Arduino_LED_off)

def get_message():
    _send_command(Arduino_message)
    rf_out_status = sp.ser.read(64)
    time.sleep(0.5)
    return rf_out_status


def disable_all_ref_clocks():
    _send_command(all_ref_disable)

def enable_60MHz_ref_clock():
    _send_command(ref_60_enable)

def enable_100MHz_ref_clock():
    _send_command(ref_100_enable)

def enable_315MHz_adc():
    _send_command(enable_adc_LO2)

def enable_45MHz_adc():
    _send_command(enable_adc_LO3)


def _send_command(command: int):
    try:
        if sp.ser.is_open:
            cmd_bytes = command.to_bytes(4, 'little')
            sp.ser.write(cmd_bytes)
    except:
        print(name, line(), f': The serial port was not opened before sending the command {command}.')







