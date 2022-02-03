# -*- coding: utf-8 -*-

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot, QThread #, pyqtSignal, QObject
from PyQt5.QtWidgets import QMainWindow
import sys
#import time
import pyqtgraph as pg
import numpy as np

#import concurrent.futures

from .Ui_mainWindow import Ui_MainWindow

# Functions specific to the operation of the WN2A Spectrum Analyzer hardware, hopefully.
# Including setting up the serial port.
import spectrumAnalyzer as sa
import serial_port as sp
import command_processor as cmd_proc

ss = sp.simple_serial()

# Utility to simplify print debugging.
line = lambda : sys._getframe(1).f_lineno
name = __name__



class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        pg.setConfigOptions(useOpenGL=True)
        self.setupUi(self)  # Must come before self.plot[]
        self.graphWidget.setYRange(0, 70000)
        self.dataLine = self.graphWidget.plot()
      #
        sa.referenceClock = 60
        self.initialized = False        # MAX2871 chip will need to be initialized
      # Query the O/S for a list of ports to populate the serial port selection list with
        ports = ss.get_os_ports()
      # Populate the serial port selection list
        self.cbxSerialPortSelection.addItems(ports)
      # Populate the Serial Speed selection list
        speeds = ss.get_os_baudrates()
        for x in speeds:
            self.cbxSerialSpeedSelection.addItem(str(x), x)
      # Check for, and reopen, the last serial port that was used.
        ss.port_open()
      # And now the user dropdowns need to be updated with the port and speed
        foundPortIndex = self.cbxSerialPortSelection.findText(ss._port)
        if (foundPortIndex >= 0):
            self.cbxSerialPortSelection.setCurrentIndex(foundPortIndex)
        foundSpeedIndex = self.cbxSerialSpeedSelection.findData(ss._baud)
        if (foundSpeedIndex >= 0):
            self.cbxSerialSpeedSelection.setCurrentIndex(foundSpeedIndex)


    @pyqtSlot()
    def on_btnSendRegisters_clicked(self):
        """
        Public slot
        SendRegisters() calls the Spectrum Analyzer code to generate new
        register values for programming the MAX2871 to set a new frequency.
        The amplitude of that frequency is then digitized (A2D) by the
        Arduino and sent back to the PC for plotting and analysis.
        """

        if sp.ser.is_open:
            freq = self.floatStopMHz.value()
            if 23.5 < freq < 6000:
                fmn = sa.MHz_to_fmn(freq)
                cmd_proc.set_max2871_freq(fmn)


    def max2871_set_freq(self, RFout):
        FMN = sa.MHz_to_fmn(RFout)
        cmd_proc.LO_device_register(FMN)


    def __cmd(self, num_points):
        pass


    @pyqtSlot()
    def on_btnTrigger_clicked(self):
        pass


    def request_data(self):
        """
        Read back data points in a separate thread so we don't block the gui.
        """
        if sp.ser.is_open:
            self.thread = QThread()                               # Create a separate thread for serial reads
            self.worker = sp.simple_serial()                      # Function for reading from the serial port
            self.worker.moveToThread(self.thread)                 # Serial reads happen inside its own thread
            self.thread.started.connect(self.worker.read_serial)  # Connect to signals...
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.worker.finished.connect(self.show_ampl_data)
            self.thread.finished.connect(self.thread.deleteLater)
            self.thread.start()                                   # After starting the thread...
            self.btnTrigger.setEnabled(False)                     # disable the Trigger button until we're done
            self.thread.finished.connect(lambda: self.btnTrigger.setEnabled(True))
        else:
            print('')
            print('     You have to open the serial port.')
            print('     You must select both a Serial port AND speed.')

    @pyqtSlot(str)
    def on_cbxSerialPortSelection_activated(self, selected_port):
        ss.set_port(selected_port)

    @pyqtSlot(str)
    def on_cbxSerialSpeedSelection_activated(self, speed_str):
        ss.set_speed(speed_str)

    @pyqtSlot()
    def on_btnRefreshPortsList_clicked(self):
        for x in range(10):
            self.cbxSerialPortSelection.removeItem(0)
        ports = ss.get_os_ports()
        self.cbxSerialPortSelection.addItems(ports)

    @pyqtSlot(int)
    def on_selectReferenceOscillator_currentIndexChanged(self, index):
        if index == 0:
            sa.referenceClock = None
            cmd_proc.disable_all_ref_clocks()
        if index == 1:
            sa.referenceClock = 60
            cmd_proc.enable_60MHz_ref_clock()
        if index == 2:
            sa.referenceClock = 100
            cmd_proc.enable_100MHz_ref_clock()
        print(name, line(), sa.referenceClock)
        return sa.referenceClock

    # amplitudeData was collected as a bunch of linear 16-bit A/D values which we want
    # to convert to decibels.
    def show_ampl_data(self, amplBytes):
        self.amplitudeData = []       # Declare amplitude storage that will allow appending
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

        # Create and add Peak Markers to the graph. Number of peak markers is chosen by the user.
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

    @pyqtSlot()
    def on_btnExit_clicked(self):
        sys.exit()

    @pyqtSlot(bool)
    def on_chkShowGrid_toggled(self, checked):
        self.graphWidget.showGrid(x=checked, y=checked)

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
        """ Create command name for disble LO3? """
        cmd_str = self.line_edit_cmd.text()
        cmd_int = int(cmd_str, 16)
        tmp_bytes = cmd_int.to_bytes(4, byteorder='little')
        sp.ser.write(tmp_bytes)     # Leave me alone!  I'm for testing...





    @pyqtSlot()
    def on_btn_disable_LO2_RFout_clicked(self):
        """
        Disable the RF output of the MAX2871 chip designated as LO2
        """
        cmd_proc.disable_LO2_RFout()

    @pyqtSlot()
    def on_btn_disable_LO3_RFout_clicked(self):
        """
        Disable the RF output of the MAX2871 chip designated as LO3
        """
        cmd_proc.disable_LO3_RFout()

    @pyqtSlot(bool)
    def on_chkArduinoLED_toggled(self, checked):
        if checked:
            cmd_proc.LED_on()
        else:
            cmd_proc.LED_off()

    @pyqtSlot()
    def on_btn_get_arduino_msg_clicked(self):
        """
        Request the Arduino message containing version number and date
        """
        print(name, line(), f'Arduino Message = {cmd_proc.get_message()}')


    @pyqtSlot()
    def on_btnSweep_clicked(self):
        ref_clock = sa.referenceClock
        start_freq = self.floatStartMHz.value()
        stop_freq = self.floatStopMHz.value()
        sa.sweep(start_freq, stop_freq, ref_clock)


    @pyqtSlot()
    def on_dbl_attenuator_dB_editingFinished(self):
        """
        Reduce the RF input signal using the onboard Digital Attenuator

        @param 0 to 31.75 dB
        @type double
        """
        dB = float(self.dbl_attenuator_dB.value())
        cmd_proc.set_attenuator(dB)

# End MainWindow() class





















