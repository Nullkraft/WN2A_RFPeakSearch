# -*- coding: utf-8 -*-

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot, QObject, QThread, pyqtSignal  #  , QObject
from PyQt5.QtWidgets import QMainWindow
import sys
import time
import pyqtgraph as pg
import numpy as np

from .Ui_mainWindow import Ui_MainWindow



# Functions specific to the operation of the WN2A Spectrum Analyzer hardware, hopefully.
# Including setting up the serial port.
import spectrumAnalyzer as sa
import serial_port as sp
import command_processor as cmd_proc

# Utility to simplify print debugging.
line = lambda : sys._getframe(1).f_lineno
name = __name__



# serialWorker is for receiving large amounts of data of a known size from the Arduino.
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
            if list(reversed_bytes[array_position:array_position+2]) == [255, 255]:     # end-of-record found
                self.amplDataBytes = reversed_bytes[array_position:]
                self.amplDataBytes = self.amplDataBytes[::-1]
                break
        self.finished.emit(self.amplDataBytes)              # Return the Amplitude Array

    # The Arduino will only simulate a fixed number of RF data points.
    def __cmd(self, numPoints):
        # The Arduino sees 1=256*16bits 2=512 3=768 4=1024 5=1280 (6 or greater)=1536
        arduinoCmds = [b'1', b'2', b'3', b'4', b'5', b'6']
        selection = numPoints // 256 - 1                # selection = floor(numPoints/256)-1
        selection = 5 if selection > 5 else selection
        return arduinoCmds[selection]

# End serialWorker() class


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        pg.setConfigOptions(useOpenGL=True)
        self.setupUi(self)  # Must come before self.plot[]
        self.graphWidget.setYRange(0, 1100)
        self.dataLine = self.graphWidget.plot()
      #
        self.referenceClock = 60
        self.initialized = False        # MAX2871 chip will need to be initialized
      # Populate the serial port selection list
        ports = sp.list_os_ports()
        self.cbxSerialPortSelection.addItems(ports)
      # Populate the Serial Speed selection list
        speeds = sp.get_os_baudrates()
        for x in speeds:
            self.cbxSerialSpeedSelection.addItem(str(x), x)
        sp.port_open()  # Open the serial port using the last settings we had.

    # SendRegisters() calls the Spectrum Analyzer code to generate new
    # register values for programming the MAX2871 to set a new frequency.
    # The amplitude of that frequency is then digitized (A2D) by the
    # Arduino and sent back to the PC for plotting and analysis.
    @pyqtSlot()
    def on_btnSendRegisters_clicked(self):
        if sp.ser.is_open:
            freq = self.floatStartMHz.value()
            if freq < 23.5:
                freq = 23.5
            if freq > 6000:
                freq = 6000
            sa.write_registers(freq, self.referenceClock, self.initialized)
            self.initialized = True


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
            print('     You have to open the serial port.')
            print('     You must select both a Serial port AND speed.')

    @pyqtSlot(str)
    def on_cbxSerialPortSelection_activated(self, selected_port):
        sp.set_port(selected_port)

    @pyqtSlot()
    def on_btnRefreshPortsList_clicked(self):
        for x in range(10):
            self.cbxSerialPortSelection.removeItem(0)
        ports = sp.list_os_ports()
        self.cbxSerialPortSelection.addItems(ports)

    @pyqtSlot(str)
    def on_cbxSerialSpeedSelection_activated(self, speed_str):
        sp.set_speed(speed_str)

    @pyqtSlot()
    def on_btn_reinitialize_clicked(self):
        ''' Delete Me - This is only useful for development & testing '''
        self.initialized = False

    @pyqtSlot(int)
    def on_selectReferenceOscillator_currentIndexChanged(self, index):
        if index == 0:
            self.referenceClock = 60
        if index == 1:
            self.referenceClock = 100

        return self.referenceClock

    # amplitudeData was collected as a bunch of linear 16-bit A/D values which we want
    # to convert to decibels.
    def showAmplData(self, amplBytes):
        self.amplitudeData = []       # Declare amplitude storage that will allow appending
#        nBytes = len(amplBytes) - 2   # Don't want to convert the two end-of-record bytes!
        nBytes = len(amplBytes)
        # Combine 2-bytes into a single 16-bit value because serial
        # reads deliver each data point as as two 8-bit values.
        for x in range(0, nBytes, 2):
            amplitude = (amplBytes[x] << 8) | amplBytes[x+1]
            self.amplitudeData.append(amplitude)
        stepSize = (self.floatStopMHz.value() - self.floatStartMHz.value()) / len(self.amplitudeData)
        self.freqRange = np.arange(self.floatStartMHz.value(), self.floatStopMHz.value(), stepSize)
        self.dataLine.setData(self.freqRange, self.amplitudeData, pen=(155,155,255))

    @pyqtSlot()
    def on_btnPeakSearch_clicked(self):
        # If there are any existing markers remove them first.
        self._clear_marker_text()
        self._clear_peak_markers()
        self._peak_search()

    def _peak_search(self):
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

    def _clear_peak_markers(self):
        try:
            # Clear the marker
            for x in self.marker:
                self.graphWidget.removeItem(x)
            # Prepare marker index for next PeakSearch()
            self.marker = self.marker[0]
        except Exception:
            pass

    def _clear_marker_text(self):
        try:
            # Now clear the marker text
            for x in self.text:
                self.graphWidget.removeItem(x)
                self.text = self.text[1:]
        except Exception:
            pass

    @pyqtSlot()
    def on_btnClearPeakSearch_clicked(self):
        self._clear_marker_text()
        self._clear_peak_markers()

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
        raise NotImplementedError

    @pyqtSlot(bool)
    def on_btnFullSpan_clicked(self, checked):
        raise NotImplementedError

    @pyqtSlot(bool)
    def on_btnLastSpan_clicked(self, checked):
        raise NotImplementedError

    @pyqtSlot()
    def on_btnExit_clicked(self):
        sys.exit()

    @pyqtSlot(float)
    def on_dblCenterMHz_valueChanged(self, centerFreq):
        raise NotImplementedError

    @pyqtSlot(float)
    def on_dblSpanMHz_valueChanged(self, deltaFreq):
        raise NotImplementedError

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

    @pyqtSlot()
    def on_line_edit_cmd_returnPressed(self):
        command = self.line_edit_cmd.text()     # Try letter 'z' for read register 6
        _cmd = command.encode()
        if sp.ser.is_open:
            reg6 = bytearray()                  # create an empty byte array
            sp.ser.write(_cmd)
            time.sleep(0.1)                     # give the Arduino some time to send the data
            bytesToRead = sp.ser.in_waiting
            reg6 += sp.ser.read(bytesToRead)    # collect 4 bytes of data from the Arduino
        else:
            print(name, line(), 'Open the port first.')

    @pyqtSlot(bool)
    def on_chkEnableRFOut_toggled(self, checked):
        if checked:
            cmd_proc.enable_rf_out()
        else:
            cmd_proc.disable_rf_out()
        print(name, line(), 'RF enable status =', cmd_proc.get_hw_status())


    @pyqtSlot(bool)
    def on_chkArduinoLED_toggled(self, checked):
        if checked:
            cmd_proc.turn_Arduino_LED_on()
        else:
            cmd_proc.turn_Arduino_LED_off()

    @pyqtSlot(bool)
    def on_chkLockDetect_clicked(self, checked):
        sa.set_lock_detect(checked)

    @pyqtSlot()
    def on_btnSweep_clicked(self):
        ampl_data_bytes = bytearray()
        command = self.line_edit_cmd.text()     # Try letter 'z' for read register 6
        _cmd = command.encode()
        start = int(self.floatStartMHz.value() * 1e6)
        stop = int(self.floatStopMHz.value() * 1e6)
        step = int(self.dblStepKHz.value() * 1e3)
        steps = list(range(start, stop, step))
        print(name, line(), f'number of data points = {len(steps)}')
        for i, freq in enumerate(steps):
            freqMHz = freq / 1e6
            sa.write_registers(freqMHz, self.referenceClock, True)
            time.sleep(0.005)        # Wait for the Arduino to program the MAX2871 registers
            sp.ser.write(_cmd)
            bytes_to_read = sp.ser.in_waiting
            ampl_data_bytes += sp.ser.read(bytes_to_read)

        self.showAmplData(ampl_data_bytes)

# End MainWindow() class














