import serial_port as sp
import sys
import time

# Utility to simplify print debugging.
line = lambda : sys._getframe(1).f_lineno
name = __name__

# Arduino and MAX2871 Commands
LO2_RF_Disable  = 0x00000AFF
LO3_RF_Disable  = 0x00000BFF
Arduino_LED_on  = 0x00000FFF
Arduino_LED_off = 0x000007FF
Arduino_message = 0x000017FF
all_ref_disable = 0x000004FF
ref_60_enable   = 0x00000CFF    # Simultaneously disables 100 MHz reference
ref_100_enable  = 0x000014FF    # Simultaneously disables 60 MHz reference


def get_message():
    _send_command(Arduino_message)
    rf_out_status = sp.ser.read(64)
    time.sleep(0.5)
    return rf_out_status

def disable_LO2_RFout():
    _send_command(LO2_RF_Disable)

def disable_LO3_RFout():
    _send_command(LO3_RF_Disable)

def turn_Arduino_LED_on():
    _send_command(Arduino_LED_on)

def turn_Arduino_LED_off():
    _send_command(Arduino_LED_off)

def disable_all_ref_clocks():
    _send_command(all_ref_disable)

def enable_60MHz_ref_clock():
    _send_command(ref_60_enable)

def enable_100MHz_ref_clock():
    _send_command(ref_100_enable)


def _send_command(command):
    try:
        if sp.ser.is_open:
            cmd_bytes = command.to_bytes(4, 'little')
            sp.ser.write(cmd_bytes)
    except:
        print(name, line(), f': The serial port was not opened before sending the Arduino command {command}.')










