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
import pickle
import numpy as np

from PyQt6 import QtCore, QtGui
from PyQt6.QtCore import pyqtSlot, QThread
from PyQt6.QtWidgets import QMainWindow
import pyqtgraph as pg
from pathlib import Path

from .Ui_mainWindow import Ui_MainWindow
import spectrumAnalyzer as sa
from spectrumAnalyzer import SA_Control as sa_ctl
import serial_port as sp


last_center_MHz_value = 0


class MainWindow(QMainWindow, Ui_MainWindow):
    last_N = -1     # for monitoring the amount of data from serial_read()

    def __init__(self):
        super().__init__()
        pg.setConfigOptions(useOpenGL=True, enableExperimental=True)
        self.setupUi(self)  # Must come before self.graphWidget.plot()
        self.setup_plot()
        #
        # MAX2871 chip will need to be initialized
        self.initialized = False
        self.amplitude = []     # Declare amplitude storage that will allow appending
        self.r1_hi_amplitudes = []
        self.r1_lo_amplitudes = []
        self.r2_hi_amplitudes = []
        self.r2_lo_amplitudes = []
        self.x_axis = []
        self.y_axis = []
        #
        # Request the list of available serial ports and use it to
        # populate the user 'Serial Port' drop-down selection list.
        ''' ~~~~~~ Setup serial port ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ '''
        serial_ports = sp.SimpleSerial().get_serial_port_list()
        self.cbxSerialPortSelection.addItems(serial_ports)
        #
        # Populate the 'User serial speed drop-down selection list'
        serial_speeds = sp.SimpleSerial().get_baud_rate_list()
        for baud in serial_speeds:
            self.cbxSerialSpeedSelection.addItem(str(baud), baud)
        # Check for, and reopen, the last serial port that was used.
        sp.SimpleSerial().port_open()
        # GUI dropdowns should display port and speed values from the port that was opened
        serial_port, serial_speed = sp.SimpleSerial().read_config()
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

    def setup_plot(self):
        """ Setting up the plot window """
        # When zooming the graph this updates the x-axis start & stop frequencies
        self.graphWidget.sigXRangeChanged.connect(self.update_start_stop)
        self.graphWidget.setLabel('bottom', text='Frequency (MHz)')
        self.graphWidget.setLabel('left', text='Amplitude', units='dBm')
        self.graphWidget.setDefaultPadding(padding=0.0)
        self.graphWidget.setMouseEnabled(x=True, y=False)
        self.dataLine = self.graphWidget.plot()
        self.graphWidget.setXRange(3.0, 3000.0)     # When starting set x-range from 3 to 3000 MHz
        self.graphWidget.setYRange(25, -62)         # dBm scale
        hor_line = pg.InfiniteLine(angle=(0), pen=(255, 128, 255), movable=True)
        ver_line = pg.InfiniteLine(pos=(100), pen=(128, 255, 128), movable=True)
        self.graphWidget.addItem(hor_line)
        self.graphWidget.addItem(ver_line)

    def load_control_file(self, control_fname: str=None):
        if control_fname is None:
            print(name(), line(), 'You must enter a control file name')
        else:
            sa_ctl.all_frequencies_dict.clear()     # get ready for a new set of control codes
            control_file = Path(control_fname)      # Filename containting new control codes
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
        sp.SimpleSerial.data_buffer_in.clear()     # Clear the serial data buffer before sweeping
        window_x_min, window_x_max = sa.get_plot_window_xrange()
        sweep_complete = sa.SA_Control().sweep(window_x_min, window_x_max)
        print(name(), line(), f'Sweep completed in {round(perf_counter()-start, 6)} seconds')
        if not sweep_complete:
           print(name(), line(), 'Sweep stopped by user')
        status_txt = f'Sweep complete, fwidth = {sa_ctl.lowpass_filter_width}'
        self.label_sweep_status.setText(status_txt)
        if self.chk_plot_enable.isChecked() and sweep_complete:
            self.plot_ampl_data(sp.SimpleSerial.data_buffer_in)
        QtGui.QGuiApplication.processEvents()


    @pyqtSlot()
    def on_btnCalibrate_clicked(self):
        default_min = 0
        default_max = 3000
        start = perf_counter()
        self.label_sweep_status.setText("Amplitude cal in progress...")
        QtGui.QGuiApplication.processEvents()
        serial_buf = sp.SimpleSerial.data_buffer_in

        ''' Run ref1 HI calibrations '''
        self.load_control_file('control_ref1_HI.pickle')
        self.set_steps()
        serial_buf.clear()     # Clear the serial data buffer before sweeping
        calibration_complete = sa.SA_Control().sweep(default_min, default_max)
        volts_list = [round(v, 3) for v in self._amplitude_bytes_to_volts(serial_buf)]
        if calibration_complete == False:
            print(name(), line(), 'Calibration cancelled by user')
        with open('amplitude_ref1_HI.pickle', 'wb') as f:
            pickle.dump(volts_list, f, protocol=pickle.HIGHEST_PROTOCOL)
            print(name(), line(), f'Saved {f}')
        with open('amplitude_ref1_HI.csv', 'w') as f:
            for amplitude in volts_list:
                f.write(f'{amplitude}' + '\n')

        ''' Run ref2 HI calibrations '''
        self.load_control_file('control_ref2_HI.pickle')
        self.set_steps()
        serial_buf.clear()     # Clear the serial data buffer before sweeping
        calibration_complete = sa.SA_Control().sweep(default_min, default_max)
        volts_list = [round(v, 3) for v in self._amplitude_bytes_to_volts(serial_buf)]
        if calibration_complete == False:
            print(name(), line(), 'Calibration cancelled by user')
        with open('amplitude_ref2_HI.pickle', 'wb') as f:
            pickle.dump(volts_list, f, protocol=pickle.HIGHEST_PROTOCOL)
            print(name(), line(), f'Saved {f}')
        with open('amplitude_ref2_HI.csv', 'w') as f:
            for amplitude in volts_list:
                f.write(f'{amplitude}' + '\n')

        ''' Run ref1 LO calibrations '''
        self.load_control_file('control_ref1_LO.pickle')
        self.set_steps()
        serial_buf.clear()     # Clear the serial data buffer before sweeping
        calibration_complete = sa.SA_Control().sweep(default_min, default_max)
        volts_list = [round(v, 3) for v in self._amplitude_bytes_to_volts(serial_buf)]
        if calibration_complete == False:
            print(name(), line(), 'Calibration cancelled by user')
        with open('amplitude_ref1_LO.pickle', 'wb') as f:
            pickle.dump(volts_list, f, protocol=pickle.HIGHEST_PROTOCOL)
            print(name(), line(), f'Saved {f}')
        with open('amplitude_ref1_LO.csv', 'w') as f:
            for amplitude in volts_list:
                f.write(f'{amplitude}' + '\n')

        ''' Run ref2 LO calibrations '''
        self.load_control_file('control_ref2_LO.pickle')
        self.set_steps()
        serial_buf.clear()     # Clear the serial data buffer before sweeping
        calibration_complete = sa.SA_Control().sweep(default_min, default_max)
        volts_list = [round(v, 3) for v in self._amplitude_bytes_to_volts(serial_buf)]
        if calibration_complete == False:
            print(name(), line(), 'Calibration cancelled by user')
        with open('amplitude_ref2_LO.pickle', 'wb') as f:
            pickle.dump(volts_list, f, protocol=pickle.HIGHEST_PROTOCOL)
            print(name(), line(), f'Saved {f}')
        with open('amplitude_ref2_LO.csv', 'w') as f:
            for amplitude in volts_list:
                f.write(f'{amplitude}' + '\n')

        self.label_sweep_status.setText("Calibration complete")
        QtGui.QGuiApplication.processEvents()
        print(name(), line(), f'Calibration of {len(volts_list)} data points took {round(perf_counter()-start, 6)} seconds')


    def set_steps(self):
        """
            Public method Create a list of frequencies for sweeping
        """
        # Get the start and stop indexes for the sweep frequencies list
        start: int = self.RFin_list.index(round(self.floatStartMHz.value(), 3))
        stop: int = self.RFin_list.index(round(self.floatStopMHz.value(), 3))
        step: int = self.intStepKHz.value()
        # Fill the list with new sweep frequecies
        sa_ctl.swept_freq_list.clear()
        sa_ctl.swept_freq_list = self.get_swept_freq_list(start, stop, step)  # Way faster than np.arange()
        self.numFrequencySteps.setValue(len(sa_ctl.swept_freq_list))    # Display the number of steps to the user
        self.set_LO3_sweep()

    def set_LO3_sweep(self):
        # Find and set the center frequency used for sweeping LO3.
        start = self.floatStartMHz.value()
        stop = self.floatStopMHz.value()
        self.graphWidget.setXRange(start, stop)     # When starting set x-range from 3 to 3000 MHz
        window_x_range = round(stop-start, 3)
        window_center = int(window_x_range/2 * 1000) / 1000 + start
        self.dblCenterMHz.setValue(window_center)


    def get_swept_freq_list(self, start: int, stop: int, step: int) -> list:
        ''' A control dictionary has freq: (ref_clock_code, LO1_N, LO2_FMN) as
        key and values in a tuple. When making the list of sweep frequencies it
        will need to be sorted by ref_clock_code if the file contains more than
        one code. However, switching between reference clocks requires as much
        as 20 milliseconds for the new clock to settle so we would like to only
        switch once during a sweep. The resulting sweep list can be sorted by
        ref1 and ref2 control codes.
        '''
        ref1_sweep_freq_list = []
        ref2_sweep_freq_list = []
        freq_steps = [f for f in range(start, stop, step)]  # Populate the list of frequencies to step thru
        freq_steps.append(stop)                             # Include the stop value
        for idx in freq_steps:
            freq = self.RFin_list[idx]                      # freq is the key for accessing the all_frequencies_dict
            ref_code, _, _ = sa_ctl.all_frequencies_dict[freq]  # We need the ref_code from all_frequencies_dict
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
    def on_btn_make_control_dict_clicked(self):
        '''
        Protected method The full control dictionary is used for programming
        the 3 LO chips on the Spectrum Analyzer board. The dictionary is created
        by comparing the amplitudes that were found when running a full sweep
        with ref1 selected and then ref2. Whichever amplitude is lower then the
        control codes for that frequency are copied to the control_dict.
        '''
        sa_ctl.all_frequencies_dict.clear()
        ''' If one of these files is missing there is no need to check the others '''
        ampl_file_1 = Path('amplitude_ref1_HI.pickle')
        ampl_file_2 = Path('amplitude_ref2_HI.pickle')
        if ampl_file_1.exists() and ampl_file_2.exists():
            if not self.r1_hi_amplitudes:    # If this list is missing so are all the others
                ''' The contents of the amplitude files need to be compared to see which one
                has the lowest level of noise. Each entry depends on its position in the file,
                e.g. Line 132427 in the file came from the frequency 132.427 MHz RFin '''
                with open('amplitude_ref1_HI.pickle', 'rb') as f:   # 3 million amplitudes collected with ref1
                    self.r1_hi_amplitudes = pickle.load(f)
                with open('amplitude_ref1_LO.pickle', 'rb') as f:   # 3 million amplitudes collected with ref1
                    self.r1_lo_amplitudes = pickle.load(f)
                with open('amplitude_ref2_HI.pickle', 'rb') as f:   # 3 million amplitudes collected with ref2
                    self.r2_hi_amplitudes = pickle.load(f)
                with open('amplitude_ref2_LO.pickle', 'rb') as f:   # 3 million amplitudes collected with ref2
                    self.r2_lo_amplitudes = pickle.load(f)
                ''' These are the controls associated with the amplitude files. When the lowest
                noise level has been found then the control associated with that amplitude file
                is assigned to a single full_control dictionary, e.g. We found Line 132427 was
                lowest in amplitude_ref1_LO so the control from control_ref1_LO is copied into
                the full_control dictionary. '''
                with open('control_ref1_HI.pickle', 'rb') as f:
                    control_ref1_hi_dict = pickle.load(f)
                with open('control_ref1_LO.pickle', 'rb') as f:
                    control_ref1_lo_dict = pickle.load(f)
                with open('control_ref2_HI.pickle', 'rb') as f:
                    control_ref2_hi_dict = pickle.load(f)
                with open('control_ref2_LO.pickle', 'rb') as f:
                    control_ref2_lo_dict = pickle.load(f)

            def lp_filt(active_list, half_window: int, index: int = 0) -> float:
                """ A Centered Moving Average is is used to smooth out the amplitude data.
                Otherwise random noise levels cause random control selection. This shows
                up as a comb effect when performing actual sweeps.
                """
                start = index - half_window
                stop = index + half_window
                if start < 0:                   # too close to the start of the list
                    start = 0
                if stop > len(active_list):       # too close to the end of the list
                    stop = len(active_list)
                avg_value = round(np.average(active_list[start:stop]),3)
                return avg_value

            """ We need smoothed amplitude data for performing the amplitude comparison step
                The lp_filt() def uses self.r1_lo_amplitudes, etc., directly. It's faster
                than passing the entire list.
            """
            window = sa_ctl.lowpass_filter_width
            a1_filtered = [lp_filt(self.r1_hi_amplitudes, window, idx) for idx, _ in enumerate(self.r1_hi_amplitudes)]
            a2_filtered = [lp_filt(self.r1_lo_amplitudes, window, idx) for idx, _ in enumerate(self.r1_lo_amplitudes)]
            a3_filtered = [lp_filt(self.r2_hi_amplitudes, window, idx) for idx, _ in enumerate(self.r2_hi_amplitudes)]
            a4_filtered = [lp_filt(self.r2_lo_amplitudes, window, idx) for idx, _ in enumerate(self.r2_lo_amplitudes)]

            for idx, freq in enumerate(self.RFin_list):
                """ For each RFin select the control code that generated the best (lowest) amplitude. """
                a1 = a1_filtered[idx]
                a2 = a2_filtered[idx]
                a3 = a3_filtered[idx]
                a4 = a4_filtered[idx]
                if a1 <= a2 and a1 <= a3 and a1 <= a4:
                    sa_ctl.all_frequencies_dict[freq] = control_ref1_hi_dict[freq]
                elif a2 < a1 and a2 <= a3 and a2 <= a4:
                    sa_ctl.all_frequencies_dict[freq] = control_ref1_lo_dict[freq]
                elif a3 < a1 and a3 < a2 and a3 <= a4:
                    sa_ctl.all_frequencies_dict[freq] = control_ref2_hi_dict[freq]
                elif a4 < a1 and a4 < a2 and a4 < a3:
                    sa_ctl.all_frequencies_dict[freq] = control_ref2_lo_dict[freq]
                """ Special cases requiring manual input """
                if 208 < freq < 210.35:
                    sa_ctl.all_frequencies_dict[freq] = control_ref2_lo_dict[freq]
                if 359.9 < freq < 360.1:
#                    sa_ctl.all_frequencies_dict[freq] = control_ref2_lo_dict[freq]
                    sa_ctl.all_frequencies_dict[freq] = control_ref1_hi_dict[freq]
                if 2482 < freq < 2484:
                    sa_ctl.all_frequencies_dict[freq] = control_ref1_hi_dict[freq]

        with open('control.pickle', 'wb') as f:
            pickle.dump(sa_ctl.all_frequencies_dict, f, protocol=pickle.HIGHEST_PROTOCOL)
            
        with open('control.csv', 'w') as fcsv:
            for f in sa_ctl.all_frequencies_dict:
                r, LO1_N, LO2_FMN = sa_ctl.all_frequencies_dict[f]
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
            self.worker = sp.SimpleSerial()                      # Function for reading from the serial port
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
        return view_range

    @pyqtSlot()
    def on_btnRefreshPortsList_clicked(self):
        for x in range(10):
            self.cbxSerialPortSelection.removeItem(0)
        ports = sp.SimpleSerial().get_serial_port_list()
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
        dBm = (((((((-9.460927*x + 110.57352)*x - 538.8610489)*x + 1423.9059205)*x - 2219.08322)*x + 2073.3123)*x - 1122.5121)*x + 355.7665)*x - 112.663
        return dBm
    
    def _amplitude_bytes_to_volts(self, amplBytes) -> list:
        volts_list = []
        # Convert two 8-bit serial bytes into one 16 bit amplitude
        hi_byte_list = amplBytes[::2]
        lo_byte_list = amplBytes[1::2]
        for idx, (hi_byte, lo_byte) in enumerate(zip(hi_byte_list, lo_byte_list)):
            if hi_byte > 3:
                hi_byte = (hi_byte & 15)        # Store the amplitude value despite it not locking
                print(name(), line(), f'WARNING:: PLL failed to lock at {sa_ctl.swept_freq_list[idx]} Mhz')
            ampl = (hi_byte << 8) | lo_byte     # Combine MSByte/LSByte into an amplitude word
            voltage = ampl * sa.SA_Control().adc_Vref()/(2**10-1)       # Convert 10 bit ADC counts to Voltage
            volts_list.append(voltage)
        return volts_list

    def plot_ampl_data(self, amplBytes):
        if amplBytes:
            self.x_axis.clear()
            self.y_axis.clear()
            self.amplitude.clear()
            volts_list = self._amplitude_bytes_to_volts(amplBytes)
            self.amplitude = [self._volts_to_dBm(voltage) for voltage in volts_list]
            argsort_index_nparray = sa.np.argsort(sa_ctl.swept_freq_list)
            for idx in argsort_index_nparray:
                self.x_axis.append(sa_ctl.swept_freq_list[idx])  # Sort the frequency data in ascending order
                self.y_axis.append(self.amplitude[idx])          # And make the amplitude match the same order
            self.graphWidget.setXRange(self.x_axis[0], self.x_axis[-1])   # Limit plot to user selected frequency range
            color = {"purple": (75, 50, 255), "yellow": (150, 255, 150)}
            self.dataLine.setData(self.x_axis, self.y_axis, pen=color["yellow"])
        else:
            print(name(), line(), 'Unable to plot. Missing amplitude data.')

    def get_visible_plot_range(self, x_plot_data: list, y_plot_data: list, window_x_min: float, window_x_max: float):
        """ Get the list of visible plot points after zooming the plot window """
        # Get x_plot_min/max values nearest to the values from the plotWidget
        visible_x_min = min(x_plot_data, key=lambda x_data: abs(x_data-window_x_min)) # x is iterated from x_plot_data
        visible_x_max = min(x_plot_data, key=lambda x_data: abs(x_data-window_x_max))
        print(name(), line())
        x_data_min = x_plot_data[0]
        x_data_max = x_plot_data[-1]
        if visible_x_min < x_data_min:
            visible_x_min = x_data_min
        if visible_x_max > x_data_max:
            visible_x_max = x_data_max
        print(name(), line(), f'{window_x_min = }, {window_x_max = }')
        print(name(), line(), f'{visible_x_min = }, {visible_x_max = }')
        # Find the indexes for the min/max values...
        idx_min = x_plot_data.index(visible_x_min)
        idx_max = x_plot_data.index(visible_x_max)
        # and return the portion of the list that is visible on the plot
        x_axis = x_plot_data[idx_min:idx_max]
        y_axis = y_plot_data[idx_min:idx_max]
        return x_axis, y_axis

    @pyqtSlot()
    def on_btnPeakSearch_clicked(self):
        window_x_min, window_x_max = sa.get_plot_window_xrange()
        x_axis, y_axis = self.get_visible_plot_range(self.x_axis, self.y_axis, window_x_min, window_x_max)
        self._clear_marker_text()
        self._clear_peak_markers()
        self._peak_search(x_axis, y_axis)

    def _peak_search(self, x_axis: list, y_axis: list):
        self.marker = sa.np.array([pg.ArrowItem()])     # Create a growable array of markers
        self.text = sa.np.array([pg.TextItem()])        # Make a growable array of labels
        # idx is sorted so that idx[0] points to the highest amplitude in the
        # amplitudeData array, idx[1] points to the second highest and so on.
        idx = sa.peakSearch(y_axis, self.numPeakMarkers.value())
        # Get the number of markers from the user control on the front panel
        num_markers = self.numPeakMarkers.value()
        # Create and add Peak Markers to the graph.
        for i in range(min(num_markers, len(idx))):
            self.marker = sa.np.append(self.marker, pg.ArrowItem())  # Add a place for a new marker
            self.text = sa.np.append(self.text, pg.TextItem())       # Add a place for a new label
            self.marker[i] = pg.ArrowItem(angle=-90, tipAngle=40, tailWidth=10, pen={'color': 'w', 'width': 1})
            frequency = x_axis[idx[i]]
            amplitude = y_axis[idx[i]]
            small_vertical_gap = 0.2
            self.marker[i].setPos(frequency, amplitude+small_vertical_gap)
            frequency_text = str('%.6f' % x_axis[idx[i]])
            amplitude_text = str('%.2f' % y_axis[idx[i]])
            markerLabel = frequency_text + ' MHz\n' + amplitude_text + ' dBm'
            self.text[i] = pg.TextItem(markerLabel, anchor = (0.5, 1.5), border = 'w', fill = (0, 0, 255, 100))
            self.graphWidget.addItem(self.marker[i])
            self.graphWidget.addItem(self.text[i])
            frequency_pos = x_axis[idx[i]]
            amplitude_pos = y_axis[idx[i]]
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
        sa.SA_Control().set_attenuator(dB)

    @pyqtSlot()
    def on_btn_open_serial_port_clicked(self):
        """
        Open a new serial port at the user selected port and baud_rate
        """
        sel_baud = self.cbxSerialSpeedSelection.currentText()
        sel_port = self.cbxSerialPortSelection.currentText()
        sp.SimpleSerial().port_open(baud_rate=sel_baud, port=sel_port)
        sleep(2)
    
    
    @pyqtSlot()
    def on_floatStartMHz_editingFinished(self):
        self.set_steps()


    @pyqtSlot()
    def on_floatStopMHz_editingFinished(self):
        self.set_steps()

    
    @pyqtSlot()
    def on_intStepKHz_editingFinished(self):
        self.set_steps()


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

    @pyqtSlot(sa_ctl, object)
    def on_graphWidget_sigRangeChanged(self, sa_obj, p1):
        """
        Update the plot window x-axis min/max values when the plot
        zoom level is changed.

        @param sa_obj The Spectrum Analyzer object imported as sa_ctl
        @type PyQt_PyObject
        @param p1 The x-y range object from the pyqtgraph PlotWidget
        @type PyQt_PyObject
        """
        x_min = round(p1[0][0], 3)
        x_max = round(p1[0][1], 3)
        sa.set_plot_window_xrange(x_min, x_max)



if __name__ == '__main__':
    print()
#    freeze_support()







