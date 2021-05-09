# -*- coding: utf-8 -*-

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot, QObject, QThread, pyqtSignal  #  , QObject
from PyQt5.QtWidgets import QMainWindow
import sys
import math
#import time
import pyqtgraph as pg
import numpy as np

from .Ui_mainWindow import Ui_MainWindow

# Developer utility function(s). DO NOT SHIP THIS SOURCE CODE
from ui.util import showDialog


# Functions specific to the operation of the WN2A Spectrum Analyzer hardware, hopefully.
# Including setting up the serial port.
import spectrumAnalyzer as sa

import serial_port as sp

# Utility to simplify print debugging. ycecream is a lot better, though.
line = lambda : sys._getframe(1).f_lineno
name = __name__



class serialWorker(QObject):
    # signals
    finished = pyqtSignal(bytearray)
    progress = pyqtSignal(int)

    def __init__(self, numPoints, parent=None):
        QObject.__init__(self, parent)
        self.numDataPoints = numPoints

    def run(self):
        self.amplDataBytes = bytearray()                    # Store 8bit data from Arduino
        command = self.__cmd(self.numDataPoints)            # Command to send to Arduino
        sp.ser.write(command)                               # Send command to the Arduino
        # Read response as raw bytes from the Arduino.
        while True:
            bytesToRead = sp.ser.in_waiting
            self.amplDataBytes += sp.ser.read(bytesToRead)
            reversed_bytes = self.amplDataBytes[::-1]        # Reverse list before searching
            array_position = reversed_bytes.find(255)        # Find the FIRST 0xFF (or 255)
            # A SECOND 0xFF (or 255) means that we found the end-of-record.
            if list(reversed_bytes[array_position:array_position+2]) == [255, 255]:
                self.amplDataBytes = reversed_bytes[array_position:]
                self.amplDataBytes = self.amplDataBytes[::-1]
                break
        self.finished.emit(self.amplDataBytes)              # Return the Amplitude Array

    # The Arduino will only simulate a fixed number of RF data points.
    def __cmd(self, numPoints):
        # The Arduino sees 1=256*16bits 2=512 3=768 4=1024 5=1280 (6 or greater)=1536
        arduinoCmds = [b'b1a', b'b2a', b'b3a', b'b4a', b'b5a', b'b6a']
        selection = numPoints // 256 - 1                # selection = floor(numPoints/256)-1
        selection = 5 if selection > 5 else selection
        return arduinoCmds[selection]

# End serialWorker() class


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        pg.setConfigOptions(useOpenGL=True)
        self.setupUi(self)  # Must come before self.plot[]
        self.graphWidget.setYRange(-100, -40)
        self.dataLine = self.graphWidget.plot()
      # Stores the register values programmed into the chip
        self.init_chip = True
        self.referenceClock = 60
        self.initialized = False
      # Populate the serial port selection list
        ports = sp.list_os_ports()
        self.cbxSerialPortSelection.addItems(ports)
      # Populate the Serial Speed selection list
        speeds = sp.get_os_baudrates()
        for x in speeds:
            self.cbxSerialSpeedSelection.addItem(str(x), x)


    @pyqtSlot()
    def on_btnSendRegisters_clicked(self):
        freq = self.floatStartMHz.value()
        sa.write_registers(freq, self.referenceClock, self.initialized)

    # Threaded read from Arduino serial
    # Simulation function: Substitute live data for production code.
    @pyqtSlot()
    def on_btnTrigger_clicked(self):
        if sp.ser.is_open:
            numDataPoints = self.numDataPoints.value()
            self.thread = QThread()                                 # Create a new serial thread
            self.worker = serialWorker(numDataPoints)               # Function for reading the serial port
            self.worker.moveToThread(self.thread)                   # Serial reads happen inside its own thread
            self.thread.started.connect(self.worker.run)            # Connect to signals...
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.worker.finished.connect(self.showAmplData)
            self.thread.finished.connect(self.thread.deleteLater)
            self.thread.start()                                     # After starting the thread...
            self.btnTrigger.setEnabled(False)                       # disable the Trigger button until we're done
            self.thread.finished.connect(lambda: self.btnTrigger.setEnabled(True))
        else:
            print('')
            print('     You must first open the serial port.')
            print('     You can do so by selecting a Serial port AND speed.')

    @pyqtSlot(str)
    def on_cbxSerialPortSelection_activated(self, selected_port):
        sp.set_port(selected_port)

    @pyqtSlot(str)
    def on_cbxSerialSpeedSelection_activated(self, speed_str):
        sp.set_speed(speed_str)

    @pyqtSlot()
    def on_btn_reinitialize_clicked(self):
        ''' Delete Me - This is only useful for development '''
        self.initialized = False

    @pyqtSlot(int)
    def on_selectReferenceOscillator_currentIndexChanged(self, index):
        if index == 0:
            self.referenceClock = 60
        if index == 1:
            self.referenceClock = 100

        return self.referenceClock

    def showAmplData(self, amplBytes):
        self.amplitudeData = []    # Storage for Amplitude values after conversion from bytes.
        nBytes = len(amplBytes) - 2   # Serial bytes received minus the two end-of-record bytes.
        for x in range(0, nBytes, 2):
            # Ccombine serial MSB & LSB
            ampl_word = (amplBytes[x+1] << 8) | amplBytes[x]
            # Convert RF Amplitude to dBV.
            amplitude = -20*math.log10(ampl_word)
            # Store converted RF Amplitude dB's
            self.amplitudeData.append(amplitude)
        stepSize = (self.floatStopMHz.value() - self.floatStartMHz.value()) / len(self.amplitudeData)
        self.freqRange = np.arange(self.floatStartMHz.value(), self.floatStopMHz.value(), stepSize)
        self.dataLine.setData(self.freqRange, self.amplitudeData, pen=(155,155,255))

    @pyqtSlot()
    def on_btnPeakSearch_clicked(self):
        self.marker = np.array([pg.ArrowItem()])     # First, we need to create a growable array of markers
        self.text = np.array([pg.TextItem()])        # Let's make some labels for each of the markers

        # Read num markers from front-panel control
        for _ in range(self.numPeakMarkers.value()-1):
            self.marker = np.append(self.marker, pg.ArrowItem())  # Add markers up to numPeakMarkers
            self.text = np.append(self.text, pg.TextItem())       # Add labels for each marker

        # idx is an array that is presorted such that idx[0] points to the highest value
        # in the amplitudeData array and idx[1] points to the second highest, etc.
        idx = sa.peakSearch(self.amplitudeData, self.numPeakMarkers.value())

        # Create and add Peak Markers to the graph
        for i in range(self.numPeakMarkers.value()):
            self.marker[i] = pg.ArrowItem(angle=-90, tipAngle=40, tailWidth=10, pen={'color': 'w', 'width': 1})
            frequency = self.freqRange[idx[i]]
            amplitude = self.amplitudeData[idx[i]]
            self.marker[i].setPos(frequency, amplitude)  # x-axis = frequency, y-axis = amplitude
            frequency_text = str('%.5f' % self.freqRange[idx[i]])
            amplitude_text = str('%.2f' % self.amplitudeData[idx[i]])
            markerLabel = frequency_text + ' MHz\n' + amplitude_text + ' dBV'
            self.text[i] = pg.TextItem(markerLabel, anchor = (0.5, 1.5), border = 'w', fill = (0, 0, 255, 100))
            self.graphWidget.addItem(self.marker[i])
            self.graphWidget.addItem(self.text[i])
            frequency_pos = self.freqRange[idx[i]]
            amplitude_pos = self.amplitudeData[idx[i]]
            self.text[i].setPos(frequency_pos, amplitude_pos)

    @pyqtSlot()
    def on_btnClearPeakSearch_clicked(self):
        for x in self.marker:
            self.graphWidget.removeItem(x)
        self.marker = self.marker[0]
        for x in self.text:
            self.graphWidget.removeItem(x)
            self.text = self.text[1:]

    @pyqtSlot()
    def on_minGraphWidth_editingFinished(self):
        szWidth = self.minGraphWidth.value()
        szHeight = self.minGraphHeight.value()
        self.setMinimumSize(QtCore.QSize(szWidth, szHeight))

    @pyqtSlot()
    def on_minGraphHeight_editingFinished(self):
        szWidth = self.minGraphWidth.value()
        szHeight = self.minGraphHeight.value()
        self.setMinimumSize(QtCore.QSize(szWidth, szHeight))

    @pyqtSlot(bool)
    def on_btnZeroSpan_clicked(self, checked):
        # fb.calculateRegisterValues()
        showDialog(self, "TODO: Create Zero span function")

    @pyqtSlot(bool)
    def on_btnFullSpan_clicked(self, checked):
        showDialog(self, "TODO: Create Full span function")

    @pyqtSlot(bool)
    def on_btnLastSpan_clicked(self, checked):
        showDialog(self, "TODO: Create Last span function")

    @pyqtSlot()
    def on_btnExit_clicked(self):
        sys.exit()

    @pyqtSlot(float)
    def on_dblCenterMHz_valueChanged(self, centerFreq):
        showDialog(self, centerFreq)

    @pyqtSlot(float)
    def on_dblStepKHz_valueChanged(self, stepFreq):
        showDialog(self, stepFreq)

    @pyqtSlot(float)
    def on_dblSpanMHz_valueChanged(self, deltaFreq):
        showDialog(self, deltaFreq)

    @pyqtSlot(bool)
    def on_chkShowGrid_toggled(self, checked):
        self.graphWidget.showGrid(x=checked, y=checked)

    @pyqtSlot()
    def on_numDataPoints_editingFinished(self):
        pass

    @pyqtSlot()
    def on_numPlotFloor_editingFinished(self):
        if self.numPlotFloor.value() < self.numPlotCeiling.value():
            self.graphWidget.setYRange(self.numPlotFloor.value(), self.numPlotCeiling.value())

    @pyqtSlot()
    def on_numPlotCeiling_editingFinished(self):
        if self.numPlotFloor.value() < self.numPlotCeiling.value():
            self.graphWidget.setYRange(self.numPlotFloor.value(), self.numPlotCeiling.value())


# End MainWindow() class














