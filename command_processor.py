import serial_port as sp
import sys

# Utility to simplify print debugging. ycecream is a lot better, though.
line = lambda : sys._getframe(1).f_lineno
name = __name__


command = None

RF_Enable = b'E'
RF_Disable = b'e'
Arduino_LED_on = b'L'
Arduino_LED_off = b'l'
status_request = b'S'

def _send_command():
    global command
    msg = None
    if sp.ser.is_open:
        sp.ser.write(command)
        msg = '1'   # Command sent
    else:
        msg = '0'   # Sending failed
    return msg


# Currently will only work with RF_En pin status.
# Add the Arduino LED pin status to improve usefulness
def get_hw_status():
    global command
    command = status_request
    _send_command()
    rf_out_status = sp.ser.read(1)
    return rf_out_status

def enable_rf_out():
    global command
    command = RF_Enable
    _send_command()


def disable_rf_out():
    global command
    command = RF_Disable
    _send_command()


def turn_Arduino_LED_on():
    global command
    command = Arduino_LED_on
    _send_command()


def turn_Arduino_LED_off():
    global command
    command = Arduino_LED_off
    _send_command()
