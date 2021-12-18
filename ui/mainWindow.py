# -*- coding: utf-8 -*-

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot, QThread #, pyqtSignal, QObject
from PyQt5.QtWidgets import QMainWindow
import sys
import time
import pyqtgraph as pg
import numpy as np

import concurrent.futures

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
        self.referenceClock = 60
        self.initialized = False        # MAX2871 chip will need to be initialized
      # Populate the serial port selection list
        ports = ss.get_os_ports()
        self.cbxSerialPortSelection.addItems(ports)
      # Populate the Serial Speed selection list
#        speeds = ss.get_os_baudrates()
        speeds = ss.get_os_baudrates()
        for x in speeds:
            self.cbxSerialSpeedSelection.addItem(str(x), x)
        ss.port_open()  # Checks to see if it can reopen the last port that was used.

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
            sa.max2871_write_registers(freq, self.referenceClock, self.initialized)
            self.initialized = True


    def __cmd(self, num_points):
        """
        The Arduino will only simulate a fixed number of RF data points and
        only sees 1=256*16bits 2=512 3=768 4=1024 5=1280 (6 or greater)=1536
        """
        arduinoCmds = [b'1', b'2', b'3', b'4', b'5', b'6']
        selection = (num_points // 256) - 1                # selection = floor(num_points/256)-1
        selection = 5 if selection > 5 else selection
        return arduinoCmds[selection]


    @pyqtSlot()
    def on_btnTrigger_clicked(self):
        """
        Tell the Arduino how many data points we want to read from the A2D.
        """
        num_data_points = self.numDataPoints.value()
        arduino_command = self.__cmd(num_data_points)
        sp.ser.write(arduino_command)   # Send a new command to the Arduino
        self.request_data()

    def request_data(self):
        """
        Read back data points in a separate thread so we don't block the gui.
        """
        if sp.ser.is_open:
            self.thread = QThread()                                 # Create a separate thread for serial reads
            self.worker = sp.simple_serial()                        # Function for reading from the serial port
            self.worker.moveToThread(self.thread)                   # Serial reads happen inside its own thread
            self.thread.started.connect(self.worker.read_serial)    # Connect to signals...
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.worker.finished.connect(self.show_ampl_data)
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

    @pyqtSlot()
    def on_btn_reinitialize_clicked(self):
        ''' Delete Me - This is only useful for development & testing '''
        command = self.line_edit_cmd.text()
        print(name, line(), f' : You typed {command}')

    @pyqtSlot(int)
    def on_selectReferenceOscillator_currentIndexChanged(self, index):
        if index == 0:
            self.referenceClock = None
            cmd_proc.disable_all_ref_clocks()
        if index == 1:
            self.referenceClock = 60
            cmd_proc.enable_60MHz_ref_clock()
        if index == 2:
            self.referenceClock = 100
            cmd_proc.enable_100MHz_ref_clock()
        return self.referenceClock

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
        pass

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
            cmd_proc.turn_Arduino_LED_on()
        else:
            cmd_proc.turn_Arduino_LED_off()

    @pyqtSlot()
    def on_btn_get_arduino_msg_clicked(self):
        """
        Request the Arduino message containing version number and date
        """
        print(name, line(), f'Arduino Message = {cmd_proc.get_message()}')

    @pyqtSlot(bool)
    def on_chkLockDetect_clicked(self, checked):
        sa.set_lock_detect(checked)


#    @pyqtSlot()
#    def on_btnSweep_clicked(self):
#        """
#        TODO:   Write adf4356_n() for programming LO1
#                Cleanup max2871_fmn()
#                Make serial flow bidirectional with Arduino
#                Do a git commit & push
#        """
#        # Required Spectrum Analyzer hardware setup
#        cmd_proc.turn_Arduino_LED_off()
#        tmp_bytes = 0x00000cff.to_bytes(4, byteorder='little')  # Select 60 MHz reference clock
#        sp.ser.write(tmp_bytes)
#        tmp_bytes = 0x000f21ff.to_bytes(4, byteorder='little')  # Set LO1 to +2 dBm and freq #15 (0x0F)
#        sp.ser.write(tmp_bytes)
#        tmp_bytes = 0x001323ff.to_bytes(4, byteorder='little')  # Set LO2 to +2 dBm followed by 19 freqs
#        sp.ser.write(tmp_bytes)
#
#        # Generate a set of test data that can be replaced with user
#        # selected start, stop and step values.
#        start_freq = 3000.0
#        stop_freq =  6000.0
#        num_freqs = 15385
#        freq_data = np.linspace(start_freq, stop_freq, num_freqs)
#        num_points = len(freq_data)
#        count = 0
#        step = 8
#        start = time.perf_counter()
#        while (num_points):
#            for freq in freq_data[count: count + step]:
#                FMN = sa.max2871_fmn(freq, self.referenceClock)
#                tmp_bytes = FMN.to_bytes(4, byteorder='little')
##                sp.ser.write(tmp_bytes)
#                num_points -= 1;
#            count += step           # Move to the next 8 data points in freq_data
#            if num_points < 8:      # If there are fewer than 8 remaining data points...
#                step = num_points
#        print(name, line(), f'Sent {len(freq_data)} data points in {time.perf_counter() - start} seconds.')
#        print(name, line(), f'Finished sending {len(freq_data)} data points to Arduino')


    @pyqtSlot()
    def on_btnSweep_clicked(self):
        """ Learning how to send byte commands to the Arduino """
        program_LO1 = 0xDEAD21FF
        LO1 = program_LO1.to_bytes(4, byteorder='little')
        sp.ser.write(LO1)
        start = time.perf_counter()
        self.sweep(100, 1000.0, num_steps=5000)
        print(name, line(), f'Delta = {time.perf_counter()-start}')


    def sweep(self, start_freq: float, stop_freq: float, step_size: float = None, num_steps: int = 5, ref_clock: float = 60):
        start_freq = float(start_freq)
        stop_freq = float(stop_freq)
        ref_clock = float(ref_clock)

        LO1_freqs = np.linspace(3600, 6600, 101)
        LO2_freqs = np.linspace(3900, 3930, 601)
        print(LO1_freqs)

        LO1_map = map(sa.adf4356_n, LO1_freqs)
        LO2_map = map(sa.max2871_fmn, LO2_freqs)
#        for n_word in LO2_map:
#            print(n_word)
#            print(name, line(), f'LO2 value = {n_word}')
#            sa.adf4356_write_registers(0, n_word)

# End MainWindow() class

