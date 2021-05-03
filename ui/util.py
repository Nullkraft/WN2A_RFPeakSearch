
from PyQt5.QtWidgets import QMessageBox

def showDialog(self, message):
    box = QMessageBox()

#    print(type(message))
    
    if type(message) == float:      # type == float
        box.setText(str(message))
    else:
        box.setText(message)        # type == str
    
    box.setWindowTitle("Message Display")
    box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    box.exec()

