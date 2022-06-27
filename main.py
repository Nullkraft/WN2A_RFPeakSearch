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



""" TODO: Use a pool in the calibrate_sa.py for file reads """
""" QUERY: How to save and reload a dictionary to and from a file """
""" NEXT: Make calibrate_sa.py take its filenames as input variables """



""" TODO: Move serial.Serial() to the simple_serial class initializer.
    SEE : https://youtu.be/2ejbLVkCndI?t=432
"""


""" TODO: Use Dependency Injection for setting up the serial port when calling open_port() 
              Dependency Inversion
              Protocol class
              Abstract base class
"""

""" TODO: Refactor Initial-Startup if needed
        1) Auto-create Ref1 dictionary - Choose as default on startup
        2) Auto-create Ref2 dictionary
"""

""" TODO: Change the initial loading of LO1 and LO2 step files to their new names """

""" TODO: Automatically select the correct LO1 and LO2 step files based on the selected reference clock """




