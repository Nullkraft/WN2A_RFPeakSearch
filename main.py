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




""" TODO: Auto-open last serial port used if still available """

""" TODO: Refactor Initial-Startup if needed
        1) Auto-create Ref1 dictionary - Choose as default on startup
        2) Auto-create Ref2 dictionary
"""

""" TODO: Change the initial loading of LO1 and LO2 step files to their new names """

""" TODO: Automatically select the correct LO1 and LO2 step files based on the selected reference clock """




