import serial_port as sp
import sys

# Utility to simplify print debugging.
line = lambda : sys._getframe(1).f_lineno
name = __name__

# Arduino and MAX2871 Commands
RF_Enable = b'E'
RF_Disable = b'e'
Arduino_LED_on = b'L'
Arduino_LED_off = b'l'
status_request = b'S'


# *********  FIX ME!  ***************
# * Output does not reflect the hardware status and in fact
# * it is reading the reg5 string from some random memory
# * address.
# ***********************************
# Currently will only work with RF_En pin status.
# Add the Arduino LED pin status to improve usefulness
def get_hw_status():
    _send_command(status_request)
#    rf_out_status = sp.ser.read(1)
    rf_out_status = sp.ser.read(4)      # This
    return rf_out_status


def enable_rf_out():
    _send_command(RF_Enable)


def disable_rf_out():
    _send_command(RF_Disable)


def turn_Arduino_LED_on():
    _send_command(Arduino_LED_on)


def turn_Arduino_LED_off():
    _send_command(Arduino_LED_off)


def _send_command(command):
    try:
        if sp.ser.is_open:
            sp.ser.write(command)
    except:
        print(name, line(), f': The serial port was not opened before sending the Arduino command {command}.')










