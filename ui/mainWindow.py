# -*- coding: utf-8 -*-

from PyQt6 import QtCore
from PyQt6.QtCore import pyqtSlot, QThread #, pyqtSignal, QObject
from PyQt6.QtWidgets import QMainWindow
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
        self.setupUi(self)  # Must come before self.plot()
        self.graphWidget.setYRange(0, 2.5)
        self.graphWidget.setMouseEnabled(x=True, y=False)
        self.dataLine = self.graphWidget.plot()
        # When zooming the graph update the x-axis start & stop frequencies
        self.graphWidget.sigXRangeChanged.connect(self.update_start_stop)
        #
        sa.referenceClock = 60
        self.initialized = False        # MAX2871 chip will need to be initialized
        # Populate the 'User serial port drop-down selection list'
        serial_ports = ss.get_os_ports()
        self.cbxSerialPortSelection.addItems(serial_ports)
        # Populate the 'User serial speed drop-down selection list'
        serial_speeds = ss.get_os_baudrates()
        for baud in serial_speeds:
            self.cbxSerialSpeedSelection.addItem(str(baud), baud)
        # Check for, and reopen, the last serial port that was used.
        ss.port_open()
        # And now the user dropdowns need to be updated with the port and speed
        foundPortIndex = self.cbxSerialPortSelection.findText(ss._port)
        if (foundPortIndex >= 0):
            self.cbxSerialPortSelection.setCurrentIndex(foundPortIndex)
        foundSpeedIndex = self.cbxSerialSpeedSelection.findData(ss._baud)
        if (foundSpeedIndex >= 0):
            self.cbxSerialSpeedSelection.setCurrentIndex(foundSpeedIndex)
        sa.hardware().load_LO1_freq_steps()
        sa.hardware().load_LO2_freq_steps()
        # Populate the 'User RFin step size drop-down selection list'
        sa.step_size_dict = {"250.0" : 0.250,
                             "125.0" : 0.125,
                             " 62.5" : 0.0625,
                             " 32.0" : 0.03125,
                             " 16.0" : 0.015625,
                             "  8.0" : 0.0078125,
                             "  4.0" : 0.00390625,
                             "  2.0" : 0.001953125}
        for str_step in sa.step_size_dict:
            self.cbx_RFin_step_size.addItem(str_step)



    @pyqtSlot()
    def update_start_stop(self):
        view_range = self.graphWidget.viewRange()
#        print(name, line(), f'View range = {view_range}')
        return view_range

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

    @pyqtSlot(str)
    def on_cbx_RFin_step_size_activated(self, RFin_step_size_str):
        """
        Slot documentation goes here.

        @param RFin_step_size DESCRIPTION
        @type str
        """
        sa.sweep_step = sa.step_size_dict[RFin_step_size_str]


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

    # amplitude was collected as a bunch of linear 16-bit A/D values
    def plot_ampl_data(self, amplBytes):
        self.amplitude = []       # Declare amplitude storage that will allow appending
        nBytes = len(amplBytes)
        # Convert two 8-bit serial bytes into one 16 bit amplitude.
        for x in range(0, nBytes, 2):
            ampl = amplBytes[x] | (amplBytes[x+1] << 8)
            volts = (ampl/1024) * 5
            self.amplitude.append(volts)
        assert len(sa.x_axis_list)==len(self.amplitude)
        self.dataLine.setData(sa.x_axis_list, self.amplitude, pen=(155,155,255))


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





        # TODO: Store sweep__start, sweep_stop, and sweep_step in spectrumAnalyzer.py
        #
        # When the user updates the start, stop, or step frequency on the GUI then
        # make a function in spectrumAnalyzer.py that converts the frequency into
        # sa.sweep__start, sa.sweep_stop, and sa.sweep_step as 1 kHz values that
        # become the index into the:
        #     sa.full_freq_list[sa.sweep_start:sa.sweep_stop:sa.sweep_step]









    @pyqtSlot()
    def on_btnSweep_clicked(self):
        ref_clock = sa.referenceClock
        sweep_start = self.floatStartMHz.value()
        sweep_stop = self.floatStopMHz.value()
        sweep_step_kHz = sa.sweep_step
        sp.ser.read(sp.ser.in_waiting) # Clear out the serial buffer.
        self.serial_read_thread()      # Start the serial receive read thread to accept sweep data
        sa.sweep(sweep_start, sweep_stop, sweep_step_kHz, ref_clock)
        assert len(sa.x_axis_list) != 0, "sa.x_axis_list was empty"
        self.graphWidget.setXRange(sa.x_axis_list[0], sa.x_axis_list[-1])   # Limit plot to user selected frequency range


    @pyqtSlot()
    def on_dbl_attenuator_dB_editingFinished(self):
        """
        Reduce the RF input signal using the onboard Digital Attenuator

        @param 0 to 31.75 dB
        @type double
        """
        dB = float(self.dbl_attenuator_dB.value())
        cmd_proc.set_attenuator(dB)


    @pyqtSlot()
    def on_dblStepSize_editingFinished(self):
        """ Load the LO2 fmn list based on the user selected step size
        """
        step_size = round(self.dblStepSize.value(), 6)
        sa.update_LO2_fmn_list(step_size)


    def get_freq_step(self):
        freq_step = round(self.dblStepSize.value(), 6)
        return freq_step
    
    @pyqtSlot(str)
    def on_cbxSerialPortSelection_activated(self, selected_port):
        """
        Slot documentation goes here.
        
        @param p0 DESCRIPTION
        @type str
        """
        ss.set_port(selected_port)
    
    @pyqtSlot(str)
    def on_cbxSerialSpeedSelection_currentTextChanged(self, speed_str):
        """
        Slot documentation goes here.
        
        @param p0 DESCRIPTION
        @type str
        """
        ss.set_speed(speed_str)
    
    @pyqtSlot()
    def on_btn_open_serial_port_clicked(self):
        """
        Slot documentation goes here.
        """
        ss.port_open()
