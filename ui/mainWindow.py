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

# Utility functions used for displaying the name and the line number
# of the source file. Requires: import sys
name = lambda: f'File \"{__name__}.py\",'
line = lambda: f'line {str(sys._getframe(1).f_lineno)},'


import sys
from time import sleep#, perf_counter
import numpy as np
import pickle

from PyQt6 import QtCore, QtGui
from PyQt6.QtCore import pyqtSlot, QThread #, pyqtSignal, QObject
from PyQt6.QtWidgets import QMainWindow
import pyqtgraph as pg
from pathlib import Path

from .Ui_mainWindow import Ui_MainWindow
import spectrumAnalyzer as sa
from spectrumAnalyzer import sa_control as sa_ctl
import command_processor as cmd_proc
import serial_port as sp


last_center_MHz_value = 0


class MainWindow(QMainWindow, Ui_MainWindow):
    last_N = -1     # for monitoring the amount of data from serial_read()

    def __init__(self):
        super().__init__()
        pg.setConfigOptions(useOpenGL=True, enableExperimental=True)
        self.setupUi(self)  # Must come before self.graphWidget.plot()
        self.graphWidget.setYRange(0, 2.5)
        self.graphWidget.setMouseEnabled(x=True, y=False)
        self.dataLine = self.graphWidget.plot()
        # When zooming the graph this updates the x-axis start & stop frequencies
        self.graphWidget.sigXRangeChanged.connect(self.update_start_stop)
        #
        # MAX2871 chip will need to be initialized
        self.initialized = False
        self.amplitude = []       # Declare amplitude storage that will allow appending
        #
        # Request the list of available serial ports and use it to
        # populate the user 'Serial Port' drop-down selection list.
        ''' ~~~~~~ Setup serial port ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ '''
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
        ''' ~~~~~~ End serial port ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ '''
        #
        # sa.full_sweep_dict contains values for ref_clock, LO1, LO2, 
        # and LO3 used for controlling the Spectrum Analyzer hardware.
        ''' ~~~~~~ Load control file ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ '''
        control_file = Path('full_control.pickle')
#        control_file = Path('full_control_ref1.pickle')
#        control_file = Path('full_control_ref2.pickle')
        if not control_file.exists():
            print(name(), line(), f'Missing control file "{control_file}"')
        with open(control_file, 'rb') as f:
            sa.full_sweep_dict = pickle.load(f)
        ''' ~~~~~~ End control file ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ '''

        # RFin_steps.pickle is used when creating the list of frequencies to sweep
        RFin_file = Path('RFin_steps.pickle')
        if not RFin_file.exists():
            print(name(), line(), f'Missing RFin file "{RFin_file}"')
        with open('RFin_steps.pickle', 'rb') as f:
            self.RFin_list = pickle.load(f)
        """ List(s) of amplitudes collected from ref1 and ref2 full sweeps with NO input """
        with open('amplitude_from_full_sweep_of_ref1.pickle', 'rb') as f:   # 3 million amplitudes collected with ref1
            self.r1_ampl_list = pickle.load(f)
        with open('amplitude_from_full_sweep_of_ref2.pickle', 'rb') as f:   # 3 million amplitudes collected with ref2
            self.r2_ampl_list = pickle.load(f)


    @pyqtSlot()
    def on_btnSweep_clicked(self):
        self.label_sweep_status.setText("Sweep in progress...")
        QtGui.QGuiApplication.processEvents()
#        sp.ser.read(sp.ser.in_waiting)         # Clear out the serial buffer.
#        self.serial_read_thread()              # Start the serial read thread to accept sweep data
        sa.sa_control().sweep()
        self.label_sweep_status.setText("Sweep complete")
        if self.chk_plot_enable.isChecked():
            self.plot_ampl_data(sp.simple_serial.data_buffer_in)
        QtGui.QGuiApplication.processEvents()

    last_n = -1
    def progress_report(self, n):
        if n != self.last_n:
            self.last_n = n
#            print(name(), line(), f'Len in_buff = {n}')
    
    
    def clear_last_N(self):
        self.last_n = -1


    def serial_read_thread(self):
        """
        Read back data points in a separate thread so we don't block the gui.
        """
        if sp.ser.is_open:
            self.thread = QThread()                               # Create a separate thread for serial reads
            self.worker = sp.simple_serial()                      # Function for reading from the serial port
            self.worker.moveToThread(self.thread)                 # Serial reads happen inside its own thread
            self.thread.started.connect(self.worker.read_serial)  # Connect to signals...
            self.worker.progress.connect(self.progress_report)
            self.worker.finished.connect(self.clear_last_N)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.plot_ampl_data)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            self.thread.start()                                   # After starting the thread...
#            self.btnSweep.setEnabled(False)                       # disable the sweep button until we're done
            self.thread.finished.connect(lambda: self.btnSweep.setEnabled(True))
        else:
            print('')
            print('     You have to open the serial port.')
            print('     You must select both a Serial port AND speed.')

    @pyqtSlot()
    def update_start_stop(self):
        view_range = self.graphWidget.viewRange()
#        print(name(), line(), f'View range = {view_range}')
        return view_range

    @pyqtSlot()
    def on_btnRefreshPortsList_clicked(self):
        for x in range(10):
            self.cbxSerialPortSelection.removeItem(0)
        ports = sp.simple_serial().get_serial_port_list()
        self.cbxSerialPortSelection.addItems(ports)

    @pyqtSlot(int)
    def on_selectReferenceOscillator_currentIndexChanged(self, selected_ref_clock):
        sa.set_reference_clock(selected_ref_clock)
        
    def plot_ampl_data(self, amplBytes):
        x_axis = list()
        y_axis = list()
        self.amplitude.clear()
        # Convert two 8-bit serial bytes into one 16 bit amplitude
        hi_byte_list = amplBytes[::2]
        lo_byte_list = amplBytes[1::2]
        index = 0
        for hi_byte, lo_byte in zip(hi_byte_list, lo_byte_list):
            if hi_byte > 3:
                hi_byte = (hi_byte & 15)        # Recover the amplitude value despite it not locking
#                print(name(), line(), f'freq, {sa_ctl.swept_freq_list[index]}, No lock: Hi byte = {hi_byte} : Lo byte = {lo_byte}')
            ampl = (hi_byte << 8) | lo_byte     # Combine MSByte/LSByte into an amplitude word
            index += 1
            volts = (ampl/2**10) * sa.sa_control().adc_Vref()       # Convert 10 bit ADC counts to Voltage
            self.amplitude.append(volts)
        argsort_index_list = np.argsort(sa_ctl.swept_freq_list)

        for idx in argsort_index_list:
            x_axis.append(sa_ctl.swept_freq_list[idx])  # Sort the frequency data in ascending order
            y_axis.append(self.amplitude[idx])          # And make the amplitude match the same order
        self.graphWidget.setXRange(x_axis[0], x_axis[-1])   # Limit plot to user selected frequency range
        yellow = (150, 255, 150)
        self.dataLine.setData(x_axis, y_axis, pen=yellow)
#        purple = (75, 50, 255)
#        self.dataLine.setData(sa_ctl.swept_freq_list, self.amplitude, pen=purple)

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
        sa.sa_control().set_attenuator(dB)

    @pyqtSlot()
    def on_btn_open_serial_port_clicked(self):
        """
        Open a new serial port at the user selected port and baud_rate
        """
        sel_baud = self.cbxSerialSpeedSelection.currentText()
        sel_port = self.cbxSerialPortSelection.currentText()
        sp.simple_serial().port_open(baud_rate=sel_baud, port=sel_port)
        sleep(2)
    
    @pyqtSlot()
    def on_btn_set_frequency_clicked(self):
        """
        Program the SA to a single frequency for testing
        """
        ref_clock, LO1_cntl_code, LO2_cntl_code = sa.full_sweep_dict[100.0]
        cmd_proc.enable_60MHz_ref_clock()
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
        self.set_steps()


    @pyqtSlot()
    def on_floatStopMHz_editingFinished(self):
        self.set_steps()

    
    @pyqtSlot()
    def on_intStepKHz_editingFinished(self):
        self.set_steps()


    def float_to_index(self, hash_value):
        num_slice = round(hash_value, 3)                # Limit to 3 decimal places before converting...
        stringified = "{:.3f}".format(num_slice)        # to a string needed for the next step.
        decimal_removed = stringified.replace(".", "")  # Works the same as multiplying by 1000 and then...
        slice_index = int(decimal_removed)              # creates the index for the RFin_list
        return slice_index


    def get_swept_freq_list(self, start: int, stop: int, step: int) -> list:
        """ Get the sweep list from the user interface. This uses the
            following lists already loaded from file:
            1) RFin_list
            2) r1_ampl_list
            3) r2_ampl_list
        """
        ref1_out_list = list()
        ref2_out_list = list()
        for idx in range(start, stop, step):
            freq = self.RFin_list[idx]       # Convert idx to a key for the control dictionaries
            if self.r2_ampl_list[idx] > self.r1_ampl_list[idx]:
                ref1_out_list.append(freq)
            else:
                ref2_out_list.append(freq)
        ''' Because python won't we manually include the stop value in the plot '''
        freq = self.RFin_list[stop]          # Convert idx to a key for the control dictionaries
        if self.r2_ampl_list[stop] > self.r1_ampl_list[stop]:
            ref1_out_list.append(freq)
        else:
            ref2_out_list.append(freq)
        return ref1_out_list + ref2_out_list    # Return the list of frequencies to be swept


    def set_steps(self):
        """
        Public method Create a list of frequencies for sweeping
        """
        MHz = 1000
        # Get the start/stop/step values for creating the list of sweep frequencies
        sa.sweep_start_freq = self.floatStartMHz.value()
        sa.sweep_stop_freq = self.floatStopMHz.value()
        sa.sweep_step_size = round(self.intStepKHz.value() / MHz, 3)
        # Convert the start/stop/step 'values' into indexes for the sweep frequencies list
        start_slice = self.float_to_index(sa.sweep_start_freq)
        stop_slice = self.float_to_index(sa.sweep_stop_freq)
        step_slice = self.float_to_index(sa.sweep_step_size)
        # Fill the list with new sweep frequencies
        sa_ctl.swept_freq_list = self.get_swept_freq_list(start_slice, stop_slice, step_slice)  # Way faster than np.arange()
        # Fill in the user control so they can see how many steps it will take
        sa.sweep_num_steps = len(sa_ctl.swept_freq_list)
        self.numFrequencySteps.setValue(sa.sweep_num_steps)
        pass

    
    @pyqtSlot()
    def on_dblCenterMHz_editingFinished(self):
        """
        Public slot What happens if I try to run it a second time.
        """
        global last_center_MHz_value
        if self.dblCenterMHz.value() != last_center_MHz_value:
            sa.sa_ctl().set_center_freq(self.dblCenterMHz.value())
            last_center_MHz_value = self.dblCenterMHz.value()
        else:
            pass


    @pyqtSlot(float)
    def on_dbl_rfin_frequency_valueChanged(self, RFin):
        floating_point_frequency = str(RFin)
        index = int(floating_point_frequency.replace('.', ''))
        with open('LO1_ref1_freq_steps.pickle', 'rb') as f:
            LO1_freq_list = pickle.load(f)
        with open('LO2_ref1_freq_steps.pickle', 'rb') as f:
            LO2_freq_list = pickle.load(f)

        LO1_frequency = LO1_freq_list[index]
        LO2_frequency = LO2_freq_list[index]
        self.label_LO1_freq.setText(f'LO1:  {LO1_frequency} MHz')
        self.label_LO2_freq.setText(f'LO2:  {LO2_frequency} MHz')
 
 
if __name__ == '__main__':
    print()
#    freeze_support()







