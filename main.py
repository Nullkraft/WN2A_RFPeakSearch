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


from ui.mainWindow import MainWindow
from PyQt6 import QtWidgets             # requires 'pip install pyqtgraph'
import sys
from loguru import logger   # https://pypi.org/project/loguru/


@logger.catch
def main():
    logger.add(sys.stdout, colorize=True, format="{level} {message}", filter="my_module", level="INFO")
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    logger.info("Logging is working.")
    sys.exit(app.exec())    # Using sys.exit() takes the return code from app.exec() and sends it to the command line.
                            # app.exec() starts the event loop.


# Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    print()
    main()

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












