from ui.mainWindow import MainWindow
from PyQt5 import QtWidgets             # requires 'pip install pyqtgraph'
import sys


# Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()

