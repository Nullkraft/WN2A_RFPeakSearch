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

# Import logging_setup to configure logging once for the application.
import logging
import logging_setup    # Used for its side effects
_ = logging_setup   # silence Warning: 'logging_setup' imported but unused

from PyQt6 import QtCore, QtGui
from PyQt6.QtCore import pyqtSlot, QCoreApplication
from PyQt6.QtWidgets import QCheckBox, QMainWindow
import pyqtgraph as pg

from ui.Ui_mainWindow import Ui_MainWindow
import numpy as np
from main_window_controller import MainWindowController


class _SuppressSweepTimingFilter(logging.Filter):
  def filter(self, record):
    msg = record.getMessage()
    return not (
      msg.startswith('Sweep completed in ')
      or msg.startswith('len(amplBytes) = ')
      or msg.startswith('Arduino message = ')
    )


class MainWindow(QMainWindow, Ui_MainWindow):
  last_center_MHz_value = 0
  PROGSTART = True

  def __init__(self):
    super().__init__()
    pg.setConfigOptions(useOpenGL=True, enableExperimental=True)
    self.setupUi(self)  # Must come before self.graphWidget.plot()
    self.chk_continuous_sweep = QCheckBox("Continuous Sweep", self.groupBox_6)
    self.chk_continuous_sweep.setChecked(False)
    self.chk_continuous_sweep.setObjectName("chk_continuous_sweep")
    self.verticalLayout_3.insertWidget(
      self.verticalLayout_3.indexOf(self.label_sweep_status),
      self.chk_continuous_sweep,
    )
    self.setup_plot()
    self.controller = MainWindowController()
    self.sa_ctl = self.controller.sa_ctl
    #
    # MAX2871 chip will need to be initialized
    self.amplitude = []   # Declare amplitude storage that will allow appending
    self.r1_hi_amplitudes = []
    self.r1_lo_amplitudes = []
    self.r2_hi_amplitudes = []
    self.r2_lo_amplitudes = []
    self.x_axis = []
    self.y_axis = []
    #
    self.num_steps = 3_000_001  # Number of Spectrum Analyzer 1kHz steps
    #
    # Request the list of available serial ports and use it to
    # populate the user 'Serial Port' drop-down selection list.
    ''' ~~~~~~ Setup serial port ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ '''
    serial_ports = self.controller.get_serial_ports()
    self.cbxSerialPortSelection.addItems(serial_ports)
    #
    # Populate the 'User serial speed drop-down selection list'
    serial_speeds = self.controller.get_serial_speeds()
    for baud in serial_speeds:
      self.cbxSerialSpeedSelection.addItem(str(baud), baud)
    # Check for, and reopen, the last serial port that was used.
    serial_port, serial_speed = self.controller.reopen_last_serial_port()
    # GUI dropdowns should display port and speed values from the port that was opened
    port_index = self.cbxSerialPortSelection.findText(serial_port)
    if (port_index >= 0):
      self.cbxSerialPortSelection.setCurrentIndex(port_index)
    speed_index = self.cbxSerialSpeedSelection.findData(str(serial_speed))
    if (speed_index >= 0):
      self.cbxSerialSpeedSelection.setCurrentIndex(speed_index)
    ''' ~~~~~~ End serial port ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ '''
    # Load the initial control file
    self.controller.load_controls('control.npy')

  def setup_plot(self):
    ''' Setting up the plot window '''
    # When zooming the graph this updates the x-axis start & stop frequencies
    self.graphWidget.sigXRangeChanged.connect(self.update_start_stop)
    self.graphWidget.setLabel('bottom', text='Frequency (MHz)')
    self.graphWidget.setLabel('left', text='Amplitude', units='dBm')
    self.graphWidget.setDefaultPadding(padding=0.0)
    self.graphWidget.setMouseEnabled(x=True, y=False)
    self.dataLine = self.graphWidget.plot()
    self.graphWidget.setXRange(3.0, 3000.0)   # When starting set x-range from 3 to 3000 MHz
    self.graphWidget.setYRange(25, -62)     # dBm scale
    hor_line = pg.InfiniteLine(angle=(0), pen=(255, 128, 255), movable=True)
    ver_line = pg.InfiniteLine(pos=(100), pen=(128, 255, 128), movable=True)
    self.graphWidget.addItem(hor_line)
    self.graphWidget.addItem(ver_line)

  @pyqtSlot()
  def on_btnCalibrate_clicked(self):
    import calibrate_sa

    def update_status(msg):
      self.label_sweep_status.setText(msg)
      QtGui.QGuiApplication.processEvents()

    calibrate_sa.run_full_calibration(self.sa_ctl, status_callback=update_status)

  def set_steps(self, num_steps: int = 401):
    if self.PROGSTART:
      return
    start_freq = round(self.floatStartMHz.value(), 3)
    stop_freq = round(self.floatStopMHz.value(), 3)
    self.controller.update_swept_freq_list(start_freq, stop_freq, num_steps)

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
    freq_steps.append(stop)               # Include the stop value
    for idx in freq_steps:
      freq = self.RFin_list[idx]            # freq is the key for accessing the all_frequencies_dict
      ref_code, _, _ = self.sa_ctl.get_control_codes(freq)  # We need the ref_code for this frequency
      ''' Selecting by ref_clock because all_frequencies_dict was already
          calibrated. If you are running a calibration then the sorting
          has no effect. All the control codes will either be for ref1 or
          ref2 depending on which one you are calibrating.
      '''
      if ref_code == 0x0CFF:              # ref_clock_1 control code = 0x0CFF
        ref1_sweep_freq_list.append(freq)       # Find all the freqs associated with ref_clock 1
      elif ref_code == 0x14FF:            # ref_clock_2 control code = 0x14FF
        ref2_sweep_freq_list.append(freq)       # Find all the freqs associated with ref_clock 2
    return ref1_sweep_freq_list + ref2_sweep_freq_list  # Return freqs sorted by ref_clock

  @pyqtSlot()
  def on_btn_make_control_dict_clicked(self):
    self.controller.make_control_dictionary()

  @pyqtSlot()
  def on_btnSweep_clicked(self):
    self.label_sweep_status.setText("Sweep in progress...")
    QtGui.QGuiApplication.processEvents()
    sweep_timing_filter = None
    if self.chk_continuous_sweep.isChecked():
      sweep_timing_filter = _SuppressSweepTimingFilter()
      logging.getLogger().addFilter(sweep_timing_filter)
    try:
      sweep_complete, ampl_bytes = self.controller.run_sweep()
      status_txt = f'Sweep complete, fwidth = {self.sa_ctl.lowpass_filter_width}'
      self.label_sweep_status.setText(status_txt)
      QtGui.QGuiApplication.processEvents()
      if self.chk_plot_enabled.isChecked() and sweep_complete:
        self.plot_ampl_data(ampl_bytes)
      if self.chk_continuous_sweep.isChecked() and sweep_complete:
        QtCore.QTimer.singleShot(0, self.on_btnSweep_clicked)
    finally:
      if sweep_timing_filter is not None:
        logging.getLogger().removeFilter(sweep_timing_filter)

  @pyqtSlot()
  def update_start_stop(self):
    view_range = self.graphWidget.viewRange()
    return view_range

  @pyqtSlot()
  def on_btnRefreshPortsList_clicked(self):
    for x in range(10):
      self.cbxSerialPortSelection.removeItem(0)
    ports = self.controller.get_serial_ports()
    self.cbxSerialPortSelection.addItems(ports)

  @pyqtSlot(int)
  def on_selectReferenceOscillator_currentIndexChanged(self, selected_ref_clock):
    self.controller.set_reference_clock(selected_ref_clock)

  def plot_ampl_data(self, amplBytes):
    if amplBytes:
      self.x_axis.clear()
      self.y_axis.clear()
      self.amplitude.clear()
      self.amplitude, self.x_axis, self.y_axis = self.controller.build_plot_data(amplBytes)
      self.graphWidget.setXRange(self.x_axis[0], self.x_axis[-1])   # Limit plot to user selected frequency range
      color = {"purple": (75, 50, 255), "yellow": (150, 255, 150)}
      self.dataLine.setData(self.x_axis, self.y_axis, pen=color["yellow"])
    else:
      logging.warning('Unable to plot. Missing amplitude data.')


  @pyqtSlot()
  def on_btnPeakSearch_clicked(self):
    x_axis, y_axis = self.controller.get_visible_plot_range(self.x_axis, self.y_axis)
    self._clear_marker_text()
    self._clear_peak_markers()
    self._peak_search(x_axis, y_axis)

  def _peak_search(self, x_axis: list, y_axis: list):
    self.marker = np.array([pg.ArrowItem()])   # Create a growable array of markers
    self.text = np.array([pg.TextItem()])    # Make a growable array of labels
    peaks = self.controller.prepare_peak_markers(
      x_axis,
      y_axis,
      self.numPeakMarkers.value(),
    )
    for i, (frequency, amplitude, marker_y, label) in enumerate(peaks):
      self.marker = np.append(self.marker, pg.ArrowItem())  # Add a place for a new marker
      self.text = np.append(self.text, pg.TextItem())     # Add a place for a new label
      self.marker[i] = pg.ArrowItem(angle=-90, tipAngle=40, tailWidth=10, pen={'color': 'w', 'width': 1})
      self.marker[i].setPos(frequency, marker_y)
      self.text[i] = pg.TextItem(label, anchor = (0.5, 1.5), border = 'w', fill = (0, 0, 255, 100))
      self.graphWidget.addItem(self.marker[i])
      self.graphWidget.addItem(self.text[i])
      self.text[i].setPos(frequency, amplitude)

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
    QCoreApplication.quit()
#    sys.exit()   # Not thread safe

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
    self.controller.send_raw_command(self.line_edit_cmd.text())

  @pyqtSlot(bool)
  def on_chkArduinoLED_toggled(self, checked):
   self.controller.toggle_arduino_led(checked)

  @pyqtSlot()
  def on_btn_get_arduino_msg_clicked(self):
    """
    Request the Arduino message containing version number and date
    """
    self.controller.get_version_message()

  @pyqtSlot()
  def on_dbl_attenuator_dB_editingFinished(self):
    """
    Reduce the RF input signal using the onboard Digital Attenuator

    @param 0 to 31.75 dB
    @type double
    """
    dB = float(self.dbl_attenuator_dB.value())    # Read attenuator value from user control
    self.controller.set_attenuator(dB)

  @pyqtSlot()
  def on_btn_open_serial_port_clicked(self):
    """
    Open a new serial port at the user selected port and baud_rate
    """
    sel_baud = self.cbxSerialSpeedSelection.currentText()
    sel_port = self.cbxSerialPortSelection.currentText()
    self.controller.open_serial_port(sel_baud, sel_port)

  @pyqtSlot()
  def on_floatStartMHz_editingFinished(self):
    plot_x_start = self.floatStartMHz.value()
    plot_x_stop = self.floatStopMHz.value()
    logging.info(f'{plot_x_start = } : {plot_x_stop = }')
    # Prevent graph, or plot, from trying to update this StopMHz control
    self.graphWidget.sigXRangeChanged.disconnect(self.update_start_stop)
    self.graphWidget.setXRange(plot_x_start, plot_x_stop)
    self.graphWidget.sigXRangeChanged.connect(self.update_start_stop)
    self.PROGSTART = False

  @pyqtSlot()
  def on_floatStopMHz_editingFinished(self):
    plot_x_start = self.floatStartMHz.value()
    plot_x_stop = self.floatStopMHz.value()
    logging.info(f'{plot_x_start = } : {plot_x_stop = }')
    # Prevent graph, or plot, from trying to update this StopMHz control
    self.graphWidget.sigXRangeChanged.disconnect(self.update_start_stop)
    self.graphWidget.setXRange(plot_x_start, plot_x_stop)
    self.graphWidget.sigXRangeChanged.connect(self.update_start_stop)
    self.PROGSTART = False

  @pyqtSlot()
  def on_intStepKHz_editingFinished(self):
    start_freq = self.floatStartMHz.value()
    stop_freq = self.floatStopMHz.value()
    step_size = self.intStepKHz.value()
    band_width = (stop_freq - start_freq) * 1000
    num_steps = int(band_width / step_size)

    self.numFrequencySteps.setValue(num_steps)    # Update 'Data Points' for user
    self.set_steps(num_steps)
    self.PROGSTART = False

  @pyqtSlot()
  def on_dblCenterMHz_editingFinished(self):
    '''
    Public slot What happens if I try to run it a second time.
    '''
    if self.dblCenterMHz.value() != MainWindow.last_center_MHz_value:
      self.controller.set_center_freq(self.dblCenterMHz.value())
      MainWindow.last_center_MHz_value = self.dblCenterMHz.value()
    else:
      pass

  @pyqtSlot(object, object)
  def on_graphWidget_sigRangeChanged(self, sa_obj, p1):
    '''
    Update the plot window x-axis min/max values when the plot
    zoom level is changed.

    @param sa_obj The Spectrum Analyzer object imported as sa_ctl
    @type PyQt_PyObject
    @param p1 The x-y range object from the pyqtgraph PlotWidget
    @type PyQt_PyObject
    '''
    x_min = round(p1[0][0], 3)
    x_max = round(p1[0][1], 3)
    self.floatStartMHz.setValue(x_min)
    self.floatStopMHz.setValue(x_max)
    self.set_steps()  # Uses default num_steps=401

#  @pyqtSlot(int)
#  def on_numFrequencySteps_valueChanged(self, p0):
#    print(name(), line(), f'Data points changed to {p0}')


if __name__ == '__main__':
  logging.info('')
#  freeze_support()
