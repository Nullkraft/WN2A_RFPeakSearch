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

# Utility functions used for displaying the name and the line number
# of the source file. Requires: import sys
name = lambda: f'File \"{__name__}.py\",'
line = lambda: f'line {str(sys._getframe(1).f_lineno)},'


import hardware_cfg as hw
import command_processor as cmd
import sys
import pickle


class data_generator():
    """ These files will be used by calibrate_sa.py for creating the
        control dictionaries needed by the calibration scripts.
    """
    def __init__(self):
        self.ref1 = cmd.ref_clock1_enable
        self.ref2 = cmd.ref_clock2_enable
        ''' RFin_list contains every frequency from 0 to 3000.0 MHz in 1 kHz steps '''
        self.RFin_list = list()
        with open('RFin_steps.csv', 'r') as f:
            for freq in f:
                RFin = float(freq)
                self.RFin_list.append(RFin)
        with open('RFin_steps.pickle', 'wb') as f:
            pickle.dump(self.RFin_list, f, protocol=pickle.HIGHEST_PROTOCOL)


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
        Fpfd = Fref/R     # Fpfd1 = reference clock_1 and Fpfd2 = reference clock_2
        if RFin <= 2000:
            IF1 = 3800
        else:
            IF1 = 3700
        LO1_freq = Fpfd * int((RFin + Fpfd + IF1 ) / Fpfd)
        return LO1_freq


    def _LO2_frequency(self, RFin: float, ref_clock: str, injection: str) -> float:
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
        LO1_freq = select_dict[ref_clock]
        IF1_corrected = LO1_freq[RFin] - RFin       # Make correction to IF1
        if injection == "HI":
            LO2_freq = IF1_corrected + hw.cfg.IF2   # High-side injection
        elif injection == "LO":
            LO2_freq = IF1_corrected - hw.cfg.IF2   # Low-side injection
        return LO2_freq


    def _LO3_frequency(self, RFin: float, ref_clock: str, injection: str) -> float:
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
        IF1 = LO1_freq - RFin    # Update with corrected IF1
        if injection == "HI":
            LO3_freq = IF1 + hw.cfg.IF2   # High-side
        elif injection == "LO":
            LO3_freq = IF1 - hw.cfg.IF2   # Low-side
        return LO3_freq
        

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
        self.LO2_ref1_hi_freq_list = [round(self._LO2_frequency(freq, "ref1", "HI"), 9) for freq in self.RFin_list]
        self.LO2_ref2_hi_freq_list = [round(self._LO2_frequency(freq, "ref2", "HI"), 9) for freq in self.RFin_list]
        self.LO2_ref1_lo_freq_list = [round(self._LO2_frequency(freq, "ref1", "LO"), 9) for freq in self.RFin_list]
        self.LO2_ref2_lo_freq_list = [round(self._LO2_frequency(freq, "ref2", "LO"), 9) for freq in self.RFin_list]
        # Create the LO2 control codes for setting the frequency of the MAX2871 chip for ref clocks 1 and 2
        self.LO2_ref1_hi_fmn_list = [hw.MHz_to_fmn(freq, hw.cfg.ref_clock_1) for freq in self.LO2_ref1_hi_freq_list]
        self.LO2_ref2_hi_fmn_list = [hw.MHz_to_fmn(freq, hw.cfg.ref_clock_2) for freq in self.LO2_ref2_hi_freq_list]
        self.LO2_ref1_lo_fmn_list = [hw.MHz_to_fmn(freq, hw.cfg.ref_clock_1) for freq in self.LO2_ref1_lo_freq_list]
        self.LO2_ref2_lo_fmn_list = [hw.MHz_to_fmn(freq, hw.cfg.ref_clock_2) for freq in self.LO2_ref2_lo_freq_list]


    def save_ref1_hi_control_file(self) -> None:
        LO1_n = self.LO1_ref1_N_list
        LO2_fmn = self.LO2_ref1_hi_fmn_list
        full_sweep_step_dict = {freq: (self.ref1, LO1, LO2) for freq, LO1, LO2 in zip(self.RFin_list, LO1_n, LO2_fmn)}
        with open('control_ref1_HI.pickle', 'wb') as f:
            pickle.dump(full_sweep_step_dict, f, protocol=pickle.HIGHEST_PROTOCOL)


    def save_ref2_hi_control_file(self):
        LO1_n = self.LO1_ref2_N_list
        LO2_fmn = self.LO2_ref2_hi_fmn_list
        full_sweep_step_dict = {freq: (self.ref2, LO1, LO2) for freq, LO1, LO2 in zip(self.RFin_list, LO1_n, LO2_fmn)}
        with open('control_ref2_HI.pickle', 'wb') as f:
            pickle.dump(full_sweep_step_dict, f, protocol=pickle.HIGHEST_PROTOCOL)


    def save_ref1_lo_control_file(self) -> None:
        LO1_n = self.LO1_ref1_N_list
        LO2_fmn = self.LO2_ref1_lo_fmn_list
        full_sweep_step_dict = {freq: (self.ref1, LO1, LO2) for freq, LO1, LO2 in zip(self.RFin_list, LO1_n, LO2_fmn)}
        with open('control_ref1_LO.pickle', 'wb') as f:
            pickle.dump(full_sweep_step_dict, f, protocol=pickle.HIGHEST_PROTOCOL)


    def save_ref2_lo_control_file(self):
        LO1_n = self.LO1_ref2_N_list
        LO2_fmn = self.LO2_ref2_lo_fmn_list
        full_sweep_step_dict = {freq: (self.ref2, LO1, LO2) for freq, LO1, LO2 in zip(self.RFin_list, LO1_n, LO2_fmn)}
        with open('control_ref2_LO.pickle', 'wb') as f:
            pickle.dump(full_sweep_step_dict, f, protocol=pickle.HIGHEST_PROTOCOL)



    def dump_control_files(self):
        LO1_n = self.LO1_ref1_N_list
        LO2_fmn = self.LO2_ref1_hi_fmn_list
        full_sweep_step_dict = {freq: (self.ref1, LO1, LO2) for freq, LO1, LO2 in zip(self.RFin_list, LO1_n, LO2_fmn)}
        with open('control_ref1_HI.csv', 'w') as f:
            for all_items in full_sweep_step_dict.items():
                f.write(f'{all_items}' + '\n')

        LO1_n = self.LO1_ref2_N_list
        LO2_fmn = self.LO2_ref2_hi_fmn_list
        full_sweep_step_dict = {freq: (self.ref2, LO1, LO2) for freq, LO1, LO2 in zip(self.RFin_list, LO1_n, LO2_fmn)}
        with open('control_ref2_HI.csv', 'w') as f:
            for all_items in full_sweep_step_dict.items():
                f.write(f'{all_items}' + '\n')

        LO1_n = self.LO1_ref1_N_list
        LO2_fmn = self.LO2_ref1_lo_fmn_list
        full_sweep_step_dict = {freq: (self.ref1, LO1, LO2) for freq, LO1, LO2 in zip(self.RFin_list, LO1_n, LO2_fmn)}
        with open('control_ref1_LO.csv', 'w') as f:
            for all_items in full_sweep_step_dict.items():
                f.write(f'{all_items}' + '\n')

        LO1_n = self.LO1_ref2_N_list
        LO2_fmn = self.LO2_ref2_lo_fmn_list
        full_sweep_step_dict = {freq: (self.ref2, LO1, LO2) for freq, LO1, LO2 in zip(self.RFin_list, LO1_n, LO2_fmn)}
        with open('control_ref2_LO.csv', 'w') as f:
            for all_items in full_sweep_step_dict.items():
                f.write(f'{all_items}' + '\n')




if __name__ == '__main__':
    print()
    import time

    print(f'Fpfd values are {hw.cfg.Fpfd1} & {hw.cfg.Fpfd2}')
    dg = data_generator()

    start = time.perf_counter()
    dg.create_data()
    dg.save_ref1_hi_control_file()
    dg.save_ref2_hi_control_file()
    dg.save_ref1_lo_control_file()
    dg.save_ref2_lo_control_file()
    print(f'Time to generate all the files = {round(time.perf_counter()-start, 6)} seconds')
    
    dg.dump_control_files()

    print("Generator done")
