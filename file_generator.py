# -*- coding: utf-8 -*-
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


import hardware_cfg as hw
import command_processor as cmd
import sys
import pickle

def line() -> str:
    """
    Function Utility to simplify print debugging.

    @return The line number of the source code file.
    @rtype str

    """
    return f'line {str(sys._getframe(1).f_lineno)},'


name = f'File \"{__name__}.py\",'


class data_generator():
    """ These files will be used by calibrate_sa.py for creating the
        control dictionaries needed by the calibration scripts.
    """
    ref1 = cmd.ref_clock1_enable
    ref2 = cmd.ref_clock2_enable

    ''' RFin_list contains every frequency from 0 to 3000.0 MHz in 1 kHz steps '''
    RFin_list = list()
    with open('RFin_steps.csv', 'r') as f:
        for freq in f:
            RFin = float(freq)
            RFin_list.append(RFin)

    def _LO1_frequency(self, RFin: float, Fref: float, R: int=1) -> float:
        """
        Protected method calculates the frequency for LO1 from RFin, Fpfd, and R
        where the Phase Frequency Detector frequency is Fpfd=Fref/R

        @param RFin is the Spectrum Anaylzer input frequency
        @type float
        @param Fref is the frequency of the selected reference clock
        @type float
        @param R is from the manufacturer's specsheet (defaults to 1)
        @type int (optional)
        @return The LO1 frequency that steps by the Fpfd value
        @rtype float
        """
        Fpfd = Fref/R     # Fpfd1 = 66.0 and Fpfd2 = 66.666 MHz
        LO1_freq = int((hw.cfg.IF1 + RFin) / Fpfd) * Fpfd
        return LO1_freq

    def _LO2_frequency(self, RFin: float, ref_clock: str) -> float:
        """
        Protected method calculates the frequency for LO2 from LO1, RFin, and
        the selected reference clock
        
        @param RFin is the Spectrum Anaylzer input frequency
        @type float
        @param ref_clock is the name of the reference clock 'ref1' or 'ref2'
        @type str
        @return LO2 frequency
        @rtype float
        """
        select_dict = {"ref1": self.LO1_ref1_freq_dict, "ref2": self.LO1_ref2_freq_dict}
        LO1_ref_dict = select_dict[ref_clock]
        LO1_freq = LO1_ref_dict[RFin]
        if RFin < 2500:
            LO2_freq = LO1_freq - RFin - hw.cfg.IF2   # Low-side
        else:
            LO2_freq = LO1_freq - RFin + hw.cfg.IF2   # High-side
        return LO2_freq

    def load_list(self, file_name) -> list:
        """
        Read the control codes for LO1, LO2 and LO3 from their associated lists.

        @param file_name The name of an ASCII file that contains int's or float's
        @type <class 'string'>
        @param data_type <class 'type'>, int or float, that you want your data converted to.
        @type <class 'int'> OR <class 'float'> depending on file contents
        @return A list containing the value(s) of 'type'
        @rtype <class 'list'>
        """
        with open(file_name, 'rb') as f:
            tmp_list = pickle.load(f)
        return tmp_list



    def create_data(self) -> None:
        # Create the list of LO1 frequencies when using reference clock 1.
        self.LO1_ref1_freq_list = [self._LO1_frequency(RFin, hw.cfg.Fpfd1) for RFin in self.RFin_list]
        self.LO1_ref1_freq_list = [round(x, 9) for x in self.LO1_ref1_freq_list]
        # Create the list of LO1 frequencies when using reference clock 2.
        self.LO1_ref2_freq_list = [self._LO1_frequency(RFin, hw.cfg.Fpfd2) for RFin in self.RFin_list]
        self.LO1_ref2_freq_list = [round(x, 9) for x in self.LO1_ref2_freq_list]
        # Create the list of LO1 N values for setting the frequency of the ADF4356 chip when using reference clock 1
        self.LO1_ref1_N_list = [int(LO1_freq/hw.cfg.Fpfd1) for LO1_freq in self.LO1_ref1_freq_list]
        # Create the list of LO1 N values for setting the frequency of the ADF4356 chip when using reference clock 2
        self.LO1_ref2_N_list = [int(LO1_freq/hw.cfg.Fpfd2) for LO1_freq in self.LO1_ref2_freq_list]
        # Create the frequency lookup tables for LO1
        self.LO1_ref1_freq_dict = dict(zip(self.RFin_list, self.LO1_ref1_freq_list))
        self.LO1_ref2_freq_dict = dict(zip(self.RFin_list, self.LO1_ref2_freq_list))
        # Create the frequency lookup tables for LO2. (LO2_freq = LO1 - freq + hw.cfg.IF2)
        self.LO2_ref1_freq_list = [round(self._LO2_frequency(freq, "ref1"), 9) for freq in self.RFin_list]
        self.LO2_ref2_freq_list = [round(self._LO2_frequency(freq, "ref2"), 9) for freq in self.RFin_list]
        # Create the LO2 control codes for setting the frequency of the MAX2871 chip for ref clocks 1 and 2
        self.LO2_ref1_fmn_list = [hw.MHz_to_fmn(freq, hw.cfg.ref_clock_1) for freq in self.LO2_ref1_freq_list]
        self.LO2_ref2_fmn_list = [hw.MHz_to_fmn(freq, hw.cfg.ref_clock_2) for freq in self.LO2_ref2_freq_list]
        pass

    def save_data_files(self) -> None:
        """Save LO1 and LO2 data for ref1 and ref2."""
        file_list = ["LO1_ref1_freq_steps.pickle", "LO1_ref2_freq_steps.pickle",
                     "LO1_ref1_N_steps.pickle", "LO1_ref2_N_steps.pickle",
                     "LO2_ref1_fmn_steps.pickle", "LO2_ref2_fmn_steps.pickle",
                     "LO2_ref1_freq_steps.pickle", "LO2_ref2_freq_steps.pickle",
                     ]
        lists_list = [self.LO1_ref1_freq_list, self.LO1_ref2_freq_list,
                      self.LO1_ref1_N_list, self.LO1_ref2_N_list,
                      self.LO2_ref1_fmn_list, self.LO2_ref2_fmn_list,
                      self.LO2_ref1_freq_list, self.LO2_ref2_freq_list,
                      ]
        for file_name, data_list in zip(file_list, lists_list):
            with open(file_name, 'wb') as f:
                pickle.dump(data_list, f, protocol=pickle.HIGHEST_PROTOCOL)

    """~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"""
    def create_ref1_control_file(self) -> None:
        LO1_n = self.load_list('LO1_ref1_N_steps.pickle')          # For sweeping. Convert N from a string to int
        LO2_fmn = self.load_list('LO2_ref1_fmn_steps.pickle')      # For sweeping. Convert fmn from string to int
        full_sweep_step_dict = {freq: (self.ref1, LO1, LO2) for freq, LO1, LO2 in zip(self.RFin_list, LO1_n, LO2_fmn)}
        with open('full_control_ref1.pickle', 'wb') as f:
            pickle.dump(full_sweep_step_dict, f, protocol=pickle.HIGHEST_PROTOCOL)

    def create_ref2_control_file(self):
        LO1_n = self.load_list('LO1_ref2_N_steps.pickle')          # For sweeping. Convert N from a string to int
        LO2_fmn = self.load_list('LO2_ref2_fmn_steps.pickle')      # For sweeping. Convert fmn from string to int
        full_sweep_step_dict = {freq: (self.ref2, LO1, LO2) for freq, LO1, LO2 in zip(self.RFin_list, LO1_n, LO2_fmn)}
        with open('full_control_ref2.pickle', 'wb') as f:
            pickle.dump(full_sweep_step_dict, f, protocol=pickle.HIGHEST_PROTOCOL)
    """~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"""


if __name__ == '__main__':
    print()
    import time
    print(f'Fpfd values are {hw.cfg.Fpfd1} & {hw.cfg.Fpfd2}')

    dg = data_generator()

    start = time.perf_counter()
    dg.create_data()
    dg.save_data_files()
    dg.create_ref1_control_file()
    dg.create_ref2_control_file()
    print(f'Time to generate all the files = {round(time.perf_counter()-start, 6)} seconds')

    print("Generator done")
