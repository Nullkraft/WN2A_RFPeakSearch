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

# Utility functions used for displaying the name and the line number
# of the source file. Requires: import sys
name = lambda: f'File \"{__name__}.py\",'
line = lambda: f'line {str(sys._getframe(1).f_lineno)},'


from ui.mainWindow import MainWindow
from PyQt6 import QtWidgets             # requires 'pip install pyqtgraph'
import sys

from time import perf_counter

def main():
    app = QtWidgets.QApplication(sys.argv)
    start = perf_counter()
    window = MainWindow()
    print(name(), line(), f'INFO::Startup took {round(perf_counter()-start, 6)} seconds')
    window.show()
    sys.exit(app.exec())    # Using sys.exit() takes the return code from app.exec() and sends
                            # it to the command line while app.exec() starts the event loop.

#    How To Reduce Coupling With Facade (Adding an abstraction layer)
#    https://www.youtube.com/watch?v=jjoLejA4iAE

# Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    print()
    main()
#    print("Most lastest line ...")
