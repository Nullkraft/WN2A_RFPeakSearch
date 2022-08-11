# -*- coding: utf-8 -*-

from ui.mainWindow import MainWindow
from PyQt6 import QtWidgets             # requires 'pip install pyqtgraph'
import sys

# Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())    # Using sys.exit() provides a return code to the command line.
                            # app.exec() starts the event loop.


""" NEXT:
    Perform a sweep using full_sweep_dict
    
    1) After gui startup; select the full_sweep_dict file to be used.
    2) Set the sweep freq_start, freq_stop, and freq_step values.
    3) When the sweep button is clicked use the sweep freq_start,
       freq_stop, and freq_step to create a sweep_slice from the 
       full_sweep_dict.
    4) Perform a sweep by grabbing the ref_clock_sel, LO1_n, LO2_fmn, 
       and LO3_fmn values from the sweep_slice.
       
        for RFin in sweep_slice:

            ref_clock_sel = sweep_slice[RFin][0]
            LO1_n = sweep_slice[RFin][1]
            LO2_fmn = sweep_slice[RFin][2]
            LO3_fmn = sweep_slice[RFin][3]

            if ref_clock_sel != last_ref_clock:
                ser.write(ref_clock_sel)
                last_ref_clock = ref_clock_sel

            if LO1_n != last_LO1_n:
                ser.write(LO1_n)
                last_LO1_n = LO1_n

            ser.write(LO2_fmn)

            if (LO3 is enabled) and (last_LO3_fmn != LO3_fmn):
                ser.write(LO3_fmn)
"""




""" TODO: 1) Use a pool in the calibrate_sa.py for file reads
          2) Make calibrate_sa.py take its filenames as input variables
"""


""" TODO: Move serial.Serial() to the simple_serial class initializer.
    SEE : https://youtu.be/2ejbLVkCndI?t=432

    Use Dependency Injection for setting up the serial port when calling open_port() 
        Dependency Inversion
        Protocol class
        Abstract base class
"""












