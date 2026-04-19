# -*- coding: utf-8 -*-

# Import logging_setup to configure logging once for the application.
import logging
import logging_setup    # Used for its side effects
_ = logging_setup   # silence Warning: 'logging_setup' imported but unused
from time import sleep

from command_processor import CommandProcessor
from spectrumAnalyzer import SA_Control, peakSearch
import serial_port as sp
import application_interface as api
import numpy as np


class MainWindowController:
  def __init__(self):
    self.cmd_proc = CommandProcessor()
    self.sa_ctl = SA_Control(self.cmd_proc)
    self.RFin_list = np.arange(0, 3_000_001) / 1000.0
    self.plot_freq_list = []
    self.sweep_step_records = []
    self.missing_adc_sample_count = 0
    self.extra_adc_sample_count = 0

  def get_serial_ports(self):
    return sp.SimpleSerial().get_serial_port_list()

  def get_serial_speeds(self):
    return sp.SimpleSerial().get_baud_rate_list()

  def reopen_last_serial_port(self):
    sp.SimpleSerial().port_open()
    return sp.SimpleSerial().read_config()

  def load_controls(self, control_fname: str = 'control.npy'):
    api.load_controls(self.sa_ctl, control_fname)

  def update_swept_freq_list(self, start_freq: float, stop_freq: float, num_steps: int = 401):
    start, stop, step, _ = api.freq_steps(self.sa_ctl, start_freq, stop_freq, 0, num_steps)
    self.plot_freq_list = self._get_plot_freq_list(start, stop, step)
    self.sweep_step_records = self.sa_ctl.build_sweep_points(self.plot_freq_list)
    self.sa_ctl.swept_freq_list = self._get_swept_freq_list(self.sweep_step_records)

  def _get_plot_freq_list(self, start: int, stop: int, step: int) -> list:
    freq_steps = [f for f in range(start, stop, step)]
    freq_steps.append(stop)
    return [self.RFin_list[idx] for idx in freq_steps]

  def _get_swept_freq_list(self, sweep_step_records: list) -> list:
    return [step.rf_freq_mhz for step in sweep_step_records]

  def make_control_dictionary(self):
    api.make_control_dictionary(self.sa_ctl, self.RFin_list)

  def run_sweep(self):
    sweep_complete = api.sweep(self.sa_ctl)
    return sweep_complete, bytes(sp.SimpleSerial.data_buffer_in)

  def build_plot_data(self, ampl_bytes):
    x_axis = []
    y_axis = []
    volts_list = api._amplitude_bytes_to_volts(self.sa_ctl, ampl_bytes)
    amplitude = [api._volts_to_dBm(voltage) for voltage in volts_list]
    if len(self.sweep_step_records) != len(self.plot_freq_list):
      self.sweep_step_records = self.sa_ctl.build_sweep_points(self.plot_freq_list)
      self.sa_ctl.swept_freq_list = self._get_swept_freq_list(self.sweep_step_records)
    for step in self.sweep_step_records:
      step.amplitude = 0
    sample_count = min(len(self.sweep_step_records), len(amplitude))
    for idx in range(sample_count):
      self.sweep_step_records[idx].amplitude = amplitude[idx]
    self.missing_adc_sample_count = max(0, len(self.sweep_step_records) - len(amplitude))
    self.extra_adc_sample_count = max(0, len(amplitude) - len(self.sweep_step_records))
    if self.missing_adc_sample_count or self.extra_adc_sample_count:
      logging.warning(
        'Sweep sample count mismatch: expected %d, received %d, missing %d, extra %d',
        len(self.sweep_step_records),
        len(amplitude),
        self.missing_adc_sample_count,
        self.extra_adc_sample_count,
      )
    plot_step_records = sorted(self.sweep_step_records, key=lambda step: step.rf_freq_mhz)
    for step in plot_step_records:
      x_axis.append(step.rf_freq_mhz)
      y_axis.append(step.amplitude)
    amplitude = [step.amplitude for step in self.sweep_step_records]
    return amplitude, x_axis, y_axis

  def get_visible_plot_range(self, x_axis: list, y_axis: list):
    window_x_min, window_x_max, _ = self.sa_ctl.get_x_range()
    return api.get_visible_plot_range(x_axis, y_axis, window_x_min, window_x_max)

  def prepare_peak_markers(self, x_axis: list, y_axis: list, num_markers: int) -> list:
    idx = peakSearch(y_axis, num_markers)
    peaks = []
    for i in range(min(num_markers, len(idx))):
      frequency = x_axis[idx[i]]
      amplitude = y_axis[idx[i]]
      small_vertical_gap = 0.2
      marker_y = amplitude + small_vertical_gap
      frequency_text = str('%.6f' % frequency)
      amplitude_text = str('%.2f' % amplitude)
      label = frequency_text + ' MHz\n' + amplitude_text + ' dBm'
      peaks.append((frequency, amplitude, marker_y, label))
    return peaks

  def set_reference_clock(self, selected_ref_clock: int):
    self.sa_ctl.set_reference_clock(selected_ref_clock)

  def send_raw_command(self, cmd_str: str):
    cmd_int = int(cmd_str, 16)
    tmp_bytes = cmd_int.to_bytes(4, byteorder='little')
    sp.ser.write(tmp_bytes)

  def toggle_arduino_led(self, checked: bool):
    self.sa_ctl.toggle_arduino_led(checked)

  def get_version_message(self):
    self.sa_ctl.get_version_message()

  def set_attenuator(self, dB: float):
    self.sa_ctl.set_attenuator(dB)

  def open_serial_port(self, baud_rate: str, port: str):
    sp.SimpleSerial().port_open(baud_rate=baud_rate, port=port)
    sleep(2)

  def set_center_freq(self, freq: float):
    self.sa_ctl.set_center_freq(freq)
