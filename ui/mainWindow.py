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
from time import sleep, perf_counter
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
#import command_processor as cmd_proc
import serial_port as sp


last_center_MHz_value = 0


class MainWindow(QMainWindow, Ui_MainWindow):
    last_N = -1     # for monitoring the amount of data from serial_read()

    def __init__(self):
        super().__init__()
        pg.setConfigOptions(useOpenGL=True, enableExperimental=True)
        self.setupUi(self)  # Must come before self.graphWidget.plot()
        self.graphWidget.setYRange(15.5, -55)     # dBm scale
        self.graphWidget.setMouseEnabled(x=True, y=False)
        self.dataLine = self.graphWidget.plot()
        # When zooming the graph this updates the x-axis start & stop frequencies
        self.graphWidget.sigXRangeChanged.connect(self.update_start_stop)
        horiz_line_item = pg.InfiniteLine(pos=(1), angle=(0), pen=(255, 128, 255), movable=True, span=(0, 1))
        vert_line_item = pg.InfiniteLine(pos=(1), pen=(128, 255, 128), movable=True, span=(0, 1))
        self.graphWidget.addItem(horiz_line_item)
        self.graphWidget.addItem(vert_line_item)
        #
        # MAX2871 chip will need to be initialized
        self.initialized = False
        self.amplitude = list()     # Declare amplitude storage that will allow appending
        self.r1_hi_ampl_list = list()
        self.r1_lo_ampl_list = list()
        self.r2_hi_ampl_list = list()
        self.r2_lo_ampl_list = list()
        self.x_axis = list()
        self.y_axis = list()
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
        # RFin_steps.pickle is used when creating the list of frequencies to sweep
        RFin_file = Path('RFin_steps.pickle')
        if not RFin_file.exists():
            print(name(), line(), f'Missing RFin file "{RFin_file}"')
        with open('RFin_steps.pickle', 'rb') as f:
            self.RFin_list = pickle.load(f)
        # Loading the initial control file (in the background?)
        self.load_control_file('control.pickle')


    def load_control_file(self, control_fname: str=None):
        if control_fname is None:
            print(name(), line(), 'You must enter a control file name')
        else:
            control_file = Path(control_fname)
        if control_file.exists():
            with open(control_file, 'rb') as f:
                sa_ctl.all_frequencies_dict = pickle.load(f)
                print(name(), line(), f'Control file "{control_file}" loaded')
        else:
            print(name(), line(), f'Missing control file "{control_file}"')


    @pyqtSlot()
    def on_btnSweep_clicked(self):
        start = perf_counter()
        self.label_sweep_status.setText("Sweep in progress...")
        QtGui.QGuiApplication.processEvents()
        sp.simple_serial.data_buffer_in.clear()     # Clear the serial data buffer before sweeping
        sweep_complete = sa.sa_control().sweep()
        print(name(), line(), f'Sweep & plot of {len(self.amplitude)} data points took {round(perf_counter()-start, 6)} seconds')
        if not sweep_complete:
           print(name(), line(), 'Sweep stopped by user')
        self.label_sweep_status.setText("Sweep complete")
        if self.chk_plot_enable.isChecked() and sweep_complete:
            self.plot_ampl_data(sp.simple_serial.data_buffer_in)
        QtGui.QGuiApplication.processEvents()


    @pyqtSlot()
    def on_btnCalibrate_clicked(self):
        start = perf_counter()
        self.label_sweep_status.setText("Amplitude cal in progress...")
        QtGui.QGuiApplication.processEvents()

        ''' Run ref1 HI calibrations '''
        self.set_steps('control_ref1_HI.pickle')
        sp.simple_serial.data_buffer_in.clear()     # Clear the serial data buffer before sweeping
        calibration_complete = sa.sa_control().sweep()
        if calibration_complete:
            volts_list = [round(v, 3) for v in self._amplitude_bytes_to_volts(sp.simple_serial.data_buffer_in)]
        else:
            print(name(), line(), 'Calibration cancelled by user')
        with open('amplitude_ref1_HI.pickle', 'wb') as f:
            pickle.dump(volts_list, f, protocol=pickle.HIGHEST_PROTOCOL)

        ''' Run ref2 HI calibrations '''
        self.set_steps('control_ref2_HI.pickle')
        sp.simple_serial.data_buffer_in.clear()     # Clear the serial data buffer before sweeping
        calibration_complete = sa.sa_control().sweep()
        if calibration_complete:
            volts_list = [round(v, 3) for v in self._amplitude_bytes_to_volts(sp.simple_serial.data_buffer_in)]
        else:
            print(name(), line(), 'Calibration cancelled by user')
        with open('amplitude_ref2_HI.pickle', 'wb') as f:
            pickle.dump(volts_list, f, protocol=pickle.HIGHEST_PROTOCOL)

        ''' Run ref1 LO calibrations '''
        self.set_steps('control_ref1_LO.pickle')
        sp.simple_serial.data_buffer_in.clear()     # Clear the serial data buffer before sweeping
        calibration_complete = sa.sa_control().sweep()
        if calibration_complete:
            volts_list = [round(v, 3) for v in self._amplitude_bytes_to_volts(sp.simple_serial.data_buffer_in)]
        else:
            print(name(), line(), 'Calibration cancelled by user')
        with open('amplitude_ref1_LO.pickle', 'wb') as f:
            pickle.dump(volts_list, f, protocol=pickle.HIGHEST_PROTOCOL)

        ''' Run ref2 LO calibrations '''
        self.set_steps('control_ref2_LO.pickle')
        sp.simple_serial.data_buffer_in.clear()     # Clear the serial data buffer before sweeping
        calibration_complete = sa.sa_control().sweep()
        if calibration_complete:
            volts_list = [round(v, 3) for v in self._amplitude_bytes_to_volts(sp.simple_serial.data_buffer_in)]
        else:
            print(name(), line(), 'Calibration cancelled by user')
        with open('amplitude_ref2_LO.pickle', 'wb') as f:
            pickle.dump(volts_list, f, protocol=pickle.HIGHEST_PROTOCOL)

        self.label_sweep_status.setText("Calibration complete")
        QtGui.QGuiApplication.processEvents()
        print(name(), line(), f'Calibration of {len(volts_list)} data points took {round(perf_counter()-start, 6)} seconds')



    @pyqtSlot()
    def on_btn_make_control_dict_clicked(self):
        '''
        Protected method The full control dictionary is used for programming
        the 3 LO chips on the Spectrum Analyzer board. The dictionary is created
        by comparing the amplitudes that were found when running a full sweep
        with ref1 selected and then ref2. Whichever amplitude is lower then the
        control codes for that frequency are copied to the control_dict.
        '''
        ampl_file_1 = Path('amplitude_ref1_HI.pickle')
        ampl_file_2 = Path('amplitude_ref2_HI.pickle')
        if ampl_file_1.exists() and ampl_file_2.exists():
            if not self.r1_hi_ampl_list:
                """ List(s) of amplitudes collected from ref1 and ref2 full sweeps with NO input """
                with open('amplitude_ref1_HI.pickle', 'rb') as f:   # 3 million amplitudes collected with ref1
                    self.r1_hi_ampl_list = pickle.load(f)
                with open('amplitude_ref1_LO.pickle', 'rb') as f:   # 3 million amplitudes collected with ref1
                    self.r1_lo_ampl_list = pickle.load(f)
                with open('amplitude_ref2_HI.pickle', 'rb') as f:   # 3 million amplitudes collected with ref2
                    self.r2_hi_ampl_list = pickle.load(f)
                with open('amplitude_ref2_LO.pickle', 'rb') as f:   # 3 million amplitudes collected with ref2
                    self.r2_lo_ampl_list = pickle.load(f)
                with open('control_ref1_HI.pickle', 'rb') as f:
                    control_ref1_hi_dict = pickle.load(f)
                with open('control_ref1_LO.pickle', 'rb') as f:
                    control_ref1_lo_dict = pickle.load(f)
                with open('control_ref2_HI.pickle', 'rb') as f:
                    control_ref2_hi_dict = pickle.load(f)
                with open('control_ref2_LO.pickle', 'rb') as f:
                    control_ref2_lo_dict = pickle.load(f)

            ampl_ref1_list = list()
            ampl_ref2_list = list()
            control_r1_dict = dict()
            control_r2_dict = dict()
            delta_list = list()

            ''' 2 Amplitude files and 2 control files are need from Compare & Combine '''
            for idx, freq in enumerate(self.RFin_list):
                ''' Create ampl_ref1_list & control_r1_dict by 
                    Compare & Combine r1 LO & HI amplitudes '''
                if self.r1_lo_ampl_list[idx] < self.r1_hi_ampl_list[idx]:
                    ampl_ref1_list.append(self.r1_lo_ampl_list[idx])
                    control_r1_dict[freq] = control_ref1_lo_dict[freq]
                else:
                    ampl_ref1_list.append(self.r1_hi_ampl_list[idx])
                    control_r1_dict[freq] = control_ref1_hi_dict[freq]

                ''' Compare amplitudes of ref2 lo-side vs. hi-side '''
                if self.r2_lo_ampl_list[idx] < self.r2_hi_ampl_list[idx]:
                    ampl_ref2_list.append(self.r2_lo_ampl_list[idx])
                    control_r2_dict[freq] = control_ref2_lo_dict[freq]
                else:
                    ampl_ref2_list.append(self.r2_hi_ampl_list[idx])
                    control_r2_dict[freq] = control_ref2_hi_dict[freq]

                ''' Compare amplitudes of ref1 vs. ref2 '''
                if ampl_ref1_list[idx] < ampl_ref2_list[idx]:
                    sa.all_frequencies_dict[freq] = control_r1_dict[freq]
                else:
                    sa.all_frequencies_dict[freq] = control_r2_dict[freq]

                difference = round(ampl_ref1_list[idx]-ampl_ref2_list[idx], 1)
                if difference > 0.5:
                    delta_list.append(freq)

        with open('control.pickle', 'wb') as f:
            pickle.dump(sa.all_frequencies_dict, f, protocol=pickle.HIGHEST_PROTOCOL)
            
        with open('control.csv', 'w') as fcsv:
            for f in sa.all_frequencies_dict:
                r, LO1_N, LO2_FMN = sa.all_frequencies_dict[f]
                freq = str(f)
                ref_clock = str(r)
                LO1 = str(LO1_N)
                LO2 = str(LO2_FMN)
                fcsv.write(f'{freq}:({ref_clock},{LO1},{LO2})\n')


    def progress_report(self, n):
        if n != self.last_N:
            self.last_N = n
#            print(name(), line(), f'Len in_buff = {n}')
        pass
    
    
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
        
    def _volts_to_dBm(self, voltage: float) -> float:
        '''
        Protected method Convert ADC results from Volts to dBm for the y_axis

        @param voltage Found based on the number of ADC bits and reference voltage
        @type float
        @return Output power in the range of -80 to +20 dBm
        @rtype float
        '''
        x = voltage
        dBm = -9.460927 * x**8 + 110.57352 * x**7 - 538.8610489 * x**6 + 1423.9059205 * x**5 - 2219.08322 * x**4 + 2073.3123 * x**3 - 1122.5121 * x**2 + 355.7665 * x - 112.663
        return dBm
    
    def _amplitude_bytes_to_volts(self, amplBytes) -> list:
        volts_list = list()
        # Convert two 8-bit serial bytes into one 16 bit amplitude
        hi_byte_list = amplBytes[::2]
        lo_byte_list = amplBytes[1::2]
        for idx, (hi_byte, lo_byte) in enumerate(zip(hi_byte_list, lo_byte_list)):
            if hi_byte > 3:
                hi_byte = (hi_byte & 15)        # Recover the amplitude value despite it not locking
                print(name(), line(), f'WARNING::Arduino timed out waiting for PLL to lock at {sa_ctl.swept_freq_list[idx]} Mhz')
            ampl = (hi_byte << 8) | lo_byte     # Combine MSByte/LSByte into an amplitude word
            voltage = ampl * sa.sa_control().adc_Vref()/2**10       # Convert 10 bit ADC counts to Voltage
            volts_list.append(voltage)
        return volts_list
        
        
    def plot_ampl_data(self, amplBytes):
        if amplBytes:
            self.x_axis.clear()
            self.y_axis.clear()
            self.amplitude.clear()
            volts_list = self._amplitude_bytes_to_volts(amplBytes)
            self.amplitude = [self._volts_to_dBm(voltage) for voltage in volts_list]
            argsort_index_nparray = np.argsort(sa_ctl.swept_freq_list)
            for idx in argsort_index_nparray:
                self.x_axis.append(sa_ctl.swept_freq_list[idx])  # Sort the frequency data in ascending order
                self.y_axis.append(self.amplitude[idx])          # And make the amplitude match the same order
            self.graphWidget.setXRange(self.x_axis[0], self.x_axis[-1])   # Limit plot to user selected frequency range
    #        purple = (75, 50, 255)
    #        self.dataLine.setData(sa_ctl.swept_freq_list, self.amplitude, pen=purple)
            yellow = (150, 255, 150)
            self.dataLine.setData(self.x_axis, self.y_axis, pen=yellow)
        else:
            print(name(), line(), 'Unable to plot. Missing amplitude data.')


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
        idx = sa.peakSearch(self.y_axis, self.numPeakMarkers.value())
        # Get the number of markers from the user control on the front panel
        num_markers = self.numPeakMarkers.value()
        # Create and add Peak Markers to the graph.
        for i in range(min(num_markers, len(idx))):
            self.marker = np.append(self.marker, pg.ArrowItem())  # Add a place for a new marker
            self.text = np.append(self.text, pg.TextItem())       # Add a place for a new label
            self.marker[i] = pg.ArrowItem(angle=-90, tipAngle=40, tailWidth=10, pen={'color': 'w', 'width': 1})
            frequency = self.x_axis[idx[i]]
            amplitude = self.y_axis[idx[i]]
            self.marker[i].setPos(frequency, amplitude)  # x-axis = frequency, y-axis = amplitude
            frequency_text = str('%.6f' % self.x_axis[idx[i]])
            amplitude_text = str('%.2f' % self.y_axis[idx[i]])
            markerLabel = frequency_text + ' MHz\n' + amplitude_text + ' dBm'
            self.text[i] = pg.TextItem(markerLabel, anchor = (0.5, 1.5), border = 'w', fill = (0, 0, 255, 100))
            self.graphWidget.addItem(self.marker[i])
            self.graphWidget.addItem(self.text[i])
            frequency_pos = self.x_axis[idx[i]]
            amplitude_pos = self.y_axis[idx[i]]
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
    def on_floatStartMHz_editingFinished(self):
        self.set_steps('control.pickle')


    @pyqtSlot()
    def on_floatStopMHz_editingFinished(self):
        self.set_steps('control.pickle')

    
    @pyqtSlot()
    def on_intStepKHz_editingFinished(self):
        self.set_steps('control.pickle')


    def float_to_index(self, hash_value):
        num_slice = round(hash_value, 3)                # Limit to 3 decimal places before converting...
        stringified = "{:.3f}".format(num_slice)        # to a string needed for the next step.
        decimal_removed = stringified.replace(".", "")  # Works the same as multiplying by 1000 and then...
        slice_index = int(decimal_removed)              # creates the index for the RFin_list
        return slice_index


#    def set_steps(self, control_file_name: str = 'control_ref1_HI.pickle'):
#    def set_steps(self, control_file_name: str = 'control_ref1_LO.pickle'):
#    def set_steps(self, control_file_name: str = 'control_ref2_HI.pickle'):
#    def set_steps(self, control_file_name: str = 'control_ref2_LO.pickle'):
    def set_steps(self, control_file_name: str=None):
        """
        Public method Create a list of frequencies for sweeping
        """
        MHz = 1000
        # Convert the start/stop/step floats into indexes for the sweep frequencies list
        start = self.float_to_index(self.floatStartMHz.value())
        stop = self.float_to_index(self.floatStopMHz.value())
        step = self.float_to_index(round(self.intStepKHz.value() / MHz, 3))
        # Fill the list with new sweep frequecies
        if control_file_name is None:
            sa_ctl.swept_freq_list = [f for f in self.RFin_list[start:stop:step]]
        else:
            sa_ctl.swept_freq_list = self.get_swept_freq_list(start, stop, step, control_file_name)  # Way faster than np.arange()
        self.numFrequencySteps.setValue(len(sa_ctl.swept_freq_list))    # Display the number of steps to the user


    def get_swept_freq_list(self, start: int, stop: int, step: int, control_fname: str) -> list:
        ''' control_fname is the filename of a control dictionary. A control dictionary has
            freq: (ref_clock_code, LO1_N, LO2_FMN) as key and values in a tuple. When making
            the list of sweep frequencies it will need to be sorted by ref_clock_code if the
            file contains more than one code. However, switching between reference clocks
            requires as much as 20 milliseconds for the new clock to settle so we would like
            to only switch once during a sweep. The resulting sweep list can be sorted by ref1 and ref2 control codes. 
        '''
        ref1_sweep_freq_list = list()
        ref2_sweep_freq_list = list()

        if control_fname is None:
            pass
        else:
            control_file = Path(control_fname)
        if not sa.all_frequencies_dict:
            if control_file.exists():
                with open(control_file, 'rb') as f:
                    sa.all_frequencies_dict = pickle.load(f)
                    print(name(), line(), f'Control file "{control_file}" opened')
            else:
                print(name(), line(), f'Missing control file "{control_file}"')

        freq_steps = [f for f in range(start, stop, step)]  # Populate the list of frequencies to step thru
        freq_steps.append(stop)                             # Include the stop value
        for idx in freq_steps:
            freq = self.RFin_list[idx]                      # freq is the key for accessing the all_frequencies_dict
            ref_code, _, _ = sa.all_frequencies_dict[freq]  # We need the ref_code from all_frequencies_dict
            ''' Selecting by ref_clock because all_frequencies_dict was already
                calibrated. If you are running a calibration then the sorting 
                has no effect. All the control codes will either be for ref1 or
                ref2 depending on which one you are calibrating.
            '''
            if ref_code == 0x0CFF:                          # ref_clock_1 control code = 0x0CFF
                ref1_sweep_freq_list.append(freq)           # Find all the freqs associated with ref_clock 1
            elif ref_code == 0x14FF:                        # ref_clock_2 control code = 0x14FF
                ref2_sweep_freq_list.append(freq)           # Find all the freqs associated with ref_clock 2
        return ref1_sweep_freq_list + ref2_sweep_freq_list  # Return the list of frequencies to be swept


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



if __name__ == '__main__':
    print()
#    freeze_support()







