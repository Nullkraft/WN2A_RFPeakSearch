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

# -*- coding: utf-8 -*-

# Utility to simplify print debugging.
line = lambda: f'line {str(sys._getframe(1).f_lineno)},'
name = f'File \"{__name__}.py\",'

import sys
import numpy as np
from multiprocessing import Process

from PyQt6 import QtCore
from PyQt6.QtCore import pyqtSlot, QThread #, pyqtSignal, QObject
from PyQt6.QtWidgets import QMainWindow
import pyqtgraph as pg

from .Ui_mainWindow import Ui_MainWindow
import spectrumAnalyzer as sa
import command_processor as cmd_proc
import serial_port as sp


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super().__init__()
        pg.setConfigOptions(useOpenGL=True)
        self.setupUi(self)  # Must come before self.graphWidget.plot()
        self.graphWidget.setYRange(0, 2.5)
        self.graphWidget.setMouseEnabled(x=True, y=False)
        self.dataLine = self.graphWidget.plot()
        # When zooming the graph this updates the x-axis start & stop frequencies
        self.graphWidget.sigXRangeChanged.connect(self.update_start_stop)
        #
        # MAX2871 chip will need to be initialized
        self.initialized = False
        #
        # Request the list of available serial ports and use it to
        # populate the user 'Serial Port' drop-down selection list.
        serial_ports = sp.simple_serial().get_serial_port_list()
        self.cbxSerialPortSelection.addItems(serial_ports)
        #
        # Populate the 'User serial speed drop-down selection list'
        serial_speeds = sp.simple_serial().get_baud_rate_list()
        for baud in serial_speeds:
            self.cbxSerialSpeedSelection.addItem(str(baud), baud)
        # Check for, and reopen, the last serial port that was used.
        sp.simple_serial().port_open()
        # GUI dropdowns should display port and speed values from the port that was opened
        serial_port, serial_speed = sp.simple_serial().read_config()
        port_index = self.cbxSerialPortSelection.findText(serial_port)
        if (port_index >= 0):
            self.cbxSerialPortSelection.setCurrentIndex(port_index)
        speed_index = self.cbxSerialSpeedSelection.findData(str(serial_speed))
        if (speed_index >= 0):
            self.cbxSerialSpeedSelection.setCurrentIndex(speed_index)
        #
        # sa.full_sweep_dict contains values for ref_clock, LO1, LO2, 
        # and LO3 used for controlling the hardware.
        # Loading sa.full_sweep_dict in a separate process speeds up the app load.
        process = Process(target=sa.load_control_dict, args=(sa.full_sweep_dict, 'full_control_ref1.csv'))
        process.start()
#


    @pyqtSlot()
    def on_btnSweep_clicked(self):
        sp.ser.read(sp.ser.in_waiting)                                      # Clear out the serial buffer.
        self.serial_read_thread()                                           # Start the serial read thread to accept sweep data
        sa.sweep(sa.sweep_start, sa.sweep_stop, sa.sweep_step_size, sa.ref_clock)
#        assert len(sa.swept_frequencies_list) != 0, "sa.swept_frequencies_list was empty"
#        self.graphWidget.setXRange(sa.swept_frequencies_list[0], sa.swept_frequencies_list[-1])   # Limit plot to user selected frequency range

    def serial_read_thread(self):
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
            self.worker.finished.connect(self.plot_ampl_data)
            self.thread.finished.connect(self.thread.deleteLater)
            self.thread.start()                                   # After starting the thread...
            self.btnTrigger.setEnabled(False)                     # disable the Trigger button until we're done
            self.thread.finished.connect(lambda: self.btnTrigger.setEnabled(True))
        else:
            print('')
            print('     You have to open the serial port.')
            print('     You must select both a Serial port AND speed.')

    @pyqtSlot()
    def update_start_stop(self):
        view_range = self.graphWidget.viewRange()
#        print(name, line(), f'View range = {view_range}')
        return view_range

    @pyqtSlot()
    def on_btnSendRegisters_clicked(self):
        print(name, line(), f'Reference clock = {sa.ref_clock}')

    @pyqtSlot()
    def on_btnRefreshPortsList_clicked(self):
        for x in range(10):
            self.cbxSerialPortSelection.removeItem(0)
        ports = sp.simple_serial().get_serial_port_list()
        self.cbxSerialPortSelection.addItems(ports)

    @pyqtSlot(int)
    def on_selectReferenceOscillator_currentIndexChanged(self, selected_ref_clock):
        sa.set_reference_clock(selected_ref_clock)
        
    # amplitude was collected as a bunch of linear 16-bit A/D values
    def plot_ampl_data(self, amplBytes):
        self.amplitude = []       # Declare amplitude storage that will allow appending
        nBytes = len(amplBytes)
        # Convert two 8-bit serial bytes into one 16 bit amplitude.
        for x in range(0, nBytes, 2):
            ampl = amplBytes[x] | (amplBytes[x+1] << 8)
            volts = (ampl/1024) * 5
            self.amplitude.append(volts)
        assert len(sa.swept_frequencies_list)==len(self.amplitude)
        self.dataLine.setData(sa.swept_frequencies_list, self.amplitude, pen=(155,155,255))

    @pyqtSlot()
    def on_btnPeakSearch_clicked(self):
        # If there are any existing markers remove them first.
        self._clear_marker_text()
        self._clear_peak_markers()
        self._peak_search()

    def _peak_search(self):
        self.marker = np.array([pg.ArrowItem()])     # Create a growable array of markers
        self.text = np.array([pg.TextItem()])        # Make a growable array of labels
        # idx is sorted so that idx[0] points to the highest amplitude in the
        # amplitudeData array, idx[1] points to the second highest and so on.
        idx = sa.peakSearch(self.amplitude, self.numPeakMarkers.value())
        # Get the number of markers from the user control on the front panel
        num_markers = self.numPeakMarkers.value()
        # Create and add Peak Markers to the graph.
        for i in range(min(num_markers, len(idx))):
            self.marker = np.append(self.marker, pg.ArrowItem())  # Add a place for a new marker
            self.text = np.append(self.text, pg.TextItem())       # Add a place for a new label
            self.marker[i] = pg.ArrowItem(angle=-90, tipAngle=40, tailWidth=10, pen={'color': 'w', 'width': 1})
            frequency = self.freqRange[idx[i]]
            amplitude = self.amplitude[idx[i]]
            self.marker[i].setPos(frequency, amplitude)  # x-axis = frequency, y-axis = amplitude
            frequency_text = str('%.5f' % self.freqRange[idx[i]])
            amplitude_text = str('%.2f' % self.amplitude[idx[i]])
            markerLabel = frequency_text + ' MHz\n' + amplitude_text + ' V'
            self.text[i] = pg.TextItem(markerLabel, anchor = (0.5, 1.5), border = 'w', fill = (0, 0, 255, 100))
            self.graphWidget.addItem(self.marker[i])
            self.graphWidget.addItem(self.text[i])
            frequency_pos = self.freqRange[idx[i]]
            amplitude_pos = self.amplitude[idx[i]]
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
        sa.toggle_arduino_led(checked)

    @pyqtSlot()
    def on_btn_get_arduino_msg_clicked(self):
        """
        Request the Arduino message containing version number and date
        """
        sa.get_version_message()

    @pyqtSlot()
    def on_dbl_attenuator_dB_editingFinished(self):
        """
        Reduce the RF input signal using the onboard Digital Attenuator

        @param 0 to 31.75 dB
        @type double
        """
        dB = float(self.dbl_attenuator_dB.value())      # Read attenuator value from user control
        sa.set_attenuator(dB)

    @pyqtSlot()
    def on_btn_open_serial_port_clicked(self):
        """
        Open a new serial port at the user selected port and baud_rate
        """
        sel_baud = self.cbxSerialSpeedSelection.currentText()
        sel_port = self.cbxSerialPortSelection.currentText()
        sp.simple_serial().port_open(baud_rate=sel_baud, port=sel_port)
    
    @pyqtSlot()
    def on_btn_set_frequency_clicked(self):
        """
        Program the SA to a single frequency for testing
        """
        ref_clock, LO1_cntl_code, LO2_cntl_code = sa.full_sweep_dict[100.0]
        cmd_proc.enable_60MHz_ref_clock()
        cmd_proc.sel_315MHz_adc()   # Selects LO2 path
        LO1_cntl_code = LO1_cntl_code.to_bytes(4, byteorder='little')
        cmd_proc.set_LO(cmd_proc.LO1_pos5dBm, LO1_cntl_code)
        LO2_control_code = LO2_cntl_code.to_bytes(4, byteorder='little')
        cmd_proc.set_LO(cmd_proc.LO2_pos5dBm, LO2_control_code)
    
    @pyqtSlot()
    def on_btnCalibrate_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError
    
    @pyqtSlot()
    def on_floatStartMHz_editingFinished(self):
        start_in_MHz = self.floatStartMHz.value()
        # Only update sa.sweep_start if the value() has changed
        if sa.sweep_start != start_in_MHz:
            sa.sweep_start = start_in_MHz

    @pyqtSlot()
    def on_floatStopMHz_editingFinished(self):
        stop_in_MHz = self.floatStopMHz.value()
        # Only update sa.sweep_stop if the value() has changed
        if sa.sweep_stop != stop_in_MHz:
           sa.sweep_stop = stop_in_MHz
    
    @pyqtSlot()
    def on_intStepKHz_editingFinished(self):
        step_in_MHz = self.intStepKHz.value()
        # Only update sa.sweep_step_size if the value() has changed
        if sa.sweep_step_size != step_in_MHz:
            sa.sweep_step_size = step_in_MHz














